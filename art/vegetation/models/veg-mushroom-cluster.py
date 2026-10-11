"""Mushroom cluster: glowing fan-capped Bloomwild mushrooms.
Concept: codex/concepts/v0.2/30-luminous-vegetation.png (bottom-right glowing
mushrooms) and 36-bloomwild.png.

Six mushrooms from 0.35 to 1.6 m tall in a 1.8 m patch. Pale stems with a
glowing cyan sheen, violet caps whose gilled undersides glow (gills baked),
a few glowing spores. Origin at the base center.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)
SIDES = 9


def mushroom(m, rng, x, f, h, r, lean):
    lx, lf = lean
    top = (x + lx * h, f + lf * h, h)
    stem = [(x, f, -0.03), (x + lx * h * 0.35, f + lf * h * 0.35, h * 0.4), top]
    E.sweep(m, stem, [r * 0.16, r * 0.12, r * 0.1], "petal", sides=6)
    # Glowing streak up the stem (baked).
    E.sweep(m, [(p[0] + rr * 0.9 + 0.006, p[1], p[2]) for p, rr in zip(stem, (r * 0.16, r * 0.12, r * 0.1))],
            [0.008, 0.007, 0.006], "glow_cyan", sides=3, detail=True)
    # Cap: shallow fan, scalloped rim, rim drooping. Rings go top center -> rim -> underside.
    prof = [(0.12, 0.2), (0.55, 0.14), (1.0, -0.02), (0.8, -0.1), (0.25, -0.05)]
    rings = []
    for pr, pu in prof:
        ring = []
        for k in range(SIDES):
            th = 2 * math.pi * k / SIDES
            lobe = 1 + 0.07 * math.cos(5 * th) * (pr > 0.5)
            ring.append((top[0] + math.cos(th) * pr * r * lobe, top[1] + math.sin(th) * pr * r * lobe, top[2] + pu * r * 0.6))
        rings.append(ring)
    cap = m.loft(rings, "cap_violet")
    E.paint_dir(cap, "glow_cyan", (0, 0, -1), thresh=0.35)
    # Gills (baked): radial lines across the underside, on the faces between rim and center.
    for k in range(SIDES):
        a0, a1 = rings[3][k], rings[3][(k + 1) % SIDES]
        b0, b1 = rings[4][k], rings[4][(k + 1) % SIDES]
        mo = tuple((a0[q] + a1[q]) / 2 for q in range(3))
        mi = tuple((b0[q] + b1[q]) / 2 for q in range(3))
        E.sweep(m, [(mo[0], mo[1], mo[2] - 0.006), (mi[0], mi[1], mi[2] - 0.006)], [0.008, 0.006], "cap_violet", sides=3, detail=True)
    # Glowing ribs on top (baked), along the loft edges.
    for k in range(0, SIDES, 2):
        pts = [(rings[i][k][0], rings[i][k][1], rings[i][k][2] + 0.008) for i in range(3)]
        E.sweep(m, pts, [0.009, 0.008, 0.006], "glow_violet", sides=3, detail=True)


def build():
    rng = random.Random(107)
    m = E.Model("veg-mushroom-cluster", category="vegetation", bevel=0.004, cage=0.015)
    for x, f, h, r, lean in ((0.0, 0.0, 1.6, 0.75, (0.05, 0.03)), (0.55, -0.3, 1.05, 0.5, (0.12, -0.08)),
                             (-0.5, -0.25, 0.85, 0.42, (-0.15, -0.05)), (-0.2, 0.55, 0.6, 0.32, (-0.05, 0.2)),
                             (0.45, 0.45, 0.42, 0.24, (0.15, 0.1)), (-0.75, 0.3, 0.35, 0.2, (-0.2, 0.1))):
        mushroom(m, rng, x, f, h, r, lean)
    for i in range(5):
        a = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(0.4, 0.9)
        p = (math.cos(a) * rr, math.sin(a) * rr, rng.uniform(0.02, 0.05))
        E.bud(m, p, (p[0], p[1], p[2] + rng.uniform(0.05, 0.09)), 0.025, "glow_cyan")
    return m.finish(BUDGET, texture_size=1024)
