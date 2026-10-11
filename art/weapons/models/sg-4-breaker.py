"""SG-4 Breaker: pump shotgun. Concept: codex/concepts/v0.2/05-sg-4-breaker.png.

Origin at the top of the pistol grip. Brown furniture, gunmetal receiver, a long
vented navy shroud over the barrel, an under-barrel tube and a ribbed pump
(separate object for the pump animation later), amber lights.
Plates, screws and vents marked detail-only are baked into the textures.
"""

from kit import Model

BUDGET = (500, 1500)


def build():
    m = Model("sg-4-breaker")

    # Stock: brown shell with a cut-out, ribbed pad, amber light.
    m.box(-0.43, -0.39, -0.11, 0.058, 0.05, "polymer", c=0.012)
    for i in range(6):
        u = -0.1 + i * 0.027
        m.box(-0.432, -0.428, u, u + 0.016, 0.046, "polymer", c=0.0, detail=True)
    m.prism([(-0.395, -0.10), (-0.30, -0.10), (-0.14, -0.03), (-0.10, -0.03), (-0.10, 0.06), (-0.37, 0.062), (-0.395, 0.05)], 0.045, "brown")
    m.prism([(-0.33, -0.065), (-0.27, -0.065), (-0.19, -0.02), (-0.33, -0.02)], 0.047, "polymer")
    m.box(-0.365, -0.295, 0.022, 0.038, 0.0455, "gunmetal", c=0.003)
    m.box(-0.36, -0.30, 0.026, 0.034, 0.0462, "glow_amber", c=0.002)
    m.box(-0.12, -0.06, -0.012, 0.06, 0.04, "polymer", c=0.006)
    m.plate(-0.38, -0.34, -0.09, 0.0, 0.0225, "polymer")
    for f, u in ((-0.375, 0.045), (-0.115, 0.045), (-0.29, -0.085), (-0.115, -0.02)):
        m.screw(f, u, 0.0225)

    # Receiver with ejection port, plates and rail.
    m.prism([(-0.08, -0.035), (0.20, -0.035), (0.20, 0.09), (-0.05, 0.09), (-0.08, 0.06)], 0.066, "gunmetal")
    m.box(0.0, 0.12, 0.035, 0.066, 0.068, "polymer", c=0.012)
    m.box(0.012, 0.108, 0.041, 0.06, 0.069, "steel", c=0.008)               # bolt face in the port
    m.box(0.125, 0.165, 0.014, 0.032, 0.0675, "gunmetal", c=0.004)
    m.box(0.13, 0.16, 0.018, 0.028, 0.0682, "glow_amber", c=0.002)
    m.box(0.07, 0.11, -0.015, 0.005, 0.0675, "polymer", c=0.004)             # shell latch
    m.plate(-0.07, -0.005, -0.025, 0.08, 0.033, "graphite")
    m.plate(0.13, 0.195, 0.04, 0.08, 0.033, "graphite")
    m.plate(-0.05, 0.19, -0.035, -0.025, 0.033, "steel", c=0.0)
    for f, u in ((-0.06, 0.07), (-0.06, -0.015), (0.188, 0.07), (0.188, -0.022), (0.03, -0.022)):
        m.screw(f, u, 0.033)
    m.box(-0.02, 0.22, 0.09, 0.103, 0.026, "polymer", c=0.002)
    for i in range(5):
        f = 0.0 + i * 0.045
        m.box(f, f + 0.022, 0.103, 0.111, 0.028, "polymer", c=0.002)
    # Iron sights: notch on the rail, thin post with an amber bead on the shroud; line at 0.124.
    m.rear_notch(-0.03, 0.124, 0.111)

    # Barrel shroud with vents, clamp band and light.
    m.prism([(0.20, 0.0), (0.66, 0.0), (0.68, 0.02), (0.68, 0.08), (0.66, 0.092), (0.20, 0.092)], 0.06, "graphite")
    for f in (0.29, 0.37, 0.45):
        m.prism([(f, 0.045), (f + 0.05, 0.045), (f + 0.06, 0.068), (f + 0.01, 0.068)], 0.062, "polymer")
    m.box(0.55, 0.585, -0.085, 0.098, 0.07, "gunmetal", c=0.008)
    m.box(0.598, 0.668, 0.036, 0.054, 0.061, "gunmetal", c=0.004)
    m.box(0.603, 0.663, 0.04, 0.05, 0.0618, "glow_amber", c=0.002)
    m.front_post(0.615, 0.124, 0.092, bead="glow_amber", ears=False)
    m.plate(0.21, 0.28, 0.008, 0.085, 0.03, "graphite")
    m.plate(0.50, 0.545, 0.008, 0.085, 0.03, "graphite")
    m.plate(0.21, 0.66, 0.0, 0.01, 0.03, "gunmetal", c=0.0)
    for f, u in ((0.218, 0.078), (0.218, 0.016), (0.54, 0.078), (0.54, 0.016)):
        m.screw(f, u, 0.03)
    m.screw(0.567, 0.075, 0.035)
    m.screw(0.567, -0.065, 0.035)

    # Barrel muzzle and magazine tube.
    m.cyl(0.66, 0.73, 0.045, 0.031, "polymer", sides=14)
    m.cyl(0.70, 0.71, 0.045, 0.0325, "gunmetal", sides=14)
    m.tube(0.73, 0.738, 0.045, 0.031, 0.019, "gunmetal", sides=14)
    m.cyl(0.20, 0.71, -0.045, 0.028, "polymer", sides=12)
    m.cyl(0.71, 0.728, -0.045, 0.024, "gunmetal", sides=12)

    # Pump: its own object, ribbed brown grip with end caps.
    m.box(0.26, 0.50, -0.086, -0.004, 0.07, "brown", c=0.012, group="pump")
    for i in range(7):
        f = 0.285 + i * 0.03
        m.box(f, f + 0.012, -0.088, -0.002, 0.0725, "polymer", c=0.002, group="pump")
    for f in (0.255, 0.49):
        m.box(f, f + 0.015, -0.09, 0.0, 0.074, "gunmetal", c=0.006, group="pump")

    # Grip, trigger guard, amber trigger.
    m.prism([(-0.04, -0.035), (0.03, -0.035), (0.015, -0.07), (-0.022, -0.16), (-0.076, -0.16), (-0.062, -0.08)], 0.036, "brown")
    m.prism([(-0.03, -0.06), (0.002, -0.06), (-0.026, -0.14), (-0.056, -0.14)], 0.038, "polymer")
    m.prism([(-0.026, -0.066), (-0.004, -0.066), (-0.028, -0.134), (-0.05, -0.134)], 0.0388, "polymer", detail=True)
    m.box(0.02, 0.095, -0.077, -0.067, 0.012, "gunmetal", c=0.002)
    m.box(0.085, 0.095, -0.077, -0.035, 0.012, "gunmetal", c=0.002)
    m.prism([(0.04, -0.035), (0.05, -0.035), (0.054, -0.065), (0.046, -0.067)], 0.008, "glow_amber")

    m.marker("muzzle", f=0.738, u=0.045)
    m.marker("grip", f=0.0, u=0.0)
    return m.finish(BUDGET)
