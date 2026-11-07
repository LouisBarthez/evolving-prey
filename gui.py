"""Small Tkinter helpers shared by the two viewers: colours, live charts, keyboard."""
import math

BG = "#0d1117"
PANEL = "#161b22"
GRID = "#30363d"
FG = "#e6edf3"
MUTED = "#8b949e"
BLUE = "#3b82f6"
RED = "#e5484d"
GOLD = "#f5c542"
GREEN = "#3fb950"
ORANGE = "#f0883e"

FONT = ("Helvetica", 11)
FONT_SMALL = ("Helvetica", 9)
FONT_BIG = ("Helvetica", 18, "bold")


class MiniChart:
    """A tiny line chart drawn on a Tk canvas, redrawn after every generation."""

    def __init__(self, canvas, x, y, w, h, title, color, log=False, fmt="{:.1f}", ref=None):
        self.c, self.x, self.y, self.w, self.h = canvas, x, y, w, h
        self.title, self.color, self.log, self.fmt, self.ref = title, color, log, fmt, ref
        self.tag = f"chart_{id(self)}"
        self.update([])

    def _t(self, v):
        return math.log10(max(v, 1e-3)) if self.log else v

    def update(self, values, second=None):
        c, tag = self.c, self.tag
        c.delete(tag)
        last = self.fmt.format(values[-1]) if values else "-"
        c.create_text(self.x, self.y, anchor="nw", text=self.title, fill=MUTED, font=FONT_SMALL, tags=tag)
        c.create_text(self.x + self.w, self.y, anchor="ne", text=last, fill=self.color,
                      font=("Helvetica", 11, "bold"), tags=tag)
        top, bottom = self.y + 18, self.y + self.h
        c.create_rectangle(self.x, top, self.x + self.w, bottom, outline=GRID, tags=tag)
        series = [s for s in (values, second) if s]
        if not series:
            return
        allv = [self._t(v) for s in series for v in s]
        if self.ref is not None:
            allv.append(self._t(self.ref))
        lo, hi = min(allv), max(allv)
        if hi - lo < 1e-9:
            lo, hi = lo - 1, hi + 1
        n = max(len(values), 2)

        def px(i, v):
            return (self.x + 4 + (self.w - 8) * i / (n - 1),
                    bottom - 4 - (bottom - top - 8) * (self._t(v) - lo) / (hi - lo))

        if self.ref is not None:
            _, yr = px(0, self.ref)
            c.create_line(self.x, yr, self.x + self.w, yr, fill=GOLD, dash=(3, 3), tags=tag)
        for s, col, width in ((second, "#6b8fc9", 1), (values, self.color, 2)):
            if s and len(s) > 1:
                c.create_line(*[k for i, v in enumerate(s) for k in px(i, v)], fill=col,
                              width=width, tags=tag)
            elif s:
                x0, y0 = px(0, s[0])
                c.create_oval(x0 - 2, y0 - 2, x0 + 2, y0 + 2, fill=col, outline="", tags=tag)


def bind_keys(root, handlers):
    """Keyboard shortcuts that work whatever the case (Caps Lock) and whatever has focus."""
    def on_key(event):
        action = handlers.get(event.keysym.lower())
        if action:
            action()
    root.bind_all("<Key>", on_key)
    root.focus_force()


def overlay(canvas, cx, cy, title, lines, hint):
    """Centered summary box shown at the end of a generation."""
    w, h = 380, 70 + 24 * len(lines)
    canvas.create_rectangle(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=PANEL,
                            outline=GRID, width=2, tags="overlay")
    canvas.create_text(cx, cy - h / 2 + 22, text=title, fill=FG, font=FONT_BIG, tags="overlay")
    for i, line in enumerate(lines):
        canvas.create_text(cx, cy - h / 2 + 54 + 24 * i, text=line, fill=FG, font=FONT, tags="overlay")
    canvas.create_text(cx, cy + h / 2 - 14, text=hint, fill=MUTED, font=FONT_SMALL, tags="overlay")
