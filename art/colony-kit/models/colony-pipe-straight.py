"""Colony pipe, straight: 4 m run on a support stand. Concept: 31-colony-structure-kit.png.

Pipe axis along x from -2 to 2 at u = 1.2 (radius 0.25, flanges at both ends),
origin on the ground under the pipe center. Runs snap end to end every 4 m;
colony-pipe-bend shares the same axis height and end flanges.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (150, 800)
U, R = 1.2, 0.25


def stand(m, x, f, along_x=True):
    """Concrete footing, steel column and saddle clamp under the pipe at (x, f)."""
    blk(m, x - 0.32, x + 0.32, f - 0.32, f + 0.32, 0.0, 0.35, "concrete", c=0.07, axis="u")
    blk(m, x - 0.12, x + 0.12, f - 0.12, f + 0.12, 0.35, U - R + 0.02, "graphite", c=0.04, axis="u")
    blk(m, x - 0.2, x + 0.2, f - 0.2, f + 0.2, 0.35, 0.45, "dark_steel", c=0.03, axis="u")
    if along_x:
        m.xcyl(f, U, x - 0.08, x + 0.08, R + 0.04, "dark_steel", sides=12)
        blk(m, x - 0.1, x + 0.1, f - R - 0.12, f + R + 0.12, U - R - 0.08, U - 0.05, "graphite", c=0.03, axis="x")
    else:
        m.cyl(f - 0.08, f + 0.08, U, R + 0.04, "dark_steel", sides=12, x=x)
        blk(m, x - R - 0.12, x + R + 0.12, f - 0.1, f + 0.1, U - R - 0.08, U - 0.05, "graphite", c=0.03, axis="f")
    for sx in (-1, 1):
        for sf in (-1, 1):
            ubolt(m, x + sx * 0.24, f + sf * 0.24, 0.35, r=0.025)
    for s in (-1, 1):
        fhazard(m, x - 0.3, x + 0.3, 0.12, 0.28, f + 0.32 * s, s, stripe=0.07)


def build():
    m = Model("colony-pipe-straight", category="colony-kit", bevel=0.008, cage=0.016)
    m.xcyl(0.0, U, -1.9, 1.9, R, "ivory", sides=12)
    for x in (-2.0, 1.9):
        m.xcyl(0.0, U, x, x + 0.1, R + 0.08, "graphite", sides=12)
    for x in (-1.2, 1.2):
        m.xcyl(0.0, U, x - 0.15, x + 0.15, R + 0.015, "rust_orange", sides=12)
    stand(m, 0.0, 0.0)
    # Valve with a handwheel on top.
    m.vcyl(0.0, U + R - 0.05, U + R + 0.18, 0.08, "gunmetal", sides=8, x=0.7)
    m.vcyl(0.0, U + R + 0.18, U + R + 0.36, 0.025, "steel", sides=6, x=0.7)
    w = m.tube(-0.03, 0.03, U + R + 0.36, 0.2, 0.16, "hazard", sides=10, x=0.7)
    m.transform(w, rotate=(90, 0, 0), pivot=(0.7, 0.0, U + R + 0.36))
    # Baked: flange bolts, weld seams, stencil.
    import math
    for x in (-1.95, 1.95):
        for k in range(8):
            a = 2 * math.pi * k / 8
            m.xcyl(0.0 + math.cos(a) * (R + 0.045), U + math.sin(a) * (R + 0.045), x - 0.07, x + 0.07, 0.018, "steel", sides=6, detail=True)
    for x in (-0.6, 0.3):
        m.xcyl(0.0, U, x - 0.012, x + 0.012, R + 0.006, "gunmetal", sides=12, detail=True)
    for s in (-1, 1):
        fplate(m, -0.9, -0.4, U - 0.06, U + 0.06, R * s, s, "lime", depth=0.006, c=0.0)
    return finish(m, BUDGET, texture_size=512)
