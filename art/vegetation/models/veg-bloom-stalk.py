"""Bloom stalk: the braided stalk, feet and big leaves of a giant Bloomwild flower.
Concept: codex/concepts/v0.2/30-luminous-vegetation.png (giant bulb flowers).

Pairs with veg-bloom-cap: both share the same origin (base center on the
ground), so place them with the same transform to assemble a 5 m flower.
Stalk top at u = 3.2. Three twisted strands, root feet and four arching cupped
leaves with faint teal veins. Origin at the base center.
"""

import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "ruins-kit", "models", "lib"))
sys.path.insert(0, os.path.join(HERE, "lib"))
import envkit as E  # noqa: E402
import bloom  # noqa: E402

BUDGET = (100, 800)


def build():
    rng = random.Random(27)
    m = E.Model("veg-bloom-stalk", category="vegetation", bevel=0.006, cage=0.03)
    bloom.stalk(m, rng, 3.25, strands=3, r_strand=0.13, twist=2.4, spread=0.16)
    E.sweep(m, [(0, 0, 0.0), (0, 0, 1.6), (0, 0, 3.2)], [0.16, 0.12, 0.1], "stem", sides=6)
    bloom.roots(m, rng, 5, 1.1)
    for j, a in enumerate((0.3, 1.9, 3.4, 4.9)):
        bloom.big_leaf(m, rng, a + rng.uniform(-0.2, 0.2), rng.uniform(1.3, 1.7), rng.uniform(0.26, 0.32),
                       base_u=rng.uniform(0.25, 0.6), mat="leaf_sage" if j % 2 else "leaf_teal")
    # Two thin glowing tendrils spiralling up the stalk.
    import math
    for j in range(2):
        pts = []
        for i in range(8):
            t = i / 7
            th = math.pi * j + t * 5.0
            rr = 0.25 * (1 - 0.3 * t)
            pts.append((rr * math.cos(th), rr * math.sin(th), 0.15 + t * 2.95))
        E.sweep(m, pts, [0.018] * 8, "glow_teal", sides=3)
    m.marker("cap", f=0.0, u=3.2)
    return m.finish(BUDGET, texture_size=1024)
