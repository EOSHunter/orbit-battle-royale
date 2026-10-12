"""Observatory dome with telescope: Crown Observatory landmark. Concepts:
codex/concepts/v0.2/33-crown-observatory.png and the domes in 47-ringfall-map.png.

12 m wide drum with an ivory dome, an open observation slit and a telescope
barrel pointing out of it, an entry door (sealed) on the -f side, amber lights.
Origin at the base center on the ground. Large architecture: under 1000 tris.
"""

import math

from kit import Model

BUDGET = (400, 1000)
R = 6.0          # drum radius
WALL = 3.6       # drum wall height
N = 16


def ring(r, u, n=N, cf=0.0):
    return [(r * math.cos(2 * math.pi * (i + 0.5) / n), cf + r * math.sin(2 * math.pi * (i + 0.5) / n), u) for i in range(n)]


def build():
    m = Model("observatory-dome", category="locations", bevel=0.03, cage=0.05)
    # Plinth and drum.
    m.loft([ring(R + 0.6, 0.0), ring(R + 0.6, 0.5), ring(R + 0.3, 0.6)], "concrete")
    m.loft([ring(R, 0.6), ring(R, WALL), ring(R + 0.15, WALL + 0.05), ring(R + 0.15, WALL + 0.35)], "graphite")
    # Dome: hemisphere of rings, slightly flattened.
    rings = []
    for k in range(7):
        a = math.radians(k * 14.0)
        rings.append(ring((R - 0.05) * math.cos(a), WALL + 0.35 + (R - 0.6) * math.sin(a)))
    m.loft(rings, "ivory")
    # Observation slit (dark recess) up the dome front, and the telescope.
    # The slit: dark segments laid along the dome's front meridian, from the drum to the crown.
    rd = R - 0.05
    for k in range(6):
        a0, a1 = math.radians(k * 14.0), math.radians((k + 1) * 14.0)
        p0 = (0.0, rd * math.cos(a0), WALL + 0.35 + (R - 0.6) * math.sin(a0))
        p1 = (0.0, rd * math.cos(a1), WALL + 0.35 + (R - 0.6) * math.sin(a1))
        mid = ((p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2)
        seg = m.box(-0.75, 0.75, -0.1, 0.12, 1.5, "polymer", c=0.0)
        tilt = math.degrees(math.atan2(p1[2] - p0[2], p1[1] - p0[1]))
        seglen = math.hypot(p1[1] - p0[1], p1[2] - p0[2]) / 1.5
        m.transform(seg, rotate=(0, 0, 0))
        for v in seg.data.vertices:
            v.co.y *= seglen
        m.transform(seg, rotate=(-tilt, 0, 0), move=(0.0, mid[0], mid[1]))
    # Telescope tilted 30 degrees up, poking out through the slit.
    tube = [m.cyl(-0.8, 6.8, 0.0, 0.62, "graphite", sides=10, r1=0.78),
            m.cyl(6.8, 7.0, 0.0, 0.7, "lens", sides=10),
            m.cyl(1.0, 1.6, 0.0, 0.85, "gunmetal", sides=10)]
    for p in tube:
        m.transform(p, rotate=(30, 0, 0), move=(0, 0, WALL + 2.6))
    m.box(-0.8, 0.8, WALL + 1.6, WALL + 2.4, 1.6, "gunmetal", c=0.1)          # mount
    # Ribs on the dome (detail) and the door, steps, lights.
    for i in range(8):
        a = 2 * math.pi * i / 8
        m.limb((math.cos(a) * (R + 0.05), math.sin(a) * (R + 0.05), WALL + 0.35),
               (math.cos(a) * 2.2, math.sin(a) * 2.2, WALL + 5.4), 0.08, 0.08, "graphite", sides=4, detail=True)
    m.box(-R - 0.35, -R + 0.05, 0.6, 3.0, 1.8, "gunmetal", c=0.1)
    m.box(-R - 0.32, -R + 0.08, 0.7, 2.9, 1.5, "polymer", c=0.05)
    m.box(-R - 1.4, -R - 0.6, 0.0, 0.3, 2.4, "concrete", c=0.05)
    m.box(-R - 0.9, -R - 0.6, 0.3, 0.6, 2.4, "concrete", c=0.05)
    for a in (40, 140, 220, 320):
        x = math.cos(math.radians(a)) * (R + 0.08)
        f = math.sin(math.radians(a)) * (R + 0.08)
        m.box(f - 0.2, f + 0.2, WALL - 0.4, WALL - 0.2, 0.5, "glow_amber", x=x, c=0.0)
    m.vents(-3.0, 3.0, 1.2, 1.5, R + 0.01, 10, "gunmetal")
    m.marker("top", f=0.0, u=WALL + 6.0)
    return m.finish(BUDGET, texture_size=1024)
