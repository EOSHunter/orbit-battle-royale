"""Render a side view and a three-quarter view of exported models for review.

    blender -b --factory-startup --python art/tools/render_preview.py -- <out_dir> <model.glb> [...]

Writes <out_dir>/<asset-id>.png: side view on top, three-quarter view below.
"""

import math
import os
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
out_dir, models = args[0], args[1:]
os.makedirs(out_dir, exist_ok=True)


def render(glb, out):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    # Normalize to about 1 m so small items frame the same as rifles.
    longest = max(max(o.dimensions) for o in meshes)
    for o in bpy.context.scene.objects:
        if o.parent is None:
            o.scale = o.scale * (1.0 / longest)
            o.location = o.location * (1.0 / longest)
    bpy.context.view_layer.update()
    lo = Vector((min(min((o.matrix_world @ Vector(c))[i] for c in o.bound_box) for o in meshes) for i in range(3)))
    hi = Vector((max(max((o.matrix_world @ Vector(c))[i] for c in o.bound_box) for o in meshes) for i in range(3)))
    center = (lo + hi) / 2
    size = max(hi - lo)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 520
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.16, 0.17, 0.19, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    scene.world = world

    for rot, energy in (((math.radians(50), 0, math.radians(30)), 3.5), ((math.radians(60), 0, math.radians(200)), 1.5)):
        light = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
        light.data.energy = energy
        light.rotation_euler = rot
        scene.collection.objects.link(light)

    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(size, (hi.z - lo.z) * 1200 / 520 * 1.1) * 1.15
    scene.collection.objects.link(cam)
    scene.camera = cam

    paths = []
    for i, direction in enumerate((Vector((1, 0, 0)), Vector((1, -0.9, 0.55)).normalized())):
        cam.location = center + direction * size * 3
        cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
        p = out.replace(".png", f"_{i}.png")
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    return paths


for glb in models:
    asset_id = os.path.splitext(os.path.basename(glb))[0]
    print("RENDERED", render(os.path.abspath(glb), os.path.join(out_dir, asset_id + ".png")))
