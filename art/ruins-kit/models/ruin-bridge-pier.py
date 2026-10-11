"""Ruin bridge pier: tall pier of The Spine with pylons rising past the deck.
Concept: codex/concepts/v0.2/38-the-spine.png.

Footprint 4 m along the bridge (f -2..2) and 6.6 m across (x -3.3..3.3) at the
pylons; the deck surface is the pier top at u = 12 (spans attach to the f = +-2
faces, see ruin-bridge-span). Pylons stand 3 m above the deck at both sides.
Pale sandstone with stepped buttresses, tall amber glow slits and an amber
medallion on each pylon. Origin at the base center.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (300, 1000)
S = "ruin_sand"
TOP = 12.0


def build():
    rng = random.Random(81)
    m = E.Model("ruin-bridge-pier", category="ruins-kit", bevel=0.02, cage=0.06)
    # Plinth steps, lower and upper shaft.
    b = E.block(m, (0, 0, 0.6), (6.4, 5.2, 1.2), "ruin_umber", bevel=0.08, jitter=0.03, seed=1)
    E.paint_up(b, "moss", prob=0.7, seed=1)
    E.block(m, (0, 0, 3.6), (5.8, 4.4, 4.8), S, bevel=0.07, jitter=0.012, seed=2)
    E.block(m, (0, 0, 8.7), (5.2, 4.0, 5.6), S, bevel=0.07, jitter=0.01, seed=3)
    E.block(m, (0, 0, TOP - 0.3), (5.2, 4.0, 0.6), S, bevel=0.06, jitter=0.008, seed=4)
    # Buttress fins on the canyon faces (x sides) and the ends.
    for s in (-1, 1):
        for fo in (-1.2, 1.2):
            E.block(m, (s * 3.05, fo, 3.0), (0.5, 0.7, 6.0), S, bevel=0.05, jitter=0.012, seed=10 + int(fo * 10) + s, taper=0.8)
        # Pylons above the deck.
        E.block(m, (s * 2.9, 0, TOP + 1.2), (0.8, 2.2, 2.4), S, bevel=0.06, jitter=0.012, seed=20 + s)
        E.block(m, (s * 2.9, 0, TOP - 2.4), (0.8, 2.2, 4.8), S, bevel=0.06, jitter=0.012, seed=22 + s)
        cap = E.block(m, (s * 2.9, 0, TOP + 2.6), (1.0, 2.5, 0.4), S, bevel=0.06, jitter=0.025, seed=24 + s)
        E.paint_up(cap, "moss", prob=0.9, seed=24 + s)
        E.block(m, (s * 2.9, 0, TOP + 3.0), (0.6, 1.4, 0.4), S, bevel=0.05, jitter=0.03, seed=26 + s, taper=0.7)
        # Ledge where the lower shaft steps in.
        lg = E.block(m, (s * 2.75, 0, 6.05), (0.4, 4.3, 0.18), S, bevel=0.04, jitter=0.01, seed=28 + s)
        E.paint_up(lg, "moss", prob=0.9, seed=28 + s)
    E.block(m, (2.6, -2.9, 0.25), (0.8, 0.7, 0.5), S, bevel=0.05, jitter=0.04, seed=40, rot=(8, -6, 30), top_mat="moss", top_prob=0.7)
    E.block(m, (-2.0, 2.95, 0.2), (0.6, 0.5, 0.4), S, bevel=0.05, jitter=0.04, seed=41, rot=(-6, 9, 15), top_mat="moss", top_prob=0.7)

    for s in (-1, 1):
        # Canyon faces: big courses, amber slits between the buttresses.
        E.face_rect(m, "x", s, s * 2.9, -0.1, 0.1, 1.6, 5.6, -0.004, 0.012, "glow_amber")
        for side in (-1, 1):
            E.face_rect(m, "x", s, s * 2.9, side * 0.12, side * 0.3, 1.5, 5.7, -0.004, 0.03, S)
        E.masonry(m, "x", s, s * 2.9, -2.2, 2.2, 1.2, 6.0, rng, E.SAND, course=(0.5, 1.0), length=(0.8, 1.8),
                  skip=[(-0.35, 0.35, 0, 20), (-1.55, -0.85, 0, 6.1), (0.85, 1.55, 0, 6.1)])
        for fo in (-1.55, 1.55):
            E.face_rect(m, "x", s, s * 2.6, fo - 0.06, fo + 0.06, 6.6, 10.8, -0.004, 0.012, "glow_amber")
        E.masonry(m, "x", s, s * 2.6, -2.0, 2.0, 6.0, 11.4, rng, E.SAND, course=(0.5, 1.0), length=(0.8, 1.8),
                  skip=[(-1.15, 1.15, 7.1, 20), (-1.75, -1.35, 0, 20), (1.35, 1.75, 0, 20)])
        # Pylon faces: slit and medallion outward, courses on the sides.
        sk2 = E.glyph_column(m, "x", s, s * 3.3, 0.0, 7.6, TOP + 2.2, rings=(TOP + 1.0,), stone=S, glow="glow_amber", w=0.08, r=0.42)
        E.masonry(m, "x", s, s * 3.3, -1.1, 1.1, 7.2, TOP + 2.4, rng, E.SAND, course=(0.5, 1.0), length=(0.6, 1.0), skip=sk2, margin=0.03)
        for fs in (-1, 1):
            E.masonry(m, "f", fs, fs * 1.1, min(s * 2.5, s * 3.3), max(s * 2.5, s * 3.3), 7.2, TOP + 2.4, rng, E.SAND,
                      course=(0.5, 1.0), length=(0.8, 0.8), margin=0.03)
        E.masonry(m, "x", s, s * 3.2, -2.6, 2.6, 0.0, 1.2, rng, ["ruin_umber"], course=(0.6, 0.6), length=(1.0, 2.0), margin=0.03)
        E.vines(m, "x", s, s * 2.6, -1.9, -1.2, TOP - 0.62, rng, count=1, length=(1.0, 3.5), b_min=6.2, h=(0.018, 0.026))
        E.vines(m, "x", s, s * 2.6, 1.2, 1.9, TOP - 0.62, rng, count=1, length=(1.0, 3.5), b_min=6.2, h=(0.018, 0.026))
    for fs in (-1, 1):
        # Ends of the pier (spans attach above u = 8 there).
        E.masonry(m, "f", fs, fs * 2.2, -2.9, 2.9, 1.2, 6.0, rng, E.SAND, course=(0.5, 1.0), length=(0.8, 1.8))
        E.masonry(m, "f", fs, fs * 2.0, -2.6, 2.6, 6.0, 11.4, rng, E.SAND, course=(0.5, 1.0), length=(0.8, 1.8))
    E.masonry(m, "u", 1, TOP, -2.4, 2.4, -2.0, 2.0, rng, E.SAND, course=(0.8, 1.4), length=(0.7, 1.4), margin=0.02,
              skip=[(-0.1, 0.1, -5, 5)], crack_prob=0.35)
    E.face_rect(m, "u", 1, TOP, -0.035, 0.035, -1.95, 1.95, -0.004, 0.008, "glow_amber")
    return m.finish(BUDGET, texture_size=1024)
