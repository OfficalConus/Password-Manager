import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from .constants import W95_BG, W95_FG, W95_BTN, W95_INPUT, W95_SH, FONT, FONT_BOLD, FONT_SM, FONT_MONO
from .lang import tr
from .vault_ui import show_vault_locked
from .win95_dialog import Win95Dialog


class VaultTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=W95_BG)
        self.build()

    def build(self):
        f = tk.Frame(self.frame, bg=W95_BG, padx=15, pady=15)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text=tr("vault_title"), font=("Terminal", 16, "bold"),
                 bg=W95_BG, fg=W95_FG).pack(pady=(0, 10))

        self.content_area = tk.Frame(f, bg=W95_BG)
        self.content_area.pack(fill=tk.BOTH, expand=True)

        self.locked_view()

    def clear_content(self):
        for w in self.content_area.winfo_children():
            w.destroy()

    def locked_view(self):
        show_vault_locked(self.content_area)

    def unlocked_view(self):
        self.clear_content()

        list_frame = tk.Frame(self.content_area, bg=W95_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.listbox = tk.Listbox(list_frame, font=FONT_MONO,
                                  bg=W95_INPUT, fg=W95_FG,
                                  relief=tk.SUNKEN, bd=2, selectbackground="#000080",
                                  selectforeground="white")
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scroll.set)
        self.listbox.bind("<Double-Button-1>", lambda e: self.copy_password())
        self.listbox.bind("<Button-3>", self.show_context_menu)

        bf = tk.Frame(self.content_area, bg=W95_BG)
        bf.pack(pady=8)
        tk.Button(bf, text=tr("vault_add"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, cursor="hand2", command=self.add_password).pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text=tr("vault_copy"), font=FONT, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, cursor="hand2", command=self.copy_password).pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text=tr("vault_edit"), font=FONT, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, cursor="hand2", command=self.edit_password).pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text=tr("vault_delete"), font=FONT, bg=W95_BTN, fg="#f44336",
                  relief=tk.RAISED, bd=2, cursor="hand2", command=self.delete_password).pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text=tr("vault_change_mp"), font=FONT_SM, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, cursor="hand2", command=self.app.change_master_password).pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text=tr("vault_reset"), font=FONT_SM, bg=W95_BTN, fg="#f44336",
                  relief=tk.RAISED, bd=2, cursor="hand2", command=self.app.reset_vault).pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text=tr("vault_lock"), font=FONT, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, cursor="hand2", command=self.lock).pack(side=tk.LEFT, padx=3)

        self.refresh_list()

    def refresh_list(self):
        if not hasattr(self, 'listbox'):
            return
        self.listbox.delete(0, tk.END)
        for item in self.app.vault_data.get("passwords", []):
            self.listbox.insert(tk.END, f'{item["label"]}  |  {item["date"]}')

    def get_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        return sel[0]

    def copy_password(self):
        idx = self.get_selected()
        if idx is None:
            return
        item = self.app.vault_data["passwords"][idx]
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(item["password"])
        messagebox.showinfo(tr("ready"), tr("vault_copied"))

    def add_password(self):
        dlg = Win95Dialog(self.app.root, tr("vault_add_title"), 400, 220, app=self.app)
        body = dlg.body

        tk.Label(body, text=tr("vault_add_label"), font=FONT, bg=W95_BG, fg=W95_FG).pack(pady=(10, 2))
        label_var = tk.StringVar()
        tk.Entry(body, textvariable=label_var, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2).pack(ipady=3, padx=20, fill=tk.X)

        tk.Label(body, text=tr("vault_add_pwd"), font=FONT, bg=W95_BG, fg=W95_FG).pack(pady=(8, 2))
        pwd_var = tk.StringVar()
        tk.Entry(body, textvariable=pwd_var, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2).pack(ipady=3, padx=20, fill=tk.X)

        def save_new():
            label = label_var.get().strip()
            pwd = pwd_var.get()
            if not label or not pwd:
                messagebox.showwarning(tr("error"), tr("fill_all"))
                return
            from datetime import datetime
            self.app.vault_data["passwords"].append({
                "label": label, "password": pwd,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            self.app.save_vault()
            self.refresh_list()
            dlg.close()
            messagebox.showinfo(tr("ready"), tr("vault_added"))

        tk.Button(body, text=tr("vault_add_btn"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, cursor="hand2", command=save_new).pack(pady=12)

    def edit_password(self):
        idx = self.get_selected()
        if idx is None:
            return
        item = self.app.vault_data["passwords"][idx]

        dlg = Win95Dialog(self.app.root, tr("vault_edit_title"), 400, 220, app=self.app)
        body = dlg.body

        tk.Label(body, text=tr("vault_edit_label"), font=FONT, bg=W95_BG, fg=W95_FG).pack(pady=(10, 2))
        label_var = tk.StringVar(value=item["label"])
        tk.Entry(body, textvariable=label_var, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2).pack(ipady=3, padx=20, fill=tk.X)

        tk.Label(body, text=tr("vault_edit_pwd"), font=FONT, bg=W95_BG, fg=W95_FG).pack(pady=(8, 2))
        pwd_var = tk.StringVar(value=item["password"])
        tk.Entry(body, textvariable=pwd_var, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2).pack(ipady=3, padx=20, fill=tk.X)

        def save_edit():
            new_label = label_var.get().strip()
            new_pwd = pwd_var.get()
            if not new_label or not new_pwd:
                messagebox.showwarning(tr("error"), tr("fill_all"))
                return
            self.app.vault_data["passwords"][idx]["label"] = new_label
            self.app.vault_data["passwords"][idx]["password"] = new_pwd
            from datetime import datetime
            self.app.vault_data["passwords"][idx]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.app.save_vault()
            self.refresh_list()
            dlg.close()
            messagebox.showinfo(tr("ready"), tr("vault_edited"))

        tk.Button(body, text=tr("vault_edit_btn"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, cursor="hand2", command=save_edit).pack(pady=12)

    def delete_password(self):
        idx = self.get_selected()
        if idx is None:
            return
        item = self.app.vault_data["passwords"][idx]
        if messagebox.askyesno(tr("confirm_delete"), f'{tr("vault_delete_confirm")} "{item["label"]}"?'):
            del self.app.vault_data["passwords"][idx]
            self.app.save_vault()
            self.refresh_list()

    def show_context_menu(self, event):
        idx = self.listbox.nearest(event.y)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.listbox.activate(idx)

        menu = tk.Menu(self.app.root, tearoff=0, bg=W95_BG, fg=W95_FG,
                       activebackground="#000080", activeforeground="white",
                       font=FONT)
        menu.add_command(label=tr("vault_copy"), command=self.copy_password)
        menu.add_command(label=tr("vault_edit"), command=self.edit_password)
        menu.add_separator()
        menu.add_command(label=tr("vault_delete"), command=self.delete_password,
                         foreground="#f44336")
        menu.post(event.x_root, event.y_root)

    def lock(self):
        self.app.lock_vault()

    def refresh(self):
        if self.app.vault_unlocked:
            self.unlocked_view()
        else:
            self.locked_view()
