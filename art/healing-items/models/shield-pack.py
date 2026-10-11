"""Shield Pack: medium shield restore. Concept: codex/concepts/v0.2/12-shield-pack.png.

A flat hexagonal case seen face-on from the side: three glowing cyan cells
behind a thick framed window on the front face, lime armor accents, amber and
cyan status lights, side clamps with steel D-rings, and a carry handle on top
that is its own object ("handle") so it can fold. Origin at the center of the
case; the "grip" marker sits on the handle bar.
"""

import kit
from kit import Model

BUDGET = (500, 1500)

kit.MATERIALS.setdefault("glow_cyan_core", ("1580c0", 0.0, 0.2, "0b6aa6", "glow"))
kit.MATERIALS.setdefault("alloy", ("9ca1a8", 0.6, 0.4, None, "metal"))

OUTER = [(-0.09, -0.125), (0.09, -0.125), (0.15, -0.055), (0.15, 0.05), (0.095, 0.12), (-0.095, 0.12), (-0.15, 0.05), (-0.15, -0.055)]
X0, X1 = -0.045, 0.03    # back face, front face of the shell
FX = 0.058                # front of the window frame
CX = 0.034                # cell axis


def scaled(pts, k, du=0.0):
    return [(f * k, u * k + du) for f, u in pts]


def build():
    m = Model("shield-pack", category="healing-items")

    # Shell, rear cover and dark inner panel behind the cells.
    m.prism(OUTER, X1 - X0, "graphite", x=(X0 + X1) / 2)
    m.prism(scaled(OUTER, 0.9), 0.008, "graphite", x=X0 - 0.002)
    inner = scaled(OUTER, 0.74, -0.002)
    m.prism(inner, 0.004, "polymer", x=X1 + 0.0005)

    # Front frame: one chamfered segment per edge of the window.
    n = len(OUTER)
    outer_f = scaled(OUTER, 0.97)
    for i in range(n):
        j = (i + 1) % n
        seg = [outer_f[i], outer_f[j], inner[j], inner[i]]
        mat = "lime" if i in (2, 6) else "graphite"
        m.prism(seg, FX - X1 + 0.004, mat, x=(FX + X1 - 0.004) / 2)
    # Lights on the frame: amber at the corners, cyan pips top and bottom.
    for f, u, mat in ((-0.06, 0.1, "glow_amber"), (0.06, 0.1, "glow_amber"), (-0.06, -0.106, "glow_amber"), (0.06, -0.106, "glow_amber"),
                      (0.0, 0.1, "glow_cyan"), (0.0, -0.106, "glow_cyan")):
        m.side_box(f - 0.012, f + 0.012, u - 0.004, u + 0.004, FX - 0.002, FX + 0.0015, mat, c=0.0)
    for f, u in ((-0.1, 0.09), (0.1, 0.09), (-0.1, -0.09), (0.1, -0.09), (-0.13, 0.0), (0.13, 0.0)):
        m.xcyl(f, u, FX - 0.0005, FX + 0.0012, 0.003, "steel", sides=6, detail=True)

    # Three cells: glowing tubes with steel end caps and status lights.
    for f in (-0.052, 0.0, 0.052):
        m.vcyl(f, -0.06, 0.06, 0.019, "glow_cyan_core", sides=10, x=CX)
        for u0, u1 in ((-0.088, -0.056), (0.056, 0.088)):
            m.vcyl(f, u0, u1, 0.022, "alloy", sides=8, x=CX)
            m.side_box(f - 0.006, f + 0.006, u0 + 0.008, u0 + 0.013, CX + 0.019, CX + 0.0225, "glow_cyan" if u0 > 0 else "glow_amber", c=0.0)
            for du in (u0 + 0.004, u1 - 0.004):
                m.side_box(f - 0.02, f + 0.02, du - 0.001, du + 0.001, CX + 0.019, CX + 0.0215, "gunmetal", detail=True)
        m.side_box(f - 0.0016, f + 0.0016, -0.05, 0.05, CX + 0.0175, CX + 0.0195, "glow_white", detail=True)

    # Side clamps with steel D-rings.
    for s in (1, -1):
        fa, fb = sorted((s * 0.14, s * 0.165))
        m.side_box(fa, fb, -0.045, 0.045, X0 + 0.006, X1 - 0.004, "gunmetal", c=0.008)
        ga, gb = sorted((s * 0.163, s * 0.168))
        m.side_box(ga, gb, -0.02, 0.02, -0.012, 0.004, "glow_amber", c=0.0015)
        ring = m.tube(-0.003, 0.003, 0.0, 0.022, 0.016, "steel", sides=8)
        m.transform(ring, rotate=(0, 0, 90), move=(-0.004, s * 0.145, -0.085))
        m.side_box(*sorted((s * 0.12, s * 0.15)), -0.075, -0.06, X0 + 0.01, X1 - 0.012, "gunmetal", c=0.004)
        m.side_box(*sorted((s * 0.1505, s * 0.152)), -0.03, 0.03, X0 + 0.01, X1 - 0.01, "lime", detail=True)

    # Back: lime diagonal plates and panel lines.
    m.prism([(-0.15, 0.03), (-0.15, -0.035), (-0.08, -0.115), (-0.05, -0.115)], 0.003, "lime", x=X0 - 0.006)
    m.prism([(0.15, -0.03), (0.15, 0.035), (0.085, 0.11), (0.055, 0.11)], 0.003, "lime", x=X0 - 0.006)
    m.side_box(-0.07, 0.07, -0.08, 0.075, X0 - 0.0072, X0 - 0.0056, "polymer", c=0.02, detail=True)
    m.side_box(-0.067, 0.067, -0.077, 0.072, X0 - 0.0074, X0 - 0.0058, "graphite", c=0.018, detail=True)

    # Top: hinge blocks (fixed) and the folding handle.
    for f in (-0.07, 0.07):
        m.side_box(f - 0.016, f + 0.016, 0.112, 0.135, -0.03, 0.02, "gunmetal", c=0.006)
        m.side_box(f - 0.008, f + 0.008, 0.125, 0.128, 0.02, 0.0215, "glow_amber", detail=True)
        m.xcyl(f, 0.13, -0.034, 0.024, 0.008, "steel", sides=8)
    for f in (-0.07, 0.07):
        m.box(f - 0.011, f + 0.011, 0.128, 0.18, 0.018, "alloy", c=0.006, x=-0.005, group="handle")
    m.cyl(-0.085, 0.085, 0.175, 0.013, "alloy", sides=8, x=-0.005, group="handle")
    m.cyl(-0.058, 0.058, 0.175, 0.0155, "rubber", sides=8, x=-0.005, group="handle")
    for i in range(7):
        f = -0.05 + i * 0.0167
        m.cyl(f, f + 0.006, 0.175, 0.0162, "rubber", sides=10, x=-0.005, group="handle", detail=True)

    m.marker("grip", f=0.0, u=0.175, x=-0.005)
    return m.finish(BUDGET, texture_size=1024)
