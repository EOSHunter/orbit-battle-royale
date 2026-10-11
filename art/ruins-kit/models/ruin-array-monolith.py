"""Ruin array monolith: a carved signal monolith of the Hollow Array.
Concept: codex/concepts/v0.2/39-hollow-array.png (tall slab with the ringed
glyph channel, cross-armed tower in the background).

Warm umber stone, 3.2 m wide slab on a stepped plinth, buttress shoulders,
a cross-arm head block and a tapered crown, 10.4 m tall. A large ringed
medallion threaded by a glowing channel on both broad faces, narrow slits on
the sides. Footprint 4.4 x 2.6 m (fits a 4 m grid cell with overhang).
Origin at the base center.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (300, 1000)
S = "ruin_umber"


def build():
    rng = random.Random(91)
    m = E.Model("ruin-array-monolith", category="ruins-kit", bevel=0.02, cage=0.06)
    b = E.block(m, (0, 0, 0.35), (4.4, 2.6, 0.7), "ruin_slate_dark", bevel=0.07, jitter=0.02, seed=1)
    E.paint_up(b, "moss_dark", prob=0.5, seed=1)
    b = E.block(m, (0, 0, 0.95), (3.8, 2.1, 0.5), S, bevel=0.06, jitter=0.015, seed=2, taper=0.95)
    E.paint_up(b, "moss", prob=0.4, seed=2)
    E.block(m, (0, 0, 5.0), (3.2, 1.6, 7.7), S, bevel=0.07, jitter=0.01, seed=3)
    for s in (-1, 1):
        sh = E.block(m, (s * 1.85, 0, 3.0), (0.6, 1.4, 4.2), S, bevel=0.06, jitter=0.012, seed=4 + s)
        E.paint_up(sh, "moss", prob=0.8, seed=4 + s)
        E.block(m, (s * 2.05, 0, 7.75), (0.8, 1.3, 0.9), S, bevel=0.06, jitter=0.02, seed=6 + s)
    arm = E.block(m, (0, 0, 8.45), (4.9, 1.75, 0.5), S, bevel=0.06, jitter=0.02, seed=8)
    E.paint_up(arm, "moss", prob=0.6, seed=8)
    E.block(m, (0, 0, 9.2), (2.6, 1.4, 1.0), S, bevel=0.06, jitter=0.02, seed=9, taper=0.72)
    top = E.block(m, (0, 0, 9.95), (1.2, 0.9, 0.5), S, bevel=0.05, jitter=0.03, seed=10, taper=0.6, rot=(0, 3, 0))
    E.paint_up(top, "moss", prob=0.5, seed=10)
    # Fallen fragments at the foot.
    for i, (x, f, sz) in enumerate(((1.9, -1.7, 0.55), (-2.4, -1.2, 0.4), (-1.0, 1.75, 0.45), (2.5, 0.9, 0.3))):
        E.block(m, (x, f, sz * 0.4), (sz * 1.3, sz, sz * 0.8), S, bevel=0.05, jitter=0.04, seed=20 + i,
                rot=(rng.uniform(-12, 12), rng.uniform(-12, 12), rng.uniform(0, 90)), top_mat="moss", top_prob=0.6)

    for s in (-1, 1):
        sk = E.glyph_column(m, "f", s, s * 0.8, 0.0, 1.3, 8.1, rings=(4.4,), stone=S, w=0.09, r=0.85)
        # A second, smaller ring high on the slab and short side traces.
        sk += E.glyph_column(m, "f", s, s * 0.8, 0.0, 6.6, 6.61, rings=(6.9,), stone=S, w=0.09, r=0.36)
        for side in (-1, 1):
            tr = [(side * 0.2, 2.2), (side * 0.9, 2.2), (side * 0.9, 1.4)]
            E.strip(m, "f", s, s * 0.8, tr, 0.05, -0.004, 0.012, "glow_glyph")
            sk.append((min(side * 0.2, side * 0.9) - 0.08, max(side * 0.2, side * 0.9) + 0.08, 1.32, 2.3))
            tr2 = [(side * 0.2, 5.7), (side * 1.2, 5.7), (side * 1.2, 7.4)]
            E.strip(m, "f", s, s * 0.8, tr2, 0.05, -0.004, 0.012, "glow_glyph")
            sk.append((min(side * 0.2, side * 1.2) - 0.08, max(side * 0.2, side * 1.2) + 0.08, 5.62, 5.78))
            sk.append((side * 1.2 - 0.08, side * 1.2 + 0.08, 5.6, 7.5))
        E.masonry(m, "f", s, s * 0.8, -1.6, 1.6, 1.2, 8.15, rng, E.UMBER, course=(0.5, 1.1), length=(0.6, 1.6), skip=sk)
        E.masonry(m, "f", s, s * 0.875, -2.45, 2.45, 8.2, 8.7, rng, E.UMBER, course=(0.5, 0.5), length=(0.8, 1.6), margin=0.03)
        E.masonry(m, "f", s, s * 1.05, -1.9, 1.9, 0.7, 1.2, rng, E.UMBER, course=(0.5, 0.5), length=(0.6, 1.2), margin=0.03)
        E.masonry(m, "f", s, s * 1.3, -2.2, 2.2, 0.0, 0.7, rng, ["ruin_slate_dark"], course=(0.7, 0.7), length=(0.8, 1.6), margin=0.03)
        # Side faces: slit through the shoulder and the slab above it.
        E.face_rect(m, "x", s, s * 2.15, -0.06, 0.06, 1.6, 4.6, -0.004, 0.012, "glow_glyph")
        E.masonry(m, "x", s, s * 2.15, -0.7, 0.7, 1.2, 5.0, rng, E.UMBER, course=(0.6, 1.0), length=(0.6, 0.6),
                  skip=[(-0.12, 0.12, 0, 9)], margin=0.03)
        E.masonry(m, "x", s, s * 1.6, -0.8, 0.8, 5.2, 7.3, rng, E.UMBER, course=(0.6, 1.0), length=(0.8, 0.8), margin=0.03)
        E.vines(m, "f", s, s * 0.8, -1.5, 1.5, 8.15, rng, count=3, length=(1.0, 3.5), b_min=1.3)
    return m.finish(BUDGET, texture_size=1024)
