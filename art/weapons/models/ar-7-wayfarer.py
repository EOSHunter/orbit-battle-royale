"""AR-7 Wayfarer: assault rifle. Concept: codex/concepts/v0.2/04-ar-7-wayfarer.png.

Origin at the top of the pistol grip; the muzzle points forward (-Y in Blender).
Navy armor panels over graphite metal, a pale lime diagonal on the handguard,
a large box magazine (separate object for reload animation later), amber light.
Plates, screws and vents marked detail-only are baked into the textures.
"""

from kit import Model

BUDGET = (500, 1500)


def build():
    m = Model("ar-7-wayfarer")

    # Stock: skeletal frame with a ribbed rubber buttpad.
    m.box(-0.40, -0.365, -0.10, 0.068, 0.046, "polymer", c=0.012)
    for i in range(6):
        u = -0.09 + i * 0.027
        m.box(-0.405, -0.398, u, u + 0.016, 0.042, "polymer", c=0.002)
    m.prism([(-0.37, -0.005), (-0.13, -0.005), (-0.09, 0.02), (-0.09, 0.075), (-0.30, 0.078), (-0.37, 0.062)], 0.04, "graphite")
    m.prism([(-0.37, -0.10), (-0.33, -0.10), (-0.11, -0.02), (-0.11, 0.012), (-0.15, 0.012), (-0.37, -0.06)], 0.034, "gunmetal")
    m.prism([(-0.372, -0.085), (-0.355, -0.085), (-0.355, 0.0), (-0.372, 0.0)], 0.036, "gunmetal")
    m.plate(-0.33, -0.16, 0.012, 0.064, 0.02, "graphite")
    m.plate(-0.345, -0.30, 0.02, 0.06, 0.02, "gunmetal")
    for f, u in ((-0.355, 0.045), (-0.12, 0.045), (-0.32, -0.07), (-0.14, -0.01)):
        m.screw(f, u, 0.02 if u > 0 else 0.017)

    # Receiver and upper.
    m.prism([(-0.10, -0.03), (0.20, -0.03), (0.22, -0.01), (0.22, 0.075), (0.20, 0.085), (-0.08, 0.085), (-0.10, 0.065)], 0.06, "graphite")
    m.box(-0.09, 0.21, 0.075, 0.096, 0.05, "gunmetal", c=0.006)
    m.box(-0.02, 0.13, -0.022, 0.035, 0.0625, "gunmetal", c=0.008)            # side plate
    m.box(-0.075, 0.055, 0.05, 0.071, 0.061, "gunmetal", c=0.004)             # light bezel
    m.box(-0.07, 0.05, 0.054, 0.067, 0.0618, "glow_amber", c=0.003)           # status light
    m.box(-0.03, 0.01, 0.028, 0.048, 0.016, "steel", x=0.037)                 # charging handle
    m.xcyl(0.11, 0.06, 0.03, 0.036, 0.008, "steel", sides=8)                  # selector
    m.plate(-0.088, -0.03, -0.018, 0.045, 0.03, "graphite")
    m.plate(0.14, 0.205, -0.02, 0.065, 0.03, "graphite")
    m.plate(-0.08, 0.20, -0.03, -0.02, 0.03, "gunmetal", c=0.0)
    m.plate(0.03, 0.11, 0.0, 0.025, 0.0313, "polymer")                        # ejection port
    for f, u in ((-0.012, -0.012), (-0.012, 0.026), (0.122, -0.012), (0.122, 0.026)):
        m.screw(f, u, 0.0313, r=0.0026)
    for f, u in ((-0.092, 0.0), (-0.092, 0.055), (0.21, 0.068), (0.21, -0.018)):
        m.screw(f, u, 0.03)

    # Top rail with teeth, and flip-up sights.
    m.box(-0.06, 0.40, 0.095, 0.108, 0.026, "polymer", c=0.002)
    for i in range(9):
        f = -0.04 + i * 0.045
        m.box(f, f + 0.022, 0.108, 0.116, 0.028, "polymer", c=0.002)
    # Iron sights on the rail: ghost ring rear, thin post front, sight line at 0.136.
    m.rear_aperture(-0.04, 0.136, 0.116)
    m.front_post(0.36, 0.136, 0.116)

    # Handguard with the lime diagonal, vents and an end cap.
    m.prism([(0.22, -0.025), (0.44, -0.025), (0.465, -0.005), (0.465, 0.07), (0.44, 0.09), (0.22, 0.09)], 0.066, "graphite")
    m.prism([(0.28, -0.025), (0.312, -0.025), (0.37, 0.09), (0.338, 0.09)], 0.0675, "lime")
    for f in (0.385, 0.42):
        m.box(f, f + 0.028, 0.045, 0.06, 0.068, "polymer", c=0.006)
        m.box(f, f + 0.028, 0.008, 0.02, 0.068, "polymer", c=0.005)
    m.box(0.455, 0.475, -0.012, 0.08, 0.07, "gunmetal", c=0.008)
    m.plate(0.228, 0.275, -0.015, 0.08, 0.033, "graphite")
    m.plate(0.38, 0.452, 0.065, 0.085, 0.033, "gunmetal")
    for f, u in ((0.232, 0.08), (0.232, -0.015), (0.448, 0.075), (0.448, -0.01)):
        m.screw(f, u, 0.033)
    m.prism([(0.16, -0.03), (0.40, -0.03), (0.42, -0.048), (0.40, -0.066), (0.18, -0.066)], 0.05, "polymer")
    m.vents(0.2, 0.39, -0.058, -0.038, 0.025, 10)

    # Barrel and ported muzzle brake.
    m.cyl(0.46, 0.525, 0.035, 0.013, "gunmetal")
    m.box(0.52, 0.59, 0.013, 0.057, 0.04, "polymer", c=0.009)
    m.tube(0.59, 0.594, 0.035, 0.016, 0.008, "gunmetal")
    m.vents(0.53, 0.58, 0.026, 0.044, 0.02, 3, "gunmetal")

    # Pistol grip with a stippled panel, trigger guard, trigger.
    m.prism([(-0.035, -0.03), (0.03, -0.03), (0.02, -0.062), (-0.012, -0.152), (-0.064, -0.152), (-0.052, -0.08)], 0.034, "polymer")
    m.prism([(-0.03, -0.045), (0.012, -0.045), (-0.012, -0.135), (-0.052, -0.135), (-0.044, -0.08)], 0.0355, "polymer", detail=True)
    m.box(0.02, 0.095, -0.072, -0.062, 0.012, "gunmetal", c=0.002)
    m.box(0.085, 0.095, -0.072, -0.03, 0.012, "gunmetal", c=0.002)
    m.prism([(0.036, -0.03), (0.046, -0.03), (0.05, -0.06), (0.044, -0.062)], 0.008, "steel")

    # Magazine: its own object so it can be animated on reload.
    m.prism([(0.07, -0.03), (0.17, -0.03), (0.175, -0.05), (0.19, -0.19), (0.085, -0.19), (0.07, -0.05)], 0.052, "polymer", group="magazine")
    m.prism([(0.075, -0.18), (0.195, -0.18), (0.195, -0.2), (0.085, -0.2)], 0.056, "gunmetal", group="magazine")
    m.prism([(0.10, -0.055), (0.118, -0.055), (0.112, -0.16), (0.094, -0.16)], 0.054, "lime", group="magazine")
    m.prism([(0.125, -0.05), (0.168, -0.05), (0.18, -0.17), (0.135, -0.17)], 0.0535, "polymer", group="magazine", detail=True)
    m.prism([(0.132, -0.06), (0.162, -0.06), (0.172, -0.16), (0.142, -0.16)], 0.0542, "gunmetal", group="magazine", detail=True)

    m.marker("muzzle", f=0.594, u=0.035)
    m.marker("grip", f=0.0, u=0.0)
    return m.finish(BUDGET)
