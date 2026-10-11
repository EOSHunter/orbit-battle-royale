"""Bloomwild tree, trunk: the twisting trunk and buttress roots of a canopy tree.
Concept: codex/concepts/v0.2/36-bloomwild.png (giant mushroom-canopy trees,
roots threaded with glowing cyan veins).

Pairs with veg-tree-canopy: both share the same origin (base center on the
ground), place them with the same transform. Trunk rises 9.2 m and flares to
meet the canopy. Dark bark, braided side strands carrying glowing veins
(baked), six buttress roots spreading about 3.5 m. Origin at the base center.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)
SPINE = [(0.0, 0.0, -0.2), (0.1, 0.0, 1.5), (0.3, 0.1, 3.5), (0.2, 0.25, 5.5), (-0.1, 0.12, 7.5), (0.0, 0.0, 9.25)]
RADII = [1.15, 0.85, 0.68, 0.62, 0.66, 0.95]


def spine_at(t):
    """Point and radius along the trunk spine, t in 0..1."""
    s = t * (len(SPINE) - 1)
    i = min(int(s), len(SPINE) - 2)
    w = s - i
    p = tuple(SPINE[i][k] * (1 - w) + SPINE[i + 1][k] * w for k in range(3))
    return p, RADII[i] * (1 - w) + RADII[i + 1] * w


def build():
    rng = random.Random(77)
    m = E.Model("veg-tree-trunk", category="vegetation", bevel=0.01, cage=0.09)
    E.sweep(m, SPINE, RADII, "bark_dark", sides=9)
    # Braided strands wrapping the trunk, each with a glowing vein (baked).
    for j in range(4):
        pts, radii, veins = [], [], []
        for i in range(9):
            t = 0.04 + 0.92 * i / 8
            (x, f, u), r = spine_at(t)
            th = 2 * math.pi * j / 4 + t * 3.4
            rs = 0.2 * (1 - 0.3 * t)
            rr = r * 0.95
            pts.append((x + rr * math.cos(th), f + rr * math.sin(th), u))
            radii.append(rs)
            veins.append((x + (rr + rs + 0.006) * math.cos(th), f + (rr + rs + 0.006) * math.sin(th), u))
        E.sweep(m, pts, radii, "bark", sides=5)
        E.sweep(m, veins, [0.03] * 9, "glow_cyan", sides=3, detail=True)
    # Bark ridges (baked).
    for j in range(14):
        th0 = 2 * math.pi * j / 14 + rng.uniform(-0.1, 0.1)
        pts = []
        for i in range(10):
            t = 0.02 + 0.95 * i / 9
            (x, f, u), r = spine_at(t)
            th = th0 + 0.25 * math.sin(t * 6 + j)
            pts.append((x + (r * 0.95) * math.cos(th), f + (r * 0.95) * math.sin(th), u))
        E.sweep(m, pts, [0.05] * 10, "bark_dark", sides=3, detail=True)
    # Buttress roots.
    for j in range(6):
        a = 2 * math.pi * j / 6 + rng.uniform(-0.25, 0.25)
        d = (math.cos(a), math.sin(a))
        L = rng.uniform(2.6, 3.6)
        pts = [(d[0] * 0.5, d[1] * 0.5, 1.6), (d[0] * 1.2, d[1] * 1.2, 0.6), (d[0] * L * 0.65, d[1] * L * 0.65, 0.1), (d[0] * L, d[1] * L, -0.1)]
        E.sweep(m, pts, [0.5, 0.36, 0.2, 0.0], "bark_dark", sides=6, flat=0.65, tip=True, normal=(-d[1], d[0], 0.0))
        vein = [(d[0] * 1.2, d[1] * 1.2, 0.6 + 0.34), (d[0] * L * 0.65, d[1] * L * 0.65, 0.1 + 0.19)]
        E.sweep(m, vein, [0.025, 0.015], "glow_cyan", sides=3, detail=True)
    m.marker("canopy", f=0.0, u=9.25)
    return m.finish(BUDGET, texture_size=1024)
