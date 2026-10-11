"""Trauma Kit: large medical case. Concept: codex/concepts/v0.2/10-trauma-kit.png.

Hard case standing on its long edge, faces pointing to the sides. Origin at the
center of the case; the "grip" marker sits on the carry handle. The front half
shell (+x) is its own object ("lid"), hinged along the bottom edge. Graphite
panels, coral corner bumpers and center strap, a coral octagon with a white
cross, an amber-lit latch, recessed end handles with amber lights.
"""

import kit
from kit import Model

BUDGET = (500, 1500)

kit.MATERIALS.setdefault("coral_red", ("d4503f", 0.05, 0.55, None, "paint"))   # case bumpers, deeper than item coral

F, U, X = 0.20, 0.135, 0.07     # half length, half height, half depth


def build():
    m = Model("trauma-kit", category="healing-items")

    for side, group in ((1, "lid"), (-1, "body")):
        xs = lambda a, b: (side * a, side * b) if side > 0 else (side * b, side * a)
        # Shell half and its raised face panels.
        m.side_box(-F, F, -U, U, *xs(0.004, X - 0.008), "graphite", c=0.03, group=group)
        m.side_box(-F + 0.02, F - 0.02, -U + 0.02, U - 0.02, *xs(0.01, X), "graphite", c=0.022, group=group)
        # Seam rim at the parting line.
        m.side_box(-F - 0.004, F + 0.004, -U - 0.004, U + 0.004, *xs(0.0, 0.006), "polymer", c=0.032, group=group)
        # Coral corner bumpers.
        for cf in (-1, 1):
            for cu in (-1, 1):
                fa, fb = sorted((cf * (F + 0.006), cf * (F - 0.06)))
                ua, ub = sorted((cu * (U + 0.006), cu * (U - 0.06)))
                m.side_box(fa, fb, ua, ub, *xs(0.008, X + 0.004), "coral_red", c=0.026, group=group)
                m.xcyl(cf * (F - 0.03), cu * (U - 0.014), side * (X + 0.0035), side * (X + 0.0052), 0.0028, "steel", sides=6, group=group, detail=True)
        # Vertical panel grooves and screws (baked).
        for f in (-0.07, 0.07):
            m.side_box(f - 0.003, f + 0.003, -U + 0.03, U - 0.03, *xs(X - 0.001, X + 0.0012), "polymer", group=group, detail=True)
        for f in (-0.085, -0.055, 0.055, 0.085):
            for u in (-0.1, 0.1):
                m.xcyl(f, u, side * (X - 0.0005), side * (X + 0.0012), 0.0025, "steel", sides=6, group=group, detail=True)
        # Feet on the bottom.
        for f in (-0.12, 0.12):
            m.side_box(f - 0.03, f + 0.03, -U - 0.012, -U + 0.01, *xs(0.012, X - 0.012), "polymer", c=0.006, group=group)

    # Lid face: coral strap, octagon with white cross, latch with amber light.
    m.side_box(-0.03, 0.03, -U - 0.002, U + 0.002, X - 0.004, X + 0.004, "coral_red", c=0.0, group="lid")
    oct_ = [(-0.07, -0.03), (-0.03, -0.07), (0.03, -0.07), (0.07, -0.03), (0.07, 0.03), (0.03, 0.07), (-0.03, 0.07), (-0.07, 0.03)]
    m.prism([(f, u + 0.01) for f, u in oct_], 0.008, "coral_red", x=X + 0.002, group="lid")
    a, b, cu = 0.042, 0.014, 0.01
    cross = [(-a, cu - b), (-b, cu - b), (-b, cu - a), (b, cu - a), (b, cu - b), (a, cu - b), (a, cu + b), (b, cu + b), (b, cu + a),
             (-b, cu + a), (-b, cu + b), (-a, cu + b)]
    m.prism(cross, 0.003, "white_paint", x=X + 0.0065, group="lid")
    m.side_box(-0.03, 0.03, -U - 0.006, -0.06, X - 0.01, X + 0.012, "polymer", c=0.008, group="lid")
    m.side_box(-0.022, 0.022, -U + 0.012, -0.072, X + 0.01, X + 0.015, "coral_red", c=0.004, group="lid")
    m.side_box(-0.018, 0.018, -0.084, -0.076, X + 0.012, X + 0.0165, "glow_amber", c=0.002, group="lid")
    for f in (-0.04, 0.04):
        m.side_box(f - 0.008, f + 0.008, -U + 0.004, -0.07, X - 0.006, X + 0.008, "gunmetal", c=0.004, group="lid")
    for f, u in ((-0.026, 0.12), (0.026, 0.12), (-0.026, -0.03), (0.026, -0.03)):
        m.xcyl(f, u, X + 0.0035, X + 0.0052, 0.0024, "steel", sides=6, group="lid", detail=True)

    # Back face: coral strap and a stencil frame.
    m.side_box(-0.03, 0.03, -U - 0.002, U + 0.002, -X - 0.004, -X + 0.004, "coral_red", c=0.0)
    m.side_box(-0.12, 0.12, -0.09, 0.09, -X - 0.0012, -X + 0.001, "polymer", c=0.02, detail=True)
    m.side_box(-0.115, 0.115, -0.085, 0.085, -X - 0.0013, -X + 0.001, "graphite", c=0.018, detail=True)

    # End caps: recessed side handles with amber lights.
    for s in (1, -1):
        fa, fb = sorted((s * F, s * (F + 0.022)))
        m.side_box(fa, fb, -0.06, 0.06, -0.035, 0.035, "polymer", c=0.006)
        ga, gb = sorted((s * (F + 0.018), s * (F + 0.03)))
        m.side_box(ga, gb, -0.05, 0.05, -0.012, 0.012, "gunmetal", c=0.004)
        la, lb = sorted((s * (F + 0.021), s * (F + 0.024)))
        m.side_box(la, lb, -0.03, 0.03, 0.026, 0.03, "glow_amber")
        m.side_box(la, lb, -0.03, 0.03, -0.03, -0.026, "glow_amber")

    # Carry handle on the back half: posts and a coral grip bar.
    for f in (-0.07, 0.07):
        m.box(f - 0.015, f + 0.015, U - 0.004, U + 0.03, 0.03, "polymer", x=-0.012, c=0.006)
    m.box(-0.09, 0.09, U + 0.022, U + 0.044, 0.026, "polymer", x=-0.012, c=0.008)
    m.box(-0.055, 0.055, U + 0.027, U + 0.049, 0.03, "coral_red", x=-0.012, c=0.008)
    for f in range(5):
        m.box(-0.045 + f * 0.022, -0.039 + f * 0.022, U + 0.046, U + 0.0502, 0.026, "polymer", x=-0.012, detail=True)

    # Inside the case (seen when the lid opens): compartment walls, baked onto the inner faces.
    for f in (-0.06, 0.06):
        m.side_box(f - 0.004, f + 0.004, -U + 0.02, U - 0.02, -0.0, 0.0018, "polymer", detail=True)
    m.side_box(-F + 0.02, F - 0.02, -0.004, 0.004, -0.0, 0.0018, "polymer", detail=True)

    m.marker("grip", f=0.0, u=U + 0.036, x=-0.012)
    return m.finish(BUDGET, texture_size=1024)
