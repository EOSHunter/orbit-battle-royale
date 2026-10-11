"""Colony corner column. Concept: codex/concepts/v0.2/31-colony-structure-kit.png.

Octagonal 0.64 m column, 4.1 m tall, origin at its base center. Place it on the
4 m grid corners (where wall modules meet at x = +-2): it covers wall joints
for straight runs, L corners and T junctions. Amber light strips on all four
faces, a concrete footing and a capital.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (150, 1000)


def build():
    m = Model("colony-corner", category="colony-kit", bevel=0.01, cage=0.02)
    m.top_prism(octagon(0, 0, 0.42, 0.42, 0.12), 0.0, 0.5, "concrete")
    m.top_prism(octagon(0, 0, 0.36, 0.36, 0.1), 0.5, 0.62, "dark_steel")
    m.top_prism(octagon(0, 0, 0.32, 0.32, 0.11), 0.62, 3.6, "graphite")
    m.top_prism(octagon(0, 0, 0.36, 0.36, 0.1), 3.6, 3.75, "dark_steel")
    m.top_prism(octagon(0, 0, 0.4, 0.4, 0.12), 3.75, 4.1, "graphite")
    # Orange band and light strips on each face.
    m.top_prism(octagon(0, 0, 0.335, 0.335, 0.115), 1.2, 1.7, "rust_orange")
    for s in (-1, 1):
        flight(m, -0.05, 0.05, 2.1, 3.2, 0.32 * s, s, depth=0.05)
        xlight(m, -0.05, 0.05, 2.1, 3.2, 0.32 * s, s, depth=0.05)
        # Baked: bolts and seams on each face, hazard band on the footing.
        for u in (0.75, 1.9, 3.4):
            for x in (-0.15, 0.15):
                fbolt(m, x, u, 0.32 * s, s, r=0.02)
                xbolt(m, x, u, 0.32 * s, s, r=0.02)
        fhazard(m, -0.28, 0.28, 0.32, 0.46, 0.42 * s, s, stripe=0.07)
        fseams_h(m, [3.95], -0.25, 0.25, 0.4 * s, s)
        xplate(m, -0.2, 0.2, 0.08, 0.4, 0.42 * s, s, "concrete", depth=0.008, c=0.02)
    return finish(m, BUDGET, texture_size=512)
