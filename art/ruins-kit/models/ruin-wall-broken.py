"""Ruin wall, broken: 4 m modular wall section collapsed to a jagged top.
Concept: codex/concepts/v0.2/32-ancient-ruins-kit.png (bottom-left broken wall).

Same grid as ruin-wall: 4 m wide (x -2..2), 0.9 m body on a 1.2 m plinth, so it
butts against intact sections. Height falls from 3.8 m at the left end to 1.5 m.
Fallen blocks lie at its feet; a broken glyph channel still glows on the slab.
Origin at the base center.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (300, 1000)
S = "ruin_slate"
TOP = [(-2.0, 3.35), (-1.55, 3.45), (-1.3, 2.95), (-0.85, 3.05), (-0.55, 2.55), (-0.1, 2.7), (0.3, 2.05),
       (0.75, 2.2), (1.1, 1.6), (1.55, 1.75), (2.0, 1.45)]


def top_fn(a):
    for (a0, b0), (a1, b1) in zip(TOP, TOP[1:]):
        if a0 <= a <= a1:
            return min(b0, b1) if abs(b1 - b0) > 0.3 else b0 + (b1 - b0) * (a - a0) / (a1 - a0)
    return TOP[-1][1] if a > 0 else TOP[0][1]


def build():
    rng = random.Random(23)
    m = E.Model("ruin-wall-broken", category="ruins-kit", bevel=0.02, cage=0.06)
    T = 0.45

    plinth = E.block(m, (0, 0, 0.25), (4.0, 1.2, 0.5), "ruin_slate_dark", bevel=0.05, jitter=0.012, seed=1)
    E.paint_up(plinth, "moss_dark", prob=0.6, seed=2)
    body = m.front_prism([(-2.0, 0.48), (2.0, 0.48)] + list(reversed(TOP)), -T, T, S)
    E.paint_up(body, "moss", thresh=0.45, prob=0.85, seed=3)

    # Standing slab at the left end with the surviving glyph.
    E.block(m, (-1.62, 0, 2.15), (0.76, 1.08, 3.3), S, bevel=0.05, jitter=0.015, seed=4)
    top = E.block(m, (-1.62, 0, 3.9), (0.76, 1.08, 0.3), S, bevel=0.05, jitter=0.04, seed=5, rot=(4, 8, 0))
    E.paint_up(top, "moss", prob=0.9, seed=6)
    # Blocks left sitting askew on the break.
    for i, (x, u, sx, rot) in enumerate(((-0.75, 3.2, 0.7, (3, -9, 6)), (0.45, 2.33, 0.6, (-5, 12, -8)), (1.35, 1.88, 0.5, (8, 4, 15)))):
        b = E.block(m, (x, rng.uniform(-0.08, 0.08), u), (sx, 0.82, 0.38), S, bevel=0.05, jitter=0.03, seed=10 + i, rot=rot)
        E.paint_up(b, "moss", prob=0.8, seed=20 + i)
    # A fallen slab leaning against the wall, and rubble at the foot.
    E.block(m, (0.9, -0.95, 0.75), (0.9, 0.3, 1.5), S, bevel=0.05, jitter=0.02, seed=30, rot=(-20, 0, 8), top_mat="moss", top_prob=0.7)
    for i, (x, f, sz) in enumerate(((-0.4, -0.95, 0.5), (1.7, -0.85, 0.42), (-1.2, 0.9, 0.55), (0.4, 0.95, 0.45), (1.3, 1.05, 0.3), (-0.9, -1.1, 0.28))):
        E.block(m, (x, f, sz * 0.4), (sz * rng.uniform(0.9, 1.4), sz, sz * 0.8), S, bevel=0.05, jitter=0.04, seed=40 + i,
                rot=(rng.uniform(-12, 12), rng.uniform(-12, 12), rng.uniform(0, 90)), top_mat="moss", top_prob=0.7)

    for s in (-1, 1):
        skip = E.glyph_column(m, "f", s, s * 0.54, -1.62, 0.65, 3.2, rings=(1.9,), stone=S, r=0.28)
        E.masonry(m, "f", s, s * 0.54, -2.0, -1.24, 0.5, 3.8, rng, E.SLATE, course=(0.5, 0.9), length=(0.8, 0.8), skip=skip, margin=0.03)
        E.masonry(m, "f", s, s * T, -1.24, 2.0, 0.48, 3.5, rng, E.SLATE, course=(0.35, 0.75), length=(0.4, 1.2), top_fn=top_fn)
        E.masonry(m, "f", s, s * 0.6, -2.0, 2.0, 0.02, 0.48, rng, ["ruin_slate_dark", "ruin_slate"], course=(0.5, 0.5), length=(0.7, 1.6))
        # A glyph trace snapped off at the break.
        E.strip(m, "f", s, s * T, [(-1.15, 1.3), (-0.3, 1.3), (-0.3, 2.3)], 0.04, -0.004, 0.028, "glow_glyph")
        E.vines(m, "f", s, s * 0.54, -1.95, -1.3, 3.75, rng, count=2, length=(0.5, 2.0), b_min=0.6)
        E.vines(m, "f", s, s * T, -1.2, 1.9, 3.0, rng, count=3, length=(0.5, 1.4), b_min=0.6, top_fn=top_fn)
    for s in (-1, 1):
        E.masonry(m, "x", s, s * 2.0, -T, T, 0.5, 1.45, rng, E.SLATE, course=(0.4, 0.5), length=(0.9, 0.9))
    E.masonry(m, "x", -1, -2.0, -0.54, 0.54, 0.5, 3.75, rng, E.SLATE, course=(0.5, 0.9), length=(1.1, 1.1))
    return m.finish(BUDGET, texture_size=1024)
