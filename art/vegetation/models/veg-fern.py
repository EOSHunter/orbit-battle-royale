"""Fern: an alien fern rosette with curled fiddleheads.
Concept: codex/concepts/v0.2/36-bloomwild.png (understory ferns) and
30-luminous-vegetation.png.

About 1.8 m across, 1 m tall. Arching fronds of teal-sage leaflets on a
stem with a faint lime glowing midrib (baked), two glowing curled fiddleheads
in the crown. Origin at the base center.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
import envkit as E  # noqa: E402

BUDGET = (100, 800)


def build():
    rng = random.Random(97)
    m = E.Model("veg-fern", category="vegetation", bevel=0.003, cage=0.02)
    for j in range(7):
        a = 2 * math.pi * j / 7 + rng.uniform(-0.2, 0.2)
        d = (math.cos(a), math.sin(a))
        L = rng.uniform(0.8, 1.05)
        rise = rng.uniform(0.55, 0.85)
        pts = []
        for i in range(6):
            t = i / 5
            reach = L * t
            up = rise * math.sin(t * math.pi * 0.7) / math.sin(math.pi * 0.7) - 0.25 * t ** 3
            pts.append((d[0] * reach, d[1] * reach, -0.03 + up))
        E.sweep(m, pts, [0.016, 0.013, 0.011, 0.008, 0.005, 0.0], "stem", sides=3, tip=True)
        rib = [(p[0], p[1], p[2] + 0.012) for p in pts[1:-1]]
        E.sweep(m, rib, [0.006] * len(rib), "glow_lime", sides=3, detail=True)
        # Leaflets: alternating pairs, shrinking toward the tip.
        for i in range(1, 5):
            for s in (-1, 1):
                t = (i + (0.25 if s > 0 else 0.0)) / 5.0
                k = t * 5
                i0 = min(int(k), 4)
                w = k - i0
                base = tuple(pts[i0][q] * (1 - w) + pts[i0 + 1][q] * w for q in range(3))
                size = 0.3 * (1 - t * 0.7)
                side = (-d[1] * s, d[0] * s)
                tip = (base[0] + side[0] * size + d[0] * size * 0.45, base[1] + side[1] * size + d[1] * size * 0.45, base[2] - size * 0.2)
                E.leaf(m, base, tip, size * 0.3, "leaf_teal" if (i + j) % 3 else "leaf_sage", normal=(0, 0, 1), cup=0.35)
    # Fiddleheads: tight spirals on short stalks.
    for j in range(2):
        a = rng.uniform(0, 2 * math.pi)
        c = (math.cos(a) * 0.08, math.sin(a) * 0.08)
        pts = [(c[0], c[1], -0.02), (c[0], c[1], 0.3)]
        for i in range(7):
            th = i * 0.9
            rr = 0.09 * (1 - i / 8)
            pts.append((c[0] + math.cos(a) * rr * math.sin(th), c[1] + math.sin(a) * rr * math.sin(th), 0.3 + 0.09 + rr * math.cos(th) - 0.09 * 0 + 0.0))
        E.sweep(m, pts, [0.022, 0.02] + [0.018 - 0.002 * i for i in range(7)], "leaf_teal", sides=3)
        E.bud(m, pts[-1], (pts[-1][0], pts[-1][1], pts[-1][2] + 0.03), 0.02, "glow_lime")
    return m.finish(BUDGET, texture_size=512)
