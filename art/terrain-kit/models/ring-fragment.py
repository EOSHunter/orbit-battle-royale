"""Ring fragment: a fallen segment of the planet's orbital ring, half buried.
Concept: codex/concepts/v0.2/35-glass-basin.png (curved ring wreck with amber
lights rising from the basin) and 29-ringfall-terrain-overview.png.

A curved, plated alloy beam (2.6 x 1.8 m section) bursting from a crater and
arching 8 m up and 4 m over, its top snapped into torn plates and struts;
amber running lights in its sides, a broken chunk lying beside it.
Footprint about 8 x 5 m. Origin at the base center (where it enters the ground).
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (300, 1000)
R = 14.0
PHI = math.radians(38)
PROFILE = [(1.3, -0.6), (1.3, 0.6), (1.0, 0.9), (-1.0, 0.9), (-1.3, 0.6), (-1.3, -0.6), (-1.0, -0.9), (1.0, -0.9)]
NORMAL = (0.0, 1.0, 0.0)


def arc(n, p0=0.0, p1=1.0):
    out = []
    for i in range(n):
        ph = PHI * (p0 + (p1 - p0) * i / (n - 1))
        out.append((R - R * math.cos(ph) - 0.6, 0.0, -1.6 + R * math.sin(ph)))
    return out


def offset(pts, db, dn):
    """Shift a path across (b) and along the normal (n) using the sweep frames."""
    out = []
    for P, T, B, N in E.frames(pts, NORMAL):
        out.append(E.xfu(P + B * db + N * dn))
    return out


def build():
    rng = random.Random(147)
    m = E.Model("ring-fragment", category="terrain-kit", bevel=0.015, cage=0.05)
    main = arc(9)
    E.profile_sweep(m, main, PROFILE, "ring_alloy", normal=NORMAL)
    # Structural frames: proud bands every ~1.7 m.
    for t in (0.12, 0.3, 0.48, 0.66, 0.84):
        seg = arc(2, t - 0.018, t + 0.018)
        E.profile_sweep(m, seg, PROFILE, "ring_panel", normal=NORMAL, scale=[1.1, 1.1])
    # Torn end: shards of plating and exposed struts.
    (P, T, B, N) = E.frames(main, NORMAL)[-1]
    top = E.xfu(P)
    tdir = E.xfu(T)
    for i, (db, dn) in enumerate(((1.1, 0.6), (-1.0, 0.75), (0.4, -0.8), (-1.15, -0.5), (0.9, -0.2))):
        base = E.xfu(P + B * db + N * dn)
        tip = (base[0] + tdir[0] * rng.uniform(0.6, 1.4) + rng.uniform(-0.3, 0.3), base[1] + rng.uniform(-0.3, 0.3),
               base[2] + tdir[2] * rng.uniform(0.6, 1.4))
        E.sweep(m, [base, tip], [0.28, 0.0], "ring_alloy", sides=4, flat=0.25, tip=True, normal=(dn, 1.0, db))
    for db, dn in ((0.5, 0.3), (-0.5, -0.3), (0.0, 0.5), (-0.6, 0.35)):
        base = E.xfu(P + B * db + N * dn - T * 0.3)
        L = rng.uniform(0.8, 1.6)
        tip = (base[0] + tdir[0] * L + rng.uniform(-0.25, 0.25), base[1] + rng.uniform(-0.25, 0.25), base[2] + tdir[2] * L)
        E.sweep(m, [base, tip], [0.09, 0.07], "gunmetal", sides=5)
    # Crater lip of churned rock and a broken chunk of the ring beside it.
    for i, (x, f, s) in enumerate(((-1.6, 1.4, 0.9), (1.4, -1.6, 1.0), (-1.9, -1.2, 0.7), (1.7, 1.5, 0.75))):
        E.rock(m, (x, f, 0.1), (s * 1.3, s, s * 0.55), "rock_gray", seed=50 + i, subdiv=1, cuts=4, cut_depth=0.3, floor=-0.3,
               top_mat="soil", top_prob=0.7, top_thresh=0.6)
    chunk = [(3.2, -2.6, -0.4), (4.4, -2.0, 0.1), (5.4, -1.2, 0.2)]
    E.profile_sweep(m, chunk, [(b * 0.75, n * 0.75) for b, n in PROFILE], "ring_alloy", normal=(0.2, 0.3, 1.0))

    # Baked details: plating panels with seams, amber light strips, rivet rows.
    for t0, t1 in ((0.0, 0.1), (0.14, 0.28), (0.32, 0.46), (0.5, 0.64), (0.68, 0.82), (0.86, 1.0)):
        seg = arc(4, t0 + 0.006, t1 - 0.006)
        for side in (-1, 1):
            # Side faces (normal axis): two panels each, amber strip between.
            E.profile_sweep(m, seg, [(0.08, side * 0.9), (0.95, side * 0.9), (0.95, side * 0.915), (0.08, side * 0.915)],
                            "ring_panel", normal=NORMAL, detail=True)
            E.profile_sweep(m, seg, [(-0.95, side * 0.9), (-0.08, side * 0.9), (-0.08, side * 0.915), (-0.95, side * 0.915)],
                            "ring_panel", normal=NORMAL, detail=True)
            E.profile_sweep(m, seg, [(-0.05, side * 0.9), (0.05, side * 0.9), (0.05, side * 0.908), (-0.05, side * 0.908)],
                            "glow_amber", normal=NORMAL, detail=True)
            # Outer and inner curved faces: plates with seams.
            E.profile_sweep(m, seg, [(side * 1.3, -0.5), (side * 1.318, -0.5), (side * 1.318, 0.5), (side * 1.3, 0.5)],
                            "ring_panel", normal=NORMAL, detail=True)
        # Lights in the outer face.
        if t0 > 0.1:
            E.profile_sweep(m, arc(2, t0 + 0.03, t0 + 0.06), [(1.29, -0.12), (1.312, -0.12), (1.312, 0.12), (1.29, 0.12)],
                            "glow_amber", normal=NORMAL, detail=True)
    return m.finish(BUDGET, texture_size=1024)
