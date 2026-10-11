"""Render a rigged model in several animation clips (front and side) for review.

    blender -b --factory-startup --python art/tools/render_poses.py -- <out.png> <model.glb> clip[@0.5] ...

Each clip is rendered at the given fraction of its length (default 0.25), front
view above, side view below, all in one contact sheet.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
out, glb, clips = args[0], args[1], args[2:] or ["tpose"]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(glb))
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
scene.render.resolution_x = 360
scene.render.resolution_y = 480
world = bpy.data.worlds.new("w")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.16, 0.17, 0.19, 1)
scene.world = world
for rot, energy in (((math.radians(50), 0, math.radians(30)), 3.5), ((math.radians(60), 0, math.radians(200)), 1.5)):
    light = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    light.data.energy = energy
    light.rotation_euler = rot
    scene.collection.objects.link(light)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.type = "ORTHO"
cam.data.ortho_scale = 2.3
scene.collection.objects.link(cam)
scene.camera = cam

arm = next(o for o in scene.objects if o.type == "ARMATURE")
tiles = []
for spec in clips:
    name, _, frac = spec.partition("@")
    frac = float(frac or 0.25)
    act = bpy.data.actions.get(name)
    if arm.animation_data is None:
        arm.animation_data_create()
    for t in list(arm.animation_data.nla_tracks):
        arm.animation_data.nla_tracks.remove(t)
    arm.animation_data.action = act
    if act and hasattr(arm.animation_data, "action_slot") and act.slots:
        arm.animation_data.action_slot = act.slots[0]
    start, end = act.frame_range if act else (0, 0)
    scene.frame_set(int(start + (end - start) * frac))
    for i, d in enumerate((Vector((0, -1, 0)), Vector((1, 0, 0)))):
        cam.location = Vector((0, 0, 0.95)) + d * 6
        cam.rotation_euler = (Vector((0, 0, 0.95)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        p = os.path.join(os.path.dirname(out), f"_pose_{name}_{i}.png")
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        tiles.append((len(tiles) // 2, i, p))

# Contact sheet: one column per clip, front on top, side below.
cols = len(clips)
sheet = bpy.data.images.new("sheet", 360 * cols, 960)
import numpy as np
px = np.zeros((960, 360 * cols, 4), dtype=np.float32)
for col, row, p in tiles:
    img = bpy.data.images.load(p)
    a = np.array(img.pixels[:], dtype=np.float32).reshape(480, 360, 4)
    y0 = (1 - row) * 480
    px[y0:y0 + 480, col * 360:(col + 1) * 360] = a
    os.remove(p)
sheet.pixels.foreach_set(px.ravel())
sheet.filepath_raw = out
sheet.file_format = "PNG"
sheet.save()
print("SHEET", out)
