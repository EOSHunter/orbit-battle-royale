"""Shield Cell: small shield battery. Concept: codex/concepts/v0.2/11-shield-cell.png.

Upright hexagonal canister, origin at its center (also the grip). Chamfered
steel-and-graphite end caps with amber slits and lime corner marks, a glowing
cyan crystal core seen between six corner struts, and a top button cap that is
its own object ("cap") so it can be pressed or twisted off.
"""

import math

import kit
from kit import Model

BUDGET = (500, 1500)

kit.MATERIALS.setdefault("alloy", ("9ca1a8", 0.6, 0.4, None, "metal"))              # light brushed plates
kit.MATERIALS.setdefault("glow_cyan_core", ("1580c0", 0.0, 0.2, "0b6aa6", "glow"))     # saturated shield energy


def hex_ring(r, u, rot=0.0):
    """Six points (x, f, u) of a hexagon with flats facing +-x when rot = 0."""
    pts = []
    for i in range(6):
        a = math.radians(30 + 60 * i + rot)
        pts.append((math.cos(a) * r, -math.sin(a) * r, u))
    return pts


def chamfer_hex(m, u0, u1, r, c, mat, group="body"):
    m.loft([hex_ring(r - c, u0), hex_ring(r, u0 + c), hex_ring(r, u1 - c), hex_ring(r - c, u1)], mat, group=group)


def face_box(m, ang, r0, r1, hw, u0, u1, mat, c=0.002, group="body", detail=False):
    """Box on the face of a hexagonal or round body, rotated ang degrees about the up axis."""
    o = m.side_box(-hw, hw, u0, u1, r0, r1, mat, c=c, group=group, detail=detail)
    m.transform(o, rotate=(0, 0, ang))
    return o


def cap_block(m, u0, u1, top, group):
    R = 0.043
    ap = R * math.cos(math.radians(30))
    chamfer_hex(m, u0, u1, R, 0.006, "graphite", group)
    # Steel face plates on every flat, with amber slits on alternate faces.
    for k in range(6):
        ang = 60 * k
        face_box(m, ang, ap - 0.003, ap + 0.0015, 0.014, u0 + 0.008, u1 - 0.008, "alloy", c=0.004, group=group)
        if k % 2 == 1:
            face_box(m, ang + 30, R - 0.004, R + 0.0008, 0.0022, u0 + 0.011, u1 - 0.011, "glow_amber", c=0.0, group=group)
        # Screws on the plates.
        for du in (u0 + 0.012, u1 - 0.012):
            for s in (-1, 1):
                o = m.xcyl(s * 0.0105, du, ap + 0.0012, ap + 0.0025, 0.0016, "gunmetal", sides=6, group=group, detail=True)
                m.transform(o, rotate=(0, 0, ang))
        face_box(m, ang, ap + 0.0012, ap + 0.002, 0.009, (u0 + u1) / 2 - 0.0012, (u0 + u1) / 2 + 0.0012, "polymer", c=0.0, group=group, detail=True)
    # Lime corner marks on two corners.
    for ang in (30, 210):
        face_box(m, ang, R - 0.004, R + 0.0008, 0.005, u0 + 0.006, u1 - 0.006, "lime", c=0.002, group=group)


def build():
    m = Model("shield-cell", category="healing-items")

    H = 0.085
    # Bottom cap and its foot ring.
    cap_block(m, -H, -0.045, False, "body")
    m.loft([hex_ring(0.034, -H - 0.005), hex_ring(0.038, -H), hex_ring(0.038, -H + 0.01), hex_ring(0.034, -H + 0.01)], "gunmetal")
    # Collars between caps and window.
    for u0, u1 in ((-0.047, -0.039), (0.039, 0.047)):
        chamfer_hex(m, u0, u1, 0.040, 0.002, "gunmetal")
    # Window: glass shell with the glowing crystal inside, six corner struts.
    m.loft([hex_ring(0.012, -0.04), hex_ring(0.012, 0.04)], "gunmetal")
    m.loft([hex_ring(0.006, -0.04, 30), hex_ring(0.03, -0.03, 30), hex_ring(0.033, -0.02, 30), hex_ring(0.033, 0.02, 30),
            hex_ring(0.03, 0.03, 30), hex_ring(0.006, 0.04, 30)], "glow_cyan_core")
    for k in range(6):
        ang = 60 * k + 30
        face_box(m, ang, 0.028, 0.0395, 0.0035, -0.04, 0.04, "graphite", c=0.0)
        face_box(m, ang, 0.0393, 0.0405, 0.0015, -0.036, 0.036, "gunmetal", c=0.0, detail=True)
    # Thin window rims and inner light strips on the glass flats.
    ap = 0.034 * math.cos(math.radians(30))
    for k in range(6):
        ang = 60 * k
        face_box(m, ang, 0.031, 0.0335, 0.0010, -0.018, 0.018, "glow_cyan", c=0.0, detail=True)
    # Lime strip down one strut pair.
    for ang in (90, 270):
        face_box(m, ang, 0.0398, 0.0412, 0.0016, -0.03, 0.03, "lime", c=0.0)

    # Top cap: its own object, with the button and glowing ring.
    cap_block(m, 0.045, H, True, "cap")
    m.vcyl(0.0, H - 0.001, H + 0.005, 0.026, "gunmetal", sides=12, group="cap")
    m.vcyl(0.0, H + 0.005, H + 0.0075, 0.0205, "glow_cyan_core", sides=16, group="cap")
    m.vcyl(0.0, H + 0.005, H + 0.0095, 0.017, "steel", sides=16, group="cap")
    for k in range(6):
        o = m.vcyl(0.0, H + 0.005, H + 0.0062, 0.0013, "steel", sides=6, x=0.0225, group="cap", detail=True)
        m.transform(o, rotate=(0, 0, 60 * k))

    m.marker("grip", f=0.0, u=0.0)
    return m.finish(BUDGET, texture_size=1024)
