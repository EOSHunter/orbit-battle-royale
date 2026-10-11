"""SR-8 Longview: bolt-action sniper. Concept: codex/concepts/v0.2/08-sr-8-longview.png.

Origin at the top of the pistol grip. Navy chassis with lime stripes, skeletal
stock, long fluted barrel with a big brake, a long scope with an amber lens,
folded bipod. Bolt and magazine are separate objects for animation later.
Plates, screws, flutes and vents marked detail-only are baked into the textures.
"""

from kit import Model

BUDGET = (500, 1500)


def build():
    m = Model("sr-8-longview")

    # Stock: buttpad, upright with lime insert, top bar, cheek rest, lower bar, strut.
    m.box(-0.47, -0.435, -0.10, 0.065, 0.046, "polymer", c=0.01)
    m.box(-0.44, -0.40, -0.10, 0.06, 0.044, "graphite", c=0.006)
    m.box(-0.432, -0.418, -0.07, 0.03, 0.046, "lime", c=0.002)
    m.box(-0.42, -0.15, 0.02, 0.05, 0.04, "graphite", c=0.005)
    m.box(-0.36, -0.22, 0.05, 0.08, 0.036, "polymer", c=0.008)
    m.box(-0.33, -0.25, 0.042, 0.052, 0.03, "gunmetal", c=0.002)            # cheek riser post
    m.box(-0.42, -0.24, -0.11, -0.09, 0.03, "gunmetal", c=0.004)
    m.prism([(-0.26, -0.11), (-0.22, -0.11), (-0.08, -0.03), (-0.12, -0.03)], 0.03, "gunmetal")
    m.plate(-0.40, -0.17, 0.025, 0.045, 0.02, "graphite")
    m.plate(-0.46, -0.44, -0.09, 0.055, 0.023, "polymer")
    for f, u in ((-0.41, 0.035), (-0.16, 0.035), (-0.41, -0.085), (-0.25, -0.1)):
        m.screw(f, u, 0.022 if u > 0 else 0.015)

    # Chassis.
    m.prism([(-0.16, -0.035), (0.36, -0.035), (0.39, -0.015), (0.39, 0.045), (0.32, 0.058), (-0.16, 0.058)], 0.056, "graphite")
    m.prism([(-0.02, 0.028), (0.30, 0.028), (0.29, 0.042), (-0.01, 0.042)], 0.0565, "lime")
    for f in (0.16, 0.22, 0.28):
        m.box(f, f + 0.04, -0.02, 0.008, 0.0575, "polymer", c=0.006)
    m.box(0.325, 0.375, -0.003, 0.013, 0.0568, "gunmetal", c=0.003)
    m.box(0.33, 0.37, 0.0, 0.01, 0.0575, "glow_amber", c=0.002)
    m.plate(-0.15, -0.03, -0.028, 0.02, 0.028, "graphite")
    m.plate(-0.15, 0.38, -0.035, -0.026, 0.028, "gunmetal", c=0.0)
    for f, u in ((-0.145, 0.05), (-0.145, -0.02), (0.38, 0.03), (0.13, -0.02), (0.05, -0.02)):
        m.screw(f, u, 0.028)

    # Bolt: body and handle with knob.
    m.cyl(-0.15, 0.15, 0.062, 0.02, "gunmetal", group="bolt")
    m.xcyl(-0.11, 0.055, 0.02, 0.07, 0.006, "steel", sides=8, group="bolt")
    m.xcyl(-0.11, 0.055, 0.065, 0.088, 0.013, "polymer", sides=12, group="bolt")
    m.vents(-0.12, 0.12, 0.074, 0.082, 0.0195, 8, "steel", group="bolt")

    # Scope: rings, tube, eyepiece, bell, objective, lens, turrets.
    for f in (-0.03, 0.13):
        m.box(f, f + 0.025, 0.07, 0.112, 0.034, "polymer", c=0.004)
        m.screw(f + 0.0125, 0.1, 0.017, r=0.0025)
    m.cyl(-0.10, 0.25, 0.125, 0.018, "polymer", sides=12)
    m.cyl(-0.17, -0.10, 0.125, 0.026, "polymer", sides=12, r1=0.018)
    m.cyl(-0.175, -0.17, 0.125, 0.026, "glow_amber", sides=12)
    m.cyl(0.25, 0.31, 0.125, 0.018, "polymer", sides=12, r1=0.032)
    m.cyl(0.31, 0.35, 0.125, 0.032, "polymer", sides=12)
    m.cyl(0.325, 0.333, 0.125, 0.0325, "lime", sides=12)
    m.tube(0.35, 0.356, 0.125, 0.032, 0.027, "gunmetal", sides=12)
    m.cyl(0.345, 0.35, 0.125, 0.027, "lens", sides=12)
    m.vcyl(0.06, 0.14, 0.168, 0.014, "gunmetal", sides=10)
    m.vcyl(0.06, 0.164, 0.17, 0.0145, "glow_amber", sides=10)
    m.xcyl(0.06, 0.125, 0.015, 0.036, 0.012, "gunmetal", sides=10)
    m.xcyl(0.06, 0.125, -0.036, -0.015, 0.012, "gunmetal", sides=10)

    # Fluted barrel and ported brake.
    m.cyl(0.39, 0.92, 0.02, 0.013, "gunmetal", sides=10)
    m.plate(0.42, 0.88, 0.016, 0.024, 0.013, "steel", c=0.0, depth=0.001)
    m.cyl(0.88, 0.92, 0.02, 0.0145, "gunmetal", sides=10)
    m.box(0.92, 1.0, -0.002, 0.042, 0.042, "polymer", c=0.006)
    for f in (0.935, 0.962):
        m.box(f, f + 0.014, 0.004, 0.036, 0.0435, "gunmetal", c=0.0, detail=True)

    # Folded bipod.
    for x in (-0.012, 0.012):
        m.cyl(0.36, 0.64, -0.05, 0.008, "gunmetal", sides=8, x=x)
        m.cyl(0.64, 0.66, -0.05, 0.011, "polymer", sides=8, x=x)
    m.xcyl(0.37, -0.04, -0.026, 0.026, 0.016, "polymer", sides=10)
    m.screw(0.37, -0.04, 0.026, r=0.005)

    # Magazine, grip, trigger guard.
    m.box(0.04, 0.12, -0.13, -0.035, 0.046, "polymer", c=0.006, group="magazine")
    m.box(0.035, 0.125, -0.142, -0.126, 0.05, "graphite", c=0.004, group="magazine")
    m.plate(0.05, 0.11, -0.12, -0.05, 0.023, "graphite", group="magazine")
    m.prism([(-0.035, -0.035), (0.03, -0.035), (0.02, -0.065), (-0.012, -0.152), (-0.064, -0.152), (-0.052, -0.08)], 0.034, "polymer")
    m.prism([(-0.03, -0.048), (0.012, -0.048), (-0.012, -0.135), (-0.052, -0.135), (-0.044, -0.08)], 0.0355, "polymer", detail=True)
    m.box(0.0, 0.035, -0.072, -0.062, 0.012, "gunmetal", c=0.002)
    m.prism([(0.012, -0.035), (0.02, -0.035), (0.024, -0.058), (0.016, -0.06)], 0.008, "steel")

    m.marker("muzzle", f=1.0, u=0.02)
    m.marker("grip", f=0.0, u=0.0)
    m.marker("sight", f=-0.175, u=0.125)
    return m.finish(BUDGET)
