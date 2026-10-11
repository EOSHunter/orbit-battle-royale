"""Colony pipe, 90 degree bend. Concept: 31-colony-structure-kit.png.

Matches colony-pipe-straight: axis at u = 1.2, radius 0.25, flanged ends.
Origin on the ground at the grid point where the incoming run would continue.
The pipe enters along +x at x = -2 (f = 0), turns on a 0.6 m elbow and leaves
along +f at f = +2 (x = 0); a straight piece rotated 90 degrees and centered at
(x 0, f 4) continues the run. Two support stands.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (200, 800)
U, R, RB = 1.2, 0.25, 0.6


def stand(m, x, f, along_x=True):
    blk(m, x - 0.32, x + 0.32, f - 0.32, f + 0.32, 0.0, 0.35, "concrete", c=0.07, axis="u")
    blk(m, x - 0.12, x + 0.12, f - 0.12, f + 0.12, 0.35, U - R + 0.02, "graphite", c=0.04, axis="u")
    if along_x:
        m.xcyl(f, U, x - 0.08, x + 0.08, R + 0.04, "dark_steel", sides=12)
    else:
        m.cyl(f - 0.08, f + 0.08, U, R + 0.04, "dark_steel", sides=12, x=x)
    for sx in (-1, 1):
        for sf in (-1, 1):
            ubolt(m, x + sx * 0.24, f + sf * 0.24, 0.35, r=0.025)


def flange_bolts(m, axis, pos, ring_r=R + 0.045):
    for k in range(8):
        a = 2 * math.pi * k / 8
        dc, du = math.cos(a) * ring_r, U + math.sin(a) * ring_r
        if axis == "x":
            m.xcyl(dc, du, pos - 0.07, pos + 0.07, 0.018, "steel", sides=6, detail=True)
        else:
            m.cyl(pos - 0.07, pos + 0.07, du, 0.018, "steel", sides=6, x=dc, detail=True)


def build():
    m = Model("colony-pipe-bend", category="colony-kit", bevel=0.008, cage=0.016)
    # Straight legs, elbow, flanges.
    m.xcyl(0.0, U, -1.9, -RB, R, "ivory", sides=12)
    m.cyl(RB, 1.9, U, R, "ivory", sides=12, x=0.0)
    pipe_arc(m, (-RB, RB), RB, R, -90.0, 0.0, U, "rust_orange", n=6, sides=12, caps=False)
    m.xcyl(0.0, U, -2.0, -1.9, R + 0.08, "graphite", sides=12)
    m.cyl(1.9, 2.0, U, R + 0.08, "graphite", sides=12, x=0.0)
    m.xcyl(0.0, U, -RB - 0.1, -RB, R + 0.06, "graphite", sides=12)
    m.cyl(RB, RB + 0.1, U, R + 0.06, "graphite", sides=12, x=0.0)
    stand(m, -1.35, 0.0, along_x=True)
    stand(m, 0.0, 1.35, along_x=False)
    # Pressure gauge on the elbow.
    gx, gf = -RB + RB * math.cos(math.radians(45)), RB - RB * math.sin(math.radians(45))
    m.vcyl(gf, U + R - 0.04, U + R + 0.13, 0.04, "gunmetal", sides=6, x=gx)
    m.cyl(gf - 0.04, gf + 0.04, U + R + 0.22, 0.1, "white_paint", sides=10, x=gx)
    m.cyl(gf + 0.04, gf + 0.05, U + R + 0.22, 0.08, "glass", sides=10, x=gx)
    # Baked bolts and weld beads.
    flange_bolts(m, "x", -1.95)
    flange_bolts(m, "f", 1.95)
    flange_bolts(m, "x", -RB - 0.05, R + 0.03)
    flange_bolts(m, "f", RB + 0.05, R + 0.03)
    for x in (-1.0,):
        m.xcyl(0.0, U, x - 0.012, x + 0.012, R + 0.006, "gunmetal", sides=12, detail=True)
    m.cyl(1.2, 1.224, U, R + 0.006, "gunmetal", sides=12, x=0.0, detail=True)
    return finish(m, BUDGET, texture_size=512)
