"""Relay Nine power core: the power station's central reactor column (concept
codex/concepts/v0.2/37-relay-nine.png). 10 m footprint, 15 m tall: armored
base, glowing cyan containment rings, cooling fins, top vent stack and side
pipe stubs that line up with the colony pipe pieces (centered at 1.2 m height).
Origin at the base center on the ground. Under 1000 tris.
"""

import math

from kit import Model

BUDGET = (400, 1000)
N = 12


def ring(r, u):
    return [(r * math.cos(2 * math.pi * (i + 0.5) / N), r * math.sin(2 * math.pi * (i + 0.5) / N), u) for i in range(N)]


def build():
    m = Model("relay-power-core", category="locations", bevel=0.03, cage=0.05)
    # Octagonal armored base with hazard band.
    m.loft([ring(5.0, 0.0), ring(5.0, 2.2), ring(4.3, 2.8), ring(3.2, 3.0)], "graphite")
    m.loft([ring(5.05, 1.6), ring(5.05, 1.9)], "hazard")
    # Core column with containment rings.
    m.loft([ring(2.6, 3.0), ring(2.6, 12.0), ring(2.0, 13.0)], "gunmetal")
    for u in (4.5, 7.0, 9.5):
        m.loft([ring(2.75, u), ring(2.75, u + 0.6)], "glow_cyan")
        m.loft([ring(2.95, u - 0.2), ring(2.95, u - 0.05)], "graphite")
        m.loft([ring(2.95, u + 0.65), ring(2.95, u + 0.8)], "graphite")
    # Cooling fins.
    for i in range(6):
        a = 2 * math.pi * i / 6
        fin = m.box(-0.12, 0.12, 3.0, 11.0, 1.6, "graphite", c=0.2)
        m.transform(fin, rotate=(0, 0, math.degrees(a)), move=(math.cos(a) * 3.2, math.sin(a) * 3.2, 0))
    # Vent stack and cap light.
    m.vcyl(0.0, 13.0, 15.0, 1.2, "graphite", sides=10)
    m.vcyl(0.0, 15.0, 15.2, 1.35, "glow_amber", sides=10)
    # Pipe stubs to the four sides, matching colony pipes.
    for a in (0, 90, 180, 270):
        rad = math.radians(a)
        p = m.cyl(0, 1.6, 1.2, 0.45, "rust_metal", sides=8)
        m.transform(p, rotate=(0, 0, a), move=(math.cos(rad) * 4.6, math.sin(rad) * 4.6, 0))
    # Panels, screws and warning plates baked in.
    m.vents(-2.0, 2.0, 0.6, 1.4, 5.0, 8, "gunmetal")
    for a in range(0, 360, 45):
        rad = math.radians(a)
        door = m.box(-0.6, 0.6, 0.3, 1.5, 0.1, "polymer", c=0.05, detail=True)
        m.transform(door, rotate=(0, 0, a), move=(math.cos(rad) * 5.0, math.sin(rad) * 5.0, 0))
    m.marker("top", f=0.0, u=15.2)
    return m.finish(BUDGET, texture_size=1024)
