import random
import tkinter as tk
from tkinter import messagebox
from .constants import W95_BG, W95_FG, W95_BTN, W95_INPUT, W95_SH, FONT, FONT_BOLD, FONT_SM
from .lang import tr
from .win95_dialog import Win95Dialog

EGG_PIN = "10052026"
EGG_CLICKS = 5
EGG_CLICK_RESET_MS = 2500

# Progressbar95-style fragment colors
FRAG_BLUE = "#0000A8"
FRAG_RED = "#E40000"
FRAG_PINK = "#FF00FF"
FRAG_YELLOW = "#FFD800"

FRAGMENT_TYPES = (
    ("blue", FRAG_BLUE, 5, "good"),
    ("yellow", FRAG_YELLOW, -2, "bad"),
    ("pink", FRAG_PINK, -5, "minus"),
    ("red", FRAG_RED, 0, "dead"),
)

# Spawn weights: blue common, red rare
FRAG_WEIGHTS = (48, 22, 18, 12)


def show_pin_dialog(app):
    dlg = Win95Dialog(app.root, tr("egg_pin_title"), 320, 160, app=app)
    body = dlg.body

    tk.Label(body, text=tr("egg_pin_prompt"), font=FONT, bg=W95_BG, fg=W95_FG).pack(pady=(12, 6))
    pin_var = tk.StringVar()
    entry = tk.Entry(
        body, textvariable=pin_var, show="*", font=("Terminal", 14),
        bg=W95_INPUT, fg=W95_FG, relief=tk.SUNKEN, bd=2, justify=tk.CENTER,
    )
    entry.pack(ipady=4, padx=24, fill=tk.X)

    def submit(_event=None):
        if pin_var.get().strip() == EGG_PIN:
            dlg.close()
            app.enter_easter_game()
        else:
            messagebox.showerror(tr("error"), tr("egg_pin_wrong"), parent=app.root)

    tk.Button(
        body, text=tr("egg_pin_ok"), font=FONT_BOLD, bg=W95_BTN, fg=W95_FG,
        relief=tk.RAISED, bd=2, command=submit,
    ).pack(pady=10)
    entry.bind("<Return>", submit)
    entry.focus()


class Progressbar95Game:
    """Fragments Flight — catch falling segments with the progress bar (A/D)."""

    BAR_W = 88
    BAR_H = 22
    FRAG_W = 26
    FRAG_H = 18
    TICK_MS = 32

    def __init__(self, parent, totp_tab):
        self.totp_tab = totp_tab
        self.app = totp_tab.app
        self.frame = tk.Frame(parent, bg=W95_BG)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.tick_id = None
        self.restart_left = 0.0
        self.game_over = False
        self.progress = 0.0
        self.fragments = []
        self.catcher_x = 120
        self.keys = set()
        self.spawn_timer = 0
        self.flash_text = ""
        self.flash_until = 0

        self._build_ui()
        self.start_round()

    def _build_ui(self):
        tk.Label(
            self.frame, text=tr("egg_game_title"), font=("Terminal", 14, "bold"),
            bg=W95_BG, fg=W95_FG,
        ).pack(pady=(6, 2))
        tk.Label(
            self.frame, text=tr("egg_game_hint"), font=FONT_SM, bg=W95_BG, fg=W95_SH,
        ).pack(pady=(0, 4))

        legend = tk.Frame(self.frame, bg=W95_BG)
        legend.pack(fill=tk.X, padx=8)
        for label, color in (
            (tr("egg_frag_blue"), FRAG_BLUE),
            (tr("egg_frag_red"), FRAG_RED),
            (tr("egg_frag_pink"), FRAG_PINK),
            (tr("egg_frag_yellow"), FRAG_YELLOW),
        ):
            row = tk.Frame(legend, bg=W95_BG)
            row.pack(side=tk.LEFT, padx=6)
            tk.Canvas(row, width=14, height=14, bg=color, highlightthickness=1,
                      highlightbackground=W95_SH).pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(row, text=label, font=FONT_SM, bg=W95_BG, fg=W95_FG).pack(side=tk.LEFT)

        self.canvas = tk.Canvas(
            self.frame, bg=W95_INPUT, relief=tk.SUNKEN, bd=2,
            highlightthickness=0, height=220,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<KeyPress>", self._key_down)
        self.canvas.bind("<KeyRelease>", self._key_up)
        self.canvas.focus_set()

        self.status = tk.Label(self.frame, text="", font=FONT, bg=W95_BG, fg=W95_FG)
        self.status.pack(pady=2)
        self.restart_lbl = tk.Label(self.frame, text="", font=FONT_SM, bg=W95_BG, fg=W95_SH)
        self.restart_lbl.pack(pady=2)

        tk.Button(
            self.frame, text=tr("egg_game_restart"), font=FONT, bg=W95_BTN, fg=W95_FG,
            relief=tk.RAISED, bd=2, command=self.start_round,
        ).pack(pady=4)

    def _on_resize(self, _event=None):
        self._draw()

    def _key_down(self, event):
        k = event.keysym.lower()
        if k in ("a", "left", "d", "right"):
            self.keys.add(k)

    def _key_up(self, event):
        k = event.keysym.lower()
        self.keys.discard(k)

    def start_round(self):
        if self.tick_id:
            try:
                self.app.root.after_cancel(self.tick_id)
            except tk.TclError:
                pass
            self.tick_id = None

        self.game_over = False
        self.progress = 0.0
        self.fragments = []
        self.restart_left = 0.0
        self.flash_text = ""
        self.flash_until = 0
        self.spawn_timer = 0
        w = max(self.canvas.winfo_width(), 200)
        self.catcher_x = (w - self.BAR_W) // 2
        self.restart_lbl.config(text="")
        self.status.config(text=tr("egg_game_running"))
        self.canvas.focus_set()
        self._draw()
        self._schedule_tick()

    def _spawn_fragment(self):
        w = max(self.canvas.winfo_width(), 1)
        kind, color, delta, _tag = random.choices(
            FRAGMENT_TYPES, weights=FRAG_WEIGHTS, k=1,
        )[0]
        self.fragments.append({
            "x": random.randint(4, max(4, w - self.FRAG_W - 4)),
            "y": -self.FRAG_H,
            "vy": random.uniform(2.2, 4.2),
            "kind": kind,
            "color": color,
            "delta": delta,
        })

    def _move_catcher(self):
        w = max(self.canvas.winfo_width(), 1)
        speed = 7
        if "a" in self.keys or "left" in self.keys:
            self.catcher_x -= speed
        if "d" in self.keys or "right" in self.keys:
            self.catcher_x += speed
        self.catcher_x = max(2, min(w - self.BAR_W - 2, self.catcher_x))

    def _catcher_y(self):
        h = max(self.canvas.winfo_height(), 1)
        return h - self.BAR_H - 8

    def _hit_test(self, frag):
        cx, cy = self.catcher_x, self._catcher_y()
        return (
            frag["x"] < cx + self.BAR_W
            and frag["x"] + self.FRAG_W > cx
            and frag["y"] + self.FRAG_H > cy
            and frag["y"] < cy + self.BAR_H
        )

    def _apply_fragment(self, frag):
        kind = frag["kind"]
        if kind == "blue":
            self.progress = min(100.0, self.progress + 5)
            self.flash_text = "+5%"
        elif kind == "pink":
            self.progress = max(0.0, self.progress - 5)
            self.flash_text = tr("egg_frag_minus")
        elif kind == "yellow":
            self.progress = max(0.0, self.progress - 2)
            self.flash_text = tr("egg_frag_bad")
        elif kind == "red":
            self.game_over = True
            self.flash_text = tr("egg_game_bsod")
            self.status.config(text=tr("egg_game_bsod"))
        self.flash_until = 25

    def _tick(self):
        self.tick_id = None
        if not self.frame.winfo_exists():
            return

        if self.restart_left > 0:
            self.restart_left = max(0.0, self.restart_left - (self.TICK_MS / 1000.0))
            secs = int(self.restart_left) + 1
            self.restart_lbl.config(text=tr("egg_game_restart_in").format(secs))
            if self.restart_left <= 0:
                self.start_round()
                return
            self._draw()
            self._schedule_tick()
            return

        if not self.game_over:
            self._move_catcher()
            self.spawn_timer += 1
            if self.spawn_timer >= 18:
                self.spawn_timer = 0
                self._spawn_fragment()

            alive = []
            for frag in self.fragments:
                frag["y"] += frag["vy"]
                if self._hit_test(frag):
                    self._apply_fragment(frag)
                    if self.game_over:
                        break
                    continue
                h = self.canvas.winfo_height()
                if frag["y"] < h + 10:
                    alive.append(frag)
            self.fragments = alive

            if self.flash_until > 0:
                self.flash_until -= 1

            if self.progress >= 100:
                self.status.config(text=tr("egg_game_win"))
                self.game_over = True
                self.restart_left = 8.0
                self.restart_lbl.config(text=tr("egg_game_restart_in").format(8))

            if self.game_over and self.progress < 100:
                self.restart_left = 5.0
                self.restart_lbl.config(text=tr("egg_game_restart_in").format(5))

        self._draw()
        self._schedule_tick()

    def _schedule_tick(self):
        if self.tick_id:
            self.app.root.after_cancel(self.tick_id)
        self.tick_id = self.app.root.after(self.TICK_MS, self._tick)

    def _draw(self):
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), 1)
        h = max(c.winfo_height(), 1)

        # Main progress track (top)
        track_y = 12
        track_h = 18
        c.create_rectangle(12, track_y, w - 12, track_y + track_h, fill="#808080", outline="")
        fill_w = int((w - 24) * (self.progress / 100.0))
        if fill_w > 0:
            c.create_rectangle(12, track_y, 12 + fill_w, track_y + track_h, fill="#0000A8", outline="")
        c.create_text(w // 2, track_y + track_h // 2, text=f"{int(self.progress)}%",
                      fill="white", font=("Terminal", 9, "bold"))

        # Falling fragments
        for frag in self.fragments:
            x, y = frag["x"], frag["y"]
            c.create_rectangle(
                x, y, x + self.FRAG_W, y + self.FRAG_H,
                fill=frag["color"], outline="black",
            )
            if frag["kind"] == "pink":
                c.create_text(x + self.FRAG_W // 2, y + self.FRAG_H // 2,
                              text="−", fill="white", font=("Terminal", 10, "bold"))
            elif frag["kind"] == "red":
                c.create_text(x + self.FRAG_W // 2, y + self.FRAG_H // 2,
                              text="!", fill="white", font=("Terminal", 10, "bold"))

        # Player-controlled progress bar (catcher)
        cx, cy = self.catcher_x, self._catcher_y()
        c.create_rectangle(cx, cy, cx + self.BAR_W, cy + self.BAR_H, fill="#C0C0C0", outline="black")
        c.create_line(cx, cy, cx + self.BAR_W, cy, fill="white")
        c.create_line(cx, cy, cx, cy + self.BAR_H, fill="white")
        c.create_line(cx + self.BAR_W, cy, cx + self.BAR_W, cy + self.BAR_H, fill="#404040")
        c.create_line(cx, cy + self.BAR_H, cx + self.BAR_W, cy + self.BAR_H, fill="#404040")
        inner = cx + 4
        c.create_rectangle(inner, cy + 4, inner + self.BAR_W - 12, cy + self.BAR_H - 6,
                           fill="#0000A8", outline="")

        if self.flash_until > 0 and self.flash_text:
            c.create_text(w // 2, h // 2, text=self.flash_text,
                          fill="#000080", font=("Terminal", 16, "bold"))

        if self.game_over and self.progress >= 100:
            c.create_rectangle(20, h // 2 - 24, w - 20, h // 2 + 24, fill="#C0C0C0", outline="black")
            c.create_text(w // 2, h // 2, text=tr("egg_game_win"), font=("Terminal", 12, "bold"))

    def destroy(self):
        if self.tick_id:
            try:
                self.app.root.after_cancel(self.tick_id)
            except tk.TclError:
                pass
            self.tick_id = None
        if self.frame.winfo_exists():
            self.frame.destroy()
