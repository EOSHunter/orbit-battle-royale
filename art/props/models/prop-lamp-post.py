"""Lamp post: four-panel amber flood light mast. Concept: codex/concepts/v0.2/40-prop-kit.png (right).

4.6 m tall, origin at the base center on the ground. Concrete footing,
octagonal graphite pole with an ivory service box and burnt-orange collar,
a head with four glowing flood panels (two facing +f, two facing -f).
The "light" marker sits in front of the head for a game light.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (150, 800)


def build():
    m = Model("prop-lamp-post", category="props", bevel=0.006, cage=0.012)
    m.top_prism(octagon(0, 0, 0.32, 0.32, 0.09), 0.0, 0.32, "concrete")
    m.top_prism(octagon(0, 0, 0.2, 0.2, 0.06), 0.32, 0.4, "dark_steel")
    m.top_prism(octagon(0, 0, 0.09, 0.09, 0.03), 0.4, 4.1, "graphite")
    m.top_prism(octagon(0, 0, 0.11, 0.11, 0.035), 1.4, 1.6, "rust_orange")
    m.top_prism(octagon(0, 0, 0.11, 0.11, 0.035), 3.0, 3.08, "dark_steel")
    # Service box with a status light.
    blk(m, -0.12, 0.12, 0.09, 0.22, 0.75, 1.2, "ivory", c=0.025, axis="u")
    flight(m, -0.05, 0.05, 1.08, 1.12, 0.22, 1, depth=0.015)
    fvents(m, -0.08, 0.08, 0.8, 0.98, 0.22, 1, 4)
    # Head: yoke and four flood panels.
    blk(m, -0.5, 0.5, -0.07, 0.07, 4.05, 4.15, "dark_steel", c=0.02, axis="x")
    for x in (-0.28, 0.28):
        for u in (4.3, 4.68):
            blk(m, x - 0.22, x + 0.22, -0.12, 0.12, u - 0.16, u + 0.16, "graphite", c=0.035, axis="f")
            for s in (-1, 1):
                blk(m, x - 0.18, x + 0.18, s * 0.11, s * 0.135, u - 0.12, u + 0.12, "glow_amber", axis="f")
    blk(m, -0.06, 0.06, -0.06, 0.06, 4.15, 4.86, "graphite", c=0.015, axis="u")
    # Baked: bolts, seams, hazard band on the footing, lens grid.
    for s in (-1, 1):
        fhazard(m, -0.2, 0.2, 0.12, 0.26, s * 0.32, s, stripe=0.05)
        for u in (0.6, 2.2, 3.6):
            fbolt(m, 0.0, u, s * 0.09, s, r=0.008)
        for x in (-0.28, 0.28):
            for u in (4.3, 4.68):
                fplate(m, x - 0.002, x + 0.002, u - 0.12, u + 0.12, s * 0.135, s, "dark_steel", depth=0.004, c=0.0)
                fplate(m, x - 0.18, x + 0.18, u - 0.002, u + 0.002, s * 0.135, s, "dark_steel", depth=0.004, c=0.0)
    xplate(m, 0.0, 0.08, 1.7, 2.4, 0.09, 1, "lime", depth=0.004, c=0.0)
    m.marker("light", f=0.4, u=4.5)
    return finish(m, BUDGET, texture_size=512)
