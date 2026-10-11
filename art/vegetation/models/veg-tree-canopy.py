"""Bloomwild tree, canopy: the luminous violet umbrella crown of a canopy tree.
Concept: codex/concepts/v0.2/36-bloomwild.png (glowing mushroom-like canopies
with radiating ribs and hanging light strands).

Pairs with veg-tree-trunk: same origin (base center of the tree on the ground).
The crown spans about 12.5 m, from u = 9.1 (joins the trunk flare) to 11.8.
Scalloped violet cap with glowing ribs (baked), a glowing gilled underside and
hanging strands tipped with glowing pods. Origin at the base center of the tree.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)
SIDES = 18
PROFILE = [(0.95, 9.1), (2.4, 9.55), (4.3, 9.85), (5.7, 9.95), (6.25, 10.2), (5.5, 10.7), (3.9, 11.3), (1.9, 11.68), (0.45, 11.8)]


def surface(r, u, th):
    """Point on the scalloped crown at profile (r, u) and angle th."""
    lobe = math.cos(6 * th)
    rim = 1.0 if r > 5.0 else (r / 5.0) ** 2
    rr = r * (1 + 0.05 * lobe * rim)
    uu = u - 0.25 * (1 - lobe) * rim * (1 if u < 10.5 else 0.6)
    return (rr * math.cos(th), rr * math.sin(th), uu)


def build():
    rng = random.Random(87)
    m = E.Model("veg-tree-canopy", category="vegetation", bevel=0.01, cage=0.09)
    rings = []
    for r, u in PROFILE:
        rings.append([surface(r, u, 2 * math.pi * k / SIDES) for k in range(SIDES)])
    cap = m.loft(rings, "cap_violet")
    E.paint_dir(cap, "glow_violet", (0, 0, -1), thresh=0.4)
    # Glowing ribs radiating over the cap, gill lines under it (both baked).
    for k in range(SIDES):
        top = [(p[0], p[1], p[2] + 0.03) for p in (rings[i][k] for i in range(4, len(PROFILE)))]
        E.sweep(m, top, [0.05] * len(top), "glow_violet" if k % 3 else "glow_pink", sides=3, detail=True)
        # Gills under the cap, midway between the ribs (on the flat faces).
        under = []
        for i in range(1, 4):
            a, b = rings[i][k], rings[i][(k + 1) % SIDES]
            under.append(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2 - 0.025))
        E.sweep(m, under, [0.035] * 3, "cap_violet", sides=3, detail=True)
    # Hanging light strands with glowing pods.
    for j in range(15):
        th = 2 * math.pi * j / 15 + rng.uniform(-0.15, 0.15)
        r = rng.uniform(2.6, 5.6)
        k = min(range(1, 4), key=lambda i: abs(PROFILE[i][0] - r))
        x, f, u = surface(r, PROFILE[k][1], th)
        L = rng.uniform(1.4, 3.4)
        sway = rng.uniform(-0.25, 0.25)
        end = (x + sway, f - sway, u - L)
        E.sweep(m, [(x, f, u + 0.05), (x + sway * 0.4, f - sway * 0.4, u - L * 0.5), end], [0.035, 0.022, 0.0],
                "glow_violet" if j % 3 else "glow_cyan", sides=3, tip=True)
        E.bud(m, (end[0], end[1], end[2] + 0.12), (end[0], end[1], end[2] - 0.12), 0.07, "glow_cyan")
    return m.finish(BUDGET, texture_size=1024)
