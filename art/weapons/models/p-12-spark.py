"""P-12 Spark: sidearm. Concept: codex/concepts/v0.2/06-p-12-spark.png.

Origin at the top of the grip. Steel slide with a navy panel, amber light strip
and glowing muzzle ring, lime band, chunky polymer frame and textured grip.
The slide and the magazine are separate objects for animation later.
Plates, screws and vents marked detail-only are baked into the textures.
"""

from kit import Model

BUDGET = (500, 1500)


def build():
    m = Model("p-12-spark")

    # Slide: own object (cycles when firing).
    m.prism([(-0.065, 0.0), (0.125, 0.0), (0.135, 0.01), (0.135, 0.042), (0.125, 0.052), (-0.048, 0.052), (-0.065, 0.036)], 0.031, "steel", group="slide")
    m.prism([(0.035, 0.026), (0.11, 0.026), (0.118, 0.05), (0.035, 0.05)], 0.0315, "graphite", group="slide")
    m.prism([(0.005, 0.0), (0.03, 0.0), (0.045, 0.052), (0.02, 0.052)], 0.0318, "lime", group="slide")
    m.box(0.04, 0.12, 0.013, 0.027, 0.0318, "polymer", c=0.004, group="slide")
    m.box(0.045, 0.115, 0.016, 0.024, 0.0322, "glow_amber", c=0.003, group="slide")
    for i in range(4):
        f = -0.055 + i * 0.012
        m.prism([(f, 0.014), (f + 0.006, 0.014), (f + 0.012, 0.042), (f + 0.006, 0.042)], 0.0322, "polymer", group="slide")
    for i in range(3):
        f = 0.075 + i * 0.012
        m.prism([(f, 0.03), (f + 0.005, 0.03), (f + 0.009, 0.046), (f + 0.004, 0.046)], 0.0322, "polymer", group="slide")
    # Iron sights: notch rear, post front with an amber dot; sight line at 0.062.
    m.rear_notch(-0.06, 0.062, 0.052, gap=0.0055, ear=0.004, notch=0.005, length=0.012, group="slide")
    m.front_post(0.108, 0.062, 0.052, post=0.0028, bead="glow_amber", ears=False, group="slide")
    m.plate(-0.063, 0.0, 0.003, 0.012, 0.0155, "gunmetal", group="slide", c=0.0)
    m.plate(0.05, 0.13, 0.003, 0.011, 0.0155, "gunmetal", group="slide", c=0.0)
    m.screw(0.122, 0.038, 0.0157, r=0.0022, group="slide")

    # Barrel and its glowing muzzle.
    m.cyl(0.125, 0.145, 0.026, 0.013, "polymer", sides=16)
    m.tube(0.145, 0.15, 0.026, 0.013, 0.007, "glow_amber", sides=16)
    m.tube(0.15, 0.152, 0.026, 0.0072, 0.005, "gunmetal", sides=16)

    # Frame with an accessory rail and amber pip.
    m.prism([(-0.05, -0.026), (0.115, -0.026), (0.125, -0.015), (0.125, 0.0), (-0.05, 0.0)], 0.028, "polymer")
    m.box(0.05, 0.12, -0.037, -0.026, 0.022, "polymer", c=0.003)
    for i in range(3):
        f = 0.06 + i * 0.02
        m.box(f, f + 0.01, -0.041, -0.037, 0.022, "gunmetal", c=0.0)
    m.prism([(0.02, -0.02), (0.05, -0.02), (0.06, -0.012), (0.03, -0.012)], 0.0285, "steel")   # slide stop
    m.box(0.06, 0.085, -0.02, -0.014, 0.0285, "glow_amber", c=0.0)
    m.plate(0.085, 0.12, -0.024, -0.004, 0.014, "graphite")
    m.screw(-0.035, -0.012, 0.014, r=0.0024)
    m.screw(0.1, -0.014, 0.0145, r=0.0024)

    # Grip with a steel side frame, stippled panel and gunmetal base.
    m.prism([(-0.048, -0.026), (0.022, -0.026), (0.017, -0.05), (-0.004, -0.118), (-0.062, -0.122), (-0.06, -0.06)], 0.032, "polymer")
    m.prism([(-0.04, -0.035), (0.008, -0.035), (-0.012, -0.105), (-0.052, -0.105)], 0.0335, "gunmetal")
    m.prism([(-0.036, -0.04), (0.002, -0.04), (-0.015, -0.1), (-0.048, -0.1)], 0.0345, "polymer")
    m.prism([(-0.032, -0.045), (-0.002, -0.045), (-0.017, -0.095), (-0.044, -0.095)], 0.0352, "polymer", detail=True)

    # Magazine base: own object.
    m.prism([(-0.068, -0.118), (0.0, -0.114), (0.002, -0.134), (-0.07, -0.138)], 0.035, "gunmetal", group="magazine")
    m.box(-0.025, -0.008, -0.13, -0.124, 0.0355, "glow_amber", c=0.0, group="magazine")
    m.prism([(-0.004, -0.114), (0.004, -0.114), (0.0, -0.13), (-0.01, -0.13)], 0.036, "lime", group="magazine")

    # Trigger guard and trigger.
    m.prism([(0.012, -0.06), (0.075, -0.06), (0.085, -0.026), (0.075, -0.026), (0.068, -0.052), (0.014, -0.052)], 0.012, "steel")
    m.prism([(0.03, -0.026), (0.04, -0.026), (0.04, -0.038), (0.036, -0.05), (0.028, -0.05), (0.032, -0.038)], 0.008, "glow_amber")

    m.marker("muzzle", f=0.152, u=0.026)
    m.marker("grip", f=0.0, u=0.0)
    return m.finish(BUDGET)
