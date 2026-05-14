import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime
from .constants import CHAR_SETS, CHAR_ORDER, W95_BG, W95_FG, W95_BTN, W95_INPUT, W95_SH, FONT, FONT_BOLD, FONT_SM, FONT_LG, FONT_XL, FONT_MONO
from .utils import calculate_strength
from .lang import tr, tr_char


class GeneratorTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=W95_BG)
        self.gen_pwd = tk.StringVar()
        self.gen_len = tk.IntVar(value=16)
        self.gen_checks = {}
        self.gen_btn = None
        self.copy_btn = None
        self.build()

    def build(self):
        f = tk.Frame(self.frame, bg=W95_BG, padx=20, pady=20)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text=tr("gen_title"), font=FONT_XL, bg=W95_BG, fg=W95_FG).pack(pady=(0, 15))

        lf = tk.Frame(f, bg=W95_BG)
        lf.pack(fill=tk.X, pady=5)
        tk.Label(lf, text=tr("gen_length"), font=FONT, bg=W95_BG, fg=W95_FG).pack(side=tk.LEFT)
        tk.Spinbox(lf, from_=4, to=64, textvariable=self.gen_len,
                   width=5, font=FONT_MONO, justify=tk.CENTER,
                   bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2,
                   buttonbackground=W95_BTN).pack(side=tk.RIGHT)

        of = tk.LabelFrame(f, text=tr("gen_charset"), font=FONT, bg=W95_BG, fg=W95_FG, padx=10, pady=8, relief=tk.GROOVE, bd=2)
        of.pack(fill=tk.X, pady=10)
        for key in CHAR_ORDER:
            var = tk.BooleanVar(value=True)
            self.gen_checks[key] = var
            ttk.Checkbutton(of, text=tr_char(key), variable=var).pack(anchor=tk.W, pady=2)

        pwd_frame = tk.Frame(f, bg=W95_BG)
        pwd_frame.pack(fill=tk.X, pady=5)
        tk.Label(pwd_frame, text=tr("gen_password"), font=FONT, bg=W95_BG, fg=W95_FG).pack(anchor=tk.W)
        self.pwd_entry = tk.Entry(f, textvariable=self.gen_pwd, font=("Terminal", 14),
                 bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2,
                 justify=tk.CENTER, state="readonly",
                 readonlybackground=W95_INPUT)
        self.pwd_entry.pack(fill=tk.X, pady=5, ipady=6)

        self.gen_str_label = tk.Label(f, text="", font=FONT, bg=W95_BG, fg=W95_FG)
        self.gen_str_label.pack()
        self.gen_str_bar = ttk.Progressbar(f, mode="determinate", length=300)
        self.gen_str_bar.pack(pady=5)

        bf = tk.Frame(f, bg=W95_BG)
        bf.pack(pady=10)

        self.gen_btn = tk.Button(bf, text=tr("gen_generate"),
                  font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
                  padx=18, pady=4, relief=tk.RAISED, bd=2, cursor="hand2",
                  activebackground="#E0E0E0",
                  command=self.animate_generate)
        self.gen_btn.pack(side=tk.LEFT, padx=5)

        self.copy_btn = tk.Button(bf, text=tr("gen_copy"),
                  font=FONT, bg=W95_BTN, fg=W95_FG,
                  padx=18, pady=4, relief=tk.RAISED, bd=2, cursor="hand2",
                  activebackground="#E0E0E0",
                  command=self.copy)
        self.copy_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = tk.Button(bf, text=tr("gen_save"),
                  font=FONT, bg=W95_BTN, fg=W95_FG,
                  padx=18, pady=4, relief=tk.RAISED, bd=2, cursor="hand2",
                  activebackground="#E0E0E0",
                  command=self.save)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.generate()

    def get_chars(self):
        return "".join(CHAR_SETS[k] for k, v in self.gen_checks.items() if v.get())

    def make_password(self, chars, length):
        if not chars:
            return ""
        pwd = "".join(random.choice(chars) for _ in range(length))
        if (self.gen_checks["lowercase"].get() and
            self.gen_checks["uppercase"].get() and
            self.gen_checks["digits"].get()):
            while not (any(c.islower() for c in pwd) and
                       any(c.isupper() for c in pwd) and
                       any(c.isdigit() for c in pwd)):
                pwd = "".join(random.choice(chars) for _ in range(length))
        return pwd

    def animate_generate(self):
        chars = self.get_chars()
        if not chars:
            messagebox.showwarning(tr("error"), tr("gen_no_chars"))
            return
        length = self.gen_len.get()
        self.gen_btn.config(state=tk.DISABLED)

        def scramble(step):
            if step >= 8:
                final = self.make_password(chars, length)
                self.gen_pwd.set(final)
                label, color, percent = calculate_strength(final)
                self.gen_str_label.config(text=f"{tr('gen_strength')} {label}", fg=color)
                self.gen_str_bar["value"] = percent
                self.gen_pwd_entry_color(W95_FG)
                self.gen_btn.config(state=tk.NORMAL)
                return
            fake = "".join(random.choice(chars) for _ in range(length))
            self.gen_pwd.set(fake)
            colors = ["#f44336", "#ff9800", "#4caf50", "#2196f3", "#e040fb", W95_FG]
            self.gen_pwd_entry_color(colors[step % len(colors)])
            self.app.root.after(50 + step * 15, lambda: scramble(step + 1))

        scramble(0)

    def gen_pwd_entry_color(self, color):
        self.pwd_entry.config(fg=color)

    def generate(self):
        chars = self.get_chars()
        if not chars:
            messagebox.showwarning(tr("error"), tr("gen_no_chars"))
            return
        pwd = self.make_password(chars, self.gen_len.get())
        self.gen_pwd.set(pwd)
        label, color, percent = calculate_strength(pwd)
        self.gen_str_label.config(text=f"{tr('gen_strength')} {label}", fg=color)
        self.gen_str_bar["value"] = percent

    def copy(self):
        pwd = self.gen_pwd.get()
        if not pwd:
            return
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(pwd)
        old_color = self.copy_btn.cget("bg")
        old_text = self.copy_btn.cget("text")
        self.copy_btn.config(text=tr("gen_copied"), bg="#E0E0E0", fg=W95_FG)
        self.app.root.after(1500, lambda: self.copy_btn.config(
            text=old_text, bg=old_color, fg=W95_FG
        ))

    def save(self):
        pwd = self.gen_pwd.get()
        if not pwd:
            return
        if not self.app.vault_unlocked:
            if not self.app.prompt_unlock():
                return

        win = tk.Toplevel(self.app.root)
        win.title(tr("gen_save"))
        win.geometry("350x160")
        win.configure(bg=W95_BG)
        win.resizable(False, False)
        tk.Label(win, text=tr("gen_save_title"), font=FONT, bg=W95_BG, fg=W95_FG).pack(pady=(15, 5))
        var = tk.StringVar()
        tk.Entry(win, textvariable=var, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2).pack(pady=5, ipady=4, padx=20, fill=tk.X)
        tk.Button(win, text=tr("gen_save_btn"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG, relief=tk.RAISED, bd=2, cursor="hand2",
                  command=lambda: self._do_save(var.get(), pwd, win)).pack(pady=10)

    def _do_save(self, label, pwd, win):
        if not label.strip():
            messagebox.showwarning(tr("error"), tr("gen_no_name"))
            return
        self.app.vault_data["passwords"].append({
            "label": label.strip(),
            "password": pwd,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        self.app.save_vault()
        if self.app.vault_tab:
            self.app.vault_tab.refresh_list()
        win.destroy()
        messagebox.showinfo(tr("ready"), tr("gen_saved"))
