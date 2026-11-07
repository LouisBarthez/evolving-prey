"""
Headless training of the size / speed evolution: runs many generations without
a window, saves a CSV, a plot and (optionally) GIFs of the first and last generation.

    python train.py --pattern 0 --generations 40 --seed 1 --gif
"""
import argparse
import csv
import os
import random

from simulation import (PATTERNS, World, average_fitness, next_generation, random_genome,
                        stats, WIDTH, HEIGHT)


def render_gif(genomes, pattern, path, label, max_frames=450, every=3):
    from PIL import Image, ImageDraw
    world = World(genomes, pattern, max_frames)
    frames = []
    while not world.done:
        world.step()
        if world.frame % every and not world.done:
            continue
        img = Image.new("RGB", (WIDTH, HEIGHT), "black")
        d = ImageDraw.Draw(img)
        for group, color in [(world.enemies, (229, 72, 77)), (world.alive, (59, 130, 246))]:
            for o in group:
                r = o.diameter / 2
                d.ellipse([o.x - r, o.y - r, o.x + r, o.y + r], fill=color)
        d.text((10, 10), f"{label}   alive {len(world.alive)}/{len(world.prey)}", fill="white",
               font_size=22)
        frames.append(img.resize((WIDTH // 2, HEIGHT // 2), Image.LANCZOS))
    frames += [frames[-1]] * 15
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=40, loop=0)


def plot(rows, path, pattern):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    g = [r["generation"] for r in rows]
    fig, ax = plt.subplots(1, 4, figsize=(16, 3.6))
    ax[0].plot(g, [r["mean_time"] for r in rows], label="mean", color="tab:blue")
    ax[0].plot(g, [r["best_time"] for r in rows], label="best", color="tab:blue", alpha=.35)
    ax[0].set_title("Survival time (frames)"); ax[0].legend()
    ax[1].plot(g, [r["mean_size"] for r in rows], color="tab:green")
    ax[1].set_title("Mean prey size (px)")
    ax[2].plot(g, [r["mean_speed"] for r in rows], color="tab:orange")
    ax[2].set_title("Mean prey speed (px/frame)")
    ax[3].plot(g, [r["angle_spread"] for r in rows], color="tab:purple")
    ax[3].set_title("Spread of launch directions (deg)")
    for a in ax:
        a.set_xlabel("generation"); a.grid(alpha=.3)
    fig.suptitle(f"Predators: {PATTERNS[pattern]}")
    fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description="Headless size/speed evolution")
    ap.add_argument("--pattern", type=int, default=0, choices=PATTERNS,
                    help=" | ".join(f"{k}: {v}" for k, v in PATTERNS.items()))
    ap.add_argument("--generations", type=int, default=40)
    ap.add_argument("--population", type=int, default=30)
    ap.add_argument("--episodes", type=int, default=5, help="runs per generation (fitness = mean)")
    ap.add_argument("--max-frames", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results")
    ap.add_argument("--gif", action="store_true", help="also save GIFs of the first and last generation")
    args = ap.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out, exist_ok=True)
    genomes = [random_genome() for _ in range(args.population)]
    first, rows = genomes, []

    for gen in range(args.generations):
        prey = average_fitness(genomes, args.pattern, args.episodes, args.max_frames)
        rows.append(stats(prey, gen))
        r = rows[-1]
        print(f"gen {gen:3d} | survival {r['mean_time']:6.0f} (best {r['best_time']:5.0f}) "
              f"| size {r['mean_size']:5.1f} | speed {r['mean_speed']:5.2f} | direction spread {r['angle_spread']:4.0f}")
        last = genomes
        genomes = next_generation(prey, gen + 1, args.population)

    tag = f"pattern{args.pattern}"
    with open(os.path.join(args.out, f"{tag}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    plot(rows, os.path.join(args.out, f"{tag}.png"), args.pattern)
    print(f"saved {args.out}/{tag}.csv and {tag}.png")
    if args.gif:
        render_gif(first, args.pattern, os.path.join(args.out, f"{tag}_gen0.gif"), "generation 0")
        render_gif(last, args.pattern, os.path.join(args.out, f"{tag}_last.gif"),
                   f"generation {args.generations - 1}")
        print(f"saved {tag}_gen0.gif and {tag}_last.gif")


if __name__ == "__main__":
    main()
