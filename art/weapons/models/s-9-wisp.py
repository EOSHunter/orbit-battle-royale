"""S-9 Wisp: SMG. Concept: codex/concepts/v0.2/07-s-9-wisp.png.

Origin at the top of the pistol grip. Ivory panels over a dark polymer body,
a translucent amber magazine lying along the top (separate object), vertical
foregrip, skeletal folding stock with a lime accent.
Plates, screws and vents marked detail-only are baked into the textures.
"""

from kit import Model

BUDGET = (500, 1500)


def build():
    m = Model("s-9-wisp")

    # Stock: tube, skeletal ivory frame, rubber pad.
    m.cyl(-0.21, -0.08, 0.045, 0.012, "gunmetal")
    m.cyl(-0.10, -0.08, 0.045, 0.016, "polymer")
    m.box(-0.36, -0.20, 0.03, 0.062, 0.03, "ivory", c=0.006)
    m.prism([(-0.36, -0.10), (-0.33, -0.10), (-0.21, 0.035), (-0.245, 0.035)], 0.028, "ivory")
    m.prism([(-0.29, -0.04), (-0.27, -0.04), (-0.235, 0.0), (-0.255, 0.0)], 0.0295, "lime")
    m.box(-0.385, -0.355, -0.11, 0.07, 0.04, "polymer", c=0.008)
    for i in range(6):
        u = -0.1 + i * 0.028
        m.box(-0.39, -0.383, u, u + 0.016, 0.036, "polymer", c=0.002)
    m.box(-0.36, -0.30, -0.11, -0.092, 0.026, "polymer", c=0.004)
    m.plate(-0.34, -0.22, 0.036, 0.056, 0.015, "ivory")
    for f, u in ((-0.35, 0.046), (-0.21, 0.046), (-0.345, -0.09)):
        m.screw(f, u, 0.015 if u > 0 else 0.014)

    # Receiver and ivory upper/handguard.
    m.prism([(-0.08, -0.03), (0.10, -0.03), (0.12, -0.012), (0.12, 0.062), (-0.08, 0.062)], 0.05, "polymer")
    m.prism([(-0.07, 0.012), (0.02, 0.012), (0.04, 0.03), (0.04, 0.07), (-0.07, 0.07)], 0.0505, "ivory")
    m.box(-0.065, -0.02, 0.031, 0.049, 0.0508, "gunmetal", c=0.004)
    m.box(-0.06, -0.025, 0.035, 0.045, 0.0514, "glow_amber", c=0.002)
    m.box(0.0, 0.035, 0.02, 0.034, 0.016, "steel", x=0.03, c=0.003)           # charging handle
    m.plate(-0.075, 0.1, -0.025, 0.005, 0.025, "graphite")
    for f, u in ((-0.07, -0.02), (0.09, -0.02), (0.03, 0.058)):
        m.screw(f, u, 0.0255)
    m.prism([(0.10, -0.022), (0.32, -0.022), (0.345, 0.0), (0.345, 0.062), (0.32, 0.074), (0.10, 0.074)], 0.056, "ivory")
    for f in (0.15, 0.22):
        m.prism([(f, 0.034), (f + 0.05, 0.034), (f + 0.056, 0.05), (f + 0.006, 0.05)], 0.058, "polymer")
        m.prism([(f + 0.01, 0.0), (f + 0.055, 0.0), (f + 0.06, 0.016), (f + 0.015, 0.016)], 0.058, "polymer")
    m.box(0.29, 0.33, 0.034, 0.05, 0.058, "polymer", c=0.006)
    m.plate(0.105, 0.14, -0.015, 0.068, 0.028, "ivory")
    m.plate(0.105, 0.34, -0.022, -0.012, 0.028, "gunmetal", c=0.0)
    for f, u in ((0.11, 0.064), (0.11, -0.012), (0.335, 0.055), (0.335, 0.005)):
        m.screw(f, u, 0.028)

    # Magazine along the top: amber translucent body in gunmetal clips.
    m.prism([(-0.05, 0.07), (0.25, 0.07), (0.22, 0.106), (-0.02, 0.106)], 0.036, "lens", group="magazine")
    for i in range(10):
        f = -0.03 + i * 0.026
        m.side_box(f, f + 0.012, 0.074, 0.1, -0.0186, 0.0186, "glow_amber", group="magazine", detail=True)
    m.box(-0.06, -0.035, 0.066, 0.11, 0.04, "gunmetal", c=0.005, group="magazine")
    m.box(0.235, 0.26, 0.066, 0.1, 0.04, "gunmetal", c=0.005, group="magazine")
    m.screw(-0.0475, 0.088, 0.02, r=0.0024, group="magazine")
    # Iron sights on posts above the magazine: ghost ring rear, thin post front; line at 0.124.
    m.box(-0.082, -0.064, 0.07, 0.112, 0.014, "polymer", c=0.003)
    m.rear_aperture(-0.078, 0.124, 0.11)
    m.box(0.30, 0.324, 0.074, 0.104, 0.014, "polymer", c=0.003)
    m.front_post(0.304, 0.124, 0.104)

    # Lower: ivory trigger housing with lime chevron, grip, trigger.
    m.prism([(0.03, -0.03), (0.10, -0.03), (0.10, -0.045), (0.075, -0.09), (0.05, -0.09), (0.05, -0.05)], 0.044, "ivory")
    m.prism([(0.072, -0.034), (0.096, -0.034), (0.096, -0.044), (0.082, -0.044)], 0.046, "lime")
    m.prism([(-0.035, -0.03), (0.03, -0.03), (0.02, -0.062), (-0.012, -0.15), (-0.062, -0.15), (-0.05, -0.08)], 0.034, "polymer")
    m.prism([(-0.03, -0.045), (0.012, -0.045), (-0.012, -0.135), (-0.052, -0.135), (-0.044, -0.08)], 0.0355, "polymer", detail=True)
    m.box(0.0, 0.05, -0.07, -0.062, 0.012, "gunmetal", c=0.002)
    m.prism([(0.015, -0.03), (0.024, -0.03), (0.028, -0.058), (0.02, -0.06)], 0.008, "steel")

    # Foregrip and mount.
    m.box(0.22, 0.27, -0.035, -0.022, 0.03, "polymer", c=0.004)
    m.vcyl(0.245, -0.14, -0.035, 0.017, "polymer", sides=10)
    for u in (-0.115, -0.09, -0.065):
        m.vcyl(0.245, u, u + 0.008, 0.0185, "gunmetal", sides=10)

    # Barrel and ported brake with an amber ring.
    m.cyl(0.345, 0.37, 0.03, 0.011, "gunmetal")
    m.cyl(0.37, 0.378, 0.03, 0.016, "glow_amber", sides=14)
    m.cyl(0.378, 0.43, 0.03, 0.018, "polymer", sides=14)
    m.tube(0.43, 0.433, 0.03, 0.018, 0.009, "gunmetal", sides=14)
    m.vents(0.385, 0.425, 0.024, 0.036, 0.0178, 3, "gunmetal")

    m.marker("muzzle", f=0.433, u=0.03)
    m.marker("grip", f=0.0, u=0.0)
    return m.finish(BUDGET)
