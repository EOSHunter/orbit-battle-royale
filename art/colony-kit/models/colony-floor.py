"""Colony floor: 4 x 4 m deck tile. Concept: codex/concepts/v0.2/31-colony-structure-kit.png.

Covers x -2..2, f -2..2. The walking surface is at u = 0 (origin at the center of
the top surface); the 0.3 m slab and its edge beams hang below, so the tile
works on the ground (sunk 0.3 m) or as an upper storey placed at u = 4 on top
of colony walls. Walk surface is flat; plates, seams, tread and the lime
edge line are baked.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (100, 1000)


def build():
    m = Model("colony-floor", category="colony-kit", bevel=0.01, cage=0.02)
    # Slab: top deck plate over a chamfered edge frame and underside beams.
    blk(m, -2, 2, -2, 2, -0.08, 0.0, "graphite")
    m.top_prism(octagon(0, 0, 2.0, 2.0, 0.06), -0.3, -0.08, "dark_steel")
    for x in (-1.9, 0.0, 1.9):
        blk(m, x - 0.1, x + 0.1, -1.95, 1.95, -0.55, -0.3, "gunmetal", c=0.04, axis="f")
    for f in (-1.9, 1.9):
        blk(m, -1.8, 1.8, f - 0.08, f + 0.08, -0.5, -0.3, "gunmetal", c=0.03, axis="x")
    # Deck plates (baked): four 2 m plates with seams, bolts and tread.
    for x0 in (-1.94, 0.04):
        for f0 in (-1.94, 0.04):
            uplate(m, x0, x0 + 1.9, f0, f0 + 1.9, 0.0, "concrete", depth=0.006, c=0.04)
            for x in (x0 + 0.08, x0 + 0.95, x0 + 1.82):
                for f in (f0 + 0.08, f0 + 1.82):
                    ubolt(m, x, f, 0.006, r=0.022)
            for i in range(6):
                a = x0 + 0.25 + i * 0.25
                uplate(m, a, a + 0.12, f0 + 0.3, f0 + 1.6, 0.006, "graphite", depth=0.004)
    # Lime walkway edge line and corner hazard marks.
    for s in (-1, 1):
        uplate(m, -1.85, 1.85, s * 1.75 - 0.04, s * 1.75 + 0.04, 0.006, "lime", depth=0.005)
    for sx in (-1, 1):
        for sf in (-1, 1):
            uhazard(m, sx * 1.98 - (0.5 if sx > 0 else 0), sx * 1.98 + (0.5 if sx < 0 else 0), sf * 1.98 - (0.12 if sf > 0 else 0), sf * 1.98 + (0.12 if sf < 0 else 0), 0.006, stripe=0.06)
    # Side edges: seams and bolts on the slab rim.
    for s in (-1, 1):
        for x in (-1.5, -0.5, 0.5, 1.5):
            fbolt(m, x, -0.19, 2.0 * s, s, r=0.02)
            xbolt(m, x, -0.19, 2.0 * s, s, r=0.02)
    return finish(m, BUDGET, texture_size=1024)
