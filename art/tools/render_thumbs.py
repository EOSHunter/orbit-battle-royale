"""Render a 256 px three-quarter thumbnail of every game model for the Asset Hub.

    blender -b --factory-startup --python art/tools/render_thumbs.py

Writes asset-hub/data/thumbs/<model>.jpg and skips models that already have one
(delete a thumbnail to re-render it). One Blender process renders them all.
"""
import glob
import math
import os

import bpy
from mathutils import Vector

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "asset-hub", "data", "thumbs")
os.makedirs(OUT, exist_ok=True)

for path in sorted(glob.glob(os.path.join(REPO, "game", "assets", "models", "*", "*.glb"))):
    asset_id = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(OUT, asset_id + ".jpg")
    if os.path.exists(out):
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    for arm in [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]:
        arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center, size = (lo + hi) / 2, (hi - lo).length
    if any(o.type == "ARMATURE" for o in bpy.context.scene.objects):
        # Skinned meshes report stale bounds; every character shares the 1.8 m T-pose frame.
        center, size = Vector((0, 0, 0.95)), 2.1
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 16
    scene.render.resolution_x = scene.render.resolution_y = 256
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 85
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.055, 0.075, 0.12, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.2
    scene.world = world
    for rot, energy in (((math.radians(50), 0, math.radians(30)), 3.5), ((math.radians(60), 0, math.radians(200)), 1.5)):
        light = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
        light.data.energy = energy
        light.rotation_euler = rot
        scene.collection.objects.link(light)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = size * 0.95
    cam.data.clip_end = size * 10
    scene.collection.objects.link(cam)
    scene.camera = cam
    # Imported glTF models face -Y; view from the front-right, a little above, in rest pose.
    for arm in [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]:
        arm.data.pose_position = "REST"
    d = Vector((0.9, -1.0, 0.55)).normalized()
    cam.location = center + d * size * 3
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("THUMB", asset_id)
