"""Colony railing: 4 m safety railing segment. Concept: 31-colony-structure-kit.png.

Runs along x from -2 to 2, 1.1 m tall, origin at base center. Posts sit at
x = -1.95, 0, 1.95 so segments butt together on the 4 m grid along deck edges
(colony-floor, colony-gantry, colony-cargo-pad). Hazard-yellow tubes, a
graphite kick plate and an amber marker light on the center post.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (150, 800)


def build():
    m = Model("colony-railing", category="colony-kit", bevel=0.006, cage=0.012)
    for x in (-1.95, 0.0, 1.95):
        blk(m, x - 0.09, x + 0.09, -0.09, 0.09, 0.0, 0.03, "dark_steel", c=0.02, axis="u")
        blk(m, x - 0.035, x + 0.035, -0.035, 0.035, 0.03, 1.1, "graphite", c=0.012, axis="u")
        for u in (0.55, 1.04):
            blk(m, x - 0.05, x + 0.05, -0.05, 0.05, u - 0.035, u + 0.035, "gunmetal", c=0.012, axis="u")
        for sx in (-1, 1):
            ubolt(m, x + sx * 0.06, 0.0, 0.03, r=0.012)
    m.xcyl(0.0, 1.06, -2.0, 2.0, 0.03, "hazard", sides=8)
    m.xcyl(0.0, 0.57, -2.0, 2.0, 0.022, "hazard", sides=6)
    blk(m, -1.95, 1.95, -0.012, 0.012, 0.05, 0.22, "graphite", c=0.0)
    flight(m, -0.02, 0.02, 0.7, 0.92, 0.035, 1, depth=0.025)
    flight(m, -0.02, 0.02, 0.7, 0.92, -0.035, -1, depth=0.025)
    for s in (-1, 1):
        fhazard(m, -1.9, -0.06, 0.06, 0.21, 0.012 * s, s, stripe=0.1, depth=0.004)
        fhazard(m, 0.06, 1.9, 0.06, 0.21, 0.012 * s, s, stripe=0.1, depth=0.004)
    return finish(m, BUDGET, texture_size=512)
