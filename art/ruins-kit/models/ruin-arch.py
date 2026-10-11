"""Ruin arch: 4 m modular gateway with a pointed arch.
Concept: codex/concepts/v0.2/32-ancient-ruins-kit.png (pointed arch doorway).

Grid: 4 m wide (x -2..2), 1 m thick, 5.2 m tall; replaces one ruin-wall section.
Opening 2.2 m wide, 4.2 m to the apex (walk-through). A molded arch band traced
by a glowing glyph line, a keystone, impost blocks and glyph medallions on the
side slabs. Origin at the base center.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (300, 1000)
S = "ruin_slate"
HALF = 1.1      # half opening width
SPRING = 2.6    # where the arch starts curving
R = 1.76        # radius of each arc of the pointed arch


def arch_curve(half, radius, n=8):
    """Left jamb top to apex to right jamb top of a pointed arch, (x, u) points."""
    cx = -half + radius   # left arc is centered right of the opening's left edge
    apex_dx = -cx         # apex at x = 0
    a0 = math.pi
    a1 = math.acos(apex_dx / radius) if abs(apex_dx / radius) <= 1 else math.pi / 2
    left = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        left.append((cx + radius * math.cos(a), SPRING + radius * abs(math.sin(a))))
    right = [(-x, u) for x, u in reversed(left[:-1])]
    return left + right


def build():
    rng = random.Random(31)
    m = E.Model("ruin-arch", category="ruins-kit", bevel=0.02, cage=0.06)
    T = 0.5
    inner = arch_curve(HALF + 0.02, R + 0.02)
    body = [(-2.0, 0.0), (-HALF - 0.02, 0.0)] + inner + [(HALF + 0.02, 0.0), (2.0, 0.0), (2.0, 4.9), (1.2, 5.05), (0.0, 5.0), (-1.3, 4.95), (-2.0, 4.9)]
    m.front_prism(body, -T, T, S)
    # Arch molding: a U-shaped band around the opening, standing proud of both faces.
    ins = [(-HALF, 0.5)] + arch_curve(HALF, R) + [(HALF, 0.5)]
    outs = [(-HALF - 0.36, 0.5)] + arch_curve(HALF + 0.36, R + 0.36) + [(HALF + 0.36, 0.5)]
    m.front_prism(outs + list(reversed(ins)), -T - 0.08, T + 0.08, S)

    for s in (-1, 1):
        E.block(m, (s * 1.62, 0, 0.25), (0.76, 1.24, 0.5), "ruin_slate_dark", bevel=0.05, jitter=0.012, seed=1 + s)
        E.block(m, (s * 1.33, 0, SPRING + 0.12), (0.7, 1.26, 0.26), S, bevel=0.05, jitter=0.012, seed=3 + s)
        E.block(m, (s * 1.75, 0, 2.6), (0.5, 1.1, 4.2), S, bevel=0.05, jitter=0.015, seed=5 + s)
        cap = E.block(m, (s * 1.45, 0, 5.12), (1.15, 1.16, 0.34), S, bevel=0.06, jitter=0.03, seed=7 + s, rot=(rng.uniform(-3, 3), 0, rng.uniform(-3, 3)))
        E.paint_up(cap, "moss", prob=0.8, seed=9 + s)
    key = E.block(m, (0, 0, R * 0.93 + SPRING + 0.2), (0.5, 1.24, 0.75), S, bevel=0.05, jitter=0.01, seed=12, taper=1.25)
    E.paint_up(key, "moss", prob=0.6, seed=13)
    top = E.block(m, (0, 0, 5.12), (0.9, 1.1, 0.3), S, bevel=0.05, jitter=0.03, seed=14)
    E.paint_up(top, "moss", prob=0.8, seed=15)

    apex = R * math.sin(math.acos((R - HALF) / R)) + SPRING
    for s in (-1, 1):
        # Glow line tracing the arch band, broken by the keystone.
        trace = [(x, u) for x, u in arch_curve(HALF + 0.18, R + 0.18, n=10)]
        trace = [(-HALF - 0.18, 0.55)] + trace + [(HALF + 0.18, 0.55)]
        left = [p for p in trace if p[0] < -0.28]
        right = [p for p in trace if p[0] > 0.28]
        for part in (left, right):
            E.strip(m, "f", s, s * (T + 0.08), part, 0.05, -0.004, 0.012, "glow_glyph")
        # Voussoir joints across the band.
        band = arch_curve(HALF + 0.18, R + 0.18, n=10)
        for i in range(1, len(band) - 1, 2):
            x, u = band[i]
            cx = -HALF + R if x < 0 else HALF - R
            d = math.hypot(x - cx, u - SPRING) or 1
            nx, nu = (x - cx) / d, (u - SPRING) / d
            E.strip(m, "f", s, s * (T + 0.08), [(x - nx * 0.17, u - nu * 0.17), (x - nx * 0.04, u - nu * 0.04)], 0.025, -0.004, 0.006, "crack")
            E.strip(m, "f", s, s * (T + 0.08), [(x + nx * 0.04, u + nu * 0.04), (x + nx * 0.17, u + nu * 0.17)], 0.025, -0.004, 0.006, "crack")
        for side in (-1, 1):
            sk = E.glyph_column(m, "f", s, s * 0.55, side * 1.75, 0.6, 4.6, rings=(2.0,), stone=S, r=0.2)
            E.masonry(m, "f", s, s * 0.55, side * 1.75 - 0.25, side * 1.75 + 0.25, 0.5, 4.7, rng, E.SLATE, course=(0.5, 1.0),
                      length=(0.6, 0.6), skip=sk, margin=0.02)
        # Wall face above the arch.
        E.masonry(m, "f", s, s * T, -1.53, 1.53, apex - 0.2, 4.95, rng, E.SLATE, course=(0.3, 0.5), length=(0.4, 0.9),
                  skip=[(-0.3, 0.3, 0, 9)], top_fn=None)
        E.masonry(m, "f", s, s * T, -1.53, -HALF - 0.36, 0.5, apex, rng, E.SLATE, course=(0.4, 0.7), length=(0.3, 0.5), margin=0.02)
        E.masonry(m, "f", s, s * T, HALF + 0.36, 1.53, 0.5, apex, rng, E.SLATE, course=(0.4, 0.7), length=(0.3, 0.5), margin=0.02)
        E.masonry(m, "f", s, s * 0.62, -2.0, -1.24, 0.02, 0.48, rng, ["ruin_slate_dark"], course=(0.5, 0.5), length=(0.8, 0.8))
        E.masonry(m, "f", s, s * 0.62, 1.24, 2.0, 0.02, 0.48, rng, ["ruin_slate_dark"], course=(0.5, 0.5), length=(0.8, 0.8))
        E.vines(m, "f", s, s * 0.55, -1.95, -1.55, 4.7, rng, count=1, length=(0.8, 2.6), b_min=0.6)
        E.vines(m, "f", s, s * 0.55, 1.55, 1.95, 4.7, rng, count=1, length=(0.8, 2.6), b_min=0.6)
        E.vines(m, "f", s, s * T, -1.4, 1.4, 4.9, rng, count=2, length=(0.3, 0.6), b_min=4.0)
    for s in (-1, 1):
        E.masonry(m, "x", s, s * 2.0, -0.55, 0.55, 0.5, 4.7, rng, E.SLATE, course=(0.5, 0.9), length=(1.1, 1.1))
    return m.finish(BUDGET, texture_size=1024)
