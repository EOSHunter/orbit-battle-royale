"""Field Patch: small health pouch. Concepts: codex/concepts/v0.2/09-field-patch-refined.png
(and 09-field-patch.png).

A padded off-white pouch lying in the forward/up plane (its faces point to the
sides), held between thumb and fingers. Origin at the center (also the grip).
Navy woven straps along the left and right edges with tabs, navy corner
wraps with lime diagonal stripes, a coral cross on both faces. The pull tab on
the front strap is its own object ("tab") for the tear-open animation.
"""

import math

import kit
from kit import Model

BUDGET = (500, 1500)

kit.MATERIALS.setdefault("weave", ("344058", 0.0, 0.85, None, "polymer"))      # navy woven strap
kit.MATERIALS.setdefault("foil", ("cfcfca", 0.15, 0.62, None, "paint"))        # padded pouch film


def outline(hf, hu, r, inset=0.0, n=4):
    """Rounded rectangle (f, u) with corner radius r, 4 * n points."""
    hf, hu, r = hf - inset, hu - inset, max(0.001, r - inset * 0.5)
    pts = []
    for cf, cu, a0 in ((hf - r, hu - r, 0), (-hf + r, hu - r, 90), (-hf + r, -hu + r, 180), (hf - r, -hu + r, 270)):
        for i in range(n):
            a = math.radians(a0 + 90 * i / (n - 1))
            pts.append((cf + math.cos(a) * r, cu + math.sin(a) * r))
    return pts


def both(m, profile, x0, x1, mat, group="body", detail=False):
    """The same thin side profile on the right face and mirrored on the left face."""
    for s in (1, -1):
        m.prism(profile, x1 - x0, mat, x=s * (x0 + x1) / 2, group=group, detail=detail)


def build():
    m = Model("field-patch", category="healing-items")
    HF, HU = 0.052, 0.054

    # Padded pouch: pillow loft, flat faces at |x| = 0.0115, thin sealed flange.
    rings = []
    for x, inset in ((-0.0115, 0.009), (-0.009, 0.0035), (-0.0045, 0.0), (0.0045, 0.0), (0.009, 0.0035), (0.0115, 0.009)):
        rings.append([(x, f, u) for f, u in outline(HF, HU, 0.012, inset)])
    m.loft(rings, "foil")
    m.prism(outline(HF + 0.004, HU + 0.004, 0.008), 0.0024, "foil")

    # Coral cross on both faces.
    for x0, x1 in ((0.0113, 0.0122),):
        a, b = 0.026, 0.0085
        cross = [(-a, -b), (-b, -b), (-b, -a), (b, -a), (b, -b), (a, -b), (a, b), (b, b), (b, a), (-b, a), (-b, b), (-a, b)]
        both(m, cross, x0, x1, "coral")
    # Pressed border line and wrinkles, baked only.
    for s in (1, -1):
        for f0, f1, u0, u1 in ((-0.04, 0.04, 0.0395, 0.041), (-0.04, 0.04, -0.041, -0.0395), (-0.041, -0.0395, -0.04, 0.04), (0.0395, 0.041, -0.04, 0.04)):
            m.side_box(f0, f1, u0, u1, s * 0.0112, s * 0.0121, "foil", group="body", detail=True)
    for f, u, a in ((-0.03, 0.022, 20), (0.018, -0.03, -35), (0.03, 0.03, 60), (-0.022, -0.02, -10)):
        for s in (1, -1):
            o = m.side_box(-0.012, 0.012, -0.0006, 0.0006, s * 0.0112, s * 0.0119, "foil", detail=True)
            m.transform(o, rotate=(a, 0, 0), move=(0, f, u))

    # Navy corner wraps (top front, bottom back) with lime diagonal stripes.
    wrap_tf = [(0.008, HU + 0.004), (HF + 0.006, HU + 0.004), (HF + 0.006, 0.006)]
    wrap_bb = [(-HF - 0.006, -0.006), (-HF - 0.006, -HU - 0.004), (-0.008, -HU - 0.004)]
    m.prism(wrap_tf, 0.0256, "weave")
    m.prism(wrap_bb, 0.0256, "weave")
    stripe_tf = [(0.006, 0.043), (0.015, 0.043), (0.043, 0.015), (0.043, 0.006)]
    stripe_bb = [(-0.043, -0.006), (-0.043, -0.015), (-0.015, -0.043), (-0.006, -0.043)]
    for st in (stripe_tf, stripe_bb):
        both(m, [(f, u) for f, u in st], 0.0114, 0.0124, "lime")

    # Woven straps down the left and right edges, with stitched seams.
    for s in (1, -1):
        f0, f1 = (HF - 0.006, HF + 0.012) if s > 0 else (-HF - 0.012, -HF + 0.006)
        m.box(f0, f1, -HU - 0.008, HU + 0.008, 0.028, "weave", c=0.003)
        for u in (-0.05, -0.03, -0.01, 0.01, 0.03, 0.05):
            for x in (0.014, -0.014):
                m.side_box(f0 + 0.002, f1 - 0.002, u - 0.0015, u + 0.0015, x, x + (0.0012 if x > 0 else -0.0012), "weave", detail=True)
        m.plate(f0 + 0.003, f1 - 0.003, -HU - 0.004, -HU + 0.004, 0.014, "gunmetal")
        m.plate(f0 + 0.003, f1 - 0.003, HU - 0.004, HU + 0.004, 0.014, "gunmetal")

    # Side tabs: a fixed one at the back and the pull tab at the front.
    for s, group in ((-1, "body"), (1, "tab")):
        fa, fb = (HF + 0.011, HF + 0.03) if s > 0 else (-HF - 0.03, -HF - 0.011)
        u0, u1 = (0.004, 0.034) if s > 0 else (-0.008, 0.022)
        m.box(fa, fb, u0, u1, 0.012, "weave", c=0.005, group=group)
        mid = (u0 + u1) / 2
        tip = fb - 0.004 if s > 0 else fa + 0.004
        back = fa + 0.005 if s > 0 else fb - 0.005
        tri = [(back, mid - 0.007), (tip, mid), (back, mid + 0.007)] if s > 0 else [(tip, mid), (back, mid - 0.007), (back, mid + 0.007)]
        for x in (0.0065, -0.0065):
            m.prism(tri, 0.0012, "glow_lime", x=x, group=group)
        m.box(fa - 0.002 if s > 0 else fb - 0.006, fa + 0.006 if s > 0 else fb + 0.002, u0 - 0.002, u1 + 0.002, 0.016, "polymer", c=0.002, group=group)

    m.marker("grip", f=0.0, u=0.0)
    return m.finish(BUDGET, texture_size=1024)
