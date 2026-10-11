"""Terminal: colony console with a glowing screen. Concepts: 31-colony-structure-kit.png, 40-prop-kit.png.

0.9 m wide, 0.6 m deep, 1.45 m tall pedestal console, origin at the base
center on the ground; the user stands on the +f side facing -f. Graphite body,
ivory side cheeks, sloped lime-glowing screen, an amber status bar and a
keyboard ledge. The "screen" marker is the screen center.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (100, 800)


def build():
    m = Model("prop-terminal", category="props", bevel=0.005, cage=0.01)
    blk(m, -0.48, 0.48, -0.32, 0.32, 0.0, 0.08, "dark_steel", c=0.02, axis="x")
    # Body: side profile with a sloped screen face toward +f.
    prof = [(-0.25, 0.08), (0.18, 0.08), (0.2, 0.85), (0.32, 0.92), (0.3, 0.98), (0.1, 1.45), (-0.25, 1.45)]
    m.prism(prof, 0.8, "graphite")
    for s in (-1, 1):
        m.prism([(-0.27, 0.06), (0.22, 0.06), (0.22, 0.85), (0.34, 0.92), (0.32, 1.0), (0.12, 1.48), (-0.27, 1.48)], 0.06, "ivory", x=s * 0.43)
    # Screen (on the 0.3..0.1 / 0.98..1.45 slope), bezel and status bar.
    import math
    ang = math.degrees(math.atan2(0.2, 0.47))
    bez = blk(m, -0.34, 0.34, -0.012, 0.03, -0.22, 0.22, "dark_steel", c=0.02, axis="f")
    scr = blk(m, -0.3, 0.3, 0.02, 0.04, -0.18, 0.18, "glow_lime", axis="f")
    for p in (bez, scr):
        m.transform(p, rotate=(-ang, 0, 0), move=(0, 0.2, 1.215))
    blk(m, -0.32, 0.32, 0.18, 0.22, 0.75, 0.79, "glow_amber", axis="f")
    # Keyboard ledge.
    blk(m, -0.36, 0.36, 0.2, 0.36, 0.86, 0.9, "dark_steel", c=0.01, axis="x")
    # Rear cable and vent box.
    blk(m, -0.25, 0.25, -0.33, -0.25, 0.3, 0.9, "ivory", c=0.03, axis="f")
    m.limb((0.0, -0.3, 0.3), (0.0, -0.5, 0.02), 0.025, 0.025, "rubber", sides=6)
    # Baked: keycaps, vents, bolts, stencil, scanlines.
    for i in range(3):
        for j in range(8):
            x = -0.3 + j * 0.085
            f = 0.24 + i * 0.04
            uplate(m, x, x + 0.065, f, f + 0.03, 0.9, "polymer", depth=0.005)
    fvents(m, -0.2, 0.2, 0.4, 0.8, -0.33, -1, 6)
    fplate(m, -0.3, 0.3, 0.15, 0.6, 0.19, 1, "dark_steel", depth=0.005, c=0.02)
    fplate(m, -0.25, -0.05, 0.5, 0.56, 0.19, 1, "lime", depth=0.008, c=0.0)
    for s in (-1, 1):
        xplate(m, -0.15, 0.1, 0.3, 0.5, s * 0.46, s, "rust_orange", depth=0.005, c=0.0)
        for f, u in ((-0.2, 0.15), (0.15, 0.15), (-0.2, 1.35)):
            xbolt(m, f, u, s * 0.46, s, r=0.01)
    m.marker("screen", f=0.24, u=1.215)
    return finish(m, BUDGET, texture_size=512)
