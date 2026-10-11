"""Colony wall: solid 4 m wall module. Concept: codex/concepts/v0.2/31-colony-structure-kit.png.

Grid: 4 m wide (x -2..2), 4 m tall (u 0..4), 0.3 m core (f -0.15..0.15) with
cladding to +-0.25. Origin at base center on the floor top. Snaps edge to edge
along x; colony-corner columns cover the joints at x = +-2. Both faces dressed.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (300, 1000)


def build():
    m = Model("colony-wall", category="colony-kit", bevel=0.01, cage=0.02)
    wall_core(m)
    # Center pilaster with a work light on each side.
    blk(m, -0.13, 0.13, -0.25, 0.25, 0.4, 3.62, "graphite", c=0.05, axis="u")
    for s in (-1, 1):
        flight(m, -0.05, 0.05, 2.75, 3.3, 0.25 * s, s)
        fseams_h(m, [1.2, 2.4], -0.12, 0.12, 0.25 * s, s)
        # Left: tall ivory panel. Right: ivory over burnt orange.
        face = panel(m, -1.78, -0.17, 0.5, 3.55, s, "ivory", seams=[-0.98])
        fplate(m, -1.62, -1.12, 2.9, 3.2, face, s, "lime", depth=0.006, c=0.0)         # unit marking
        fplate(m, -1.62, -1.32, 2.78, 2.84, face, s, "lime", depth=0.006, c=0.0)
        fplate(m, -0.85, -0.3, 0.75, 1.25, face, s, "graphite", depth=0.01, c=0.03)    # access hatch
        face = panel(m, 0.17, 1.78, 1.55, 3.55, s, "ivory", seams=[0.98])
        fseams_h(m, [2.55], 0.2, 1.75, face, s)
        face = panel(m, 0.17, 1.78, 0.5, 1.45, s, "rust_orange")
        fvents(m, 0.35, 1.0, 0.7, 1.25, face, s, 5)
        fplate(m, 1.2, 1.6, 0.75, 1.2, face, s, "graphite", depth=0.01, c=0.03)
    # Conduit with brackets on the front face only (rotate the module to swap).
    m.xcyl(0.31, 3.42, -1.95, 1.95, 0.05, "dark_steel", sides=8)
    for x in (-1.5, 1.5):
        blk(m, x - 0.06, x + 0.06, 0.25, 0.37, 3.34, 3.5, "gunmetal", c=0.02, axis="x")
    # Junction box on the back face.
    blk(m, 0.45, 0.95, -0.2, -0.36, 2.0, 2.6, "graphite", c=0.04, axis="f")
    fvents(m, 0.52, 0.88, 2.1, 2.4, -0.36, -1, 3)
    return finish(m, BUDGET, texture_size=1024)
