"""Luminous roots: a mossy earth mound laced with glowing cyan roots.
Concept: codex/concepts/v0.2/30-luminous-vegetation.png (bottom-left root mounds).

About 3 x 2.6 m and 0.6 m high: ground-cover prop that hides terrain seams.
Thick bark roots creep over the mound with glowing veins baked along their
backs; thin branching rootlets glow cyan. A few stones poke through.
Origin at the base center.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)
RX, RF, RU = 1.5, 1.3, 0.45


def ground(x, f):
    q = 1 - (x / RX) ** 2 - (f / RF) ** 2
    return RU * math.sqrt(max(q, 0.0)) * 0.92 - 0.06


def path(rng, start_a, length, n, start_r=0.15, wander=0.5):
    a = start_a
    x, f = start_r * math.cos(a), start_r * math.sin(a)
    pts = []
    for i in range(n):
        pts.append((x, f))
        a += rng.uniform(-wander, wander) / n * 2
        step = length / (n - 1)
        x += math.cos(a) * step
        f += math.sin(a) * step
    return pts


def build():
    rng = random.Random(67)
    m = E.Model("veg-luminous-roots", category="vegetation", bevel=0.006, cage=0.035)
    mound = E.rock(m, (0, 0, -0.06), (RX, RF, RU), "soil", seed=3, subdiv=2, cuts=2, cut_depth=0.1, bumps=0.07,
                   floor=-0.05, top_mat="moss_dark", top_thresh=0.75, top_prob=0.6)
    for i, (x, f, r) in enumerate(((0.7, -0.4, 0.22), (-0.6, 0.55, 0.28), (-0.2, -0.75, 0.16))):
        E.rock(m, (x, f, ground(x, f) - 0.02), (r * 1.2, r, r * 0.8), "rock_gray", seed=10 + i, subdiv=1, cuts=3, floor=-0.3,
               top_mat="moss", top_prob=0.5)
    for j in range(6):
        a = 2 * math.pi * j / 6 + rng.uniform(-0.3, 0.3)
        L = rng.uniform(1.1, 1.7)
        flat = path(rng, a, L, 5)
        r0 = rng.uniform(0.05, 0.075)
        radii = [r0, r0 * 0.8, r0 * 0.6, r0 * 0.4, 0.0]
        pts = [(x, f, ground(x, f) + rr * 0.45) for (x, f), rr in zip(flat, radii)]
        pts[0] = (pts[0][0], pts[0][1], pts[0][2] + 0.08)
        E.sweep(m, pts, radii, "bark_dark", sides=5, tip=True, flat=0.7)
        # Glowing vein along the root's back (baked).
        back = [(p[0], p[1], p[2] + rr * 0.7 + 0.004) for p, rr in zip(pts[:-1], radii[:-1])]
        E.sweep(m, back, [0.012, 0.011, 0.009, 0.007], "glow_cyan", sides=3, detail=True)
        # Glowing rootlets branching off.
        for k in (1, 2):
            bx, bf = flat[k]
            ba = a + rng.choice((-1, 1)) * rng.uniform(0.6, 1.2)
            bl = path(rng, ba, rng.uniform(0.35, 0.6), 4, start_r=0.0, wander=1.0)
            bpts = [(bx + x, bf + f, ground(bx + x, bf + f) + 0.012) for x, f in bl]
            E.sweep(m, bpts, [0.022, 0.016, 0.01, 0.0], "glow_cyan", sides=3, tip=True)
            twig = bl[-2]
            tl = path(rng, ba + rng.uniform(-1, 1), 0.25, 3, start_r=0.0, wander=1.0)
            tpts = [(bx + twig[0] + x, bf + twig[1] + f, ground(bx + twig[0] + x, bf + twig[1] + f) + 0.01) for x, f in tl]
            E.sweep(m, tpts, [0.012, 0.008, 0.0], "glow_cyan", sides=3, tip=True)
    # Moss tufts (baked) on the mound.
    for _ in range(10):
        x, f = rng.uniform(-1.1, 1.1), rng.uniform(-0.9, 0.9)
        E.rock(m, (x, f, ground(x, f) - 0.015), (0.12, 0.1, 0.03), "moss", seed=rng.randint(0, 999), subdiv=1, cuts=0, detail=True)
    return m.finish(BUDGET, texture_size=1024)
