"""Colony cargo container: 20 ft shipping container prop. Concept: 34-anchorport.png, 40-prop-kit.png.

6.06 x 2.44 x 2.59 m (ISO 20 ft), length along x, origin at the base center on
the ground. Stacks directly (next container at u = 2.59). Navy body with
corner castings, frame rails, baked corrugation, cargo doors with lock bars on
the +x end, lime stencils and a small amber status light.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (100, 800)
L, W, H = 3.03, 1.22, 2.59


def build():
    m = Model("colony-cargo-container", category="colony-kit", bevel=0.01, cage=0.02)
    # Body and frame.
    blk(m, -L + 0.08, L - 0.08, -W + 0.04, W - 0.04, 0.12, H - 0.1, "container_blue")
    for sf in (-1, 1):
        for u0, u1 in ((0.0, 0.16), (H - 0.13, H)):
            blk(m, -L + 0.15, L - 0.15, sf * (W - 0.12), sf * W, u0, u1, "dark_steel", c=0.02, axis="x")
    for sx in (-1, 1):
        for u0, u1 in ((0.0, 0.16), (H - 0.13, H)):
            blk(m, sx * (L - 0.15), sx * (L - 0.05), -W + 0.15, W - 0.15, u0, u1, "dark_steel")
        for sf in (-1, 1):
            blk(m, sx * (L - 0.16), sx * L, sf * (W - 0.16), sf * W, 0.0, H, "dark_steel", c=0.025, axis="u")
            for u0 in (0.0, H - 0.18):
                blk(m, sx * (L - 0.18), sx * (L + 0.005), sf * (W - 0.18), sf * (W + 0.005), u0, u0 + 0.18, "gunmetal", c=0.02, axis="u")
    # Door end (+x): two leaves, four lock bars with cams and handles.
    blk(m, L - 0.09, L - 0.04, -W + 0.15, W - 0.15, 0.16, H - 0.13, "container_blue")
    for f in (-0.75, -0.3, 0.3, 0.75):
        m.vcyl(f, 0.2, H - 0.17, 0.025, "steel", sides=6, x=L - 0.01)
        blk(m, L - 0.04, L + 0.03, f - 0.04, f + 0.04, 1.0, 1.08, "gunmetal", c=0.01, axis="x")
        m.limb((L + 0.01, f, 1.04), (L + 0.06, f + 0.2, 1.04), 0.015, 0.015, "hazard", sides=4)
    xlight(m, -0.6, -0.45, H - 0.32, H - 0.26, L - 0.04, 1, depth=0.03)
    # Baked corrugation on long sides, roof and the closed end.
    for sf in (-1, 1):
        face = sf * (W - 0.04)
        x = -L + 0.2
        while x < L - 0.25:
            fplate(m, x, x + 0.09, 0.2, H - 0.16, face, sf, "container_blue", depth=0.014, c=0.0)
            x += 0.2
        fplate(m, -2.4, -1.2, 1.7, 2.1, face + sf * 0.014, sf, "lime", depth=0.006, c=0.0)
        fplate(m, -2.4, -1.7, 1.55, 1.64, face + sf * 0.014, sf, "white_paint", depth=0.006, c=0.0)
        fplate(m, 1.4, 2.6, 0.3, 0.55, face + sf * 0.014, sf, "rust_orange", depth=0.006, c=0.0)
    x = -L + 0.3
    while x < L - 0.3:
        uplate(m, x, x + 0.12, -W + 0.12, W - 0.12, H - 0.1, "container_blue", depth=0.012)
        x += 0.3
    for f in (-0.9, -0.5, -0.1, 0.3, 0.7):
        xplate(m, f, f + 0.18, 0.2, H - 0.16, -L + 0.08, -1, "container_blue", depth=0.014, c=0.0)
    xplate(m, -0.006, 0.006, 0.2, H - 0.18, L - 0.04, 1, "polymer", depth=0.004, c=0.0)
    xplate(m, 0.15, 0.95, 1.6, 1.9, L - 0.04, 1, "lime", depth=0.006, c=0.0)
    return finish(m, BUDGET, texture_size=1024)
