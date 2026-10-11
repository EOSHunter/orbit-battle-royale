"""Shared helpers for the environment kits (ruins-kit, vegetation, terrain-kit).

Lives in a subfolder so build_models.py (which globs models/*.py) does not treat
it as an asset. Asset scripts add this folder to sys.path:

    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ruins-kit", "models", "lib"))
    import envkit as E

Coordinates follow kit.py: (x, f, u) = right, forward, up in meters.

Low-poly helpers: block (chamfered, jittered stone block), rock (faceted
boulder from a noisy icosphere cut by random planes), sweep (tube or ribbon
along a polyline: stems, roots, blades, petals, leaves), bud (bipyramid).

Detail helpers (baked only, they stand off a flat face by < cage):
masonry (stone plates whose gaps read as mortar joints), face_poly / face_ring
(glyph strips, medallions), strip (cracks, vines), glyph_column (the ruins'
signature vertical glow line through a ringed medallion).
"""

import math
import random

import bmesh
import bpy
from mathutils import Euler, Vector, noise

import kit
from kit import Model  # noqa: F401  (re-exported for scripts)

kit.MATERIALS.update({
    # Ancient ruins: dark weathered slate (ruins kit), pale sandstone (The Spine),
    # warm umber (Hollow Array). Glyphs glow teal-cyan, Spine slits amber.
    "ruin_slate": ("575d61", 0.0, 0.86, None, "stone"),
    "ruin_slate_dark": ("40454a", 0.0, 0.88, None, "stone"),
    "ruin_sand": ("8e897d", 0.0, 0.86, None, "stone"),
    "ruin_umber": ("75655a", 0.0, 0.86, None, "stone"),
    "ruin_sand_dark": ("7b776d", 0.0, 0.88, None, "stone"),
    "ruin_umber_dark": ("66584e", 0.0, 0.88, None, "stone"),
    "ruin_umber_light": ("877769", 0.0, 0.85, None, "stone"),
    "ruin_sand_light": ("a09b8f", 0.0, 0.85, None, "stone"),
    "crack": ("22262a", 0.0, 0.95, None, "stone"),
    "moss": ("52653a", 0.0, 0.92, None, "stone"),
    "moss_dark": ("46573a", 0.0, 0.92, None, "stone"),
    "ruin_slate_light": ("6d7477", 0.0, 0.85, None, "stone"),
    "glow_glyph": ("5fe6e2", 0.0, 0.35, "5fe6e2", "glow"),
    # Vegetation.
    "grass_pale": ("a7ab92", 0.0, 0.78, None, "stone"),
    "grass_dry": ("9c8f63", 0.0, 0.8, None, "stone"),
    "leaf_teal": ("3f5d5c", 0.0, 0.7, None, "stone"),
    "leaf_sage": ("6b7a5e", 0.0, 0.72, None, "stone"),
    "leaf_violet": ("5a4a86", 0.0, 0.62, None, "stone"),
    "petal": ("8f93b4", 0.0, 0.55, None, "stone"),
    "stem": ("4f5547", 0.0, 0.8, None, "stone"),
    "bark_dark": ("3a3433", 0.0, 0.9, None, "stone"),
    "soil": ("3d3630", 0.0, 0.95, None, "stone"),
    "cap_violet": ("6d5aa8", 0.0, 0.5, None, "stone"),
    "glow_violet": ("b48cff", 0.0, 0.35, "b48cff", "glow"),
    "glow_pink": ("ff9fd8", 0.0, 0.35, "ff9fd8", "glow"),
    # Terrain.
    "rock_gray": ("5f5d5a", 0.0, 0.86, None, "stone"),
    "rock_tan": ("8a7f6e", 0.0, 0.88, None, "stone"),
    # Volcanic glass: near-black, glossy, with paler conchoidal chips at the edges.
    "obsidian": ("1d2129", 0.25, 0.1, None, "stone"),
    "ring_alloy": ("59606a", 0.75, 0.42, None, "metal"),
    "ring_panel": ("3a3f47", 0.55, 0.5, None, "metal"),
})


def V(p):
    """(x, f, u) -> Blender vector."""
    return Vector((p[0], -p[1], p[2]))


def xfu(v):
    return (v.x, -v.y, v.z)


def _finish_bm(m, bm, mat, group, name, detail, top_mat=None, top_thresh=0.6, top_prob=1.0, rng=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if top_mat:
        rng = rng or random.Random(1)
        off = Vector((rng.uniform(0, 50), rng.uniform(0, 50), rng.uniform(0, 50)))
        for f in bm.faces:
            f.normal_update()
            # Coherent patches: a smooth noise field nudges the slope threshold and thins
            # the cover by top_prob, so moss gathers in drifts instead of speckles.
            c = f.calc_center_median()
            k = noise.noise(c * 1.4 + off)
            if f.normal.z + 0.3 * k > top_thresh and noise.noise(c * 0.9 + off * 1.3) > 0.45 - 0.9 * top_prob:
                f.material_index = 1
    obj = m._add(bm, mat, group, name, detail)
    if top_mat:
        obj.data.materials.append(kit.material(top_mat))
    return obj


def paint_up(obj, mat, thresh=0.6, prob=1.0, seed=1, below=None):
    """Assign a second material (moss, soil) to faces whose normal points up."""
    rng = random.Random(seed)
    me = obj.data
    idx = len(me.materials)
    me.materials.append(kit.material(mat))
    for p in me.polygons:
        if p.normal.z > thresh and rng.random() < prob and (below is None or p.center.z < below):
            p.material_index = idx
    return obj


# ------------------------------------------------------------------ blocks


def block(m, center, size, mat, bevel=0.05, jitter=0.0, seed=0, rot=(0.0, 0.0, 0.0), taper=1.0,
          group="body", name="block", detail=False, top_mat=None, top_prob=1.0, top_thresh=0.6):
    """Chamfered stone block. center (x, f, u), size (sx, sf, su). rot in degrees about x, f, u.
    taper scales the top face. 44 triangles with bevel, 12 without."""
    rng = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sf, su = size
    for v in bm.verts:
        t = taper if v.co.z > 0 else 1.0
        v.co = Vector((v.co.x * sx * t, v.co.y * sf * t, v.co.z * su))
    if bevel > 0:
        b = min(bevel, 0.3 * min(sx, sf, su))
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=b, offset_type="OFFSET", segments=1,
                        profile=0.5, affect="EDGES", clamp_overlap=True)
    if jitter > 0:
        for v in bm.verts:
            v.co += Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * jitter
    R = Euler((math.radians(rot[0]), math.radians(-rot[1]), math.radians(rot[2])), "XYZ").to_matrix()
    c = V(center)
    for v in bm.verts:
        v.co = R @ v.co + c
    return _finish_bm(m, bm, mat, group, name, detail, top_mat, top_thresh, top_prob, rng)


def rock(m, center, radii, mat, seed=0, subdiv=2, cuts=7, cut_depth=0.28, bumps=0.12, freq=1.6,
         floor=None, rot_u=0.0, group="body", name="rock", detail=False, top_mat=None, top_thresh=0.55,
         top_prob=1.0, bias_up=0.0, sharp=None, strata=0.0, strata_freq=6.0, fine=0.0, fine_freq=7.0,
         columns=0.0, columns_freq=5.0, cut_z=(-0.6, 1.0), flat_top=None):
    """Faceted rock: noisy icosphere, sliced flat by random planes (angular facets).
    floor: flatten the bottom at this fraction of the u radius (e.g. -0.3) so it sits.
    sharp: optional (k) exponent stretching the top into a point (glass shards).
    subdiv 1: 20 tris, 2: 80, 3: 320 before nothing is removed."""
    rng = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for v in bm.verts:
        d = v.co.normalized()
        n = noise.noise(d * freq + off)
        v.co = d * (1.0 + bumps * n)
    for _ in range(cuts):
        n = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(*cut_z) + bias_up)).normalized()
        dpl = 1.0 - rng.uniform(0.05, cut_depth)
        for v in bm.verts:
            k = v.co.dot(n)
            if k > dpl:
                v.co -= n * (k - dpl)
    if strata:
        # Horizontal layering (sedimentary ledges / columnar cliffs when stretched).
        for v in bm.verts:
            d = v.co.normalized()
            k = noise.noise(Vector((d.x * 1.2, d.y * 1.2, v.co.z * strata_freq)) + off)
            v.co += Vector((d.x, d.y, 0.0)) * strata * k
    if columns:
        # Vertical fluting / columnar jointing (cliffs): radial push varying around the axis.
        for v in bm.verts:
            d = v.co.normalized()
            hd = Vector((d.x, d.y, 0.0))
            if hd.length > 1e-6:
                k = noise.noise(Vector((d.x * columns_freq, d.y * columns_freq, v.co.z * 0.35)) + off)
                v.co += hd.normalized() * columns * k
    if fine:
        # Outward-only fine relief for the high-detail copy (cracks, pitting).
        for v in bm.verts:
            d = v.co.normalized()
            k = noise.fractal(d * fine_freq + off * 1.7, 0.6, 2.2, 4)
            v.co += d * fine * min(1.0, max(0.0, 0.5 + 0.6 * k))
    if flat_top is not None:
        for v in bm.verts:
            if v.co.z > flat_top:
                v.co.z = flat_top + (v.co.z - flat_top) * 0.15
    if floor is not None:
        for v in bm.verts:
            if v.co.z < floor:
                v.co.z = floor + (v.co.z - floor) * 0.08
    rx, rf, ru = radii
    R = Euler((0, 0, math.radians(rot_u)), "XYZ").to_matrix()
    c = V(center)
    for v in bm.verts:
        co = Vector((v.co.x * rx, v.co.y * rf, v.co.z * ru))
        v.co = R @ co + c
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.dissolve_degenerate(bm, dist=0.0005, edges=bm.edges)
    return _finish_bm(m, bm, mat, group, name, detail, top_mat, top_thresh, top_prob, rng)


# ------------------------------------------------------------------ sweeps


def sweep(m, pts, radii, mat, sides=6, flat=1.0, fold=0.0, normal=None, tip=False, twist=0.0,
          caps=True, phase=None, group="body", name="sweep", detail=False):
    """Tube / ribbon along a polyline of (x, f, u) points.
    radii: one per point. flat squashes the cross-section along the normal axis
    (ribbon). fold lifts the side edges along the normal (cupped leaf / petal).
    normal: hint (x, f, u) for the cross-section's up axis. tip: last point is a
    single vertex (pointed blade). twist: radians added per ring."""
    P = [V(p) for p in pts]
    n = len(P)
    T = []
    for i in range(n):
        t = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)])
        T.append(t.normalized())
    ref = V(normal) if normal is not None else (Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0)))
    N = ref - T[0] * ref.dot(T[0])
    if N.length < 1e-6:
        N = Vector((1, 0, 0)) - T[0] * T[0].x
    N.normalize()
    frames = []
    for i in range(n):
        if i > 0:
            Nn = N - T[i] * N.dot(T[i])
            if Nn.length > 1e-6:
                N = Nn.normalized()
        B = T[i].cross(N).normalized()
        frames.append((B, N))
    if phase is None:
        phase = 0.0
    bm = bmesh.new()
    rings = []
    for i in range(n):
        r = radii[i]
        if tip and i == n - 1:
            rings.append([bm.verts.new(P[i])])
            continue
        B, Nf = frames[i]
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides + phase + twist * i
            c, s = math.cos(a), math.sin(a)
            off = B * (c * r) + Nf * (s * r * flat + fold * r * abs(c))
            ring.append(bm.verts.new(P[i] + off))
        rings.append(ring)
    for i in range(n - 1):
        a, b = rings[i], rings[i + 1]
        if len(b) == 1:
            for k in range(sides):
                bm.faces.new((a[k], a[(k + 1) % sides], b[0]))
        else:
            for k in range(sides):
                j = (k + 1) % sides
                bm.faces.new((a[k], a[j], b[j], b[k]))
    if caps and len(rings[0]) > 2:
        bm.faces.new(list(reversed(rings[0])))
    if caps and len(rings[-1]) > 2:
        bm.faces.new(rings[-1])
    return _finish_bm(m, bm, mat, group, name, detail)


def curve(p0, p1, bend=(0.0, 0.0, 0.0), n=4, droop=0.0):
    """Points from p0 to p1 bowed by `bend` (x, f, u offset at the middle) and drooping
    by `droop` at the end (quadratic)."""
    out = []
    for i in range(n):
        t = i / (n - 1)
        b = 4 * t * (1 - t)
        out.append(tuple(p0[k] + (p1[k] - p0[k]) * t + bend[k] * b - (droop * t * t if k == 2 else 0.0) for k in range(3)))
    return out


def bud(m, base, tip, r, mat, sides=4, at=0.45, group="body", name="bud", detail=False):
    """Bipyramid (glowing buds, berries, stamen tips): 2*sides triangles."""
    a, b = V(base), V(tip)
    axis = (b - a).normalized()
    ref = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
    s1 = axis.cross(ref).normalized()
    s2 = axis.cross(s1).normalized()
    mid = a + (b - a) * at
    bm = bmesh.new()
    va, vb = bm.verts.new(a), bm.verts.new(b)
    ring = [bm.verts.new(mid + (s1 * math.cos(2 * math.pi * k / sides) + s2 * math.sin(2 * math.pi * k / sides)) * r) for k in range(sides)]
    for k in range(sides):
        j = (k + 1) % sides
        bm.faces.new((va, ring[j], ring[k]))
        bm.faces.new((vb, ring[k], ring[j]))
    return _finish_bm(m, bm, mat, group, name, detail)


# ------------------------------------------------------------ face details


def fmap(axis, sign, plane, a, b, h):
    """Point on an axis-aligned face. axis 'f': (a, b) = (x, u); 'x': (f, u); 'u': (x, f).
    h is the height above the face along its outward normal (sign)."""
    if axis == "f":
        return (a, plane + sign * h, b)
    if axis == "x":
        return (plane + sign * h, a, b)
    return (a, b, plane + sign * h)


def face_poly(m, axis, sign, plane, pts, h0, h1, mat, group="body", name="facepoly", detail=True):
    """Prism standing on a face: polygon pts [(a, b)...] from height h0 to h1."""
    bm = bmesh.new()
    lo = [bm.verts.new(V(fmap(axis, sign, plane, a, b, h0))) for a, b in pts]
    hi = [bm.verts.new(V(fmap(axis, sign, plane, a, b, h1))) for a, b in pts]
    bm.faces.new(lo)
    bm.faces.new(list(reversed(hi)))
    k = len(pts)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    return _finish_bm(m, bm, mat, group, name, detail)


def face_rect(m, axis, sign, plane, a0, a1, b0, b1, h0, h1, mat, **kw):
    return face_poly(m, axis, sign, plane, [(a0, b0), (a1, b0), (a1, b1), (a0, b1)], h0, h1, mat, **kw)


def face_ring(m, axis, sign, plane, a, b, r_out, r_in, h0, h1, mat, segs=24, group="body", name="ring", detail=True):
    bm = bmesh.new()
    vs = {}
    for key, r, h in (("ol", r_out, h0), ("oh", r_out, h1), ("il", r_in, h0), ("ih", r_in, h1)):
        vs[key] = [bm.verts.new(V(fmap(axis, sign, plane, a + r * math.cos(2 * math.pi * k / segs),
                                       b + r * math.sin(2 * math.pi * k / segs), h))) for k in range(segs)]
    for k in range(segs):
        j = (k + 1) % segs
        bm.faces.new((vs["ol"][k], vs["ol"][j], vs["oh"][j], vs["oh"][k]))
        bm.faces.new((vs["il"][j], vs["il"][k], vs["ih"][k], vs["ih"][j]))
        bm.faces.new((vs["oh"][k], vs["oh"][j], vs["ih"][j], vs["ih"][k]))
        bm.faces.new((vs["ol"][j], vs["ol"][k], vs["il"][k], vs["il"][j]))
    return _finish_bm(m, bm, mat, group, name, detail)


def face_disc(m, axis, sign, plane, a, b, r, h0, h1, mat, segs=16, **kw):
    pts = [(a + r * math.cos(2 * math.pi * k / segs), b + r * math.sin(2 * math.pi * k / segs)) for k in range(segs)]
    return face_poly(m, axis, sign, plane, pts, h0, h1, mat, **kw)


def strip(m, axis, sign, plane, pts, width, h0, h1, mat, **kw):
    """Polyline strip on a face (cracks, vines, glyph traces): one quad prism per segment."""
    for i in range(len(pts) - 1):
        (a0, b0), (a1, b1) = pts[i], pts[i + 1]
        da, db = a1 - a0, b1 - b0
        L = math.hypot(da, db) or 1.0
        na, nb = -db / L * width / 2, da / L * width / 2
        ext_a, ext_b = da / L * width * 0.3, db / L * width * 0.3
        quad = [(a0 + na - ext_a, b0 + nb - ext_b), (a1 + na + ext_a, b1 + nb + ext_b),
                (a1 - na + ext_a, b1 - nb + ext_b), (a0 - na - ext_a, b0 - nb - ext_b)]
        face_poly(m, axis, sign, plane, quad, h0, h1, mat, **kw)


def _clipped(top_fn, a0, a1, b1, margin):
    if top_fn is None:
        return b1
    lim = min(top_fn(a0 + (a1 - a0) * t / 6.0) for t in range(7)) - margin
    return min(b1, lim)


def masonry(m, axis, sign, plane, a0, a1, b0, b1, rng, mat, course=(0.45, 0.85), length=(0.5, 1.5),
            depth=(0.012, 0.024), gap=0.035, skip=(), top_fn=None, margin=0.04, crack_prob=0.25, group="body", bot_fn=None):
    """Cover a face rectangle with irregular stone plates (detail only). The gaps bake as
    mortar joints and the plate edges as chipped block edges. skip: rects (a0, a1, b0, b1)
    left free for glyphs. top_fn(a) -> max b (clip under broken outlines)."""
    a0 += margin
    a1 -= margin
    b0 += margin
    b1 -= margin
    b = b0
    while b < b1 - 0.12:
        h = rng.uniform(*course)
        bt = min(b + h, b1)
        if b1 - bt < 0.2:
            bt = b1
        a = a0 + (rng.uniform(0, length[0]) if rng.random() < 0.5 else 0)
        if a > a0 + 0.12:
            _plate_skip(m, axis, sign, plane, a0, a - gap, b, bt - gap, rng, mat, depth, skip, top_fn, margin, crack_prob, group, bot_fn)
        while a < a1 - 0.1:
            w = rng.uniform(*length)
            at = min(a + w, a1)
            if a1 - at < 0.25:
                at = a1
            _plate_skip(m, axis, sign, plane, a, at - gap, b, bt - gap, rng, mat, depth, skip, top_fn, margin, crack_prob, group, bot_fn)
            a = at
        b = bt


def _plate_skip(m, axis, sign, plane, a0, a1, b0, b1, rng, mat, depth, skip, top_fn, margin, crack_prob, group, bot_fn=None):
    pieces = [(a0, a1)]
    for s0, s1, t0, t1 in skip:
        if b1 <= t0 or b0 >= t1:
            continue
        nxt = []
        for p0, p1 in pieces:
            if p1 <= s0 or p0 >= s1:
                nxt.append((p0, p1))
                continue
            if p0 < s0:
                nxt.append((p0, s0))
            if p1 > s1:
                nxt.append((s1, p1))
        pieces = nxt
    for p0, p1 in pieces:
        if p1 - p0 < 0.1:
            continue
        top = _clipped(top_fn, p0, p1, b1, margin)
        if bot_fn is not None:
            b0 = max(b0, max(bot_fn(p0 + (p1 - p0) * t / 6.0) for t in range(7)) + margin)
        if top - b0 < 0.1:
            continue
        d = rng.uniform(*depth)
        pm = mat if isinstance(mat, str) else rng.choice(mat)
        face_rect(m, axis, sign, plane, p0, p1, b0, top, -0.004, d, pm, group=group)
        if rng.random() < crack_prob and (p1 - p0) > 0.4:
            # Hairline crack across the block.
            ca = rng.uniform(p0 + 0.1, p1 - 0.1)
            pts = [(ca, top - 0.02)]
            bb = top
            while bb > b0 + 0.08:
                bb -= rng.uniform(0.08, 0.2)
                pts.append((min(max(pts[-1][0] + rng.uniform(-0.1, 0.1), p0 + 0.03), p1 - 0.03), max(bb, b0 + 0.04)))
            strip(m, axis, sign, plane, pts, 0.012, d - 0.006, d + 0.002, "crack", group=group)


def glyph_column(m, axis, sign, plane, a, b0, b1, rings=(), stone="ruin_slate", glow="glow_glyph",
                 w=0.05, r=0.32, group="body"):
    """The ruins' signature: a glowing channel running up a face, threaded through ringed
    medallions. Returns the skip rects for masonry()."""
    skip = [(a - w - 0.05, a + w + 0.05, b0, b1)]
    face_rect(m, axis, sign, plane, a - w / 2, a + w / 2, b0, b1, -0.004, 0.009, glow, group=group)
    # Raised lips either side of the channel.
    for s in (-1, 1):
        face_rect(m, axis, sign, plane, a + s * (w / 2 + 0.005), a + s * (w / 2 + 0.05), b0, b1, -0.004, 0.026, stone, group=group)
    for rb in rings:
        face_ring(m, axis, sign, plane, a, rb, r, r * 0.8, -0.004, 0.03, stone, group=group)
        face_ring(m, axis, sign, plane, a, rb, r * 0.74, r * 0.62, -0.004, 0.02, glow, group=group)
        face_disc(m, axis, sign, plane, a, rb, r * 0.5, -0.004, 0.028, stone, group=group)
        face_disc(m, axis, sign, plane, a, rb, r * 0.16, -0.004, 0.032, glow, segs=10, group=group)
        skip.append((a - r - 0.04, a + r + 0.04, rb - r - 0.04, rb + r + 0.04))
    return skip


def vines(m, axis, sign, plane, a0, a1, b_top, rng, count=3, length=(0.6, 2.0), b_min=0.0, top_fn=None,
          h=(0.022, 0.03), group="body"):
    """Moss streaks and hanging vines on a face, baked into the color map."""
    for _ in range(count):
        a = rng.uniform(a0, a1)
        top = top_fn(a) - 0.02 if top_fn else b_top - 0.02
        L = rng.uniform(*length)
        pts = [(a, top)]
        b = top
        while b > max(top - L, b_min + 0.1):
            b -= rng.uniform(0.12, 0.3)
            pts.append((pts[-1][0] + rng.uniform(-0.06, 0.06), b))
        w = rng.uniform(0.05, 0.12)
        mat = "moss" if rng.random() < 0.6 else "moss_dark"
        strip(m, axis, sign, plane, pts, w, -0.004, rng.uniform(*h), mat, group=group)
        # Leafy clumps along the vine.
        for (pa, pb) in pts[1::2]:
            face_disc(m, axis, sign, plane, pa + rng.uniform(-0.05, 0.05), pb, rng.uniform(0.05, 0.11), -0.004,
                      rng.uniform(*h), mat, segs=6, group=group)
        # Moss cushion where it starts.
        face_disc(m, axis, sign, plane, a, top - 0.06, rng.uniform(0.12, 0.22), -0.004, h[1], mat, segs=7, group=group)


# Plate palettes: mostly the base stone with darker and lighter blocks mixed in.
SLATE = ["ruin_slate", "ruin_slate", "ruin_slate", "ruin_slate_dark", "ruin_slate_light"]
SAND = ["ruin_sand", "ruin_sand", "ruin_sand", "ruin_sand_dark", "ruin_sand_light"]
UMBER = ["ruin_umber", "ruin_umber", "ruin_umber", "ruin_umber_dark", "ruin_umber_light"]


def transformed(m, fn, rotate=(0.0, 0.0, 0.0), pivot=(0.0, 0.0, 0.0), move=(0.0, 0.0, 0.0)):
    """Run fn() (which adds parts and details), then rotate/move everything it added.
    Lets face details be authored on an axis-aligned block and then tumbled."""
    before = {id(o) for store in (m.parts, m.details) for objs in store.values() for o in objs}
    out = fn()
    for store in (m.parts, m.details):
        for objs in store.values():
            for o in objs:
                if id(o) not in before:
                    m.transform(o, rotate=rotate, pivot=pivot, move=move)
    return out


# ------------------------------------------------------------ organics


def paint_dir(obj, mat, direction=(0.0, 0.0, -1.0), thresh=0.3, prob=1.0, seed=1):
    """Assign a second material to faces facing `direction` (x, f, u), e.g. glowing gills
    on the underside of a cap."""
    rng = random.Random(seed)
    d = V(direction).normalized()
    me = obj.data
    idx = len(me.materials)
    me.materials.append(kit.material(mat))
    for p in me.polygons:
        if p.normal.dot(d) > thresh and rng.random() < prob:
            p.material_index = idx
    return obj


def frames(pts, normal=None):
    """Parallel-transport frames along a polyline, matching sweep(): [(P, T, B, N)] in Blender space."""
    P = [V(p) for p in pts]
    n = len(P)
    T = [(P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized() for i in range(n)]
    ref = V(normal) if normal is not None else (Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0)))
    N = ref - T[0] * ref.dot(T[0])
    if N.length < 1e-6:
        N = Vector((1, 0, 0)) - T[0] * T[0].x
    N.normalize()
    out = []
    for i in range(n):
        if i > 0:
            Nn = N - T[i] * N.dot(T[i])
            if Nn.length > 1e-6:
                N = Nn.normalized()
        out.append((P[i], T[i], T[i].cross(N).normalized(), N))
    return out


def on_ribbon(pts, radii, normal, k, lift, flat=0.0, fold=0.0):
    """Points on the top surface of a sweep() ribbon: k in -1..1 across the width
    (0 = midrib), lifted `lift` meters off the surface. Returns (x, f, u) points."""
    out = []
    for (P, T, B, N), r in zip(frames(pts, normal), radii):
        c = abs(k)
        h = flat * r * (1 - c) + fold * r * c + lift
        out.append(xfu(P + B * (k * r) + N * h))
    return out


def leaf(m, base, tip, width, mat, normal=(0.0, 0.0, 1.0), thick=0.25, at=0.45, cup=0.3, group="body", name="leaf", detail=False):
    """Small solid leaf: diamond with a raised midrib and cupped edges, 8 triangles."""
    a, b = V(base), V(tip)
    axis = (b - a).normalized()
    nv = V(normal)
    nv = (nv - axis * nv.dot(axis))
    if nv.length < 1e-6:
        nv = Vector((0, 0, 1)) - axis * axis.z
    nv.normalize()
    side = axis.cross(nv).normalized()
    mid = a + (b - a) * at
    bm = bmesh.new()
    va, vb = bm.verts.new(a), bm.verts.new(b)
    ring = [bm.verts.new(mid + side * width + nv * width * cup), bm.verts.new(mid + nv * width * thick),
            bm.verts.new(mid - side * width + nv * width * cup), bm.verts.new(mid - nv * width * thick * 0.4)]
    for k in range(4):
        j = (k + 1) % 4
        bm.faces.new((va, ring[j], ring[k]))
        bm.faces.new((vb, ring[k], ring[j]))
    return _finish_bm(m, bm, mat, group, name, detail)


def profile_sweep(m, pts, profile, mat, normal=None, caps=True, group="body", name="psweep", detail=False, scale=None):
    """Sweep an arbitrary closed 2D profile [(b, n)] (b across, n along the normal) along a
    polyline. scale: optional per-point multiplier."""
    fr = frames(pts, normal)
    bm = bmesh.new()
    rings = []
    for i, (P, T, B, N) in enumerate(fr):
        s = scale[i] if scale else 1.0
        rings.append([bm.verts.new(P + B * (pb * s) + N * (pn * s)) for pb, pn in profile])
    k = len(profile)
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for j in range(k):
            jj = (j + 1) % k
            bm.faces.new((a[j], a[jj], b[jj], b[j]))
    if caps:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    return _finish_bm(m, bm, mat, group, name, detail)


def shard(m, base, height, radius, mat, seed=0, sides=5, lean=(0.0, 0.0), mid=0.55, twist=0.4, top_cut=0.0,
          group="body", name="shard", detail=False, sink=0.3):
    """Sharp crystal / glass shard: irregular polygon base, a narrowed facet break, an
    off-center apex (or a slanted broken top when top_cut > 0). About 4*sides triangles."""
    rng = random.Random(seed)
    bx, bf, bu = base
    lx, lf = lean
    angs = sorted(rng.uniform(0, 2 * math.pi) for _ in range(sides))
    angs = [2 * math.pi * k / sides + rng.uniform(-0.35, 0.35) for k in range(sides)]
    bm = bmesh.new()

    def ring(h, scl, rot):
        out = []
        for a in angs:
            rr = radius * scl * rng.uniform(0.75, 1.15)
            out.append(bm.verts.new(V((bx + lx * h + rr * math.cos(a + rot), bf + lf * h + rr * math.sin(a + rot), bu + h))))
        return out

    r0 = ring(-sink, 1.0, 0.0)
    r1 = ring(height * mid, rng.uniform(0.5, 0.7), twist * rng.uniform(-1, 1))
    for k in range(sides):
        j = (k + 1) % sides
        bm.faces.new((r0[k], r0[j], r1[j], r1[k]))
    bm.faces.new(list(reversed(r0)))
    if top_cut > 0:
        r2 = ring(height * (1 - top_cut), 0.35, 0.0)
        for k, v in enumerate(r2):
            v.co.z += (math.cos(angs[k]) * radius * 0.6) * rng.uniform(0.6, 1.4)
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new((r1[k], r1[j], r2[j], r2[k]))
        bm.faces.new(r2)
    else:
        apex = bm.verts.new(V((bx + lx * height + rng.uniform(-0.15, 0.15) * radius, bf + lf * height + rng.uniform(-0.15, 0.15) * radius, bu + height)))
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new((r1[k], r1[j], apex))
    return _finish_bm(m, bm, mat, group, name, detail)


def rock_pair(m, center, radii, mat, seed=0, subdiv=2, high=5, fine=0.035, fine_freq=7.0, top_mat=None, top_prob=1.0,
              top_thresh=0.55, high_top_prob=0.8, **kw):
    """A low-poly rock plus its high-resolution twin (detail only): same silhouette, but
    the twin carries fine outward relief (cracks, pitting, ledges) that bakes into the
    normal map, and its own finer moss mask."""
    low = rock(m, center, radii, mat, seed=seed, subdiv=subdiv, top_mat=top_mat, top_prob=top_prob, top_thresh=top_thresh, **kw)
    rock(m, center, radii, mat, seed=seed, subdiv=high, fine=fine, fine_freq=fine_freq, detail=True, top_mat=top_mat,
         top_prob=high_top_prob, top_thresh=top_thresh, **kw)
    return low
