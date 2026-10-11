"""Colony supply crate: loot container. Concept: codex/concepts/v0.2/20-colony-supply-crate.png.

Wide armored crate, origin at the bottom center on the ground, front (latch)
facing forward. Navy body with dark corner posts, steel and lime straps over
the lid, amber corner lights and a glowing amber seam under the lid. The body
is a hollow tray with a glowing floor; the lid is its own object ("lid") hinged
at the back, marked by the "lid_hinge" empty. Glowing panels under the lid show
when it opens.
"""

import kit
from kit import Model

BUDGET = (100, 800)

kit.MATERIALS.setdefault("alloy", ("9ca1a8", 0.6, 0.4, None, "metal"))
kit.MATERIALS.setdefault("moss_lime", ("9db864", 0.05, 0.55, None, "paint"))   # pale olive-lime straps

HX, HF = 0.45, 0.3      # half length (sideways), half depth (forward)
SEAM = 0.318            # top of the body tray
LID0, LID1 = 0.334, 0.55


def plan(hx, hf, c, u):
    return [(hx, -hf + c, u), (hx, hf - c, u), (hx - c, hf, u), (-hx + c, hf, u), (-hx, hf - c, u), (-hx, -hf + c, u),
            (-hx + c, -hf, u), (hx - c, -hf, u)]


def build():
    m = Model("colony-supply-crate", category="pickups", bevel=0.004, cage=0.008)

    # Body: hollow tray (outer wall, rim, inner wall, floor) with a glowing floor.
    m.loft([plan(HX - 0.015, HF - 0.015, 0.03, 0.0), plan(HX, HF, 0.04, 0.02), plan(HX, HF, 0.04, SEAM),
            plan(HX - 0.045, HF - 0.045, 0.02, SEAM), plan(HX - 0.045, HF - 0.045, 0.02, 0.08)], "graphite")
    m.top_prism([(x, f) for x, f, _ in plan(HX - 0.07, HF - 0.07, 0.02, 0)], 0.075, 0.086, "glow_amber")
    # Glowing seam between body and lid.
    m.loft([plan(HX - 0.006, HF - 0.006, 0.036, SEAM - 0.002), plan(HX - 0.006, HF - 0.006, 0.036, LID0 + 0.002)], "glow_amber")

    # Lid: chamfered slab with a raised center panel, glow panels underneath.
    m.loft([plan(HX + 0.003, HF + 0.003, 0.042, LID0), plan(HX + 0.003, HF + 0.003, 0.042, LID1 - 0.03),
            plan(HX - 0.025, HF - 0.025, 0.03, LID1)], "polymer", group="lid")
    m.top_prism([(x, f) for x, f, _ in plan(0.24, 0.17, 0.03, 0)], LID1 - 0.004, LID1 + 0.01, "graphite", group="lid")
    for x in (-0.2, 0.2):
        m.side_box(-0.18, 0.18, LID0 - 0.006, LID0 + 0.002, x - 0.12, x + 0.12, "glow_amber", group="lid")
    # Straps over the lid: lime and steel pairs running front to back.
    for s in (1, -1):
        m.side_box(-HF - 0.008, HF + 0.008, LID0 + 0.03, LID1 + 0.008, *sorted((s * 0.25, s * 0.31)), "moss_lime", c=0.0, group="lid")
        m.side_box(-HF - 0.007, HF + 0.007, LID0 + 0.03, LID1 + 0.006, *sorted((s * 0.31, s * 0.335)), "alloy", c=0.0, group="lid")
    # Lid corner caps with amber lights on the front.
    for sx in (1, -1):
        for sf in (1, -1):
            xa, xb = sorted((sx * (HX - 0.07), sx * (HX + 0.012)))
            fa, fb = sorted((sf * (HF - 0.07), sf * (HF + 0.012)))
            m.side_box(fa, fb, LID0 + 0.004, LID1 - 0.008, xa, xb, "polymer", c=0.02, group="lid")
            if sf > 0:
                m.side_box(HF + 0.011, HF + 0.016, LID0 + 0.06, LID1 - 0.06, sx * (HX - 0.045) - 0.012, sx * (HX - 0.045) + 0.012, "glow_amber", group="lid")
    m.box(HF - 0.01, HF + 0.022, LID0 + 0.01, LID0 + 0.075, 0.12, "alloy", c=0.012, group="lid")       # latch catch
    # Lid panel lines, stencils and screws (baked).
    m.side_box(-0.16, 0.16, LID1 + 0.0095, LID1 + 0.0112, -0.2, 0.2, "polymer", detail=True)
    m.side_box(-0.155, 0.155, LID1 + 0.0105, LID1 + 0.0125, -0.195, 0.195, "graphite", detail=True)
    for k, x in enumerate((-0.12, -0.07, -0.02, 0.03, 0.08)):
        m.side_box(0.06, 0.1, LID1 + 0.012, LID1 + 0.014, x, x + 0.035 if k % 2 else x + 0.025, "polymer", detail=True)
    for x in (-0.28, 0.28):
        for f in (-0.27, 0.27):
            m.vcyl(f, LID1 - 0.005, LID1 + 0.003, 0.006, "steel", sides=6, x=x, group="lid", detail=True)

    # Corner posts on the body with amber lights near the base.
    for sx in (1, -1):
        for sf in (1, -1):
            xa, xb = sorted((sx * (HX - 0.075), sx * (HX + 0.014)))
            fa, fb = sorted((sf * (HF - 0.075), sf * (HF + 0.014)))
            m.side_box(fa, fb, 0.0, SEAM - 0.004, xa, xb, "polymer", c=0.022)
            if sf > 0:
                m.side_box(HF + 0.013, HF + 0.018, 0.04, 0.12, sx * (HX - 0.03) - 0.01, sx * (HX - 0.03) + 0.01, "glow_amber")
    # Front: steel panels, latch with glowing window.
    for s in (1, -1):
        m.side_box(HF - 0.004, HF + 0.006, 0.06, 0.26, *sorted((s * 0.11, s * 0.3)), "alloy", c=0.0)
        m.side_box(HF + 0.005, HF + 0.0068, 0.08, 0.24, *sorted((s * 0.13, s * 0.28)), "graphite", detail=True)
    m.box(HF - 0.01, HF + 0.026, 0.12, SEAM + 0.002, 0.12, "polymer", c=0.014)
    m.side_box(HF + 0.024, HF + 0.03, 0.16, 0.29, -0.022, 0.022, "glow_amber", c=0.0)
    m.side_box(HF + 0.025, HF + 0.0275, 0.15, 0.30, -0.035, 0.035, "alloy", detail=True)
    # Sides: lime panels and recessed handles; back: panel lines.
    for s in (1, -1):
        xa, xb = sorted((s * (HX - 0.004), s * (HX + 0.006)))
        m.side_box(0.12, 0.2, 0.05, 0.27, xa, xb, "moss_lime", c=0.0)
        ha, hb = sorted((s * (HX - 0.004), s * (HX + 0.03)))
        m.side_box(-0.12, 0.06, 0.17, 0.24, ha, hb, "polymer", c=0.016)
        m.side_box(-0.11, 0.05, 0.12, 0.27, s * (HX + 0.0005), s * (HX + 0.0025), "polymer", detail=True)
    m.side_box(-HF - 0.0025, -HF + 0.001, 0.05, 0.28, -0.3, 0.3, "polymer", detail=True)

    m.marker("lid_hinge", f=-HF, u=LID0)
    return m.finish(BUDGET, texture_size=1024)
