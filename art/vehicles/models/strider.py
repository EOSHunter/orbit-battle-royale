"""Strider: heavy six-wheeled survey rover, slow and durable. Concept: codex/concepts/v0.2/23-strider.png.

Origin at the center of the wheelbase on the ground; faces forward (-Y in Blender).
Armored cab with a wraparound windshield and a sensor turret, ivory and lime armor
over a graphite frame, a tall survey module with a radome, dish and antennas, a
rear cargo deck with containers and railings, ladders, tow shackles, amber lights.
Wheels are separate objects (wheel-fl/fr/ml/mr/rl/rr) with their origin at the hub.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vkit import (bolt_f, bolt_u, bolt_x, lerp, octo, origins, panel, plate_f,  # noqa: E402
                   plate_u, plate_x, torus, vents_x, wheel)
from kit import Model  # noqa: E402

BUDGET = (4000, 8000)

WR = 0.7       # wheel radius
WW = 0.56      # tire width
TR = 1.3       # half track
AXLES = {"f": 2.3, "m": 0.15, "r": -2.0}


def build():
    m = Model("strider", category="vehicles", bevel=0.014, cage=0.03)

    # ---------------------------------------------------------- wheels
    for ax, f in AXLES.items():
        for side, x in (("l", -TR), ("r", TR)):
            wheel(m, f, WR, x, WR, WW, f"wheel-{ax}{side}", sides=14, lugs=12, lug_h=0.04, lug_c=0.0,
                  hub_ratio=0.58, side_lugs=True)

    # ---------------------------------------------------------- frame and running gear
    m.top_prism([(-0.95, 3.2), (0.95, 3.2), (1.0, 3.0), (1.0, -3.15), (0.9, -3.3), (-0.9, -3.3), (-1.0, -3.15), (-1.0, 3.0)],
                0.62, 1.2, "graphite")
    for ax, f in AXLES.items():
        for s in (-1, 1):
            m.limb((s * 0.9, f + 0.5, 0.82), (s * 1.0, f, WR), 0.07, 0.06, "gunmetal", sides=6)        # trailing arm
            m.limb((s * 0.85, f - 0.35, 1.3), (s * 1.0, f - 0.05, WR + 0.1), 0.05, 0.05, "gunmetal", sides=6)
            m.limb(lerp((s * 0.85, f - 0.35, 1.3), (s * 1.0, f - 0.05, WR + 0.1), 0.15),
                   lerp((s * 0.85, f - 0.35, 1.3), (s * 1.0, f - 0.05, WR + 0.1), 0.75), 0.085, 0.085, "spring", sides=8)
            m.box(f - 0.16, f + 0.16, WR - 0.16, WR + 0.16, 0.14, "gunmetal", x=s * 0.97, c=0.04)         # hub carrier
        m.xcyl(f, WR, -0.95, 0.95, 0.06, "gunmetal", sides=6)
    # Side skirts / fender shelf with amber markers and lime panels.
    for s in (-1, 1):
        prof = [(-3.25, 1.35), (3.15, 1.35), (3.3, 1.5), (3.2, 1.66), (-3.2, 1.66), (-3.3, 1.55)]
        m.prism(prof, 0.66, "graphite", x=s * 1.32)
        m.prism([(2.95, 1.42), (3.2, 1.42), (3.25, 1.5), (3.2, 1.6), (2.95, 1.6)], 0.69, "navy", x=s * 1.32)
        for f in (2.95, 0.85, -0.85, -3.0):
            m.side_box(f - 0.14, f + 0.14, 1.44, 1.54, s * 1.6, s * 1.67, "glow_amber", c=0.01)
        for f0, f1 in ((1.0, 1.55), (-0.65, -0.1)):
            m.side_box(f0, f1, 1.4, 1.62, s * 1.64, s * 1.665, "lime", c=0.01)
        for f in (-3.1, -2.6, -1.5, -1.0, 1.7, 3.1):
            bolt_x(m, f, 1.5, s * 1.65, r=0.02)
        plate_u(m, [(s * 1.05, -3.1), (s * 1.6, -3.1), (s * 1.6, 3.1), (s * 1.05, 3.1)], 1.66, "gunmetal", depth=0.006)
        vents_x(m, -2.6, -1.6, 0.75, 1.1, 1.0, 8)

    # ---------------------------------------------------------- cab
    cab = [octo(3.3, 1.02, 1.4, 2.1, 0.1, 0.3), octo(2.75, 1.15, 1.4, 2.78, 0.1, 0.38),
           octo(1.0, 1.15, 1.4, 2.82, 0.1, 0.32)]
    m.loft(cab, "graphite", name="cab")
    # Ivory armor on the cab flanks, with a lime chevron and a navy window frame.
    for s in (-1, 1):
        m.prism([(1.05, 1.62), (2.55, 1.62), (2.95, 1.9), (2.75, 2.45), (2.2, 2.45), (1.6, 2.1), (1.05, 2.1)], 0.05, "ivory", x=s * 1.17)
        m.prism([(1.05, 2.1), (1.6, 2.1), (2.2, 2.45), (1.75, 2.45), (1.3, 2.15), (1.05, 2.15)], 0.055, "lime", x=s * 1.17)
        m.prism([(1.15, 2.2), (2.6, 2.2), (2.7, 2.62), (1.15, 2.62)], 0.03, "tinted_glass", x=s * 1.16)  # side window
        m.prism([(1.62, 1.6), (2.2, 1.6), (2.25, 2.15), (1.62, 2.15)], 0.04, "navy", x=s * 1.18)      # door
        plate_x(m, [(1.7, 1.7), (2.1, 1.7), (2.1, 2.0), (1.7, 2.0)], 1.2, "navy", mirror=False) if s > 0 else None
        for f, u in ((1.1, 1.67), (2.45, 1.67), (1.1, 2.05), (2.0, 1.67)):
            bolt_x(m, f, u, s * 1.195)
    # Windshield: three panes on the sloped front, framed.
    a0, a1 = (0.66, 3.31, 2.06), (0.8, 2.78, 2.76)
    panel(m, [(-a0[0], a0[1], a0[2]), (a0[0], a0[1], a0[2]), (a1[0], a1[1], a1[2]), (-a1[0], a1[1], a1[2])], 0.04, "tinted_glass")
    for s in (-1, 1):
        panel(m, [(s * 0.9, 3.25, 1.98), (s * 0.97, 3.07, 1.9), (s * 1.09, 2.78, 2.42), (s * 0.92, 2.8, 2.6)], 0.04, "tinted_glass")
    m.limb((0.0, 3.33, 2.05), (0.0, 2.8, 2.82), 0.035, 0.035, "polymer", sides=6)
    # Roll guard / brush bars over the windshield.
    for s in (-1, 1):
        m.limb((s * 1.05, 3.45, 1.75), (s * 0.95, 3.0, 2.82), 0.04, 0.04, "polymer", sides=6)
    m.limb((-0.95, 3.0, 2.84), (0.95, 3.0, 2.84), 0.04, 0.04, "polymer", sides=6)
    m.box(2.92, 3.08, 2.82, 2.92, 1.4, "polymer", c=0.03)                     # light bar
    m.box(3.06, 3.09, 2.84, 2.9, 1.3, "glow_amber", c=0.0)
    # Nose: bumper, grille, headlights, tow shackles.
    m.front_prism([(-1.05, 0.95), (1.05, 0.95), (1.12, 1.15), (1.05, 1.5), (-1.05, 1.5), (-1.12, 1.15)], 3.2, 3.5, "navy")
    m.front_prism([(-0.6, 1.05), (0.6, 1.05), (0.6, 1.42), (-0.6, 1.42)], 3.48, 3.52, "polymer")
    for i in range(6):
        plate_f(m, [(-0.55, 1.08 + i * 0.055), (0.55, 1.08 + i * 0.055), (0.55, 1.1 + i * 0.055), (-0.55, 1.1 + i * 0.055)], 3.52, "gunmetal")
    for s in (-1, 1):
        m.box(3.38, 3.56, 1.62, 1.82, 0.42, "polymer", x=s * 0.78, c=0.03)
        m.box(3.55, 3.58, 1.66, 1.78, 0.34, "glow_amber", x=s * 0.78, c=0.01)
        m.box(3.45, 3.54, 1.15, 1.32, 0.26, "polymer", x=s * 0.88, c=0.02)
        m.box(3.53, 3.56, 1.18, 1.29, 0.2, "glow_amber", x=s * 0.88, c=0.01)
        torus(m, (s * 0.42, 3.62, 0.98), "x", 0.09, 0.025, "spring", n=8, k=4)          # shackle
        m.box(3.45, 3.6, 0.98, 1.12, 0.14, "gunmetal", x=s * 0.42, c=0.02)
        m.limb((s * 1.1, 3.5, 0.98), (s * 1.1, 3.5, 1.75), 0.045, 0.045, "polymer", sides=6)    # brush guard
        bolt_f(m, s * 0.95, 1.4, 3.5, r=0.02)
        bolt_f(m, s * 0.95, 1.05, 3.5, r=0.02)
    m.limb((-1.1, 3.5, 1.75), (1.1, 3.5, 1.75), 0.045, 0.045, "polymer", sides=6)
    m.box(3.1, 3.4, 0.6, 0.98, 1.6, "gunmetal", c=0.08)                      # skid plate
    plate_u(m, [(-0.9, 3.1), (0.9, 3.1), (0.75, 3.3), (-0.75, 3.3)], 2.1, "ivory", depth=0.005)

    # Sensor turret on the cab roof.
    m.vcyl(2.2, 2.82, 2.95, 0.22, "gunmetal", sides=10)
    m.box(2.0, 2.48, 2.95, 3.25, 0.5, "graphite", c=0.05)
    for s in (-1, 1):
        m.cyl(2.48, 2.56, 3.1, 0.08, "polymer", sides=10, x=s * 0.12)
        m.cyl(2.555, 2.565, 3.1, 0.06, "lens", sides=10, x=s * 0.12)
        m.box(2.3, 2.48, 3.25, 3.29, 0.1, "glow_amber", x=s * 0.18, c=0.0)
    for s in (-1, 1):
        m.limb((s * 0.9, 1.1, 2.82), (s * 0.9, 2.6, 2.82), 0.03, 0.03, "polymer", sides=6)       # roof rails
        for f in (1.2, 2.5):
            m.limb((s * 0.9, f, 2.8), (s * 0.9, f, 2.9), 0.025, 0.025, "polymer", sides=4)

    # ---------------------------------------------------------- survey module
    mod = [octo(1.0, 1.1, 1.62, 2.55, 0.0, 0.15), octo(-0.9, 1.1, 1.62, 2.55, 0.0, 0.15)]
    m.loft(mod, "white_paint", name="module")
    for s in (-1, 1):
        m.prism([(-0.85, 1.7), (-0.2, 1.7), (-0.2, 2.35), (-0.85, 2.35)], 0.03, "graphite", x=s * 1.11)
        m.prism([(-0.15, 1.7), (0.95, 1.7), (0.95, 1.9), (-0.15, 1.9)], 0.03, "navy", x=s * 1.11)
        m.box(-0.75, -0.3, 2.1, 2.18, 0.03, "glow_amber", x=s * 1.12, c=0.0)
        vents_x(m, 0.1, 0.8, 2.05, 2.35, 1.11, 7)
        plate_x(m, [(-0.8, 1.75), (-0.25, 1.75), (-0.25, 2.0), (-0.8, 2.0)], 1.125, "lime", mirror=False) if s < 0 else None
        # Ladder up the module side.
        for x in (0.85, 0.65):
            m.limb((s * 1.16, x, 1.0), (s * 1.16, x, 2.6), 0.022, 0.022, "spring", sides=4)
        for k in range(6):
            u = 1.1 + k * 0.25
            m.limb((s * 1.16, 0.85, u), (s * 1.16, 0.65, u), 0.018, 0.018, "spring", sides=4)
    # Equipment on the roof: racks, radome, dish, antennas.
    m.box(-0.8, 0.4, 2.55, 2.9, 1.2, "graphite", c=0.06)
    m.box(-0.7, -0.1, 2.9, 3.0, 0.8, "gunmetal", c=0.03)
    m.vcyl(-0.5, 2.9, 3.2, 0.14, "gunmetal", sides=8)
    m.sphere(-0.5, 3.45, 0.34, "white_paint", segments=14, rings=8)
    m.vcyl(0.1, 2.9, 3.4, 0.04, "polymer", sides=6, x=0.5)
    dish = m.cyl(0.0, 0.1, 0.0, 0.28, "polymer", sides=12, r1=0.08)
    m.transform(dish, rotate=(20, 0, -25), move=(0.5, 0.1, 3.55))
    face = m.cyl(-0.01, 0.0, 0.0, 0.25, "steel", sides=12, detail=True)
    m.transform(face, rotate=(20, 0, -25), move=(0.5, 0.1, 3.55))
    for x, f, h in ((-0.9, 0.9, 3.9), (-0.75, 0.55, 3.5), (0.85, 0.85, 3.7), (0.95, -0.3, 3.3), (-0.95, -0.4, 3.6)):
        m.limb((x, f, 2.55), (x, f, h), 0.025, 0.012, "polymer", sides=4)
        m.vcyl(f, 2.55, 2.8, 0.05, "gunmetal", sides=6, x=x)
        m.vcyl(f, h - 0.6, h - 0.5, 0.035, "polymer", sides=6, x=x)
    for s in (-1, 1):
        m.limb((s * 1.05, -0.85, 2.6), (s * 1.05, 0.95, 2.6), 0.03, 0.03, "polymer", sides=6)

    # ---------------------------------------------------------- rear cargo deck
    m.top_prism([(-1.15, -0.95), (1.15, -0.95), (1.15, -3.25), (-1.15, -3.25)], 1.2, 1.62, "graphite")
    for i in range(7):
        plate_u(m, [(-1.1, -1.05 - i * 0.3), (1.1, -1.05 - i * 0.3), (1.1, -1.12 - i * 0.3), (-1.1, -1.12 - i * 0.3)], 1.62, "steel", depth=0.01)
    # Containers: grey with lime blotches, and an olive one with a lid.
    m.box(-2.4, -1.05, 1.62, 2.5, 1.0, "white_paint", x=-0.5, c=0.06)
    m.box(-2.3, -1.15, 2.5, 2.56, 0.9, "gunmetal", x=-0.5, c=0.02)
    m.side_box(-2.2, -1.6, 1.8, 2.3, -1.003, -1.02, "lime", c=0.04)
    m.box(-3.05, -1.3, 1.62, 2.3, 0.8, "olive", x=0.55, c=0.05)
    m.box(-2.95, -1.4, 2.3, 2.36, 0.7, "gunmetal", c=0.02, x=0.55)
    for f in (-2.6, -2.0, -1.5):
        m.side_box(f - 0.04, f + 0.04, 1.62, 2.3, 0.14, 0.96, "polymer", c=0.0, detail=True)
    m.side_box(-3.15, -2.55, 1.62, 2.1, -1.0, -0.1, "graphite", c=0.04)
    m.box(-3.1, -2.6, 2.1, 2.14, 0.8, "glow_amber", x=-0.55, c=0.0, detail=True)
    vents_x(m, -3.05, -2.65, 1.7, 2.0, 1.0, 4)
    # Railings.
    for s in (-1, 1):
        m.limb((s * 1.12, -0.95, 2.15), (s * 1.12, -3.2, 2.15), 0.03, 0.03, "polymer", sides=6)
        for f in (-1.0, -2.1, -3.2):
            m.limb((s * 1.12, f, 1.62), (s * 1.12, f, 2.15), 0.028, 0.028, "polymer", sides=4)
    m.limb((-1.12, -3.2, 2.15), (1.12, -3.2, 2.15), 0.03, 0.03, "polymer", sides=6)
    # Rear bumper, tail lights, hitch.
    m.box(-3.45, -3.2, 0.95, 1.35, 2.1, "navy", c=0.06)
    for s in (-1, 1):
        m.box(-3.5, -3.42, 1.05, 1.25, 0.3, "polymer", x=s * 0.8, c=0.02)
        m.box(-3.52, -3.49, 1.08, 1.22, 0.24, "glow_red", x=s * 0.8, c=0.01)
        torus(m, (s * 0.4, -3.5, 0.95), "x", 0.08, 0.022, "spring", n=8, k=4)
    m.box(-3.5, -3.42, 1.05, 1.2, 0.3, "gunmetal", c=0.02)

    m.marker("seat", f=2.25, u=2.3, x=-0.5)            # driver eye
    m.marker("seat_passenger", f=2.25, u=2.3, x=0.5)
    m.marker("seat_rear_l", f=1.45, u=2.3, x=-0.5)
    m.marker("seat_rear_r", f=1.45, u=2.3, x=0.5)
    m.marker("exit", f=1.9, u=0.1, x=-2.3)
    m.marker("exit_r", f=1.9, u=0.1, x=2.3)
    m.marker("turret", f=2.24, u=3.1)
    pivots = {}
    for ax, f in AXLES.items():
        pivots[f"wheel-{ax}l"] = (-TR, f, WR)
        pivots[f"wheel-{ax}r"] = (TR, f, WR)
    return m.finish(BUDGET, texture_size=2048, before_export=origins("strider", pivots))
