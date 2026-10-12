"""Fractured communications dish: Crown Observatory landmark (concept
codex/concepts/v0.2/33-crown-observatory.png). A 14 m dish on a lattice tower,
tilted toward the sky, with a broken-out wedge and the feed horn on three struts.
Origin at the tower base center on the ground. Under 1000 tris.
"""

import math

from kit import Model

BUDGET = (400, 1000)
H = 9.0          # tower height to the dish hub
RD = 7.0         # dish radius
DEPTH = 1.6


def build():
    m = Model("comms-dish", category="locations", bevel=0.03, cage=0.05)
    # Base pad and lattice tower (four legs with cross braces).
    m.box(-2.6, 2.6, 0.0, 0.5, 5.2, "concrete", c=0.15)
    legs = [(-1.6, -1.6), (1.6, -1.6), (1.6, 1.6), (-1.6, 1.6)]
    for x, f in legs:
        m.limb((x, f, 0.5), (x * 0.4, f * 0.4, H - 0.6), 0.16, 0.12, "gunmetal", sides=6)
    for k in range(4):
        (x0, f0), (x1, f1) = legs[k], legs[(k + 1) % 4]
        for u0, u1, s0, s1 in ((0.8, 4.4, 1.0, 0.7), (4.4, 0.8, 1.0, 0.7)):
            m.limb((x0 * s0, f0 * s0, u0), (x1 * s1, f1 * s1, u1), 0.06, 0.06, "gunmetal", sides=4)
    m.cyl(-1.2, 1.2, H - 0.3, 1.1, "graphite", sides=10)                     # hub housing
    m.box(-0.2, 0.2, H - 1.0, H - 0.8, 2.4, "glow_amber", c=0.0)

    # Dish: paraboloid built from wedges, one wedge missing (fractured), tilted 35° up.
    parts = []
    seg = 20
    for i in range(seg):
        if i in (3, 4):
            continue
        a0 = 2 * math.pi * i / seg
        a1 = 2 * math.pi * (i + 1) / seg
        rings = []
        for k in range(4):
            r = RD * k / 3.0
            u = DEPTH * (r / RD) ** 2
            rings.append([(math.cos(a0) * r, math.sin(a0) * r, u), (math.cos(a1) * r, math.sin(a1) * r, u),
                          (math.cos(a1) * r, math.sin(a1) * r, u - 0.15), (math.cos(a0) * r, math.sin(a0) * r, u - 0.15)])
        parts.append(m.loft(rings, "ivory" if i % 5 else "graphite", group="dish"))
    # Jagged break along the missing wedge.
    for i, r in enumerate((2.2, 3.8, 5.6)):
        a = 2 * math.pi * 3 / seg + (0.12 if i % 2 else -0.05)
        shard = m.box(-0.5, 0.5, 0.0, 0.12, 0.9, "ivory", c=0.05, group="dish")
        m.transform(shard, rotate=(0, 0, math.degrees(a)), move=(math.cos(a) * r, math.sin(a) * r, DEPTH * (r / RD) ** 2))
        parts.append(shard)
    # Feed horn on three struts.
    for i in range(3):
        a = 2 * math.pi * i / 3 + 0.5
        parts.append(m.limb((math.cos(a) * RD * 0.9, math.sin(a) * RD * 0.9, DEPTH * 0.8), (0, 0, 4.6), 0.07, 0.07, "gunmetal", sides=4, group="dish"))
    parts.append(m.cyl(0, 0.0001, 4.6, 0.4, "graphite", sides=8, group="dish"))
    horn = m.vcyl(0.0, 4.2, 5.0, 0.42, "graphite", sides=8, group="dish")
    lamp = m.vcyl(0.0, 4.0, 4.2, 0.3, "glow_amber", sides=8, group="dish")
    parts += [horn, lamp]
    for p in parts:
        m.transform(p, rotate=(-58, 0, 15), pivot=(0, 0, 0), move=(0, 0, H + 0.4))
    m.marker("hub", f=0.0, u=H)
    return m.finish(BUDGET, texture_size=1024)
