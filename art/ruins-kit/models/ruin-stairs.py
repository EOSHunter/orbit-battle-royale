"""Ruin stairs: 4 x 4 m stair module climbing 2 m.
Concept: codex/concepts/v0.2/32-ancient-ruins-kit.png (stair block).

Grid: x -2..2, f -2..2 (climbs toward +f), eight 0.25 m risers on 0.5 m treads,
top tread at u = 2.0 so it meets a 2 m terrace. 3.2 m walkable width between
sloped cheek walls carrying teal glyph lines; medallions on the newels.
Origin at the base center.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (250, 1000)
S = "ruin_slate"
STEPS = 8
RISE = 0.25
RUN = 0.5


def build():
    rng = random.Random(51)
    m = E.Model("ruin-stairs", category="ruins-kit", bevel=0.02, cage=0.06)
    prof = [(-2.0, 0.0), (2.0, 0.0), (2.0, STEPS * RISE)]
    for i in reversed(range(STEPS)):
        f0 = -2.0 + i * RUN
        u = (i + 1) * RISE
        prof += [(f0, u), (f0, u - RISE)] if i > 0 else [(f0, u)]
    steps = m.prism(prof, 3.2, S)
    E.paint_up(steps, "moss_dark", prob=0.15, seed=3)

    # Sloped cheek walls and newel blocks.
    for s in (-1, 1):
        m.prism([(-2.0, 0.0), (2.0, 0.0), (2.0, 2.5), (1.55, 2.5), (-1.75, 0.68), (-2.0, 0.68)], 0.4, S, x=s * 1.8)
        nb = E.block(m, (s * 1.8, -1.72, 0.5), (0.56, 0.6, 1.0), S, bevel=0.05, jitter=0.02, seed=10 + s)
        E.paint_up(nb, "moss", prob=0.8, seed=12 + s)
        E.block(m, (s * 1.8, -1.72, 1.08), (0.44, 0.46, 0.18), S, bevel=0.04, jitter=0.02, seed=14 + s, rot=(0, 0, 8 * s))
        tb = E.block(m, (s * 1.8, 1.75, 2.62), (0.52, 0.5, 0.3), S, bevel=0.05, jitter=0.02, seed=16 + s)
        E.paint_up(tb, "moss", prob=0.8, seed=18 + s)
    # A cracked tread stone lifted out of place, and rubble at the foot.
    E.block(m, (0.7, -0.75, 0.81), (1.0, 0.5, 0.14), S, bevel=0.04, jitter=0.02, seed=20, rot=(6, -4, 7))
    for i, (x, f, sz) in enumerate(((-1.2, -2.35, 0.35), (1.3, -2.3, 0.28), (0.2, -2.45, 0.22))):
        E.block(m, (x, f, sz * 0.4), (sz * 1.3, sz, sz * 0.8), S, bevel=0.05, jitter=0.04, seed=30 + i,
                rot=(rng.uniform(-12, 12), rng.uniform(-12, 12), rng.uniform(0, 90)), top_mat="moss", top_prob=0.6)

    # Treads and risers: individual stones.
    for i in range(STEPS):
        f0 = -2.0 + i * RUN
        u = (i + 1) * RISE
        E.masonry(m, "u", 1, u, -1.6, 1.6, f0, f0 + RUN, rng, E.SLATE, course=(RUN, RUN), length=(0.5, 1.3), margin=0.03, crack_prob=0.3)
        E.masonry(m, "f", -1, f0, -1.6, 1.6, u - RISE, u, rng, E.SLATE, course=(RISE, RISE), length=(0.5, 1.3), margin=0.02, crack_prob=0.0)
    for s in (-1, 1):
        slope = lambda a: 0.68 + (a + 1.75) * (2.5 - 0.68) / 3.3  # noqa: E731
        # Outer and inner faces of the cheek walls: courses under the sloped top, glyph line along it.
        for plane in (2.0, 1.6):
            ax_sign = s if plane == 2.0 else -s
            E.masonry(m, "x", ax_sign, s * plane, -2.0, 2.0, 0.0 if plane == 2.0 else 0.25, 2.5, rng, E.SLATE, course=(0.4, 0.7),
                      length=(0.6, 1.2), top_fn=lambda a: min(2.5, slope(a)) - 0.25 if a < 1.55 else 2.25, margin=0.03)
            E.strip(m, "x", ax_sign, s * plane, [(-1.85, 0.5), (1.5, slope(1.5) - 0.18), (1.95, slope(1.5) - 0.18)], 0.045, -0.004, 0.03, "glow_glyph")
        # Medallion on the front of each newel.
        E.face_ring(m, "f", -1, -2.02, s * 1.8, 0.55, 0.19, 0.15, -0.004, 0.026, S)
        E.face_ring(m, "f", -1, -2.02, s * 1.8, 0.55, 0.13, 0.1, -0.004, 0.02, "glow_glyph")
        E.face_disc(m, "f", -1, -2.02, s * 1.8, 0.55, 0.05, -0.004, 0.024, "glow_glyph", segs=8)
        E.vines(m, "x", s, s * 2.0, -1.5, 1.5, 2.3, rng, count=2, length=(0.4, 1.0), b_min=0.2, top_fn=lambda a: slope(a) - 0.05)
    E.masonry(m, "f", 1, 2.0, -2.0, 2.0, 0.0, 2.0, rng, E.SLATE, course=(0.4, 0.7), length=(0.6, 1.4))
    return m.finish(BUDGET, texture_size=1024)
