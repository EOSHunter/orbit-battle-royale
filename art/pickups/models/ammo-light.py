"""Light ammo box. Concept: codex/concepts/v0.2/19-ammunition-boxes.png (top left).

Small hard-shell ammo box: light gray lower shell, dark graphite lid, chunky
dark end caps with amber lights, a lime color band wrapped over lid and body,
a front latch with an amber window, a carry handle, and labels as raised
plates. Origin at the bottom center on the ground.

ammo_box() is shared with the other ammo boxes (they load it from this file).
"""

import math

import kit
from kit import Model

BUDGET = (100, 800)

kit.MATERIALS.setdefault("case_gray", ("a9adb1", 0.15, 0.55, None, "paint"))   # light shell of the ammo boxes
kit.MATERIALS.setdefault("ammo_lime", ("b5e05a", 0.05, 0.5, None, "paint"))
kit.MATERIALS.setdefault("ammo_blue", ("4f9ad8", 0.05, 0.5, None, "paint"))
kit.MATERIALS.setdefault("ammo_red", ("dd4b3c", 0.05, 0.5, None, "paint"))
kit.MATERIALS.setdefault("ammo_yellow", ("e8b628", 0.05, 0.5, None, "paint"))
kit.MATERIALS.setdefault("brass", ("b08a4a", 0.9, 0.35, None, "metal"))


def plan(hx, hf, c, u):
    """Chamfered rectangle (x, f, u) ring, 8 points."""
    return [(hx, -hf + c, u), (hx, hf - c, u), (hx - c, hf, u), (-hx + c, hf, u), (-hx, hf - c, u), (-hx, -hf + c, u),
            (-hx + c, -hf, u), (hx - c, -hf, u)]


def block(m, hx, hf, u0, u1, c, mat, group="body", top_c=None):
    """Box chamfered on all edges: plan corners by c, top and bottom edges by top_c."""
    t = c if top_c is None else top_c
    m.loft([plan(hx - t, hf - t, c, u0), plan(hx, hf, c, u0 + t), plan(hx, hf, c, u1 - t), plan(hx - t, hf - t, c, u1)], mat, group=group)


def ammo_box(asset_id, L, W, H, band, handle=True, shells=False):
    """L along forward, W sideways, H tall. band: color material of the caliber."""
    m = Model(asset_id, category="pickups", bevel=0.0025, cage=0.004)
    hf, hx = L / 2, W / 2
    split = H * 0.6

    # Dark skid, light shell, dark lid.
    block(m, hx - 0.01, hf - 0.02, 0.0, 0.022, 0.01, "polymer")
    block(m, hx, hf - 0.012, 0.016, split, 0.012, "case_gray", top_c=0.004)
    block(m, hx + 0.004, hf - 0.008, split - 0.004, H, 0.014, "graphite", top_c=0.012)
    # Lid panels and seam, baked.
    for s in (1, -1):
        m.side_box(-hf + 0.04, hf - 0.04, split + 0.01, H - 0.016, s * (hx + 0.0035), s * (hx + 0.0048), "graphite", c=0.006, detail=True)
        m.side_box(-hf + 0.04, hf - 0.04, 0.03, split - 0.012, s * (hx - 0.0004), s * (hx + 0.0009), "case_gray", c=0.01, detail=True)
        m.side_box(-hf + 0.05, hf - 0.05, 0.036, split - 0.018, s * (hx + 0.0009), s * (hx + 0.0016), "polymer", c=0.008, detail=True)
        m.side_box(-hf + 0.052, hf - 0.052, 0.038, split - 0.02, s * (hx + 0.0012), s * (hx + 0.002), "case_gray", c=0.007, detail=True)
    for f in (-hf * 0.5, hf * 0.5):
        m.side_box(f - hf * 0.3, f + hf * 0.3, H - 0.0005, H + 0.0012, -hx * 0.55, hx * 0.55, "polymer", detail=True)
        m.side_box(f - hf * 0.3 + 0.003, f + hf * 0.3 - 0.003, H + 0.0008, H + 0.0016, -hx * 0.55 + 0.003, hx * 0.55 - 0.003, "graphite", detail=True)

    # End caps: chunky dark armor with amber lights on both faces.
    cap = min(0.06, L * 0.16)
    for s in (1, -1):
        fa, fb = sorted((s * (hf - cap), s * (hf + 0.004)))
        if shells and s < 0:
            # Open shell rack instead of a solid cap: side frames, top and bottom bars.
            fa = -hf - 0.03
            for x in (1, -1):
                m.side_box(fa, fb, 0.004, H - 0.006, *sorted((x * (hx - 0.004), x * (hx + 0.008))), "polymer", c=0.012)
            m.side_box(fa, fb, H * 0.84, H - 0.004, -hx, hx, "polymer", c=0.01)
        else:
            m.side_box(fa, fb, 0.004, H - 0.006, -hx - 0.008, hx + 0.008, "polymer", c=0.016)
        mid = (fa + fb) / 2
        for x in (1, -1):
            m.side_box(mid - cap * 0.18, mid + cap * 0.18, H * 0.62, H * 0.8, *sorted((x * (hx + 0.007), x * (hx + 0.0105))), "glow_amber", c=0.0)
            m.side_box(mid - cap * 0.3, mid + cap * 0.3, H * 0.58, H * 0.84, *sorted((x * (hx + 0.0068), x * (hx + 0.0092))), "gunmetal", c=0.0)
            m.xcyl(mid, H * 0.18, x * (hx + 0.0075), x * (hx + 0.0095), 0.0035, "steel", sides=6, detail=True)
        if not (shells and s < 0):
            m.side_box(*sorted((s * (hf + 0.003), s * (hf + 0.0055))), H * 0.3, H * 0.75, -hx * 0.5, hx * 0.5, "gunmetal", c=0.0)

    # Caliber color band over lid and body, front and back.
    bf = hf * 0.32
    m.side_box(bf - 0.022, bf + 0.022, 0.012, H + 0.002, -hx - 0.006, hx + 0.006, band, c=0.012)
    # Latch with amber window on both faces.
    for s in (1, -1):
        xa, xb = sorted((s * (hx + 0.004), s * (hx + 0.012)))
        m.side_box(-0.022, 0.022, split - 0.04, split + 0.03, xa, xb, "polymer", c=0.006)
        ga, gb = sorted((s * (hx + 0.0115), s * (hx + 0.0135)))
        m.side_box(-0.01, 0.01, split - 0.026, split + 0.02, ga, gb, "glow_amber", c=0.003)
        # Stencil labels: caliber color tag and white text bars.
        m.side_box(-hf * 0.62, -hf * 0.3, split * 0.35, split * 0.55, s * (hx + 0.0015), s * (hx + 0.0028), band, c=0.002, detail=True)
        for k in range(3):
            u = split * 0.3 - k * 0.012
            if u > 0.035:
                m.side_box(-hf * 0.62, -hf * 0.62 + 0.03 + 0.02 * (k % 2), u, u + 0.005, s * (hx + 0.0015), s * (hx + 0.0026), "white_paint", detail=True)

    if handle:
        hl = min(0.1, L * 0.28)
        for f in (-hl, hl):
            m.side_box(f - 0.014, f + 0.014, H - 0.004, H + 0.03, -0.012, 0.012, "polymer", c=0.006)
        m.side_box(-hl - 0.012, hl + 0.012, H + 0.022, H + 0.04, -0.013, 0.013, "polymer", c=0.008)
        for k in range(5):
            f = -hl * 0.6 + k * hl * 0.3
            m.side_box(f - 0.004, f + 0.004, H + 0.0395, H + 0.042, -0.011, 0.011, "rubber", detail=True)

    if shells:
        # Open rack at the back end showing shells.
        for x in (-hx * 0.6, 0.0, hx * 0.6):
            m.vcyl(-hf - 0.004, 0.024, H * 0.84, 0.022, "polymer", sides=8, x=x)
            m.vcyl(-hf - 0.004, H * 0.5, H * 0.62, 0.0228, band, sides=8, x=x)
            m.vcyl(-hf - 0.004, 0.026, 0.036, 0.0228, "brass", sides=8, x=x, detail=True)
    m.marker("grip", f=0.0, u=H * 0.5)
    return m


def build():
    m = ammo_box("ammo-light", L=0.34, W=0.17, H=0.16, band="ammo_lime")
    return m.finish(BUDGET, texture_size=512)
