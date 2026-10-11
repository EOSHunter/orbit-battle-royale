"""Glow shrub: a luminous Ringfall bush with teal and lime glowing buds.
Concept: codex/concepts/v0.2/30-luminous-vegetation.png (glowing bud bushes).

About 1.4 m across and 1.1 m tall: woody forked stems, small cupped sage-teal
leaves and clusters of glowing teal buds with a few lime ones.
Origin at the base center.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)


def build():
    rng = random.Random(17)
    m = E.Model("veg-glow-shrub", category="vegetation", bevel=0.004, cage=0.012)
    tips = []
    for i in range(6):
        a = 2 * math.pi * i / 6 + rng.uniform(-0.3, 0.3)
        lean = rng.uniform(0.25, 0.5)
        H = rng.uniform(0.75, 1.05)
        d = (math.cos(a), math.sin(a))
        p0 = (d[0] * 0.04, d[1] * 0.04, -0.05)
        p1 = (d[0] * lean * 0.35, d[1] * lean * 0.35, H * 0.45)
        p2 = (d[0] * lean * 0.8, d[1] * lean * 0.8, H)
        E.sweep(m, [p0, p1, p2], [0.028, 0.018, 0.008], "stem", sides=4)
        tips.append((p2, d))
        # Two forks per stem.
        for k, t in enumerate((0.5, 0.75)):
            base = tuple(p1[j] + (p2[j] - p1[j]) * (t - 0.4) for j in range(3))
            side = (k * 2 - 1) * rng.uniform(0.6, 1.0)
            ax = (d[0] * math.cos(side) - d[1] * math.sin(side), d[0] * math.sin(side) + d[1] * math.cos(side))
            L = rng.uniform(0.22, 0.35)
            tip = (base[0] + ax[0] * L, base[1] + ax[1] * L, base[2] + L * 0.8)
            E.sweep(m, [base, tip], [0.01, 0.005], "stem", sides=3)
            tips.append((tip, ax))
    # Leaves along the upper stems, buds at every tip.
    for n, (tip, d) in enumerate(tips):
        for j in range(2 if n % 3 == 0 else 1):
            a = math.atan2(d[1], d[0]) + rng.uniform(-1.6, 1.6)
            base = (tip[0] - d[0] * rng.uniform(0.05, 0.2), tip[1] - d[1] * rng.uniform(0.05, 0.2), tip[2] - rng.uniform(0.08, 0.3))
            L = rng.uniform(0.1, 0.16)
            end = (base[0] + math.cos(a) * L, base[1] + math.sin(a) * L, base[2] + L * 0.45)
            E.leaf(m, base, end, L * 0.32, "leaf_teal" if rng.random() < 0.6 else "leaf_sage", normal=(0, 0, 1))
        for j in range(2):
            off = (rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), rng.uniform(-0.04, 0.03))
            b0 = (tip[0] + off[0], tip[1] + off[1], tip[2] + off[2])
            L = rng.uniform(0.05, 0.09)
            glow = "glow_lime" if rng.random() < 0.2 else "glow_teal"
            E.bud(m, b0, (b0[0] + off[0] * 0.6, b0[1] + off[1] * 0.6, b0[2] + L), L * 0.38, glow)
    return m.finish(BUDGET, texture_size=512)
