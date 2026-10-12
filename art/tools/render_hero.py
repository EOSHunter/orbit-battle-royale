"""Render the operator as menu hero art: a lit, posed cut-out on a transparent
background, holding the AR-7 the way bots carry it in game.

    blender -b --factory-startup --python art/tools/render_hero.py -- <out.png> [clip[@frac]] [yaw_deg] [preview]

Writes a PNG with alpha (1200 x 1600, or 300 x 400 with "preview"). The game's
menus composite it over the key art.
"""

import math
import os
import sys

import bpy
from mathutils import Euler, Vector

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
args = sys.argv[sys.argv.index("--") + 1:]
out = os.path.abspath(args[0])
clip, _, frac = (args[1] if len(args) > 1 else "idle-loop@0.3").partition("@")
frac = float(frac or 0.3)
yaw = math.radians(float(args[2]) if len(args) > 2 else -28.0)
preview = len(args) > 3 and args[3] == "preview"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.gltf(filepath=os.path.join(REPO, "game", "assets", "models", "characters", "operator.glb"))
body = [o for o in scene.objects]
arm = next(o for o in body if o.type == "ARMATURE")
act = bpy.data.actions.get(clip)
if arm.animation_data is None:
    arm.animation_data_create()
for t in list(arm.animation_data.nla_tracks):
    arm.animation_data.nla_tracks.remove(t)
arm.animation_data.action = act
if act and hasattr(arm.animation_data, "action_slot") and act.slots:
    arm.animation_data.action_slot = act.slots[0]
start, end = act.frame_range if act else (0, 0)
scene.frame_set(int(start + (end - start) * frac))

# The gun, where the bot code puts it: Godot (0.2, 1.17, -0.3) in front of a
# body turned 180 degrees, which is (-0.2, 0.3 forward, 1.17 up) in the body's
# own glTF-in-Blender frame (the model faces -Y).
before = set(scene.objects)
bpy.ops.import_scene.gltf(filepath=os.path.join(REPO, "game", "assets", "models", "weapons", "ar-7-wayfarer.glb"))
gun_objs = [o for o in scene.objects if o not in before]
gun_root = bpy.data.objects.new("gun", None)
scene.collection.objects.link(gun_root)
for o in gun_objs:
    if o.parent is None:
        o.parent = gun_root
gun_root.location = Vector((-0.2, -0.3, 1.17))
gun_root.rotation_euler = Euler((0, 0, math.radians(float(os.environ.get("GUN_YAW", "-90")))))

# Turn the whole figure for a three-quarter view.
pivot = bpy.data.objects.new("pivot", None)
scene.collection.objects.link(pivot)
for o in list(scene.objects):
    if o.parent is None and o is not pivot:
        o.parent = pivot
pivot.rotation_euler = Euler((0, 0, yaw))

scene.render.engine = "CYCLES"
scene.cycles.samples = 24 if preview else 96
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.render.resolution_x = 300 if preview else 1200
scene.render.resolution_y = 400 if preview else 1600
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"

world = bpy.data.worlds.new("w")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.22, 0.16, 0.32, 1)  # dusk violet ambient
bg.inputs[1].default_value = 0.35
scene.world = world


def area(name, color, energy, size, loc, target):
    light = bpy.data.objects.new(name, bpy.data.lights.new(name, "AREA"))
    light.data.color = color
    light.data.energy = energy
    light.data.size = size
    light.location = Vector(loc)
    light.rotation_euler = (Vector(target) - light.location).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(light)


# Sunset key from behind-right, a hard warm rim from behind-left, cool violet fill
# from the front, and a soft bounce from below: matches the key art's light.
area("key", (1.0, 0.62, 0.32), 900, 1.2, (2.6, 2.4, 2.6), (0, 0, 1.2))
area("rim", (1.0, 0.75, 0.45), 1100, 0.6, (-2.2, 2.6, 2.2), (0, 0, 1.3))
area("fill", (0.55, 0.5, 1.0), 260, 3.0, (-1.5, -3.5, 1.6), (0, 0, 1.1))
area("bounce", (0.45, 0.35, 0.6), 60, 3.0, (0, -1.5, -0.6), (0, 0, 1.0))

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.lens = 70
scene.collection.objects.link(cam)
scene.camera = cam
# Low hero angle, slightly below the chest, framing head to boots.
cam.location = Vector((0.3, -4.1, 0.7))
cam.rotation_euler = (Vector((0.0, 0.0, 0.98)) - cam.location).to_track_quat("-Z", "Y").to_euler()

scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("HERO", out)
