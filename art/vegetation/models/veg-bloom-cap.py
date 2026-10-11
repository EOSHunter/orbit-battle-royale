"""Bloom cap: the glowing bulb of a giant Bloomwild flower.
Concept: codex/concepts/v0.2/30-luminous-vegetation.png (golden bulb flower).

Pairs with veg-bloom-stalk: same origin (base center of the whole flower on the
ground); the bulb sits from u = 3.15 to about 5.0, 1.9 m across. Nine cupped
pale-lavender petals with glowing amber rims and midribs closed around an
amber core, a crown of glowing stamens, sepals gripping the stalk top.
Origin at the base center of the flower.
"""

import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "ruins-kit", "models", "lib"))
sys.path.insert(0, os.path.join(HERE, "lib"))
import envkit as E  # noqa: E402
import bloom  # noqa: E402

BUDGET = (100, 800)
BASE = 3.15


def build():
    rng = random.Random(37)
    m = E.Model("veg-bloom-cap", category="vegetation", bevel=0.006, cage=0.03)
    bloom.petal_bulb(m, rng, center_u=BASE + 0.85, base_u=BASE, radius=0.92, height=1.75, petals=9)
    bloom.stamens(m, rng, 8, BASE + 1.62, 0.55, 0.65)
    for j in range(5):
        a = 2 * math.pi * j / 5 + 0.3
        d = (math.cos(a), math.sin(a))
        pts = [(d[0] * 0.1, d[1] * 0.1, BASE - 0.15), (d[0] * 0.3, d[1] * 0.3, BASE + 0.05), (d[0] * 0.5, d[1] * 0.5, BASE + 0.35)]
        E.sweep(m, pts, [0.07, 0.06, 0.0], "leaf_sage", sides=3, flat=0.35, tip=True, normal=(d[0], d[1], 0.0))
    return m.finish(BUDGET, texture_size=1024)
