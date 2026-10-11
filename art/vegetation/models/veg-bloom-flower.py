"""Bloom flower: a young Bloomwild flower in one piece, violet variant.
Concept: codex/concepts/v0.2/30-luminous-vegetation.png (violet bulb with pink
core) and 36-bloomwild.png.

About 2.3 m tall and 1.8 m across the leaves. Braided stalk, three cupped
leaves, a bulb of six violet petals with glowing pink rims around a glowing
core and a crown of cyan-tipped stamens. Origin at the base center.
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
    rng = random.Random(47)
    m = E.Model("veg-bloom-flower", category="vegetation", bevel=0.004, cage=0.02)
    top = 1.45
    bloom.stalk(m, rng, top + 0.05, strands=2, r_strand=0.06, twist=3.0, spread=0.07, sides=5, n=6)
    bloom.roots(m, rng, 3, 0.5, r=0.045)
    for j, a in enumerate((0.4, 2.5, 4.4)):
        bloom.big_leaf(m, rng, a, rng.uniform(0.75, 0.95), 0.17, base_u=0.12, mat="leaf_violet", vein="glow_cyan", n=6, droop=0.6)
    bloom.petal_bulb(m, rng, center_u=top + 0.42, base_u=top, radius=0.45, height=0.85, petals=6,
                     petal_mat="cap_violet", glow="glow_pink", n=6, gap=0.85)
    bloom.stamens(m, rng, 5, top + 0.8, 0.25, 0.35, stem="cap_violet", tip="glow_cyan")
    return m.finish(BUDGET, texture_size=1024)
