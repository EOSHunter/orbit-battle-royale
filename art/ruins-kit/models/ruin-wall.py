"""Ruin wall: 4 m modular wall section of the ancient ruins kit.
Concept: codex/concepts/v0.2/32-ancient-ruins-kit.png.

Grid: 4 m wide (x -2..2), 0.9 m thick body on a 1.2 m plinth, about 4 m tall
(the pilaster cap reaches 4.8 m). Ends are plain so sections butt together;
drop ruin-pillar on a joint to hide it. Origin at the base center.
Dark weathered slate laid in irregular courses (baked), a central pilaster with
the ringed glowing glyph channel, a circuit-like glyph trace, tall slabs of
uneven height, mossy tops and hanging vines baked into the color map.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (300, 1000)
S = "ruin_slate"


def build():
    rng = random.Random(11)
    m = E.Model("ruin-wall", category="ruins-kit", bevel=0.02, cage=0.06)
    T = 0.45  # half thickness of the body

    plinth = E.block(m, (0, 0, 0.25), (4.0, 1.2, 0.5), "ruin_slate_dark", bevel=0.05, jitter=0.01, seed=1)
    E.paint_up(plinth, "moss_dark", prob=0.5, seed=2)
    m.front_prism([(-2, 0.48), (2, 0.48), (2, 3.42), (-2, 3.42)], -T, T, S)

    # Cornice: chunky capping stones of uneven height, slightly askew.
    tops = {}
    for x0, x1, top, sd in ((-1.45, -0.55, 3.92, 3), (0.55, 1.35, 3.8, 4), (1.35, 2.0, 3.66, 5)):
        c = E.block(m, ((x0 + x1) / 2, 0, (3.4 + top) / 2), (x1 - x0, 1.08, top - 3.4), S, bevel=0.06, jitter=0.03, seed=sd,
                    rot=(rng.uniform(-2, 2), 0, rng.uniform(-2, 2)))
        E.paint_up(c, "moss", prob=0.75, seed=sd)
        tops[(x0, x1)] = top
    # Tall slab rising above the cornice at the left end.
    sl = E.block(m, (-1.73, 0, 2.3), (0.54, 1.02, 3.6), S, bevel=0.05, jitter=0.015, seed=21)
    E.block(m, (-1.73, 0, 4.2), (0.54, 1.02, 0.2), S, bevel=0.04, jitter=0.03, seed=22, rot=(0, 6, 0))
    E.paint_up(sl, "moss", prob=0.9, seed=23)
    # Central pilaster and capital.
    E.block(m, (0, 0, 2.35), (1.1, 1.12, 3.8), S, bevel=0.05, jitter=0.01, seed=6)
    cap = E.block(m, (0, 0, 4.42), (1.36, 1.3, 0.36), S, bevel=0.06, jitter=0.02, seed=7)
    E.paint_up(cap, "moss", prob=0.8, seed=8)
    E.block(m, (0, 0, 4.7), (0.8, 0.9, 0.22), S, bevel=0.05, jitter=0.03, seed=9, rot=(0, 0, 4))
    # Framing slab, and a recessed panel frame on the right.
    E.block(m, (-1.08, 0, 1.9), (0.36, 1.0, 2.9), "ruin_slate_dark", bevel=0.04, jitter=0.012, seed=10)
    E.block(m, (1.3, 0, 1.75), (0.42, 1.0, 2.6), S, bevel=0.04, jitter=0.012, seed=12)
    E.block(m, (1.0, 0, 3.22), (1.5, 0.98, 0.3), S, bevel=0.04, jitter=0.012, seed=13)
    # Fallen chips along the plinth.
    for i, (x, s) in enumerate(((-0.9, 1), (1.6, -1), (0.7, -1))):
        E.block(m, (x, s * 0.78, 0.12), (0.35, 0.3, 0.24), S, bevel=0.05, jitter=0.04, seed=30 + i,
                rot=(rng.uniform(-10, 10), rng.uniform(-10, 10), rng.uniform(0, 90)), top_mat="moss", top_prob=0.6)

    def top_fn(a):
        if abs(a) < 0.55:
            return 4.24
        if a < -1.46:
            return 4.1
        return 3.4

    for s in (-1, 1):
        # Pilaster face: glyph channel through a ringed medallion.
        skip = E.glyph_column(m, "f", s, s * 0.56, 0.0, 0.62, 4.1, rings=(2.45,), stone=S)
        E.masonry(m, "f", s, s * 0.56, -0.55, 0.55, 0.5, 4.24, rng, E.SLATE, course=(0.5, 0.9), length=(0.4, 1.0), skip=skip)
        # Body faces with a stepped glyph trace.
        trace = [(0.62, 1.55), (0.85, 1.55), (0.85, 0.75)] if s < 0 else [(-0.62, 2.9), (-0.8, 2.9), (-0.8, 1.2)]
        E.strip(m, "f", s, s * T, trace, 0.04, -0.004, 0.01, "glow_glyph")
        tskip = []
        for (a0, b0), (a1, b1) in zip(trace, trace[1:]):
            tskip.append((min(a0, a1) - 0.07, max(a0, a1) + 0.07, min(b0, b1) - 0.07, max(b0, b1) + 0.07))
        E.masonry(m, "f", s, s * T, -2.0, 2.0, 0.48, 3.42, rng, E.SLATE, skip=[(-0.6, 0.6, 0, 5), (-2, -1.45, 0, 5)] + tskip,
                  course=(0.35, 0.75), length=(0.4, 1.2))
        E.masonry(m, "f", s, s * 0.51, -2.0, -1.46, 0.5, 4.1, rng, E.SLATE, course=(0.7, 1.3), length=(0.6, 0.6), margin=0.03)
        E.masonry(m, "f", s, s * 0.5, 1.09, 1.51, 0.5, 3.05, rng, E.SLATE, course=(0.6, 1.2), length=(0.5, 0.5), margin=0.03)
        E.masonry(m, "f", s, s * 0.5, -1.26, -0.9, 0.5, 3.35, rng, ["ruin_slate_dark"], course=(0.8, 1.4), length=(0.5, 0.5), margin=0.03)
        E.masonry(m, "f", s, s * 0.6, -2.0, 2.0, 0.02, 0.48, rng, ["ruin_slate_dark", "ruin_slate"], course=(0.5, 0.5), length=(0.7, 1.6))
        E.vines(m, "f", s, s * 0.56, -0.45, 0.45, 4.24, rng, count=2, length=(0.8, 2.8), b_min=0.6)
        E.vines(m, "f", s, s * 0.51, -1.95, -1.5, 4.08, rng, count=1, length=(0.8, 2.4), b_min=0.6)
    for s in (-1, 1):
        E.masonry(m, "x", s, s * 2.0, -T, T, 0.5, 3.4, rng, E.SLATE, course=(0.5, 0.9), length=(0.9, 0.9))
        E.masonry(m, "x", s, s * 0.55, -0.55, 0.55, 0.5, 4.2, rng, E.SLATE, course=(0.6, 1.0), length=(1.1, 1.1))
    return m.finish(BUDGET, texture_size=1024)
