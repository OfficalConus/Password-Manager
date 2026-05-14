import tkinter as tk
from tkinter import messagebox
import os
import base64
from .constants import VAULT_DIR, W95_BG, W95_FG, W95_BTN, W95_INPUT, W95_SH, FONT, FONT_BOLD, FONT_SM, FONT_MONO
from .lang import tr
from .crypto import derive_key, encrypt_data, decrypt_data

NOTE_FILE = os.path.join(VAULT_DIR, "notes.enc")
SALT_FILE = os.path.join(VAULT_DIR, "notes.salt")


class NotepadTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=W95_BG)
        self.build()

    def build(self):
        f = tk.Frame(self.frame, bg=W95_BG, padx=15, pady=15)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text=tr("notes_title"), font=("Terminal", 16, "bold"),
                 bg=W95_BG, fg=W95_FG).pack(pady=(0, 10))

        self.text = tk.Text(f, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG,
                             relief=tk.SUNKEN, bd=2, wrap=tk.WORD, undo=True)
        self.text.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        btnf = tk.Frame(f, bg=W95_BG)
        btnf.pack(fill=tk.X)

        tk.Button(btnf, text=tr("notes_save"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, command=self.save_notes).pack(side=tk.LEFT, padx=2)
        tk.Button(btnf, text=tr("notes_load"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, command=self.load_notes).pack(side=tk.LEFT, padx=2)
        tk.Button(btnf, text=tr("notes_clear"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, command=self.clear_notes).pack(side=tk.LEFT, padx=2)

        self.status = tk.Label(f, text="", font=FONT_SM, bg=W95_BG, fg=W95_SH)
        self.status.pack()

        self.load_notes()

    def _get_key(self):
        if not self.app.master_password:
            return None
        salt = b"notes_salt_fixed"
        return derive_key(self.app.master_password, salt)

    def save_notes(self):
        if not self.app.master_password:
            if not self.app.prompt_unlock():
                messagebox.showwarning(tr("error"), tr("notes_locked"))
                return
        key = self._get_key()
        if not key:
            return
        try:
            data = self.text.get("1.0", tk.END).encode("utf-8")
            enc = encrypt_data(data, key)
            with open(NOTE_FILE, "wb") as f:
                f.write(base64.b64encode(enc))
            self.status.config(text=tr("notes_saved"))
        except Exception as e:
            messagebox.showerror(tr("error"), f"{tr('notes_save_err')}: {e}")

    def load_notes(self):
        if not os.path.exists(NOTE_FILE):
            return
        if not self.app.master_password:
            return
        key = self._get_key()
        if not key:
            return
        try:
            with open(NOTE_FILE, "rb") as f:
                enc = base64.b64decode(f.read())
            data = decrypt_data(enc, key).decode("utf-8")
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", data)
            self.status.config(text=tr("notes_loaded"))
        except Exception:
            self.status.config(text=tr("notes_load_err"))

    def clear_notes(self):
        if messagebox.askyesno(tr("confirm_delete"), tr("notes_clear_confirm")):
            self.text.delete("1.0", tk.END)
            self.status.config(text=tr("notes_cleared"))
