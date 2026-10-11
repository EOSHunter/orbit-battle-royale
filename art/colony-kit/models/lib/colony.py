"""Shared helpers for the colony structure kit and the prop kit.

Lives in a subfolder so build_models.py (which globs models/*.py) does not
treat it as an asset. Scripts import it with:

    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "colony-kit", "models", "lib"))
    from colony import *

Axes follow the kit: x right, f forward, u up, 1 unit = 1 m.
"""

import math

import kit
from kit import Model, chamfer_rect

# Colony palette additions (concept 31/40: burnt-orange panels, dark frames).
kit.MATERIALS.setdefault("rust_orange", ("9a4a26", 0.1, 0.6, None, "paint"))
kit.MATERIALS.setdefault("dark_steel", ("2c3139", 0.75, 0.45, None, "metal"))
kit.MATERIALS.setdefault("navy", ("2f3a4f", 0.2, 0.55, None, "paint"))
kit.MATERIALS.setdefault("window_glow", ("141e28", 0.3, 0.12, "1e1610", "glow"))
kit.MATERIALS.setdefault("container_green", ("4a5a3c", 0.15, 0.6, None, "paint"))
kit.MATERIALS.setdefault("container_blue", ("34465e", 0.15, 0.6, None, "paint"))
kit.MATERIALS.setdefault("canvas", ("6d6450", 0.0, 0.92, None, "polymer"))
kit.MATERIALS.setdefault("asphalt", ("3a3d42", 0.0, 0.9, None, "stone"))


def blk(m, x0, x1, f0, f1, u0, u1, mat, c=0.0, axis="x", detail=False, group="body", name="blk"):
    """Axis-aligned block. c chamfers the edges that run along `axis`."""
    x0, x1 = min(x0, x1), max(x0, x1)
    f0, f1 = min(f0, f1), max(f0, f1)
    u0, u1 = min(u0, u1), max(u0, u1)
    if axis == "x":
        return m.box(f0, f1, u0, u1, x1 - x0, mat, x=(x0 + x1) / 2, c=c, group=group, name=name, detail=detail)
    if axis == "u":
        return m.top_prism(chamfer_rect(x0, x1, f0, f1, c), u0, u1, mat, group=group, name=name, detail=detail)
    return m.front_prism(chamfer_rect(x0, x1, u0, u1, c), f0, f1, mat, group=group, name=name, detail=detail)


# ------------------------------------------------------------ detail (baked)

def fplate(m, x0, x1, u0, u1, f_face, sign, mat, depth=0.012, c=0.015):
    """Raised plate on a face whose normal points toward sign*f."""
    return blk(m, x0, x1, f_face - sign * 0.003, f_face + sign * depth, u0, u1, mat, c=c, axis="f", detail=True)


def xplate(m, f0, f1, u0, u1, x_face, sign, mat, depth=0.012, c=0.015):
    """Raised plate on a face whose normal points toward sign*x."""
    return blk(m, x_face - sign * 0.003, x_face + sign * depth, f0, f1, u0, u1, mat, c=c, axis="x", detail=True)


def uplate(m, x0, x1, f0, f1, u_face, mat, depth=0.008, c=0.0):
    """Painted / raised plate on an upward face."""
    return blk(m, x0, x1, f0, f1, u_face - 0.003, u_face + depth, mat, c=c, axis="u", detail=True)


def fbolt(m, x, u, f_face, sign, r=0.02, mat="steel"):
    m.cyl(f_face - sign * 0.003, f_face + sign * 0.011, u, r, mat, sides=6, x=x, detail=True, name="bolt")


def xbolt(m, f, u, x_face, sign, r=0.02, mat="steel"):
    m.xcyl(f, u, x_face - sign * 0.003, x_face + sign * 0.011, r, mat, sides=6, detail=True, name="bolt")


def ubolt(m, x, f, u_face, r=0.02, mat="steel"):
    m.vcyl(f, u_face - 0.003, u_face + 0.01, r, mat, sides=6, x=x, detail=True, name="bolt")


def fbolts_rect(m, x0, x1, u0, u1, f_face, sign, inset=0.06, r=0.018, nx=2, nu=2):
    for i in range(nx):
        x = x0 + inset + (x1 - x0 - 2 * inset) * (i / max(1, nx - 1))
        for u in (u0 + inset, u1 - inset):
            fbolt(m, x, u, f_face, sign, r)
    for j in range(1, nu - 1):
        u = u0 + inset + (u1 - u0 - 2 * inset) * (j / (nu - 1))
        for x in (x0 + inset, x1 - inset):
            fbolt(m, x, u, f_face, sign, r)


def fvents(m, x0, x1, u0, u1, f_face, sign, count, mat="dark_steel", frame="gunmetal"):
    """Louvered grille on an f-facing face: frame plate plus horizontal slats."""
    fplate(m, x0, x1, u0, u1, f_face, sign, "polymer", depth=0.004, c=0.01)
    step = (u1 - u0) / count
    for i in range(count):
        a = u0 + i * step + step * 0.25
        fplate(m, x0 + 0.02, x1 - 0.02, a, a + step * 0.45, f_face, sign, mat, depth=0.014, c=0.0)


def xvents(m, f0, f1, u0, u1, x_face, sign, count, mat="dark_steel"):
    xplate(m, f0, f1, u0, u1, x_face, sign, "polymer", depth=0.004, c=0.01)
    step = (u1 - u0) / count
    for i in range(count):
        a = u0 + i * step + step * 0.25
        xplate(m, f0 + 0.02, f1 - 0.02, a, a + step * 0.45, x_face, sign, mat, depth=0.014, c=0.0)


def fhazard(m, x0, x1, u0, u1, f_face, sign, stripe=0.12, depth=0.008):
    """Diagonal hazard stripes on an f-facing face (baked)."""
    fplate(m, x0, x1, u0, u1, f_face, sign, "polymer", depth=depth * 0.5, c=0.0)
    h = u1 - u0
    a = x0
    while a + stripe + h <= x1 + 1e-6:
        prof = [(a, u0), (a + stripe, u0), (a + stripe + h, u1), (a + h, u1)]
        m.front_prism(prof, f_face - sign * 0.002, f_face + sign * depth, "hazard", detail=True, name="hz")
        a += stripe * 2


def uhazard(m, x0, x1, f0, f1, u_face, stripe=0.15, depth=0.006):
    """Diagonal hazard stripes on an upward face, running along x."""
    uplate(m, x0, x1, f0, f1, u_face, "polymer", depth=depth * 0.5)
    h = f1 - f0
    a = x0
    while a + stripe + h <= x1 + 1e-6:
        prof = [(a, f0), (a + stripe, f0), (a + stripe + h, f1), (a + h, f1)]
        m.top_prism(prof, u_face - 0.002, u_face + depth, "hazard", detail=True, name="hz")
        a += stripe * 2


def fseams(m, xs, u0, u1, f_face, sign, w=0.012):
    """Recessed-looking panel seams (dark thin strips) at x positions."""
    for x in xs:
        fplate(m, x - w / 2, x + w / 2, u0, u1, f_face, sign, "polymer", depth=0.004, c=0.0)


def fseams_h(m, us, x0, x1, f_face, sign, w=0.012):
    for u in us:
        fplate(m, x0, x1, u - w / 2, u + w / 2, f_face, sign, "polymer", depth=0.004, c=0.0)


# --------------------------------------------------------------- low parts

def flight(m, x0, x1, u0, u1, f_face, sign, housing="gunmetal", glow="glow_amber", depth=0.06):
    """Strip light on an f-facing face: housing block plus glowing lens (low poly)."""
    blk(m, x0 - 0.03, x1 + 0.03, f_face - sign * 0.01, f_face + sign * depth, u0 - 0.03, u1 + 0.03, housing, c=0.015, axis="f")
    blk(m, x0, x1, f_face, f_face + sign * (depth + 0.012), u0, u1, glow, c=0.0, axis="f")


def xlight(m, f0, f1, u0, u1, x_face, sign, housing="gunmetal", glow="glow_amber", depth=0.06):
    blk(m, x_face - sign * 0.01, x_face + sign * depth, f0 - 0.03, f1 + 0.03, u0 - 0.03, u1 + 0.03, housing, c=0.015, axis="x")
    blk(m, x_face, x_face + sign * (depth + 0.012), f0, f1, u0, u1, glow, c=0.0, axis="x")


def post(m, x, f, u0, u1, r, mat, sides=6):
    return m.vcyl(f, u0, u1, r, mat, sides=sides, x=x)


def rail(m, a, b, r, mat="hazard", sides=6):
    """Railing tube between two (x, f, u) points."""
    return m.limb(a, b, r, r, mat, sides=sides)


def octagon(cx, cf, rx, rf, c):
    """Top-down chamfered rectangle centered on (cx, cf), half sizes rx, rf."""
    return chamfer_rect(cx - rx, cx + rx, cf - rf, cf + rf, c)


def ring_pts(cx, cf, r, n, phase=0.5):
    return [(cx + r * math.cos(2 * math.pi * (i + phase) / n), cf + r * math.sin(2 * math.pi * (i + phase) / n)) for i in range(n)]


def uring(m, cx, cf, r_out, r_in, u0, u1, mat, n=24, detail=False):
    """Flat annulus (ring marking or ring wall) as n trapezoid segments joined into one solid."""
    import bmesh
    bm = bmesh.new()
    vs = []
    for i in range(n):
        a = 2 * math.pi * i / n
        ca, sa = math.cos(a), math.sin(a)
        vs.append([bm.verts.new((cx + ca * r, -(cf + sa * r), u)) for r, u in ((r_out, u0), (r_out, u1), (r_in, u1), (r_in, u0))])
    for i in range(n):
        j = (i + 1) % n
        for k in range(4):
            l = (k + 1) % 4
            bm.faces.new((vs[i][k], vs[j][k], vs[j][l], vs[i][l]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return m._add(bm, mat, "body", "ring", detail)


def uarc(m, cx, cf, r_out, r_in, a0, a1, u0, u1, mat, n=6, detail=False):
    """Arc segment of an annulus between angles a0..a1 (degrees), closed solid."""
    import bmesh
    bm = bmesh.new()
    vs = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        ca, sa = math.cos(a), math.sin(a)
        vs.append([bm.verts.new((cx + ca * r, -(cf + sa * r), u)) for r, u in ((r_out, u0), (r_out, u1), (r_in, u1), (r_in, u0))])
    for i in range(n):
        for k in range(4):
            l = (k + 1) % 4
            bm.faces.new((vs[i][k], vs[i + 1][k], vs[i + 1][l], vs[i][l]))
    bm.faces.new(vs[0])
    bm.faces.new(list(reversed(vs[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return m._add(bm, mat, "body", "arc", detail)


def pipe_arc(m, center, r_bend, r_pipe, a0, a1, u, mat, n=6, sides=10, caps=True):
    """Horizontal pipe elbow: torus section around center (x, f) at height u."""
    rings = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        dx, df = math.cos(a), math.sin(a)
        ring = []
        for k in range(sides):
            t = 2 * math.pi * (k + 0.5) / sides
            rr = r_bend + r_pipe * math.cos(t)
            ring.append((center[0] + dx * rr, center[1] + df * rr, u + r_pipe * math.sin(t)))
        rings.append(ring)
    return m.loft(rings, mat, caps=caps)


# ------------------------------------------------------------ wall modules
# Wall modules: 4 m wide (x -2..2), 4 m tall (u 0..4), core 0.3 m thick
# centered on f = 0, origin at base center. Corners/columns snap at x = +-2.

WALL_W = 2.0
WALL_H = 4.0
CORE = 0.15


def wall_core(m, opening=None, plinth_mat="concrete"):
    """Core slab, plinth, top cap and end posts. opening = (x0, x1, u0, u1) cut through."""
    if opening is None:
        blk(m, -WALL_W, WALL_W, -CORE, CORE, 0, WALL_H, "graphite")
        blk(m, -WALL_W, WALL_W, -0.26, 0.26, 0, 0.4, plinth_mat, c=0.07, axis="x")
    else:
        x0, x1, u0, u1 = opening
        blk(m, -WALL_W, x0, -CORE, CORE, 0, WALL_H, "graphite")
        blk(m, x1, WALL_W, -CORE, CORE, 0, WALL_H, "graphite")
        blk(m, x0, x1, -CORE, CORE, u1, WALL_H, "graphite")
        if u0 > 0.01:
            blk(m, x0, x1, -CORE, CORE, 0, u0, "graphite")
            blk(m, -WALL_W, WALL_W, -0.26, 0.26, 0, 0.4, plinth_mat, c=0.07, axis="x")
        else:
            blk(m, -WALL_W, x0, -0.26, 0.26, 0, 0.4, plinth_mat, c=0.07, axis="x")
            blk(m, x1, WALL_W, -0.26, 0.26, 0, 0.4, plinth_mat, c=0.07, axis="x")
    blk(m, -WALL_W, WALL_W, -0.25, 0.25, 3.62, WALL_H, "graphite", c=0.07, axis="x")
    for s in (-1, 1):
        blk(m, s * WALL_W, s * (WALL_W - 0.2), -0.23, 0.23, 0.4, 3.62, "graphite", c=0.05, axis="u")
        # Plinth details: hazard band on top lip, bolts on the cap.
        for x in (-1.9, -1.0, 1.0, 1.9):
            fbolt(m, x, 3.7, 0.25 * s, s, r=0.022)
            fbolt(m, x, 0.3, 0.26 * s, s, r=0.022)
        fseams_h(m, [3.86], -WALL_W, WALL_W, 0.25 * s, s)
        for x in (-WALL_W + 0.1, WALL_W - 0.1):
            fseams_h(m, [1.4, 2.6], x - 0.08, x + 0.08, 0.23 * s, s)
    # Seams that break the plinth into cast blocks.
    for s in (-1, 1):
        fseams(m, [-1.0, 0.0, 1.0], 0.02, 0.38, 0.26 * s, s)


def panel(m, x0, x1, u0, u1, s, mat, depth=0.05, c=0.06, bolts=True, seams=()):
    """Raised cladding panel on the face toward s*f, sitting on the wall core."""
    f0 = s * CORE
    blk(m, x0, x1, f0 - s * 0.01, f0 + s * depth, u0, u1, mat, c=c, axis="f")
    face = f0 + s * depth
    if bolts:
        fbolts_rect(m, x0, x1, u0, u1, face, s, inset=0.07, r=0.016, nx=2, nu=3 if (u1 - u0) > 1.5 else 2)
    for x in seams:
        fseams(m, [x], u0 + 0.03, u1 - 0.03, face, s)
    return face


# ------------------------------------------------- building-scale weathering
# The kit's bake sources are tuned for hand-held weapons (mm-scale grime).
# For structures we layer meter-scale weathering on top: crease grime, dusty
# lower edges, rust streaks running down painted panels and chipped edges.
# Patched in only for the duration of finish(), so other categories built in
# the same Blender process are unaffected.

_orig_source = kit._source_material


def _weathered_source(name):
    mat, src = _orig_source(name)
    base, metal, rough, emit, kind = kit.MATERIALS[name]
    if kind == "glow":
        return mat, src
    nt = src["nt"]
    N, M, X = kit._node, kit._math, kit._mix
    obj = N(nt, "ShaderNodeTexCoord").outputs["Object"]

    def noise(vec, scale, detail=4.0, rough_=0.55):
        n = N(nt, "ShaderNodeTexNoise")
        nt.links.new(vec, n.inputs["Vector"])
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough_
        return n.outputs["Fac"]

    def ramp(v, lo, gain):
        return M(nt, "MULTIPLY", M(nt, "SUBTRACT", v, lo), gain, clamp=True)

    sep = N(nt, "ShaderNodeSeparateXYZ")
    nt.links.new(obj, sep.inputs[0])
    low = M(nt, "SUBTRACT", 1.0, M(nt, "MULTIPLY", sep.outputs["Z"], 1.4), clamp=True)

    ao = N(nt, "ShaderNodeAmbientOcclusion", samples=8, only_local=True)
    ao.inputs["Distance"].default_value = 0.14
    crease = M(nt, "SUBTRACT", 1.0, ao.outputs["AO"], clamp=True)

    blot = M(nt, "ADD", M(nt, "MULTIPLY", noise(obj, 0.9), 0.6), M(nt, "MULTIPLY", noise(obj, 4.5, 6.0), 0.4))
    dirt = ramp(blot, 0.42, 2.4)

    stretch = N(nt, "ShaderNodeVectorMath", operation="MULTIPLY")
    nt.links.new(obj, stretch.inputs[0])
    stretch.inputs[1].default_value = (7.0, 7.0, 0.45)
    streak = M(nt, "MULTIPLY", ramp(noise(stretch.outputs[0], 1.0, 3.0), 0.5, 4.0), ramp(noise(obj, 2.2), 0.36, 3.0), clamp=True)

    bev = N(nt, "ShaderNodeBevel", samples=8)
    bev.inputs["Radius"].default_value = 0.025
    geo = N(nt, "ShaderNodeNewGeometry")
    dot = N(nt, "ShaderNodeVectorMath", operation="DOT_PRODUCT")
    nt.links.new(bev.outputs["Normal"], dot.inputs[0])
    nt.links.new(geo.outputs["Normal"], dot.inputs[1])
    edge = M(nt, "MULTIPLY", M(nt, "SUBTRACT", 1.0, kit._sock(dot.outputs, "Value")), 6.0, clamp=True)
    chips = M(nt, "MULTIPLY", M(nt, "MULTIPLY", edge, 1.6), ramp(noise(obj, 16.0, 6.0, 0.7), 0.36, 3.5), clamp=True)

    c = src["channels"]["color"]
    r = src["channels"]["roughness"]
    c = X(nt, "RGBA", M(nt, "MULTIPLY", crease, 0.75, clamp=True), c, kit._rgb("1a1714"))
    dust = kit._rgb("6e6253") if kind != "stone" else kit._rgb("4a443c")
    c = X(nt, "RGBA", M(nt, "ADD", M(nt, "MULTIPLY", dirt, 0.45), M(nt, "MULTIPLY", low, 0.5), clamp=True), c, dust)
    if kind in ("paint", "metal"):
        c = X(nt, "RGBA", M(nt, "MULTIPLY", streak, 0.85 if kind == "paint" else 0.55), c, kit._rgb("6a3a1e"))
    else:
        c = X(nt, "RGBA", M(nt, "MULTIPLY", streak, 0.3), c, kit._rgb("2a2622"))
    if kind == "paint":
        c = X(nt, "RGBA", chips, c, kit._rgb(kit.BARE_METAL))
        r = X(nt, "FLOAT", chips, r, 0.32)
    elif kind == "stone":
        c = X(nt, "RGBA", M(nt, "MULTIPLY", chips, 0.6), c, kit._rgb("b8b4ac"))
    r = M(nt, "ADD", r, M(nt, "MULTIPLY", M(nt, "ADD", dirt, streak), 0.12), clamp=True)
    src["channels"]["color"] = c
    src["channels"]["roughness"] = r
    if kind == "paint":
        src["channels"]["metallic"] = X(nt, "FLOAT", chips, src["channels"]["metallic"], 0.9)
    nt.links.new(c, src["bsdf"].inputs["Base Color"])
    nt.links.new(r, src["bsdf"].inputs["Roughness"])
    return mat, src


def finish(m, budget, texture_size=1024):
    kit._source_material = _weathered_source
    try:
        return m.finish(budget, texture_size=texture_size)
    finally:
        kit._source_material = _orig_source
