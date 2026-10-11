"""Vehicle spawn pad: low round pad with a glowing amber ring. Concept: codex/concepts/v0.2/40-prop-kit.png (center).

6 m diameter, 0.25 m tall, origin at the pad center on the ground; vehicles
spawn on the "spawn" marker at deck height facing +f. Graphite deck with a
glowing amber ring, ivory and burnt-orange outer ring segments, four lit
edge blocks with access ramps, baked landing marks.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (200, 800)
R, H = 3.0, 0.25
N = 20


def build():
    m = Model("prop-vehicle-spawn-pad", category="props", bevel=0.008, cage=0.016)
    m.top_prism(ring_pts(0, 0, R - 0.45, N), 0.0, H, "graphite")
    # Outer ring in alternating ivory / orange arc segments with a chamfered edge.
    for k in range(4):
        a0 = k * 90 + 8
        uarc(m, 0, 0, R, R - 0.46, a0, a0 + 74, 0.0, H - 0.02, "ivory" if k % 2 else "rust_orange", n=5)
    # Glowing ring inset in the deck.
    uring(m, 0, 0, 1.95, 1.82, H - 0.01, H + 0.008, "glow_amber", n=N)
    # Four lit edge blocks with ramps (at the ring gaps).
    for k in range(4):
        ang = k * 90
        b = blk(m, -0.28, 0.28, R - 0.55, R + 0.05, 0.0, H + 0.12, "dark_steel", c=0.05, axis="x")
        g = blk(m, -0.18, 0.18, R + 0.05, R + 0.07, 0.06, H + 0.04, "glow_amber", axis="f")
        ramp = m.prism([(R + 0.05, 0.0), (R + 0.5, 0.0), (R + 0.05, H - 0.04)], 0.5, "gunmetal")
        for p in (b, g, ramp):
            m.transform(p, rotate=(0, 0, ang))
    # Baked: landing marks, seams, bolts.
    uring(m, 0, 0, 1.3, 1.22, H - 0.003, H + 0.006, "white_paint", n=40, detail=True)
    uring(m, 0, 0, 2.5, 2.4, H - 0.003, H + 0.006, "rust_orange", n=40, detail=True)
    for k in range(4):
        p = uplate(m, -0.03, 0.03, 0.35, 0.95, H, "white_paint", depth=0.006)
        m.transform(p, rotate=(0, 0, k * 90))
    uplate(m, -0.25, 0.25, 0.95, 1.05, H, "lime", depth=0.006)
    for k in range(12):
        a = 2 * math.pi * k / 12
        ubolt(m, math.cos(a) * 2.2, math.sin(a) * 2.2, H, r=0.02)
        p = uplate(m, -0.006, 0.006, 0.4, 2.5, H, "polymer", depth=0.004)
        m.transform(p, rotate=(0, 0, math.degrees(a) + 15))
    m.marker("spawn", f=0.0, u=H)
    return finish(m, BUDGET, texture_size=1024)
