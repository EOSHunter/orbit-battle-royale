"""Descent device: back-mounted thruster glider pack. Concept: codex/concepts/v0.2/27-descent-device-options.png
(middle option, the twin-thruster pack, with fold-out glide fins from the first option).

Worn on the operator's back: the origin and the "mount" marker are the
attachment point on the harness plate where it touches the back (between the
shoulder blades); the pack extends backward (-forward) from there and the
operator faces forward. A navy center spine with a pale chevron and an amber
light strip, two lime-paneled thrusters with glowing amber nozzles, harness
plate with shoulder strap stubs, and two glide fins as their own objects
("fin-left", "fin-right") so they can unfold. Nozzle markers "thrust_l" and
"thrust_r" mark where the exhaust effect starts.
"""

import math

import kit
from kit import Model

BUDGET = (500, 1500)

kit.MATERIALS.setdefault("alloy", ("9ca1a8", 0.6, 0.4, None, "metal"))

TX, TF, TR = 0.118, -0.095, 0.058     # thruster axis x, forward position, radius


def face_box(m, ang, r0, r1, hw, u0, u1, mat, cx, cf, c=0.004, group="body", detail=False):
    """Box on the side of an upright cylinder at (cx, cf), rotated ang degrees about it."""
    o = m.side_box(-hw, hw, u0, u1, r0, r1, mat, c=c, group=group, detail=detail)
    m.transform(o, rotate=(0, 0, ang), move=(cx, cf, 0.0))
    return o


def build():
    m = Model("descent-device", category="drop-transport", bevel=0.003, cage=0.005)

    # Harness plate against the back, with shoulder strap stubs and a buckle.
    m.box(-0.035, -0.004, -0.22, 0.2, 0.3, "polymer", c=0.03)
    for s in (1, -1):
        strap = [(-0.02, 0.17), (0.0, 0.215), (0.05, 0.245), (0.11, 0.23), (0.13, 0.2), (0.115, 0.19), (0.05, 0.215), (0.005, 0.19), (-0.01, 0.15)]
        m.prism(strap, 0.055, "fabric", x=s * 0.09)
        m.box(-0.004, 0.012, -0.2, -0.12, 0.05, "fabric", x=s * 0.1, c=0.004)
        m.box(0.008, 0.016, -0.17, -0.15, 0.06, "alloy", x=s * 0.1, c=0.003)
    for u in (-0.15, -0.05, 0.05, 0.15):
        m.side_box(-0.0045, -0.0015, u - 0.02, u + 0.02, -0.13, 0.13, "fabric", detail=True)

    # Center spine: chamfered navy block, pale chevron and amber strip on its back.
    m.box(-0.12, -0.03, -0.24, 0.2, 0.11, "graphite", c=0.025)
    m.box(-0.13, -0.11, -0.2, 0.17, 0.07, "graphite", c=0.015)
    chevron = [(-0.032, 0.15), (0.032, 0.15), (0.032, -0.03), (0.0, -0.08), (-0.032, -0.03)]
    m.front_prism(chevron, -0.128, -0.136, "ivory")
    m.front_prism([(-0.006, 0.12), (0.006, 0.12), (0.006, -0.02), (-0.006, -0.02)], -0.135, -0.139, "glow_amber")
    m.front_prism([(-0.02, -0.14), (0.02, -0.14), (0.02, -0.18), (-0.02, -0.18)], -0.129, -0.134, "glow_amber")
    for u in (0.17, -0.11):
        for s in (1, -1):
            m.xcyl(-0.12, u, s * 0.035, s * 0.0368, 0.004, "steel", sides=6, detail=True)
    for s in (1, -1):
        m.side_box(-0.11, -0.04, -0.2, 0.17, s * 0.0545 - 0.0006, s * 0.0545 + 0.0008, "graphite", c=0.01, detail=True)

    # Cross braces tying the thrusters to the spine.
    for u0, u1 in ((0.08, 0.12), (-0.15, -0.11)):
        m.side_box(TF - 0.03, TF + 0.03, u0, u1, -TX, TX, "gunmetal", c=0.008)

    # Thrusters.
    for s in (1, -1):
        cx = s * TX
        m.vcyl(TF, -0.17, 0.15, TR, "graphite", sides=12, x=cx)
        m.vcyl(TF, 0.15, 0.175, TR - 0.006, "alloy", sides=12, x=cx)
        m.vcyl(TF, 0.175, 0.19, TR - 0.022, "gunmetal", sides=10, x=cx)
        m.vcyl(TF, -0.19, -0.165, TR + 0.004, "gunmetal", sides=12, x=cx)
        m.limb((cx, TF, -0.19), (cx, TF, -0.245), TR - 0.016, TR - 0.006, "polymer", sides=12)
        m.vcyl(TF, -0.2475, -0.244, TR - 0.014, "glow_amber", sides=12, x=cx)
        m.marker("thrust_l" if s < 0 else "thrust_r", f=TF, u=-0.25, x=cx)
        # Lime panels and amber lights facing back and outward (90 degrees = backward).
        ap = TR * math.cos(math.radians(15))
        for ang in ((30, 90) if s > 0 else (150, 90)):
            face_box(m, ang, ap - 0.004, ap + 0.003, 0.018, -0.12, 0.11, "lime", cx, TF, c=0.006)
        face_box(m, 90, ap + 0.002, ap + 0.006, 0.006, -0.16, -0.13, "glow_amber", cx, TF, c=0.0)
        face_box(m, 0 if s > 0 else 180, ap - 0.002, ap + 0.004, 0.012, -0.185, -0.17, "glow_amber", cx, TF, c=0.0)
        for ang in range(0, 360, 30):
            face_box(m, ang + 15, TR + 0.0035, TR + 0.0048, 0.002, -0.186, -0.169, "polymer", cx, TF, c=0.0, detail=True)
        for ang in (-30, -90, -150, 30, 90, 150):
            face_box(m, ang, ap - 0.0005, ap + 0.0012, 0.03, 0.135, 0.139, "polymer", cx, TF, c=0.0, detail=True)

    # Glide fins: folded against the outside of each thruster, hinged at the top.
    for s, name in ((1, "fin-right"), (-1, "fin-left")):
        fin = [(-0.055, 0.14), (-0.135, 0.14), (-0.15, 0.12), (-0.12, -0.08), (-0.1, -0.1), (-0.07, -0.06)]
        m.prism(fin, 0.012, "graphite", x=s * (TX + TR + 0.004), group=name)
        m.prism([(-0.13, 0.11), (-0.125, 0.0), (-0.115, 0.0), (-0.12, 0.11)], 0.004, "ivory", x=s * (TX + TR + 0.011), group=name)
        m.box(-0.122, -0.098, -0.095, -0.07, 0.016, "glow_amber", x=s * (TX + TR + 0.005), c=0.006, group=name)
        m.xcyl(-0.1, 0.13, s * (TX + TR - 0.006), s * (TX + TR + 0.012), 0.012, "alloy", sides=8, group=name)

    m.marker("mount", f=0.0, u=0.0)
    return m.finish(BUDGET, texture_size=1024)
