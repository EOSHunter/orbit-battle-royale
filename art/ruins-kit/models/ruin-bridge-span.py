"""Ruin bridge span: one 8 m arched segment of The Spine.
Concept: codex/concepts/v0.2/38-the-spine.png.

Pale weathered sandstone, segmental arch with a raised voussoir band traced by
an amber glow line, amber slits in the spandrels and low broken parapets.
Grid: f -4..4 (the span runs along f), deck 5 m wide (x -2.5..2.5), walking
surface at u = 0 (origin at the deck center, on the walking surface).
Assembly: ruin-bridge-pier is 4 m long along f with its top at u = 12; put
piers 12 m apart and a span midway between each pair, 12 m up:
pier at f = 0, span at f = 6, pier at f = 12, span at f = 18 ...
The arch springs from the pier faces at u = -4 (8 m above the pier base).
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import envkit as E  # noqa: E402

BUDGET = (300, 1000)
S = "ruin_sand"
HALF = 4.0
SPRING = -4.0
CROWN = -1.6
SAG = CROWN - SPRING
R = (HALF ** 2 + SAG ** 2) / (2 * SAG)
CU = CROWN - R


def arc(radius, n=12):
    """Intrados-style arc points (f, u) from f = +end to -end about the arch center."""
    a_end = math.asin(min(1.0, HALF / R))
    pts = []
    for i in range(n + 1):
        a = a_end - 2 * a_end * i / n
        pts.append((radius * math.sin(a), CU + radius * math.cos(a)))
    return pts


def under(f):
    """Height of the intrados at f."""
    return CU + math.sqrt(max(R * R - f * f, 0.0))


def build():
    rng = random.Random(71)
    m = E.Model("ruin-bridge-span", category="ruins-kit", bevel=0.02, cage=0.06)
    # Spandrel body: deck underside down to the arch, extruded across the bridge.
    m.prism([(-HALF, -0.55), (HALF, -0.55)] + arc(R), 4.4, S)
    # Voussoir band, proud of both spandrel faces.
    inner = arc(R)
    outer = [(p[0] * (R + 0.55) / R, CU + (p[1] - CU) * (R + 0.55) / R) for p in inner]
    outer = [(max(-HALF, min(HALF, f)), u) for f, u in outer]
    m.prism(list(reversed(outer)) + inner, 4.64, S)
    # Deck slab with a projecting cornice.
    E.block(m, (0, 0, -0.3), (5.2, 8.0, 0.6), S, bevel=0.06, jitter=0.01, seed=1)
    # Parapets: low blocks with a broken gap and a fallen stone.
    for s in (-1, 1):
        f = -4.0
        i = 0
        while f < 3.99:
            L = min(rng.uniform(1.4, 2.3), 4.0 - f)
            if not (s > 0 and i == 2):
                h = 0.95 if not (s < 0 and i == 1) else 0.55
                p = E.block(m, (s * 2.25, f + L / 2, h / 2), (0.5, L - 0.04, h), S, bevel=0.05, jitter=0.02, seed=10 + i + 5 * s,
                            rot=(0, rng.uniform(-1, 1), 0))
                E.paint_up(p, "moss", prob=0.6, seed=20 + i)
            f += L
            i += 1
    E.block(m, (1.4, 0.6, 0.18), (0.5, 0.9, 0.36), S, bevel=0.05, jitter=0.03, seed=40, rot=(10, 4, 70), top_mat="moss", top_prob=0.6)
    E.block(m, (-0.8, -2.3, 0.07), (0.3, 0.25, 0.14), S, bevel=0.03, jitter=0.02, seed=41, rot=(5, 5, 20))

    for s in (-1, 1):
        # Spandrel masonry above the band, amber slits, band joints and its glow line.
        band_top = lambda a: CU + math.sqrt(max((R + 0.55) ** 2 - a * a, 0.0))  # noqa: E731
        E.masonry(m, "x", s, s * 2.2, -HALF, HALF, SPRING, -0.6, rng, E.SAND, course=(0.4, 0.8), length=(0.6, 1.5),
                  bot_fn=band_top, margin=0.03, skip=[(-3.4, -3.0, -5, 0), (3.0, 3.4, -5, 0)])
        for fs in (-3.2, 3.2):
            E.face_rect(m, "x", s, s * 2.2, fs - 0.07, fs + 0.07, band_top(fs) + 0.25, -1.0, -0.004, 0.012, "glow_amber")
            E.face_rect(m, "x", s, s * 2.2, fs - 0.16, fs - 0.08, band_top(fs) + 0.2, -0.95, -0.004, 0.028, S)
            E.face_rect(m, "x", s, s * 2.2, fs + 0.08, fs + 0.16, band_top(fs) + 0.2, -0.95, -0.004, 0.028, S)
        mid = [(p[0] * (R + 0.27) / R, CU + (p[1] - CU) * (R + 0.27) / R) for p in arc(R, n=18)]
        E.strip(m, "x", s, s * 2.32, mid, 0.05, -0.004, 0.012, "glow_amber")
        for p in arc(R, n=14)[1:-1]:
            nf, nu = p[0] / R, (p[1] - CU) / R
            for d0, d1 in ((0.03, 0.2), (0.34, 0.52)):
                E.strip(m, "x", s, s * 2.32, [(p[0] + nf * d0, p[1] + nu * d0), (p[0] + nf * d1, p[1] + nu * d1)], 0.03, -0.004, 0.006, "crack")
        # Cornice face and parapet faces.
        E.masonry(m, "x", s, s * 2.6, -HALF, HALF, -0.6, 0.0, rng, E.SAND, course=(0.6, 0.6), length=(0.8, 1.6), margin=0.02)
        E.vines(m, "x", s, s * 2.6, -3.8, 3.8, -0.02, rng, count=3, length=(0.3, 0.55), b_min=-0.6, h=(0.018, 0.024))
    # Walking surface: big worn pavers with a center glyph line.
    E.masonry(m, "u", 1, 0.0, -2.0, 2.0, -HALF, HALF, rng, E.SAND, course=(0.8, 1.4), length=(0.7, 1.4), margin=0.02,
              skip=[(-0.1, 0.1, -5, 5)], crack_prob=0.35)
    E.face_rect(m, "u", 1, 0.0, -0.035, 0.035, -3.9, 3.9, -0.004, 0.008, "glow_amber")
    for _ in range(6):
        E.face_disc(m, "u", 1, 0.0, rng.choice((-1, 1)) * rng.uniform(1.4, 1.95), rng.uniform(-3.8, 3.8), rng.uniform(0.1, 0.25),
                    -0.004, 0.026, rng.choice(["moss", "moss_dark"]), segs=7)
    return m.finish(BUDGET, texture_size=1024)
