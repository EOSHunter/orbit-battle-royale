"""Colony habitat module: complete small habitat pod, one piece. Concept: 31-colony-structure-kit.png (bottom left).

8 m long (x -4..4) and 5 m deep (f -2.5..2.5) sealed pod on skid feet, 4.3 m
tall. Origin at the base center on the ground; footprint fits 2 x 2 grid cells
(8 x 8 m) with room for the entry steps on the +f side. The door is sealed
(the pod is solid cover); use the wall kit for enterable buildings.
Chamfered shell with framing ribs, ivory and burnt-orange cladding, lit windows,
roof equipment and amber work lights.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (500, 1000)
FL = 0.8          # shell underside
TOP = 4.0
D = 2.5


def shell_profile(d, u0, u1, cb, ct):
    return [(-d + cb, u0), (d - cb, u0), (d, u0 + cb), (d, u1 - ct), (d - ct, u1), (-d + ct, u1), (-d, u1 - ct), (-d, u0 + cb)]


def build():
    m = Model("colony-habitat-module", category="colony-kit", bevel=0.012, cage=0.024)
    # Shell and end caps.
    m.prism(shell_profile(D, FL, TOP, 0.25, 0.8), 7.6, "graphite")
    for s in (-1, 1):
        m.prism(shell_profile(D - 0.12, FL + 0.1, TOP - 0.1, 0.25, 0.75), 0.2, "ivory", x=s * 3.85)
    # Framing ribs.
    for x in (-3.65, -1.3, 1.3, 3.65):
        m.prism(shell_profile(D + 0.1, FL - 0.05, TOP + 0.08, 0.3, 0.85), 0.24, "graphite", x=x)
    # Side cladding, front (+f, with door) and back.
    for s in (-1, 1):
        f0 = s * D
        for x0, x1, mat in ((-3.5, -1.45, "ivory"), (1.45, 3.5, "ivory"), (-1.15, 1.15, "rust_orange" if s < 0 else "ivory")):
            if s > 0 and x0 == -1.15:
                continue
            blk(m, x0, x1, f0 - s * 0.01, f0 + s * 0.06, FL + 0.35, TOP - 0.9, mat, c=0.06, axis="f")
            fbolts_rect(m, x0, x1, FL + 0.35, TOP - 0.9, f0 + s * 0.06, s, inset=0.07, r=0.018)
        # Windows.
        for xc in (-2.5, 2.5):
            blk(m, xc - 0.65, xc + 0.65, f0, f0 + s * 0.09, 2.2, 2.75, "graphite", axis="f")
            blk(m, xc - 0.55, xc + 0.55, f0, f0 + s * 0.1, 2.27, 2.68, "window_glow", axis="f")
            fplate(m, xc - 0.65, xc + 0.65, 2.88, 2.95, f0 + s * 0.06, s, "hazard", depth=0.006, c=0.0)
        fvents(m, -2.9, -2.1, FL + 0.55, FL + 1.05, f0 + s * 0.06, s, 4)
        fplate(m, 2.0, 3.0, FL + 0.6, FL + 0.9, f0 + s * 0.06, s, "lime", depth=0.006, c=0.0)
    # Sealed door with a portal frame on +f.
    blk(m, -0.95, 0.95, D - 0.02, D + 0.22, FL, FL + 2.75, "graphite", c=0.1, axis="f")
    blk(m, -0.7, 0.7, D + 0.18, D + 0.25, FL + 0.05, FL + 2.45, "dark_steel", c=0.12, axis="f")
    flight(m, -0.45, 0.45, FL + 2.55, FL + 2.63, D + 0.22, 1, depth=0.04)
    fplate(m, -0.012, 0.012, FL + 0.08, FL + 2.4, D + 0.25, 1, "polymer", depth=0.005, c=0.0)
    fhazard(m, -0.66, 0.66, FL + 0.1, FL + 0.32, D + 0.25, 1, stripe=0.09)
    fplate(m, 0.98, 1.12, FL + 1.1, FL + 1.4, D + 0.06, 1, "lime", depth=0.012, c=0.0)
    # Entry steps (4 risers of 0.2) and handrails.
    prof = [(D + 1.0, 0.0), (D + 1.0, 0.2), (D + 0.75, 0.2), (D + 0.75, 0.4), (D + 0.5, 0.4), (D + 0.5, 0.6), (D + 0.22, 0.6), (D + 0.22, 0.0)]
    m.prism(prof, 1.5, "dark_steel")
    for s in (-1, 1):
        m.limb((s * 0.8, D + 1.0, 0.2), (s * 0.8, D + 1.0, 1.25), 0.03, 0.03, "hazard", sides=4)
        m.limb((s * 0.8, D + 1.0, 1.2), (s * 0.8, D + 0.25, 1.75), 0.03, 0.03, "hazard", sides=4)
    for i, u in enumerate((0.2, 0.4, 0.6)):
        uplate(m, -0.72, 0.72, D + 0.97 - i * 0.25 - 0.08, D + 0.97 - i * 0.25, u, "hazard", depth=0.006)
    # Skid feet.
    for x in (-3.0, 3.0):
        for s in (-1, 1):
            blk(m, x - 0.35, x + 0.35, s * 1.6 - 0.35, s * 1.6 + 0.35, 0.0, 0.18, "concrete")
            blk(m, x - 0.18, x + 0.18, s * 1.6 - 0.18, s * 1.6 + 0.18, 0.18, FL + 0.1, "dark_steel")
    blk(m, -3.4, 3.4, -1.75, 1.75, FL - 0.25, FL, "gunmetal", c=0.06, axis="x")
    # Roof equipment.
    blk(m, -2.8, -1.4, -1.2, 0.4, TOP, TOP + 0.6, "ivory", c=0.08, axis="u")
    blk(m, -2.85, -1.35, -1.25, 0.45, TOP + 0.6, TOP + 0.7, "dark_steel", c=0.04, axis="u")
    xvents(m, -1.0, 0.2, TOP + 0.1, TOP + 0.5, -1.4, 1, 3)
    blk(m, 1.0, 2.2, -0.6, 0.6, TOP, TOP + 0.35, "graphite", c=0.06, axis="u")
    m.vcyl(0.0, TOP + 0.35, TOP + 0.55, 0.32, "dark_steel", sides=10, x=1.6)
    m.vcyl(-0.3, TOP, TOP + 1.6, 0.03, "steel", sides=5, x=3.0)
    m.vcyl(0.3, TOP, TOP + 1.1, 0.03, "steel", sides=5, x=3.2)
    m.vcyl(-0.3, TOP + 1.6, TOP + 1.7, 0.06, "glow_amber", sides=6, x=3.0)
    # Roof plates (baked) and end-cap detail.
    for x in (-2.5, 0.0, 2.5):
        uplate(m, x - 1.1, x + 1.1, -1.6, 1.6, TOP, "polymer", depth=0.003)
        uplate(m, x - 1.08, x + 1.08, -1.58, 1.58, TOP + 0.003, "graphite", depth=0.004)
    for s in (-1, 1):
        xvents(m, -1.2, 1.2, FL + 0.6, FL + 1.3, s * 3.95, s, 5)
        xlight(m, -0.6, 0.6, TOP - 0.55, TOP - 0.48, s * 3.95, s, depth=0.04)
        xplate(m, -1.8, -1.3, 2.4, 3.0, s * 3.95, s, "lime", depth=0.006, c=0.0)
    m.marker("door", f=D + 0.25, u=FL)
    return finish(m, BUDGET, texture_size=1024)
