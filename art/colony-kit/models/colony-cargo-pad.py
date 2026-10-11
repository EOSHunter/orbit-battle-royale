"""Colony cargo pad: raised 8 x 8 m octagonal landing / loading pad. Concept: 31-colony-structure-kit.png.

Covers x -4..4, f -4..4 (2 x 2 grid modules), origin at the base center on the
ground. Deck surface at u = 1.0, the same height as the top of colony-ramp:
put a ramp's high end against any straight edge (ramp spans x -2..2 of that
edge). Edge lights sit outside the ramp lanes. Markings (landing ring, cross,
hazard edge) are baked.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (300, 1000)
H = 1.0


def build():
    m = Model("colony-cargo-pad", category="colony-kit", bevel=0.01, cage=0.02)
    m.top_prism(octagon(0, 0, 4.0, 4.0, 1.25), 0.0, 0.3, "concrete")
    m.top_prism(octagon(0, 0, 3.9, 3.9, 1.2), 0.3, H - 0.12, "graphite")
    m.top_prism(octagon(0, 0, 3.98, 3.98, 1.24), H - 0.12, H, "dark_steel")
    # Corner bollard blocks on the four diagonal faces.
    import math
    for sx in (-1, 1):
        for sf in (-1, 1):
            cx, cf = sx * 3.15, sf * 3.15
            b = blk(m, -0.45, 0.45, -0.32, 0.32, H, H + 0.55, "graphite", c=0.08, axis="u")
            o = blk(m, -0.42, 0.42, 0.32, 0.36, H + 0.08, H + 0.45, "rust_orange", c=0.0, axis="u")
            lt = blk(m, -0.25, 0.25, 0.36, 0.38, H + 0.3, H + 0.38, "glow_amber", axis="f")
            ang = math.degrees(math.atan2(sx, sf))
            for p in (b, o, lt):
                m.transform(p, rotate=(0, 0, ang), move=(cx, cf, 0))
    # Edge lights on the straight faces, outside the ramp lanes (|x| > 2).
    for s in (-1, 1):
        for a in (-2.6, 2.6):
            flight(m, a - 0.3, a + 0.3, 0.55, 0.65, 3.9 * s, s, depth=0.05)
            xlight(m, a - 0.3, a + 0.3, 0.55, 0.65, 3.9 * s, s, depth=0.05)
    # Baked markings and plating.
    uring(m, 0, 0, 2.3, 2.1, H - 0.003, H + 0.006, "white_paint", n=40, detail=True)
    uplate(m, -1.2, 1.2, -0.06, 0.06, H, "hazard", depth=0.006)
    uplate(m, -0.06, 0.06, -1.2, 1.2, H, "hazard", depth=0.006)
    for s in (-1, 1):
        uhazard(m, -2.6, 2.6, s * 3.75 - 0.12, s * 3.75 + 0.12, H, stripe=0.18)
        uplate(m, s * 3.75 - 0.05, s * 3.75 + 0.05, -2.6, 2.6, H, "lime", depth=0.005)
    for x in (-2.0, 0.0, 2.0):
        uplate(m, x - 0.006, x + 0.006, -3.6, 3.6, H, "polymer", depth=0.004)
        uplate(m, -3.6, 3.6, x - 0.006, x + 0.006, H, "polymer", depth=0.004)
    for x in (-3.0, -1.0, 1.0, 3.0):
        for f in (-3.0, -1.0, 1.0, 3.0):
            if abs(x) + abs(f) < 5.5:
                ubolt(m, x, f, H, r=0.03)
    for s in (-1, 1):
        fseams(m, [-2.0, 0.0, 2.0], 0.32, H - 0.14, 3.9 * s, s)
        fhazard(m, -1.9, 1.9, H - 0.11, H - 0.01, 3.98 * s, s, stripe=0.1, depth=0.006)
    m.marker("landing", f=0.0, u=H)
    return finish(m, BUDGET, texture_size=1024)
