"""Colony roof: 4 x 4 m roof tile with an edge trim parapet. Concept: 31-colony-structure-kit.png.

Covers x -2..2, f -2..2; origin at the center of the slab underside, so it sits
on colony walls at u = 4. The raised parapet trim runs along the front edge
(f = +1.85..+2.3, overhanging the wall cladding); rotate the tile in 90 degree
steps to trim other edges, and use two tiles at a corner. Interior roof tiles
can be any rotation (the trim then faces the open edge). Carries a vent unit,
a conduit and a lamp on the parapet.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (200, 1000)


def build():
    m = Model("colony-roof", category="colony-kit", bevel=0.01, cage=0.02)
    # Slab, with raised roof plates leaving drainage gutters between them.
    blk(m, -2, 2, -2, 2, 0.0, 0.28, "graphite")
    for x0, x1 in ((-1.95, -0.05), (0.05, 1.95)):
        blk(m, x0, x1, -1.95, 1.75, 0.28, 0.36, "ivory", c=0.05, axis="x")
    # Parapet trim on the front edge, chamfered outward, with a cap rail.
    m.prism([(1.75, 0.0), (2.3, 0.0), (2.3, 0.62), (2.18, 0.78), (1.75, 0.78), (1.75, 0.0)][:5], 4.0, "graphite")
    blk(m, -2, 2, 2.2, 2.34, -0.25, 0.1, "graphite", c=0.04, axis="x")               # fascia lip over the wall top
    blk(m, -2, 2, 1.74, 1.86, 0.36, 0.86, "rust_orange", c=0.03, axis="x")
    for x in (-1.0, 1.0):
        blk(m, x - 0.1, x + 0.1, 1.68, 2.36, 0.0, 0.84, "dark_steel", c=0.03, axis="f")
    flight(m, -0.3, 0.3, 0.4, 0.5, 2.3, 1)
    for x in (-1.8, -1.3, -0.6, 0.6, 1.3, 1.8):
        fbolt(m, x, 0.68, 2.3, 1, r=0.02)
    fhazard(m, -1.95, -1.15, 0.1, 0.3, 2.3, 1, stripe=0.1)
    fhazard(m, 1.15, 1.95, 0.1, 0.3, 2.3, 1, stripe=0.1)
    # Rooftop vent unit and conduit.
    blk(m, -1.4, -0.4, -1.3, -0.4, 0.36, 0.95, "graphite", c=0.06, axis="u")
    blk(m, -1.45, -0.35, -1.35, -0.35, 0.95, 1.05, "dark_steel", c=0.03, axis="u")
    fvents(m, -1.3, -0.5, 0.45, 0.85, -0.4, 1, 4)
    xvents(m, -1.2, -0.5, 0.45, 0.85, -0.4, 1, 4)
    m.vcyl(-0.85, 1.05, 1.3, 0.12, "gunmetal", sides=8, x=-0.9)
    m.vcyl(-0.85, 1.3, 1.36, 0.16, "dark_steel", sides=8, x=-0.9)
    m.cyl(-1.9, 1.6, 0.46, 0.06, "dark_steel", sides=8, x=1.2)
    for f in (-1.2, 0.6):
        blk(m, 1.1, 1.3, f - 0.05, f + 0.05, 0.36, 0.5, "gunmetal", c=0.02, axis="f")
    # Baked: plate seams, bolts, hazard gutters, lime stencil.
    for x0, x1 in ((-1.95, -0.05), (0.05, 1.95)):
        for f in (-1.0, 0.0, 1.0):
            uplate(m, x0 + 0.05, x1 - 0.05, f - 0.006, f + 0.006, 0.36, "polymer", depth=0.004)
        for x in (x0 + 0.08, x1 - 0.08):
            for f in (-1.88, -0.5, 0.5, 1.68):
                ubolt(m, x, f, 0.36, r=0.022)
    uplate(m, 0.3, 0.9, -1.6, -1.45, 0.36, "lime", depth=0.004)
    uplate(m, 0.3, 0.6, -1.4, -1.33, 0.36, "lime", depth=0.004)
    return finish(m, BUDGET, texture_size=1024)
