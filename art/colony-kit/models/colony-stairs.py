"""Colony stairs: one storey (4 m) flight. Concept: 31-colony-structure-kit.png.

2 m wide (x -1..1), climbs toward +f: 20 risers of 0.2 m and 0.3 m treads, from
f = 0 (origin, ground, center of the first step's front edge) to the top step at
f = 6, u = 4, which meets a colony-floor or colony-gantry deck edge (2 m grid).
Railings on both sides at 1 m, steel stringers, legs and footings under the top.
Collision suggestion: a ramp box from (f 0, u 0) to (f 6, u 4).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (300, 1000)
N, RISE, RUN = 20, 0.2, 0.3


def build():
    m = Model("colony-stairs", category="colony-kit", bevel=0.01, cage=0.02)
    top_f, top_u = N * RUN, N * RISE
    prof = [(0.0, 0.0)]
    for i in range(N):
        prof += [(i * RUN, (i + 1) * RISE), ((i + 1) * RUN, (i + 1) * RISE)]
    prof += [(top_f, top_u - 0.3), (1.0, 0.0)]
    m.prism(prof, 1.84, "dark_steel")
    # Stringers.
    for s in (-1, 1):
        m.prism([(-0.15, 0.0), (0.35, 0.0), (top_f + 0.05, top_u - 0.45), (top_f + 0.05, top_u + 0.12),
                 (top_f - 0.2, top_u + 0.12), (-0.15, 0.32)], 0.12, "graphite", x=s * 0.98)
        # Footing and leg under the upper end.
        blk(m, s * 0.68, s * 1.04, 4.1, 4.46, 0.0, 0.35, "concrete", c=0.05, axis="u")
        blk(m, s * 0.78, s * 0.94, 4.2, 4.36, 0.35, 2.45, "graphite", c=0.04, axis="u")
        xlight(m, 0.05, 0.2, 0.1, 0.24, 1.04 * s, s, depth=0.04)
    m.limb((-0.86, 4.28, 0.5), (0.86, 4.28, 2.05), 0.05, 0.05, "gunmetal", sides=6)
    m.limb((0.86, 4.28, 0.5), (-0.86, 4.28, 2.05), 0.05, 0.05, "gunmetal", sides=6)
    blk(m, -0.95, 0.95, 4.16, 4.4, 2.0, 2.4, "graphite", c=0.04, axis="x")
    # Railings.
    for s in (-1, 1):
        x = s * 0.98
        posts = [0.15, 2.1, 4.05, 5.85]
        for f in posts:
            u = min(N, int(f / RUN) + 1) * RISE + 0.12
            m.vcyl(f, u - 0.1, u + 1.0, 0.03, "hazard", sides=6, x=x)
        a = (x, posts[0], posts[0] / RUN * RISE + RISE + 1.12)
        b = (x, top_f, top_u + 1.12)
        m.limb(a, b, 0.032, 0.032, "hazard", sides=6)
        m.limb((x, a[1], a[2] - 0.5), (x, b[1], b[2] - 0.5), 0.022, 0.022, "hazard", sides=6)
    # Baked: grating treads, nosing stripes, stringer bolts.
    for i in range(N):
        f0, u = i * RUN, (i + 1) * RISE
        uplate(m, -0.9, 0.9, f0 + 0.02, f0 + 0.08, u, "hazard", depth=0.006)
        for k in range(7):
            a = f0 + 0.1 + k * 0.028
            uplate(m, -0.88, 0.88, a, a + 0.012, u, "gunmetal", depth=0.006)
    for s in (-1, 1):
        for i in range(6):
            f = 0.5 + i * 1.0
            u = f / RUN * RISE - 0.05
            xbolt(m, f, u, 1.04 * s, s, r=0.02)
            xbolt(m, f + 0.15, u + 0.1, 1.04 * s, s, r=0.02)
    return finish(m, BUDGET, texture_size=1024)
