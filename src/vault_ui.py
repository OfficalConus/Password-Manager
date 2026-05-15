import tkinter as tk
from .constants import W95_BG, W95_SH, FONT
from .lang import tr


def clear_children(widget):
    for child in widget.winfo_children():
        child.destroy()


def show_vault_locked(parent):
    clear_children(parent)
    tk.Label(parent, text=tr("vault_locked_title"),
             font=("Terminal", 14, "bold"), bg=W95_BG, fg=W95_SH).pack(pady=(40, 10))
    tk.Label(parent, text=tr("vault_locked_desc"),
             font=FONT, bg=W95_BG, fg=W95_SH, justify=tk.CENTER).pack()
