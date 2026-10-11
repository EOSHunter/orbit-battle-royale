"""Hard-surface kit for Orbit Royale models, run inside Blender.

Models are built from side profiles: a profile is a list of (f, u) points,
where f is meters forward from the asset origin (toward the muzzle or front)
and u is meters up. Profiles are extruded sideways, which gives clean
silhouettes for few triangles. Blender axes follow docs/asset-pipeline.md:
the model faces -Y, Z is up, 1 unit = 1 meter.

finish() turns the parts into a game-ready model:

1. The low-poly mesh: parts joined per group (body, magazine, ...), counted
   against the triangle budget.
2. A high-detail copy: rounded (beveled) edges plus detail-only parts such
   as screws, which cost nothing in the game because they are baked.
3. One shared UV atlas and baked textures (Cycles): base color with edge
   wear and grime, ORM (occlusion, roughness, metallic), a tangent-space
   normal map from the high-detail copy, and an emission map for glowing
   parts. Materials below are procedural sources for those bakes.
4. Export: game/assets/models/<category>/<id>.glb, the editable
   art/<category>/models/<id>.blend, and the texture PNGs in
   art/<category>/textures/.

Typical script:

    from kit import Model
    m = Model("ar-7-wayfarer")
    m.prism([(0, 0), (0.3, 0), (0.3, 0.08), (0, 0.08)], 0.06, "graphite")
    m.screw(0.1, 0.04, side=0.03)          # detail-only, baked into the normal map
    m.marker("muzzle", f=0.56, u=0.03)
    m.finish()
"""

import math
import os

import bmesh
import bpy
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Shared palette, from the concept art and the design system tokens.
# name: (base color, metallic, roughness, emission color or None, kind)
# kind: "paint" wears to bare metal at edges, "metal" brightens at edges,
# "polymer" gets a stippled grip texture, "glow" emits.
MATERIALS = {
    "graphite": ("46536b", 0.25, 0.5, None, "paint"),    # slate-navy armor panels
    "gunmetal": ("3d424b", 0.85, 0.38, None, "metal"),   # exposed metal
    "polymer": ("1d2027", 0.0, 0.72, None, "polymer"),   # grips, stocks, rubber
    "steel": ("8a8f96", 0.95, 0.3, None, "metal"),       # bright metal parts
    "ivory": ("b4b7bb", 0.1, 0.55, None, "paint"),       # light panels
    "brown": ("5a4636", 0.05, 0.65, None, "paint"),      # shotgun furniture
    "olive": ("4b5136", 0.05, 0.7, None, "paint"),       # olive armor
    "lime": ("c5f277", 0.1, 0.5, None, "paint"),         # painted markings
    "glow_amber": ("ffb45c", 0.0, 0.4, "ffb45c", "glow"),
    "glow_lime": ("c5f277", 0.0, 0.4, "c5f277", "glow"),
    "lens": ("3a2206", 0.3, 0.12, "a8611c", "glow"),     # amber glass, faint glow
    # Items: health is coral, shields are cyan.
    "coral": ("e8695c", 0.05, 0.55, None, "paint"),
    "cyan": ("4fb6e8", 0.05, 0.5, None, "paint"),
    "white_paint": ("d9dde2", 0.05, 0.5, None, "paint"),
    "glow_cyan": ("70d6ff", 0.0, 0.3, "70d6ff", "glow"),
    "glow_coral": ("ff797f", 0.0, 0.3, "ff797f", "glow"),
    "glow_teal": ("5ff2d0", 0.0, 0.4, "5ff2d0", "glow"),     # luminous plants
    "glow_white": ("fff1dc", 0.0, 0.3, "fff1dc", "glow"),    # lamps, windows
    "glass": ("22313d", 0.4, 0.06, None, "metal"),
    "black_glass": ("0d1015", 0.7, 0.04, None, "metal"),     # Glass Basin formations
    "rubber": ("15171b", 0.0, 0.88, None, "polymer"),
    "fabric": ("3b4254", 0.0, 0.92, None, "polymer"),        # suit fabric, straps
    "skin_glove": ("23262c", 0.0, 0.75, None, "polymer"),
    "concrete": ("8a8d90", 0.0, 0.88, None, "stone"),
    "basalt": ("34363b", 0.0, 0.82, None, "stone"),
    "ruin_stone": ("a39a88", 0.0, 0.86, None, "stone"),      # ancient ruins
    "sand": ("b9a78a", 0.0, 0.95, None, "stone"),
    "foliage": ("5f7d55", 0.0, 0.7, None, "stone"),
    "bark": ("4a3d33", 0.0, 0.9, None, "stone"),
    "rust_metal": ("6b4a36", 0.6, 0.7, None, "metal"),
    "hazard": ("e0a238", 0.05, 0.55, None, "paint"),         # hazard yellow-amber stripes
}

BARE_METAL = "8d9298"
TEXTURE_SIZE = 1024
_EDGE_RADIUS = 0.0028
EMISSION_STRENGTH = 3.0


def _rgb(hex_str):
    v = [int(hex_str[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    # Hex values are sRGB; Blender wants linear.
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v] + [1.0]


def material(name):
    """Flat stand-in used while modeling; replaced by bake sources in finish()."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    base, metal, rough, emit, kind = MATERIALS[name]
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = _rgb(base)
    mat["kit"] = name
    return mat


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0


def chamfer_rect(f0, f1, u0, u1, c=0.0):
    """Rectangle profile with optional 45° corners of size c."""
    c = min(c, 0.3 * abs(f1 - f0), 0.3 * abs(u1 - u0))
    if c <= 0:
        return [(f0, u0), (f1, u0), (f1, u1), (f0, u1)]
    return [(f0 + c, u0), (f1 - c, u0), (f1, u0 + c), (f1, u1 - c),
            (f1 - c, u1), (f0 + c, u1), (f0, u1 - c), (f0, u0 + c)]


class Model:
    def __init__(self, asset_id, category="weapons", kind="models", bevel=0.0018, cage=0.003):
        """bevel: edge rounding baked into the normal map (m). cage: how far detail-only
        parts may stand off the low-poly surface and still bake (m). Scale both up for
        vehicles and buildings, e.g. bevel=0.01, cage=0.02."""
        reset_scene()
        self.id = asset_id
        self.category = category
        self.kind = kind
        self.parts = {}      # group name -> low-poly objects
        self.details = {}    # group name -> detail-only objects (high copy only)
        self.markers = []
        self.bevel = bevel
        self.cage = cage

    # ------------------------------------------------------------ primitives

    def _add(self, bm, mat, group, name, detail=False):
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        obj = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(obj)
        me.materials.append(material(mat))
        (self.details if detail else self.parts).setdefault(group, []).append(obj)
        return obj

    def prism(self, profile, width, mat, x=0.0, group="body", name="part", detail=False):
        """Extrude a side profile [(f, u), ...] sideways, centered on x."""
        bm = bmesh.new()
        h = width / 2.0
        right = [bm.verts.new((x + h, -f, u)) for f, u in profile]
        left = [bm.verts.new((x - h, -f, u)) for f, u in profile]
        bm.faces.new(right)
        bm.faces.new(list(reversed(left)))
        n = len(profile)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((right[j], right[i], left[i], left[j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return self._add(bm, mat, group, name, detail)

    def box(self, f0, f1, u0, u1, width, mat, x=0.0, c=0.003, group="body", name="box", detail=False):
        """Box seen from the side, corners chamfered by c (0 for square)."""
        return self.prism(chamfer_rect(f0, f1, u0, u1, c), width, mat, x, group, name, detail)

    def side_box(self, f0, f1, u0, u1, x0, x1, mat, c=0.0, group="body", name="box", detail=False):
        """Box given by its sideways extent instead of a centered width."""
        return self.box(f0, f1, u0, u1, abs(x1 - x0), mat, (x0 + x1) / 2.0, c, group, name, detail)

    def _ring_solid(self, ring0, ring1, mat, group, name, detail):
        bm = bmesh.new()
        a = [bm.verts.new(p) for p in ring0]
        b = [bm.verts.new(p) for p in ring1]
        bm.faces.new(a)
        bm.faces.new(list(reversed(b)))
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return self._add(bm, mat, group, name, detail)

    def cyl(self, f0, f1, u, r, mat, sides=12, x=0.0, r1=None, group="body", name="cyl", detail=False):
        """Cylinder (or cone when r1 is given) running forward from f0 to f1."""
        r1 = r if r1 is None else r1
        angles = [2 * math.pi * (i + 0.5) / sides for i in range(sides)]
        ring0 = [(x + math.cos(a) * r, -f0, u + math.sin(a) * r) for a in angles]
        ring1 = [(x + math.cos(a) * r1, -f1, u + math.sin(a) * r1) for a in angles]
        return self._ring_solid(ring0, ring1, mat, group, name, detail)

    def vcyl(self, f, u0, u1, r, mat, sides=12, x=0.0, group="body", name="vcyl", detail=False):
        """Upright cylinder (scope turrets, foregrips)."""
        angles = [2 * math.pi * (i + 0.5) / sides for i in range(sides)]
        ring0 = [(x + math.cos(a) * r, -f + math.sin(a) * r, u0) for a in angles]
        ring1 = [(x + math.cos(a) * r, -f + math.sin(a) * r, u1) for a in angles]
        return self._ring_solid(ring0, ring1, mat, group, name, detail)

    def xcyl(self, f, u, x0, x1, r, mat, sides=10, group="body", name="xcyl", detail=False):
        """Cylinder running sideways (pins, knobs, screws)."""
        angles = [2 * math.pi * (i + 0.5) / sides for i in range(sides)]
        ring0 = [(x0, -(f + math.cos(a) * r), u + math.sin(a) * r) for a in angles]
        ring1 = [(x1, -(f + math.cos(a) * r), u + math.sin(a) * r) for a in angles]
        return self._ring_solid(ring0, ring1, mat, group, name, detail)

    def tube(self, f0, f1, u, r_out, r_in, mat, sides=12, x=0.0, group="body", name="tube", detail=False):
        """Open-ended tube along f (muzzles, rings), with its inside visible."""
        bm = bmesh.new()
        o0, o1, i0, i1 = [], [], [], []
        for k in range(sides):
            a = 2 * math.pi * (k + 0.5) / sides
            ca, sa = math.cos(a), math.sin(a)
            o0.append(bm.verts.new((x + ca * r_out, -f0, u + sa * r_out)))
            o1.append(bm.verts.new((x + ca * r_out, -f1, u + sa * r_out)))
            i0.append(bm.verts.new((x + ca * r_in, -f0, u + sa * r_in)))
            i1.append(bm.verts.new((x + ca * r_in, -f1, u + sa * r_in)))
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new((o0[k], o0[j], o1[j], o1[k]))
            bm.faces.new((i0[j], i0[k], i1[k], i1[j]))
            bm.faces.new((o0[j], o0[k], i0[k], i0[j]))
            bm.faces.new((o1[k], o1[j], i1[j], i1[k]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return self._add(bm, mat, group, name, detail)

    def top_prism(self, profile, u0, u1, mat, group="body", name="top", detail=False):
        """Extrude a top-down profile [(x, f), ...] upward from u0 to u1 (floors, hulls, walls)."""
        bm = bmesh.new()
        lo = [bm.verts.new((x, -f, u0)) for x, f in profile]
        hi = [bm.verts.new((x, -f, u1)) for x, f in profile]
        bm.faces.new(lo)
        bm.faces.new(list(reversed(hi)))
        n = len(profile)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return self._add(bm, mat, group, name, detail)

    def front_prism(self, profile, f0, f1, mat, group="body", name="front", detail=False):
        """Extrude a front profile [(x, u), ...] forward from f0 to f1 (cross-sections, arches)."""
        bm = bmesh.new()
        a = [bm.verts.new((x, -f0, u)) for x, u in profile]
        b = [bm.verts.new((x, -f1, u)) for x, u in profile]
        bm.faces.new(a)
        bm.faces.new(list(reversed(b)))
        n = len(profile)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return self._add(bm, mat, group, name, detail)

    def sphere(self, f, u, r, mat, x=0.0, segments=10, rings=6, scale=(1.0, 1.0, 1.0), group="body", name="sphere", detail=False):
        """Low-poly UV sphere or ellipsoid (scale is x, f, u)."""
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=r)
        for v in bm.verts:
            v.co.x = x + v.co.x * scale[0]
            v.co.y = -f + v.co.y * scale[1]
            v.co.z = u + v.co.z * scale[2]
        return self._add(bm, mat, group, name, detail)

    def limb(self, a, b, r0, r1, mat, sides=8, group="body", name="limb", detail=False, caps=True):
        """Tapered cylinder between two points given as (x, f, u)."""
        from mathutils import Vector
        p0 = Vector((a[0], -a[1], a[2]))
        p1 = Vector((b[0], -b[1], b[2]))
        axis = (p1 - p0).normalized()
        ref = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
        side = axis.cross(ref).normalized()
        up = side.cross(axis).normalized()
        bm = bmesh.new()
        r_a, r_b = [], []
        for i in range(sides):
            t = 2 * math.pi * (i + 0.5) / sides
            d = side * math.cos(t) + up * math.sin(t)
            r_a.append(bm.verts.new(p0 + d * r0))
            r_b.append(bm.verts.new(p1 + d * r1))
        if caps:
            bm.faces.new(r_a)
            bm.faces.new(list(reversed(r_b)))
        for i in range(sides):
            j = (i + 1) % sides
            bm.faces.new((r_a[i], r_a[j], r_b[j], r_b[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return self._add(bm, mat, group, name, detail)

    def loft(self, rings, mat, group="body", name="loft", detail=False, caps=True):
        """Skin a list of rings (each a list of (x, f, u) with the same count) into one closed shape.
        Good for torsos, hulls and helmets: describe cross-sections, get a smooth body."""
        bm = bmesh.new()
        vs = [[bm.verts.new((x, -f, u)) for x, f, u in ring] for ring in rings]
        n = len(rings[0])
        for k in range(len(vs) - 1):
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((vs[k][i], vs[k][j], vs[k + 1][j], vs[k + 1][i]))
        if caps:
            bm.faces.new(vs[0])
            bm.faces.new(list(reversed(vs[-1])))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return self._add(bm, mat, group, name, detail)

    def transform(self, obj, rotate=(0.0, 0.0, 0.0), pivot=(0.0, 0.0, 0.0), move=(0.0, 0.0, 0.0)):
        """Rotate a part (degrees about x, f, u axes) around a pivot (x, f, u), then move it."""
        from mathutils import Euler, Matrix, Vector
        pv = Vector((pivot[0], -pivot[1], pivot[2]))
        rot = Euler((math.radians(rotate[0]), math.radians(-rotate[1]), math.radians(rotate[2])), "XYZ").to_matrix().to_4x4()
        m = Matrix.Translation(Vector((move[0], -move[1], move[2]))) @ Matrix.Translation(pv) @ rot @ Matrix.Translation(-pv)
        obj.data.transform(m)
        return obj

    # ------------------------------------------------- detail-only helpers

    def screw(self, f, u, side, r=0.0032, mat="steel", group="body"):
        """Hex screw head on both side faces at |x| = side. Baked only."""
        for s in (-1, 1):
            x0 = s * side
            self.xcyl(f, u, x0 - s * 0.0005, x0 + s * 0.0012, r, mat, sides=6, group=group, name="screw", detail=True)

    def plate(self, f0, f1, u0, u1, side, mat, group="body", c=0.002, depth=0.0008):
        """Thin raised panel on both sides at |x| = side. Baked only."""
        for s in (-1, 1):
            self.side_box(f0, f1, u0, u1, s * (side - 0.0004), s * (side + depth), mat, c=c, group=group, name="plate", detail=True)

    def vents(self, f0, f1, u0, u1, side, count, mat="polymer", group="body"):
        """Row of raised fins on both sides at |x| = side, reading as grooves. Baked only."""
        step = (f1 - f0) / count
        for i in range(count):
            a = f0 + i * step
            self.plate(a, a + step * 0.45, u0, u1, side, mat, group, c=0.0005, depth=0.0012)

    # ------------------------------------------------------------ iron sights
    # All sights sit on x = 0. The sight line runs at height line_u parallel to
    # the bore, so aiming down sights only has to put that line on the camera axis.

    def rear_aperture(self, f, line_u, base_u, r_in=0.0058, r_out=0.0082, mat="polymer", group="body"):
        """Thin ghost ring centered on the sight line, on a narrow base."""
        self.tube(f, f + 0.006, line_u, r_out, r_in, mat, sides=10, group=group)
        self.box(f - 0.004, f + 0.01, base_u, line_u - r_out + 0.0015, 0.012, mat, c=0.002, group=group)
        self.marker("sight", f=f, u=line_u)

    def rear_notch(self, f, line_u, base_u, gap=0.0065, ear=0.0045, notch=0.006, mat="polymer", length=0.014, group="body"):
        """Square notch: two thin ears whose tops are level with the front post tip."""
        self.box(f, f + length, base_u, line_u - notch, gap + 2 * ear, mat, c=0.002, group=group)
        for s in (-1, 1):
            self.side_box(f, f + length, line_u - notch - 0.001, line_u, s * gap / 2, s * (gap / 2 + ear), mat, c=0.0, group=group)
        self.marker("sight", f=f, u=line_u)

    def front_post(self, f, line_u, base_u, mat="polymer", post=0.0024, bead=None, ears=True, group="body"):
        """Thin front post whose tip is the aim point, with optional guard ears and glow bead."""
        self.box(f - 0.004, f + 0.016, base_u, base_u + 0.006, 0.013, mat, c=0.002, group=group)
        tip = line_u - (0.0025 if bead else 0.0)
        self.box(f + 0.004, f + 0.009, base_u, tip, post, mat, c=0.0, group=group)
        if bead:
            self.box(f + 0.004, f + 0.009, tip, line_u, post + 0.0004, bead, c=0.0, group=group)
        if ears:
            for s in (-1, 1):
                self.side_box(f, f + 0.012, base_u, line_u + 0.004, s * 0.0068, s * 0.0092, mat, c=0.0, group=group)

    def mirror_x(self, obj):
        me = obj.data.copy()
        for v in me.vertices:
            v.co.x = -v.co.x
        me.flip_normals()
        copy = bpy.data.objects.new(obj.name + "-m", me)
        bpy.context.scene.collection.objects.link(copy)
        for store in (self.parts, self.details):
            for objs in store.values():
                if obj in objs:
                    objs.append(copy)
                    return copy
        return copy

    def marker(self, name, f, u, x=0.0):
        """Named empty exported as a node (muzzle, grip) for the game to find."""
        e = bpy.data.objects.new(name, None)
        e.empty_display_size = 0.03
        e.location = (x, -f, u)
        bpy.context.scene.collection.objects.link(e)
        self.markers.append(e)
        return e

    # --------------------------------------------------------------- output

    def finish(self, budget=(500, 1500), texture_size=TEXTURE_SIZE, before_export=None):
        """before_export(lows) runs after baking, before export: e.g. add an armature and skin."""
        global _EDGE_RADIUS
        _EDGE_RADIUS = max(0.0028, self.bevel * 1.5)
        lows, highs = [], []
        for group, objs in self.parts.items():
            name = self.id if group == "body" else f"{self.id}-{group}"
            low = _join(objs, name)
            _shade(low)
            high = _high_copy(low, self.details.get(group, []), name + "-high", self.bevel)
            lows.append(low)
            highs.append(high)
        tris = sum(_tri_count(o) for o in lows)

        _unwrap(lows)
        tex_dir = os.path.join(REPO, "art", self.category, "textures")
        images = _bake(self.id, lows, highs, texture_size, tex_dir, self.cage)
        final = _final_material(self.id, images)
        for low in lows:
            for p in low.data.polygons:
                p.material_index = 0
            low.data.materials.clear()
            low.data.materials.append(final)
        for high in highs:
            bpy.data.objects.remove(high, do_unlink=True)
        for mat in list(bpy.data.materials):
            if mat.users == 0:
                bpy.data.materials.remove(mat)

        if before_export:
            before_export(lows)
        out_dir = os.path.join(REPO, "game", "assets", self.kind, self.category)
        src_dir = os.path.join(REPO, "art", self.category, "models")
        os.makedirs(out_dir, exist_ok=True)
        os.makedirs(src_dir, exist_ok=True)
        glb = os.path.join(out_dir, self.id + ".glb")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.export_scene.gltf(
            filepath=glb, export_format="GLB", use_selection=False,
            export_apply=True, export_yup=True, export_materials="EXPORT",
            export_tangents=True, export_image_format="JPEG", export_jpeg_quality=92,
        )
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(src_dir, self.id + ".blend"), compress=True)
        lo, hi = budget
        status = "OK" if lo <= tris <= hi else ("UNDER" if tris < lo else "OVER")
        print(f"MODEL {self.id}: {tris} triangles (budget {lo}-{hi}) {status}, {os.path.getsize(glb) // 1024} KB")
        return tris


# ----------------------------------------------------------------- helpers


def _tri_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def _select(objs, active=None):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]


def _join(objs, name):
    _select(objs)
    if len(objs) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    obj.data.name = name
    return obj


def _shade(obj):
    """Smooth with hard edges above 35°: crisp panels, round cylinders."""
    me = obj.data
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(35))


def _high_copy(low, details, name, width=0.0018):
    """Rounded-edge copy of the low mesh plus detail-only parts, for baking."""
    high = low.copy()
    high.data = low.data.copy()
    high.name = name
    bpy.context.scene.collection.objects.link(high)
    if details:
        high = _join([high] + [d for d in details], name)
    bevel = high.modifiers.new("round", "BEVEL")
    bevel.width = width
    bevel.segments = 3
    bevel.limit_method = "ANGLE"
    bevel.angle_limit = math.radians(30)
    bevel.harden_normals = True
    bevel.use_clamp_overlap = True
    _select([high])
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    high.data.shade_smooth()
    high.hide_render = False
    return high


def _unwrap(lows):
    _select(lows)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(rotate=True, margin=0.006)
    bpy.ops.object.mode_set(mode="OBJECT")


# ------------------------------------------------------------ bake sources


def _node(nt, kind, loc=(0, 0), **props):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in props.items():
        setattr(n, k, v)
    return n


def _sock(sockets, name):
    return next(s for s in sockets if s.name == name and s.enabled)


def _mix(nt, data_type, fac, a, b, blend="MIX"):
    m = _node(nt, "ShaderNodeMix", data_type=data_type, blend_type=blend)
    nt.links.new(fac, _sock(m.inputs, "Factor"))
    for name, v in (("A", a), ("B", b)):
        s = _sock(m.inputs, name)
        if isinstance(v, bpy.types.NodeSocket):
            nt.links.new(v, s)
        else:
            s.default_value = v
    return _sock(m.outputs, "Result")


def _math(nt, op, a, b=None, clamp=False):
    m = _node(nt, "ShaderNodeMath", operation=op, use_clamp=clamp)
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, bpy.types.NodeSocket):
            nt.links.new(v, m.inputs[i])
        else:
            m.inputs[i].default_value = v
    return m.outputs[0]


def _source_material(name):
    """Procedural material whose channels are baked: returns (material, channel sockets)."""
    base, metal, rough, emit, kind = MATERIALS[name]
    mat = bpy.data.materials.new("src-" + name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = _node(nt, "ShaderNodeOutputMaterial", (1200, 0))
    bsdf = _node(nt, "ShaderNodeBsdfPrincipled", (900, 0))

    # Edge mask: where a rounded-normal lookup disagrees with the true normal.
    geo = _node(nt, "ShaderNodeNewGeometry")
    bevel = _node(nt, "ShaderNodeBevel", samples=8)
    bevel.inputs["Radius"].default_value = _EDGE_RADIUS
    dot = _node(nt, "ShaderNodeVectorMath", operation="DOT_PRODUCT")
    nt.links.new(bevel.outputs["Normal"], dot.inputs[0])
    nt.links.new(geo.outputs["Normal"], dot.inputs[1])
    edge_raw = _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", 1.0, _sock(dot.outputs, "Value")), 9.0, clamp=True)
    breakup = _node(nt, "ShaderNodeTexNoise")
    breakup.inputs["Scale"].default_value = 140.0
    breakup.inputs["Detail"].default_value = 6.0
    edge = _math(nt, "MULTIPLY", edge_raw, _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", breakup.outputs["Fac"], 0.25), 2.4, clamp=True), clamp=True)

    # Grime in creases, and large-scale tone variation.
    ao = _node(nt, "ShaderNodeAmbientOcclusion", samples=8)
    ao.inputs["Distance"].default_value = 0.015
    grime = _math(nt, "SUBTRACT", 1.0, ao.outputs["AO"])
    tone = _node(nt, "ShaderNodeTexNoise")
    tone.inputs["Scale"].default_value = 25.0
    tone.inputs["Detail"].default_value = 3.0
    fine = _node(nt, "ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 600.0 if kind == "polymer" else 260.0
    fine.inputs["Detail"].default_value = 2.0

    color = _rgb(base)
    darker = [c * 0.78 for c in color[:3]] + [1.0]
    c = _mix(nt, "RGBA", _math(nt, "MULTIPLY", tone.outputs["Fac"], 0.7), color, darker)
    r = rough
    m = metal
    rough_s = _math(nt, "ADD", r - 0.06, _math(nt, "MULTIPLY", tone.outputs["Fac"], 0.12))
    metal_s = _math(nt, "ADD", m, 0.0)
    if kind == "paint":
        c = _mix(nt, "RGBA", edge, c, _rgb(BARE_METAL))
        metal_s = _mix(nt, "FLOAT", edge, m, 0.9)
        rough_s = _mix(nt, "FLOAT", edge, rough_s, 0.3)
    elif kind == "metal":
        c = _mix(nt, "RGBA", _math(nt, "MULTIPLY", edge, 0.7), c, _rgb(BARE_METAL))
        rough_s = _mix(nt, "FLOAT", edge, rough_s, 0.22)
    elif kind == "polymer":
        lighter = [min(1.0, x * 1.6 + 0.01) for x in color[:3]] + [1.0]
        c = _mix(nt, "RGBA", _math(nt, "MULTIPLY", edge, 0.6), c, lighter)
        rough_s = _mix(nt, "FLOAT", edge, rough_s, 0.5)
    elif kind == "stone":
        # Chipped, lighter edges and a coarse mottled surface; never metallic.
        lighter = [min(1.0, x * 1.35 + 0.02) for x in color[:3]] + [1.0]
        c = _mix(nt, "RGBA", _math(nt, "MULTIPLY", edge, 0.8), c, lighter)
        mottle = _node(nt, "ShaderNodeTexNoise")
        mottle.inputs["Scale"].default_value = 9.0
        mottle.inputs["Detail"].default_value = 8.0
        c = _mix(nt, "RGBA", _math(nt, "MULTIPLY", mottle.outputs["Fac"], 0.5), c, darker)
        fine.inputs["Scale"].default_value = 45.0
    grime_col = [0.02, 0.018, 0.015, 1.0]
    if kind != "glow":
        c = _mix(nt, "RGBA", _math(nt, "MULTIPLY", grime, 0.8, clamp=True), c, grime_col)

    # Surface relief: grip stipple on polymer, faint tooling elsewhere.
    bump = _node(nt, "ShaderNodeBump")
    bump.inputs["Strength"].default_value = {"polymer": 0.35, "stone": 0.5}.get(kind, 0.06)
    bump.inputs["Distance"].default_value = 0.004 if kind == "stone" else 0.0004
    nt.links.new(fine.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    nt.links.new(c, bsdf.inputs["Base Color"])
    nt.links.new(rough_s, bsdf.inputs["Roughness"])
    nt.links.new(metal_s, bsdf.inputs["Metallic"])
    emit_rgb = _rgb(emit) if emit else [0, 0, 0, 1]
    bsdf.inputs["Emission Color"].default_value = emit_rgb
    nt.links.new(bsdf.outputs[0], out.inputs["Surface"])

    emission = _node(nt, "ShaderNodeEmission", (900, -300))
    channels = {
        "color": c,
        "roughness": rough_s,
        "metallic": metal_s,
        "emission": emit_rgb,
    }
    return mat, {"nt": nt, "out": out, "bsdf": bsdf, "emission": emission, "channels": channels}


def _route(src, channel):
    """Point the material output at one channel (emission shader) or at the BSDF."""
    nt, out, emission = src["nt"], src["out"], src["emission"]
    if channel == "bsdf":
        nt.links.new(src["bsdf"].outputs[0], out.inputs["Surface"])
        return
    v = src["channels"][channel]
    for link in list(emission.inputs["Color"].links):
        nt.links.remove(link)
    if isinstance(v, bpy.types.NodeSocket):
        nt.links.new(v, emission.inputs["Color"])
    else:
        emission.inputs["Color"].default_value = v
    emission.inputs["Strength"].default_value = 1.0
    nt.links.new(emission.outputs[0], out.inputs["Surface"])


def _bake(asset_id, lows, highs, size, tex_dir, cage=0.003):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.render.bake.margin = 8
    world = bpy.data.worlds.new("bake")
    scene.world = world
    world.light_settings.distance = 0.02

    # Swap the high copies onto procedural sources.
    sources = {}
    for high in highs:
        for i, slot in enumerate(high.material_slots):
            key = slot.material.get("kit") if slot.material else "polymer"
            if key not in sources:
                sources[key] = _source_material(key)
            high.material_slots[i].material = sources[key][0]

    # Bake target node on every low object.
    target = bpy.data.materials.new("bake-target")
    target.use_nodes = True
    tnode = target.node_tree.nodes.new("ShaderNodeTexImage")
    target.node_tree.nodes.active = tnode
    for low in lows:
        for p in low.data.polygons:
            p.material_index = 0
        low.data.materials.clear()
        low.data.materials.append(target)

    def new_image(label, data):
        img = bpy.data.images.new(f"{asset_id}_{label}", size, size, alpha=False)
        img.colorspace_settings.name = "Non-Color" if data else "sRGB"
        if label == "normal":
            img.generated_color = (0.5, 0.5, 1.0, 1.0)
        return img

    def bake(img, bake_type, channel=None, **kw):
        tnode.image = img
        for _mat, src in sources.values():
            _route(src, channel or "bsdf")
        for low, high in zip(lows, highs):
            _select([high, low], active=low)
            bpy.ops.object.bake(type=bake_type, use_selected_to_active=True, cage_extrusion=cage,
                                max_ray_distance=cage * 2.7, use_clear=False, margin=8, **kw)

    images = {}
    for label, channel, data in (("basecolor", "color", False), ("roughness", "roughness", True),
                                 ("metallic", "metallic", True), ("emission", "emission", False)):
        img = new_image(label, data)
        bake(img, "EMIT", channel)
        images[label] = img
    scene.cycles.samples = 32
    images["normal"] = new_image("normal", True)
    bake(images["normal"], "NORMAL", normal_space="TANGENT")
    images["ao"] = new_image("ao", True)
    bake(images["ao"], "AO")

    # Pack occlusion, roughness, metallic into one ORM texture (glTF layout).
    def channel(img):
        a = np.empty(size * size * 4, dtype=np.float32)
        img.pixels.foreach_get(a)
        return a.reshape(-1, 4)[:, 0]
    orm = new_image("orm", True)
    px = np.ones((size * size, 4), dtype=np.float32)
    px[:, 0] = 0.35 + 0.65 * channel(images["ao"])
    px[:, 1] = np.clip(channel(images["roughness"]), 0.05, 1.0)
    px[:, 2] = np.clip(channel(images["metallic"]), 0.0, 1.0)
    orm.pixels.foreach_set(px.ravel())

    os.makedirs(tex_dir, exist_ok=True)
    final = {}
    for label in ("basecolor", "orm", "normal", "emission"):
        img = images.get(label) or orm
        path = os.path.join(tex_dir, f"{asset_id}_{label}.png")
        img.filepath_raw = path
        img.file_format = "PNG"
        img.save()
        final[label] = img
    for label in ("roughness", "metallic", "ao"):
        bpy.data.images.remove(images[label])
    bpy.data.materials.remove(target)
    return final


def _final_material(asset_id, images):
    mat = bpy.data.materials.new(asset_id)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")

    def tex(label, loc):
        n = _node(nt, "ShaderNodeTexImage", loc)
        n.image = images[label]
        return n

    color = tex("basecolor", (-600, 300))
    nt.links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
    orm = tex("orm", (-600, 0))
    sep = _node(nt, "ShaderNodeSeparateColor", (-300, 0))
    nt.links.new(orm.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
    normal = tex("normal", (-600, -300))
    nmap = _node(nt, "ShaderNodeNormalMap", (-300, -300))
    nt.links.new(normal.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    emission = tex("emission", (-600, -600))
    nt.links.new(emission.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = EMISSION_STRENGTH

    # glTF reads occlusion from a group node named "glTF Material Output".
    group = bpy.data.node_groups.get("glTF Material Output")
    if group is None:
        group = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
        group.interface.new_socket("Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
    gnode = _node(nt, "ShaderNodeGroup", (0, -500))
    gnode.node_tree = group
    nt.links.new(sep.outputs["Red"], gnode.inputs["Occlusion"])
    return mat
