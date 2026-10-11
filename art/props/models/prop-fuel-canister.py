"""Fuel canister (stands in for a barrel stack). Concept: codex/concepts/v0.2/40-prop-kit.png (top right, lit cylinders).

0.56 m diameter, 1.15 m tall pressurized fuel cell in a protective cage,
origin at the base center on the ground. Graphite tank with burnt-orange
bands, vertical amber sight-glass strips on +f and -f, a domed top with a
valve and carry hoops. Reads as explosive cover in a match.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (100, 800)
R, H = 0.25, 1.0


def build():
    m = Model("prop-fuel-canister", category="props", bevel=0.004, cage=0.008)
    m.vcyl(0.0, 0.06, H, R, "graphite", sides=14)
    m.top_prism(ring_pts(0, 0, R, 14), H, H + 0.02, "graphite")
    m.limb((0.0, 0.0, H + 0.02), (0.0, 0.0, H + 0.1), R - 0.02, 0.1, "graphite", sides=14)
    m.vcyl(0.0, H + 0.1, H + 0.16, 0.05, "dark_steel", sides=8)
    m.xcyl(0.0, H + 0.14, -0.1, 0.1, 0.018, "hazard", sides=6)
    m.top_prism(octagon(0, 0, R + 0.04, R + 0.04, 0.1), 0.0, 0.08, "dark_steel")
    for u0 in (0.2, 0.82):
        m.vcyl(0.0, u0, u0 + 0.06, R + 0.015, "rust_orange", sides=14)
    # Cage posts.
    for x, f in ((0.21, 0.21), (-0.21, 0.21), (0.21, -0.21), (-0.21, -0.21)):
        m.vcyl(f, 0.06, H + 0.06, 0.016, "gunmetal", sides=5, x=x)
    m.top_prism(octagon(0, 0, R + 0.03, R + 0.03, 0.1), H + 0.04, H + 0.07, "gunmetal")
    # Sight-glass strips.
    for s in (-1, 1):
        blk(m, -0.05, 0.05, s * (R - 0.03), s * (R + 0.025), 0.3, 0.78, "dark_steel", c=0.015, axis="f")
        blk(m, -0.025, 0.025, s * (R + 0.02), s * (R + 0.032), 0.33, 0.75, "glow_amber", axis="f")
        fhazard(m, -0.12, 0.12, 0.09, 0.17, s * (R - 0.004), s, stripe=0.04, depth=0.004)
        fplate(m, 0.08, 0.15, 0.4, 0.7, s * (R - 0.006), s, "lime", depth=0.006, c=0.0)
    for s in (-1, 1):
        xplate(m, -0.08, 0.08, 0.36, 0.7, s * (R - 0.006), s, "ivory", depth=0.006, c=0.01)
    return finish(m, BUDGET, texture_size=512)
