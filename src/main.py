import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import base64
import hashlib
import ctypes
from ctypes import wintypes
from .constants import VAULT_FILE, ICON_FILE, W95_BG, W95_FG, W95_BTN, W95_SH, W95_INPUT, FONT, FONT_BOLD, FONT_SM, FONT_LG, FONT_MONO
from .crypto import derive_key, encrypt_data, decrypt_data
from .passgen import GeneratorTab
from .savepass import VaultTab
from .twofa import TOTPTab
from .notepad import NotepadTab
from .email_tab import EmailTab
from .lang import tr, set_lang, get_lang, SUPPORTED
from .win95_dialog import Win95Dialog
from .title_bar_util import bind_title_drag

AUTO_LOCK_MS = 120_000

GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080


class PasswordApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry("840x540+100+100")
        self.root.title("Password Manager")
        self.root.configure(bg=W95_BG)
        try:
            self.root.iconbitmap(ICON_FILE.replace(".png", ".ico"))
        except Exception:
            pass

        self.drag_start = (0, 0)
        self.win_pos = (0, 0)
        self.is_maxed = False
        self.saved_geom = ""
        self.lang_var = tk.StringVar(value=get_lang())

        self.vault_data = {"passwords": [], "totp": []}
        self.vault_unlocked = False
        self.master_password = ""
        self.vault_tab = None
        self.auto_lock_id = None
        self._pending_restore = False

        self.root.bind("<Map>", self._on_map)
        self.setup_styles()
        self.create_border()
        self.create_title_bar()
        self.setup_ui()

        try:
            self.root.attributes("-toolwindow", False)
        except tk.TclError:
            pass
        self.root.after(100, lambda: self._fix_taskbar(self.root))
        self.root.after(200, self.startup_unlock)

    def _top_hwnd(self, widget):
        hwnd = widget.winfo_id()
        parent = ctypes.windll.user32.GetParent(hwnd)
        return parent if parent else hwnd

    def _get_window_long(self, hwnd, index):
        if ctypes.sizeof(ctypes.c_void_p) == 8:
            return ctypes.windll.user32.GetWindowLongPtrW(hwnd, index)
        return ctypes.windll.user32.GetWindowLongW(hwnd, index)

    def _set_window_long(self, hwnd, index, value):
        if ctypes.sizeof(ctypes.c_void_p) == 8:
            return ctypes.windll.user32.SetWindowLongPtrW(hwnd, index, value)
        return ctypes.windll.user32.SetWindowLongW(hwnd, index, value)

    def _fix_taskbar(self, widget=None):
        if sys.platform != "win32":
            return
        widget = widget or self.root
        try:
            widget.update_idletasks()
            hwnd = self._top_hwnd(widget)
            style = self._get_window_long(hwnd, GWL_EXSTYLE)
            style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            self._set_window_long(hwnd, GWL_EXSTYLE, style)

            SWP_FRAMECHANGED = 0x0020
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOZORDER = 0x0004
            SWP_SHOWWINDOW = 0x0040
            ctypes.windll.user32.SetWindowPos(
                hwnd, 0, 0, 0, 0, 0,
                SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_SHOWWINDOW,
            )
        except Exception:
            pass

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#808080", borderwidth=2)
        style.configure("TNotebook.Tab", font=FONT, padding=[16, 4],
                        background=W95_BTN, foreground=W95_FG, borderwidth=2,
                        relief=tk.RAISED)
        style.map("TNotebook.Tab", background=[("selected", W95_BG), ("active", "#E0E0E0")],
                  foreground=[("selected", W95_FG), ("active", W95_FG)])
        style.configure("TProgressbar", thickness=10, troughcolor=W95_BG,
                        background="#000080", lightcolor="#000080", darkcolor="#000080",
                        bordercolor=W95_SH, relief=tk.SUNKEN)
        style.configure("red.Horizontal.TProgressbar", background="#f44336", lightcolor="#f44336", darkcolor="#f44336")
        style.configure("orange.Horizontal.TProgressbar", background="#ff9800", lightcolor="#ff9800", darkcolor="#ff9800")
        style.configure("green.Horizontal.TProgressbar", background="#4caf50", lightcolor="#4caf50", darkcolor="#4caf50")
        style.configure("TCheckbutton", font=FONT, background=W95_BG, foreground=W95_FG)

    def create_border(self):
        B = 3
        self.outer = tk.Frame(self.root, bg=W95_BG)
        self.outer.pack(fill=tk.BOTH, expand=True)

        self.border_t = tk.Canvas(self.outer, height=B, highlightthickness=0)
        self.border_t.pack(fill=tk.X)
        self.border_t.bind("<Configure>", self._draw_border_top)

        mid = tk.Frame(self.outer, bg=W95_BG)
        mid.pack(fill=tk.BOTH, expand=True)

        self.border_l = tk.Canvas(mid, width=B, highlightthickness=0)
        self.border_l.pack(side=tk.LEFT, fill=tk.Y)
        self.border_l.bind("<Configure>", self._draw_border_left)

        self.inner = tk.Frame(mid, bg=W95_BG)
        self.inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.border_r = tk.Canvas(mid, width=B, highlightthickness=0)
        self.border_r.pack(side=tk.RIGHT, fill=tk.Y)
        self.border_r.bind("<Configure>", self._draw_border_right)

        self.border_b = tk.Canvas(self.outer, height=B, highlightthickness=0)
        self.border_b.pack(fill=tk.X)
        self.border_b.bind("<Configure>", self._draw_border_bottom)

    def _draw_border_top(self, event=None):
        w = self.border_t.winfo_width()
        h = 3
        self.border_t.delete("all")
        for x in range(0, w, 2):
            r = x / max(w, 1)
            if r < 0.5:
                val = int(0 + (128 - 0) * (r * 2))
            else:
                val = int(128 + (255 - 128) * ((r - 0.5) * 2))
            self.border_t.create_rectangle(x, 0, x + 2, h, fill=f"#{val:02x}{val:02x}{val:02x}", outline="")

    def _draw_border_bottom(self, event=None):
        w = self.border_b.winfo_width()
        h = 3
        self.border_b.delete("all")
        for x in range(0, w, 2):
            r = x / max(w, 1)
            if r < 0.5:
                val = int(255 + (128 - 255) * (r * 2))
            else:
                val = int(128 + (0 - 128) * ((r - 0.5) * 2))
            self.border_b.create_rectangle(x, 0, x + 2, h, fill=f"#{val:02x}{val:02x}{val:02x}", outline="")

    def _draw_border_left(self, event=None):
        h = self.border_l.winfo_height()
        w = 3
        self.border_l.delete("all")
        for y in range(0, h, 2):
            r = y / max(h, 1)
            val = int(0 + (128 - 0) * r)
            self.border_l.create_rectangle(0, y, w, y + 2, fill=f"#{val:02x}{val:02x}{val:02x}", outline="")

    def _draw_border_right(self, event=None):
        h = self.border_r.winfo_height()
        w = 3
        self.border_r.delete("all")
        for y in range(0, h, 2):
            r = y / max(h, 1)
            val = int(128 + (255 - 128) * r)
            self.border_r.create_rectangle(0, y, w, y + 2, fill=f"#{val:02x}{val:02x}{val:02x}", outline="")

    def create_title_bar(self):
        self.title_bar = tk.Frame(self.inner, height=26)
        self.title_bar.pack(fill=tk.X, side=tk.TOP)
        self.title_bar.pack_propagate(False)

        self.tc = tk.Canvas(self.title_bar, height=26, highlightthickness=0, bg="#000080")
        self.tc.pack(fill=tk.BOTH, expand=True)
        self.tc.bind("<Configure>", self._redraw_title)
        bind_title_drag(self.tc, self._title_click, self._drag_win)
        self.title_bar.bind("<Button-1>", self._title_click)
        self.title_bar.bind("<B1-Motion>", self._drag_win)

    def _redraw_title(self, event=None):
        self.tc.delete("all")
        w = self.tc.winfo_width()
        h = 24
        bw = 8
        for x in range(0, w, bw):
            r = x / max(w, 1)
            R = int(0 + (79 - 0) * r)
            G = int(0 + (195 - 0) * r)
            B = int(128 + (247 - 128) * r)
            self.tc.create_rectangle(x, 0, x + bw, h, fill=f"#{R:02x}{G:02x}{B:02x}", outline="")
        self.tc.create_line(0, h - 1, w, h - 1, fill="white")

        mid = h // 2
        self.tc.create_text(6, mid, text=f"  {tr('app_title')}",
                            font=("Terminal", 10), fill="white", anchor="w")

        bw, bh = 20, 18
        by = (h - bh) // 2

        cx = w - bw - 3
        self._win95_btn(cx, by, bw, bh, "✕", close=True)
        self._btn_rects = [(cx, by, cx + bw, by + bh, self.root.destroy)]

        mx = cx - bw - 3
        self._win95_btn(mx, by, bw, bh, "□" if not self.is_maxed else "❐")
        self._btn_rects.append((mx, by, mx + bw, by + bh, self._toggle_max))

        nx = mx - bw - 3
        self._win95_btn(nx, by, bw, bh, "_")
        self._btn_rects.append((nx, by, nx + bw, by + bh, self._iconify))

        bind_title_drag(self.tc, self._title_click, self._drag_win)

    def _win95_btn(self, x, y, w, h, text, close=False):
        # 1. Main body
        self.tc.create_rectangle(x, y, x + w, y + h, fill="#C0C0C0", outline="")
    
        # 2. Draw a single-pixel 3D border instead of multiple lines
        # Light top-left
        self.tc.create_line(x, y, x + w, y, fill="white")
        self.tc.create_line(x, y, x, y + h, fill="white")
        # Dark bottom-right
        self.tc.create_line(x + w, y, x + w, y + h, fill="#808080")
        self.tc.create_line(x, y + h, x + w, y + h, fill="#808080")
    
         # 3. Text (Slightly adjusted centering)
        self.tc.create_text(x + w // 2, y + h // 2, text=text, 
        font=("Terminal", 10 if not close else 9), fill="black")


    def _title_click(self, ev):
        for x1, y1, x2, y2, fn in getattr(self, "_btn_rects", []):
            if x1 <= ev.x <= x2 and y1 <= ev.y <= y2:
                fn()
                return
        self.drag_start = (ev.x_root, ev.y_root)
        self.win_pos = (self.root.winfo_x(), self.root.winfo_y())

    def _drag_win(self, ev):
        if self.is_maxed:
            return
        dx = ev.x_root - self.drag_start[0]
        dy = ev.y_root - self.drag_start[1]
        self.root.geometry(f"+{self.win_pos[0] + dx}+{self.win_pos[1] + dy}")

    def _iconify(self):
        self._pending_restore = True
        self.root.overrideredirect(False)
        self.root.iconify()

    def _on_map(self, event):
        if event.widget != self.root or not self._pending_restore:
            return
        if self.root.wm_state() != "normal":
            return
        self._pending_restore = False
        self.root.after(10, self._restore_override)

    def _restore_override(self):
        try:
            self.root.overrideredirect(True)
            self._redraw_title()
            self.root.after(10, lambda: self._fix_taskbar(self.root))
        except Exception:
            pass

    def _toggle_max(self):
        if self.is_maxed:
            self.root.geometry(self.saved_geom)
            self.is_maxed = False
        else:
            self.saved_geom = self.root.geometry()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            self.root.geometry(f"{sw}x{sh - 48}+0+0")
            self.is_maxed = True
        self.root.after(50, self._redraw_title)

    def _on_lang_change(self, *args):
        set_lang(self.lang_var.get())
        self._rebuild_ui()

    def _rebuild_ui(self):
        was_unlocked = self.vault_unlocked
        if hasattr(self, 'totp_tab') and self.totp_tab and self.totp_tab.refresh_id:
            self.root.after_cancel(self.totp_tab.refresh_id)
            self.totp_tab.refresh_id = None
        if self.content:
            self.content.destroy()
        self.setup_ui()
        self._redraw_title()
        if was_unlocked:
            self.vault_unlocked = True

    def setup_ui(self):
        self.content = tk.Frame(self.inner, bg=W95_BG)
        self.content.pack(fill=tk.BOTH, expand=True)

        top_bar = tk.Frame(self.content, bg=W95_BG)
        top_bar.pack(fill=tk.X, padx=4, pady=(4, 0))
        tk.Label(top_bar, text=tr("app_title"), font=FONT_SM, bg=W95_BG, fg=W95_SH).pack(side=tk.LEFT)
        lang_menu = ttk.Combobox(top_bar, textvariable=self.lang_var,
                                 values=list(SUPPORTED.keys()),
                                 state="readonly", width=6, font=FONT_SM)
        lang_menu.pack(side=tk.RIGHT)
        lang_menu.bind("<<ComboboxSelected>>", self._on_lang_change)

        self.notebook = ttk.Notebook(self.content)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        gen_tab = GeneratorTab(self.notebook, self)
        vault_tab = VaultTab(self.notebook, self)
        totp_tab = TOTPTab(self.notebook, self)
        notes_tab = NotepadTab(self.notebook, self)
        email_tab = EmailTab(self.notebook, self)

        self.vault_tab = vault_tab
        self.totp_tab = totp_tab
        self.notes_tab = notes_tab

        self.notebook.add(gen_tab.frame, text=f"  {tr('tab_gen')}  ")
        self.notebook.add(vault_tab.frame, text=f"  {tr('tab_vault')}  ")
        self.notebook.add(totp_tab.frame, text=f"  {tr('tab_2fa')}  ")
        self.notebook.add(notes_tab.frame, text=f"  {tr('tab_notes')}  ")
        self.notebook.add(email_tab.frame, text=f"  {tr('tab_email')}  ")

    def startup_unlock(self):
        self.root.update_idletasks()
        self.root.lift()
        self.root.focus_force()
        if not self.vault_unlocked:
            self.prompt_unlock()
        self.root.after(50, lambda: self._fix_taskbar(self.root))

    def reset_auto_lock(self):
        if self.auto_lock_id:
            self.root.after_cancel(self.auto_lock_id)
        self.auto_lock_id = self.root.after(AUTO_LOCK_MS, self.auto_lock)

    def auto_lock(self):
        if not self.vault_unlocked:
            return
        self.lock_vault()
        messagebox.showinfo(
            tr("autolock_title"),
            tr("autolock_msg")
        )
        self.prompt_unlock()

    def vault_exists(self) -> bool:
        return os.path.exists(VAULT_FILE) and os.path.getsize(VAULT_FILE) > 0

    def save_vault(self):
        if not self.master_password:
            return
        salt = os.urandom(16)
        key = derive_key(self.master_password, salt)
        master_hash = hashlib.sha256(key).hexdigest()

        data = {
            "salt": base64.b64encode(salt).decode(),
            "master_hash": master_hash,
            "passwords": [],
            "totp": [],
        }

        for p in self.vault_data.get("passwords", []):
            enc = base64.b64encode(
                encrypt_data(p["password"].encode(), key)
            ).decode()
            data["passwords"].append({
                "label": p["label"],
                "password": enc,
                "date": p["date"],
            })

        for t in self.vault_data.get("totp", []):
            enc = base64.b64encode(
                encrypt_data(t["secret"].encode(), key)
            ).decode()
            data["totp"].append({
                "label": t["label"],
                "secret": enc,
            })

        try:
            with open(VAULT_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror(tr("save_error"), tr("save_error_msg").format(e))

    def decrypt_vault(self, password: str) -> bool:
        try:
            with open(VAULT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            salt = base64.b64decode(data["salt"])
            key = derive_key(password, salt)

            if data.get("master_hash") != hashlib.sha256(key).hexdigest():
                return False

            vault = {"passwords": [], "totp": []}

            for p in data.get("passwords", []):
                pwd = decrypt_data(base64.b64decode(p["password"]), key).decode()
                vault["passwords"].append({
                    "label": p["label"],
                    "password": pwd,
                    "date": p.get("date", ""),
                })

            for t in data.get("totp", []):
                secret = decrypt_data(base64.b64decode(t["secret"]), key).decode()
                vault["totp"].append({
                    "label": t["label"],
                    "secret": secret,
                })

            self.vault_data = vault
            return True
        except Exception:
            return False

    def change_master_password(self):
        if not self.vault_unlocked:
            return
        dlg = Win95Dialog(self.root, tr("mp_change_title"), 350, 250, app=self)
        body = dlg.body

        tk.Label(body, text=tr("mp_current"), font=FONT, bg=W95_BG, fg=W95_FG).pack(pady=(12, 2))
        cur_var = tk.StringVar()
        tk.Entry(body, textvariable=cur_var, show="*", font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2).pack(ipady=3, padx=25, fill=tk.X)

        tk.Label(body, text=tr("mp_new"), font=FONT, bg=W95_BG, fg=W95_FG).pack(pady=(8, 2))
        new_var = tk.StringVar()
        tk.Entry(body, textvariable=new_var, show="*", font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2).pack(ipady=3, padx=25, fill=tk.X)

        tk.Label(body, text=tr("mp_repeat"), font=FONT, bg=W95_BG, fg=W95_FG).pack(pady=(8, 2))
        rep_var = tk.StringVar()
        tk.Entry(body, textvariable=rep_var, show="*", font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2).pack(ipady=3, padx=25, fill=tk.X)

        def confirm():
            cur = cur_var.get()
            new = new_var.get()
            rep = rep_var.get()
            if not cur or not new or not rep:
                messagebox.showwarning(tr("error"), tr("fill_all"))
                return
            if cur != self.master_password:
                messagebox.showerror(tr("error"), tr("mp_wrong"))
                return
            if new != rep:
                messagebox.showerror(tr("error"), tr("mp_no_match"))
                return
            if len(new) < 4:
                messagebox.showerror(tr("error"), tr("mp_too_short"))
                return
            self.master_password = new
            self.save_vault()
            dlg.close()
            messagebox.showinfo(tr("ready"), tr("mp_changed"))

        tk.Button(body, text=tr("mp_change_btn"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG, relief=tk.RAISED, bd=2, command=confirm).pack(pady=12)

    def reset_vault(self):
        if not messagebox.askyesno(
            tr("reset_title"),
            tr("reset_msg")
        ):
            return
        if os.path.exists(VAULT_FILE):
            os.remove(VAULT_FILE)
        self.vault_data = {"passwords": [], "totp": []}
        self.vault_unlocked = False
        self.master_password = ""
        if self.auto_lock_id:
            self.root.after_cancel(self.auto_lock_id)
            self.auto_lock_id = None
        self._refresh_vault_tabs()
        messagebox.showinfo(tr("ready"), tr("reset_done"))

    def _refresh_vault_tabs(self):
        if self.vault_tab:
            self.vault_tab.refresh()
        if self.notes_tab:
            self.notes_tab.refresh()
        if self.totp_tab:
            self.totp_tab.refresh()

    def lock_vault(self):
        self.vault_unlocked = False
        self.master_password = ""
        if self.auto_lock_id:
            self.root.after_cancel(self.auto_lock_id)
            self.auto_lock_id = None
        self._refresh_vault_tabs()

    def prompt_unlock(self):
        if self.vault_unlocked:
            self.reset_auto_lock()
            return True

        first_run = not self.vault_exists()
        title = tr("unlock_title_set") if first_run else tr("unlock_title_in")
        dlg = Win95Dialog(self.root, title, 350, 190, app=self)
        body = dlg.body

        desc = tr("unlock_desc_set") if first_run else tr("unlock_desc_in")
        tk.Label(body, text=desc, font=FONT, bg=W95_BG, fg=W95_FG, justify=tk.CENTER).pack(pady=(15, 10))

        pwd_var = tk.StringVar()
        entry = tk.Entry(body, textvariable=pwd_var, show="*", font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2)
        entry.pack(pady=5, ipady=4, padx=20, fill=tk.X)

        result = [False]

        def confirm():
            p = pwd_var.get()
            if not p:
                return
            if first_run:
                self.master_password = p
                self.vault_unlocked = True
                self.vault_data = {"passwords": [], "totp": []}
                result[0] = True
                dlg.close()
                self._refresh_vault_tabs()
                self.reset_auto_lock()
            elif self.decrypt_vault(p):
                self.master_password = p
                self.vault_unlocked = True
                result[0] = True
                dlg.close()
                self._refresh_vault_tabs()
                self.reset_auto_lock()
            else:
                messagebox.showerror(tr("error"), tr("unlock_wrong"))

        btn_text = tr("unlock_btn_set") if first_run else tr("unlock_btn_in")
        tk.Button(body, text=btn_text, font=FONT_BOLD, bg=W95_BTN, fg=W95_FG, relief=tk.RAISED, bd=2, command=confirm).pack(pady=10)

        entry.bind("<Return>", lambda e: confirm())
        entry.focus()
        dlg.wait()
        return result[0]
