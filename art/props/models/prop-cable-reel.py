"""Cable reel: industrial cable spool on a cradle. Concept: codex/concepts/v0.2/40-prop-kit.png, 31-colony-structure-kit.png.

1.1 m diameter flanges, 0.8 m wide (axis along x), origin at the base center
on the ground. Ivory flanges with burnt-orange rims, wound black cable, a
graphite cradle stand and a loose cable end trailing to the ground with a
connector plug.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (100, 800)
RF, U, W = 0.55, 0.62, 0.4


def build():
    m = Model("prop-cable-reel", category="props", bevel=0.005, cage=0.01)
    for sx in (-1, 1):
        x0 = sx * W
        m.xcyl(0.0, U, x0 - 0.03, x0 + 0.03, RF, "ivory", sides=16)
        m.xcyl(0.0, U, x0 + sx * 0.03, x0 + sx * 0.05, 0.12, "dark_steel", sides=8)
        # Cradle: A-frame per side.
        m.limb((x0 + sx * 0.08, -0.45, 0.0), (x0 + sx * 0.08, 0.0, U), 0.035, 0.035, "graphite", sides=6)
        m.limb((x0 + sx * 0.08, 0.45, 0.0), (x0 + sx * 0.08, 0.0, U), 0.035, 0.035, "graphite", sides=6)
        blk(m, x0 + sx * 0.03, x0 + sx * 0.13, -0.55, 0.55, 0.0, 0.06, "dark_steel", c=0.015, axis="f")
    m.xcyl(0.0, U, -W - 0.15, W + 0.15, 0.04, "steel", sides=6)
    m.xcyl(0.0, U, -W + 0.03, W - 0.03, 0.44, "rubber", sides=16)
    # Loose end trailing to a plug.
    pts = [(0.15, 0.0, U + 0.44), (0.2, 0.35, U + 0.25), (0.25, 0.6, 0.15), (0.3, 0.9, 0.04), (0.45, 1.2, 0.04)]
    for a, b in zip(pts, pts[1:]):
        m.limb(a, b, 0.03, 0.03, "rubber", sides=6, caps=False)
    blk(m, 0.4, 0.55, 1.2, 1.36, 0.0, 0.1, "rust_orange", c=0.02, axis="f")
    blk(m, 0.44, 0.51, 1.36, 1.38, 0.03, 0.07, "glow_amber", axis="f")
    # Baked: winding lines, flange ribs, bolts, stencil.
    for i in range(9):
        x = -W + 0.06 + i * 0.085
        m.xcyl(0.0, U, x, x + 0.04, 0.444, "polymer", sides=16, detail=True)
    for sx in (-1, 1):
        for k in range(6):
            a = 2 * math.pi * k / 6
            p = xplate(m, -0.02, 0.02, 0.14, RF - 0.05, sx * (W + 0.03), sx, "ivory", depth=0.008, c=0.0)
            m.transform(p, rotate=(math.degrees(a), 0, 0), pivot=(0, 0, 0), move=(0, 0, U))
            xbolt(m, math.cos(a) * 0.09, U + math.sin(a) * 0.09, sx * (W + 0.05), sx, r=0.012)
        m.xcyl(0.0, U, sx * (W + 0.03) - 0.012, sx * (W + 0.03) + 0.012, RF + 0.004, "rust_orange", sides=16, detail=True)
        xplate(m, -0.15, 0.15, U + 0.2, U + 0.3, sx * (W + 0.03), sx, "lime", depth=0.006, c=0.0)
    return finish(m, BUDGET, texture_size=512)
