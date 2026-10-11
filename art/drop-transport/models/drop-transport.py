"""Drop transport: the start-of-match colony carrier that 60 players jump out of.
Concepts: codex/concepts/v0.2/25-drop-transport.png (exterior) and
26-drop-transport-interior.png (hold).

Origin at the center of the aircraft (mid-length, on the fuselage axis); faces forward
(-Y in Blender). About 52 m long with a 50 m span: a faceted graphite and ivory hull
with a lime band, high swept wings with four boxy engine nacelles (amber intakes,
glowing exhausts), twin canted tail fins on an upswept tail, belly gear sponsons.
The rear ramp is its own object (group "ramp", closed, origin on the hinge line):
rotate it about its local X axis to open it. Behind it the hold is modeled: deck with
light rails, 60 jump seats along the walls, wall ribs, overhead bins, ceiling lights.
Markers: ramp_hinge, jump_point (ramp lip when open), seat (pilot view), hold.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "vehicles", "models"))
from _vkit import (face_panel, hull_ring, lerp, loft_open, octo, origins, panel,  # noqa: E402
                   plate_u, plate_x, thick_strip, vents_u, vents_x)
from kit import Model  # noqa: E402

BUDGET = (8000, 15000)

# Fuselage stations: (f, half width, bottom, top, bottom chamfer, top chamfer).
STATIONS = [
    (27.0, 0.9, -1.7, -0.3, 0.3, 0.3),
    (25.6, 2.5, -2.9, 1.0, 0.8, 0.9),
    (22.8, 3.9, -3.7, 2.9, 1.0, 1.4),
    (18.0, 4.6, -4.0, 3.8, 1.1, 1.5),
    (8.0, 4.8, -4.1, 4.0, 1.15, 1.5),
    (-6.0, 4.8, -4.1, 4.0, 1.15, 1.5),
    (-13.0, 4.6, -3.9, 3.95, 1.05, 1.45),     # ramp hinge station
    (-17.0, 3.9, 0.9, 3.85, 0.7, 1.2),
    (-21.5, 2.6, 1.8, 3.7, 0.5, 0.85),
    (-25.0, 1.2, 2.5, 3.45, 0.25, 0.35),
]
HINGE_K = 6
HINGE = (0.0, -13.0, -3.9)
FLOOR = -3.0
CEIL = 2.6
WALL = 3.95


def nacelle(m, x, f0, length, u):
    """Boxy engine pod: lofted shell, amber-lit intake with vertical vanes, glowing exhaust."""
    W, H = 1.55, 1.95
    rings = [hull_ring(f0, W * 0.86, u - H * 0.86, u + H * 0.86, 0.45, 0.45, bulge=0.02, x=x),
             hull_ring(f0 - 0.7, W, u - H, u + H, 0.55, 0.55, bulge=0.03, x=x),
             hull_ring(f0 - length * 0.3, W * 1.03, u - H * 1.03, u + H * 1.03, 0.6, 0.6, bulge=0.03, x=x),
             hull_ring(f0 - length * 0.55, W * 1.02, u - H * 1.02, u + H * 1.02, 0.6, 0.6, bulge=0.03, x=x),
             hull_ring(f0 - length + 0.6, W * 0.92, u - H * 0.94, u + H * 0.94, 0.55, 0.55, bulge=0.03, x=x),
             hull_ring(f0 - length, W * 0.8, u - H * 0.82, u + H * 0.82, 0.45, 0.45, bulge=0.02, x=x)]
    m.loft(rings, "graphite", name="nacelle")
    # Ivory upper cowl panel and a lime ring.
    m.loft([[(px, pf, pu + 0.02) for px, pf, pu in r] for r in
            (octo(f0 - 0.9, W + 0.03, u + 0.1, u + H + 0.03, 0.0, 0.58, x=x), octo(f0 - length * 0.5, W + 0.05, u + 0.1, u + H + 0.05, 0.0, 0.6, x=x))],
           "ivory", name="cowl")
    m.loft([octo(f0 - length * 0.56, W * 1.035, u - H * 1.035, u + H * 1.035, 0.6, 0.6, x=x),
            octo(f0 - length * 0.6, W * 1.035, u - H * 1.035, u + H * 1.035, 0.6, 0.6, x=x)], "lime", name="band")
    # Intake: dark recessed face, two glowing vertical slots, vanes.
    face = [(x + px, pu) for px, pu in [(-W * 0.7, -H * 0.55), (W * 0.7, -H * 0.55), (W * 0.75, H * 0.55), (-W * 0.75, H * 0.55)]]
    m.front_prism([(px, u + pu) for px, pu in face], f0 - 0.1, f0 + 0.08, "navy")
    for s in (-1, 1):
        m.box(f0 + 0.05, f0 + 0.14, u - H * 0.45, u + H * 0.45, 0.24, "glow_amber", x=x + s * 0.42, c=0.02)
    for k in range(5):
        m.box(f0 + 0.06, f0 + 0.12, u - H * 0.5, u + H * 0.5, 0.06, "gunmetal", x=x - 0.9 + k * 0.45, c=0.0, detail=True)
    # Exhaust: graphite frame and glowing core.
    fb = f0 - length
    m.front_prism([(x - W * 0.62, u - H * 0.62), (x + W * 0.62, u - H * 0.62), (x + W * 0.62, u + H * 0.62), (x - W * 0.62, u + H * 0.62)], fb - 0.25, fb + 0.05, "gunmetal")
    m.front_prism([(x - W * 0.5, u - H * 0.5), (x + W * 0.5, u - H * 0.5), (x + W * 0.5, u + H * 0.5), (x - W * 0.5, u + H * 0.5)], fb - 0.3, fb - 0.2, "glow_amber")
    for k in range(4):
        m.box(fb - 0.33, fb - 0.28, u - H * 0.5, u + H * 0.5, 0.05, "gunmetal", x=x - 0.6 + k * 0.4, c=0.0, detail=True)
    # Baked: panel seams, vents and bolts on the flanks.
    for s in (-1, 1):
        for fp in (f0 - 1.5, f0 - length * 0.35, f0 - length * 0.75):
            m.side_box(fp - 0.04, fp + 0.04, u - H * 0.7, u + H * 0.7, x + s * (W * 1.02 - 0.01), x + s * (W * 1.02 + 0.03), "gunmetal", c=0.0, detail=True)
        vents_x_at(m, f0 - 2.2, f0 - 3.6, u - 0.9, u - 0.1, x + s * W * 1.02, 6)
    m.box(f0 - 1.0, f0 - 0.7, u - H - 0.05, u - H + 0.02, 0.3, "glow_amber", x=x, c=0.0)


def vents_x_at(m, f0, f1, u0, u1, x, count):
    f0, f1 = sorted((f0, f1))
    step = (f1 - f0) / count
    s = 1 if x >= 0 else -1
    for i in range(count):
        a = f0 + i * step
        m.side_box(a, a + step * 0.45, u0, u1, x - s * 0.01, x + s * 0.04, "polymer", c=0.0, detail=True)


def wing(m, s):
    """High swept wing: lofted airfoil sections from root to tip, with flap panels."""
    secs = []
    for x, le, te, u, t in ((3.8, 9.0, -6.5, 3.4, 1.3), (12.0, 4.5, -7.2, 3.2, 0.85), (25.0, -3.4, -8.8, 2.9, 0.42)):
        c = le - te
        secs.append([(s * x, le, u), (s * x, le - 0.12 * c, u + t * 0.5), (s * x, te + 0.35 * c, u + t * 0.42),
                     (s * x, te, u + 0.05), (s * x, te + 0.35 * c, u - t * 0.3), (s * x, le - 0.12 * c, u - t * 0.35)])
    m.loft(secs, "graphite", name="wing")
    # Ivory top skin panels with gaps, lime tip stripe.
    for a, b in ((0.08, 0.46), (0.52, 0.93)):
        r0 = [lerp(secs[0][i], secs[2][i], a) for i in (1, 2)]
        r1 = [lerp(secs[0][i], secs[2][i], b) for i in (1, 2)]
        quad = [lerp(r0[0], r0[1], 0.04), lerp(r0[0], r0[1], 0.85), lerp(r1[0], r1[1], 0.85), lerp(r1[0], r1[1], 0.04)]
        face_panel(m, quad, "ivory", inset=0.0, depth=0.08, push=0.06, center=(s * 14.0, -10.0))
    tip = [lerp(secs[1][i], secs[2][i], 0.9) for i in range(6)]
    m.loft([tip, [lerp(secs[1][i], secs[2][i], 0.94) for i in range(6)]], "lime", name="tipband")
    # Flaps along the trailing edge (separate plates for a layered look).
    for a, b in ((0.12, 0.42), (0.46, 0.78)):
        p0, p1 = lerp(secs[0][3], secs[2][3], a), lerp(secs[0][3], secs[2][3], b)
        quad = [p0, p1, (p1[0], p1[1] + 1.2, p1[2] + 0.08), (p0[0], p0[1] + 1.6, p0[2] + 0.1)]
        panel(m, [(q[0], q[1] - 0.15, q[2]) for q in quad], 0.14, "gunmetal")
    # Wingtip light.
    m.box(-4.0, -3.0, 2.85, 3.05, 0.25, "glow_amber", x=s * 25.05, c=0.02)


def build():
    m = Model("drop-transport", category="drop-transport", bevel=0.04, cage=0.08)

    rings = [hull_ring(*st, bulge=0.03) for st in STATIONS]
    # Ramp opening: bottom chamfers and bottom between the hinge station and the next one.
    opening = [(HINGE_K, i) for i in range(10, 16)]
    loft_open(m, rings, "graphite", skip=opening, name="hull")

    # ---------------------------------------------------------- ivory armor panels on the hull
    def band(k0, k1, faces, t0=0.04, t1=0.96, mat="ivory", depth=0.12, push=0.05, inset=0.0):
        for i in faces:
            a0, a1 = rings[k0][i], rings[k0][(i + 1) % 16]
            b0, b1 = rings[k1][i], rings[k1][(i + 1) % 16]
            quad = [lerp(a0, b0, t0), lerp(a1, b1, t0), lerp(a1, b1, t1), lerp(a0, b0, t1)]
            face_panel(m, quad, mat, inset=inset, depth=depth, push=push, center=(0.0, 0.0))
    band(3, 4, [2, 3, 4, 5, 6, 7], 0.03, 0.62)                 # forward top
    band(3, 4, [1, 8], 0.08, 0.55)                            # forward upper sides
    band(4, 5, [3, 4, 5, 6], 0.05, 0.42)                      # mid top
    band(4, 5, [3, 4, 5, 6], 0.5, 0.95)
    band(4, 5, [1, 8], 0.18, 0.62)
    band(5, 6, [2, 3, 4, 5, 6, 7], 0.1, 0.9)
    band(2, 3, [1, 8], 0.35, 0.92)
    band(7, 8, [4, 5], 0.05, 0.9)
    band(4, 5, [0, 9], 0.66, 0.74, mat="lime", depth=0.1, push=0.04)        # lime side stripe
    band(5, 6, [0, 1, 8, 9], 0.04, 0.09, mat="lime", depth=0.1, push=0.04)   # lime band near the tail
    # Graphite armor blocks low on the sides (darker navy).
    band(4, 5, [0, 9], 0.1, 0.55, mat="navy", depth=0.14, push=0.06)
    band(5, 6, [0, 9], 0.2, 0.85, mat="navy", depth=0.14, push=0.06)

    # ---------------------------------------------------------- cockpit
    A, B = rings[1], rings[2]
    for i in range(2, 8):
        a0, a1, b0, b1 = A[i], A[i + 1], B[i], B[i + 1]
        quad = [lerp(a0, b0, 0.1), lerp(a1, b1, 0.1), lerp(a1, b1, 0.75), lerp(a0, b0, 0.75)]
        face_panel(m, quad, "tinted_glass", inset=0.08, depth=0.08, push=0.05, center=(0.0, -0.5))
    for i in (1, 8):
        a0, a1, b0, b1 = A[i], A[i + 1], B[i], B[i + 1]
        quad = [lerp(a0, b0, 0.15), lerp(a1, b1, 0.15), lerp(a1, b1, 0.7), lerp(a0, b0, 0.7)]
        face_panel(m, quad, "tinted_glass", inset=0.15, depth=0.08, push=0.05, center=(0.0, -0.5))
    # Chin sensor block and nose lights.
    m.front_prism([(-1.3, -2.9), (1.3, -2.9), (1.6, -2.0), (1.3, -1.4), (-1.3, -1.4), (-1.6, -2.0)], 25.0, 26.6, "navy")
    for k in range(5):
        m.front_prism([(-1.1, -2.6 + k * 0.22), (1.1, -2.6 + k * 0.22), (1.1, -2.5 + k * 0.22), (-1.1, -2.5 + k * 0.22)], 26.58, 26.66, "gunmetal", detail=True)
    for s in (-1, 1):
        m.box(25.2, 26.0, -0.4, -0.15, 0.8, "glow_amber", x=s * 1.9, c=0.05)
        m.box(24.4, 25.0, -3.05, -2.85, 0.6, "glow_amber", x=s * 1.6, c=0.05)

    # ---------------------------------------------------------- dorsal spine, wings, nacelles
    m.top_prism([(-1.2, 16.0), (1.2, 16.0), (1.6, 12.0), (1.6, -12.0), (1.0, -16.5), (-1.0, -16.5), (-1.6, -12.0), (-1.6, 12.0)], 3.6, 4.55, "graphite")
    m.top_prism([(-0.9, 14.5), (0.9, 14.5), (1.2, 11.5), (1.2, -11.0), (-1.2, -11.0), (-1.2, 11.5)], 4.55, 4.75, "ivory")
    vents_u(m, -0.8, 0.8, -9.0, -3.0, 4.75, 10, depth=0.06)
    vents_u(m, -0.8, 0.8, 2.0, 7.0, 4.75, 8, depth=0.06)
    for f in (13.0, 0.0, -14.0):
        m.box(f - 0.4, f + 0.4, 4.55, 4.8, 0.4, "glow_amber", c=0.05)
    for f, h in ((9.0, 6.0), (-8.0, 5.6)):
        m.limb((0.0, f, 4.7), (0.0, f - 0.8, h), 0.08, 0.03, "polymer", sides=4)
    for s in (-1, 1):
        wing(m, s)
        nacelle(m, s * 10.0, 9.2, 9.5, 1.65)
        nacelle(m, s * 18.0, 4.0, 8.5, 1.75)
        for x, f0 in ((10.0, 9.2), (18.0, 4.0)):
            m.box(f0 - 7.0, f0 - 1.5, 2.9, 3.6, 0.8, "gunmetal", x=s * x, c=0.15)        # pylon

    # ---------------------------------------------------------- tail
    for s in (-1, 1):
        fin = m.prism([(-15.5, 3.5), (-21.0, 3.4), (-25.5, 11.0), (-23.4, 11.2)], 0.45, "graphite", x=s * 2.1)
        m.transform(fin, rotate=(0, -s * 14, 0), pivot=(s * 2.1, -18.0, 3.5))
        top = m.prism([(-22.3, 9.0), (-24.8, 9.0), (-25.55, 11.02), (-23.38, 11.22)], 0.5, "ivory", x=s * 2.1)
        m.transform(top, rotate=(0, -s * 14, 0), pivot=(s * 2.1, -18.0, 3.5))
        stripe = m.prism([(-18.6, 4.6), (-19.4, 4.6), (-22.0, 9.4), (-21.2, 9.4)], 0.5, "lime", x=s * 2.1)
        m.transform(stripe, rotate=(0, -s * 14, 0), pivot=(s * 2.1, -18.0, 3.5))
        light = m.box(-25.4, -24.9, 10.9, 11.15, 0.5, "glow_amber", x=s * 2.1, c=0.03)
        m.transform(light, rotate=(0, -s * 14, 0), pivot=(s * 2.1, -18.0, 3.5))
        m.top_prism([(s * 1.0, -19.0), (s * 9.5, -22.6), (s * 9.5, -24.4), (s * 1.0, -25.0)], 3.15, 3.55, "graphite")   # stabilizer
        m.top_prism([(s * 2.0, -20.0), (s * 9.0, -22.9), (s * 9.0, -23.4), (s * 2.0, -21.0)], 3.55, 3.6, "ivory")
        m.box(-24.4, -22.6, 3.2, 3.5, 0.2, "glow_amber", x=s * 9.55, c=0.03)
    m.box(-25.3, -24.8, 2.7, 3.2, 1.0, "glow_red", c=0.05)

    # ---------------------------------------------------------- belly gear sponsons
    for s in (-1, 1):
        sp = [octo(7.0, 0.9, -4.0, -2.2, 0.4, 0.2, x=s * 4.6), octo(5.5, 1.0, -4.3, -2.0, 0.45, 0.2, x=s * 4.65),
              octo(-5.5, 1.0, -4.3, -2.0, 0.45, 0.2, x=s * 4.65), octo(-7.5, 0.85, -3.9, -2.2, 0.4, 0.2, x=s * 4.6)]
        m.loft(sp, "navy", name="sponson")
        for f in (3.2, 0.0, -3.2):
            m.xcyl(f, -4.45, s * 4.2, s * 4.75, 0.8, "rubber", sides=12)
            m.xcyl(f, -4.45, s * 4.74, s * 4.8, 0.45, "gunmetal", sides=8)
        m.box(-5.0, 5.0, -3.0, -2.75, 0.06, "glow_amber", x=s * 5.66, c=0.0)
        for f in (-4.0, -1.6, 1.6, 4.0):
            m.side_box(f - 0.05, f + 0.05, -4.25, -2.0, s * 5.64, s * 5.7, "gunmetal", c=0.0, detail=True)
    # Nose gear.
    m.box(19.0, 22.0, -4.3, -3.6, 1.6, "navy", c=0.2)
    for s in (-1, 1):
        m.xcyl(20.5, -4.45, s * 0.25, s * 0.75, 0.6, "rubber", sides=12)

    # ---------------------------------------------------------- ramp (closed)
    K0, K1 = rings[HINGE_K], rings[HINGE_K + 1]
    idx = [10, 11, 12, 13, 14, 15, 0]
    thick_strip(m, [K0[i] for i in idx], [K1[i] for i in idx], 0.35, 0.0, "graphite", group="ramp", name="ramp")
    # Ramp outer armor: ivory plate, lime chevrons, amber edge lights, inner deck grip.
    pa, pb = [K0[i] for i in idx], [K1[i] for i in idx]
    for c0, c1 in ((2, 4),):
        quad = [lerp(pa[c0], pb[c0], 0.1), lerp(pa[c1], pb[c1], 0.1), lerp(pa[c1], pb[c1], 0.88), lerp(pa[c0], pb[c0], 0.88)]
        face_panel(m, quad, "ivory", inset=0.04, depth=0.1, push=0.05, center=(0.0, 0.0), group="ramp")
    for t in (0.25, 0.55):
        quad = [lerp(pa[2], pb[2], t), lerp(pa[4], pb[4], t), lerp(pa[4], pb[4], t + 0.06), lerp(pa[2], pb[2], t + 0.06)]
        face_panel(m, quad, "lime", inset=0.0, depth=0.06, push=0.11, center=(0.0, 0.0), group="ramp", detail=True)
    for i in (0, 6):
        q = [lerp(pa[i], pb[i], 0.15), lerp(pa[i], pb[i], 0.85)]
        m.limb(q[0], q[1], 0.08, 0.08, "glow_amber", sides=4, group="ramp")
    m.limb(pb[1], pb[5], 0.09, 0.09, "gunmetal", sides=6, group="ramp")                      # ramp lip
    # Door frame around the opening (on the hull).
    for i in (0, 10):
        m.limb(K0[i], K1[i], 0.14, 0.14, "gunmetal", sides=6)
    m.limb(K1[10], K1[0], 0.14, 0.14, "gunmetal", sides=6)
    m.xcyl(HINGE[1], HINGE[2] + 0.15, -3.0, 3.0, 0.18, "gunmetal", sides=8)                 # hinge barrel

    # ---------------------------------------------------------- hold interior
    F0, F1 = -13.6, 12.0
    m.top_prism([(-WALL, F1), (WALL, F1), (WALL, F0), (-WALL, F0)], FLOOR - 0.3, FLOOR, "gunmetal")         # deck
    m.top_prism([(-WALL, F1), (WALL, F1), (WALL, -17.0), (-WALL, -17.0)], CEIL, CEIL + 0.3, "graphite")       # ceiling
    m.front_prism([(-WALL, FLOOR), (WALL, FLOOR), (WALL, CEIL), (-WALL, CEIL)], F1, F1 + 0.3, "graphite")     # fore bulkhead
    m.front_prism([(-3.3, 0.9), (3.3, 0.9), (3.3, CEIL), (-3.3, CEIL)], -17.3, -17.0, "graphite")             # aft wall above door
    for s in (-1, 1):
        m.side_box(F0, F1, FLOOR, CEIL, s * WALL, s * (WALL + 0.25), "graphite", c=0.0)                      # wall
        m.prism([(-13.0, FLOOR), (-13.0, CEIL), (-17.0, CEIL), (-17.0, 0.9)], 0.25, "graphite", x=s * 3.4)     # tail side wall
        m.side_box(F0, F1, FLOOR, FLOOR + 0.1, s * (WALL - 0.6), s * (WALL - 0.45), "glow_amber", c=0.0)     # floor light rail
        # Jump seats: a frame rail, a pan and a back per seat with lime stripes, harness detail baked.
        m.side_box(-12.0, 11.0, FLOOR + 0.3, FLOOR + 0.45, s * (WALL - 0.4), s * WALL, "gunmetal", c=0.03)
        m.side_box(-12.0, 11.0, FLOOR, FLOOR + 0.3, s * (WALL - 0.12), s * WALL, "gunmetal", c=0.0)
        for k in range(30):
            f = -11.6 + k * 0.77
            m.side_box(f + 0.02, f + 0.6, FLOOR + 0.45, FLOOR + 0.6, s * (WALL - 0.55), s * (WALL - 0.1), "seat", c=0.04)
            m.side_box(f, f + 0.62, FLOOR + 0.6, FLOOR + 1.6, s * (WALL - 0.14), s * WALL, "seat", c=0.04)
            m.side_box(f + 0.26, f + 0.36, FLOOR + 0.65, FLOOR + 1.55, s * (WALL - 0.16), s * (WALL - 0.13), "lime", c=0.0, detail=True)
            m.side_box(f + 0.1, f + 0.16, FLOOR + 0.62, FLOOR + 1.5, s * (WALL - 0.17), s * (WALL - 0.13), "fabric", c=0.0, detail=True)
            m.side_box(f + 0.46, f + 0.52, FLOOR + 0.62, FLOOR + 1.5, s * (WALL - 0.17), s * (WALL - 0.13), "fabric", c=0.0, detail=True)
        # Wall ribs and overhead bins.
        for k in range(9):
            f = -12.4 + k * 2.95
            m.side_box(f, f + 0.3, FLOOR, CEIL, s * (WALL - 0.3), s * WALL, "gunmetal", c=0.06)
            m.side_box(f + 0.3, f + 2.65, CEIL - 1.1, CEIL - 0.15, s * (WALL - 0.75), s * WALL, "navy", c=0.08)
            m.side_box(f + 0.6, f + 2.35, CEIL - 0.1, CEIL - 0.04, s * (WALL - 0.7), s * (WALL - 0.4), "glow_amber", c=0.0)
            m.side_box(f + 1.0, f + 1.9, CEIL - 0.9, CEIL - 0.35, s * (WALL - 0.78), s * (WALL - 0.74), "hazard", c=0.0, detail=True)
    # Ceiling beams and cable/pipe runs.
    for k in range(9):
        f = -12.4 + k * 2.95
        m.box(f, f + 0.3, CEIL - 0.35, CEIL, 2 * WALL, "gunmetal", c=0.06)
    for x, r in ((-2.6, 0.12), (-2.3, 0.08), (2.4, 0.14), (2.75, 0.07)):
        m.cyl(-16.8, F1, CEIL - 0.45, r, "bronze" if r > 0.1 else "gunmetal", sides=8, x=x)
    # Ceiling light boxes (red jump lights and amber work lights) and deck rails.
    for k in range(8):
        f = -11.5 + k * 3.0
        m.box(f, f + 1.2, CEIL - 0.08, CEIL, 1.0, "glow_red" if k % 2 else "glow_amber", c=0.0)
    for x in (-1.6, 1.6):
        m.side_box(F0, F1, FLOOR, FLOOR + 0.05, x - 0.1, x + 0.1, "glow_amber", c=0.0)
        for k in range(12):
            f = -12.8 + k * 2.1
            plate_u(m, [(x - 0.15, f), (x + 0.15, f), (x + 0.15, f + 0.12), (x - 0.15, f + 0.12)], FLOOR + 0.05, "steel", depth=0.03)
    for k in range(10):
        f = -12.6 + k * 2.4
        plate_u(m, [(-1.3, f), (1.3, f), (1.3, f + 0.08), (-1.3, f + 0.08)], FLOOR, "steel", depth=0.03)
    # Cargo cases forward in the hold.
    for x, f in ((-2.2, 9.8), (2.2, 9.8), (-2.2, 8.4)):
        m.box(f - 0.6, f + 0.6, FLOOR, FLOOR + 1.0, 1.1, "olive", x=x, c=0.08)
        m.box(f - 0.62, f + 0.62, FLOOR + 0.42, FLOOR + 0.52, 1.14, "hazard", x=x, c=0.0, detail=True)
    # Jump light by the door.
    m.box(-12.9, -12.6, CEIL - 0.7, CEIL - 0.2, 0.6, "glow_red", x=-2.8, c=0.03)
    m.box(-12.9, -12.6, CEIL - 0.7, CEIL - 0.2, 0.6, "glow_lime", x=2.8, c=0.03)

    # ---------------------------------------------------------- baked hull detail
    for s in (-1, 1):
        for f in range(-11, 18, 3):
            m.side_box(f - 0.05, f + 0.05, -2.8, 2.4, s * 4.78, s * 4.86, "gunmetal", c=0.0, detail=True)
        for f in (14.0, -9.5):
            m.side_box(f - 1.0, f + 1.0, -1.2, 1.0, s * 4.78, s * 4.88, "navy", c=0.1, detail=True)    # hatch
            m.side_box(f - 0.15, f + 0.15, 1.1, 1.3, s * 4.8, s * 4.9, "glow_amber", c=0.0)
        for f in (16.0, 6.0, -4.0):
            m.side_box(f - 0.25, f + 0.25, 2.1, 2.3, s * 4.8, s * 4.9, "glow_amber", c=0.0)
        vents_x_at(m, 10.0, 13.0, -2.6, -1.6, s * 4.8, 8)

    m.marker("ramp_hinge", f=HINGE[1], u=HINGE[2])
    m.marker("jump_point", f=-18.6, u=-3.7)          # ramp lip when the ramp is lowered level
    m.marker("seat", f=23.2, u=1.2, x=-1.0)          # pilot view
    m.marker("hold", f=0.0, u=FLOOR)
    return m.finish(BUDGET, texture_size=2048, before_export=origins("drop-transport", {"ramp": HINGE}))
