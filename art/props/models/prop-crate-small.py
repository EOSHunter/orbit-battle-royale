"""Small supply crate. Concept: codex/concepts/v0.2/40-prop-kit.png (top row).

0.62 x 0.44 x 0.44 m hard case, origin at the base center on the ground, long
side along x. Graphite shell, ivory lid, burnt-orange corner guards and
straps, a carry handle and an amber status strip on the +f face.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (100, 800)
X, F, H = 0.31, 0.22, 0.44


def build():
    m = Model("prop-crate-small", category="props", bevel=0.004, cage=0.008)
    blk(m, -X, X, -F, F, 0.02, H - 0.1, "graphite", c=0.035, axis="x")
    blk(m, -X + 0.005, X - 0.005, -F + 0.005, F - 0.005, H - 0.11, H, "ivory", c=0.03, axis="x")
    blk(m, -X + 0.03, X - 0.03, -F + 0.03, F - 0.03, 0.0, 0.03, "rubber")
    for sx in (-1, 1):
        for sf in (-1, 1):
            blk(m, sx * (X + 0.01), sx * (X - 0.06), sf * (F + 0.01), sf * (F - 0.06), 0.0, H + 0.005, "rust_orange", c=0.012, axis="u")
        blk(m, sx * 0.16 - 0.025, sx * 0.16 + 0.025, -F - 0.008, F + 0.008, 0.02, H + 0.008, "rust_orange")
    # Handle and latches.
    for x in (-0.09, 0.09):
        blk(m, x - 0.015, x + 0.015, -0.015, 0.015, H, H + 0.045, "dark_steel")
    blk(m, -0.11, 0.11, -0.018, 0.018, H + 0.035, H + 0.06, "rubber", c=0.008, axis="x")
    for sf in (-1, 1):
        for x in (-0.06, 0.06):
            blk(m, x - 0.025, x + 0.025, sf * F, sf * (F + 0.018), H - 0.16, H - 0.08, "gunmetal", c=0.006, axis="f")
    flight(m, -0.06, 0.06, 0.15, 0.18, F, 1, depth=0.012)
    # Baked: panel insets, bolts, vents, stencils.
    for sf in (-1, 1):
        fplate(m, -0.12, 0.12, 0.06, 0.26, sf * F, sf, "graphite", depth=0.004, c=0.01)
        if sf < 0:
            fvents(m, -0.1, 0.1, 0.2, 0.27, sf * F, sf, 3)
        else:
            fplate(m, -0.1, 0.1, 0.22, 0.25, sf * F, sf, "lime", depth=0.004, c=0.0)
        for x in (-0.26, 0.26):
            for u in (0.06, H - 0.14):
                fbolt(m, x, u, sf * F, sf, r=0.006)
    for sx in (-1, 1):
        xplate(m, -0.12, 0.12, 0.08, 0.26, sx * X, sx, "graphite", depth=0.004, c=0.01)
    uplate(m, -0.26, -0.18, -0.15, 0.15, H, "lime", depth=0.003)
    return finish(m, BUDGET, texture_size=512)
