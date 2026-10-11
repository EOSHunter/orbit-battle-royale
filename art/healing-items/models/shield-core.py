"""Shield Core: full shield restore. Concept: codex/concepts/v0.2/13-shield-core.png.

Upright reactor canister, origin at its center (also the grip). A glowing cyan
core behind four steel bars and two clamp rings, a heavy stepped base and a
collar with amber light bands, two navy side grips with black perforated
inserts and lime marks, a top handle arch, and a top cap with a cyan ring that
is its own object ("cap").
"""

import math

import kit
from kit import Model

BUDGET = (500, 1500)

kit.MATERIALS.setdefault("glow_cyan_core", ("1580c0", 0.0, 0.2, "0b6aa6", "glow"))
kit.MATERIALS.setdefault("alloy", ("9ca1a8", 0.6, 0.4, None, "metal"))


def ngon(r, u, n=12, rot=15.0):
    return [(math.cos(math.radians(rot + 360 * i / n)) * r, -math.sin(math.radians(rot + 360 * i / n)) * r, u) for i in range(n)]


def face_box(m, ang, r0, r1, hw, u0, u1, mat, c=0.002, group="body", detail=False):
    o = m.side_box(-hw, hw, u0, u1, r0, r1, mat, c=c, group=group, detail=detail)
    m.transform(o, rotate=(0, 0, ang))
    return o


def build():
    m = Model("shield-core", category="healing-items")

    # Heavy base: stepped, chamfered 12-gon.
    m.loft([ngon(0.05, -0.115), ngon(0.058, -0.108), ngon(0.058, -0.075), ngon(0.054, -0.07), ngon(0.054, -0.058), ngon(0.048, -0.052)], "graphite")
    for k in range(4):
        ang = 90 * k + 45
        face_box(m, ang, 0.054, 0.0605, 0.018, -0.104, -0.08, "alloy", c=0.004)
        face_box(m, ang, 0.06, 0.0615, 0.012, -0.098, -0.086, "polymer", detail=True)
    for ang in (0, 180):
        face_box(m, ang, 0.052, 0.0565, 0.012, -0.068, -0.062, "glow_amber", c=0.0)
    for ang in (90, 270):
        face_box(m, ang, 0.055, 0.0595, 0.006, -0.1, -0.08, "lime", c=0.0)

    # Core window: glowing column, two clamp rings, four steel bars.
    m.vcyl(0.0, -0.055, 0.055, 0.042, "glow_cyan_core", sides=12)
    m.vcyl(0.0, -0.007, 0.003, 0.0455, "gunmetal", sides=12)
    for k in range(4):
        ang = 90 * k + 45
        o = m.vcyl(0.0, -0.055, 0.055, 0.0042, "alloy", sides=6, x=0.045)
        m.transform(o, rotate=(0, 0, ang))
        face_box(m, ang, 0.044, 0.0505, 0.007, -0.01, 0.006, "gunmetal", c=0.0)
    for k in range(6):
        face_box(m, 30 * k * 2 + 15, 0.0412, 0.0425, 0.0014, -0.04, 0.04, "glow_white", c=0.0, detail=True)

    # Upper collar with amber light bands.
    m.loft([ngon(0.046, 0.05), ngon(0.054, 0.058), ngon(0.054, 0.085), ngon(0.046, 0.093)], "graphite")
    for ang in (0, 180):
        face_box(m, ang, 0.05, 0.0555, 0.016, 0.076, 0.081, "glow_amber", c=0.0)
        face_box(m, ang, 0.051, 0.0555, 0.022, 0.06, 0.074, "alloy", c=0.003)
    for ang in (90, 270):
        face_box(m, ang, 0.052, 0.056, 0.006, 0.062, 0.08, "lime", c=0.0)
    for k in range(12):
        face_box(m, 30 * k + 15, 0.0535, 0.055, 0.0012, 0.087, 0.09, "polymer", detail=True)

    # Side grips on +x and -x: navy frames with perforated black inserts.
    for s in (1, -1):
        xa, xb = sorted((s * 0.056, s * 0.078))
        m.side_box(-0.017, 0.017, -0.09, 0.09, xa, xb, "graphite", c=0.008)
        ia, ib = sorted((s * 0.074, s * 0.081))
        m.side_box(-0.011, 0.011, -0.06, 0.06, ia, ib, "rubber", c=0.004)
        for u in (-0.05, -0.038, -0.026, -0.014, -0.002, 0.01, 0.022, 0.034, 0.046):
            for f in (-0.006, 0.0, 0.006):
                o = m.xcyl(f + (0.003 if int(u * 1000) % 24 else 0.0), u, s * 0.0805, s * 0.0795, 0.0016, "polymer", sides=6, detail=True)
        la, lb = sorted((s * 0.077, s * 0.0795))
        m.side_box(-0.012, 0.012, 0.066, 0.078, la, lb, "lime", c=0.002)
        m.side_box(-0.012, 0.012, -0.08, -0.068, la, lb, "lime", c=0.002)
        # Brackets tying the grip to the body.
        ba, bb = sorted((s * 0.04, s * 0.06))
        for u0, u1 in ((-0.098, -0.078), (0.074, 0.094)):
            m.side_box(-0.012, 0.012, u0, u1, ba, bb, "gunmetal", c=0.004)
            m.xcyl(0.0, (u0 + u1) / 2, s * 0.077, s * 0.0795, 0.004, "steel", sides=6, detail=True)

    # Top handle arch across the cap, from grip to grip.
    for s in (1, -1):
        xa, xb = sorted((s * 0.05, s * 0.064))
        m.side_box(-0.01, 0.01, 0.088, 0.13, xa, xb, "alloy", c=0.004)
    m.side_box(-0.011, 0.011, 0.12, 0.134, -0.064, 0.064, "alloy", c=0.005)
    m.side_box(-0.012, 0.012, 0.122, 0.136, -0.035, 0.035, "rubber", c=0.005)

    # Top cap with glowing ring: its own object.
    m.vcyl(0.0, 0.092, 0.104, 0.04, "gunmetal", sides=12, group="cap")
    m.vcyl(0.0, 0.104, 0.108, 0.03, "glow_cyan_core", sides=12, group="cap")
    m.vcyl(0.0, 0.104, 0.111, 0.024, "alloy", sides=12, group="cap")
    m.vcyl(0.0, 0.111, 0.113, 0.009, "glow_cyan", sides=8, group="cap")
    for k in range(8):
        o = m.vcyl(0.0, 0.104, 0.1052, 0.0016, "steel", sides=6, x=0.035, group="cap", detail=True)
        m.transform(o, rotate=(0, 0, 45 * k + 22.5))

    m.marker("grip", f=0.0, u=0.0)
    return m.finish(BUDGET, texture_size=1024)
