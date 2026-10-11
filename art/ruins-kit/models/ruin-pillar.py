"""Ruin pillar: square carved pillar with stepped base and capital.
Concept: codex/concepts/v0.2/32-ancient-ruins-kit.png (top-row pillars).

Footprint 1.8 m base, 1.15 m shaft, 5.5 m tall. Sized to stand on a ruin-wall
joint (covers the 0.9-1.2 m wall ends) or alone. Origin at the base center.
A glowing glyph channel runs up all four faces through ringed medallions set in
the collar; masonry courses, cracks and vines are baked.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (300, 1000)
S = "ruin_slate"


def build():
    rng = random.Random(41)
    m = E.Model("ruin-pillar", category="ruins-kit", bevel=0.02, cage=0.06)
    b = E.block(m, (0, 0, 0.18), (1.8, 1.8, 0.36), "ruin_slate_dark", bevel=0.06, jitter=0.015, seed=1)
    E.paint_up(b, "moss_dark", prob=0.6, seed=1)
    b = E.block(m, (0, 0, 0.55), (1.48, 1.48, 0.4), S, bevel=0.06, jitter=0.012, seed=2, taper=0.94)
    E.paint_up(b, "moss", prob=0.5, seed=2)
    E.block(m, (0, 0, 2.7), (1.15, 1.15, 3.9), S, bevel=0.07, jitter=0.01, seed=3)
    E.block(m, (0, 0, 2.45), (1.3, 1.3, 1.1), S, bevel=0.08, jitter=0.012, seed=4)
    E.block(m, (0, 0, 4.78), (1.38, 1.38, 0.28), S, bevel=0.05, jitter=0.015, seed=5)
    cap = E.block(m, (0, 0, 5.07), (1.62, 1.62, 0.3), S, bevel=0.06, jitter=0.025, seed=6)
    E.paint_up(cap, "moss", prob=0.8, seed=6)
    crown = E.block(m, (0, 0, 5.34), (1.05, 1.05, 0.26), S, bevel=0.05, jitter=0.03, seed=7, rot=(0, 0, 5))
    E.paint_up(crown, "moss", prob=0.8, seed=7)
    # A chipped stone at the foot.
    E.block(m, (0.95, -0.7, 0.13), (0.4, 0.32, 0.26), S, bevel=0.05, jitter=0.04, seed=8, rot=(8, -6, 35), top_mat="moss", top_prob=0.7)

    for axis, s in (("f", -1), ("f", 1), ("x", -1), ("x", 1)):
        sk = E.glyph_column(m, axis, s, s * 0.65, 0.0, 1.95, 2.95, rings=(2.45,), stone=S, r=0.3)
        E.masonry(m, axis, s, s * 0.65, -0.65, 0.65, 1.9, 3.0, rng, E.SLATE, course=(1.1, 1.1), length=(0.6, 0.6), skip=sk, margin=0.03)
        sk2 = E.glyph_column(m, axis, s, s * 0.575, 0.0, 0.8, 1.88, stone=S) + E.glyph_column(m, axis, s, s * 0.575, 0.0, 3.02, 4.55, stone=S)
        E.masonry(m, axis, s, s * 0.575, -0.575, 0.575, 0.75, 4.64, rng, E.SLATE, course=(0.45, 0.8), length=(0.5, 0.5), skip=sk2, margin=0.03)
        E.masonry(m, axis, s, s * 0.74, -0.74, 0.74, 0.35, 0.75, rng, E.SLATE, course=(0.4, 0.4), length=(0.5, 0.8), margin=0.03)
        E.masonry(m, axis, s, s * 0.9, -0.9, 0.9, 0.0, 0.36, rng, ["ruin_slate_dark"], course=(0.36, 0.36), length=(0.6, 0.9), margin=0.02)
        E.masonry(m, axis, s, s * 0.81, -0.81, 0.81, 4.92, 5.22, rng, E.SLATE, course=(0.3, 0.3), length=(0.5, 0.8), margin=0.02)
        E.vines(m, axis, s, s * 0.575, -0.5, 0.5, 4.6, rng, count=1 + (s > 0), length=(0.8, 2.2), b_min=0.8)
    return m.finish(BUDGET, texture_size=1024)
