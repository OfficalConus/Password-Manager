import tkinter as tk
from tkinter import messagebox
import smtplib
import ssl
from email.message import EmailMessage
from .constants import W95_BG, W95_FG, W95_BTN, W95_INPUT, W95_SH, FONT, FONT_BOLD, FONT_SM, FONT_MONO
from .lang import tr


class EmailTab:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=W95_BG)
        self.build()

    def build(self):
        f = tk.Frame(self.frame, bg=W95_BG, padx=15, pady=15)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text=tr("email_title"), font=("Terminal", 16, "bold"),
                 bg=W95_BG, fg=W95_FG).pack(pady=(0, 10))

        gf = tk.LabelFrame(f, text=tr("email_settings"), font=FONT, bg=W95_BG, fg=W95_FG, padx=10, pady=8, relief=tk.GROOVE, bd=2)
        gf.pack(fill=tk.X, pady=5)

        row = tk.Frame(gf, bg=W95_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="SMTP:", font=FONT, bg=W95_BG, fg=W95_FG, width=10, anchor="w").pack(side=tk.LEFT)
        self.smtp_ent = tk.Entry(row, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2)
        self.smtp_ent.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=3)

        row = tk.Frame(gf, bg=W95_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="Port:", font=FONT, bg=W95_BG, fg=W95_FG, width=10, anchor="w").pack(side=tk.LEFT)
        self.port_ent = tk.Entry(row, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2, width=8)
        self.port_ent.pack(side=tk.LEFT, ipady=3)
        self.port_ent.insert(0, "587")

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

        mf = tk.LabelFrame(f, text=tr("email_compose"), font=FONT, bg=W95_BG, fg=W95_FG, padx=10, pady=8, relief=tk.GROOVE, bd=2)
        mf.pack(fill=tk.BOTH, expand=True, pady=5)

        row = tk.Frame(mf, bg=W95_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="To:", font=FONT, bg=W95_BG, fg=W95_FG, width=6, anchor="w").pack(side=tk.LEFT)
        self.to_ent = tk.Entry(row, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2)
        self.to_ent.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=3)

        row = tk.Frame(mf, bg=W95_BG)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=tr("email_subject"), font=FONT, bg=W95_BG, fg=W95_FG, width=6, anchor="w").pack(side=tk.LEFT)
        self.subj_ent = tk.Entry(row, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2)
        self.subj_ent.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=3)

        tk.Label(mf, text=tr("email_message"), font=FONT, bg=W95_BG, fg=W95_FG, anchor="w").pack(fill=tk.X, pady=(4, 0))
        self.msg_text = tk.Text(mf, font=FONT_MONO, bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2, height=8)
        self.msg_text.pack(fill=tk.BOTH, expand=True, pady=4)

        btnf = tk.Frame(f, bg=W95_BG)
        btnf.pack(fill=tk.X)
        tk.Button(btnf, text=tr("email_send"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, command=self.send_email).pack(side=tk.LEFT, padx=2)
        tk.Button(btnf, text=tr("email_clear"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
                  relief=tk.RAISED, bd=2, command=self.clear_compose).pack(side=tk.LEFT, padx=2)

        self.status = tk.Label(f, text="", font=FONT_SM, bg=W95_BG, fg=W95_SH)
        self.status.pack()

    def send_email(self):
        smtp = self.smtp_ent.get().strip()
        port = self.port_ent.get().strip()
        user = self.user_ent.get().strip()
        pwd = self.pass_ent.get()
        to = self.to_ent.get().strip()
        subj = self.subj_ent.get().strip()
        body = self.msg_text.get("1.0", tk.END).strip()

        if not all([smtp, port, user, pwd, to, subj, body]):
            messagebox.showwarning(tr("error"), tr("fill_all"))
            return

        try:
            msg = EmailMessage()
            msg["From"] = user
            msg["To"] = to
            msg["Subject"] = subj
            msg.set_content(body)

            ctx = ssl.create_default_context()
            with smtplib.SMTP(smtp, int(port)) as server:
                server.starttls(context=ctx)
                server.login(user, pwd)
                server.send_message(msg)

            self.status.config(text=tr("email_sent"))
        except Exception as e:
            messagebox.showerror(tr("error"), f"{tr('email_send_err')}: {e}")

    def clear_compose(self):
        self.to_ent.delete(0, tk.END)
        self.subj_ent.delete(0, tk.END)
        self.msg_text.delete("1.0", tk.END)
        self.status.config(text="")
