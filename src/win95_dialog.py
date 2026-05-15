import tkinter as tk
from .constants import W95_BG, W95_FG, FONT
from .title_bar_util import bind_title_drag


class Win95Dialog:
    """Borderless Toplevel with Win95-style title bar (gradient + close button)."""

    def __init__(self, parent, title, width, height, app=None):
        self.app = app
        self._title = title
        self._close_rect = (0, 0, 0, 0)
        self._drag_start = (0, 0)
        self._win_pos = (0, 0)

        self.win = tk.Toplevel(parent)
        self.win.withdraw()
        self.win.overrideredirect(True)
        self.win.configure(bg=W95_BG)
        self.win.resizable(False, False)

        self.outer = tk.Frame(self.win, bg=W95_BG, bd=2, relief=tk.RAISED)
        self.outer.pack(fill=tk.BOTH, expand=True)

        self._build_title_bar()
        self.body = tk.Frame(self.outer, bg=W95_BG)
        self.body.pack(fill=tk.BOTH, expand=True)

        self.win.update_idletasks()
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        if pw > 1 and ph > 1:
            px = parent.winfo_rootx() + max(0, (pw - width) // 2)
            py = parent.winfo_rooty() + max(0, (ph - height) // 2)
        else:
            px = max(0, (sw - width) // 2)
            py = max(0, (sh - height) // 2)
        self.win.geometry(f"{width}x{height}+{px}+{py}")

        self.win.transient(parent)
        self.win.deiconify()
        self.win.lift()
        self.win.attributes("-topmost", True)
        self.win.after(80, lambda: self.win.attributes("-topmost", False))
        self.win.focus_force()
        self.win.grab_set()

        if app and hasattr(app, "_fix_taskbar"):
            self.win.after(50, lambda: app._fix_taskbar(self.win))

    def _build_title_bar(self):
        self.title_bar = tk.Frame(self.outer, height=26, bg="#000080")
        self.title_bar.pack(fill=tk.X, side=tk.TOP)
        self.title_bar.pack_propagate(False)

        self.tc = tk.Canvas(self.title_bar, height=26, highlightthickness=0, bg="#000080")
        self.tc.pack(fill=tk.BOTH, expand=True)
        self.tc.bind("<Configure>", self._redraw_title)
        bind_title_drag(self.tc, self._title_click, self._drag_win)
        self.title_bar.bind("<Button-1>", self._title_click)
        self.title_bar.bind("<B1-Motion>", self._drag_win)

    def _redraw_title(self, _event=None):
        self.tc.delete("all")
        w = self.tc.winfo_width()
        if w < 2:
            return
        h = 24
        bw = 8
        for x in range(0, w, bw):
            r = x / max(w, 1)
            red = int(0 + (79 - 0) * r)
            green = int(0 + (195 - 0) * r)
            blue = int(128 + (247 - 128) * r)
            self.tc.create_rectangle(x, 0, x + bw, h, fill=f"#{red:02x}{green:02x}{blue:02x}", outline="")
        self.tc.create_line(0, h - 1, w, h - 1, fill="white")
        self.tc.create_text(6, h // 2, text=f"  {self._title}",
                            font=("Terminal", 10), fill="white", anchor="w")

        btn_w, btn_h = 20, 18
        btn_y = (h - btn_h) // 2
        btn_x = w - btn_w - 3
        self._draw_btn(btn_x, btn_y, btn_w, btn_h, "✕")
        self._close_rect = (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h)
        bind_title_drag(self.tc, self._title_click, self._drag_win)

    def _draw_btn(self, x, y, w, h, text):
        self.tc.create_rectangle(x, y, x + w, y + h, fill="#C0C0C0", outline="")
        self.tc.create_line(x, y, x + w, y, fill="white")
        self.tc.create_line(x, y, x, y + h, fill="white")
        self.tc.create_line(x + w, y, x + w, y + h, fill="#808080")
        self.tc.create_line(x, y + h, x + w, y + h, fill="#808080")
        self.tc.create_text(x + w // 2, y + h // 2, text=text, font=("Terminal", 9), fill="black")

    def _title_click(self, ev):
        x1, y1, x2, y2 = self._close_rect
        if x2 > x1 and x1 <= ev.x <= x2 and y1 <= ev.y <= y2:
            self.close()
            return
        self._drag_start = (ev.x_root, ev.y_root)
        self._win_pos = (self.win.winfo_x(), self.win.winfo_y())

    def _drag_win(self, ev):
        dx = ev.x_root - self._drag_start[0]
        dy = ev.y_root - self._drag_start[1]
        self.win.geometry(f"+{self._win_pos[0] + dx}+{self._win_pos[1] + dy}")

    def close(self):
        try:
            self.win.grab_release()
        except tk.TclError:
            pass
        self.win.destroy()

    def wait(self):
        self.win.wait_window()
