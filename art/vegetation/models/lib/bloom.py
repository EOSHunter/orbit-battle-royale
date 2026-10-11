"""Shared builders for the Bloomwild flower pieces (stalk, cap, small flower).
Concept: codex/concepts/v0.2/30-luminous-vegetation.png (giant bulb flowers).
"""

import math

import envkit as E


def stalk(m, rng, height, strands=3, r_strand=0.13, twist=2.2, spread=0.17, sides=6, n=8, mat="stem"):
    """Twisted stalk of braided strands with flared feet. Returns the top point (x, f, u)."""
    for j in range(strands):
        pts, radii = [], []
        for i in range(n):
            t = i / (n - 1)
            th = 2 * math.pi * j / strands + t * twist
            rr = spread * (1 - 0.35 * t) + (0.28 * (0.18 - t) / 0.18 if t < 0.18 else 0.0)
            pts.append((rr * math.cos(th), rr * math.sin(th), -0.05 + t * height))
            radii.append(r_strand * (1 - 0.4 * t))
        E.sweep(m, pts, radii, mat, sides=sides)
    return (0.0, 0.0, height)


def roots(m, rng, count, reach, mat="stem", r=0.08):
    for j in range(count):
        a = 2 * math.pi * j / count + rng.uniform(-0.3, 0.3)
        d = (math.cos(a), math.sin(a))
        L = reach * rng.uniform(0.75, 1.1)
        pts = [(d[0] * 0.12, d[1] * 0.12, 0.35 * reach), (d[0] * L * 0.45, d[1] * L * 0.45, 0.06), (d[0] * L, d[1] * L, -0.06)]
        E.sweep(m, pts, [r, r * 0.6, 0.0], mat, sides=5, tip=True)


def big_leaf(m, rng, a, length, width, base_u, mat="leaf_sage", vein="glow_teal", n=7, droop=0.5):
    """Arching, cupped leaf rising from the stalk foot. Glowing midrib baked (detail)."""
    d = (math.cos(a), math.sin(a))
    pts = []
    for i in range(n):
        t = i / (n - 1)
        reach = length * (0.12 + 0.88 * t)
        up = base_u + length * (0.9 * math.sin(t * math.pi * 0.55) - droop * t * t)
        pts.append((d[0] * reach * t ** 0.6, d[1] * reach * t ** 0.6, up))
    prof = [0.05, 0.55, 0.85, 1.0, 0.9, 0.55, 0.0][:n] if n == 7 else [max(0.0, math.sin(math.pi * i / (n - 1)) ** 0.7) for i in range(n)]
    radii = [width * p for p in prof]
    radii[0] = max(radii[0], 0.03)
    normal = (-d[0], -d[1], 0.6)
    E.sweep(m, pts, radii, mat, sides=4, flat=0.1, fold=0.4, normal=normal, tip=True)
    if vein:
        rib = E.on_ribbon(pts[:-1], radii[:-1], normal, 0.0, 0.004, flat=0.1, fold=0.4)
        E.sweep(m, rib, [0.012] * len(rib), vein, sides=3, detail=True)
        for k in (-0.55, 0.55):
            lat = E.on_ribbon(pts[1:-1], radii[1:-1], normal, k, 0.004, flat=0.1, fold=0.4)
            E.sweep(m, lat, [0.007] * len(lat), vein, sides=3, detail=True)


def petal_bulb(m, rng, center_u, base_u, radius, height, petals, petal_mat="petal", glow="glow_amber", n=7, gap=0.82):
    """Closed bulb of cupped petals around a glowing core, petal rims and midribs glowing (baked)."""
    for j in range(petals):
        a = 2 * math.pi * j / petals + rng.uniform(-0.06, 0.06)
        d = (math.cos(a), math.sin(a))
        prof = [(0.2, 0.0), (0.62, 0.17), (0.95, 0.4), (1.0, 0.62), (0.78, 0.82), (0.45, 0.96), (0.42, 1.05)]
        pts = []
        for (rr, hh) in prof[:n]:
            rr *= radius * rng.uniform(0.96, 1.04)
            pts.append((d[0] * rr, d[1] * rr, base_u + hh * height))
        # Curl the tip outward.
        last = pts[-1]
        pts[-1] = (last[0] + d[0] * radius * 0.18, last[1] + d[1] * radius * 0.18, last[2])
        half = math.pi * radius / petals * gap
        radii = [half * w for w in (0.3, 0.75, 0.95, 1.0, 0.85, 0.5, 0.0)[:n]]
        normal = (d[0], d[1], 0.0)
        E.sweep(m, pts, radii, petal_mat, sides=4, flat=0.12, fold=-0.3, normal=normal, tip=True)
        for k, w in ((0.0, 0.011), (-0.9, 0.012), (0.9, 0.012)):
            line = E.on_ribbon(pts[1:-1], radii[1:-1], normal, k, 0.006, flat=0.12, fold=-0.3)
            E.sweep(m, line, [w] * len(line), glow, sides=3, detail=True)
    m.sphere(0.0, center_u, radius * 0.86, glow, segments=8, rings=6, scale=(1.0, 1.0, height / (2 * radius) * 1.05))


def stamens(m, rng, count, top_u, spread, length, stem="petal", tip="glow_amber"):
    for j in range(count):
        a = 2 * math.pi * j / count + rng.uniform(-0.3, 0.3)
        d = (math.cos(a), math.sin(a))
        L = length * rng.uniform(0.75, 1.15)
        sp = spread * rng.uniform(0.6, 1.2)
        p0 = (d[0] * 0.05, d[1] * 0.05, top_u - 0.15)
        p1 = (d[0] * sp * 0.4, d[1] * sp * 0.4, top_u + L * 0.6)
        p2 = (d[0] * sp, d[1] * sp, top_u + L)
        E.sweep(m, [p0, p1, p2], [0.012, 0.009, 0.006], stem, sides=3)
        E.bud(m, (p2[0], p2[1], p2[2] - 0.02), (p2[0] + d[0] * 0.02, p2[1] + d[1] * 0.02, p2[2] + 0.07), 0.035, tip)
