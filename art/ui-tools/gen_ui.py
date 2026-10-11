"""Generates the Orbit Royale brand-and-UI SVG set.

Geometry is authored here as explicit coordinates (no fonts, no rasters).
Weapon silhouettes are traced from the side profiles in art/weapons/models/*.py
through a stand-in for art/tools/kit.py that records (f, u) outlines.
"""
import html
import importlib.util
import math
import os
import re
import sys
import types
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True

# Repo root, two levels up from art/ui-tools/.
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "game", "assets", "ui", "brand-and-ui")

# Design tokens (design-system/project/tokens.json, Ringfall theme).
BG = "#0b101b"
SURFACE = "#141d2d"
RAISED = "#213047"
BORDER = "#46566d"
BORDER_CONTROL = "#7083a0"
TEXT = "#f3f5fa"
TEXT2 = "#b4bfd0"
ACCENT = "#c5f277"
HEALTH = "#ff8d7f"
SHIELD = "#70d6ff"

WRITTEN = []


# ----------------------------------------------------------------- helpers

def n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "", "-") else s


def pt(p):
    return f"{n(p[0])} {n(p[1])}"


def area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2


def P(pts, hole=False):
    """Polygon subpath. Solids wind clockwise on screen, holes counter-clockwise (nonzero rule)."""
    pts = list(pts)
    if (area(pts) < 0) != hole:
        pts = pts[::-1]
    return "M" + "L".join(pt(p) for p in pts) + "Z"


def R(x0, y0, x1, y1, r=0, hole=False):
    if r <= 0:
        return P([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], hole)
    a = f"A{n(r)} {n(r)} 0 0 {0 if hole else 1} "
    if not hole:
        return (f"M{n(x0 + r)} {n(y0)}H{n(x1 - r)}{a}{n(x1)} {n(y0 + r)}V{n(y1 - r)}{a}{n(x1 - r)} {n(y1)}"
                f"H{n(x0 + r)}{a}{n(x0)} {n(y1 - r)}V{n(y0 + r)}{a}{n(x0 + r)} {n(y0)}Z")
    return (f"M{n(x0 + r)} {n(y0)}{a}{n(x0)} {n(y0 + r)}V{n(y1 - r)}{a}{n(x0 + r)} {n(y1)}"
            f"H{n(x1 - r)}{a}{n(x1)} {n(y1 - r)}V{n(y0 + r)}{a}{n(x1 - r)} {n(y0)}Z")


def C(cx, cy, r, hole=False):
    s = 0 if hole else 1
    return f"M{n(cx - r)} {n(cy)}A{n(r)} {n(r)} 0 1 {s} {n(cx + r)} {n(cy)}A{n(r)} {n(r)} 0 1 {s} {n(cx - r)} {n(cy)}Z"


def chamfer(x0, y0, x1, y1, c, hole=False, bottom=True):
    pts = [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c)]
    if bottom:
        pts += [(x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c)]
    else:
        pts += [(x1, y1), (x0, y1)]
    pts += [(x0, y0 + c)]
    return P(pts, hole)


def cross(cx, cy, a, b, hole=False):
    pts = [(-a, -b), (-b, -b), (-b, -a), (b, -a), (b, -b), (a, -b), (a, b), (b, b), (b, a), (-b, a), (-b, b), (-a, b)]
    return P([(cx + x, cy + y) for x, y in pts], hole)


def ngon(cx, cy, r, k, start, hole=False):
    return P([(cx + r * math.cos(math.radians(start + 360 * i / k)), cy + r * math.sin(math.radians(start + 360 * i / k))) for i in range(k)], hole)


def polar(cx, cy, r, deg):
    return (cx + r * math.cos(math.radians(deg)), cy + r * math.sin(math.radians(deg)))


def ink(d, color=TEXT, cls="ink"):
    return f'<path class="{cls}" fill="{color}" d="{d}"/>'


def accent(d, color=ACCENT):
    return f'<path class="accent" fill="{color}" d="{d}"/>'


def svg(w, h, title, body, x=0, y=0):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{n(x)} {n(y)} {n(w)} {n(h)}" width="{n(w)}" height="{n(h)}">\n'
            f'<title>{html.escape(title)}</title>\n{body}\n</svg>\n')


def write(folder, name, content):
    d = os.path.join(OUT, folder)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name + ".svg")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    WRITTEN.append((folder, name, path))


# ------------------------------------------------------------ stroke font
# Cap height 10 units, y down. Squared-round geometric caps (radius 2-2.5).

O_PATH = "M2.5 0H4.5A2.5 2.5 0 0 1 7 2.5V7.5A2.5 2.5 0 0 1 4.5 10H2.5A2.5 2.5 0 0 1 0 7.5V2.5A2.5 2.5 0 0 1 2.5 0Z"
FONT = {
    "A": (7, "M0 10L3.5 0L7 10M1.3 6.6H5.7"),
    "B": (7, "M0 10V0H5A2 2 0 0 1 7 2V3A2 2 0 0 1 5 5H0M5 5A2 2 0 0 1 7 7V8A2 2 0 0 1 5 10H0"),
    "C": (7, "M7 0H2.5A2.5 2.5 0 0 0 0 2.5V7.5A2.5 2.5 0 0 0 2.5 10H7"),
    "D": (7, "M0 0H4.5A2.5 2.5 0 0 1 7 2.5V7.5A2.5 2.5 0 0 1 4.5 10H0Z"),
    "E": (6.5, "M6.5 0H0V10H6.5M0 5H5"),
    "F": (6.5, "M6.5 0H0V10M0 5H5"),
    "L": (6.5, "M0 0V10H6.5"),
    "O": (7, O_PATH),
    "Q": (7, O_PATH + "M4.4 7.4L7.4 10.4"),
    "R": (7, "M0 10V0H5A2 2 0 0 1 7 2V3A2 2 0 0 1 5 5H0M4 5L7 10"),
    "S": (7, "M7 1.8A2 2 0 0 0 5 0H2A2 2 0 0 0 0 2V3A2 2 0 0 0 2 5H5A2 2 0 0 1 7 7V8A2 2 0 0 1 5 10H2A2 2 0 0 1 0 8.2"),
    "T": (7, "M0 0H7M3.5 0V10"),
    "W": (9, "M0 0L2 10L4.5 2.5L7 10L9 0"),
    "X": (7, "M0 0L7 10M7 0L0 10"),
    "Y": (7, "M0 0L3.5 5L7 0M3.5 5V10"),
    "1": (3, "M0 2.2L3 0V10"),
    "2": (7, "M0 0H5A2 2 0 0 1 7 2V3A2 2 0 0 1 5 5H2A2 2 0 0 0 0 7V10H7"),
    "3": (7, "M0 0H5A2 2 0 0 1 7 2V3A2 2 0 0 1 5 5H2M5 5A2 2 0 0 1 7 7V8A2 2 0 0 1 5 10H0"),
    "4": (7, "M5.5 10V0L0 7H7"),
    "5": (7, "M7 0H0V5H5A2 2 0 0 1 7 7V8A2 2 0 0 1 5 10H0"),
}


def text_width(s, track):
    return sum(FONT[ch][0] for ch in s) + track * (len(s) - 1)


def text(s, cap, x, y, color, stroke_px, track=1.6, anchor="middle", cls="ink-s", cap_style="butt"):
    """Letters as stroked paths. x is the center (anchor middle) or left edge; y is the cap top."""
    k = cap / 10.0
    w = text_width(s, track) * k
    x0 = x - w / 2 if anchor == "middle" else x
    parts = []
    cx = 0.0
    for ch in s:
        cw, d = FONT[ch]
        parts.append(f'<path transform="translate({n(cx)} 0)" d="{d}"/>')
        cx += cw + track
    return (f'<g class="{cls}" transform="translate({n(x0)} {n(y)}) scale({n(k)})" fill="none" stroke="{color}" '
            f'stroke-width="{n(stroke_px / k)}" stroke-linecap="{cap_style}" stroke-linejoin="miter" stroke-miterlimit="3">'
            + "".join(parts) + "</g>")


# ------------------------------------------------------------------- logo

def ellipse_point(t, cx, cy, rx, ry, rot):
    x, y = rx * math.cos(t), ry * math.sin(t)
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return (cx + x * c - y * s, cy + x * s + y * c)


def runs(pred, N=1440):
    """Parameter intervals [t0, t1] (t1 may exceed 2pi) where pred(t) is true, boundaries bisected."""
    ts = [2 * math.pi * i / N for i in range(N)]
    vals = [pred(t) for t in ts]
    if all(vals):
        return [(0.0, 2 * math.pi)]
    if not any(vals):
        return []

    def edge(a, b):
        va = pred(a)
        for _ in range(40):
            m = (a + b) / 2
            if pred(m) == va:
                a = m
            else:
                b = m
        return (a + b) / 2

    start = vals.index(False)
    out = []
    i = 0
    cur = None
    while i < N:
        k = (start + i) % N
        k1 = (start + i + 1) % N
        ta = ts[k] + (2 * math.pi if start + i >= N else 0)
        tb = ta + 2 * math.pi / N
        if not vals[k] and vals[k1]:
            cur = edge(ta, tb)
        if vals[k] and not vals[k1] and cur is not None:
            out.append((cur, edge(ta, tb)))
            cur = None
        i += 1
    return out


def arc_path(intervals, cx, cy, rx, ry, rot):
    d = ""
    for t0, t1 in intervals:
        p0 = ellipse_point(t0, cx, cy, rx, ry, rot)
        p1 = ellipse_point(t1, cx, cy, rx, ry, rot)
        large = 1 if (t1 - t0) > math.pi else 0
        d += f"M{pt(p0)}A{n(rx)} {n(ry)} {n(rot)} {large} 1 {pt(p1)}"
    return d


def emblem(uid, cx, cy, Rr, w, rx, ry, rot, aw, gap, ring_color, arc_color, dot=None, simple=False):
    """Planetary O: a ring crossed by one tilted orbital arc.

    The arc never shows inside the counter. Where its front half crosses the ring
    the ring is cut back by `gap`; its back half stops `gap` short of the ring.
    simple=True keeps only the parts of the arc outside the ring (favicon)."""
    Ri = Rr - w
    rm = Rr - w / 2

    def info(t):
        p = ellipse_point(t, cx, cy, rx, ry, rot)
        return math.hypot(p[0] - cx, p[1] - cy), math.sin(t) > 0

    def vis(t):
        d, front = info(t)
        if simple:
            return d >= Rr + gap
        return d >= Ri if front else d >= Rr + gap

    def cut(t):
        d, front = info(t)
        return front and (Ri - 6 <= d <= Rr + gap + aw)

    arc_d = arc_path(runs(vis), cx, cy, rx, ry, rot)
    defs = ""
    ring_attr = ""
    if not simple:
        cut_d = arc_path(runs(cut), cx, cy, rx, ry, rot)
        pad = rx + aw + gap + 10
        defs = (f'<mask id="{uid}" maskUnits="userSpaceOnUse" x="{n(cx - pad)}" y="{n(cy - pad)}" width="{n(2 * pad)}" height="{n(2 * pad)}">'
                f'<rect x="{n(cx - pad)}" y="{n(cy - pad)}" width="{n(2 * pad)}" height="{n(2 * pad)}" fill="#fff"/>'
                f'<path d="{cut_d}" fill="none" stroke="#000" stroke-width="{n(aw + 2 * gap)}"/></mask>')
        ring_attr = f' mask="url(#{uid})"'
    body = (f'<circle class="ink-s" cx="{n(cx)}" cy="{n(cy)}" r="{n(rm)}" fill="none" stroke="{ring_color}" stroke-width="{n(w)}"{ring_attr}/>'
            f'<path class="accent-s" d="{arc_d}" fill="none" stroke="{arc_color}" stroke-width="{n(aw)}"/>')
    if dot:
        t, r = dot
        p = ellipse_point(t, cx, cy, rx, ry, rot)
        body += f'<circle class="accent" cx="{n(p[0])}" cy="{n(p[1])}" r="{n(r)}" fill="{arc_color}"/>'
    return defs, body


def rr_right(x0, y0, x1, y1, r, hole=False):
    """Rectangle with the two right corners rounded (letter bowls)."""
    if not hole:
        return f"M{n(x0)} {n(y0)}H{n(x1 - r)}A{n(r)} {n(r)} 0 0 1 {n(x1)} {n(y0 + r)}V{n(y1 - r)}A{n(r)} {n(r)} 0 0 1 {n(x1 - r)} {n(y1)}H{n(x0)}Z"
    return f"M{n(x0)} {n(y0)}V{n(y1)}H{n(x1 - r)}A{n(r)} {n(r)} 0 0 0 {n(x1)} {n(y1 - r)}V{n(y0 + r)}A{n(r)} {n(r)} 0 0 0 {n(x1 - r)} {n(y0)}Z"


def shift_path(d, dx):
    """Shift an absolute path made of M/L/H/V/A/Z commands horizontally."""
    out = []
    for cmd, args in re.findall(r"([MLHVAZ])([^MLHVAZ]*)", d):
        nums = [float(v) for v in re.findall(r"-?\d*\.?\d+", args)]
        if cmd in "ML":
            nums = [v + dx if i % 2 == 0 else v for i, v in enumerate(nums)]
        elif cmd == "H":
            nums = [v + dx for v in nums]
        elif cmd == "A":
            nums = [v + dx if i % 7 == 5 else v for i, v in enumerate(nums)]
        out.append(cmd + " ".join(n(v) for v in nums))
    return "".join(out)


# Wordmark geometry: cap height 100, baseline y = 100, stems 24, bars 20.
LETTER_R = (R(0, 0, 24, 100) + rr_right(0, 0, 78, 62, 28) + rr_right(24, 20, 54, 42, 9, hole=True)
            + P([(34, 56), (60, 56), (86, 100), (60, 100)]))
LETTER_B = (R(0, 0, 24, 100) + rr_right(0, 0, 72, 56, 26) + rr_right(0, 44, 80, 100, 28)
            + rr_right(24, 20, 48, 40, 8, hole=True) + rr_right(24, 60, 56, 80, 9, hole=True))
LETTER_I = R(0, 0, 24, 100)
LETTER_T = R(0, 0, 80, 20) + R(28, 0, 52, 100)

O_CX, O_CY, O_R, O_W = 58, 50, 58, 24
ARC = dict(rx=80, ry=24, rot=-20, aw=8, gap=5)
DOT_T = 0.85 * math.pi


def wordmark(color, cls="ink"):
    d = shift_path(LETTER_R, 144) + shift_path(LETTER_B, 246) + shift_path(LETTER_I, 342) + shift_path(LETTER_T, 382)
    return f'<path class="{cls}" fill="{color}" d="{d}"/>'


def logo_o(uid, ring, arc, dot=True):
    return emblem(uid, O_CX, O_CY, O_R, O_W, ARC["rx"], ARC["ry"], ARC["rot"], ARC["aw"], ARC["gap"], ring, arc,
                  dot=(DOT_T, 8) if dot else None)


def royale_stacked(color, cls="accent-s"):
    cap, sw = 26, 3.6
    k = cap / 10
    span = 462 - 144
    letters_w = sum(FONT[c][0] for c in "ROYALE") * k
    track = (span - letters_w) / 5 / k
    return text("ROYALE", cap, 144, 124, color, sw, track=track, anchor="start", cls=cls)


def build_logos():
    f = "orbit-logo-masters"
    # Stacked: ORBIT over a tracked ROYALE that spans R..T.
    defs, o = logo_o("orbit-ring-cut", TEXT, ACCENT)
    body = f"<defs>{defs}</defs>\n{o}\n{wordmark(TEXT)}\n{royale_stacked(ACCENT)}"
    write(f, "logo-stacked", svg(504, 176, "Orbit Royale logo, stacked", body, x=-34, y=-18))

    # Horizontal: ROYALE on the same baseline, after ORBIT.
    defs, o = logo_o("orbit-ring-cut", TEXT, ACCENT)
    cap = 40
    roy = text("ROYALE", cap, 500, 60, ACCENT, 5.2, track=2.4, anchor="start", cls="accent-s")
    width = 500 + text_width("ROYALE", 2.4) * cap / 10
    body = f"<defs>{defs}</defs>\n{o}\n{wordmark(TEXT)}\n{roy}"
    write(f, "logo-horizontal", svg(width + 34 + 16, 136, "Orbit Royale logo, horizontal", body, x=-34, y=-18))

    # Emblem alone.
    defs, o = logo_o("orbit-ring-cut", TEXT, ACCENT)
    body = f'<defs>{defs}</defs>\n<g transform="translate({n(-O_CX)} {n(-O_CY)})">{o}</g>'
    write(f, "emblem", svg(192, 192, "Orbit Royale emblem", body, x=-96, y=-96))

    # Monochrome stacked lockups.
    for name, col, title in (("logo-mono-dark", TEXT, "Orbit Royale logo, monochrome for dark backgrounds"),
                             ("logo-mono-light", BG, "Orbit Royale logo, monochrome for light backgrounds")):
        defs, o = logo_o("orbit-ring-cut", col, col)
        body = f"<defs>{defs}</defs>\n{o}\n{wordmark(col, cls='mono')}\n{royale_stacked(col, cls='mono-s')}"
        write(f, name, svg(504, 176, title, body, x=-34, y=-18))

    # Favicon: dark tile, heavy ring, arc wings outside the ring only.
    defs, o = emblem("fav", 32, 32, 19, 8, 29.5, 8.5, -20, 4.5, 3, TEXT, ACCENT, simple=True)
    body = f'<rect x="0" y="0" width="64" height="64" rx="14" fill="{BG}"/>\n{o}'
    write(f, "favicon", svg(64, 64, "Orbit Royale favicon", body))

    # Small emblem for 24-48 px: thicker strokes, no moon.
    defs, o = emblem("orbit-ring-cut-s", 24, 24, 14.5, 6.5, 22.5, 6.5, -20, 3.6, 2.4, TEXT, ACCENT)
    write(f, "emblem-small", svg(48, 48, "Orbit Royale emblem, small", f"<defs>{defs}</defs>\n{o}"))


# --------------------------------------------------------- weapon tracing

def chamfer_rect(f0, f1, u0, u1, c=0.0):
    c = min(c, 0.3 * abs(f1 - f0), 0.3 * abs(u1 - u0))
    if c <= 0:
        return [(f0, u0), (f1, u0), (f1, u1), (f0, u1)]
    return [(f0 + c, u0), (f1 - c, u0), (f1, u0 + c), (f1, u1 - c), (f1 - c, u1), (f0 + c, u1), (f0, u1 - c), (f0, u0 + c)]


class SideModel:
    """Records side profiles (f, u) of every non-detail part; mirrors kit.Model's signatures."""

    def __init__(self, asset_id, *a, **k):
        self.id = asset_id
        self.parts = []

    def prism(self, profile, width, mat, x=0.0, group="body", name="part", detail=False):
        if not detail:
            self.parts.append((list(profile), mat, group))

    def box(self, f0, f1, u0, u1, width, mat, x=0.0, c=0.003, group="body", name="box", detail=False):
        self.prism(chamfer_rect(f0, f1, u0, u1, c), width, mat, x, group, name, detail)

    def side_box(self, f0, f1, u0, u1, x0, x1, mat, c=0.0, group="body", name="box", detail=False):
        self.box(f0, f1, u0, u1, abs(x1 - x0), mat, 0, c, group, name, detail)

    def cyl(self, f0, f1, u, r, mat, sides=12, x=0.0, r1=None, group="body", name="cyl", detail=False):
        r1 = r if r1 is None else r1
        self.prism([(f0, u - r), (f1, u - r1), (f1, u + r1), (f0, u + r)], 0, mat, group=group, detail=detail)

    def vcyl(self, f, u0, u1, r, mat, sides=12, x=0.0, group="body", name="vcyl", detail=False):
        self.prism([(f - r, u0), (f + r, u0), (f + r, u1), (f - r, u1)], 0, mat, group=group, detail=detail)

    def xcyl(self, f, u, x0, x1, r, mat, sides=10, group="body", name="xcyl", detail=False):
        self.prism([(f + r * math.cos(2 * math.pi * i / 16), u + r * math.sin(2 * math.pi * i / 16)) for i in range(16)], 0, mat, group=group, detail=detail)

    def tube(self, f0, f1, u, r_out, r_in, mat, sides=12, x=0.0, group="body", name="tube", detail=False):
        self.prism([(f0, u - r_out), (f1, u - r_out), (f1, u + r_out), (f0, u + r_out)], 0, mat, group=group, detail=detail)

    def screw(self, *a, **k):
        pass

    def plate(self, *a, **k):
        pass

    def vents(self, *a, **k):
        pass

    def marker(self, *a, **k):
        pass

    def rear_aperture(self, f, line_u, base_u, r_in=0.0058, r_out=0.0082, mat="polymer", group="body"):
        self.tube(f, f + 0.006, line_u, r_out, r_in, mat, sides=10, group=group)
        self.box(f - 0.004, f + 0.01, base_u, line_u - r_out + 0.0015, 0.012, mat, c=0.002, group=group)

    def rear_notch(self, f, line_u, base_u, gap=0.0065, ear=0.0045, notch=0.006, mat="polymer", length=0.014, group="body"):
        self.box(f, f + length, base_u, line_u - notch, gap + 2 * ear, mat, c=0.002, group=group)
        for s in (-1, 1):
            self.side_box(f, f + length, line_u - notch - 0.001, line_u, s * gap / 2, s * (gap / 2 + ear), mat, c=0.0, group=group)

    def front_post(self, f, line_u, base_u, mat="polymer", post=0.0024, bead=None, ears=True, group="body"):
        self.box(f - 0.004, f + 0.016, base_u, base_u + 0.006, 0.013, mat, c=0.002, group=group)
        tip = line_u - (0.0025 if bead else 0.0)
        self.box(f + 0.004, f + 0.009, base_u, tip, post, mat, c=0.0, group=group)
        if bead:
            self.box(f + 0.004, f + 0.009, tip, line_u, post + 0.0004, bead, c=0.0, group=group)
        if ears:
            for s in (-1, 1):
                self.side_box(f, f + 0.012, base_u, line_u + 0.004, s * 0.0068, s * 0.0092, mat, c=0.0, group=group)

    def finish(self, *a, **k):
        return self


def trace_weapon(name):
    mod_kit = types.ModuleType("kit")
    mod_kit.Model = SideModel
    mod_kit.MATERIALS = {}
    sys.modules["kit"] = mod_kit
    path = os.path.join(ROOT, "art", "weapons", "models", name + ".py")
    spec = importlib.util.spec_from_file_location("weapon_" + name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build().parts


SEPARATE = ("magazine", "pump", "slide", "bolt")


def weapon_icon(name, title, max_h=80, max_w=116, gap=1.5):
    parts = trace_weapon(name)
    fs = [p[0] for poly, _, _ in parts for p in poly]
    us = [p[1] for poly, _, _ in parts for p in poly]
    f0, f1, u0, u1 = min(fs), max(fs), min(us), max(us)
    s = min(max_w / (f1 - f0), max_h / (u1 - u0))
    fc, uc = (f0 + f1) / 2, (u0 + u1) / 2

    def tx(poly):
        return [(64 + (f - fc) * s, 64 - (u - uc) * s) for f, u in poly]

    base, base_acc, groups, group_acc = [], [], {}, []
    for poly, mat, group in parts:
        d = P(tx(poly))
        lime = mat == "lime"
        if group in SEPARATE:
            (group_acc if lime else groups.setdefault(group, [])).append(d)
        else:
            (base_acc if lime else base).append(d)
    uid = "cut-" + name
    cut = "".join("".join(v) for v in groups.values())
    defs = (f'<defs><mask id="{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="128" height="128">'
            f'<rect width="128" height="128" fill="#fff"/>'
            f'<path d="{cut}" fill="#000" stroke="#000" stroke-width="{n(2 * gap)}" stroke-linejoin="round"/></mask></defs>')
    body = [defs, f'<g mask="url(#{uid})">', ink("".join(base))]
    if base_acc:
        body.append(accent("".join(base_acc)))
    body.append("</g>")
    for g, ds in groups.items():
        body.append(ink("".join(ds)))
    if group_acc:
        body.append(accent("".join(group_acc)))
    write("item-and-weapon-icons", name, svg(128, 128, title, "\n".join(body)))
    return s


# ------------------------------------------------------------ item icons

def item(name, title, ink_d, accents, under=False):
    """accents: list of (d, color). under=True puts the accent beneath the ink (parts that wrap it)."""
    acc = "\n".join(accent(d, c) for d, c in accents)
    body = f"{acc}\n{ink(ink_d)}" if under else f"{ink(ink_d)}\n{acc}"
    write("item-and-weapon-icons", name, svg(128, 128, title, body))


def build_items():
    # Field Patch: padded pouch, woven side straps, tabs, coral cross.
    d = R(32, 24, 96, 104, 12) + cross(64, 64, 24, 10.5, hole=True)
    d += P([(74, 24), (80, 24), (96, 40), (96, 46)], hole=True)          # corner wraps
    d += P([(32, 82), (32, 88), (48, 104), (54, 104)], hole=True)
    d += R(18, 18, 29, 110, 3) + R(99, 18, 110, 110, 3)                   # straps
    d += R(9, 66, 19, 84, 3)                                              # fixed tab
    d += R(109, 40, 121, 62, 3) + P([(112, 45.5), (117.5, 51), (112, 56.5)], hole=True)  # pull tab
    item("field-patch", "Field Patch", d, [(cross(64, 64, 21, 7.5), HEALTH)])

    # Trauma Kit: hard case with handle, corner bumpers, lid seam, coral octagon.
    d = R(12, 38, 116, 108, 10)
    d += R(44, 18, 84, 40, 7) + R(52, 25, 76, 38, 3, hole=True)           # handle
    d += R(12, 58, 40, 61, hole=True) + R(88, 58, 116, 61, hole=True)     # lid seam
    d += ngon(64, 76, 25, 8, 22.5, hole=True)
    for x in (26, 99.5):
        d += R(x, 38, x + 2.5, 58, hole=True) + R(x, 61, x + 2.5, 108, hole=True)
    acc = ngon(64, 76, 21.5, 8, 22.5) + cross(64, 76, 12.5, 4.5, hole=True)
    item("trauma-kit", "Trauma Kit", d, [(acc, HEALTH)])

    # Shield Cell: hex canister, chamfered caps, struts around a cyan crystal.
    d = R(52, 8, 76, 14, 2)
    d += chamfer(38, 16, 90, 42, 6) + R(62.5, 22, 65.5, 36, hole=True)
    d += R(42, 44, 86, 49) + R(42, 49, 50, 81) + R(78, 49, 86, 81) + R(42, 81, 86, 86)
    d += chamfer(38, 88, 90, 114, 6) + R(62.5, 94, 65.5, 108, hole=True)
    d += R(46, 114, 82, 119, 1.5)
    crystal = P([(64, 51.5), (75, 58), (75, 72), (64, 78.5), (53, 72), (53, 58)])
    item("shield-cell", "Shield Cell", d, [(crystal, SHIELD)])

    # Shield Pack: flat octagonal case, handle, framed window with three cells.
    outer = [(-0.09, -0.125), (0.09, -0.125), (0.15, -0.055), (0.15, 0.05), (0.095, 0.12), (-0.095, 0.12), (-0.15, 0.05), (-0.15, -0.055)]
    d = P([(64 + f * 330, 70 - u * 330) for f, u in outer])
    d += R(28, 46, 100, 96, 6, hole=True)
    d += R(44, 14, 84, 32, 6) + R(51, 20.5, 77, 30.4, hole=True)          # handle
    d += R(6, 62, 14.5, 80, 2) + R(8.5, 66, 11.5, 76, hole=True)          # clamps
    d += R(113.5, 62, 122, 80, 2) + R(116.5, 66, 119.5, 76, hole=True)
    cells = "".join(R(x, 51, x + 18, 91, 7) for x in (33, 55, 77))
    item("shield-pack", "Shield Pack", d, [(cells, SHIELD)])

    # Shield Core: reactor canister, top arch handle, bars and clamp rings over a cyan core.
    d = "M34 34V22A14 14 0 0 1 48 8H80A14 14 0 0 1 94 22V34H88V22A8 8 0 0 0 80 14H48A8 8 0 0 0 40 22V34Z"
    d += R(48, 18, 80, 28, 2)
    d += R(34, 30, 94, 36, 2)
    d += R(40, 38, 47, 84) + R(81, 38, 88, 84) + R(38, 48, 90, 54) + R(38, 68, 90, 74)
    for x in (26, 93):
        d += R(x, 42, x + 9, 80, 3)
        for y in (52, 61, 70):
            d += C(x + 4.5, y, 1.7, hole=True)
    d += R(36, 86, 92, 92, 2)
    d += P([(32, 94), (96, 94), (96, 100), (104, 100), (104, 114), (24, 114), (24, 100), (32, 100)])
    d += R(44, 104, 56, 107, hole=True) + R(72, 104, 84, 107, hole=True)
    item("shield-core", "Shield Core", d, [(R(49, 38, 79, 84, 4), SHIELD)], under=True)

    # Phoenix Capsule: armored capsule, twin windows (coral and cyan), stepped injector.
    d = R(50, 6, 78, 14, 3)
    d += chamfer(42, 16, 86, 34, 5) + R(60, 22, 68, 28, hole=True)
    d += R(47, 34, 81, 82) + R(51, 38, 62, 80, 3, hole=True) + R(66, 38, 77, 80, 3, hole=True)
    d += chamfer(42, 82, 86, 98, 5) + R(60, 87, 68, 93, hole=True)
    d += R(48, 100, 80, 106, 2) + R(54, 108, 74, 114, 2) + R(59, 116, 69, 121, 1.5) + R(62, 121, 66, 125)
    item("phoenix-capsule", "Phoenix Capsule", d,
         [(R(53.5, 40.5, 59.5, 77.5, 2), SHIELD), (R(68.5, 40.5, 74.5, 77.5, 2), HEALTH)])

    # Fragmentation grenade: round segmented body, fuse block, spoon, pull ring.
    cx, cy, r = 58, 76, 36

    def xr(y):
        return math.sqrt(r * r - (y - cy) ** 2)

    d = f"M{n(cx - xr(72))} 72A{r} {r} 0 0 1 {n(cx + xr(72))} 72Z"
    d += f"M{n(cx + xr(81))} 81A{r} {r} 0 0 1 {n(cx - xr(81))} 81Z"
    for x in (38, 56.5, 75):
        d += R(x, 52 if x != 56.5 else 45, x + 3, 69, hole=True)
        d += R(x, 84, x + 3, 100 if x != 56.5 else 107, hole=True)
    d += chamfer(46, 24, 70, 42, 3) + R(55, 29, 61, 33, hole=True)
    o0, o1 = polar(cx, cy, 44, -68), polar(cx, cy, 44, 15)
    i0, i1 = polar(cx, cy, 39.5, -68), polar(cx, cy, 39.5, 15)
    d += f"M70 26L78 26L{pt(o0)}A44 44 0 0 1 {pt(o1)}L{pt(i1)}A39.5 39.5 0 0 0 {pt(i0)}L70 35Z"
    d += C(35, 24, 9) + C(35, 24, 5.2, hole=True) + R(43.5, 27, 47, 30.5)
    belt = f"M{n(cx - xr(74))} 74L{n(cx + xr(74))} 74A{r} {r} 0 0 1 {n(cx + xr(79))} 79L{n(cx - xr(79))} 79A{r} {r} 0 0 1 {n(cx - xr(74))} 74Z"
    item("fragmentation-grenade", "Fragmentation grenade", d, [(belt, ACCENT)])

    # Arc grenade: armored head and base on struts around a coil column.
    d = C(36, 18, 8) + C(36, 18, 4.8, hole=True) + R(43, 16, 53, 20)
    d += R(52, 12, 76, 26, 2)
    d += P([(76, 13), (86, 13), (93, 21), (93, 74), (89, 74), (89, 23), (84, 19), (76, 19)])
    d += chamfer(42, 28, 86, 48, 5) + R(50, 36, 58, 40, hole=True) + R(70, 36, 78, 40, hole=True)
    d += R(44, 48, 50, 90) + R(78, 48, 84, 90)
    d += chamfer(40, 90, 88, 116, 6) + R(50, 100, 58, 104, hole=True) + R(70, 100, 78, 104, hole=True)
    coil = R(61, 50, 67, 88) + "".join(R(53, y, 75, y + 5, 2.5) for y in (52, 59, 66, 73, 80))
    item("arc-grenade", "Arc grenade", d, [(coil, ACCENT)])

    # Veil grenade: tall smoke canister, slotted crown, glowing vent slots.
    d = C(36, 18, 8) + C(36, 18, 4.8, hole=True) + R(43, 16, 51, 20)
    d += R(50, 10, 78, 18, 2)
    d += R(48, 20, 80, 30) + "".join(R(x, 22.5, x + 3, 27.5, hole=True) for x in (53, 59.5, 66, 72.5))
    d += P([(78, 11), (86, 11), (92, 18), (92, 72), (88, 72), (88, 20), (84, 16), (78, 16)])
    d += R(44, 32, 84, 104, 4) + R(44, 38, 84, 40.5, hole=True) + R(44, 95.5, 84, 98, hole=True)
    slots_x = (50.5, 61.5, 72.5)
    d += "".join(R(x, 45, x + 5, 91, 2.5, hole=True) for x in slots_x)
    d += R(42, 106, 86, 118, 3) + R(52, 110, 60, 113, hole=True) + R(68, 110, 76, 113, hole=True)
    glow = "".join(R(x + 1.5, 47.5, x + 3.5, 88.5, 1) for x in slots_x)
    item("veil-grenade", "Veil grenade", d, [(glow, ACCENT)])

    # Tethercaster: wrist launcher with a coil window, tether line, three-prong claw.
    d = chamfer(8, 40, 68, 92, 8) + R(20, 52, 52, 80, 4, hole=True) + R(24, 44.5, 46, 47.5, hole=True)
    d += R(68, 56, 80, 76, 2) + R(80, 60, 86, 72)
    d += R(98, 58, 106, 74, 2)
    up = [(101, 58), (108, 46), (118, 38), (124.5, 38), (122, 42.5), (114, 48), (107.5, 58)]
    d += P(up) + P([(x, 132 - y) for x, y in up])
    d += P([(106, 63.5), (119, 64), (123.5, 66), (119, 68), (106, 68.5)])
    coil = "".join(R(x, 55, x + 4, 77, 2) for x in (23.5, 30.5, 37.5, 44.5)) + R(86, 65, 98, 67)
    item("tethercaster", "Tethercaster", d, [(coil, ACCENT)])

    # Ammo boxes: proportions follow the pickup models; glyph shows the round.
    def ammo(name, title, w, h, handle, glyph):
        top_extra = 12 if handle else 0
        yb = 64 + (h + top_extra) / 2
        yt = yb - h
        x0, x1 = 64 - w / 2, 64 + w / 2
        hs = (h - 8) * 0.55
        ys = yb - 8 - hs
        cap = min(16, w * 0.17)
        bx = x0 + w * 0.62
        d = R(x0 + 6, yb - 6, x1 - 6, yb, 1.5)                                       # skid
        d += R(x0 + 2, ys, x1 - 2, yb - 8, 2)                                         # shell
        d += chamfer(x0, yt, x1, ys - 2, 6, bottom=False)                             # lid
        for y_a, y_b in ((yt, ys - 2), (ys, yb - 8)):
            d += R(x0 + cap, y_a, x0 + cap + 2.5, y_b, hole=True)
            d += R(x1 - cap - 2.5, y_a, x1 - cap, y_b, hole=True)
            d += R(bx - 2, y_a, bx + 10, y_b, hole=True)
        if handle:
            hx = x0 + w * 0.32
            d += R(hx - 16, yt - 12, hx + 16, yt, 4) + R(hx - 10, yt - 7, hx + 10, yt, hole=True)
        cy = (ys + yb - 8) / 2
        gx = x0 + cap + 7
        if glyph == "shell":
            for k, yy in enumerate((cy - 6, cy + 6)):
                L, hh = 22, 3.6
                d += P([(gx, yy - hh - 1.5), (gx + 4, yy - hh - 1.5), (gx + 4, yy - hh), (gx + L, yy - hh), (gx + L, yy + hh),
                        (gx + 4, yy + hh), (gx + 4, yy + hh + 1.5), (gx, yy + hh + 1.5)], hole=True)
        else:
            L, hh = glyph
            d += P([(gx, cy - hh), (gx + L * 0.58, cy - hh), (gx + L * 0.84, cy - hh * 0.62), (gx + L, cy),
                    (gx + L * 0.84, cy + hh * 0.62), (gx + L * 0.58, cy + hh), (gx, cy + hh)], hole=True)
        band = R(bx, yt, bx + 8, yb - 8)
        item(name, title, d, [(band, ACCENT)])

    ammo("ammo-light", "Light ammo", 80, 50, True, (20, 3.2))
    ammo("ammo-medium", "Medium ammo", 100, 54, False, (27, 4.2))
    ammo("ammo-heavy", "Heavy ammo", 116, 60, False, (34, 6))
    ammo("ammo-shells", "Shotgun shells", 86, 58, True, "shell")


# -------------------------------------------------------------- HUD icons

def hud(name, title, d, extra=""):
    write("hud-icon-set", name, svg(48, 48, title, ink(d) + extra))


def pin(hole_d):
    cx, cy, r, tip = 24, 18, 13.5, (24, 45)
    dist = tip[1] - cy
    a = math.degrees(math.asin(r / dist))
    left = polar(cx, cy, r, 180 - (90 - a))
    right = polar(cx, cy, r, 90 - a)
    return f"M{pt(tip)}L{pt(left)}A{r} {r} 0 1 1 {pt(right)}Z" + hole_d


def build_hud():
    hud("health", "Health", cross(24, 24, 19, 7))
    hud("shield", "Shield", "M24 4L41 11V25C41 34 33 40 24 45C15 40 7 34 7 25V11Z")
    d = C(24, 15, 6.5) + "M14 40V33A10 10 0 0 1 34 33V40Z"
    for s in (1, -1):
        x = 24 + s * 17
        d += C(x, 20.5, 4.2)
        xa, xb = (x - 4.5, x + 4.5)
        d += f"M{n(xa)} 38V31.5A4.5 4.5 0 0 1 {n(xb)} 31.5V38Z"
    hud("survivors", "Survivors", d)
    d = P([(14, 5), (34, 5), (42, 13), (42, 30), (36, 35), (36, 43), (12, 43), (12, 35), (6, 30), (6, 13)])
    d += P([(11.5, 20.5), (21, 24), (21, 29), (14.5, 29), (11.5, 26)], hole=True)
    d += P([(36.5, 20.5), (27, 24), (27, 29), (33.5, 29), (36.5, 26)], hole=True)
    d += P([(24, 29.5), (27, 34), (21, 34)], hole=True)
    d += R(19.5, 37.5, 22, 43, hole=True) + R(26, 37.5, 28.5, 43, hole=True)
    hud("eliminations", "Eliminations", d)
    hud("storm", "Storm", P([(19, 4), (33, 4), (27, 18), (38, 18), (17, 44), (22, 26.5), (11, 26.5)]))
    hud("marker-ping", "Ping marker", pin(C(24, 18, 5.5, hole=True)))
    hud("marker-loot", "Loot marker", pin(R(16.5, 11.5, 31.5, 24.5, 1.5, hole=True) + R(16.5, 15.5, 31.5, 17.3) + R(22.5, 14, 25.5, 19.5)))
    car = [(14, 20), (14, 15), (17.5, 15), (20, 10), (28, 10), (30.5, 15), (34, 15), (34, 20)]
    hud("marker-vehicle", "Vehicle marker", pin(P(car, hole=True) + C(19, 23.2, 2.4, hole=True) + C(29, 23.2, 2.4, hole=True)))
    hud("marker-danger", "Danger marker", pin(R(22, 8.5, 26, 20.5, 1, hole=True) + C(24, 25, 2.3, hole=True)))
    check = [(12.2, 25.8), (15.8, 22.2), (21, 27.4), (32.2, 16.2), (35.8, 19.8), (21, 34.6)]
    hud("status-success", "Success", C(24, 24, 20) + P(check, hole=True))
    hud("status-warning", "Warning", "M21.4 6.5Q24 2 26.6 6.5L44.2 37.5Q46.8 42 41.6 42H6.4Q1.2 42 3.8 37.5Z"
        + R(22, 15, 26, 29, 1, hole=True) + C(24, 35, 2.4, hole=True))
    xs = []
    for x, y in [(-11, -2.6), (-2.6, -2.6), (-2.6, -11), (2.6, -11), (2.6, -2.6), (11, -2.6), (11, 2.6), (2.6, 2.6), (2.6, 11), (-2.6, 11), (-2.6, 2.6), (-11, 2.6)]:
        c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
        xs.append((24 + x * c - y * s, 24 + x * s + y * c))
    hud("status-error", "Error", C(24, 24, 20) + P(xs, hole=True))
    # Inventory: pack with handle, flap seam, front pocket, side pockets.
    d = R(10, 12, 38, 44, 6) + R(18, 5, 30, 13, 3) + R(21, 8, 27, 12, hole=True)
    d += R(13, 21, 35, 23, hole=True) + R(15, 28, 33, 40, 3, hole=True) + R(17.5, 30.5, 30.5, 37.5, 1.5)
    d += R(5, 24, 9, 40, 2) + R(39, 24, 43, 40, 2)
    hud("inventory", "Inventory", d)
    d = P([(5, 10), (16.25, 7.2), (16.25, 38.2), (5, 41)])
    d += P([(17.75, 7.2), (30.25, 10), (30.25, 41), (17.75, 38.2)]) + C(24, 21, 3.2, hole=True)
    d += P([(31.75, 10), (43, 7.2), (43, 38.2), (31.75, 41)])
    hud("map", "Map", d)
    g = []
    for k in range(8):
        c = 45 * k
        g += [polar(24, 24, 15.5, c - 15), polar(24, 24, 21, c - 8), polar(24, 24, 21, c + 8), polar(24, 24, 15.5, c + 15)]
    hud("settings", "Settings", P(g) + C(24, 24, 6.5, hole=True))
    d = ""
    for a0, a1 in ((190, 318), (10, 138)):
        ro, ri = 17, 11.5
        d += f"M{pt(polar(24, 24, ro, a0))}A{ro} {ro} 0 0 1 {pt(polar(24, 24, ro, a1))}L{pt(polar(24, 24, ri, a1))}A{ri} {ri} 0 0 0 {pt(polar(24, 24, ri, a0))}Z"
        d += P([polar(24, 24, ri - 4.5, a1 - 0.5), polar(24, 24, ro + 4.5, a1 - 0.5), polar(24, 24, (ro + ri) / 2, a1 + 26)])
    hud("reload", "Reload", d)
    d = ""
    for x in (8, 20, 32):
        d += f"M{x} 19C{x} 13 {x + 1.5} 9 {x + 4} 5C{x + 6.5} 9 {x + 8} 13 {x + 8} 19Z"
        d += R(x, 21, x + 8, 39) + R(x - 0.5, 40.5, x + 8.5, 43)
    hud("ammo", "Ammo", d)


# ----------------------------------------------------------------- glyphs

GF = "controller-and-key-glyphs"
LEG = 3.4   # legend stroke px


def keycap(inner):
    return (f'<rect x="4" y="4" width="56" height="56" rx="6" fill="{SURFACE}" stroke="{BORDER_CONTROL}" stroke-width="2"/>'
            f'<path d="M10 54H54" stroke="{BORDER}" stroke-width="2" stroke-linecap="round" fill="none"/>' + inner)


def glyph(name, title, body):
    write(GF, name, svg(64, 64, title, body))


def legend(s, cap=None, y_mid=30, sw=None):
    if cap is None:
        cap = 22 if len(s) == 1 else (19 if len(s) == 2 else 14)
    if sw is None:
        sw = LEG if len(s) < 3 else 2.8
    return text(s, cap, 32, y_mid - cap / 2, TEXT, sw, track=2.2 if len(s) > 1 else 0)


def stroke_icon(d, sw=3.2, color=TEXT, join="round", cap="round"):
    return f'<path class="ink-s" d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="{join}" stroke-linecap="{cap}"/>'


def mouse(highlight):
    body = ""
    hl = {
        "left": "M32 8V26H18V22A14 14 0 0 1 32 8Z",
        "right": "M32 8A14 14 0 0 1 46 22V26H32Z",
        "wheel": R(28.5, 12, 35.5, 24, 3.5),
        "side": R(13, 30, 18, 37, 1.5) + R(13, 39, 18, 46, 1.5),
    }
    body += f'<path class="accent" fill="{ACCENT}" d="{hl[highlight]}"/>'
    outline = "M18 22A14 14 0 0 1 46 22V42A14 14 0 0 1 18 42Z M32 8V12M32 24V26M18 26H46"
    body += stroke_icon(outline, 3)
    body += f'<rect x="28.5" y="12" width="7" height="12" rx="3.5" fill="none" stroke="{TEXT}" stroke-width="2.4" class="ink-s"/>'
    if highlight == "side":
        body += stroke_icon("M13 30H18V46H13Z", 2)
    if highlight == "wheel":
        body += stroke_icon("M50 14L53 10L56 14M50 22L53 26L56 22", 2.4)
    return body


def pad_round(inner, r=24):
    return f'<circle cx="32" cy="32" r="{r}" fill="{SURFACE}" stroke="{BORDER_CONTROL}" stroke-width="2.5"/>' + inner


def bumper(label, left):
    big, small = 14, 5
    if left:
        d = f"M6 46V{20 + big}A{big} {big} 0 0 1 {6 + big} 20H{58 - small}A{small} {small} 0 0 1 58 {20 + small}V46Z"
    else:
        d = f"M6 46V{20 + small}A{small} {small} 0 0 1 {6 + small} 20H{58 - big}A{big} {big} 0 0 1 58 {20 + big}V46Z"
    return (f'<path d="{d}" fill="{SURFACE}" stroke="{BORDER_CONTROL}" stroke-width="2.5" stroke-linejoin="round"/>'
            + legend(label, cap=14, y_mid=34, sw=2.8))


def trigger(label, left):
    big, small = 16, 6
    if left:
        d = f"M14 58V{6 + big}A{big} {big} 0 0 1 {14 + big} 6H{50 - small}A{small} {small} 0 0 1 50 {6 + small}V54A4 4 0 0 1 46 58Z"
    else:
        d = f"M14 58V{6 + small}A{small} {small} 0 0 1 {14 + small} 6H{50 - big}A{big} {big} 0 0 1 50 {6 + big}V54A4 4 0 0 1 46 58Z"
    return (f'<path d="{d}" fill="{SURFACE}" stroke="{BORDER_CONTROL}" stroke-width="2.5" stroke-linejoin="round"/>'
            + legend(label, cap=14, y_mid=36, sw=2.8))


def stick(label):
    return (pad_round(f'<circle cx="32" cy="32" r="17" fill="none" stroke="{BORDER}" stroke-width="2"/>', r=25)
            + legend(label, cap=13, y_mid=32, sw=2.6))


def dpad_cross():
    plus = "M24 6H40V24H58V40H40V58H24V40H6V24H24Z"
    arrows = "M32 11L36.5 17H27.5Z M32 53L36.5 47H27.5Z M11 32L17 27.5V36.5Z M53 32L47 27.5V36.5Z"
    return (f'<path d="{plus}" fill="{SURFACE}" stroke="{BORDER_CONTROL}" stroke-width="2.5" stroke-linejoin="round"/>'
            + f'<circle cx="32" cy="32" r="4" fill="{BORDER}"/>'
            + f'<path class="ink" d="{arrows}" fill="{TEXT}"/>')


def dpad_split():
    base = [(25, 6), (39, 6), (39, 22), (32, 28.5), (25, 22)]
    out = ""
    for rot in (0, 90, 180, 270):
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts = [(32 + (x - 32) * c - (y - 32) * s, 32 + (x - 32) * s + (y - 32) * c) for x, y in base]
        out += f'<path d="{P(pts)}" fill="{SURFACE}" stroke="{BORDER_CONTROL}" stroke-width="2.5" stroke-linejoin="round"/>'
        tri = [(32, 10.5), (35.5, 15.5), (28.5, 15.5)]
        tri = [(32 + (x - 32) * c - (y - 32) * s, 32 + (x - 32) * s + (y - 32) * c) for x, y in tri]
        out += f'<path class="ink" d="{P(tri)}" fill="{TEXT}"/>'
    return out


def capsule(inner):
    return f'<rect x="20" y="10" width="24" height="44" rx="12" fill="{SURFACE}" stroke="{BORDER_CONTROL}" stroke-width="2.5"/>' + inner


def build_glyphs():
    for ch in "WASDQEFRC12345":
        glyph(f"key-{ch.lower()}", f"Key {ch}", keycap(legend(ch)))
    for lab in ("F1", "F5"):
        glyph(f"key-{lab.lower()}", f"Key {lab}", keycap(legend(lab)))
    glyph("key-esc", "Key Esc", keycap(legend("ESC")))
    glyph("key-space", "Key Space", keycap(stroke_icon("M15 27V37H49V27", LEG, join="miter", cap="square")))
    glyph("key-shift", "Key Shift", keycap(stroke_icon("M32 13L47 29H39V45H25V29H17Z", 3, join="round")))
    glyph("key-tab", "Key Tab", keycap(stroke_icon("M13 30H41M33 22L41 30L33 38M48 20V40", LEG, join="miter", cap="square")))
    for side in ("left", "right", "wheel", "side"):
        glyph(f"mouse-{side}", f"Mouse {side}", mouse(side))

    # Xbox-style layout (generic shapes, no logos).
    for ch in "ABXY":
        glyph(f"xbox-{ch.lower()}", f"Xbox {ch} button", pad_round(legend(ch, cap=22, y_mid=32)))
    glyph("xbox-lb", "Xbox left bumper", bumper("LB", True))
    glyph("xbox-rb", "Xbox right bumper", bumper("RB", False))
    glyph("xbox-lt", "Xbox left trigger", trigger("LT", True))
    glyph("xbox-rt", "Xbox right trigger", trigger("RT", False))
    glyph("xbox-ls", "Xbox left stick", stick("LS"))
    glyph("xbox-rs", "Xbox right stick", stick("RS"))
    glyph("xbox-start", "Xbox menu button", pad_round(stroke_icon("M23 25H41M23 32H41M23 39H41", 3, cap="round"), r=20))
    view = (f'<rect class="ink-s" x="21" y="22" width="14" height="12" rx="1.5" fill="none" stroke="{TEXT}" stroke-width="2.8"/>'
            f'<rect class="ink-s" x="28" y="29" width="14" height="12" rx="1.5" fill="{SURFACE}" stroke="{TEXT}" stroke-width="2.8"/>')
    glyph("xbox-view", "Xbox view button", pad_round(view, r=20))
    glyph("xbox-dpad", "Xbox directional pad", dpad_cross())

    # PlayStation-style layout (generic shapes, no logos).
    shapes = {
        "cross": stroke_icon("M23 23L41 41M41 23L23 41", 3.6, cap="round"),
        "circle": f'<circle class="ink-s" cx="32" cy="32" r="10" fill="none" stroke="{TEXT}" stroke-width="3.6"/>',
        "square": f'<rect class="ink-s" x="22.5" y="22.5" width="19" height="19" rx="1" fill="none" stroke="{TEXT}" stroke-width="3.6"/>',
        "triangle": stroke_icon("M32 20.5L43 39.5H21Z", 3.6, join="round"),
    }
    for k, v in shapes.items():
        glyph(f"ps-{k}", f"PlayStation {k} button", pad_round(v))
    glyph("ps-l1", "PlayStation L1", bumper("L1", True))
    glyph("ps-r1", "PlayStation R1", bumper("R1", False))
    glyph("ps-l2", "PlayStation L2", trigger("L2", True))
    glyph("ps-r2", "PlayStation R2", trigger("R2", False))
    glyph("ps-l3", "PlayStation L3 (press left stick)", stick("L3"))
    glyph("ps-r3", "PlayStation R3 (press right stick)", stick("R3"))
    glyph("ps-options", "PlayStation options button", capsule(stroke_icon("M27 25H37M27 32H37M27 39H37", 3)))
    glyph("ps-share", "PlayStation share button", capsule(stroke_icon("M32 33V19M27 24L32 19L37 24M26.5 32V40H37.5V32", 2.8, join="round")))
    glyph("ps-dpad", "PlayStation directional buttons", dpad_split())


# ------------------------------------------------------------------ index

SECTIONS = [
    ("orbit-logo-masters", "ORBIT logo masters", 300),
    ("item-and-weapon-icons", "Item and weapon icons (128 × 128)", 112),
    ("hud-icon-set", "HUD icon set (48 × 48)", 48),
    ("controller-and-key-glyphs", "Controller and key glyphs (64 × 64)", 64),
]


def inline(path, suffix, size):
    with open(path, encoding="utf-8") as fh:
        s = fh.read()
    s = re.sub(r"<title>.*?</title>\n?", "", s)
    ids = re.findall(r'id="([^"]+)"', s)
    for i in ids:
        s = s.replace(f'id="{i}"', f'id="{i}-{suffix}"').replace(f"url(#{i})", f"url(#{i}-{suffix})")
    vb = re.search(r'viewBox="([^"]+)"', s).group(1).split()
    w, h = float(vb[2]), float(vb[3])
    if w >= h:
        dw, dh = size, size * h / w
    else:
        dw, dh = size * w / h, size
    s = re.sub(r'width="[^"]+" height="[^"]+"', f'width="{n(dw)}" height="{n(dh)}"', s, count=1)
    return s.strip()


def build_index():
    css = f"""
:root {{ --bg: {BG}; --surface: {SURFACE}; --raised: {RAISED}; --border: {BORDER}; --text: {TEXT}; --text-2: {TEXT2}; --accent: {ACCENT}; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--text); font: 16px/1.5 "IBM Plex Sans", "Segoe UI", system-ui, sans-serif; }}
main {{ max-width: 1400px; margin: 0 auto; padding: 32px 16px 64px; }}
h1 {{ font: 700 28px/36px "Archivo", "Arial Narrow", system-ui, sans-serif; margin: 0 0 8px; }}
h2 {{ font: 700 20px/28px "Archivo", "Arial Narrow", system-ui, sans-serif; margin: 48px 0 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
p {{ color: var(--text-2); margin: 0; }}
.grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(var(--tile), 1fr)); }}
.tile {{ background: var(--surface); border-radius: 8px; overflow: hidden; }}
.pair {{ display: grid; grid-template-columns: 1fr 1fr; }}
.pair.wide {{ grid-template-columns: 1fr; }}
.sw {{ display: flex; align-items: center; justify-content: center; padding: 12px; min-height: 72px; }}
.sw.dark {{ background: var(--bg); }}
.sw.light {{ background: {TEXT}; }}
.sw svg {{ max-width: 100%; height: auto; }}
.name {{ padding: 8px 12px; font: 14px/20px "IBM Plex Mono", Consolas, monospace; color: var(--text-2); word-break: break-all; }}
/* Tintable icons are authored in text-primary; on the light swatch they are shown in the background color. */
.tint .light .ink {{ fill: {BG}; }}
.tint .light .ink-s {{ stroke: {BG}; }}
"""
    out = ["<!doctype html>", '<html lang="en">', "<head>", '<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">', "<title>Orbit Royale brand and UI</title>",
           f"<style>{css}</style>", "</head>", "<body>", "<main>", "<h1>Orbit Royale brand and UI</h1>",
           "<p>Every SVG in this folder, on the dark background and on a light swatch. Item and HUD icons are authored in text-primary "
           "for tinting; the light swatch recolors them to show the silhouette. Logos are shown as authored.</p>"]
    k = 0
    for folder, title, size in SECTIONS:
        files = [w for w in WRITTEN if w[0] == folder]
        tint = folder in ("item-and-weapon-icons", "hud-icon-set")
        tile = 320 if folder == "orbit-logo-masters" else (220 if size > 64 else 180)
        out.append(f"<h2>{html.escape(title)} · {len(files)} files</h2>")
        out.append(f'<div class="grid{" tint" if tint else ""}" style="--tile:{tile}px">')
        for _, name, path in files:
            wide = folder == "orbit-logo-masters" and name.startswith("logo")
            sz = 280 if wide else (120 if folder == "orbit-logo-masters" else size)
            k += 1
            dark = inline(path, f"d{k}", sz)
            light = inline(path, f"l{k}", sz)
            out.append(f'<figure class="tile" style="margin:0"><div class="pair{" wide" if wide else ""}">'
                       f'<div class="sw dark">{dark}</div><div class="sw light">{light}</div></div>'
                       f'<figcaption class="name">{html.escape(folder)}/{html.escape(name)}.svg</figcaption></figure>')
        out.append("</div>")
    out += ["</main>", "</body>", "</html>", ""]
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))


# ------------------------------------------------------------------- main

def main():
    build_logos()
    scales = {}
    for name, title, mh in (("ar-7-wayfarer", "AR-7 Wayfarer", 80), ("sg-4-breaker", "SG-4 Breaker", 80),
                            ("p-12-spark", "P-12 Spark", 76), ("s-9-wisp", "S-9 Wisp", 80), ("sr-8-longview", "SR-8 Longview", 80)):
        scales[name] = weapon_icon(name, title, max_h=mh)
    build_items()
    build_hud()
    build_glyphs()
    bad = []
    for _, name, path in WRITTEN:
        try:
            ET.parse(path)
        except ET.ParseError as e:
            bad.append((path, str(e)))
    build_index()
    print("written", len(WRITTEN), "svg files; parse errors:", bad)
    print("weapon scales px/m:", {k: round(v, 1) for k, v in scales.items()})
    for folder in sorted({w[0] for w in WRITTEN}):
        print(folder, sum(1 for w in WRITTEN if w[0] == folder))


if __name__ == "__main__":
    main()
