"""Arc grenade: electric charge. Concept: codex/concepts/v0.2/16-arc-grenade.png.

Upright canister: a heavy armored base and head (charcoal with moss panels and
amber lights) joined by four steel struts around a glowing violet coil column
wrapped in copper rings. The squared fuse on top carries the lever ("lever",
with an amber light strip) and the pull ring and pin ("pin"), each a separate
object. Origin at the center of the body.
"""

import math

import kit
from kit import Model

BUDGET = (500, 1500)

kit.MATERIALS.setdefault("charcoal", ("2e3238", 0.35, 0.55, None, "paint"))
kit.MATERIALS.setdefault("moss", ("6f7d43", 0.05, 0.6, None, "paint"))
kit.MATERIALS.setdefault("copper", ("b4683a", 0.9, 0.32, None, "metal"))
kit.MATERIALS.setdefault("alloy", ("9ca1a8", 0.6, 0.4, None, "metal"))
kit.MATERIALS.setdefault("glow_violet", ("7a5cf0", 0.0, 0.3, "8a6cff", "glow"))


def ngon(r, u, n=8, rot=22.5):
    return [(math.cos(math.radians(rot + 360 * i / n)) * r, -math.sin(math.radians(rot + 360 * i / n)) * r, u) for i in range(n)]


def face_box(m, ang, r0, r1, hw, u0, u1, mat, c=0.0015, group="body", detail=False):
    o = m.side_box(-hw, hw, u0, u1, r0, r1, mat, c=c, group=group, detail=detail)
    m.transform(o, rotate=(0, 0, ang))
    return o


def build():
    m = Model("arc-grenade", category="grenades")
    R = 0.031

    # Armored base.
    m.loft([ngon(R - 0.006, -0.06), ngon(R, -0.054), ngon(R, -0.03), ngon(R - 0.004, -0.024), ngon(R - 0.004, -0.02)], "charcoal")
    for k in range(4):
        ang = 90 * k
        face_box(m, ang, R * 0.92 - 0.002, R * 0.92 + 0.0015, 0.009, -0.05, -0.034, "polymer", c=0.002)
        face_box(m, ang, R * 0.92 + 0.0012, R * 0.92 + 0.0025, 0.006, -0.044, -0.04, "glow_amber", c=0.0)
        face_box(m, ang + 45, R - 0.003, R + 0.001, 0.004, -0.052, -0.03, "moss", c=0.0015)
    m.vcyl(0.0, -0.063, -0.058, 0.02, "gunmetal", sides=10)

    # Coil column: violet core, copper rings, steel struts.
    m.vcyl(0.0, -0.022, 0.024, 0.0185, "glow_violet", sides=12)
    for u in (-0.011, 0.0, 0.013):
        m.vcyl(0.0, u - 0.0018, u + 0.0018, 0.0235, "copper", sides=12)
    for k in range(4):
        ang = 90 * k + 45
        face_box(m, ang, 0.021, 0.028, 0.0028, -0.024, 0.026, "alloy", c=0.001)
        face_box(m, ang, 0.024, 0.0295, 0.004, -0.0005, 0.0035, "gunmetal", c=0.001)
    for k in range(8):
        face_box(m, 45 * k, 0.0176, 0.0192, 0.0007, -0.02, 0.022, "glow_white", c=0.0, detail=True)

    # Armored head with an amber band.
    m.loft([ngon(R - 0.004, 0.024), ngon(R, 0.03), ngon(R, 0.044), ngon(R - 0.008, 0.052)], "charcoal")
    m.vcyl(0.0, 0.0255, 0.0285, R + 0.0005, "glow_amber", sides=8)
    for k in range(4):
        face_box(m, 90 * k + 45, R - 0.003, R + 0.001, 0.005, 0.031, 0.045, "moss", c=0.0015)
        face_box(m, 90 * k, R * 0.92 - 0.001, R * 0.92 + 0.0012, 0.008, 0.033, 0.042, "gunmetal", c=0.002, detail=True)

    # Fuse block.
    m.vcyl(0.0, 0.05, 0.056, 0.016, "gunmetal", sides=10)
    m.box(-0.011, 0.011, 0.056, 0.072, 0.02, "charcoal", c=0.003)
    m.box(-0.008, 0.008, 0.07, 0.076, 0.014, "gunmetal", c=0.002)
    m.side_box(-0.012, 0.0, 0.06, 0.064, 0.0098, 0.0108, "glow_amber", c=0.0)
    m.screw(0.006, 0.066, 0.01, r=0.0013)

    # Lever with amber light strip.
    lever = [(0.004, 0.077), (0.014, 0.075), (0.028, 0.056), (0.04, 0.048), (0.042, -0.01), (0.037, -0.012), (0.035, 0.045),
             (0.024, 0.052), (0.01, 0.07), (0.004, 0.071)]
    m.prism(lever, 0.012, "gunmetal", group="lever")
    m.box(0.0405, 0.0435, -0.004, 0.03, 0.006, "glow_amber", c=0.001, group="lever")
    m.xcyl(0.012, 0.07, -0.009, 0.009, 0.004, "steel", sides=8, group="lever")
    m.xcyl(0.012, 0.07, -0.0095, 0.0095, 0.0025, "polymer", sides=6, group="lever", detail=True)

    # Pull ring and pin.
    m.xcyl(-0.002, 0.065, -0.016, 0.0, 0.0018, "steel", sides=6, group="pin")
    ring = m.tube(-0.0015, 0.0015, 0.0, 0.015, 0.012, "steel", sides=12, group="pin")
    m.transform(ring, rotate=(0, 0, 90))
    m.transform(ring, rotate=(0, 20, 0), move=(-0.017, -0.012, 0.06))

    m.marker("grip", f=0.0, u=0.0)
    return m.finish(BUDGET, texture_size=1024)
