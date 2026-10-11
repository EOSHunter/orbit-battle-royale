"""Generator: skid-mounted colony power unit. Concept: codex/concepts/v0.2/40-prop-kit.png (bottom center).

1.8 x 1.1 m footprint, 1.75 m tall, origin at the base center on the ground,
long side along x. Graphite skid, ivory engine housing with louvered vents,
a taller graphite control tower with amber light strips, exhaust stack,
fuel line and a burnt-orange service panel.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (150, 800)


def build():
    m = Model("prop-generator", category="props", bevel=0.006, cage=0.012)
    # Skid.
    blk(m, -0.95, 0.95, -0.58, 0.58, 0.0, 0.12, "dark_steel", c=0.03, axis="x")
    for sf in (-1, 1):
        blk(m, -0.98, 0.98, sf * 0.5, sf * 0.6, 0.0, 0.16, "graphite", c=0.03, axis="x")
    # Engine housing.
    blk(m, -0.85, 0.25, -0.48, 0.48, 0.12, 1.05, "ivory", c=0.07, axis="x")
    blk(m, -0.88, 0.28, -0.5, 0.5, 1.05, 1.12, "graphite", c=0.03, axis="x")
    # Control tower.
    blk(m, 0.28, 0.9, -0.45, 0.45, 0.12, 1.6, "graphite", c=0.06, axis="u")
    blk(m, 0.26, 0.92, -0.47, 0.47, 1.6, 1.68, "dark_steel", c=0.03, axis="u")
    blk(m, 0.4, 0.78, 0.45, 0.5, 0.5, 1.1, "rust_orange", c=0.03, axis="f")
    flight(m, 0.36, 0.42, 0.7, 1.4, 0.45, 1, depth=0.03)
    flight(m, 0.36, 0.42, 0.7, 1.4, -0.45, -1, depth=0.03)
    xlight(m, -0.2, 0.2, 1.45, 1.5, 0.9, 1, depth=0.03)
    # Exhaust stack and fuel line.
    m.vcyl(-0.25, 1.12, 1.75, 0.07, "gunmetal", sides=8, x=-0.6)
    m.vcyl(-0.25, 1.62, 1.68, 0.09, "dark_steel", sides=8, x=-0.6)
    m.limb((-0.98, 0.3, 0.3), (-1.05, 0.3, 0.6), 0.03, 0.03, "rubber", sides=6)
    m.limb((-1.05, 0.3, 0.6), (-0.86, 0.3, 0.85), 0.03, 0.03, "rubber", sides=6)
    m.xcyl(-0.25, 1.12, -0.3, -0.05, 0.12, "dark_steel", sides=8)
    # Baked: vents, seams, bolts, warnings.
    for sf in (-1, 1):
        face = sf * 0.48
        fvents(m, -0.75, -0.2, 0.3, 0.9, face, sf, 8)
        fplate(m, -0.1, 0.18, 0.3, 0.9, face, sf, "graphite", depth=0.005, c=0.02)
        fhazard(m, -0.8, 0.2, 0.15, 0.24, face, sf, stripe=0.06)
        fplate(m, -0.05, 0.12, 0.8, 0.86, face, sf, "lime", depth=0.007, c=0.0)
        for x in (-0.8, 0.2):
            for u in (0.2, 1.0):
                fbolt(m, x, u, face, sf, r=0.01)
        fseams(m, [0.59], 0.2, 1.55, sf * 0.45, sf)
    xvents(m, -0.3, 0.3, 0.4, 1.2, 0.9, 1, 7)
    xplate(m, -0.35, 0.35, 0.3, 0.9, -0.85, -1, "graphite", depth=0.005, c=0.02)
    uplate(m, -0.7, 0.1, -0.3, 0.3, 1.12, "dark_steel", depth=0.005, c=0.02)
    return finish(m, BUDGET, texture_size=512)
