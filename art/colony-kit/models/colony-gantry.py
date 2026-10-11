"""Colony gantry: elevated walkway segment. Concept: 31-colony-structure-kit.png.

Deck 2 m wide (x -1..1) and 4 m long (f -2..2), walking surface at u = 4.0
(one storey, level with colony-floor tiles placed at u = 4). Origin on the
ground under the deck center. A braced H-frame leg pair stands at f = 0 so
every segment carries itself; chain segments every 4 m along f. Railings on
both sides, hanging cable runs, grating, hazard edges and lights are baked or
modeled. Connect colony-stairs to a deck end (stairs top lands at f = +-2).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (300, 1000)
U = 4.0


def build():
    m = Model("colony-gantry", category="colony-kit", bevel=0.01, cage=0.02)
    # Deck plate and edge beams.
    blk(m, -0.95, 0.95, -2, 2, U - 0.06, U, "dark_steel")
    for s in (-1, 1):
        blk(m, s * 0.92, s * 1.08, -2, 2, U - 0.38, U + 0.05, "graphite", c=0.04, axis="f")
    for f in (-1.95, 1.95):
        blk(m, -0.95, 0.95, f - 0.05, f + 0.05, U - 0.3, U - 0.06, "gunmetal")
    blk(m, -1.25, 1.25, -0.2, 0.2, U - 0.7, U - 0.06, "graphite", c=0.06, axis="x")
    # H-frame legs with bracing.
    for s in (-1, 1):
        x = s * 0.95
        blk(m, x - 0.35, x + 0.35, -0.35, 0.35, 0.0, 0.5, "concrete", c=0.08, axis="u")
        blk(m, x - 0.2, x + 0.2, -0.2, 0.2, 0.5, 0.62, "dark_steel", c=0.04, axis="u")
        blk(m, x - 0.15, x + 0.15, -0.15, 0.15, 0.62, U - 0.7, "graphite", c=0.05, axis="u")
        flight(m, x - 0.04, x + 0.04, 2.2, 2.9, 0.15, 1, depth=0.04)
        flight(m, x - 0.04, x + 0.04, 2.2, 2.9, -0.15, -1, depth=0.04)
        # Baked lattice look on the leg faces.
        for sf in (-1, 1):
            for u0 in (0.8, 1.7):
                fplate(m, x - 0.11, x + 0.11, u0, u0 + 0.8, 0.15 * sf, sf, "dark_steel", depth=0.004, c=0.0)
                m.front_prism([(x - 0.1, u0), (x - 0.06, u0), (x + 0.1, u0 + 0.75), (x + 0.06, u0 + 0.75)],
                              0.15 * sf - sf * 0.002, 0.15 * sf + sf * 0.012, "graphite", detail=True)
            xplate(m, -0.11, 0.11, 0.8, 3.2, x + s * 0.15, s, "dark_steel", depth=0.004, c=0.0)
            fhazard(m, x - 0.33, x + 0.33, 0.3, 0.46, 0.35 * sf, sf, stripe=0.08)
    m.limb((-0.82, 0.0, 0.8), (0.82, 0.0, U - 0.75), 0.045, 0.045, "gunmetal", sides=6)
    m.limb((0.82, 0.0, 0.8), (-0.82, 0.0, U - 0.75), 0.045, 0.045, "gunmetal", sides=6)
    blk(m, -0.8, 0.8, -0.1, 0.1, 0.75, 0.9, "graphite", c=0.03, axis="x")
    # Railings.
    for s in (-1, 1):
        x = s * 1.0
        for f in (-1.9, 0.0, 1.9):
            m.vcyl(f, U + 0.05, U + 1.1, 0.03, "graphite", sides=6, x=x)
        m.cyl(-2.0, 2.0, U + 1.06, 0.03, "hazard", sides=6, x=x)
        m.cyl(-2.0, 2.0, U + 0.58, 0.022, "hazard", sides=6, x=x)
    # Hanging cable runs under the outer beams.
    for s in (-1, 1):
        x = s * 1.12
        pts = [(x, -2.0, U - 0.3), (x, -1.0, U - 0.62), (x, 0.0, U - 0.72), (x, 1.0, U - 0.62), (x, 2.0, U - 0.3)]
        for a, b in zip(pts, pts[1:]):
            m.limb(a, b, 0.03, 0.03, "rubber", sides=5, caps=False)
    # Baked deck grating and edge markings.
    for i in range(40):
        f = -1.95 + i * 0.1
        uplate(m, -0.85, 0.85, f, f + 0.035, U, "gunmetal", depth=0.006)
    for s in (-1, 1):
        uplate(m, s * 0.86 - 0.04, s * 0.86 + 0.04, -1.98, 1.98, U, "hazard", depth=0.007)
        for f in (-1.5, -0.5, 0.5, 1.5):
            xbolt(m, f, U - 0.15, s * 1.08, s)
    return finish(m, BUDGET, texture_size=1024)
