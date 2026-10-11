"""Colony comms mast: 14 m relay tower. Concept: 31-colony-structure-kit.png (center), 37-relay-nine.png.

One piece. Origin at the base center on the ground; footprint is a 3 x 3 m
concrete pad (fits a 4 m grid cell). Octagonal core column wrapped by a
four-post lattice, clamped equipment pods, amber work lights, a dish and an
antenna crown with a beacon at the top.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (400, 1000)
P = 0.45   # lattice half width


def build():
    m = Model("colony-comms-mast", category="colony-kit", bevel=0.01, cage=0.02)
    # Pad, plinth and two equipment cabinets.
    m.top_prism(octagon(0, 0, 1.5, 1.5, 0.35), 0.0, 0.3, "concrete")
    m.top_prism(octagon(0, 0, 0.75, 0.75, 0.2), 0.3, 0.9, "graphite")
    blk(m, 0.75, 1.4, -1.3, -0.3, 0.3, 1.5, "ivory", c=0.06, axis="u")
    blk(m, 0.72, 1.43, -1.33, -0.27, 1.5, 1.6, "dark_steel", c=0.03, axis="u")
    blk(m, -1.4, -0.75, 0.2, 1.1, 0.3, 1.1, "rust_orange", c=0.06, axis="u")
    xvents(m, -1.2, -0.4, 0.5, 1.3, 1.4, 1, 6)
    xlight(m, -1.15, -1.0, 1.32, 1.42, 1.4, 1, depth=0.04)
    fvents(m, -1.3, -0.85, 0.45, 0.95, 1.1, 1, 4)
    flight(m, -1.25, -0.9, 1.0, 1.05, 1.1, 1, depth=0.04)
    m.limb((1.05, -0.3, 0.6), (0.4, 0.0, 0.6), 0.05, 0.05, "rubber", sides=5, caps=False)
    # Core column and lattice posts.
    m.top_prism(octagon(0, 0, 0.26, 0.26, 0.08), 0.9, 12.2, "graphite")
    for sx in (-1, 1):
        for sf in (-1, 1):
            m.vcyl(sf * P, 0.9, 10.2, 0.05, "gunmetal", sides=4, x=sx * P)
    # Braces on all four faces, three bays.
    for k, (u0, u1) in enumerate(((1.2, 4.2), (4.2, 7.2), (7.2, 10.2))):
        for s in (-1, 1):
            a, b = (-P, s * P, u0), (P, s * P, u1)
            if k % 2:
                a, b = (P, s * P, u0), (-P, s * P, u1)
            m.limb(a, b, 0.03, 0.03, "gunmetal", sides=4, caps=False)
            a, b = (s * P, -P, u0), (s * P, P, u1)
            if k % 2 == 0:
                a, b = (s * P, P, u0), (s * P, -P, u1)
            m.limb(a, b, 0.03, 0.03, "gunmetal", sides=4, caps=False)
    for u in (4.2, 7.2):
        m.top_prism(octagon(0, 0, P + 0.07, P + 0.07, 0.1), u - 0.06, u + 0.06, "dark_steel")
    # Platform with a guard ring at 10.2 m.
    m.top_prism(octagon(0, 0, 0.9, 0.9, 0.3), 10.2, 10.35, "dark_steel")
    uring(m, 0, 0, 0.92, 0.84, 10.35, 10.62, "hazard", n=8)
    # Equipment pods clamped to the column.
    blk(m, 0.26, 0.62, -0.3, 0.3, 5.0, 6.4, "ivory", c=0.06, axis="u")
    blk(m, -0.6, -0.26, -0.25, 0.25, 8.0, 9.2, "ivory", c=0.06, axis="u")
    blk(m, -0.25, 0.25, 0.26, 0.6, 2.4, 3.4, "rust_orange", c=0.06, axis="u")
    xlight(m, -0.08, 0.08, 5.5, 6.1, 0.62, 1, depth=0.04)
    xlight(m, -0.08, 0.08, 8.3, 8.9, -0.6, -1, depth=0.04)
    flight(m, -0.06, 0.06, 2.6, 3.2, 0.6, 1, depth=0.04)
    # Dish.
    m.cyl(-0.3, -0.62, 6.9, 0.07, "gunmetal", sides=6)
    m.cyl(-0.62, -0.95, 6.9, 0.12, "white_paint", sides=10, r1=0.62)
    m.cyl(-0.95, -0.98, 6.9, 0.62, "ivory", sides=10, r1=0.58)
    # Antenna crown and beacon.
    m.top_prism(octagon(0, 0, 0.3, 0.3, 0.1), 12.2, 12.45, "dark_steel")
    for x, f, h, r in ((0.15, 0.1, 14.2, 0.035), (-0.15, 0.08, 13.4, 0.03), (0.0, -0.18, 13.0, 0.03)):
        m.vcyl(f, 12.45, h, r, "steel", sides=4, x=x)
    blk(m, 0.18, 0.34, -0.12, 0.12, 11.2, 12.6, "white_paint", c=0.04, axis="u")       # sector antenna
    blk(m, -0.34, -0.18, -0.12, 0.12, 11.0, 12.3, "white_paint", c=0.04, axis="u")
    m.vcyl(0.0, 12.45, 12.7, 0.09, "glow_amber", sides=6, x=-0.05)
    # Baked detail: seams, bolts, signage, hazard band.
    for s in (-1, 1):
        fhazard(m, -0.6, 0.6, 0.35, 0.6, 0.75 * s, s, stripe=0.09)
        for u in (1.5, 3.0, 4.5, 6.0, 7.5, 9.0, 10.5, 11.8):
            fbolt(m, 0.0, u, 0.26 * s, s, r=0.02)
            xbolt(m, 0.0, u, 0.26 * s, s, r=0.02)
        fseams_h(m, [2.5, 5.0, 7.5, 10.0], -0.15, 0.15, 0.26 * s, s)
    xplate(m, -0.2, 0.2, 5.15, 5.4, 0.62, 1, "lime", depth=0.006, c=0.0)
    xplate(m, -1.2, -0.6, 1.0, 1.2, 1.4, 1, "lime", depth=0.006, c=0.0)
    m.marker("beacon", f=0.0, u=12.6)
    return finish(m, BUDGET, texture_size=1024)
