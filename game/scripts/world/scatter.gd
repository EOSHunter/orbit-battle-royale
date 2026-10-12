extends Node3D
## Vegetation and rocks scattered over the map, built into MultiMeshes when the
## level loads. The scene stores only model paths and packed transforms (the
## MultiMesh data itself can't be baked by the headless map builder).
## Each batch: {"path": glb path, "vis": visibility range in m, "shadow": bool,
## "xforms": PackedFloat32Array of 12 floats per instance (basis x, y, z, origin)}.

@export var batches: Array[Dictionary] = []

static var _parts_cache := {}


func _ready() -> void:
	for b: Dictionary in batches:
		var xforms: PackedFloat32Array = b.xforms
		var count := xforms.size() / 12
		# Vegetation joins the "foliage" group so Foliage density can thin it.
		# Its instances are shuffled so showing the first N thins evenly.
		var foliage := String(b.path).contains("/vegetation/")
		var order := range(count)
		if foliage:
			var rng := RandomNumberGenerator.new()
			rng.seed = count
			for i in range(count - 1, 0, -1):
				var j := rng.randi_range(0, i)
				var tmp: int = order[i]
				order[i] = order[j]
				order[j] = tmp
		for part: Array in _parts(b.path):
			var mm := MultiMesh.new()
			mm.transform_format = MultiMesh.TRANSFORM_3D
			mm.mesh = part[0]
			mm.instance_count = count
			var local: Transform3D = part[1]
			for i in count:
				var o: int = order[i] * 12
				var xf := Transform3D(
					Vector3(xforms[o], xforms[o + 1], xforms[o + 2]),
					Vector3(xforms[o + 3], xforms[o + 4], xforms[o + 5]),
					Vector3(xforms[o + 6], xforms[o + 7], xforms[o + 8]),
					Vector3(xforms[o + 9], xforms[o + 10], xforms[o + 11]))
				mm.set_instance_transform(i, xf * local)
			var mmi := MultiMeshInstance3D.new()
			mmi.multimesh = mm
			mmi.visibility_range_end = b.vis
			mmi.visibility_range_end_margin = 20.0
			if not b.shadow:
				mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			if foliage:
				mmi.add_to_group("foliage")
			add_child(mmi)


func _parts(path: String) -> Array:
	if _parts_cache.has(path):
		return _parts_cache[path]
	var out: Array = []
	var inst := (load(path) as PackedScene).instantiate()
	_collect(inst, Transform3D.IDENTITY, out)
	inst.free()
	_parts_cache[path] = out
	return out


func _collect(n: Node, xf: Transform3D, out: Array) -> void:
	for c in n.get_children():
		var n3 := c as Node3D
		if n3 == null:
			continue
		var t := xf * n3.transform
		var mi := c as MeshInstance3D
		if mi and mi.mesh:
			out.append([mi.mesh, t])
		_collect(c, t, out)
