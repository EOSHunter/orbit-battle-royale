"""Ruin canyon arch: the great ring-arch gate that spans the Hollow Array canyons.
Concept: codex/concepts/v0.2/39-hollow-array.png (semicircular arch over the canyon).

A semicircular ring of voussoirs on two square legs: 14 m outer span
(x -7..7), 12 m clear opening, 13 m tall, 2 m deep (f -1..1). Warm umber stone,
a glowing channel tracing the ring on both faces, medallions on the legs and a
projecting keystone. Fits a 16 m (4 x 4 m cells) gap. Origin at the base center.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (300, 1000)
S = "ruin_umber"
RI = 5.6
RO = 7.0
SPRING = 6.0
N = 14


def ring_pts(r, n=N):
    return [(r * math.cos(math.pi * i / n), SPRING + r * math.sin(math.pi * i / n)) for i in range(n + 1)]


def build():
    rng = random.Random(101)
    m = E.Model("ruin-canyon-arch", category="ruins-kit", bevel=0.02, cage=0.06)
    # Legs and arch as one U-shaped outline (front view), 2 m deep.
    outer = [(RO, 0.0)] + ring_pts(RO)[:] + [(-RO, 0.0)]
    inner = [(-RI, 0.0)] + list(reversed(ring_pts(RI))) + [(RI, 0.0)]
    m.front_prism(outer + inner, -1.0, 1.0, S)
    # Plinths, imposts and the keystone.
    for s in (-1, 1):
        p = E.block(m, (s * 6.3, 0, 0.45), (2.2, 2.6, 0.9), "ruin_slate_dark", bevel=0.07, jitter=0.02, seed=1 + s)
        E.paint_up(p, "moss", prob=0.6, seed=1 + s)
        E.block(m, (s * 6.3, 0, SPRING - 0.2), (1.9, 2.4, 0.5), S, bevel=0.06, jitter=0.02, seed=3 + s)
    E.block(m, (0, 0, SPRING + RO - 0.55), (1.0, 2.4, 1.7), S, bevel=0.06, jitter=0.015, seed=5, taper=1.3)
    # Voussoirs that have slipped proud of the ring.
    for i, k in enumerate((3, 5, 10, 12)):
        a = math.pi * (k + 0.5) / N
        cx, cu = (RI + RO) / 2 * math.cos(a), SPRING + (RI + RO) / 2 * math.sin(a)
        E.block(m, (cx, 0, cu), (1.5, 2.1 + 0.06 * (i % 2), 1.0), S, bevel=0.06, jitter=0.03, seed=10 + i,
                rot=(0, -math.degrees(a) + 90, 0))
    # Broken chunks at the foot of the legs.
    for i, (x, f, sz) in enumerate(((7.6, -1.2, 0.8), (-7.7, 0.9, 0.7), (5.2, 1.7, 0.5), (-5.0, -1.8, 0.6))):
        E.block(m, (x, f, sz * 0.4), (sz * 1.3, sz, sz * 0.8), S, bevel=0.06, jitter=0.05, seed=20 + i,
                rot=(rng.uniform(-12, 12), rng.uniform(-12, 12), rng.uniform(0, 90)), top_mat="moss", top_prob=0.6)

    mid = (RI + RO) / 2
    for s in (-1, 1):
        # Glow channel tracing the ring, between raised lips.
        path = ring_pts(mid, n=28)
        left = [p for p in path if p[0] < -0.55]
        right = [p for p in path if p[0] > 0.55]
        for part in (left, right):
            part = ([(part[0][0], SPRING - 0.5)] + part) if part[0][1] < SPRING + 0.5 else part
            if part[-1][1] < SPRING + 0.5:
                part = part + [(part[-1][0], SPRING - 0.5)]
            E.strip(m, "f", s, s * 1.0, part, 0.12, -0.004, 0.012, "glow_glyph")
            for off in (-0.15, 0.15):
                lip =[((x / mid) * (mid + off) if u > SPRING else x + math.copysign(off, x), (SPRING + (u - SPRING) * (mid + off) / mid) if u > SPRING else u)
                       for x, u in part]
                E.strip(m, "f", s, s * 1.0, lip, 0.08, -0.004, 0.028, S)
        # Voussoir joints.
        for k in range(1, N):
            a = math.pi * k / N
            c, sn = math.cos(a), math.sin(a)
            for r0, r1 in ((RI + 0.05, mid - 0.25), (mid + 0.25, RO - 0.05)):
                E.strip(m, "f", s, s * 1.0, [(r0 * c, SPRING + r0 * sn), (r1 * c, SPRING + r1 * sn)], 0.04, -0.004, 0.008, "crack")
        # Legs: courses and medallions.
        for side in (-1, 1):
            sk = E.glyph_column(m, "f", s, s * 1.0, side * mid, 0.92, SPRING - 0.5, rings=(3.4,), stone=S, w=0.12, r=0.45)
            E.masonry(m, "f", s, s * 1.0, min(side * RO, side * RI), max(side * RO, side * RI), 0.9, SPRING - 0.45, rng, E.UMBER,
                      course=(0.6, 1.1), length=(0.6, 0.6), skip=sk, margin=0.03)
        E.vines(m, "f", s, s * 1.0, -RO + 0.2, -RI - 0.2, SPRING - 0.5, rng, count=1, length=(1.0, 3.0), b_min=1.0)
        E.vines(m, "f", s, s * 1.0, RI + 0.2, RO - 0.2, SPRING - 0.5, rng, count=1, length=(1.0, 3.0), b_min=1.0)
    for s in (-1, 1):
        E.masonry(m, "x", s, s * RO, -1.0, 1.0, 0.9, SPRING - 0.45, rng, E.UMBER, course=(0.6, 1.1), length=(1.0, 1.0), margin=0.03)
        E.masonry(m, "x", -s, s * RI, -1.0, 1.0, 0.9, SPRING - 0.45, rng, E.UMBER, course=(0.6, 1.1), length=(1.0, 1.0), margin=0.03)
    return m.finish(BUDGET, texture_size=1024)
