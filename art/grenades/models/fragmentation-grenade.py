"""Fragmentation grenade. Concept: codex/concepts/v0.2/15-fragmentation-grenade.png.

Round body built from faceted charcoal armor plates (some moss green) over a
glowing amber core that shows through the seams, a belt ring, and a squared
fuse block with an amber window on top. The spoon lever ("lever") and the pull
ring with its pin ("pin") are separate objects. Origin at the center of the body.
"""

import math

import kit
from kit import Model

BUDGET = (500, 1500)

kit.MATERIALS.setdefault("charcoal", ("2e3238", 0.35, 0.55, None, "paint"))    # grenade armor
kit.MATERIALS.setdefault("moss", ("6f7d43", 0.05, 0.6, None, "paint"))          # muted green plates
kit.MATERIALS.setdefault("glow_amber_deep", ("c06a12", 0.0, 0.3, "b8620e", "glow"))

R = 0.034


def sp(r, lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return (math.cos(la) * math.cos(lo) * r, -math.cos(la) * math.sin(lo) * r, math.sin(la) * r)


def plate(m, lat0, lat1, lon0, lon1, mat):
    """Thick spherical plate: chamfered outer face, flat 6-point outline."""
    def ring(r, inset):
        a0, a1 = lat0 + inset, lat1 - inset
        b0, b1 = lon0 + inset, lon1 - inset
        bm = (b0 + b1) / 2
        return [sp(r, a0, b0), sp(r, a0, bm), sp(r, a0, b1), sp(r, a1, b1), sp(r, a1, bm), sp(r, a1, b0)]
    m.loft([ring(R - 0.006, 0), ring(R, 0), ring(R + 0.0012, 3.5)], mat)


def build():
    m = Model("fragmentation-grenade", category="grenades")

    # Glowing core seen through the seams.
    m.sphere(0.0, 0.0, R - 0.004, "glow_amber_deep", segments=8, rings=5)
    green = {(0, 1), (2, 4), (1, 3), (3, 0)}
    rows = ((6, 38), (42, 64), (-38, -6), (-72, -42))
    for ri, (a0, a1) in enumerate(rows):
        for k in range(6):
            lon0 = k * 60 + (30 if ri % 2 else 0) + 3
            mat = "moss" if (ri, k) in green else "charcoal"
            plate(m, a0, a1, lon0, lon0 + 54, mat)
            # Panel cuts and rivets on the plates (baked).
            mid_lat, mid_lon = (a0 + a1) / 2, lon0 + 27
            o = m.side_box(-0.0016, 0.0016, -0.0016, 0.0016, R - 0.004, R + 0.0006, "gunmetal", c=0.0006, detail=True)
            m.transform(o, rotate=(0, mid_lat, 0))
            m.transform(o, rotate=(0, 0, mid_lon))
    # Equator belt with lugs.
    m.vcyl(0.0, -0.0035, 0.0035, R + 0.0008, "gunmetal", sides=16)
    for k in range(6):
        o = m.side_box(-0.004, 0.004, -0.005, 0.005, R - 0.002, R + 0.0035, "polymer", c=0.0)
        m.transform(o, rotate=(0, 0, 60 * k + 30))
    # Bottom cap.
    m.vcyl(0.0, -R - 0.002, -R + 0.006, 0.012, "gunmetal", sides=10)

    # Fuse: collar, squared block with amber windows.
    m.vcyl(0.0, R - 0.006, R + 0.004, 0.016, "gunmetal", sides=12)
    m.vcyl(0.0, R + 0.004, R + 0.008, 0.018, "polymer", sides=12)
    m.box(-0.013, 0.013, R + 0.008, R + 0.03, 0.024, "charcoal", c=0.004)
    m.box(-0.014, 0.005, R + 0.026, R + 0.034, 0.02, "charcoal", c=0.003)
    for s in (1, -1):
        m.side_box(-0.006, 0.004, R + 0.014, R + 0.024, s * 0.0115, s * 0.0128, "glow_amber", c=0.0012)
    m.side_box(0.0128, 0.0138, R + 0.014, R + 0.024, -0.004, 0.004, "glow_amber", c=0.001)
    m.plate(-0.012, 0.012, R + 0.009, R + 0.011, 0.012, "gunmetal", c=0.0)
    m.screw(-0.009, R + 0.028, 0.012, r=0.0014)
    m.screw(0.009, R + 0.028, 0.012, r=0.0014)

    # Spoon lever down the front of the body.
    lever = [(0.006, R + 0.034), (0.016, R + 0.032), (0.03, R + 0.008), (0.042, 0.004), (0.04, -0.03), (0.034, -0.032),
             (0.033, 0.002), (0.024, R + 0.004), (0.012, R + 0.024), (0.004, R + 0.026)]
    m.prism(lever, 0.012, "moss", group="lever")
    m.prism([(0.0405, -0.026), (0.0418, -0.0), (0.0405, 0.0)], 0.008, "charcoal", group="lever")
    m.xcyl(0.012, R + 0.028, -0.009, 0.009, 0.0045, "steel", sides=8, group="lever")
    m.box(0.039, 0.0424, -0.022, -0.008, 0.006, "polymer", c=0.0, group="lever", detail=True)

    # Pull ring and pin on the left side.
    m.xcyl(0.0, R + 0.019, -0.016, 0.0, 0.0018, "steel", sides=6, group="pin")
    ring = m.tube(-0.0015, 0.0015, 0.0, 0.016, 0.0128, "steel", sides=12, group="pin")
    m.transform(ring, rotate=(0, 0, 90))
    m.transform(ring, rotate=(0, -25, 0), move=(-0.018, 0.012, R + 0.012))

    m.marker("grip", f=0.0, u=0.0)
    return m.finish(BUDGET, texture_size=1024)
