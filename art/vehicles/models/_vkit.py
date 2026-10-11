"""Shared helpers for vehicle and aircraft models (not an asset: the underscore
makes build_models.py skip it). Import from a vehicle script with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _vkit import *

Coordinates follow kit.py: f forward, u up, x right, meters.
"""

import math
import os
import sys

import bmesh

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import kit  # noqa: E402

# Extra materials shared by the vehicles.
kit.MATERIALS.setdefault("bronze", ("7a6040", 0.75, 0.42, None, "metal"))       # roll cage accents, tubes
kit.MATERIALS.setdefault("spring", ("c8962c", 0.7, 0.38, None, "metal"))        # coilover springs
kit.MATERIALS.setdefault("navy", ("2f3a4c", 0.25, 0.5, None, "paint"))          # darker armor
kit.MATERIALS.setdefault("seat", ("2a2c30", 0.0, 0.85, None, "polymer"))        # seat fabric
kit.MATERIALS.setdefault("glow_red", ("ff4a2e", 0.0, 0.4, "ff4a2e", "glow"))    # tail lights
kit.MATERIALS.setdefault("tinted_glass", ("1c2630", 0.6, 0.06, None, "metal"))  # smoked cockpit glass


def octo(f, w, u0, u1, c, ct=None, x=0.0):
    """Chamfered rectangle cross-section ring at f: half width w, from u0 to u1.
    c = bottom chamfer, ct = top chamfer (defaults to c). 8 points, same order every call."""
    ct = c if ct is None else ct
    return [(x + w, f, u0 + c), (x + w, f, u1 - ct), (x + w - ct, f, u1), (x - w + ct, f, u1),
            (x - w, f, u1 - ct), (x - w, f, u0 + c), (x - w + c, f, u0), (x + w - c, f, u0)]


def hull_ring(f, w, u0, u1, c, ct=None, bulge=0.04, x=0.0):
    """16-point hull cross-section: the octo() ring with every edge split and its
    midpoint pushed outward by bulge * half-size, for smoother fuselages."""
    pts = octo(f, w, u0, u1, c, ct, x)
    cu = (u0 + u1) / 2.0
    out = []
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        out.append(p)
        mx, mu = (p[0] + q[0]) / 2.0, (p[2] + q[2]) / 2.0
        dx, du = mx - x, mu - cu
        d = max(1e-6, (dx * dx + du * du) ** 0.5)
        k = bulge * max(w, (u1 - u0) / 2.0)
        out.append((mx + dx / d * k, f, mu + du / d * k))
    return out


def face_panel(m, quad, mat, inset=0.08, depth=0.03, push=0.012, center=None, group="body", detail=False):
    """Panel laid on a hull face: quad [(x, f, u)] shrunk toward its centroid by inset (fraction)
    and pushed outward (away from center (x, u) axis, default (0, mid)) so it sits proud."""
    from mathutils import Vector
    vs = [Vector(p) for p in quad]
    c = sum(vs, Vector((0, 0, 0))) / len(vs)
    vs = [c + (v - c) * (1 - inset) for v in vs]
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(vs)):
        a, b = vs[i], vs[(i + 1) % len(vs)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    n.normalize()
    ax = Vector((center[0], c.y, center[1])) if center else Vector((0.0, c.y, c.z - 0.5))
    if n.dot(c - ax) < 0:
        n = -n
    vs = [v + n * push for v in vs]
    return panel(m, [tuple(v) for v in vs], depth, mat, group=group, detail=detail)


def circle_x(x, f, u, r, n, phase=0.5):
    """Ring of n points in the f-u plane at x (for lofts along x, e.g. tires)."""
    return [(x, f + r * math.cos(2 * math.pi * (i + phase) / n), u + r * math.sin(2 * math.pi * (i + phase) / n)) for i in range(n)]


def circle_f(x, f, u, r, n, phase=0.5, sx=1.0, su=1.0):
    """Ring of n points in the x-u plane at f (for lofts along f: fuselages, nacelles)."""
    return [(x + sx * r * math.cos(2 * math.pi * (i + phase) / n), f, u + su * r * math.sin(2 * math.pi * (i + phase) / n)) for i in range(n)]


def circle_u(x, f, u, r, n, phase=0.5, sx=1.0, sf=1.0):
    """Ring of n points in the x-f plane at height u (for lofts upward: pods, domes)."""
    return [(x + sx * r * math.cos(2 * math.pi * (i + phase) / n), f + sf * r * math.sin(2 * math.pi * (i + phase) / n), u) for i in range(n)]


def xtube(m, f, u, x0, x1, r_out, r_in, mat, sides=16, group="body", detail=False, name="xtube"):
    """Annulus extruded sideways from x0 to x1 (rims, rings on wheel faces)."""
    bm = bmesh.new()
    o0, o1, i0, i1 = [], [], [], []
    for k in range(sides):
        a = 2 * math.pi * (k + 0.5) / sides
        ca, sa = math.cos(a), math.sin(a)
        o0.append(bm.verts.new((x0, -(f + ca * r_out), u + sa * r_out)))
        o1.append(bm.verts.new((x1, -(f + ca * r_out), u + sa * r_out)))
        i0.append(bm.verts.new((x0, -(f + ca * r_in), u + sa * r_in)))
        i1.append(bm.verts.new((x1, -(f + ca * r_in), u + sa * r_in)))
    for k in range(sides):
        j = (k + 1) % sides
        bm.faces.new((o0[k], o0[j], o1[j], o1[k]))
        bm.faces.new((i0[j], i0[k], i1[k], i1[j]))
        bm.faces.new((o0[j], o0[k], i0[k], i0[j]))
        bm.faces.new((o1[k], o1[j], i1[j], i1[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return m._add(bm, mat, group, name, detail)


def utube(m, x, f, u0, u1, r_out, r_in, mat, sides=16, group="body", detail=False, name="utube", sf=1.0):
    """Annulus extruded upward (ducted fan shrouds, hatches, rings on top faces)."""
    bm = bmesh.new()
    o0, o1, i0, i1 = [], [], [], []
    for k in range(sides):
        a = 2 * math.pi * (k + 0.5) / sides
        ca, sa = math.cos(a), math.sin(a)
        o0.append(bm.verts.new((x + ca * r_out, -(f + sa * r_out * sf), u0)))
        o1.append(bm.verts.new((x + ca * r_out, -(f + sa * r_out * sf), u1)))
        i0.append(bm.verts.new((x + ca * r_in, -(f + sa * r_in * sf), u0)))
        i1.append(bm.verts.new((x + ca * r_in, -(f + sa * r_in * sf), u1)))
    for k in range(sides):
        j = (k + 1) % sides
        bm.faces.new((o0[k], o0[j], o1[j], o1[k]))
        bm.faces.new((i0[j], i0[k], i1[k], i1[j]))
        bm.faces.new((o0[j], o0[k], i0[k], i0[j]))
        bm.faces.new((o1[k], o1[j], i1[j], i1[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return m._add(bm, mat, group, name, detail)


def torus(m, center, axis, R, r, mat, n=12, k=4, group="body", detail=False, name="torus"):
    """Ring of radius R and tube radius r around axis 'x', 'f' or 'u' through center (x, f, u)."""
    cx, cf, cu = center
    bm = bmesh.new()
    rows = []
    for i in range(n):
        a = 2 * math.pi * i / n
        row = []
        for j in range(k):
            b = 2 * math.pi * (j + 0.5) / k
            rad = R + r * math.cos(b)
            h = r * math.sin(b)
            p, q = rad * math.cos(a), rad * math.sin(a)
            if axis == "x":
                co = (cx + h, cf + p, cu + q)
            elif axis == "f":
                co = (cx + p, cf + h, cu + q)
            else:
                co = (cx + p, cf + q, cu + h)
            row.append(bm.verts.new((co[0], -co[1], co[2])))
        rows.append(row)
    for i in range(n):
        i2 = (i + 1) % n
        for j in range(k):
            j2 = (j + 1) % k
            bm.faces.new((rows[i][j], rows[i2][j], rows[i2][j2], rows[i][j2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return m._add(bm, mat, group, name, detail)


def bolt_x(m, f, u, x, r=0.014, h=0.008, mat="steel", group="body", sides=6):
    """Bolt head on a face at x, pointing outward (sign of x). Baked only."""
    s = 1 if x >= 0 else -1
    m.xcyl(f, u, x - s * 0.002, x + s * h, r, mat, sides=sides, group=group, name="bolt", detail=True)


def bolt_u(m, x, f, u, r=0.014, h=0.008, mat="steel", group="body", down=False, sides=6):
    """Bolt head on an upward (or downward) face at height u. Baked only."""
    s = -1 if down else 1
    m.vcyl(f, min(u - s * 0.002, u + s * h), max(u - s * 0.002, u + s * h), r, mat, sides=sides, x=x, group=group, name="bolt", detail=True)


def bolt_f(m, x, u, f, r=0.014, h=0.008, mat="steel", group="body", back=False, sides=6):
    """Bolt head on a forward (or backward) face at f. Baked only."""
    s = -1 if back else 1
    m.cyl(f - s * 0.002, f + s * h, u, r, mat, sides=sides, x=x, group=group, name="bolt", detail=True)


def plate_x(m, profile, x, mat, depth=0.006, group="body", mirror=True):
    """Raised panel (side profile [(f, u)]) on the face at x, and its mirror at -x. Baked only."""
    for s in ((1, -1) if mirror else (1,)):
        xx = s * x
        sg = 1 if xx >= 0 else -1
        m.prism(profile, depth + 0.002, mat, x=xx + sg * (depth / 2 - 0.001), group=group, name="plate", detail=True)


def plate_u(m, profile, u, mat, depth=0.006, group="body", down=False):
    """Raised panel (top profile [(x, f)]) on a face at height u. Baked only."""
    if down:
        m.top_prism(profile, u - depth, u + 0.002, mat, group=group, name="plate", detail=True)
    else:
        m.top_prism(profile, u - 0.002, u + depth, mat, group=group, name="plate", detail=True)


def plate_f(m, profile, f, mat, depth=0.006, group="body", back=False):
    """Raised panel (front profile [(x, u)]) on a face at f. Baked only."""
    if back:
        m.front_prism(profile, f + 0.002, f - depth, mat, group=group, name="plate", detail=True)
    else:
        m.front_prism(profile, f - 0.002, f + depth, mat, group=group, name="plate", detail=True)


def vents_x(m, f0, f1, u0, u1, x, count, mat="polymer", depth=0.008, group="body", mirror=True):
    """Row of vertical fins on the face at x: reads as a louvered vent. Baked only."""
    step = (f1 - f0) / count
    for i in range(count):
        a = f0 + i * step
        plate_x(m, kit.chamfer_rect(a, a + step * 0.45, u0, u1), x, mat, depth, group, mirror)


def vents_u(m, x0, x1, f0, f1, u, count, mat="polymer", depth=0.008, group="body"):
    """Row of fins across x on a top face: louvers. Baked only."""
    step = (f1 - f0) / count
    for i in range(count):
        a = f0 + i * step
        plate_u(m, [(x0, a), (x1, a), (x1, a + step * 0.45), (x0, a + step * 0.45)], u, mat, depth, group)


def wheel(m, f, u, x, r, w, group, tire="rubber", rim="graphite", accent="ivory", sides=18, lugs=18,
          lug_h=0.03, hub_ratio=0.6, lug_c=0.012, side_lugs=True):
    """Off-road wheel centered at (x, f, u): chunky tire with low-poly lugs on the silhouette,
    recessed rim with accent ring, hub cap. Outer face points away from the centerline."""
    s = 1 if x >= 0 else -1
    xo, xi = x + s * w / 2, x - s * w / 2
    hr = r * hub_ratio
    # Tire body lofted across its width: inner cap, sidewall, tread, sidewall, recessed rim face.
    prof = [(xi + s * 0.0, hr * 0.98), (xi, r * 0.86), (xi + s * w * 0.12, r * 0.985),
            (xo - s * w * 0.12, r * 0.985), (xo, r * 0.86), (xo, hr * 1.04),
            (xo - s * 0.05, hr * 0.98)]
    rings = [circle_x(px, f, u, pr, sides) for px, pr in prof]
    m.loft(rings, tire, group=group, name="tire")
    # Chunky alternating lugs: low poly so the silhouette reads knobby.
    for i in range(lugs):
        a = 360.0 * i / lugs
        if i % 2:
            x0, x1 = sorted((x + s * 0.01, xo + s * 0.006))
        else:
            x0, x1 = sorted((xi - s * 0.006, x - s * 0.01))
        lw = 2 * math.pi * r / lugs * 0.55
        o = m.side_box(f - lw / 2, f + lw / 2, u + r * 0.95, u + r + lug_h, x0, x1, tire, c=lug_c, group=group, name="lug")
        m.transform(o, rotate=(a, 0, 0), pivot=(x, f, u))
    # Rim: recessed disc, raised spokes ring, accent ring and hub cap.
    xtube(m, f, u, xo - s * 0.05, xo - s * 0.035, hr * 0.98, hr * 0.62, rim, sides=sides, group=group, name="rim")
    m.xcyl(f, u, xo - s * 0.05, xo - s * 0.02, hr * 0.42, rim, sides=10, group=group, name="hub")
    m.xcyl(f, u, xo - s * 0.03, xo - s * 0.005, hr * 0.2, "gunmetal", sides=8, group=group, name="cap")
    # Baked: accent ring segments, lug nuts, tread grooves on the sidewall.
    for k in range(4):
        a0 = k * 90 + 12
        for j in range(3):
            a = math.radians(a0 + j * 22)
            pf, pu = f + math.cos(a) * hr * 0.8, u + math.sin(a) * hr * 0.8
            m.xcyl(pf, pu, xo - s * 0.037, xo - s * 0.03, hr * 0.13, accent, sides=6, group=group, name="accent", detail=True)
    for k in range(6):
        a = math.radians(k * 60)
        m.xcyl(f + math.cos(a) * hr * 0.3, u + math.sin(a) * hr * 0.3, xo - s * 0.022, xo - s * 0.012, 0.016, "steel", sides=6, group=group, name="nut", detail=True)
    for i in range(lugs * 2 if side_lugs else 0):
        a = math.radians(360.0 * (i + 0.5) / (lugs * 2))
        pf, pu = f + math.cos(a) * r * 0.93, u + math.sin(a) * r * 0.93
        o = m.side_box(pf - 0.025, pf + 0.025, pu - 0.04, pu + 0.04, xo - s * 0.006, xo + s * 0.006, tire, c=0.008, group=group, name="sidelug", detail=True)
        m.transform(o, rotate=(math.degrees(a) - 90, 0, 0), pivot=(x, pf, pu))


def panel(m, pts, depth, mat, group="body", detail=False, name="panel"):
    """Slab from a planar polygon [(x, f, u), ...] thickened by depth along its normal
    (centered on the polygon). For glass, armor plates and decals on sloped faces."""
    from mathutils import Vector
    vs = [Vector(p) for p in pts]
    n = Vector((0.0, 0.0, 0.0))
    for i in range(len(vs)):
        a, b = vs[i], vs[(i + 1) % len(vs)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    n.normalize()
    r0 = [tuple(v - n * depth / 2) for v in vs]
    r1 = [tuple(v + n * depth / 2) for v in vs]
    return m.loft([r0, r1], mat, group=group, name=name, detail=detail)


def loft_open(m, rings, mat, skip=(), group="body", name="loft", detail=False):
    """Like Model.loft, but faces (k, i) in skip are removed: an opening between ring k and
    k+1 starting at point i. Normals are computed on the closed shape first, so the open
    shell keeps facing outward."""
    bm = bmesh.new()
    vs = [[bm.verts.new((x, -f, u)) for x, f, u in ring] for ring in rings]
    n = len(rings[0])
    holes = []
    for k in range(len(vs) - 1):
        for i in range(n):
            j = (i + 1) % n
            face = bm.faces.new((vs[k][i], vs[k][j], vs[k + 1][j], vs[k + 1][i]))
            if (k, i) in skip:
                holes.append(face)
    bm.faces.new(vs[0])
    bm.faces.new(list(reversed(vs[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.delete(bm, geom=holes, context="FACES_ONLY")
    return m._add(bm, mat, group, name, detail)


def thick_strip(m, poly_a, poly_b, thickness, center_u, mat, group="body", name="strip", detail=False):
    """Solid plate between two polylines [(x, f, u)] (same count), thickened inward toward the
    axis (x=0, u=center_u). Used for doors and ramps that close an opening in a hull."""
    from mathutils import Vector

    def inward(p):
        d = Vector((-p[0], 0.0, center_u - p[2]))
        d.normalize()
        return (p[0] + d.x * thickness, p[1], p[2] + d.z * thickness)

    bm = bmesh.new()
    oa = [bm.verts.new((p[0], -p[1], p[2])) for p in poly_a]
    ob = [bm.verts.new((p[0], -p[1], p[2])) for p in poly_b]
    ia = [bm.verts.new((q[0], -q[1], q[2])) for q in map(inward, poly_a)]
    ib = [bm.verts.new((q[0], -q[1], q[2])) for q in map(inward, poly_b)]
    n = len(poly_a)
    for i in range(n - 1):
        bm.faces.new((oa[i], oa[i + 1], ob[i + 1], ob[i]))
        bm.faces.new((ia[i + 1], ia[i], ib[i], ib[i + 1]))
        bm.faces.new((oa[i + 1], oa[i], ia[i], ia[i + 1]))
        bm.faces.new((ob[i], ob[i + 1], ib[i + 1], ib[i]))
    bm.faces.new((oa[0], ob[0], ib[0], ia[0]))
    bm.faces.new((ob[-1], oa[-1], ia[-1], ib[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return m._add(bm, mat, group, name, detail)


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


def origins(model_id, pivots):
    """before_export hook: move the origin of group objects to their pivot (x, f, u),
    so the game can spin wheels and rotors or swing ramps about their own origin."""
    from mathutils import Matrix, Vector

    def hook(lows):
        for low in lows:
            for group, p in pivots.items():
                if low.name == f"{model_id}-{group}":
                    v = Vector((p[0], -p[1], p[2]))
                    low.data.transform(Matrix.Translation(-v))
                    low.location = v
    return hook
