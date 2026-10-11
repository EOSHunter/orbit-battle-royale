"""Colony wall with a window. Concept: codex/concepts/v0.2/31-colony-structure-kit.png.

Same envelope as colony-wall: 4 m wide (x -2..2), 4 m tall, core 0.3 m on f = 0,
origin at base center on the floor top. Window 2.6 m x 1.5 m (x -1.3..1.3,
u 1.2..2.7): dark glass with a faint warm interior glow, a center mullion,
a chamfered frame proud of both faces and an amber light over it.
The glass is opaque geometry (no transparency in the kit).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (300, 1000)
WX, U0, U1 = 1.3, 1.2, 2.7


def build():
    m = Model("colony-wall-window", category="colony-kit", bevel=0.01, cage=0.02)
    wall_core(m, opening=(-WX, WX, U0, U1))
    # Glass, mullion, frame.
    blk(m, -WX, WX, -0.03, 0.03, U0, U1, "window_glow")
    blk(m, -0.05, 0.05, -0.09, 0.09, U0, U1, "graphite", c=0.02, axis="u")
    for s in (-1, 1):
        blk(m, s * WX, s * (WX + 0.22), -0.32, 0.32, U0 - 0.2, U1 + 0.25, "graphite", c=0.06, axis="u")
        for uu, du in ((U1, -1), (U0, 1)):
            m.front_prism([(s * WX, uu), (s * (WX - 0.22), uu), (s * WX, uu + du * 0.22)], -0.28, 0.28, "graphite")
    blk(m, -WX - 0.24, WX + 0.24, -0.38, 0.38, U0 - 0.2, U0, "graphite", c=0.05, axis="x")
    blk(m, -WX - 0.22, WX + 0.22, -0.32, 0.32, U1, U1 + 0.25, "graphite", c=0.06, axis="x")
    for s in (-1, 1):
        face = 0.32 * s
        flight(m, -0.5, 0.5, U1 + 0.08, U1 + 0.16, face, s)
        for x in (-WX - 0.11, WX + 0.11):
            for u in (U0 - 0.05, U1 + 0.12):
                fbolt(m, x, u, face, s, r=0.02)
        uhazard(m, -WX - 0.2, WX + 0.2, 0.33 * s - 0.04 if s > 0 else -0.37, 0.37 if s > 0 else -0.29, U0)
        # Glass glints / interior mullion frames (baked).
        for x in (-0.65, 0.65):
            fplate(m, x - 0.015, x + 0.015, U0, U1, 0.03 * s, s, "graphite", depth=0.01, c=0.0)
        # Cladding.
        f1 = panel(m, -1.78, -1.55, 0.5, 3.55, s, "ivory", bolts=False)
        f2 = panel(m, 1.55, 1.78, 0.5, 3.55, s, "rust_orange", bolts=False)
        for f, x in ((f1, -1.665), (f2, 1.665)):
            for u in (0.6, 2.0, 3.45):
                fbolt(m, x, u, f, s, r=0.016)
        f3 = panel(m, -1.45, 1.45, 0.5, U0 - 0.25, s, "rust_orange", seams=[0.0])
        fvents(m, -1.2, -0.2, 0.58, 0.88, f3, s, 4)
        fvents(m, 0.2, 1.2, 0.58, 0.88, f3, s, 4)
        f4 = panel(m, -1.45, 1.45, U1 + 0.3, 3.55, s, "ivory", seams=[-0.6, 0.6])
        fplate(m, 0.75, 1.3, 3.15, 3.45, f4, s, "lime", depth=0.006, c=0.0)
    return finish(m, BUDGET, texture_size=1024)
