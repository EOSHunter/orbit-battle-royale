"""Colony work light: amber flood lamp mast on a tripod. Concept: 40-prop-kit.png (right), 31-colony-structure-kit.png.

2.9 m tall, origin at the base center on the ground, tripod footprint about
1.4 m. Two flood heads face +f; the "light" marker sits between them so the
game can attach an OmniLight3D/SpotLight3D there.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (150, 800)


def build():
    m = Model("colony-work-light", category="colony-kit", bevel=0.005, cage=0.01)
    import math
    # Tripod legs with rubber feet and a hub.
    for k in range(3):
        a = math.radians(90 + k * 120)
        fx, ff = math.cos(a) * 0.68, math.sin(a) * 0.68
        m.limb((0.0, 0.0, 0.85), (fx, ff, 0.05), 0.03, 0.025, "graphite", sides=6)
        m.vcyl(ff, 0.0, 0.06, 0.06, "rubber", sides=6, x=fx)
        m.limb((fx * 0.45, ff * 0.45, 0.48), (0.0, 0.0, 0.42), 0.015, 0.015, "gunmetal", sides=4, caps=False)
    blk(m, -0.08, 0.08, -0.08, 0.08, 0.7, 1.0, "rust_orange", c=0.025, axis="u")
    # Telescoping mast.
    m.vcyl(0.0, 0.95, 2.0, 0.045, "graphite", sides=8)
    m.vcyl(0.0, 1.95, 2.65, 0.032, "steel", sides=8)
    m.vcyl(0.0, 1.9, 1.98, 0.06, "dark_steel", sides=8)
    blk(m, -0.05, 0.05, 0.045, 0.1, 1.2, 1.55, "graphite", c=0.01, axis="f")
    flight(m, -0.02, 0.02, 1.25, 1.5, 0.1, 1, depth=0.015)
    # Crossbar and two flood heads.
    m.xcyl(0.0, 2.65, -0.48, 0.48, 0.03, "dark_steel", sides=6)
    for x in (-0.3, 0.3):
        blk(m, x - 0.2, x + 0.2, -0.11, 0.07, 2.53, 2.83, "graphite", c=0.03, axis="f")
        blk(m, x - 0.17, x + 0.17, 0.07, 0.095, 2.56, 2.8, "glow_amber", axis="f")
        blk(m, x - 0.21, x + 0.21, 0.07, 0.13, 2.81, 2.85, "dark_steel", axis="f")     # visor
        fvents(m, x - 0.15, x + 0.15, 2.57, 2.79, -0.11, -1, 5)
    # Cable to a ground battery box.
    m.limb((0.05, 0.0, 1.2), (0.25, 0.25, 0.3), 0.012, 0.012, "rubber", sides=4, caps=False)
    m.limb((0.25, 0.25, 0.3), (0.4, 0.45, 0.02), 0.012, 0.012, "rubber", sides=4, caps=False)
    blk(m, 0.3, 0.7, 0.35, 0.6, 0.0, 0.28, "ivory", c=0.03, axis="x")
    fvents(m, 0.35, 0.55, 0.06, 0.22, 0.6, 1, 3)
    flight(m, 0.6, 0.66, 0.12, 0.2, 0.6, 1, depth=0.012)
    fhazard(m, -0.08, 0.08, 0.72, 0.84, 0.08, 1, stripe=0.04, depth=0.004)
    fhazard(m, -0.08, 0.08, 0.72, 0.84, -0.08, -1, stripe=0.04, depth=0.004)
    m.marker("light", f=0.2, u=2.68)
    return finish(m, BUDGET, texture_size=512)
