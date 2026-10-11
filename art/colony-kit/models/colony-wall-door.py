"""Colony wall with a doorway. Concept: codex/concepts/v0.2/31-colony-structure-kit.png.

Same envelope as colony-wall: 4 m wide (x -2..2), 4 m tall, core 0.3 m on f = 0,
origin at base center on the floor top. Open doorway 1.6 m wide x 2.6 m tall
(x -0.8..0.8, u 0..2.6) with a chamfered portal frame that stands 0.34 m proud
of both faces, amber jamb lights and a hazard-striped threshold plate.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (300, 1000)
DX, DH = 0.8, 2.6


def build():
    m = Model("colony-wall-door", category="colony-kit", bevel=0.01, cage=0.02)
    wall_core(m, opening=(-DX, DX, 0.0, DH))
    # Portal: jambs, header and chamfered inner corners.
    for s in (-1, 1):
        blk(m, s * DX, s * (DX + 0.36), -0.34, 0.34, 0.0, DH, "graphite", c=0.07, axis="u")
        m.front_prism([(s * DX, DH - 0.32), (s * DX, DH + 0.01), (s * (DX - 0.32), DH + 0.01)], -0.3, 0.3, "graphite")
    blk(m, -DX - 0.36, DX + 0.36, -0.34, 0.34, DH, DH + 0.46, "graphite", c=0.1, axis="f")
    blk(m, -DX, DX, -0.34, 0.34, 0.0, 0.035, "dark_steel")
    uhazard(m, -DX, DX, -0.32, -0.2, 0.035)
    uhazard(m, -DX, DX, 0.2, 0.32, 0.035)
    for s in (-1, 1):
        face = 0.34 * s
        # Jamb lights and the light bar over the door.
        for x in (-DX - 0.18, DX + 0.18):
            flight(m, x - 0.04, x + 0.04, 0.5, 2.1, face, s)
        flight(m, -0.45, 0.45, DH + 0.2, DH + 0.28, face, s)
        for x in (-DX - 0.3, -DX - 0.06, DX + 0.06, DX + 0.3):
            for u in (0.15, 2.3):
                fbolt(m, x, u, face, s, r=0.02)
        fseams_h(m, [1.3], -DX - 0.34, -DX - 0.02, face, s)
        fseams_h(m, [1.3], DX + 0.02, DX + 0.34, face, s)
        fhazard(m, -DX - 0.34, -DX - 0.02, 0.02, 0.32, face, s, stripe=0.08)
        fhazard(m, DX + 0.02, DX + 0.34, 0.02, 0.32, face, s, stripe=0.08)
        # Cladding beside and above the portal.
        f1 = panel(m, -1.78, -1.2, 0.5, 3.55, s, "ivory")
        fplate(m, -1.68, -1.3, 2.9, 3.3, f1, s, "lime", depth=0.006, c=0.0)
        fvents(m, -1.68, -1.3, 0.8, 1.3, f1, s, 4)
        f2 = panel(m, 1.2, 1.78, 0.5, 3.55, s, "rust_orange", seams=[1.49])
        fplate(m, 1.3, 1.68, 1.6, 2.0, f2, s, "graphite", depth=0.01, c=0.03)       # door control panel
        fplate(m, 1.4, 1.58, 1.75, 1.85, f2, s, "lime", depth=0.016, c=0.0)
        f3 = panel(m, -1.1, 1.1, DH + 0.5, 3.58, s, "ivory", bolts=False)
        fplate(m, -0.6, 0.6, DH + 0.6, DH + 0.88, f3, s, "graphite", depth=0.006, c=0.02)  # sign plate
        fplate(m, -0.5, 0.1, DH + 0.68, DH + 0.8, f3, s, "lime", depth=0.01, c=0.0)
        fplate(m, 0.2, 0.5, DH + 0.68, DH + 0.8, f3, s, "white_paint", depth=0.01, c=0.0)
    m.marker("doorway", f=0.0, u=0.0)
    return finish(m, BUDGET, texture_size=1024)
