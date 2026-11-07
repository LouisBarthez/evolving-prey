"""
Evolving prey: core simulation (no GUI).

Blue prey spawn in the middle of an arena full of red predators.
Each prey has a genome (size, speed, launch angle).
A prey's fitness is how long it survives. After every generation, the next
one is built around the survivors' genomes, weighted by survival_time ** 5,
plus a random mutation whose size adapts to how much the best individuals agree.

This is the core of the original Tkinter project (ia.py / test.py / alea.py),
separated from the display so it can also run headless and fast.
"""
import math
import random
from dataclasses import dataclass

import numpy as np

WIDTH, HEIGHT = 800, 600
CENTER = (WIDTH / 2, HEIGHT / 2)

ENEMY_DIAMETER = 20
ENEMY_SPEED = 5

MIN_SIZE, MAX_SIZE = 5, 60
MAX_SPEED = 10          # above this, prey could "tunnel" through predators between frames
FITNESS_EXPONENT = 5    # weight = survival_time ** 5 (from the original code)


# --------------------------------------------------------------------------
# Agents
# --------------------------------------------------------------------------
class MovingCircle:
    """A circle that moves in a straight line and bounces off the walls."""

    def __init__(self, x, y, diameter, dx, dy, genome=None):
        self.x, self.y = x, y
        self.diameter = diameter
        self.dx, self.dy = dx, dy
        self.genome = genome
        self.time = 0          # frames survived
        self.alive = True

    def move(self):
        self.x += self.dx
        self.y += self.dy
        r = self.diameter / 2
        # Bounce, and clamp the position so a circle never gets stuck in a wall
        if self.x - r < 0:
            self.x, self.dx = r, abs(self.dx)
        elif self.x + r > WIDTH:
            self.x, self.dx = WIDTH - r, -abs(self.dx)
        if self.y - r < 0:
            self.y, self.dy = r, abs(self.dy)
        elif self.y + r > HEIGHT:
            self.y, self.dy = HEIGHT - r, -abs(self.dy)


class OrbitingCircle(MovingCircle):
    """Predator of the closing ring (pattern 9): turns around the center while the ring shrinks."""

    def __init__(self, angle, radius, angular_speed, shrink=1.0, min_radius=0):
        self.angle, self.radius, self.w = angle, radius, angular_speed
        self.shrink, self.min_radius = shrink, min_radius
        super().__init__(*self._pos(), ENEMY_DIAMETER, 0, 0)

    def _pos(self):
        return (CENTER[0] + self.radius * math.cos(self.angle),
                CENTER[1] + self.radius * math.sin(self.angle))

    def move(self):
        self.angle += self.w
        self.radius = max(self.radius - self.shrink, self.min_radius)
        self.x, self.y = self._pos()


# --------------------------------------------------------------------------
# Predator patterns (from alea.py, ia.py and test.py)
# --------------------------------------------------------------------------
PATTERNS = {
    0: "random predators",
    1: "random diagonals from the borders",
    2: "border patrol",
    3: "wave right to left",
    4: "wave left to right",
    5: "wave top to bottom",
    6: "wave bottom to top",
    7: "swarm from a corner",
    8: "zigzag from the sides",
    9: "closing ring with one rotating gap",
}


def spawn_enemies(pattern, n=100):
    r, s = ENEMY_DIAMETER // 2, ENEMY_SPEED
    enemies = []

    def add(x, y, dx, dy):
        enemies.append(MovingCircle(x, y, ENEMY_DIAMETER, dx, dy))

    if pattern == 0:  # ia.py
        for _ in range(10):
            while True:
                x = random.randint(r, WIDTH - r)
                y = random.randint(r, HEIGHT - r)
                if math.hypot(x - CENTER[0], y - CENTER[1]) > 100:  # not on top of the prey
                    break
            add(x, y, random.choice([-s, s]), random.choice([-s, s]))

    elif pattern == 1:
        for _ in range(n):
            side = random.choice(["left", "right", "top", "bottom"])
            if side == "left":
                x, y = r, random.randint(r, HEIGHT - r)
            elif side == "right":
                x, y = WIDTH - r, random.randint(r, HEIGHT - r)
            elif side == "top":
                x, y = random.randint(r, WIDTH - r), r
            else:
                x, y = random.randint(r, WIDTH - r), HEIGHT - r
            add(x, y, random.choice([-s, s]), random.choice([-s, s]))

    elif pattern == 2:  # test.py: each border has balls sliding along it
        for _ in range(n // 4):
            add(WIDTH - r, random.randint(r, HEIGHT - r), 0, random.choice([-s, s]))
            add(r, random.randint(r, HEIGHT - r), 0, random.choice([-s, s]))
            add(random.randint(r, WIDTH - r), r, random.choice([-s, s]), 0)
            add(random.randint(r, WIDTH - r), HEIGHT - r, random.choice([-s, s]), 0)

    elif pattern == 3:
        for _ in range(n):
            add(WIDTH - r, random.randint(r, HEIGHT - r), -s, 0)
    elif pattern == 4:
        for _ in range(n):
            add(r, random.randint(r, HEIGHT - r), s, 0)
    elif pattern == 5:
        for _ in range(n):
            add(random.randint(r, WIDTH - r), r, 0, s)
    elif pattern == 6:
        for _ in range(n):
            add(random.randint(r, WIDTH - r), HEIGHT - r, 0, -s)

    elif pattern == 7:
        for _ in range(n):
            add(r, HEIGHT - r, s, -s)

    elif pattern == 8:
        for _ in range(n):
            x = random.choice([r, WIDTH - r])
            add(x, random.randint(r, HEIGHT - r), s if x == r else -s, random.choice([-s, s]))

    elif pattern == 9:
        # A ring closes on the prey. A gap of 12 missing predators (~43 degrees) turns
        # with the ring: to escape, a prey must aim where the gap *will be* when it
        # reaches the ring, so the right angle depends on its speed.
        start = 0.0   # same gap every time, otherwise there is no right direction to learn
        for i in range(n):
            if i < 12:
                continue
            enemies.append(OrbitingCircle(start + 2 * math.pi * i / n, 260, 0.012))

    else:
        raise ValueError(f"unknown pattern {pattern}")
    return enemies


# --------------------------------------------------------------------------
# Genome and evolution
# --------------------------------------------------------------------------
@dataclass
class Genome:
    size: float     # diameter            ("taille" in the original code)
    speed: float    # px / frame          ("vitesse" in the original code)
    angle: float    # launch direction, degrees


def clamp_genome(g):
    g.size = min(max(g.size, MIN_SIZE), MAX_SIZE)
    g.speed = min(max(g.speed, 0), MAX_SPEED)
    g.angle %= 360
    return g


def random_genome():
    """Same initialisation as the original code: random size, speed and direction."""
    return Genome(random.randint(5, 50), random.randint(1, 10), random.uniform(0, 360))


# Smallest mutation allowed for each gene, so the population never freezes completely
MIN_MUTATION = {"size": 0.3, "speed": 0.03, "angle": 1.0}


def weighted_mean_std(values, w):
    c = sum(w)
    m = sum(wi * v for wi, v in zip(w, values)) / c
    var = sum(wi * (v - m) ** 2 for wi, v in zip(w, values)) / c
    return m, math.sqrt(var)


def weighted_circular_mean_std(angles, w):
    """Angles wrap around (359 and 1 degrees are neighbours): average unit vectors."""
    c = sum(w)
    s = sum(wi * math.sin(math.radians(a)) for wi, a in zip(w, angles)) / c
    co = sum(wi * math.cos(math.radians(a)) for wi, a in zip(w, angles)) / c
    R = min(max(math.hypot(s, co), 1e-12), 1.0)
    return math.degrees(math.atan2(s, co)), math.degrees(math.sqrt(-2 * math.log(R)))


def next_generation(prey, gen, n):
    """
    Build generation `gen` from the previous prey.

    Recombination: parent = mean genome weighted by survival_time ** 5
    (m_taillec / m_dxc / m_dyc in the original code).

    Adaptive mutation: child = parent + exponential noise with a random sign
    (as in the original code), but the noise scale is the weighted spread of the
    population. When the best individuals agree, the spread is small and the
    population tightens around them; when they disagree (or a gene doesn't
    matter), it stays large and keeps exploring.
    """
    tmax = max(p.time for p in prey) or 1
    w = [(p.time / tmax) ** FITNESS_EXPONENT for p in prey]  # normalised: no overflow
    if sum(w) == 0:
        w = [1.0] * len(prey)
    m_size, s_size = weighted_mean_std([p.genome.size for p in prey], w)
    m_speed, s_speed = weighted_mean_std([p.genome.speed for p in prey], w)
    m_angle, s_angle = weighted_circular_mean_std([p.genome.angle for p in prey], w)
    s_size = max(s_size, MIN_MUTATION["size"])
    s_speed = max(s_speed, MIN_MUTATION["speed"])
    s_angle = max(s_angle, MIN_MUTATION["angle"])

    noise = lambda scale: random.expovariate(1 / scale) * random.choice([-1, 1])
    return [clamp_genome(Genome(m_size + noise(s_size), m_speed + noise(s_speed),
                                m_angle + noise(s_angle))) for _ in range(n)]


# --------------------------------------------------------------------------
# World: one generation
# --------------------------------------------------------------------------
class World:
    def __init__(self, genomes, pattern, max_frames=1500):
        self.pattern = pattern
        self.max_frames = max_frames
        self.frame = 0
        self.enemies = spawn_enemies(pattern)
        self.prey = []
        for g in genomes:
            a = math.radians(g.angle)
            self.prey.append(MovingCircle(*CENTER, g.size, g.speed * math.cos(a),
                                          g.speed * math.sin(a), genome=g))

    @property
    def alive(self):
        return [p for p in self.prey if p.alive]

    @property
    def done(self):
        return self.frame >= self.max_frames or not self.alive

    def step(self):
        self.frame += 1
        for e in self.enemies:
            e.move()
        ex = np.array([e.x for e in self.enemies])
        ey = np.array([e.y for e in self.enemies])
        for p in self.alive:   # list copy: safe to kill prey while looping
            p.move()
            dist = np.hypot(ex - p.x, ey - p.y)
            if np.any(dist < (ENEMY_DIAMETER + p.diameter) / 2):
                p.alive = False
                p.time = self.frame
        if self.done:
            for p in self.alive:   # survived until the end
                p.time = self.frame

    def run(self):
        while not self.done:
            self.step()
        return self.prey


def average_fitness(genomes, pattern, extra_runs, max_frames, first_run=None):
    """
    Fitness = survival time averaged over several independent worlds (new random
    predators each time). This removes a lot of the luck.
    `first_run` lets the viewer reuse the world it just displayed.
    """
    runs = [first_run] if first_run is not None else []
    runs += [World(genomes, pattern, max_frames).run() for _ in range(extra_runs)]
    prey = runs[0]
    for i, p in enumerate(prey):
        p.time = sum(run[i].time for run in runs) / len(runs)
    return prey


def stats(prey, gen):
    return {
        "generation": gen,
        "mean_size": sum(p.genome.size for p in prey) / len(prey),
        "mean_speed": sum(p.genome.speed for p in prey) / len(prey),
        "angle_spread": weighted_circular_mean_std([p.genome.angle for p in prey], [1] * len(prey))[1],
        "mean_time": sum(p.time for p in prey) / len(prey),
        "best_time": max(p.time for p in prey),
    }
