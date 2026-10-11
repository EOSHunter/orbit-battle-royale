"""Jersey barrier. Concept: codex/concepts/v0.2/40-prop-kit.png (second row, left).

2.0 m long along x, 0.6 m wide at the base, 0.85 m tall (crouch cover),
origin at the base center on the ground; chains end to end every 2 m.
Ivory concrete-look body with burnt-orange warning bands, graphite end
frames with amber marker lights, forklift slots and a lifting eye.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (100, 800)


def jersey(grow=0.0):
    g = grow
    return [(-0.3 - g, 0.0), (0.3 + g, 0.0), (0.3 + g, 0.09 + g), (0.13 + g, 0.3 + g * 0.5), (0.09 + g, 0.85 + g),
            (-0.09 - g, 0.85 + g), (-0.13 - g, 0.3 + g * 0.5), (-0.3 - g, 0.09 + g)]


def build():
    m = Model("prop-barrier", category="props", bevel=0.006, cage=0.012)
    m.prism(jersey(), 1.76, "ivory")
    for sx in (-1, 1):
        x = sx * 0.94
        m.prism(jersey(0.02), 0.12, "graphite", x=x)
        for sf in (-1, 1):
            flight(m, x - 0.03, x + 0.03, 0.5, 0.7, sf * 0.13, sf, depth=0.03)
    m.xcyl(0.0, 0.9, -0.06, 0.06, 0.035, "steel", sides=6)
    blk(m, -0.1, 0.1, -0.06, 0.06, 0.84, 0.88, "dark_steel", c=0.01, axis="x")
    # Baked: orange bands on the sloped faces, forklift slots, stencil.
    for xb in (-0.45, 0.1):
        m.prism(jersey(0.004), 0.22, "rust_orange", x=xb, detail=True)
    for sf in (-1, 1):
        for x0 in (-0.75, 0.45):
            fplate(m, x0, x0 + 0.28, 0.015, 0.075, sf * 0.3, sf, "polymer", depth=0.004, c=0.0)
        fplate(m, 0.45, 0.75, 0.5, 0.58, sf * 0.115, sf, "lime", depth=0.012, c=0.0)
        fplate(m, -0.8, -0.6, 0.5, 0.58, sf * 0.115, sf, "white_paint", depth=0.012, c=0.0)
    return finish(m, BUDGET, texture_size=512)
