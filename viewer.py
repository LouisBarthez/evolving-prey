"""
Live Tkinter view of the size / speed evolution.

    python viewer.py --pattern 2

Keys: Space = next generation, A = auto mode, F = fast mode,
      R = restart, Q / Esc = quit
"""
import argparse
import random
import tkinter as tk

import gui
from gui import BG, PANEL, FG, MUTED, BLUE, RED, GREEN, ORANGE
from simulation import (PATTERNS, World, average_fitness, next_generation, random_genome,
                        stats, WIDTH, HEIGHT)

PANEL_W = 280


class Viewer:
    def __init__(self, root, args):
        self.root, self.args = root, args
        root.configure(bg=BG)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=0)
        self.panel = tk.Canvas(root, width=PANEL_W, height=HEIGHT, bg=PANEL, highlightthickness=0)
        self.panel.grid(row=0, column=1)

        p = self.panel
        p.create_text(16, 16, anchor="nw", text="Evolving prey", fill=FG, font=gui.FONT_BIG)
        p.create_text(16, 46, anchor="nw", width=PANEL_W - 30, fill=MUTED, font=gui.FONT_SMALL,
                      text=f"Predators: {PATTERNS[args.pattern]}\n"
                           f"Genes: size, speed, direction  |  population {args.population}")
        w = PANEL_W - 32
        self.charts = {
            "time": gui.MiniChart(p, 16, 92, w, 92, "Survival time (frames)  mean / best", BLUE, fmt="{:.0f}"),
            "size": gui.MiniChart(p, 16, 200, w, 92, "Mean size (px)", GREEN),
            "speed": gui.MiniChart(p, 16, 308, w, 92, "Mean speed (px/frame)", ORANGE, fmt="{:.2f}"),
        }
        self.status = p.create_text(16, 418, anchor="nw", fill=FG, font=gui.FONT, text="")
        p.create_text(16, HEIGHT - 16, anchor="sw", fill=MUTED, font=gui.FONT_SMALL,
                      text="Space  next generation\nA  auto mode\nF  fast mode\nR  restart\nQ  quit")

        gui.bind_keys(root, {"space": self.next, "a": self.toggle_auto, "f": self.toggle_fast,
                             "r": self.restart, "q": root.destroy, "escape": root.destroy})
        self.auto, self.fast = args.auto, False
        self.restart()

    # -- controls ---------------------------------------------------------
    def toggle_auto(self):
        self.auto = not self.auto
        self._update_status()
        if self.auto and self.paused:
            self.next()

    def toggle_fast(self):
        self.fast = not self.fast
        self._update_status()

    def restart(self):
        if getattr(self, "job", None):
            self.root.after_cancel(self.job)
        self.gen, self.history = 0, []
        self.genomes = [random_genome() for _ in range(self.args.population)]
        for ch in self.charts.values():
            ch.update([])
        self.start_generation()

    def _update_status(self):
        on = lambda b: "ON" if b else "off"
        self.panel.itemconfig(self.status, text=f"Generation {self.gen}\n"
                              f"Auto: {on(self.auto)}    Fast: {on(self.fast)}")

    # -- simulation loop ---------------------------------------------------
    def start_generation(self):
        self.paused = False
        c = self.canvas
        c.delete("all")
        self.world = World(self.genomes, self.args.pattern, self.args.max_frames)
        self.items = {}
        for e in self.world.enemies:
            self.items[e] = self._circle(e, RED)
        for prey in self.world.prey:
            self.items[prey] = self._circle(prey, BLUE)
        self.hud = c.create_text(10, 10, anchor="nw", fill=FG, font=gui.FONT, text="")
        self._update_status()
        self.loop()

    def _circle(self, o, color):
        r = o.diameter / 2
        return self.canvas.create_oval(o.x - r, o.y - r, o.x + r, o.y + r, fill=color, outline="")

    def loop(self):
        for _ in range(10 if self.fast else 1):
            self.world.step()
            if self.world.done:
                break
        for o, item in self.items.items():
            if not o.alive:
                self.canvas.itemconfig(item, state="hidden")
            else:
                r = o.diameter / 2
                self.canvas.coords(item, o.x - r, o.y - r, o.x + r, o.y + r)
        self.canvas.itemconfig(self.hud, text=f"Generation {self.gen}    alive {len(self.world.alive)}"
                                              f"/{self.args.population}    frame {self.world.frame}")
        if self.world.done:
            self.end_generation()
        else:
            self.job = self.root.after(5, self.loop)

    def end_generation(self):
        self.job = None
        self.canvas.itemconfig(self.hud, text=f"Generation {self.gen}: evaluating...")
        self.root.update_idletasks()
        # Fitness = mean over the run you just watched + a few hidden runs
        self.prey = average_fitness(self.genomes, self.args.pattern, self.args.episodes - 1,
                                    self.args.max_frames, first_run=self.world.prey)
        s = stats(self.prey, self.gen)
        self.history.append(s)
        h = self.history
        self.charts["time"].update([r["mean_time"] for r in h], [r["best_time"] for r in h])
        self.charts["size"].update([r["mean_size"] for r in h])
        self.charts["speed"].update([r["mean_speed"] for r in h])
        self.paused = True
        gui.overlay(self.canvas, WIDTH / 2, HEIGHT / 2, f"Generation {self.gen}",
                    [f"Mean survival: {s['mean_time']:.0f} frames",
                     f"Mean size: {s['mean_size']:.1f} px",
                     f"Mean speed: {s['mean_speed']:.2f} px/frame"],
                    f"fitness averaged over {self.args.episodes} runs   |   Space: next")
        if self.auto:
            self.job = self.root.after(400, self.next)

    def next(self):
        if not self.paused:
            return
        self.gen += 1
        self.genomes = next_generation(self.prey, self.gen, self.args.population)
        self.start_generation()


def main():
    ap = argparse.ArgumentParser(description="Live view of the size/speed evolution")
    ap.add_argument("--pattern", type=int, default=0, choices=PATTERNS,
                    help=" | ".join(f"{k}: {v}" for k, v in PATTERNS.items()))
    ap.add_argument("--population", type=int, default=30)
    ap.add_argument("--episodes", type=int, default=5, help="runs per generation (fitness = mean)")
    ap.add_argument("--max-frames", type=int, default=1500)
    ap.add_argument("--auto", action="store_true", help="start in auto mode")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    root = tk.Tk()
    root.title(f"Evolving prey | {PATTERNS[args.pattern]}")
    root.resizable(False, False)
    Viewer(root, args)
    root.mainloop()


if __name__ == "__main__":
    main()
