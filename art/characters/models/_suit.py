"""Shared builder for the expedition-suit operator: player, bots and first-person arms.

Concepts: codex/concepts/v0.2/01-operator.png, 02-operator-bot-variants.png,
03-first-person-arms.png. 1.8 m tall, built in a T-pose facing forward (-Y in
Blender), origin between the feet. The operator's right side is -X.

build_operator(m, lod, palette) adds the mesh parts to a kit Model.
rig(lows, with_animations) runs as finish()'s before_export hook: it adds a
humanoid skeleton named after Godot's SkeletonProfileHumanoid (Hips, Spine,
Chest, ... LeftUpperArm, ...), skins every vertex to its two nearest bones and
adds simple keyframed cycles: idle, walk, run, crouch, jump, fall (rifle-ready
arms in all of them). Loop clips end in "-loop" so Godot loops them on import.
"""

import math

import bpy
import kit
from mathutils import Matrix, Vector

# Palettes map role -> (color, metallic, roughness, emission, kind).
PALETTES = {
    "navy": {"armor": "46536b", "armor_light": "b9bcc0", "suit": "2a3040", "accent": "c5f277", "gear": "2a2c27"},
    "rust": {"armor": "9a4a33", "armor_light": "c9b9a6", "suit": "26272b", "accent": "e0a238", "gear": "3a2f27"},
    "tan": {"armor": "b49f7d", "armor_light": "d8ccb5", "suit": "2b2a28", "accent": "6b5a3f", "gear": "4a3f30"},
    "olive": {"armor": "5b6640", "armor_light": "a8a888", "suit": "26282a", "accent": "c5f277", "gear": "3d3f2c"},
    "white": {"armor": "d5d8db", "armor_light": "eef0f2", "suit": "25272c", "accent": "70d6ff", "gear": "3a3e44"},
    "black": {"armor": "2b2d31", "armor_light": "4a4d52", "suit": "1d1e21", "accent": "c5f277", "gear": "26272a"},
}


def use_palette(name):
    p = PALETTES[name]
    kit.MATERIALS.update({
        "armor": (p["armor"], 0.25, 0.5, None, "paint"),
        "armor_light": (p["armor_light"], 0.1, 0.55, None, "paint"),
        "suit": (p["suit"], 0.0, 0.9, None, "polymer"),
        "accent": (p["accent"], 0.1, 0.5, None, "paint"),
        "gear": (p["gear"], 0.0, 0.8, None, "polymer"),
        "visor": ("b8801e", 0.85, 0.1, "6b4208", "glow"),
    })


# Skeleton in the T-pose: name -> (head (x, f, u), tail, parent).
R, L = -1.0, 1.0
SHOULDER_U = 1.44


def _bones():
    b = {
        "Hips": ((0, 0, 0.95), (0, 0, 1.05), None),
        "Spine": ((0, 0, 1.05), (0, 0, 1.2), "Hips"),
        "Chest": ((0, 0, 1.2), (0, 0, 1.34), "Spine"),
        "UpperChest": ((0, 0, 1.34), (0, 0, 1.48), "Chest"),
        "Neck": ((0, 0, 1.48), (0, 0, 1.57), "UpperChest"),
        "Head": ((0, 0, 1.57), (0, 0, 1.8), "Neck"),
    }
    for side, s in (("Left", L), ("Right", R)):
        b[side + "Shoulder"] = ((s * 0.04, 0, 1.43), (s * 0.19, 0, SHOULDER_U), "UpperChest")
        b[side + "UpperArm"] = ((s * 0.19, 0, SHOULDER_U), (s * 0.47, 0, SHOULDER_U), side + "Shoulder")
        b[side + "LowerArm"] = ((s * 0.47, 0, SHOULDER_U), (s * 0.74, 0, SHOULDER_U), side + "UpperArm")
        b[side + "Hand"] = ((s * 0.74, 0, SHOULDER_U), (s * 0.92, 0, SHOULDER_U), side + "LowerArm")
        b[side + "UpperLeg"] = ((s * 0.1, 0, 0.93), (s * 0.105, 0.01, 0.5), "Hips")
        b[side + "LowerLeg"] = ((s * 0.105, 0.01, 0.5), (s * 0.11, 0, 0.09), side + "UpperLeg")
        b[side + "Foot"] = ((s * 0.11, 0, 0.09), (s * 0.11, 0.12, 0.03), side + "LowerLeg")
        b[side + "Toes"] = ((s * 0.11, 0.12, 0.03), (s * 0.11, 0.19, 0.03), side + "Foot")
    return b


def _ring(cx, cf, u, a, b, n, phase=0.0):
    return [(cx + a * math.cos(2 * math.pi * (i + phase) / n), cf + b * math.sin(2 * math.pi * (i + phase) / n), u) for i in range(n)]


# ---------------------------------------------------------------------- mesh


def build_operator(m, lod="player", arms_only=False):
    """lod: "player" (5k-15k tris), "bot" (1k-3k), "arms" (first-person arms only)."""
    hi = lod != "bot"
    n_limb = 16 if hi else 7
    n_torso = 18 if hi else 8

    if not arms_only:
        _torso(m, n_torso, hi)
        _legs(m, n_limb, hi)
        _helmet(m, hi)
    _arms(m, n_limb, hi, arms_only)


def _torso(m, n, hi):
    rings = [
        _ring(0, 0.0, 0.86, 0.15, 0.1, n), _ring(0, 0.0, 0.95, 0.17, 0.115, n), _ring(0, 0.0, 1.06, 0.155, 0.105, n),
        _ring(0, 0.005, 1.2, 0.175, 0.115, n), _ring(0, 0.01, 1.33, 0.2, 0.125, n), _ring(0, 0.0, 1.44, 0.185, 0.11, n),
        _ring(0, 0.0, 1.5, 0.08, 0.075, n), _ring(0, 0.005, 1.6, 0.06, 0.06, n),
    ]
    m.loft(rings, "suit")
    # Collar ring.
    m.loft([_ring(0, 0.0, 1.47, 0.11, 0.095, n), _ring(0, 0.005, 1.55, 0.085, 0.08, n)], "suit")

    # Chest plate front and back, ivory upper panel, amber status light.
    chest = [(-0.17, 1.17), (0.17, 1.17), (0.205, 1.28), (0.17, 1.43), (0.07, 1.46), (-0.07, 1.46), (-0.17, 1.43), (-0.205, 1.28)]
    m.front_prism(chest, 0.105, 0.15, "armor")
    m.front_prism([(x * 0.95, u) for x, u in chest], -0.14, -0.1, "armor")
    m.front_prism([(-0.15, 1.34), (0.15, 1.34), (0.13, 1.42), (0.06, 1.445), (-0.06, 1.445), (-0.13, 1.42)], 0.148, 0.158, "armor_light")
    m.box(0.15, 0.162, 1.36, 1.375, 0.06, "glow_amber", c=0.0)
    # Chest rig: three magazine pouches and a center radio pouch.
    for x in (-0.11, 0.0, 0.11):
        m.box(0.15, 0.2, 1.17, 1.29, 0.085, "gear", x=x, c=0.012)
        m.box(0.16, 0.205, 1.27, 1.3, 0.09, "gear", x=x, c=0.008)
        if hi:
            m.plate(0.155, 0.195, 1.19, 1.25, 0.0425, "gear", c=0.004)
    if hi:
        for x in (-0.14, 0.14):
            m.plate(0.12, 0.148, 1.2, 1.4, abs(x) + 0.03, "accent")
        m.plate(-0.13, -0.11, 1.2, 1.4, 0.18, "armor_light")
    # Shoulder straps over the top.
    for s in (L, R):
        m.limb((s * 0.11, 0.15, 1.4), (s * 0.13, 0.0, 1.5), 0.022, 0.022, "gear", sides=4)
        m.limb((s * 0.13, 0.0, 1.5), (s * 0.11, -0.13, 1.4), 0.022, 0.022, "gear", sides=4)

    # Belt with buckle and pouches.
    m.loft([_ring(0, 0.0, 0.98, 0.178, 0.122, n), _ring(0, 0.0, 1.05, 0.172, 0.118, n)], "gear")
    m.box(0.115, 0.135, 0.985, 1.045, 0.08, "steel", c=0.006)
    for x, f in ((0.15, 0.05), (-0.15, 0.05), (0.16, -0.06), (-0.16, -0.06)):
        m.box(f - 0.04, f + 0.04, 0.9, 1.04, 0.05, "gear", x=x + (0.02 if x > 0 else -0.02), c=0.01)
    # Groin and hip armor.
    m.front_prism([(-0.12, 0.86), (0.12, 0.86), (0.14, 0.97), (-0.14, 0.97)], 0.09, 0.12, "armor_light")
    m.front_prism([(-0.08, 0.78), (0.08, 0.78), (0.11, 0.86), (-0.11, 0.86)], 0.07, 0.1, "suit")

    # Backpack with a lime panel and an amber canister on the hip.
    m.box(-0.29, -0.13, 1.06, 1.44, 0.3, "gear", c=0.03)
    m.box(-0.3, -0.24, 1.3, 1.46, 0.26, "armor", c=0.02)
    m.box(-0.295, -0.285, 1.16, 1.28, 0.08, "accent", c=0.0)
    m.box(-0.27, -0.13, 1.08, 1.18, 0.34, "gear", c=0.02)
    m.vcyl(-0.08, 0.98, 1.14, 0.032, "glow_amber", sides=8 if hi else 6, x=0.21)
    m.vcyl(-0.08, 0.97, 0.99, 0.036, "steel", sides=8 if hi else 6, x=0.21)
    m.vcyl(-0.08, 1.13, 1.15, 0.036, "steel", sides=8 if hi else 6, x=0.21)
    if hi:
        m.vents(-0.28, -0.14, 1.2, 1.28, 0.15, 6, "gear")
        for f, u in ((-0.29, 1.42), (-0.29, 1.08)):
            m.screw(f, u, 0.15, r=0.006)


def _legs(m, n, hi):
    for s in (L, R):
        x = s * 0.1
        m.limb((x, 0.0, 0.95), (s * 0.105, 0.01, 0.5), 0.09, 0.062, "suit", sides=n)
        m.limb((s * 0.105, 0.01, 0.5), (s * 0.11, 0.0, 0.1), 0.06, 0.046, "suit", sides=n)
        m.sphere(0.012, 0.5, 0.063, "suit", x=s * 0.105, segments=n, rings=6 if hi else 4)
        # Thigh plate with lime stripe, side thigh pouch on the right.
        m.box(0.06, 0.1, 0.62, 0.86, 0.13, "armor", x=x, c=0.02)
        if hi:
            m.plate(0.07, 0.095, 0.66, 0.84, abs(x) + 0.066, "accent", c=0.003)
        # Knee pad and shin guard.
        m.box(0.045, 0.11, 0.43, 0.58, 0.115, "armor", x=s * 0.105, c=0.025)
        m.box(0.03, 0.075, 0.15, 0.42, 0.1, "armor", x=s * 0.108, c=0.015)
        m.box(0.05, 0.077, 0.2, 0.38, 0.04, "armor_light", x=s * 0.108, c=0.008)
        # Boot: upper, toe cap, sole, ankle cuff.
        m.box(-0.08, 0.13, 0.025, 0.14, 0.125, "gear", x=s * 0.11, c=0.03)
        m.box(0.08, 0.19, 0.025, 0.09, 0.115, "gear", x=s * 0.11, c=0.025)
        m.box(-0.085, 0.195, 0.0, 0.03, 0.13, "rubber", x=s * 0.11, c=0.01)
        m.limb((s * 0.11, 0.0, 0.1), (s * 0.11, 0.0, 0.2), 0.058, 0.055, "gear", sides=max(6, n // 2))
        if hi:
            m.vents(-0.08, 0.19, 0.003, 0.027, abs(s * 0.11) + 0.065, 10, "rubber")
            m.plate(0.0, 0.08, 0.06, 0.12, abs(s * 0.11) + 0.0625, "armor", c=0.006)
    # Thigh pouch (right) and holster strap.
    m.box(-0.05, 0.05, 0.7, 0.86, 0.06, "gear", x=R * 0.2, c=0.012)


def _helmet(m, hi):
    seg, rings = (24, 16) if hi else (10, 7)
    m.sphere(0.005, 1.69, 0.135, "armor", segments=seg, rings=rings, scale=(1.0, 1.12, 1.06))
    m.sphere(0.075, 1.69, 0.112, "visor", segments=seg, rings=rings, scale=(1.08, 0.9, 0.6))
    # Ear pods with amber rings, chin guard, crest, lime stripe.
    for s in (L, R):
        m.xcyl(0.0, 1.68, s * 0.12, s * 0.152, 0.046, "armor", sides=12 if hi else 6)
        m.xcyl(0.0, 1.68, s * 0.15, s * 0.156, 0.03, "glow_amber", sides=12 if hi else 6)
    m.box(0.07, 0.15, 1.55, 1.62, 0.11, "gear", c=0.02)
    m.box(-0.08, 0.07, 1.8, 1.83, 0.05, "armor_light", c=0.01)
    if hi:
        m.vents(0.08, 0.14, 1.565, 1.6, 0.055, 4, "gear")
        m.plate(-0.06, 0.06, 1.78, 1.81, 0.03, "accent", c=0.005)


def _arms(m, n, hi, arms_only):
    for s in (L, R):
        sh = (s * 0.19, 0.0, SHOULDER_U)
        el = (s * 0.47, 0.0, SHOULDER_U)
        wr = (s * 0.74, 0.0, SHOULDER_U)
        if arms_only:
            m.limb((s * 0.3, 0.0, SHOULDER_U), el, 0.052, 0.046, "suit", sides=n)
        else:
            m.limb(sh, el, 0.06, 0.047, "suit", sides=n)
            # Shoulder pad with lime edge, upper-arm plate.
            pad = m.sphere(0.0, 1.47, 0.095, "armor", x=s * 0.24, segments=12 if hi else 6, rings=6 if hi else 4, scale=(1.15, 1.0, 0.62))
            m.transform(pad, rotate=(0, s * -18, 0), pivot=(s * 0.24, 0, 1.47))
            m.limb((s * 0.29, 0.0, SHOULDER_U), (s * 0.4, 0.0, SHOULDER_U), 0.066, 0.06, "armor", sides=8 if hi else 5)
        m.sphere(0.0, SHOULDER_U, 0.049, "suit", x=s * 0.47, segments=n, rings=6 if hi else 4)
        m.limb(el, wr, 0.047, 0.039, "suit", sides=n)
        # Forearm guard with the amber wrist display (03-first-person-arms.png).
        m.limb((s * 0.53, 0.0, SHOULDER_U), (s * 0.71, 0.0, SHOULDER_U), 0.054, 0.05, "armor", sides=8 if hi else 5)
        m.box(-0.025, 0.025, SHOULDER_U + 0.045, SHOULDER_U + 0.062, 0.05, "gunmetal", x=s * 0.68, c=0.006)
        m.box(-0.017, 0.017, SHOULDER_U + 0.06, SHOULDER_U + 0.066, 0.036, "glow_amber", x=s * 0.68, c=0.0)
        m.limb((s * 0.705, 0.0, SHOULDER_U), (s * 0.74, 0.0, SHOULDER_U), 0.052, 0.052, "gear", sides=8 if hi else 5)
        if hi:
            for xx in (0.56, 0.62):
                m.side_box(-0.02, 0.02, SHOULDER_U + 0.05, SHOULDER_U + 0.056, s * xx, s * (xx + 0.03), "accent", detail=True)
        _glove(m, s, hi)


def _glove(m, s, hi):
    u = SHOULDER_U
    # Back of the hand (armored) and palm, palm facing down in the T-pose.
    m.box(-0.045, 0.045, u - 0.022, u + 0.022, 0.1, "skin_glove", x=s * 0.8, c=0.008)
    m.box(-0.04, 0.04, u + 0.018, u + 0.03, 0.08, "armor", x=s * 0.8, c=0.006)
    # Four fingers, two segments each on the player model.
    for i in range(4):
        f = -0.033 + i * 0.022
        if hi:
            m.limb((s * 0.85, f, u), (s * 0.895, f, u - 0.004), 0.0105, 0.0095, "skin_glove", sides=6)
            m.limb((s * 0.895, f, u - 0.004), (s * 0.93, f, u - 0.012), 0.0095, 0.008, "skin_glove", sides=6)
            m.side_box(f - 0.009, f + 0.009, u + 0.006, u + 0.013, s * 0.855, s * 0.885, "armor", detail=False)
        else:
            m.limb((s * 0.85, f, u), (s * 0.925, f, u - 0.01), 0.011, 0.009, "skin_glove", sides=4)
    # Thumb, angled forward.
    m.limb((s * 0.77, 0.045, u - 0.01), (s * 0.81, 0.085, u - 0.016), 0.013, 0.011, "skin_glove", sides=6 if hi else 4)
    m.limb((s * 0.81, 0.085, u - 0.016), (s * 0.835, 0.108, u - 0.02), 0.011, 0.009, "skin_glove", sides=6 if hi else 4)


# ----------------------------------------------------------------- rigging


def rig(lows, with_animations=True, only=None):
    """Add the skeleton, skin every mesh, and keyframe the basic cycles.
    only: restrict to a set of bone names (first-person arms)."""
    bones = _bones()
    if only:
        bones = {k: v for k, v in bones.items() if k in only}
    arm_data = bpy.data.armatures.new("Skeleton")
    arm = bpy.data.objects.new("Armature", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = {}
    for name, (h, t, parent) in bones.items():
        b = arm_data.edit_bones.new(name)
        b.head = Vector((h[0], -h[1], h[2]))
        b.tail = Vector((t[0], -t[1], t[2]))
        b.roll = 0.0
        eb[name] = b
    for name, (h, t, parent) in bones.items():
        if parent and parent in eb:
            eb[name].parent = eb[parent]
            eb[name].use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")

    segs = {name: (Vector((h[0], -h[1], h[2])), Vector((t[0], -t[1], t[2]))) for name, (h, t, _) in bones.items()}
    for low in lows:
        _skin(low, arm, segs)
    if with_animations:
        _animate(arm)
    return arm


def _seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (a + ab * t - p).length


def _skin(obj, arm, segs):
    groups = {name: obj.vertex_groups.new(name=name) for name in segs}
    for v in obj.data.vertices:
        p = obj.matrix_world @ v.co
        d = sorted((_seg_dist(p, a, b), name) for name, (a, b) in segs.items())
        if "Hips" in segs and 0.76 < p.z < 1.0 and abs(p.x) < 0.14 and -p.y > 0.06:
            d = [(0.0, "Hips"), (1.0, "Spine")]  # groin armor rides the pelvis, not the thighs
        (d1, n1), (d2, n2) = d[0], d[1]
        # Blend across a joint only when the second bone is nearly as close.
        w1 = 1.0 / (d1 + 0.01) ** 4
        w2 = 1.0 / (d2 + 0.01) ** 4 if d2 < d1 * 1.6 + 0.02 else 0.0
        total = w1 + w2
        groups[n1].add([v.index], w1 / total, "REPLACE")
        if w2 > 0:
            groups[n2].add([v.index], w2 / total, "REPLACE")
    mod = obj.modifiers.new("Skeleton", "ARMATURE")
    mod.object = arm
    obj.parent = arm


# --------------------------------------------------------------- animation

FPS = 30


def _world_rot(axis, deg):
    v = {"x": Vector((1, 0, 0)), "f": Vector((0, -1, 0)), "u": Vector((0, 0, 1))}[axis]
    return Matrix.Rotation(math.radians(deg), 3, v)


def _key(arm, frame, pose):
    """pose: bone -> list of (axis, degrees) applied in the T-pose (armature) frame, and
    "_hips_u": vertical offset of the hips in meters."""
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        rest = pb.bone.matrix_local.to_3x3()
        world = Matrix.Identity(3)
        for axis, deg in pose.get(pb.name, []):
            world = (deg if axis == "m" else _world_rot(axis, deg)) @ world
        pb.rotation_quaternion = (rest.inverted() @ world @ rest).to_quaternion()
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        if pb.name == "Hips":
            pb.location = rest.inverted() @ Vector((0, 0, pose.get("_hips_u", 0.0)))
            pb.keyframe_insert("location", frame=frame)


def _p(x, f, u):
    return Vector((x, -f, u))


def _two_bone(shoulder, hand, a, b, pole):
    """Elbow and reachable hand position for a two-bone chain (Blender coordinates)."""
    d = hand - shoulder
    length = min(d.length, a + b - 1e-3)
    axis = d.normalized()
    cos_a = max(-1.0, min(1.0, (a * a + length * length - b * b) / (2 * a * length)))
    alpha = math.acos(cos_a)
    bend = (pole - axis * pole.dot(axis)).normalized()
    elbow = shoulder + axis * a * math.cos(alpha) + bend * a * math.sin(alpha)
    return elbow, shoulder + axis * length


def _reach(side, hand_target, pole):
    """Upper/lower arm rotations (T-pose frame) that put the hand on hand_target (x, f, u)."""
    s = L if side == "Left" else R
    shoulder = _p(s * 0.19, 0.0, SHOULDER_U)
    rest_dir = Vector((s, 0.0, 0.0))
    elbow, hand = _two_bone(shoulder, _p(*hand_target), 0.28, 0.27, _p(*pole).normalized())
    w_upper = rest_dir.rotation_difference((elbow - shoulder).normalized()).to_matrix()
    w_lower_world = rest_dir.rotation_difference((hand - elbow).normalized()).to_matrix()
    return {side + "UpperArm": [("m", w_upper)], side + "LowerArm": [("m", w_upper.inverted() @ w_lower_world)]}


def _rifle_arms(swing=0.0, bob=0.0):
    """Both hands on a rifle: right hand on the grip at the right hip, left hand on the
    handguard further forward. The operator's right is -X. swing/bob nudge the hands."""
    pose = {}
    pose.update(_reach("Right", (-0.2, 0.3 + swing * 0.004, 1.17 + bob * 0.004), (-1.0, -0.3, -1.0)))
    pose.update(_reach("Left", (-0.02, 0.5 + swing * 0.004, 1.23 + bob * 0.004), (1.0, -0.2, -1.2)))
    pose["Chest"] = [("x", 3.0 + bob)]
    return pose


def _merge(*poses):
    out = {}
    for p in poses:
        for k, v in p.items():
            if k.startswith("_"):
                out[k] = out.get(k, 0.0) + v
            else:
                out[k] = out.get(k, []) + v
    return out


def _gait(phase, stride, knee, lift, hip_drop, swing_arms=0.0):
    s = math.sin(phase)
    c = math.cos(phase)
    return {
        "LeftUpperLeg": [("x", stride * s)],
        "RightUpperLeg": [("x", -stride * s)],
        "LeftLowerLeg": [("x", knee * max(0.0, -c) + 5)],
        "RightLowerLeg": [("x", knee * max(0.0, c) + 5)],
        "LeftFoot": [("x", -lift * s)],
        "RightFoot": [("x", lift * s)],
        "Hips": [("u", 6.0 * s)],
        "_hips_u": -hip_drop * abs(math.cos(phase)),
    }


def _clip(arm, name, frames, pose_at):
    arm.animation_data_create()
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    for f in range(0, frames + 1, 2):
        _key(arm, f, pose_at(f / frames))
    track = arm.animation_data.nla_tracks.new()
    track.name = name
    track.strips.new(name, 0, act)
    arm.animation_data.action = None


def _animate(arm):
    arms = _rifle_arms
    _clip(arm, "idle-loop", 60, lambda t: _merge(arms(bob=1.5 * math.sin(t * 2 * math.pi)), {"_hips_u": -0.01}))
    _clip(arm, "walk-loop", 32, lambda t: _merge(arms(swing=4 * math.sin(t * 2 * math.pi)), _gait(t * 2 * math.pi, 26, 40, 10, 0.025)))
    _clip(arm, "run-loop", 20, lambda t: _merge(arms(swing=7 * math.sin(t * 2 * math.pi)), {"Spine": [("x", 10)]}, _gait(t * 2 * math.pi, 40, 75, 18, 0.05)))
    _clip(arm, "crouch-loop", 40, lambda t: _merge(arms(), {"Spine": [("x", 14)], "_hips_u": -0.32,
                                                          "LeftUpperLeg": [("x", -70 + 12 * math.sin(t * 2 * math.pi))], "RightUpperLeg": [("x", -55 - 12 * math.sin(t * 2 * math.pi))],
                                                          "LeftLowerLeg": [("x", 110)], "RightLowerLeg": [("x", 95)], "LeftFoot": [("x", -35)], "RightFoot": [("x", -35)]}))
    _clip(arm, "jump", 12, lambda t: _merge(arms(), {"LeftUpperLeg": [("x", -30 * t)], "RightUpperLeg": [("x", 10 * t)], "LeftLowerLeg": [("x", 50 * t)], "RightLowerLeg": [("x", 30 * t)]}))
    _clip(arm, "fall-loop", 30, lambda t: _merge(arms(swing=3 * math.sin(t * 2 * math.pi)), {"LeftUpperLeg": [("x", -25)], "RightUpperLeg": [("x", 5)], "LeftLowerLeg": [("x", 45)], "RightLowerLeg": [("x", 25)], "Spine": [("x", 6)]}))
    # Weapon handling: a small recoil, a reload (support hand to the magazine and
    # back) and a grenade throw.
    _clip(arm, "fire", 4, lambda t: _merge(arms(swing=-6 * (1 - t), bob=-3 * (1 - t))))

    def reload_pose(t):
        k = math.sin(min(1.0, t * 1.4) * math.pi)
        pose = arms()
        pose.update(_reach("Left", (-0.02 - 0.1 * k, 0.5 - 0.12 * k, 1.23 - 0.2 * k), (1.0, -0.2, -1.2)))
        return _merge(pose, {"Head": [("x", 12 * k)]})
    _clip(arm, "reload", 56, reload_pose)

    def throw_pose(t):
        wind = math.sin(min(1.0, t * 2.0) * math.pi * 0.5)
        out = max(0.0, (t - 0.5) * 2.0)
        hand = (-0.25, -0.15 + 0.75 * out, 1.55 + 0.15 * wind - 0.35 * out)
        pose = _reach("Right", hand, (-1.0, -0.5, -0.4))
        pose.update(_reach("Left", (0.15, 0.4 - 0.2 * out, 1.35), (1.0, 0.0, -1.0)))
        return _merge(pose, {"Spine": [("u", 20 * wind - 35 * out)]})
    _clip(arm, "throw", 24, throw_pose)

    # Healing: hands brought to the chest (patch) and held there.
    def heal_pose(t):
        pose = _reach("Right", (-0.06, 0.2, 1.28 + 0.01 * math.sin(t * 2 * math.pi)), (-1.0, 0.0, -1.0))
        pose.update(_reach("Left", (0.06, 0.22, 1.3), (1.0, 0.0, -1.0)))
        return _merge(pose, {"Head": [("x", 18)]})
    _clip(arm, "heal-loop", 40, heal_pose)

    # Drop: freefall (belly down, arms and legs spread) and gliding under the descent device.
    _clip(arm, "freefall-loop", 40, lambda t: {
        "Hips": [("x", 75 + 3 * math.sin(t * 2 * math.pi))],
        "LeftUpperArm": [("u", -25), ("f", 15)], "RightUpperArm": [("u", 25), ("f", -15)],
        "LeftLowerArm": [("f", 55)], "RightLowerArm": [("f", -55)],
        "LeftUpperLeg": [("x", 15), ("f", -12)], "RightUpperLeg": [("x", 15), ("f", 12)],
        "LeftLowerLeg": [("x", 45 + 5 * math.sin(t * 2 * math.pi))], "RightLowerLeg": [("x", 45 - 5 * math.sin(t * 2 * math.pi))],
        "Head": [("x", -40)]})

    def glide_pose(t):
        pose = _reach("Right", (-0.28, 0.12, 1.75), (-1.0, 0.3, -0.3))
        pose.update(_reach("Left", (0.28, 0.12, 1.75), (1.0, 0.3, -0.3)))
        return _merge(pose, {"LeftUpperLeg": [("x", -10 + 4 * math.sin(t * 2 * math.pi))], "RightUpperLeg": [("x", -2)],
                             "LeftLowerLeg": [("x", 20)], "RightLowerLeg": [("x", 30)], "Head": [("x", -15)]})
    _clip(arm, "glide-loop", 40, glide_pose)
    _clip(arm, "land", 12, lambda t: _merge(arms(), {"_hips_u": -0.25 * math.sin(t * math.pi), "Spine": [("x", 15 * math.sin(t * math.pi))],
                                                   "LeftUpperLeg": [("x", -45 * math.sin(t * math.pi))], "RightUpperLeg": [("x", -45 * math.sin(t * math.pi))],
                                                   "LeftLowerLeg": [("x", 80 * math.sin(t * math.pi))], "RightLowerLeg": [("x", 80 * math.sin(t * math.pi))]}))

    # Vehicles: seated with hands on the controls.
    def drive_pose(t):
        steer = 0.03 * math.sin(t * 2 * math.pi)
        pose = _reach("Right", (-0.2, 0.45, 1.02 + steer), (-1.0, 0.0, -1.0))
        pose.update(_reach("Left", (0.2, 0.45, 1.02 - steer), (1.0, 0.0, -1.0)))
        return _merge(pose, {"_hips_u": -0.42, "Spine": [("x", 5)],
                             "LeftUpperLeg": [("x", -85)], "RightUpperLeg": [("x", -85)],
                             "LeftLowerLeg": [("x", 80)], "RightLowerLeg": [("x", 80)]})
    _clip(arm, "drive-loop", 60, drive_pose)

    # Elimination: knees buckle and the body slumps forward (the game tips it over).
    def death_pose(t):
        k = min(1.0, t * 1.5)
        return {"_hips_u": -0.45 * k, "Spine": [("x", 35 * k)], "Head": [("x", 25 * k)],
                "LeftUpperLeg": [("x", -60 * k)], "RightUpperLeg": [("x", -40 * k)],
                "LeftLowerLeg": [("x", 100 * k)], "RightLowerLeg": [("x", 80 * k)],
                "LeftUpperArm": [("f", -70 * k)], "RightUpperArm": [("f", 70 * k)]}
    _clip(arm, "death", 30, death_pose)
    _clip(arm, "tpose", 1, lambda t: {})
