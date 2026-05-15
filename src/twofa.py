import tkinter as tk
from tkinter import ttk, messagebox
import base64
from .crypto import totp, totp_remaining
from .constants import W95_BG, W95_FG, W95_BTN, W95_INPUT, W95_SH, FONT, FONT_BOLD, FONT_SM, FONT_MONO
from .lang import tr
from .vault_ui import clear_children, show_vault_locked
from .tk_layout import Progressbar95Game


class TOTPTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=W95_BG)
        self.refresh_id = None
        self.game = None
        self.build()

    def build(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("red.Horizontal.TProgressbar", background="#f44336", lightcolor="#f44336", darkcolor="#f44336", troughcolor=W95_BG, relief=tk.SUNKEN)
        style.configure("orange.Horizontal.TProgressbar", background="#ff9800", lightcolor="#ff9800", darkcolor="#ff9800", troughcolor=W95_BG, relief=tk.SUNKEN)
        style.configure("green.Horizontal.TProgressbar", background="#4caf50", lightcolor="#4caf50", darkcolor="#4caf50", troughcolor=W95_BG, relief=tk.SUNKEN)

        f = tk.Frame(self.frame, bg=W95_BG, padx=15, pady=15)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text=tr("totp_title"),
                 font=("Terminal", 16, "bold"), bg=W95_BG, fg=W95_FG).pack(pady=(0, 10))

        self.content_area = tk.Frame(f, bg=W95_BG)
        self.content_area.pack(fill=tk.BOTH, expand=True)

        self.refresh()

    def show_game(self):
        if self.refresh_id:
            self.app.root.after_cancel(self.refresh_id)
            self.refresh_id = None
        self.stop_game()
        clear_children(self.content_area)
        self.game = Progressbar95Game(self.content_area, self)

    def stop_game(self):
        if self.game:
            self.game.destroy()
            self.game = None

    def refresh(self):
        if getattr(self.app, "easter_game_mode", False):
            if not self.game or not self.game.frame.winfo_exists():
                self.show_game()
            return

        self.stop_game()

        if not self.app.vault_unlocked:
            if self.refresh_id:
                self.app.root.after_cancel(self.refresh_id)
                self.refresh_id = None
            show_vault_locked(self.content_area)
            return

        if not hasattr(self, "inner") or not self.inner.winfo_exists():
            self.unlocked_view()

        self._update_codes()

    def unlocked_view(self):
        clear_children(self.content_area)

        af = tk.LabelFrame(self.content_area, text=tr("totp_add_key"), font=FONT, bg=W95_BG, fg=W95_FG,
                           padx=10, pady=8, relief=tk.GROOVE, bd=2)
        af.pack(fill=tk.X, pady=5)

        row1 = tk.Frame(af, bg=W95_BG)
        row1.pack(fill=tk.X, pady=2)
        tk.Label(row1, text=tr("totp_label"), font=FONT, bg=W95_BG, fg=W95_FG).pack(side=tk.LEFT)
        self.label_ent = tk.Entry(row1, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2)
        self.label_ent.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0), ipady=3)

        row2 = tk.Frame(af, bg=W95_BG)
        row2.pack(fill=tk.X, pady=2)
        tk.Label(row2, text=tr("totp_secret"), font=FONT, bg=W95_BG, fg=W95_FG).pack(side=tk.LEFT)
        self.secret_ent = tk.Entry(row2, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2)
        self.secret_ent.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0), ipady=3)

        tk.Button(af, text=tr("totp_add_btn"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, cursor="hand2",
                  command=self.add_key).pack(pady=5)

        self.canvas = tk.Canvas(self.content_area, bg=W95_INPUT, relief=tk.SUNKEN, bd=2, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=8)
        scroll = tk.Scrollbar(self.canvas, orient=tk.VERTICAL, command=self.canvas.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scroll.set)
        self.inner = tk.Frame(self.canvas, bg=W95_INPUT)
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        def _conf(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.inner.bind("<Configure>", _conf)

        self.timer_label = tk.Label(self.content_area, text="", font=FONT, bg=W95_BG, fg=W95_SH)
        self.timer_label.pack()

        self.countdown_bar = ttk.Progressbar(self.content_area, mode="determinate", length=300)
        self.countdown_bar.pack(pady=2)

    def _update_codes(self):
        try:
            for w in self.inner.winfo_children():
                w.destroy()

            items = self.app.vault_data.get("totp", [])
            if not items:
                tk.Label(self.inner, text=tr("totp_empty"),
                         font=FONT, bg=W95_INPUT, fg=W95_SH, justify=tk.CENTER).pack(pady=40)
            else:
                for i, item in enumerate(items):
                    code = totp(item["secret"])
                    remaining = totp_remaining()
                    card = tk.Frame(self.inner, bg=W95_BG, padx=10, pady=8, relief=tk.RAISED, bd=2)
                    card.pack(fill=tk.X, padx=8, pady=4)

                    tk.Label(card, text=item["label"], font=FONT_BOLD,
                             bg=W95_BG, fg=W95_FG).pack(anchor=tk.W)

                    cf = tk.Frame(card, bg=W95_BG)
                    cf.pack(fill=tk.X)
                    cl = tk.Label(cf, text=code, font=("Terminal", 24, "bold"),
                                  bg=W95_BG, fg=W95_FG)
                    cl.pack(side=tk.LEFT)
                    tk.Label(cf, text=f"({remaining}{tr('seconds_abbr')})", font=FONT,
                             bg=W95_BG, fg=W95_SH).pack(side=tk.LEFT, padx=(8, 0))

                    bf = tk.Frame(card, bg=W95_BG)
                    bf.pack(side=tk.RIGHT)
                    tk.Button(bf, text=tr("totp_copy"), font=FONT_SM, bg=W95_BTN, fg=W95_FG,
                              relief=tk.RAISED, bd=2, cursor="hand2",
                              command=lambda c=code: self._copy(c)).pack(side=tk.LEFT, padx=2)
                    tk.Button(bf, text=tr("totp_delete"), font=FONT_SM, bg=W95_BTN, fg="#f44336",
                              relief=tk.RAISED, bd=2, cursor="hand2",
                              command=lambda idx=i: self.delete_key(idx)).pack(side=tk.LEFT, padx=2)

            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            remaining = totp_remaining()
            self.timer_label.config(text=tr("totp_refresh").format(remaining))
            self.countdown_bar["value"] = (remaining / 30) * 100
            if remaining <= 5:
                self.countdown_bar["style"] = "red.Horizontal.TProgressbar"
            elif remaining <= 10:
                self.countdown_bar["style"] = "orange.Horizontal.TProgressbar"
            else:
                self.countdown_bar["style"] = ""
            if self.refresh_id:
                self.app.root.after_cancel(self.refresh_id)
            self.refresh_id = self.app.root.after(1000, self.refresh)
        except tk.TclError:
            self.refresh_id = None

    def add_key(self):
        if not self.app.vault_unlocked:
            return
        label = self.label_ent.get().strip()
        secret = self.secret_ent.get().strip()
        if not label or not secret:
            messagebox.showwarning(tr("error"), tr("fill_all"))
            return
        try:
            base64.b32decode(secret.upper())
        except Exception:
            messagebox.showerror(tr("error"), tr("totp_invalid_secret"))
            return
        self.app.vault_data.setdefault("totp", []).append({
            "label": label,
            "secret": secret.upper()
        })
        self.app.save_vault()
        self.label_ent.delete(0, tk.END)
        self.secret_ent.delete(0, tk.END)
        self.refresh()

    def delete_key(self, idx):
        item = self.app.vault_data["totp"][idx]
        if messagebox.askyesno(tr("confirm_delete"), f'{tr("totp_delete_confirm")} "{item["label"]}"?'):
            del self.app.vault_data["totp"][idx]
            self.app.save_vault()
            self.refresh()

    def _copy(self, text):
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(text)
