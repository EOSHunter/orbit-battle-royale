"""Large supply crate. Concept: codex/concepts/v0.2/40-prop-kit.png (top left).

1.4 x 0.9 x 0.86 m cargo case (waist-high cover), origin at the base center on
the ground, long side along x. Ivory upper shell over a graphite base band,
burnt-orange corner guards and straps, side handles, recessed latches and an
amber light strip on both long faces.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (150, 800)
X, F, H = 0.7, 0.45, 0.86


def build():
    m = Model("prop-crate-large", category="props", bevel=0.005, cage=0.01)
    blk(m, -X, X, -F, F, 0.04, 0.36, "graphite", c=0.05, axis="x")
    blk(m, -X + 0.01, X - 0.01, -F + 0.01, F - 0.01, 0.36, H - 0.04, "ivory", c=0.06, axis="x")
    blk(m, -X + 0.05, X - 0.05, -F + 0.05, F - 0.05, H - 0.05, H, "graphite", c=0.03, axis="x")
    blk(m, -X + 0.06, X - 0.06, -F + 0.06, F - 0.06, 0.0, 0.05, "rubber")
    for sx in (-1, 1):
        for sf in (-1, 1):
            blk(m, sx * (X + 0.015), sx * (X - 0.1), sf * (F + 0.015), sf * (F - 0.1), 0.0, H + 0.01, "rust_orange", c=0.02, axis="u")
        blk(m, sx * 0.36 - 0.04, sx * 0.36 + 0.04, -F - 0.012, F + 0.012, 0.03, H + 0.012, "rust_orange")
        # End handles.
        blk(m, sx * X, sx * (X + 0.06), -0.16, 0.16, 0.52, 0.56, "dark_steel", c=0.01, axis="x")
        for f in (-0.14, 0.14):
            blk(m, sx * X, sx * (X + 0.06), f - 0.015, f + 0.015, 0.5, 0.58, "dark_steel")
    for sf in (-1, 1):
        face = sf * (F - 0.01)
        flight(m, -0.2, 0.2, 0.62, 0.66, face, sf, depth=0.015)
        for x in (-0.14, 0.14):
            blk(m, x - 0.04, x + 0.04, face, face + sf * 0.025, 0.3, 0.44, "gunmetal", c=0.01, axis="f")
        # Baked: panel seams, bolts, vents, stencils.
        fplate(m, -0.28, 0.28, 0.08, 0.3, sf * F, sf, "dark_steel", depth=0.004, c=0.015)
        fvents(m, 0.42, 0.6, 0.1, 0.28, sf * F, sf, 4)
        fplate(m, -0.6, -0.44, 0.45, 0.75, face, sf, "graphite", depth=0.004, c=0.015)
        fplate(m, 0.44, 0.62, 0.68, 0.76, face, sf, "lime", depth=0.004, c=0.0)
        for x in (-0.55, 0.55):
            for u in (0.42, 0.78):
                fbolt(m, x, u, face, sf, r=0.008)
    uplate(m, -0.26, 0.26, -0.3, 0.3, H, "ivory", depth=0.004, c=0.02)
    uplate(m, -0.5, -0.42, -0.3, 0.3, H, "lime", depth=0.004)
    for x in (-0.55, 0.55):
        for f in (-0.32, 0.32):
            ubolt(m, x, f, H, r=0.01)
    return finish(m, BUDGET, texture_size=512)
