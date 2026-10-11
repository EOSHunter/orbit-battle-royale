"""Phoenix Capsule: full health and shield restore. Concept: codex/concepts/v0.2/14-phoenix-capsule.png.

Long upright capsule, origin at its center (also the grip). Twin glowing
windows on both faces, coral health and cyan shield split by a dark spine with
amber lights; white armor brackets frame the windows, lime trims the edges.
A stepped injector nozzle with an amber ring at the bottom, and a top cap with
the coral/cyan dial that is its own object ("cap").
"""

import math

import kit
from kit import Model

BUDGET = (500, 1500)

kit.MATERIALS.setdefault("glow_cyan_core", ("1580c0", 0.0, 0.2, "0b6aa6", "glow"))
kit.MATERIALS.setdefault("glow_coral_core", ("d04a3a", 0.0, 0.2, "a8302a", "glow"))
kit.MATERIALS.setdefault("alloy", ("9ca1a8", 0.6, 0.4, None, "metal"))


def ngon(r, u, n=8, rot=0.0, sx=1.0, sf=1.0):
    return [(math.cos(math.radians(rot + 360 * i / n)) * r * sx, -math.sin(math.radians(rot + 360 * i / n)) * r * sf, u)
            for i in range(n)]


def both(m, f0, f1, u0, u1, x0, x1, mat, c=0.0, group="body", detail=False, swap=None):
    """Box on the right face and mirrored on the left; swap gives the left one another material."""
    m.side_box(f0, f1, u0, u1, x0, x1, mat, c=c, group=group, detail=detail)
    m.side_box(f0, f1, u0, u1, -x1, -x0, swap or mat, c=c, group=group, detail=detail)


def build():
    m = Model("phoenix-capsule", category="healing-items")

    # Core body: octagonal, slightly flattened sideways; lofted shoulders.
    body = [ngon(0.026, -0.112, rot=22.5, sx=0.95), ngon(0.036, -0.10, rot=22.5, sx=0.95), ngon(0.036, 0.10, rot=22.5, sx=0.95),
            ngon(0.03, 0.115, rot=22.5, sx=0.95)]
    m.loft(body, "graphite")

    # Twin windows on both faces: coral at the front, cyan behind (swapped on the left face).
    for (f0, f1, mat, other) in ((0.004, 0.026, "glow_coral_core", "glow_cyan_core"), (-0.026, -0.004, "glow_cyan_core", "glow_coral_core")):
        both(m, f0, f1, -0.062, 0.078, 0.022, 0.0345, mat, c=0.006, swap=other)
        both(m, f0 + 0.004, f0 + 0.0065, -0.045, 0.06, 0.0344, 0.0352, "glow_white", c=0.001, detail=True)
        # Bubbles in the fluid, baked only.
        for k in range(5):
            fu = -0.04 + k * 0.024
            ff = f0 + 0.006 + (k % 3) * 0.005
            both(m, ff, ff + 0.002, fu, fu + 0.002, 0.0344, 0.0352, "glow_white", detail=True)
    # Central spine between the windows with amber lights.
    both(m, -0.0045, 0.0045, -0.07, 0.09, 0.02, 0.0375, "polymer", c=0.002)
    for u0, u1 in ((0.012, 0.03), (-0.045, -0.035)):
        both(m, -0.0018, 0.0018, u0, u1, 0.037, 0.0385, "glow_amber")
    # Window frame rails along the front and back edges.
    for s in (1, -1):
        m.box(0.024 * s, 0.037 * s, -0.07, 0.085, 0.05, "graphite", c=0.004)
        m.box(0.036 * s, 0.0395 * s, -0.035, 0.055, 0.016, "lime", c=0.002)
        m.box(0.039 * s, 0.0402 * s, -0.025, 0.045, 0.005, "polymer", detail=True)
    # White armor brackets above and below the windows (chunky, chamfered).
    for u0, u1 in ((0.074, 0.118), (-0.108, -0.06)):
        m.loft([ngon(0.035, u0, rot=22.5, sx=1.08), ngon(0.042, u0 + 0.006, rot=22.5, sx=1.08), ngon(0.042, u1 - 0.006, rot=22.5, sx=1.08),
                ngon(0.035, u1, rot=22.5, sx=1.08)], "white_paint")
        mid = (u0 + u1) / 2
        # Dark inset plates on the faces with amber bars.
        both(m, -0.012, 0.012, u0 + 0.008, u1 - 0.008, 0.036, 0.0455, "polymer", c=0.004)
        both(m, -0.0035, 0.0035, u0 + 0.012, u1 - 0.012, 0.045, 0.0465, "glow_amber", c=0.001)
        # Edge lugs front and back.
        m.box(0.036, 0.047, u0 + 0.01, u1 - 0.01, 0.03, "graphite", c=0.004)
        m.box(-0.047, -0.036, u0 + 0.01, u1 - 0.01, 0.03, "graphite", c=0.004)
        m.box(0.045, 0.049, mid - 0.008, mid + 0.008, 0.012, "lime", c=0.001)
        for f in (-0.022, 0.022):
            m.screw(f, u0 + 0.01, 0.0455, r=0.0018)
            m.screw(f, u1 - 0.01, 0.0455, r=0.0018)
        both(m, -0.03, 0.03, mid - 0.0008, mid + 0.0008, 0.0445, 0.0455, "polymer", detail=True)

    # Lower injector: stepped rings down to the nozzle with an amber ring.
    m.vcyl(0.0, -0.125, -0.106, 0.03, "graphite", sides=10)
    m.vcyl(0.0, -0.128, -0.12, 0.033, "gunmetal", sides=10)
    m.vcyl(0.0, -0.14, -0.125, 0.022, "polymer", sides=10)
    m.vcyl(0.0, -0.144, -0.14, 0.019, "glow_amber", sides=10)
    m.vcyl(0.0, -0.152, -0.143, 0.015, "steel", sides=10)
    m.vcyl(0.0, -0.157, -0.151, 0.008, "gunmetal", sides=8)
    for k in range(4):
        o = m.side_box(-0.004, 0.004, -0.124, -0.112, 0.03, 0.0335, "glow_amber", c=0.001)
        m.transform(o, rotate=(0, 0, 45 + 90 * k))

    # Top cap with the split coral / cyan dial: its own object.
    m.vcyl(0.0, 0.112, 0.124, 0.032, "gunmetal", sides=12, group="cap")
    m.vcyl(0.0, 0.124, 0.134, 0.028, "alloy", sides=12, group="cap")
    m.top_prism([(math.cos(math.radians(a)) * 0.021, -math.sin(math.radians(a)) * 0.021) for a in range(-90, 91, 30)], 0.134, 0.1365, "glow_coral_core", group="cap")
    m.top_prism([(math.cos(math.radians(a)) * 0.021, -math.sin(math.radians(a)) * 0.021) for a in range(90, 271, 30)], 0.134, 0.1365, "glow_cyan_core", group="cap")
    m.box(-0.0025, 0.0025, 0.1355, 0.139, 0.024, "polymer", c=0.001, group="cap")
    for k in range(4):
        o = m.side_box(-0.003, 0.003, 0.114, 0.13, 0.031, 0.034, "glow_amber", c=0.001, group="cap")
        m.transform(o, rotate=(0, 0, 90 * k))
    for k in range(8):
        o = m.side_box(-0.002, 0.002, 0.125, 0.133, 0.0278, 0.0288, "gunmetal", group="cap", detail=True)
        m.transform(o, rotate=(0, 0, 22.5 + 45 * k))

    m.marker("grip", f=0.0, u=0.0)
    return m.finish(BUDGET, texture_size=1024)
