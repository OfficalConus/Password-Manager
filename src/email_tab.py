import tkinter as tk
from tkinter import ttk, messagebox
import imaplib
import email
from email.header import decode_header
from .constants import W95_BG, W95_FG, W95_BTN, W95_INPUT, W95_SH, FONT, FONT_BOLD, FONT_SM, FONT_MONO
from .lang import tr

EMAIL_PROVIDERS = {
    "Gmail": ("imap.gmail.com", "993"),
    "Outlook": ("outlook.office365.com", "993"),
    "Yandex": ("imap.yandex.com", "993"),
    "Mail.ru": ("imap.mail.ru", "993"),
}


def _decode_header(value):
    if not value:
        return ""
    parts = []
    for chunk, charset in decode_header(value):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return "".join(parts)


def _message_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and part.get_content_disposition() != "attachment":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html" and part.get_content_disposition() != "attachment":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
        return ""
    payload = msg.get_payload(decode=True)
    if not payload:
        return ""
    charset = msg.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")


class EmailTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=W95_BG)
        self.messages = []
        self.build()

    def build(self):
        f = tk.Frame(self.frame, bg=W95_BG, padx=15, pady=15)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text=tr("email_title"), font=("Terminal", 16, "bold"),
                 bg=W95_BG, fg=W95_FG).pack(pady=(0, 10))

        gf = tk.LabelFrame(f, text=tr("email_settings"), font=FONT, bg=W95_BG, fg=W95_FG,
                           padx=10, pady=8, relief=tk.GROOVE, bd=2)
        gf.pack(fill=tk.X, pady=5)

        row = tk.Frame(gf, bg=W95_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=tr("email_provider"), font=FONT, bg=W95_BG, fg=W95_FG, width=10, anchor="w").pack(side=tk.LEFT)
        self.provider_var = tk.StringVar(value="Gmail")
        provider_menu = ttk.Combobox(
            row, textvariable=self.provider_var, values=list(EMAIL_PROVIDERS),
            state="readonly", width=18, font=FONT,
        )
        provider_menu.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        provider_menu.bind("<<ComboboxSelected>>", self._on_provider_change)

        row = tk.Frame(gf, bg=W95_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="IMAP:", font=FONT, bg=W95_BG, fg=W95_FG, width=10, anchor="w").pack(side=tk.LEFT)
        self.imap_ent = tk.Entry(row, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2)
        self.imap_ent.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=3)

        row = tk.Frame(gf, bg=W95_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Port:", font=FONT, bg=W95_BG, fg=W95_FG, width=10, anchor="w").pack(side=tk.LEFT)
        self.port_ent = tk.Entry(row, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2, width=8)
        self.port_ent.pack(side=tk.LEFT, ipady=3)

        self._apply_provider("Gmail")

        row = tk.Frame(gf, bg=W95_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=tr("email_user"), font=FONT, bg=W95_BG, fg=W95_FG, width=10, anchor="w").pack(side=tk.LEFT)
        self.user_ent = tk.Entry(row, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2)
        self.user_ent.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=3)

        row = tk.Frame(gf, bg=W95_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=tr("email_pass"), font=FONT, bg=W95_BG, fg=W95_FG, width=10, anchor="w").pack(side=tk.LEFT)
        self.pass_ent = tk.Entry(row, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2, show="*")
        self.pass_ent.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=3)

        btnf = tk.Frame(f, bg=W95_BG)
        btnf.pack(fill=tk.X, pady=(0, 5))
        tk.Button(btnf, text=tr("email_fetch"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, command=self.fetch_inbox).pack(side=tk.LEFT, padx=2)

        paned = tk.PanedWindow(f, orient=tk.VERTICAL, bg=W95_BG, sashwidth=4)
        paned.pack(fill=tk.BOTH, expand=True, pady=5)

        inbox_frame = tk.LabelFrame(paned, text=tr("email_inbox"), font=FONT, bg=W95_BG, fg=W95_FG,
                                    padx=6, pady=6, relief=tk.GROOVE, bd=2)
        paned.add(inbox_frame, minsize=80)

        list_frame = tk.Frame(inbox_frame, bg=W95_BG)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self.inbox_list = tk.Listbox(list_frame, font=FONT_SM, bg=W95_INPUT, fg=W95_FG,
                                     relief=tk.SUNKEN, bd=2, selectbackground="#000080",
                                     selectforeground="white")
        self.inbox_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.inbox_list.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.inbox_list.config(yscrollcommand=scroll.set)
        self.inbox_list.bind("<<ListboxSelect>>", self.show_message)

        body_frame = tk.LabelFrame(paned, text=tr("email_message"), font=FONT, bg=W95_BG, fg=W95_FG,
                                   padx=6, pady=6, relief=tk.GROOVE, bd=2)
        paned.add(body_frame, minsize=120)

        self.msg_text = tk.Text(body_frame, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG,
                                relief=tk.SUNKEN, bd=2, wrap=tk.WORD, state=tk.DISABLED)
        self.msg_text.pack(fill=tk.BOTH, expand=True)

        self.status = tk.Label(f, text="", font=FONT_SM, bg=W95_BG, fg=W95_SH)
        self.status.pack()

    def _apply_provider(self, name):
        host, port = EMAIL_PROVIDERS.get(name, ("", "993"))
        self.imap_ent.delete(0, tk.END)
        self.imap_ent.insert(0, host)
        self.port_ent.delete(0, tk.END)
        self.port_ent.insert(0, port)

    def _on_provider_change(self, _event=None):
        self._apply_provider(self.provider_var.get())

    def _set_body(self, text):
        self.msg_text.config(state=tk.NORMAL)
        self.msg_text.delete("1.0", tk.END)
        self.msg_text.insert("1.0", text)
        self.msg_text.config(state=tk.DISABLED)

    def fetch_inbox(self):
        host = self.imap_ent.get().strip()
        port = self.port_ent.get().strip()
        user = self.user_ent.get().strip()
        pwd = self.pass_ent.get()

        if not all([host, port, user, pwd]):
            messagebox.showwarning(tr("error"), tr("fill_all"))
            return

        self.inbox_list.delete(0, tk.END)
        self.messages = []
        self._set_body("")
        self.status.config(text=tr("email_loading"))

        try:
            mail = imaplib.IMAP4_SSL(host, int(port))
            mail.login(user, pwd)
            mail.select("INBOX")

            _, data = mail.search(None, "ALL")
            ids = data[0].split()
            recent = ids[-30:] if len(ids) > 30 else ids
            recent.reverse()

            for msg_id in recent:
                _, msg_data = mail.fetch(msg_id, "(RFC822)")
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)
                subject = _decode_header(msg.get("Subject", "")) or tr("email_no_subject")
                sender = _decode_header(msg.get("From", ""))
                body = _message_body(msg)
                self.messages.append({
                    "from": sender,
                    "subject": subject,
                    "body": body,
                })
                self.inbox_list.insert(tk.END, f"{sender[:40]} | {subject[:50]}")

            mail.logout()
            count = len(self.messages)
            self.status.config(text=tr("email_loaded").format(count))
            if count:
                self.inbox_list.selection_set(0)
                self.show_message()
        except Exception as e:
            self.status.config(text="")
            messagebox.showerror(tr("error"), f"{tr('email_read_err')}: {e}")

    def show_message(self, _event=None):
        sel = self.inbox_list.curselection()
        if not sel:
            return
        msg = self.messages[sel[0]]
        header = f"{tr('email_from')}: {msg['from']}\n{tr('email_subject')}: {msg['subject']}\n{'-' * 40}\n\n"
        self._set_body(header + msg["body"])
