"""Debris pile: rubble heap with a bent girder and a broken pipe. Concept: codex/concepts/v0.2/40-prop-kit.png (bottom left).

About 3.2 x 2.4 m, up to 1.1 m tall (low cover), origin at the pile center on
the ground. Broken concrete chunks (seeded, so rebuilds are identical), a
rusted I-beam leaning across, a cracked ivory pipe section and a torn
burnt-orange panel.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (200, 800)


def chunk(m, rnd, x, f, size, mat="concrete"):
    sx = size * rnd.uniform(0.4, 0.62)
    sf = size * rnd.uniform(0.35, 0.55)
    su = size * rnd.uniform(0.35, 0.6)
    o = m.sphere(f, su * 0.55, 1.0, mat, x=x, segments=6, rings=4, scale=(sx, sf, su))
    for v in o.data.vertices:
        v.co.x += rnd.uniform(-0.18, 0.18) * size
        v.co.y += rnd.uniform(-0.18, 0.18) * size
        v.co.z = max(0.0, v.co.z + rnd.uniform(-0.12, 0.12) * size)
    m.transform(o, rotate=(0, 0, rnd.uniform(0, 360)), pivot=(x, f, 0))
    return o


def build():
    m = Model("prop-debris-pile", category="props", bevel=0.008, cage=0.016)
    rnd = random.Random(7)
    big = [(-0.6, 0.1, 1.1), (0.4, -0.2, 0.95), (0.1, 0.55, 0.8), (-1.2, -0.5, 0.7), (1.1, 0.5, 0.65)]
    for x, f, s in big:
        chunk(m, rnd, x, f, s)
    for _ in range(8):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.8, 1.5)
        chunk(m, rnd, math.cos(a) * r * 1.1, math.sin(a) * r * 0.8, rnd.uniform(0.18, 0.38), rnd.choice(["concrete", "concrete", "basalt"]))
    # Rusted I-beam leaning on the heap.
    prof = [(-0.1, -0.12), (0.1, -0.12), (0.1, -0.09), (0.02, -0.09), (0.02, 0.09), (0.1, 0.09), (0.1, 0.12),
            (-0.1, 0.12), (-0.1, 0.09), (-0.02, 0.09), (-0.02, -0.09), (-0.1, -0.09)]
    beam = m.front_prism(prof, -1.3, 1.4, "rust_metal")
    m.transform(beam, rotate=(-14, 0, 28), pivot=(0, 0, 0), move=(-0.1, 0.0, 0.62))
    # Cracked pipe section.
    pipe = m.tube(-0.45, 0.45, 0.0, 0.26, 0.21, "ivory", sides=10)
    m.transform(pipe, rotate=(0, 8, 65), pivot=(0, 0, 0), move=(1.25, -0.55, 0.25))
    band = m.tube(-0.08, 0.08, 0.0, 0.275, 0.2, "rust_orange", sides=10)
    m.transform(band, rotate=(0, 8, 65), pivot=(0, 0, 0), move=(1.25, -0.55, 0.25))
    # Torn panel slab.
    sheet = m.top_prism([(-0.5, -0.35), (0.45, -0.4), (0.55, 0.1), (0.2, 0.42), (-0.4, 0.3)], 0.0, 0.03, "rust_orange")
    m.transform(sheet, rotate=(18, -10, 30), pivot=(0, 0, 0), move=(-1.05, 0.75, 0.25))
    # Rebar stubs poking out of the heap.
    for _ in range(8):
        x, f = rnd.uniform(-1.0, 0.8), rnd.uniform(-0.4, 0.6)
        a = (x, f, rnd.uniform(0.4, 0.7))
        b = (x + rnd.uniform(-0.3, 0.3), f + rnd.uniform(-0.3, 0.3), a[2] + rnd.uniform(0.2, 0.4))
        m.limb(a, b, 0.012, 0.012, "rust_metal", sides=4)
    return finish(m, BUDGET, texture_size=1024)
