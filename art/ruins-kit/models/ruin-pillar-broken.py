"""Ruin pillar, broken: the ruin-pillar snapped at 2.9 m, its upper drum and
capital fallen beside it. Concept: codex/concepts/v0.2/32-ancient-ruins-kit.png.

Same 1.8 m base footprint as ruin-pillar; the fallen pieces reach about 3 m out
along +x. Origin at the base center of the standing stump.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (300, 1000)
S = "ruin_slate"


def build():
    rng = random.Random(43)
    m = E.Model("ruin-pillar-broken", category="ruins-kit", bevel=0.02, cage=0.06)
    b = E.block(m, (0, 0, 0.18), (1.8, 1.8, 0.36), "ruin_slate_dark", bevel=0.06, jitter=0.015, seed=1)
    E.paint_up(b, "moss_dark", prob=0.7, seed=1)
    b = E.block(m, (0, 0, 0.55), (1.48, 1.48, 0.4), S, bevel=0.06, jitter=0.012, seed=2, taper=0.94)
    E.paint_up(b, "moss", prob=0.6, seed=2)
    E.block(m, (0, 0, 1.6), (1.15, 1.15, 1.8), S, bevel=0.07, jitter=0.01, seed=3)
    E.block(m, (0, 0, 2.3), (1.3, 1.3, 0.8), S, bevel=0.08, jitter=0.012, seed=4)
    # Fracture: a jagged stump above the collar.
    stump = E.rock(m, (0, 0, 2.7), (0.62, 0.62, 0.55), S, seed=5, subdiv=2, cuts=9, cut_depth=0.5, bumps=0.25,
                   floor=-0.4, top_mat="moss", top_thresh=0.5, top_prob=0.7)
    # Fallen upper drum lying along +x, capital tipped beyond it.
    def drum():
        # Upper shaft lying on its side: authored upright-ish along x, faces carry the glyph.
        b = E.block(m, (2.05, 0.3, 0.56), (2.1, 1.12, 1.12), S, bevel=0.07, jitter=0.01, seed=6)
        for s in (-1, 1):
            sk = []
            if s < 0:
                pl = 0.3 + s * 0.56
                E.face_rect(m, "f", s, pl, 1.08, 3.02, 0.535, 0.585, -0.004, 0.009, "glow_glyph")
                for o in (-1, 1):
                    E.face_rect(m, "f", s, pl, 1.08, 3.02, 0.56 + o * 0.03, 0.56 + o * 0.075, -0.004, 0.026, S)
                E.face_ring(m, "f", s, pl, 2.05, 0.56, 0.3, 0.24, -0.004, 0.03, S)
                E.face_ring(m, "f", s, pl, 2.05, 0.56, 0.22, 0.18, -0.004, 0.02, "glow_glyph")
                E.face_disc(m, "f", s, pl, 2.05, 0.56, 0.15, -0.004, 0.028, S)
                E.face_disc(m, "f", s, pl, 2.05, 0.56, 0.05, -0.004, 0.032, "glow_glyph", segs=10)
                sk = [(1.0, 3.2, 0.45, 0.67), (1.7, 2.4, 0.2, 0.92)]
            E.masonry(m, "f", s, 0.3 + s * 0.56, 1.0, 3.1, 0.0, 1.12, rng, E.SLATE, course=(1.12, 1.12), length=(0.6, 0.9),
                      skip=sk, margin=0.04)
            E.masonry(m, "u", 1, 1.12, 1.0, 3.1, -0.26, 0.86, rng, E.SLATE, course=(1.12, 1.12), length=(0.6, 0.9), margin=0.04) if s > 0 else None
        return b
    d = E.transformed(m, drum, rotate=(0, 0, 14), pivot=(2.05, 0.3, 0.56))
    E.paint_up(d, "moss", prob=0.5, seed=6)
    # The capital tipped over beyond it, and its crown.
    E.block(m, (3.55, 0.75, 0.3), (1.62, 1.62, 0.3), S, bevel=0.06, jitter=0.03, seed=7, rot=(8, -10, 25), top_mat="moss", top_prob=0.8)
    E.block(m, (3.3, 1.9, 0.25), (1.0, 1.0, 0.26), S, bevel=0.05, jitter=0.03, seed=8, rot=(-6, 30, 40), top_mat="moss", top_prob=0.6)
    for i, (x, f, sz) in enumerate(((0.9, -0.8, 0.35), (-0.95, 0.6, 0.42), (1.2, 1.2, 0.3), (-0.6, -1.05, 0.25))):
        E.block(m, (x, f, sz * 0.4), (sz * 1.2, sz, sz * 0.8), S, bevel=0.05, jitter=0.04, seed=20 + i,
                rot=(rng.uniform(-12, 12), rng.uniform(-12, 12), rng.uniform(0, 90)), top_mat="moss", top_prob=0.6)

    for axis, s in (("f", -1), ("f", 1), ("x", -1), ("x", 1)):
        sk = E.glyph_column(m, axis, s, s * 0.65, 0.0, 1.95, 2.65, rings=(2.3,), stone=S, r=0.28)
        E.masonry(m, axis, s, s * 0.65, -0.65, 0.65, 1.9, 2.7, rng, E.SLATE, course=(0.8, 0.8), length=(0.6, 0.6), skip=sk, margin=0.03)
        sk2 = E.glyph_column(m, axis, s, s * 0.575, 0.0, 0.8, 1.88, stone=S)
        E.masonry(m, axis, s, s * 0.575, -0.575, 0.575, 0.75, 1.9, rng, E.SLATE, course=(0.45, 0.8), length=(0.5, 0.5), skip=sk2, margin=0.03)
        E.masonry(m, axis, s, s * 0.74, -0.74, 0.74, 0.35, 0.75, rng, E.SLATE, course=(0.4, 0.4), length=(0.5, 0.8), margin=0.03)
        E.masonry(m, axis, s, s * 0.9, -0.9, 0.9, 0.0, 0.36, rng, ["ruin_slate_dark"], course=(0.36, 0.36), length=(0.6, 0.9), margin=0.02)
        E.vines(m, axis, s, s * 0.575, -0.5, 0.5, 1.9, rng, count=1, length=(0.5, 1.0), b_min=0.8)
    return m.finish(BUDGET, texture_size=1024)
