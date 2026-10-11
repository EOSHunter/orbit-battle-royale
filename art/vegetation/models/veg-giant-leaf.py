"""Giant leaf: a clump of huge Bloomwild understory leaves with luminous veins.
Concept: codex/concepts/v0.2/36-bloomwild.png (violet-pink giant leaves) and
30-luminous-vegetation.png.

Three to four broad cupped leaves up to 3 m long arching from one crown, about
4 m across and 2.2 m tall: big cover-breaking foliage. Glowing violet midribs and
lateral veins are baked into the emission map. Origin at the base center.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)


def leaf(m, rng, a, length, width, rise, mat):
    d = (math.cos(a), math.sin(a))
    n = 10
    pts, radii = [], []
    for i in range(n):
        t = i / (n - 1)
        reach = length * t
        up = rise * math.sin(min(1.0, t * 1.5) * math.pi * 0.5) - rise * 0.75 * max(0.0, t - 0.55) ** 2 * 4
        # A slight sideways sweep so the leaves don't look stamped.
        side = 0.12 * length * math.sin(t * math.pi) * rng.choice((-1, 1))
        pts.append((d[0] * reach - d[1] * side, d[1] * reach + d[0] * side, 0.05 + up))
        radii.append(width * (math.sin(math.pi * min(1.0, t * 1.08)) ** 0.75) if i < n - 1 else 0.0)
    radii[0] = 0.035
    normal = (-d[0] * 0.3, -d[1] * 0.3, 1.0)
    E.sweep(m, pts, radii, mat, sides=4, flat=0.08, fold=0.32, normal=normal, tip=True)
    # Stem keel under the midrib.
    E.sweep(m, [(0, 0, -0.05), pts[1], pts[2]], [0.06, 0.045, 0.03], "stem", sides=5)
    # Glowing veins (baked): midrib and pairs of laterals running out to the edge.
    rib = E.on_ribbon(pts[:-1], radii[:-1], normal, 0.0, 0.005, flat=0.08, fold=0.32)
    E.sweep(m, rib, [0.018] * len(rib), "glow_violet", sides=3, detail=True)
    for s in (-1, 1):
        r45 = E.on_ribbon(pts[:-1], radii[:-1], normal, s * 0.45, 0.005, flat=0.08, fold=0.32)
        r85 = E.on_ribbon(pts[:-1], radii[:-1], normal, s * 0.85, 0.005, flat=0.08, fold=0.32)
        for i in range(1, n - 3):
            mid = tuple((r45[i][k] + r45[i + 1][k]) / 2 for k in range(3))
            E.sweep(m, [rib[i], mid, r85[i + 1]], [0.01, 0.008, 0.005], "glow_violet", sides=3, detail=True)


def build():
    rng = random.Random(57)
    m = E.Model("veg-giant-leaf", category="vegetation", bevel=0.006, cage=0.03)
    for a, L, w, rise, mat in ((0.2, 2.9, 0.62, 1.7, "leaf_violet"), (2.3, 2.5, 0.55, 1.4, "leaf_violet"),
                               (4.1, 2.3, 0.5, 1.25, "leaf_teal"), (5.3, 1.6, 0.4, 1.2, "leaf_violet")):
        leaf(m, rng, a + rng.uniform(-0.15, 0.15), L, w, rise, mat)
    # Small curled shoot in the crown.
    E.sweep(m, [(0, 0, 0), (0.05, 0.02, 0.35), (0.12, 0.0, 0.55), (0.18, -0.06, 0.5)], [0.05, 0.045, 0.035, 0.0], "leaf_teal", sides=5, tip=True)
    return m.finish(BUDGET, texture_size=1024)
