"""Colony ramp: 4 m wide vehicle/foot ramp rising 1 m over 4 m. Concept: 31-colony-structure-kit.png.

Covers x -2..2 and climbs toward +f from f = 0 (origin, ground, center of the
low edge) to f = 4, u = 1.0 (14 degrees): it meets the 1 m plinth decks of the
colony-cargo-pad and other raised platforms on the 4 m grid. Low side curbs
with amber marker lights; grip plates and hazard chevrons are baked.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from colony import *  # noqa: E402,F401,F403

BUDGET = (150, 1000)
L, H = 4.0, 1.0


def build():
    m = Model("colony-ramp", category="colony-kit", bevel=0.01, cage=0.02)
    # Deck wedge with a thick nose plate.
    m.prism([(0.0, 0.0), (L, 0.0), (L, H), (0.0, 0.03)], 3.6, "dark_steel")
    # Side curbs: sloped graphite beams with chamfered tops.
    for s in (-1, 1):
        x = s * 1.9
        m.prism([(-0.05, 0.0), (L, 0.0), (L, H + 0.18), (L - 0.12, H + 0.22), (0.15, 0.2), (-0.05, 0.12)], 0.2, "graphite", x=x)
        m.prism([(0.4, 0.0), (L - 0.15, 0.0), (L - 0.15, H - 0.2), (0.4, 0.0)][:3], 0.05, "rust_orange", x=s * 2.015)
        for f in (1.0, 2.5, 3.6):
            u = f / L * H + 0.13
            xlight(m, f - 0.08, f + 0.08, u - 0.03, u + 0.03, s * 2.0, s, depth=0.03)
            xbolt(m, f - 0.3, u - 0.05, s * 2.0, s)
            xbolt(m, f + 0.3, u - 0.05, s * 2.0, s)
    # Baked: grip plates with chevrons, rib tread.
    import math
    slope = math.atan2(H, L)
    def su(f):
        return 0.03 + (H - 0.03) * f / L

    for i in range(10):
        f = 0.35 + i * 0.37
        p = uplate(m, -1.75, 1.75, f, f + 0.06, su(f + 0.03), "gunmetal", depth=0.006)
        m.transform(p, rotate=(-math.degrees(slope), 0, 0), pivot=(0, f + 0.03, su(f + 0.03)))
    for f in (0.9, 2.4):
        for s in (-1, 1):
            p = m.top_prism([(s * 0.1, f), (s * 0.5, f + 0.4), (s * 0.5, f + 0.65), (s * 0.1, f + 0.25)],
                            su(f + 0.3) - 0.004, su(f + 0.3) + 0.007, "lime", detail=True)
            m.transform(p, rotate=(-math.degrees(slope), 0, 0), pivot=(0, f + 0.3, su(f + 0.3)))
    for f in (0.05, 3.75):
        p = uplate(m, -1.78, 1.78, f, f + 0.16, su(f + 0.08), "hazard", depth=0.006)
        m.transform(p, rotate=(-math.degrees(slope), 0, 0), pivot=(0, f + 0.08, su(f + 0.08)))
    return finish(m, BUDGET, texture_size=1024)
