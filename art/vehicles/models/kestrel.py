"""Kestrel: unarmed utility rotorcraft. Concept: codex/concepts/v0.2/24-kestrel.png.

Origin on the ground under the center of the cabin (between the skids); faces forward
(-Y in Blender). Ivory fuselage over a graphite belly, a big faceted cockpit canopy,
two ducted rotors on stub pylons, a tail boom with twin swept fins and lime stripes,
skids on angled legs, amber lights.
Groups: rotor-l and rotor-r (the fan blades inside each duct, origin at the hub so the
game spins them about their up axis).
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vkit import (bolt_u, bolt_x, face_panel, hull_ring, lerp, origins, panel,  # noqa: E402
                   plate_u, plate_x, utube, vents_u, vents_x)
from kit import Model  # noqa: E402

BUDGET = (4000, 8000)

DUCT_X = 3.45
DUCT_F = -0.2
DUCT_U = 2.95
DUCT_R = 1.7


def strip(a, b, i0, i1):
    """Polygon covering ring a points i0..i1 and ring b points i1..i0 (one hull face band)."""
    return [a[i] for i in range(i0, i1 + 1)] + [b[i] for i in range(i1, i0 - 1, -1)]


def duct(m, s):
    x, f, u = s * DUCT_X, DUCT_F, DUCT_U
    n = 28
    # Shroud: ivory ring with a rolled lip, graphite lower band.
    utube(m, x, f, u - 0.15, u + 0.3, DUCT_R + 0.12, DUCT_R, "ivory", sides=n)
    utube(m, x, f, u - 0.45, u - 0.15, DUCT_R + 0.08, DUCT_R, "graphite", sides=n)
    utube(m, x, f, u + 0.3, u + 0.36, DUCT_R + 0.06, DUCT_R + 0.01, "graphite", sides=n)
    # Dark segment blocks and amber lights around the shroud.
    for k in range(6):
        a = 2 * math.pi * (k + 0.5) / 6
        px, pf = x + math.cos(a) * (DUCT_R + 0.14), f + math.sin(a) * (DUCT_R + 0.14)
        blk = m.side_box(pf - 0.3, pf + 0.3, u - 0.4, u + 0.25, px - 0.07, px + 0.07, "graphite", c=0.04)
        m.transform(blk, rotate=(0, 0, -math.degrees(a)), pivot=(px, pf, u))
        g = m.side_box(pf - 0.2, pf + 0.2, u - 0.38, u - 0.32, px + 0.06, px + 0.09, "glow_amber", c=0.0)
        m.transform(g, rotate=(0, 0, -math.degrees(a)), pivot=(px, pf, u))
        vents = m.side_box(pf - 0.18, pf + 0.18, u - 0.2, u + 0.15, px + 0.065, px + 0.08, "polymer", c=0.02, detail=True)
        m.transform(vents, rotate=(0, 0, -math.degrees(a)), pivot=(px, pf, u))
    # Inner amber ring light and lower bell.
    utube(m, x, f, u + 0.18, u + 0.22, DUCT_R + 0.005, DUCT_R - 0.03, "glow_amber", sides=n)
    utube(m, x, f, u - 0.75, u - 0.45, DUCT_R * 0.75, DUCT_R * 0.6, "graphite", sides=16)
    # Stators: four struts to a central motor pod with a domed cap.
    for k in range(4):
        a = 2 * math.pi * (k + 0.125) / 4
        m.limb((x + math.cos(a) * 0.3, f + math.sin(a) * 0.3, u - 0.1), (x + math.cos(a) * (DUCT_R - 0.02), f + math.sin(a) * (DUCT_R - 0.02), u - 0.1),
               0.05, 0.04, "gunmetal", sides=4)
    m.vcyl(f, u - 0.55, u + 0.05, 0.32, "gunmetal", sides=12, x=x)
    m.sphere(f, u - 0.55, 0.32, "graphite", x=x, segments=12, rings=6, scale=(1, 1, 0.5))
    # Rotor (spinning group): hub, dome and five pitched blades.
    g = "rotor-l" if s < 0 else "rotor-r"
    m.vcyl(f, u + 0.05, u + 0.2, 0.28, "steel", sides=12, x=x, group=g)
    m.sphere(f, u + 0.2, 0.22, "steel", x=x, segments=12, rings=6, scale=(1, 1, 0.55), group=g)
    for k in range(5):
        a = 360.0 * k / 5
        bl = m.side_box(f - 0.13, f + 0.13, u + 0.08, u + 0.13, x + 0.2, x + DUCT_R - 0.06, "graphite", c=0.0, group=g)
        m.transform(bl, rotate=(14, 0, 0), pivot=(x, f, u + 0.1))
        m.transform(bl, rotate=(0, 0, a), pivot=(x, f, u))
        tip = m.side_box(f - 0.13, f + 0.13, u + 0.08, u + 0.135, x + DUCT_R - 0.35, x + DUCT_R - 0.07, "white_paint", c=0.0, group=g, detail=True)
        m.transform(tip, rotate=(14, 0, 0), pivot=(x, f, u + 0.1))
        m.transform(tip, rotate=(0, 0, a), pivot=(x, f, u))


def build():
    m = Model("kestrel", category="vehicles", bevel=0.016, cage=0.035)

    # ---------------------------------------------------------- fuselage
    st = [(4.75, 0.38, 1.05, 1.55, 0.12, 0.15),
          (4.35, 0.9, 0.82, 2.02, 0.28, 0.4),
          (3.05, 1.2, 0.68, 2.65, 0.32, 0.5),
          (1.0, 1.28, 0.66, 2.82, 0.32, 0.5),
          (-1.4, 1.22, 0.7, 2.82, 0.3, 0.45),
          (-2.6, 0.85, 1.25, 2.72, 0.25, 0.35),
          (-3.6, 0.42, 1.85, 2.55, 0.12, 0.15),
          (-6.4, 0.34, 2.05, 2.48, 0.09, 0.1),
          (-6.9, 0.26, 2.1, 2.4, 0.06, 0.07)]
    rings = [hull_ring(*p, bulge=0.035 if p[0] > -3 else 0.0) for p in st]
    m.loft(rings, "ivory", name="fuselage")
    # Graphite belly armor as a proud lower shell over the cabin.
    belly = []
    for f, w, u0, u1, c, ct in st[1:6]:
        mid = u0 + (u1 - u0) * 0.42
        belly.append([(w + 0.03, f, mid), (w + 0.03, f, u0 + c), (w - c + 0.02, f, u0 - 0.03), (-w + c - 0.02, f, u0 - 0.03),
                      (-w - 0.03, f, u0 + c), (-w - 0.03, f, mid), (0.0, f, mid - 0.2)])
    m.loft(belly, "graphite", name="belly")

    # Cockpit glass: windshield, chamfer panes and side panes between the first rings.
    A, B, C = rings[1], rings[2], rings[3]
    glass = "tinted_glass"
    face_panel(m, strip(A, B, 4, 6), glass, inset=0.06, push=0.02)                 # top center
    for i0, i1 in ((2, 4), (6, 8)):
        face_panel(m, strip(A, B, i0, i1), glass, inset=0.08, push=0.02)           # upper chamfers
    face_panel(m, strip(A, B, 0, 2), glass, inset=0.1, push=0.02)                  # right side
    face_panel(m, strip(A, B, 8, 10), glass, inset=0.1, push=0.02)                 # left side
    face_panel(m, strip(rings[0], A, 2, 6), glass, inset=0.18, push=0.015)          # chin window
    # Window frame mullions.
    for i in (2, 4, 6, 8):
        m.limb(A[i], B[i], 0.035, 0.035, "graphite", sides=4)
    # Cabin side windows and sliding door.
    for s in (-1, 1):
        x = s * 1.31
        m.prism([(1.2, 1.75), (2.6, 1.85), (2.75, 2.35), (1.2, 2.4)], 0.04, glass, x=x * 1.005)
        m.prism([(-1.2, 0.95), (0.95, 0.95), (0.95, 2.5), (-1.2, 2.5)], 0.03, "graphite", x=x * 0.995)
        m.prism([(-0.9, 1.75), (0.0, 1.75), (0.0, 2.35), (-0.9, 2.35)], 0.05, glass, x=x)
        m.prism([(0.55, 0.95), (1.85, 1.0), (1.4, 1.45), (0.55, 1.45)], 0.04, "lime", x=x * 1.01) if s > 0 else None
        m.side_box(-1.3, 1.0, 2.52, 2.56, s * 1.27, s * 1.33, "polymer", c=0.0)        # door rail
        m.side_box(0.1, 0.9, 1.6, 2.4, s * 1.3, s * 1.34, "polymer", c=0.02)          # grille panel
        for f, u in ((-1.15, 1.0), (-1.15, 2.45), (0.9, 1.0), (0.9, 2.45)):
            bolt_x(m, f, u, s * 1.33)
        # Nose amber lights.
        m.side_box(4.25, 4.55, 0.95, 1.05, s * 0.45, s * 0.75, "glow_amber", c=0.01)
    vents_x(m, 0.15, 0.85, 1.65, 2.35, 1.34, 8)
    plate_x(m, [(-1.0, 1.1), (-0.3, 1.1), (-0.3, 1.5), (-1.0, 1.5)], 1.33, "graphite")
    # Nose sensor/grille block.
    m.front_prism([(-0.36, 0.9), (0.36, 0.9), (0.42, 1.2), (0.36, 1.42), (-0.36, 1.42), (-0.42, 1.2)], 4.6, 4.88, "graphite")
    m.front_prism([(-0.26, 1.0), (0.26, 1.0), (0.26, 1.32), (-0.26, 1.32)], 4.86, 4.9, "polymer")
    for k in range(4):
        m.front_prism([(-0.22, 1.04 + k * 0.07), (0.22, 1.04 + k * 0.07), (0.22, 1.07 + k * 0.07), (-0.22, 1.07 + k * 0.07)], 4.89, 4.91, "gunmetal", detail=True)
    for s in (-1, 1):
        m.box(4.7, 4.9, 0.8, 0.9, 0.18, "glow_amber", x=s * 0.3, c=0.02)

    # Interior seen through the glass: two seats and a console.
    for s in (-1, 1):
        m.box(2.9, 3.4, 0.9, 1.25, 0.6, "seat", x=s * 0.48, c=0.05)
        bk = m.box(2.75, 2.9, 1.15, 2.05, 0.6, "seat", x=s * 0.48, c=0.05)
        m.transform(bk, rotate=(-10, 0, 0), pivot=(s * 0.48, 2.85, 1.2))
    m.box(3.55, 4.0, 0.85, 1.55, 1.7, "polymer", c=0.08)
    m.box(3.75, 3.95, 1.5, 1.56, 1.4, "glow_amber", c=0.0)

    # ---------------------------------------------------------- dorsal engine and pylons
    m.top_prism([(-0.75, 1.6), (0.75, 1.6), (0.9, 0.9), (0.9, -1.6), (0.6, -2.5), (-0.6, -2.5), (-0.9, -1.6), (-0.9, 0.9)], 2.7, 3.2, "graphite")
    m.top_prism([(-0.55, 1.4), (0.55, 1.4), (0.6, -2.2), (-0.6, -2.2)], 3.2, 3.3, "ivory")
    for s in (-1, 1):
        m.box(0.6, 1.3, 2.95, 3.2, 0.36, "polymer", x=s * 0.62, c=0.04)        # intakes
        m.box(-2.6, -2.2, 2.8, 3.1, 0.3, "gunmetal", x=s * 0.35, c=0.03)       # exhausts
        m.box(-2.62, -2.58, 2.85, 3.05, 0.22, "glow_amber", x=s * 0.35, c=0.0)
    vents_u(m, -0.45, 0.45, -1.8, 0.8, 3.3, 12)
    for s in (-1, 1):
        # Stub pylon: tapered, with an ivory top and graphite underside.
        m.top_prism([(s * 0.85, 0.7), (s * (DUCT_X - DUCT_R + 0.1), 0.35), (s * (DUCT_X - DUCT_R + 0.1), -0.75), (s * 0.85, -1.2)],
                    2.62, 3.05, "graphite")
        m.top_prism([(s * 0.85, 0.6), (s * (DUCT_X - DUCT_R + 0.1), 0.28), (s * (DUCT_X - DUCT_R + 0.1), -0.68), (s * 0.85, -1.1)],
                    3.05, 3.12, "ivory")
        m.box(-0.75, 0.35, 2.55, 3.15, 0.5, "graphite", x=s * (DUCT_X - DUCT_R + 0.05), c=0.05)   # duct mount
        duct(m, s)

    # ---------------------------------------------------------- tail
    for s in (-1, 1):
        m.top_prism([(0.0, -5.9), (s * 1.25, -6.35), (s * 1.25, -6.7), (0.0, -6.8)], 2.2, 2.3, "ivory")      # stabilizer
        fin = [(-5.95, 2.25), (-6.45, 2.25), (-7.15, 4.0), (-6.8, 4.05)]
        m.prism(fin, 0.1, "ivory", x=s * 1.2)
        m.prism([(-6.5, 3.4), (-6.88, 3.4), (-7.15, 4.0), (-6.8, 4.05)], 0.105, "graphite", x=s * 1.2)
        m.prism([(-6.15, 2.6), (-6.3, 2.6), (-6.72, 3.5), (-6.6, 3.5)], 0.11, "lime", x=s * 1.2)
        m.prism([(-6.0, 2.25), (-6.35, 2.25), (-6.6, 1.55), (-6.4, 1.55)], 0.09, "graphite", x=s * 1.2)   # ventral fin
        m.box(-7.18, -7.08, 3.92, 4.0, 0.06, "glow_amber", x=s * 1.2, c=0.0)
    m.box(-7.0, -6.85, 2.15, 2.35, 0.25, "glow_red", c=0.01)

    # ---------------------------------------------------------- skids
    for s in (-1, 1):
        x = s * 1.45
        m.limb((x, -2.3, 0.1), (x, 2.9, 0.1), 0.07, 0.07, "gunmetal", sides=8)
        m.limb((x, 2.9, 0.1), (x, 3.35, 0.35), 0.07, 0.06, "gunmetal", sides=8)
        m.limb((x, -2.3, 0.1), (x, -2.55, 0.22), 0.07, 0.06, "gunmetal", sides=8)
        for f in (2.0, -1.2):
            m.limb((s * 0.95, f, 0.85), (x, f + 0.15, 0.12), 0.11, 0.08, "graphite", sides=6)
            m.box(f - 0.12, f + 0.12, 0.08, 0.3, 0.24, "gunmetal", x=x, c=0.04)
            m.box(f - 0.05, f + 0.05, 0.5, 0.56, 0.04, "glow_amber", x=s * 1.2, c=0.0)
        for f in (-2.0, -0.4, 1.0, 2.6):
            m.xcyl(f, 0.1, x - 0.075, x + 0.075, 0.08, "polymer", sides=8, detail=True)
    # Baked hull detail: bolts and seams on the top.
    for f in (2.3, 1.3, 0.3, -0.7, -1.7):
        bolt_u(m, 0.68, f, 2.82, r=0.02)
        bolt_u(m, -0.68, f, 2.82, r=0.02)
    plate_u(m, [(-0.2, -3.0), (0.2, -3.0), (0.2, -5.8), (-0.2, -5.8)], 2.4, "graphite", depth=0.006)

    m.marker("seat", f=3.05, u=2.05, x=-0.48)          # pilot eye
    m.marker("seat_passenger", f=3.05, u=2.05, x=0.48)
    m.marker("seat_rear_l", f=0.0, u=2.05, x=-0.6)
    m.marker("seat_rear_r", f=0.0, u=2.05, x=0.6)
    m.marker("exit", f=0.5, u=0.1, x=-2.2)
    m.marker("exit_r", f=0.5, u=0.1, x=2.2)
    pivots = {"rotor-l": (-DUCT_X, DUCT_F, DUCT_U), "rotor-r": (DUCT_X, DUCT_F, DUCT_U)}
    return m.finish(BUDGET, texture_size=2048, before_export=origins("kestrel", pivots))
