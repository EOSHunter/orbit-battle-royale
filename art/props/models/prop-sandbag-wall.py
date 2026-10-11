"""Sandbag wall: stacked sandbag cover. Concept: codex/concepts/v0.2/40-prop-kit.png (cover pieces).

2.0 m long along x, 0.4 m deep, about 0.9 m tall (crouch cover), origin at
the base center on the ground. Five staggered courses of canvas bags held by
a graphite stake frame with a hazard tag; chains end to end every 2 m.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (200, 800)


def bag(m, rnd, x, f, u, mat):
    o = m.sphere(f, u, 1.0, mat, x=x, segments=6, rings=4, scale=(0.27, 0.19, 0.1))
    for v in o.data.vertices:
        v.co.z = u + (v.co.z - u) * (0.8 if v.co.z < u else 1.0)
        v.co.x += rnd.uniform(-0.012, 0.012)
        v.co.z += rnd.uniform(-0.01, 0.01)
    m.transform(o, rotate=(0, 0, rnd.uniform(-4, 4)), pivot=(x, f, u))


def build():
    m = Model("prop-sandbag-wall", category="props", bevel=0.006, cage=0.012)
    rnd = random.Random(3)
    k = 0
    for i in range(5):
        u = 0.09 + i * 0.17
        xs = [-0.72, -0.24, 0.24, 0.72] if i % 2 == 0 else [-0.48, 0.0, 0.48]
        for x in xs:
            bag(m, rnd, x + rnd.uniform(-0.03, 0.03), rnd.uniform(-0.02, 0.02), u, "canvas" if k % 3 else "olive")
            k += 1
    # Stake frame at both ends.
    for sx in (-1, 1):
        for sf in (-1, 1):
            m.vcyl(sf * 0.3, 0.0, 0.95, 0.025, "graphite", sides=5, x=sx * 1.02)
        m.cyl(-0.32, 0.32, 0.82, 0.02, "dark_steel", sides=5, x=sx * 1.02)
    blk(m, -1.04, -0.98, 0.3, 0.32, 0.6, 0.78, "hazard")
    blk(m, -1.03, -0.99, 0.32, 0.34, 0.65, 0.73, "glow_amber")
    return finish(m, BUDGET, texture_size=512)
