"""Barrel. Concept: codex/concepts/v0.2/40-prop-kit.png (top right).

0.6 m diameter, 0.92 m tall drum, origin at the base center on the ground.
Ivory drum with burnt-orange rolling hoops, a graphite lid with bung caps and
an amber level-gauge strip.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (100, 800)
R, H = 0.29, 0.92


def build():
    m = Model("prop-barrel", category="props", bevel=0.004, cage=0.008)
    m.vcyl(0.0, 0.0, H, R, "ivory", sides=16)
    for u0, u1, mat in ((0.0, 0.05, "graphite"), (0.27, 0.31, "rust_orange"), (0.61, 0.65, "rust_orange"), (H - 0.05, H, "graphite")):
        m.vcyl(0.0, u0, u1, R + 0.012, mat, sides=16)
    m.vcyl(0.0, H, H + 0.01, R - 0.02, "graphite", sides=16)
    m.vcyl(0.14, H, H + 0.03, 0.035, "dark_steel", sides=6, x=0.1)
    m.vcyl(-0.12, H, H + 0.025, 0.025, "dark_steel", sides=6, x=-0.1)
    # Gauge strip on +f.
    blk(m, -0.045, 0.045, R - 0.02, R + 0.025, 0.36, 0.58, "graphite", c=0.012, axis="f")
    blk(m, -0.025, 0.025, R + 0.02, R + 0.03, 0.39, 0.55, "glow_amber", axis="f")
    # Baked: rust streak plates, weld seam, stencil, rolling ribs.
    for k in range(16):
        a = 2 * math.pi * (k + 0.5) / 16
        if k in (3, 4):
            p = fplate(m, -0.06, 0.06, 0.68, 0.84, R, 1, "lime", depth=0.004, c=0.0)
            m.transform(p, rotate=(0, 0, math.degrees(a) - 90.0))
    seam = fplate(m, -0.006, 0.006, 0.06, H - 0.06, R - 0.004, 1, "gunmetal", depth=0.006, c=0.0)
    m.transform(seam, rotate=(0, 0, 160))
    for u in (0.12, 0.8):
        m.vcyl(0.0, u - 0.008, u + 0.008, R + 0.004, "ivory", sides=16, detail=True)
    for u in (0.47,):
        m.vcyl(0.0, u - 0.01, u + 0.01, R + 0.004, "polymer", sides=16, detail=True)
    return finish(m, BUDGET, texture_size=512)
