"""Veil grenade: smoke canister. Concept: codex/concepts/v0.2/17-veil-grenade.png.

Tall charcoal canister with long vertical vent slots glowing amber from inside,
moss bands at the shoulder and above the heavy base, amber lights in the base,
and a slotted vent crown with an amber ring under the top cap. The lever
("lever", with a moss pivot) and the pull ring and pin ("pin") are separate
objects. Origin at the center of the body.
"""

import math

import kit
from kit import Model

BUDGET = (500, 1500)

kit.MATERIALS.setdefault("charcoal", ("2e3238", 0.35, 0.55, None, "paint"))
kit.MATERIALS.setdefault("moss", ("6f7d43", 0.05, 0.6, None, "paint"))
kit.MATERIALS.setdefault("glow_amber_deep", ("c06a12", 0.0, 0.3, "b8620e", "glow"))


def ngon(r, u, n=12, rot=15.0):
    return [(math.cos(math.radians(rot + 360 * i / n)) * r, -math.sin(math.radians(rot + 360 * i / n)) * r, u) for i in range(n)]


def face_box(m, ang, r0, r1, hw, u0, u1, mat, c=0.0015, group="body", detail=False):
    o = m.side_box(-hw, hw, u0, u1, r0, r1, mat, c=c, group=group, detail=detail)
    m.transform(o, rotate=(0, 0, ang))
    return o


def build():
    m = Model("veil-grenade", category="grenades")
    R = 0.028

    # Glowing inner canister seen through the slots.
    m.vcyl(0.0, -0.032, 0.03, R - 0.004, "glow_amber_deep", sides=12)
    # Slotted shell: twelve ribs leaving narrow vents between them.
    for k in range(12):
        face_box(m, 30 * k, R - 0.005, R, 0.0046, -0.032, 0.03, "charcoal", c=0.0)
    # One solid face (the lever side) as in the concept.
    face_box(m, 270, R - 0.004, R + 0.0012, 0.012, -0.033, 0.031, "charcoal", c=0.003)
    face_box(m, 270, R + 0.001, R + 0.0018, 0.009, -0.028, 0.026, "charcoal", detail=True)

    # Lower body, moss band, heavy base with amber lights.
    m.loft([ngon(R, -0.048), ngon(R, -0.032)], "charcoal")
    m.loft([ngon(R + 0.0012, -0.0425), ngon(R + 0.0012, -0.0385)], "moss")
    m.loft([ngon(R - 0.004, -0.066), ngon(R + 0.002, -0.061), ngon(R + 0.002, -0.05), ngon(R, -0.048)], "polymer")
    for k in range(4):
        face_box(m, 90 * k + 15, R - 0.001, R + 0.0035, 0.0045, -0.059, -0.054, "glow_amber", c=0.001)
        face_box(m, 90 * k + 60, R - 0.001, R + 0.0032, 0.005, -0.06, -0.051, "charcoal", c=0.0015)

    # Shoulder with moss panel, neck, slotted vent crown, top cap.
    m.loft([ngon(R, 0.03), ngon(R, 0.042), ngon(R - 0.007, 0.05)], "charcoal")
    face_box(m, 180, R - 0.003, R + 0.0012, 0.008, 0.031, 0.043, "moss", c=0.0015)
    face_box(m, 60, R - 0.003, R + 0.0012, 0.006, 0.033, 0.041, "moss", c=0.0015)
    m.vcyl(0.0, 0.05, 0.054, 0.019, "gunmetal", sides=12)
    m.vcyl(0.0, 0.054, 0.066, 0.0125, "glow_amber_deep", sides=10)
    for k in range(8):
        face_box(m, 45 * k, 0.011, 0.0165, 0.0026, 0.054, 0.066, "gunmetal", c=0.0)
    m.vcyl(0.0, 0.0555, 0.058, 0.0168, "glow_amber", sides=12)
    m.vcyl(0.0, 0.066, 0.072, 0.0165, "charcoal", sides=12)
    m.vcyl(0.0, 0.072, 0.074, 0.011, "gunmetal", sides=12)

    # Lever: guard frame around the crown and a long strap down the solid face.
    lever = [(0.006, 0.08), (0.02, 0.08), (0.03, 0.064), (0.036, 0.05), (0.036, -0.012), (0.031, -0.016), (0.0305, 0.044),
             (0.024, 0.062), (0.016, 0.073), (0.006, 0.073)]
    m.prism(lever, 0.013, "charcoal", group="lever")
    m.box(0.034, 0.037, -0.004, 0.036, 0.007, "polymer", c=0.0, group="lever", detail=True)
    m.xcyl(0.02, 0.064, -0.01, 0.01, 0.005, "moss", sides=8, group="lever")
    m.side_box(-0.02, 0.02, 0.074, 0.08, -0.004, 0.004, "charcoal", c=0.002, group="lever")

    # Pull ring and pin.
    m.xcyl(0.016, 0.06, -0.018, 0.0, 0.0017, "steel", sides=6, group="pin")
    ring = m.tube(-0.0015, 0.0015, 0.0, 0.014, 0.011, "steel", sides=12, group="pin")
    m.transform(ring, rotate=(0, 0, 90))
    m.transform(ring, rotate=(0, 20, 0), move=(-0.02, 0.006, 0.052))

    m.marker("grip", f=0.0, u=0.0)
    return m.finish(BUDGET, texture_size=1024)
