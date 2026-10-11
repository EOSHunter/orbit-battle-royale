"""Security fence panel. Concept: codex/concepts/v0.2/40-prop-kit.png (top center).

4 m long along x (posts at x = +-1.95, panels butt end to end on the 4 m grid),
2.2 m tall, origin at the base center on the ground. Graphite posts on splayed
feet with burnt-orange ballast blocks, a solid lower kick panel and an open
wire-mesh upper panel built from real thin bars (see-through without alpha),
plus amber post lights.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (200, 800)
HX = 1.95


def build():
    m = Model("prop-fence", category="props", bevel=0.005, cage=0.01)
    for sx in (-1, 1):
        x = sx * HX
        blk(m, x - 0.06, x + 0.06, -0.06, 0.06, 0.0, 2.2, "graphite", c=0.02, axis="u")
        blk(m, x - 0.08, x + 0.08, -0.08, 0.08, 2.2, 2.26, "dark_steel", c=0.015, axis="u")
        blk(m, x - 0.18, x + 0.18, -0.42, 0.42, 0.0, 0.08, "dark_steel", c=0.02, axis="x")
        for sf in (-1, 1):
            m.limb((x, sf * 0.38, 0.06), (x, sf * 0.05, 0.75), 0.022, 0.022, "gunmetal", sides=4)
            blk(m, x - 0.15, x + 0.15, sf * 0.22, sf * 0.42, 0.08, 0.26, "rust_orange", c=0.03, axis="x")
            flight(m, x - 0.02, x + 0.02, 1.2, 1.7, sf * 0.06, sf, depth=0.02)
    # Lower solid panel.
    blk(m, -HX + 0.06, HX - 0.06, -0.025, 0.025, 0.1, 0.9, "graphite")
    blk(m, -HX + 0.06, HX - 0.06, -0.04, 0.04, 0.88, 0.95, "dark_steel")
    # Mesh frame and bars.
    m.xcyl(0.0, 2.1, -HX, HX, 0.025, "dark_steel", sides=6)
    x = -HX + 0.2
    while x < HX - 0.1:
        blk(m, x - 0.007, x + 0.007, -0.007, 0.007, 0.95, 2.1, "gunmetal")
        x += 0.24
    for u in (1.2, 1.45, 1.7, 1.95):
        blk(m, -HX + 0.06, HX - 0.06, -0.006, 0.006, u - 0.007, u + 0.007, "gunmetal")
    # Baked: panel ribs, hazard band, stencil, bolts.
    for sf in (-1, 1):
        face = sf * 0.025
        for xs in (-1.3, -0.65, 0.0, 0.65, 1.3):
            fplate(m, xs - 0.015, xs + 0.015, 0.14, 0.86, face, sf, "dark_steel", depth=0.008, c=0.0)
        fhazard(m, -1.85, -1.4, 0.14, 0.4, face, sf, stripe=0.07)
        fhazard(m, 1.4, 1.85, 0.14, 0.4, face, sf, stripe=0.07)
        fplate(m, -0.4, 0.3, 0.55, 0.7, face, sf, "lime", depth=0.004, c=0.0)
        for xb in (-HX, HX):
            for u in (0.3, 0.8, 1.4, 2.0):
                fbolt(m, xb, u, sf * 0.06, sf, r=0.01)
    return finish(m, BUDGET, texture_size=1024)
