"""Colony warehouse door: 8 m wide roll-up door wall module. Concept: 31-colony-structure-kit.png (top right).

Two grid modules wide (x -4..4), 4 m tall like colony-wall (core on f = 0,
origin at base center on the floor top); colony-corner columns go at x = +-4.
Opening 6.4 m x 3.3 m (x -3.2..3.2). The ribbed shutter is rolled two-thirds
of the way up (bottom edge at 2.3 m), so players and vehicles pass under it;
it reads as a big loading bay with a roll housing, guide rails, hazard posts
and amber bay lights.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (300, 1000)
OX, OH, SB = 3.2, 3.3, 2.3


def build():
    m = Model("colony-warehouse-door", category="colony-kit", bevel=0.01, cage=0.02)
    # Side wall stubs, posts, header and roll housing.
    for s in (-1, 1):
        blk(m, s * 4.0, s * (OX + 0.4), -0.15, 0.15, 0.0, 4.0, "graphite")
        blk(m, s * 4.0, s * (OX + 0.4), -0.26, 0.26, 0.0, 0.4, "concrete", c=0.07, axis="x")
        blk(m, s * (OX + 0.45), s * OX, -0.36, 0.36, 0.0, OH + 0.1, "graphite", c=0.08, axis="u")
        blk(m, s * OX, s * (OX - 0.06), -0.12, 0.12, 0.0, OH, "dark_steel")           # guide rail
        for sf in (-1, 1):
            f0 = 0.36 * sf
            fhazard(m, s * (OX + 0.43) if s < 0 else OX + 0.02, s * (OX + 0.02) if s < 0 else OX + 0.43, 0.05, 1.3, f0, sf, stripe=0.1)
            flight(m, s * (OX + 0.22) - 0.04, s * (OX + 0.22) + 0.04, 1.6, 2.9, f0, sf, depth=0.05)
            panel(m, min(s * 3.97, s * (OX + 0.48)), max(s * 3.97, s * (OX + 0.48)), 0.5, 3.55, sf, "ivory" if s < 0 else "rust_orange", bolts=False)
            for u in (0.7, 1.9, 3.1):
                fbolt(m, s * (OX + 0.22), u, f0, sf, r=0.022)
    blk(m, -4.0, 4.0, -0.25, 0.25, OH, 4.0, "graphite", c=0.07, axis="x")
    m.prism([(-0.62, OH + 0.05), (-0.25, OH + 0.05), (-0.25, 3.95), (-0.5, 3.95), (-0.62, 3.8)], 2 * OX + 0.6, "dark_steel")
    m.prism([(0.25, OH + 0.05), (0.5, OH + 0.05), (0.5, 3.95), (0.25, 3.95)], 2 * OX + 0.6, "graphite")
    # Shutter: slab with a bottom bar; ribs baked.
    blk(m, -OX + 0.03, OX - 0.03, -0.06, 0.06, SB, OH + 0.05, "ivory")
    blk(m, -OX + 0.03, OX - 0.03, -0.09, 0.09, SB - 0.06, SB + 0.06, "graphite", c=0.03, axis="x")
    for sf in (-1, 1):
        f0 = 0.06 * sf
        k = 0
        u = SB + 0.12
        while u < OH - 0.05:
            fplate(m, -OX + 0.05, OX - 0.05, u, u + 0.05, f0, sf, "white_paint" if k % 2 else "ivory", depth=0.01, c=0.0)
            u += 0.12
            k += 1
        fhazard(m, -OX + 0.05, OX - 0.05, SB - 0.05, SB + 0.05, 0.09 * sf, sf, stripe=0.12, depth=0.006)
    # Bay signage and lights on the housing.
    for sf in (-1, 1):
        f0 = 0.62 * sf if sf < 0 else 0.5
        flight(m, -2.2, -1.2, 3.55, 3.63, f0, sf, depth=0.04)
        flight(m, 1.2, 2.2, 3.55, 3.63, f0, sf, depth=0.04)
        fplate(m, -0.7, 0.7, 3.45, 3.78, f0, sf, "graphite", depth=0.006, c=0.02)
        fplate(m, -0.6, 0.0, 3.53, 3.7, f0, sf, "lime", depth=0.01, c=0.0)
        fplate(m, 0.1, 0.6, 3.53, 3.7, f0, sf, "white_paint", depth=0.01, c=0.0)
    # Floor threshold.
    blk(m, -OX, OX, -0.4, 0.4, 0.0, 0.03, "dark_steel")
    uhazard(m, -OX, OX, -0.38, -0.26, 0.03, stripe=0.15)
    uhazard(m, -OX, OX, 0.26, 0.38, 0.03, stripe=0.15)
    m.marker("bay", f=0.0, u=0.0)
    return finish(m, BUDGET, texture_size=1024)
