"""Skimmer: one-seat hover bike, fast and exposed. Concept: codex/concepts/v0.2/22-skimmer.png.

Origin on the ground under the center of the bike; faces forward (-Y in Blender).
A slim navy-graphite spine with lime chevrons, smoked windscreen, black saddle and a
tall rear frame with an amber tail light, riding on four puck-shaped hover pads
(front and rear pairs) with glowing amber undersides on hydraulic struts.
Groups: bars (handlebars, pivot at the steering head), pad-fl/fr/rl/rr (pads,
origin at each pad center so they can tilt and bob).
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vkit import (bolt_u, bolt_x, circle_u, octo, origins, plate_u, plate_x,  # noqa: E402
                   torus, utube, vents_x)
from kit import Model  # noqa: E402

BUDGET = (3000, 6000)

PODS = {"pad-fl": (-0.62, 1.22), "pad-fr": (0.62, 1.22), "pad-rl": (-0.62, -1.18), "pad-rr": (0.62, -1.18)}
PU = 0.3        # pad bottom height while hovering
STEER = (0.0, 0.85, 1.2)


def pad(m, x, f, group):
    """Puck-shaped hover pad: banded armor shell, glowing underside, lime status light."""
    s = 1 if x >= 0 else -1
    n = 16
    sf = 1.12
    prof = [(PU + 0.03, 0.3), (PU, 0.36), (PU + 0.06, 0.43), (PU + 0.17, 0.45), (PU + 0.22, 0.41), (PU + 0.25, 0.3)]
    m.loft([circle_u(x, f, u, r, n, sf=sf) for u, r in prof], "graphite", group=group, name="pad")
    utube(m, x, f, PU - 0.015, PU + 0.03, 0.34, 0.24, "glow_amber", sides=n, group=group, sf=sf)    # glow ring
    m.vcyl(f, PU - 0.01, PU + 0.03, 0.2, "gunmetal", sides=10, x=x, group=group)                   # emitter
    utube(m, x, f, PU + 0.24, PU + 0.28, 0.24, 0.12, "gunmetal", sides=12, group=group, sf=sf)       # top hub ring
    m.vcyl(f, PU + 0.24, PU + 0.3, 0.1, "steel", sides=8, x=x, group=group)
    # Outer status strip (lime), front/back amber marker lights.
    m.side_box(f - 0.16, f + 0.16, PU + 0.11, PU + 0.15, x + s * 0.43, x + s * 0.47, "glow_lime", c=0.01, group=group)
    m.side_box(f - 0.2, f + 0.2, PU + 0.09, PU + 0.17, x + s * 0.4, x + s * 0.452, "polymer", c=0.02, group=group)
    # Baked: armor band seams, bolts around the top, vents on the band.
    for k in range(8):
        a = 2 * math.pi * (k + 0.25) / 8
        px, pf = x + math.cos(a) * 0.36, f + math.sin(a) * 0.36 * sf
        bolt_u(m, px, pf, PU + 0.22 + 0.0, r=0.012, group=group)
        seam = m.box(pf - 0.012, pf + 0.012, PU + 0.06, PU + 0.21, 0.02, "gunmetal", x=x + math.cos(a) * 0.445, c=0.0, group=group, detail=True)
        m.transform(seam, rotate=(0, 0, -math.degrees(a)), pivot=(x + math.cos(a) * 0.445, pf, 0))
    utube(m, x, f, PU + 0.235, PU + 0.25, 0.4, 0.37, "polymer", sides=n, group=group, detail=True, sf=sf)


def build():
    m = Model("skimmer", category="vehicles", bevel=0.01, cage=0.02)

    # ---------------------------------------------------------- spine
    rings = [octo(1.82, 0.08, 0.86, 0.94, 0.03),
             octo(1.6, 0.22, 0.76, 1.02, 0.07, 0.08),
             octo(1.15, 0.33, 0.66, 1.16, 0.1, 0.12),
             octo(0.62, 0.36, 0.56, 1.2, 0.12, 0.12),
             octo(0.15, 0.3, 0.55, 1.02, 0.1, 0.08),
             octo(-0.55, 0.27, 0.58, 1.0, 0.1, 0.08),
             octo(-1.05, 0.22, 0.66, 1.0, 0.08, 0.06),
             octo(-1.3, 0.12, 0.76, 0.96, 0.04, 0.04)]
    m.loft(rings, "graphite", name="spine")
    # Nose armor cowl: graphite shell over the front with lime chevrons.
    cowl = [octo(1.7, 0.18, 0.92, 1.03, 0.0, 0.06), octo(1.2, 0.335, 1.0, 1.19, 0.0, 0.12), octo(0.75, 0.37, 1.02, 1.23, 0.0, 0.12)]
    m.loft(cowl, "graphite", name="cowl")
    for s in (-1, 1):
        m.prism([(1.05, 0.98), (1.25, 0.98), (1.0, 1.2), (0.8, 1.2)], 0.02, "lime", x=s * 0.345)
        m.prism([(0.35, 0.62), (0.55, 0.62), (0.35, 1.0), (0.15, 1.0)], 0.02, "lime", x=s * 0.32)
    # Headlight slit and lower amber strip.
    m.prism([(1.62, 0.9), (1.8, 0.89), (1.82, 0.92), (1.64, 0.94)], 0.3, "glow_amber")
    m.box(1.38, 1.56, 0.74, 0.78, 0.3, "glow_amber", c=0.01)
    m.box(1.3, 1.6, 0.7, 0.8, 0.36, "polymer", c=0.03)
    vents_x(m, 1.25, 1.5, 0.84, 0.94, 0.27, 5)
    # Belly engine block: angular hanging pod.
    m.prism([(-0.35, 0.62), (0.75, 0.62), (0.6, 0.38), (0.3, 0.3), (-0.2, 0.36)], 0.5, "graphite")
    m.prism([(-0.25, 0.58), (0.6, 0.58), (0.5, 0.42), (0.25, 0.36), (-0.15, 0.4)], 0.54, "navy")
    m.box(-0.1, 0.3, 0.34, 0.37, 0.3, "glow_amber", c=0.01)                    # belly glow
    vents_x(m, -0.15, 0.45, 0.45, 0.55, 0.27, 8)
    # Side armor plates over the frame.
    for s in (-1, 1):
        m.prism([(-0.9, 0.7), (-0.2, 0.62), (0.1, 0.72), (0.1, 0.98), (-0.55, 1.02), (-0.9, 0.95)], 0.03, "graphite", x=s * 0.3)
        m.prism([(-0.8, 0.85), (-0.55, 0.85), (-0.45, 0.98), (-0.7, 0.98)], 0.035, "lime", x=s * 0.3)
        m.box(-0.5, -0.2, 0.7, 0.73, 0.02, "glow_amber", x=s * 0.315, c=0.0)
        for f, u in ((-0.85, 0.75), (-0.85, 0.92), (0.05, 0.76), (0.05, 0.94), (-0.4, 0.68)):
            bolt_x(m, f, u, s * 0.317, r=0.01)
        plate_x(m, [(0.7, 0.75), (1.1, 0.8), (1.1, 0.95), (0.7, 0.95)], 0.36, "graphite")

    # ---------------------------------------------------------- saddle and tail frame
    seat = [octo(0.25, 0.2, 1.0, 1.08, 0.02, 0.05), octo(-0.1, 0.24, 0.96, 1.06, 0.02, 0.06),
            octo(-0.6, 0.24, 0.98, 1.12, 0.02, 0.06), octo(-0.9, 0.22, 1.02, 1.22, 0.02, 0.07)]
    m.loft(seat, "seat", name="seat")
    for i in range(6):
        plate_u(m, [(-0.2, -0.05 - i * 0.12), (0.2, -0.05 - i * 0.12), (0.2, -0.09 - i * 0.12), (-0.2, -0.09 - i * 0.12)], 1.06, "polymer", depth=0.006)
    for s in (-1, 1):
        m.limb((s * 0.2, -0.85, 0.95), (s * 0.18, -1.32, 1.42), 0.035, 0.03, "gunmetal", sides=6)
        m.limb((s * 0.22, -1.0, 0.72), (s * 0.18, -1.32, 1.42), 0.03, 0.03, "gunmetal", sides=6)
    m.box(-1.45, -1.22, 1.38, 1.48, 0.46, "graphite", c=0.03)                 # tail bar
    m.box(-1.47, -1.44, 1.4, 1.46, 0.36, "glow_amber", c=0.0)
    m.box(-1.36, -1.28, 1.48, 1.5, 0.3, "lime", c=0.0, detail=True)

    # ---------------------------------------------------------- struts to the pads
    for name, (x, f) in PODS.items():
        s = 1 if x >= 0 else -1
        root = (s * 0.26, f * 0.55, 0.72)
        knee = (x - s * 0.22, f, PU + 0.32)
        m.limb(root, knee, 0.05, 0.04, "gunmetal", sides=6)
        mid = [root[i] + (knee[i] - root[i]) * 0.35 for i in range(3)]
        mid2 = [root[i] + (knee[i] - root[i]) * 0.65 for i in range(3)]
        m.limb(mid, mid2, 0.065, 0.065, "polymer", sides=8)                   # piston sleeve
        g0 = [root[i] + (knee[i] - root[i]) * 0.42 for i in range(3)]
        g1 = [root[i] + (knee[i] - root[i]) * 0.58 for i in range(3)]
        m.limb(g0, g1, 0.07, 0.07, "glow_amber", sides=8)                     # glow band
        m.sphere(f, PU + 0.32, 0.075, "gunmetal", x=x - s * 0.22, segments=8, rings=5)
        m.sphere(f * 0.55, 0.72, 0.07, "gunmetal", x=s * 0.26, segments=8, rings=5)
        # Second link for a hydraulic look.
        m.limb((s * 0.24, f * 0.7, 0.6), (x - s * 0.3, f, PU + 0.24), 0.03, 0.03, "steel", sides=6)
        pad(m, x, f, name)

    # ---------------------------------------------------------- cockpit: bars, screen, display
    m.vcyl(0.85, 1.12, 1.22, 0.06, "gunmetal", sides=8, group="bars")       # steering head
    m.box(0.72, 0.86, 1.18, 1.27, 0.24, "polymer", c=0.03, group="bars")      # clamp
    m.limb((-0.12, 0.8, 1.24), (-0.46, 0.72, 1.3), 0.026, 0.024, "gunmetal", sides=6, group="bars")
    m.limb((0.12, 0.8, 1.24), (0.46, 0.72, 1.3), 0.026, 0.024, "gunmetal", sides=6, group="bars")
    for s in (-1, 1):
        m.limb((s * 0.36, 0.735, 1.287), (s * 0.52, 0.71, 1.31), 0.034, 0.034, "rubber", sides=8, group="bars")
        m.box(0.69, 0.79, 1.27, 1.33, 0.08, "polymer", x=s * 0.3, c=0.015, group="bars")     # switch pod
        m.box(0.785, 0.8, 1.285, 1.315, 0.06, "glow_amber" if s < 0 else "glow_red", x=s * 0.3, c=0.0, group="bars")
        m.box(0.62, 0.66, 1.27, 1.29, 0.12, "gunmetal", x=s * 0.44, c=0.0, group="bars")      # levers
    m.box(0.82, 0.92, 1.22, 1.3, 0.24, "polymer", c=0.02, group="bars")       # display
    m.box(0.81, 0.83, 1.24, 1.28, 0.18, "glow_cyan", c=0.0, group="bars", detail=True)
    shape = [(-0.24, 0.0), (0.24, 0.0), (0.26, 0.2), (0.12, 0.36), (-0.12, 0.36), (-0.26, 0.2)]
    screen = m.front_prism([(x, 1.17 + u) for x, u in shape], 0.95, 0.985, "tinted_glass")
    m.transform(screen, rotate=(-38, 0, 0), pivot=(0, 0.97, 1.17))
    m.box(0.93, 0.95, 1.16, 1.2, 0.46, "polymer", c=0.0)
    m.box(0.95, 1.05, 1.19, 1.26, 0.06, "glow_amber", c=0.01)                # top marker in front of screen

    # Baked spine detail.
    for f in (1.4, 1.0, 0.5):
        bolt_u(m, 0.0, f, 1.2 if f < 1.2 else 1.1, r=0.01)
    for s in (-1, 1):
        plate_x(m, [(-1.2, 0.78), (-0.95, 0.72), (-0.95, 0.9), (-1.2, 0.92)], 0.24, "graphite", mirror=False) if s > 0 else None

    m.marker("seat", f=-0.3, u=1.78)          # rider eye
    m.marker("exit", f=-0.2, u=0.1, x=-1.3)
    pivots = {name: (x, f, PU + 0.15) for name, (x, f) in PODS.items()}
    pivots["bars"] = STEER
    return m.finish(BUDGET, texture_size=2048, before_export=origins("skimmer", pivots))
