"""Mule: colony buggy, reliable and loud. Concept: codex/concepts/v0.2/21-mule.png.

Origin at the center of the wheelbase on the ground; faces forward (-Y in Blender).
Open two-row cockpit under a tubular roll cage with an amber light bar, graphite
chassis with ivory armor panels and lime camo, yellow coilovers, knobby tires,
winch bumper, rear cargo rack with a crate and a fuel tank, red tail lights.
Wheels are separate objects (wheel-fl/fr/rl/rr) with their origin at the hub.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vkit import (bolt_f, bolt_u, bolt_x, octo, origins, plate_u, plate_x, torus,  # noqa: E402
                   vents_u, wheel)
import kit  # noqa: E402
from kit import Model  # noqa: E402

kit.MATERIALS.setdefault("bone", ("bdb39b", 0.1, 0.55, None, "paint"))   # khaki-ivory armor (concept)

BUDGET = (4000, 8000)

WB = 1.36      # half wheelbase
TR = 0.94      # half track
WR = 0.47      # wheel radius
WW = 0.38      # tire width


def coilover(m, top, bottom, r=0.065):
    """Yellow spring over a dark damper body, between two (x, f, u) points."""
    m.limb(top, bottom, 0.03, 0.03, "gunmetal", sides=6)
    t = [top[i] + (bottom[i] - top[i]) * 0.12 for i in range(3)]
    b = [top[i] + (bottom[i] - top[i]) * 0.8 for i in range(3)]
    m.limb(t, b, r, r, "spring", sides=8)
    for k in range(7):     # baked coils
        p0 = [t[i] + (b[i] - t[i]) * (k + 0.3) / 7 for i in range(3)]
        p1 = [t[i] + (b[i] - t[i]) * (k + 0.7) / 7 for i in range(3)]
        m.limb(p0, p1, r + 0.012, r + 0.012, "spring", sides=8, detail=True)


def seat(m, x, f, u, back_h=0.62):
    """Bucket seat: hip point at (x, f, u)."""
    m.box(f - 0.24, f + 0.2, u - 0.1, u + 0.02, 0.48, "seat", x=x, c=0.04)
    for s in (-1, 1):
        m.box(f - 0.22, f + 0.18, u - 0.02, u + 0.07, 0.07, "seat", x=x + s * 0.22, c=0.03)
    back = m.box(f - 0.32, f - 0.18, u - 0.05, u + back_h, 0.48, "seat", x=x, c=0.05)
    m.transform(back, rotate=(-12, 0, 0), pivot=(x, f - 0.25, u))
    for s in (-1, 1):
        wing = m.box(f - 0.3, f - 0.1, u + 0.1, u + back_h - 0.08, 0.08, "seat", x=x + s * 0.24, c=0.03)
        m.transform(wing, rotate=(-12, 0, 0), pivot=(x, f - 0.25, u))
    # Baked: lime stripes and harness straps.
    for s in (-1, 1):
        st = m.box(f - 0.2, f - 0.17, u + 0.05, u + back_h - 0.05, 0.05, "lime", x=x + s * 0.11, c=0.0, detail=True)
        m.transform(st, rotate=(-12, 0, 0), pivot=(x, f - 0.25, u))
    m.box(f - 0.22, f + 0.18, u + 0.02, u + 0.032, 0.3, "fabric", x=x, c=0.0, detail=True)


def build():
    m = Model("mule", category="vehicles", bevel=0.012, cage=0.025)

    # ---------------------------------------------------------- wheels
    for name, f, x in (("wheel-fl", WB, -TR), ("wheel-fr", WB, TR), ("wheel-rl", -WB, -TR), ("wheel-rr", -WB, TR)):
        wheel(m, f, WR, x, WR, WW, name, sides=16, lugs=16, lug_h=0.035)

    # ---------------------------------------------------------- chassis
    # Floor pan / skid tub.
    m.top_prism([(0.6, 1.95), (-0.6, 1.95), (-0.66, 1.7), (-0.66, -1.75), (-0.58, -1.95), (0.58, -1.95), (0.66, -1.75), (0.66, 1.7)],
                0.38, 0.5, "gunmetal")
    # Rocker sills with an ivory kick panel.
    for s in (-1, 1):
        m.side_box(-1.0, 0.85, 0.42, 0.74, s * 0.6, s * 0.76, "graphite", c=0.05)
        m.prism([(0.82, 0.6), (0.82, 0.98), (0.55, 1.0), (0.15, 0.78), (0.15, 0.6)], 0.06, "bone", x=s * 0.77)
        m.prism([(-0.85, 0.6), (-0.85, 1.02), (-0.55, 1.02), (-0.4, 0.78), (-0.4, 0.6)], 0.06, "graphite", x=s * 0.75)
        # Nerf bar.
        m.limb((s * 0.82, 0.62, 0.62), (s * 0.84, 0.45, 0.55), 0.035, 0.035, "bronze", sides=6)
        m.limb((s * 0.84, 0.45, 0.55), (s * 0.84, -0.75, 0.55), 0.035, 0.035, "bronze", sides=6)
        m.limb((s * 0.84, -0.75, 0.55), (s * 0.8, -0.9, 0.62), 0.035, 0.035, "bronze", sides=6)
        plate_x(m, [(0.78, 0.64), (0.78, 0.94), (0.56, 0.95), (0.3, 0.8), (0.3, 0.64)], 0.8, "lime", mirror=False) if s > 0 else None
        for f, u in ((0.75, 0.66), (0.75, 0.92), (0.22, 0.66)):
            bolt_x(m, f, u, s * 0.8)
        for f in (-0.9, -0.3, 0.3, 0.75):
            bolt_x(m, f, 0.47, s * 0.76)
    plate_x(m, [(0.7, 0.66), (0.7, 0.8), (0.5, 0.9), (0.45, 0.66)], 0.8, "lime", mirror=False)

    # ---------------------------------------------------------- nose
    # Hood: lofted graphite block, ivory cheeks, dark vented center.
    rings = [octo(2.1, 0.46, 0.5, 0.8, 0.08, 0.1), octo(1.98, 0.6, 0.46, 0.95, 0.1, 0.14),
             octo(1.5, 0.66, 0.46, 1.04, 0.1, 0.16), octo(0.86, 0.66, 0.46, 1.1, 0.1, 0.14)]
    m.loft(rings, "graphite", name="hood")
    for s in (-1, 1):
        cheek = [(s * 0.28, 2.02, 0.96), (s * 0.6, 1.96, 0.9), (s * 0.66, 1.5, 0.92), (s * 0.66, 0.9, 0.98),
                 (s * 0.5, 0.9, 1.12), (s * 0.36, 1.5, 1.06)]
        ring0 = [(px, pf, pu) for px, pf, pu in cheek]
        ring1 = [(px, pf, pu + 0.04) for px, pf, pu in cheek]
        m.loft([ring0, ring1], "bone", name="cheek")
    # Hood scoop and vents.
    m.top_prism([(-0.26, 1.82), (0.26, 1.82), (0.3, 1.0), (-0.3, 1.0)], 1.0, 1.12, "navy")
    vents_u(m, -0.22, 0.22, 1.1, 1.7, 1.12, 9)
    # Grille fascia.
    m.front_prism([(-0.4, 0.52), (0.4, 0.52), (0.46, 0.66), (0.4, 0.8), (-0.4, 0.8), (-0.46, 0.66)], 2.02, 2.16, "navy")
    for i in range(5):
        u = 0.56 + i * 0.045
        m.front_prism([(-0.34, u), (0.34, u), (0.34, u + 0.018), (-0.34, u + 0.018)], 2.14, 2.17, "polymer", detail=True)
    # Headlights: angled amber strips in dark housings at the hood corners.
    for s in (-1, 1):
        h = m.box(1.92, 2.08, 0.84, 0.95, 0.34, "polymer", x=s * 0.44, c=0.03)
        m.transform(h, rotate=(0, s * 10, 0), pivot=(s * 0.44, 2.0, 0.9))
        g = m.box(2.06, 2.1, 0.86, 0.92, 0.3, "glow_amber", x=s * 0.44, c=0.01)
        m.transform(g, rotate=(0, s * 10, 0), pivot=(s * 0.44, 2.0, 0.9))
    # Bumper with winch, tow eye and square fog lamps.
    m.box(2.06, 2.3, 0.42, 0.66, 1.24, "graphite", c=0.06)
    m.box(2.0, 2.24, 0.3, 0.44, 0.9, "gunmetal", c=0.05)                 # skid plate
    m.xcyl(2.27, 0.54, -0.22, 0.22, 0.075, "steel", sides=10)             # winch drum
    m.box(2.24, 2.34, 0.47, 0.6, 0.16, "gunmetal", c=0.02)                # fairlead
    torus(m, (0.0, 2.38, 0.47), "x", 0.045, 0.014, "steel", n=8, k=4)     # hook
    for s in (-1, 1):
        m.box(2.26, 2.34, 0.46, 0.62, 0.18, "polymer", x=s * 0.48, c=0.02)
        m.box(2.33, 2.36, 0.48, 0.6, 0.14, "glow_amber", x=s * 0.48, c=0.01)
        m.limb((s * 0.62, 2.18, 0.5), (s * 0.7, 2.0, 0.72), 0.03, 0.03, "bronze", sides=6)
        bolt_f(m, s * 0.5, 0.45, 2.3)
        bolt_f(m, s * 0.2, 0.45, 2.3)
    # Dashboard and steering.
    m.box(0.6, 0.9, 0.85, 1.12, 1.2, "navy", c=0.05)
    m.box(0.55, 0.62, 1.04, 1.1, 0.4, "glow_amber", x=-0.36, c=0.01)     # gauge strip
    m.limb((-0.38, 0.75, 1.02), (-0.38, 0.5, 1.12), 0.025, 0.025, "gunmetal", sides=6)
    wheel_ring = torus(m, (-0.38, 0.47, 1.14), "f", 0.17, 0.02, "polymer", n=12, k=4)
    m.transform(wheel_ring, rotate=(-25, 0, 0), pivot=(-0.38, 0.47, 1.14))

    # ---------------------------------------------------------- fenders
    for fc in (WB, -WB):
        for s in (-1, 1):
            x = s * TR
            # Arched graphite fender shell over the wheel.
            arc = []
            for k in range(7):
                a = 3.14159 * (0.08 + 0.84 * k / 6)
                arc.append((fc + 0.58 * math.cos(a), WR + 0.58 * math.sin(a)))
            top = [(fc - 0.62, WR + 0.16), (fc - 0.6, WR + 0.6), (fc - 0.4, WR + 0.68), (fc + 0.45, WR + 0.66), (fc + 0.64, WR + 0.48), (fc + 0.64, WR + 0.2)]
            prof = top[::-1] + arc[::-1]
            m.prism(prof[::-1], 0.42, "graphite", x=x * 0.97)
            # Ivory armor slab on top, lime splash, bolts.
            xin, xout = x * 0.97 - s * 0.23, x * 0.97 + s * 0.25
            slab = []
            for f, ub, ut in ((fc - 0.68, WR + 0.5, WR + 0.6), (fc - 0.46, WR + 0.58, WR + 0.73),
                              (fc + 0.46, WR + 0.58, WR + 0.71), (fc + 0.68, WR + 0.42, WR + 0.54)):
                slab.append([(xin, f, ub), (xout, f, ub), (xout, f, ut - 0.07), (xout - s * 0.07, f, ut), (xin, f, ut)])
            m.loft(slab, "bone", name="slab")
            plate_x(m, [(fc - 0.2, WR + 0.62), (fc + 0.05, WR + 0.62), (fc + 0.15, WR + 0.69), (fc - 0.1, WR + 0.7)], abs(x * 0.97) + 0.23, "lime", mirror=False) if s > 0 else None
            for f in (fc - 0.5, fc - 0.1, fc + 0.3):
                bolt_x(m, f, WR + 0.63, x * 0.97 + s * 0.23)
            plate_u(m, [(x * 0.97 - 0.18, fc - 0.35), (x * 0.97 + 0.18, fc - 0.35), (x * 0.97 + 0.18, fc + 0.35), (x * 0.97 - 0.18, fc + 0.35)], WR + 0.71, "bone", depth=0.005)

    # ---------------------------------------------------------- suspension
    for s in (-1, 1):
        # Front double wishbones.
        for u in (0.38, 0.62):
            m.limb((s * 0.6, WB - 0.25, u), (s * 0.78, WB, u + 0.02), 0.03, 0.025, "gunmetal", sides=6)
            m.limb((s * 0.6, WB + 0.25, u), (s * 0.78, WB, u + 0.02), 0.03, 0.025, "gunmetal", sides=6)
        m.box(WB - 0.1, WB + 0.1, 0.3, 0.68, 0.08, "gunmetal", x=s * 0.78, c=0.03)       # knuckle
        coilover(m, (s * 0.52, WB - 0.1, 1.05), (s * 0.76, WB - 0.02, 0.42))
        # Rear trailing arms.
        m.limb((s * 0.62, -0.75, 0.48), (s * 0.78, -WB, 0.44), 0.045, 0.035, "gunmetal", sides=6)
        m.limb((s * 0.62, -0.9, 0.7), (s * 0.78, -WB, 0.62), 0.03, 0.03, "gunmetal", sides=6)
        m.box(-WB - 0.1, -WB + 0.1, 0.3, 0.68, 0.08, "gunmetal", x=s * 0.78, c=0.03)
        coilover(m, (s * 0.55, -WB + 0.15, 1.12), (s * 0.77, -WB + 0.05, 0.44))
    # Axle tubes (drive shafts).
    for f in (WB, -WB):
        m.xcyl(f, WR, -0.78, 0.78, 0.035, "gunmetal", sides=6)

    # ---------------------------------------------------------- cockpit
    seat(m, -0.36, 0.08, 0.66)
    seat(m, 0.36, 0.08, 0.66)
    seat(m, -0.36, -0.82, 0.86)
    seat(m, 0.36, -0.82, 0.86)
    m.box(-1.05, -0.55, 0.5, 0.76, 1.2, "graphite", c=0.04)              # rear seat riser
    m.box(-0.25, 0.4, 0.5, 0.78, 0.22, "navy", c=0.04)                    # center tunnel
    m.box(-0.1, 0.05, 0.78, 0.92, 0.08, "gunmetal", c=0.02)               # shifter
    plate_u(m, [(-0.08, 0.0), (0.08, 0.0), (0.08, 0.3), (-0.08, 0.3)], 0.78, "polymer")

    # ---------------------------------------------------------- roll cage
    R = 0.038
    cage = "gunmetal"
    for s in (-1, 1):
        m.limb((s * 0.64, 0.86, 1.08), (s * 0.6, 0.38, 1.9), R, R, cage, sides=6)            # A-pillar
        m.limb((s * 0.6, 0.38, 1.9), (s * 0.6, -0.4, 1.96), R, R, cage, sides=6)              # roof rail
        m.limb((s * 0.68, -0.4, 0.7), (s * 0.6, -0.4, 1.96), R, R, cage, sides=6)             # B hoop
        m.limb((s * 0.6, -0.4, 1.96), (s * 0.64, -1.25, 1.62), R, R, cage, sides=6)           # rear rail
        m.limb((s * 0.64, -1.25, 1.62), (s * 0.66, -1.25, 1.0), R, R, cage, sides=6)          # C post
        m.limb((s * 0.64, -1.25, 1.62), (s * 0.7, -2.0, 1.42), R, R, cage, sides=6)           # rack rail
        m.limb((s * 0.7, -2.0, 1.42), (s * 0.7, -2.0, 0.95), R, R, cage, sides=6)
        # Bronze accent sleeves on the A-pillars (concept detail).
        m.limb((s * 0.635, 0.78, 1.21), (s * 0.615, 0.52, 1.66), R + 0.008, R + 0.008, "spring", sides=6)
        m.limb((s * 0.66, -0.4, 1.0), (s * 0.64, -0.4, 1.4), R + 0.008, R + 0.008, "spring", sides=6)
    m.limb((-0.6, 0.38, 1.9), (0.6, 0.38, 1.9), R, R, cage, sides=6)
    m.limb((-0.6, -0.4, 1.96), (0.6, -0.4, 1.96), R, R, cage, sides=6)
    m.limb((-0.64, -0.4, 1.0), (0.6, -0.4, 1.85), 0.03, 0.03, cage, sides=6)                 # X brace
    m.limb((-0.66, -1.25, 1.62), (0.66, -1.25, 1.62), R, R, cage, sides=6)
    m.limb((-0.7, -2.0, 1.42), (0.7, -2.0, 1.42), R, R, cage, sides=6)
    m.limb((-0.6, -0.02, 1.93), (0.6, -0.02, 1.93), 0.028, 0.028, cage, sides=6)
    # Light bar on the front roof bar.
    m.box(0.3, 0.46, 1.93, 2.05, 1.1, "polymer", c=0.025)
    m.box(0.45, 0.47, 1.95, 2.03, 1.02, "glow_amber", c=0.0)
    for i in range(5):
        m.box(0.46, 0.48, 1.945, 2.035, 0.02, "polymer", x=-0.4 + i * 0.2, c=0.0, detail=True)
    for s in (-1, 1):
        m.box(0.34, 0.44, 1.88, 1.95, 0.05, "gunmetal", x=s * 0.45, c=0.0)

    # ---------------------------------------------------------- rear bed
    m.top_prism([(-0.66, -1.05), (0.66, -1.05), (0.66, -2.0), (-0.66, -2.0)], 0.5, 0.98, "graphite")
    m.top_prism([(-0.62, -1.15), (0.62, -1.15), (0.62, -1.95), (-0.62, -1.95)], 0.98, 1.02, "gunmetal")    # deck plate
    for i in range(5):
        plate_u(m, [(-0.6, -1.2 - i * 0.15), (0.6, -1.2 - i * 0.15), (0.6, -1.24 - i * 0.15), (-0.6, -1.24 - i * 0.15)], 1.02, "steel", depth=0.008)
    # Olive cargo case and dark fuel cell.
    m.box(-1.75, -1.2, 1.02, 1.36, 0.52, "olive", x=-0.28, c=0.03)
    m.box(-1.75, -1.2, 1.36, 1.39, 0.54, "polymer", x=-0.28, c=0.01)
    plate_x(m, [(-1.65, 1.1), (-1.3, 1.1), (-1.3, 1.28), (-1.65, 1.28)], 0.02, "olive", mirror=False)
    m.box(-1.55, -1.4, 1.39, 1.42, 0.2, "steel", x=-0.28, c=0.0)
    m.xcyl(-1.6, 1.22, 0.04, 0.62, 0.18, "navy", sides=12)
    m.xcyl(-1.6, 1.22, 0.62, 0.66, 0.12, "gunmetal", sides=8)
    for x in (0.15, 0.5):
        m.xcyl(-1.6, 1.22, x, x + 0.04, 0.19, "polymer", sides=12, detail=True)
    # Rear fascia: bumper, tail lights, tow hitch.
    m.box(-2.12, -1.94, 0.45, 0.72, 1.3, "graphite", c=0.05)
    m.box(-2.16, -2.08, 0.5, 0.62, 0.14, "gunmetal", c=0.02)
    for s in (-1, 1):
        m.box(-2.05, -1.95, 0.95, 1.25, 0.12, "polymer", x=s * 0.62, c=0.02)
        m.box(-2.07, -2.04, 0.98, 1.22, 0.08, "glow_red", x=s * 0.62, c=0.01)
        m.box(-2.14, -2.11, 0.55, 0.65, 0.12, "glow_amber", x=s * 0.45, c=0.01)
    m.box(-2.0, -1.97, 0.55, 0.68, 0.3, "steel", c=0.0, detail=True)                       # plate
    m.box(-1.98, -1.94, 0.6, 0.66, 0.24, "lime", c=0.0, detail=True)

    # ---------------------------------------------------------- baked detail
    for s in (-1, 1):
        for f in (1.9, 1.5, 1.0):
            bolt_x(m, f, 0.52, s * 0.66)
        plate_x(m, [(1.9, 0.5), (1.4, 0.5), (1.4, 0.7), (1.9, 0.62)], 0.66, "navy")
        for f in (-1.2, -1.6, -1.9):
            bolt_x(m, f, 0.94, s * 0.66)
    for x in (-0.5, 0.5):
        for f in (1.6, 1.2):
            bolt_u(m, x, f, 1.0)

    m.marker("seat", f=0.0, u=1.45, x=-0.36)            # driver eye
    m.marker("seat_passenger", f=0.0, u=1.45, x=0.36)
    m.marker("seat_rear_l", f=-0.9, u=1.65, x=-0.36)
    m.marker("seat_rear_r", f=-0.9, u=1.65, x=0.36)
    m.marker("exit", f=0.0, u=0.1, x=-1.6)
    m.marker("exit_r", f=0.0, u=0.1, x=1.6)
    m.marker("tow", f=-2.16, u=0.56)
    pivots = {"wheel-fl": (-TR, WB, WR), "wheel-fr": (TR, WB, WR), "wheel-rl": (-TR, -WB, WR), "wheel-rr": (TR, -WB, WR)}
    return m.finish(BUDGET, texture_size=2048, before_export=origins("mule", pivots))
