extends Node3D
## Gives every model under this node static collision when the level loads, so
## location scenes only store placements. One trimesh shape is built per mesh
## and shared by every instance of it. Collision sits on the world layer, which
## also makes every surface hookable by the Tethercaster.
## Meshes tagged with the "no_collide" meta (or under a node tagged so) are skipped.

static var _shapes := {}


func _ready() -> void:
	_walk(self)


## Draw distance by size, so far locations cost few draw calls: props vanish
## first, buildings and landmarks stay visible across the map. Small pieces also
## stop casting shadows.
func _set_draw_distance(mi: MeshInstance3D) -> void:
	var s := mi.mesh.get_aabb().size * mi.global_transform.basis.get_scale() if mi.is_inside_tree() else mi.mesh.get_aabb().size
	var size := maxf(s.x, maxf(s.y, s.z))
	if size < 2.5:
		mi.visibility_range_end = 120.0
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	elif size < 7.0:
		mi.visibility_range_end = 350.0
	else:
		mi.visibility_range_end = 1000.0
	mi.visibility_range_end_margin = 15.0


func _walk(n: Node) -> void:
	if n.has_meta("no_collide"):
		return
	for c in n.get_children():
		var mi := c as MeshInstance3D
		if mi and mi.mesh:
			_set_draw_distance(mi)
		if mi and mi.mesh and not mi.has_meta("no_collide"):
			var shape: Shape3D = _shapes.get(mi.mesh)
			if shape == null:
				shape = mi.mesh.create_trimesh_shape()
				_shapes[mi.mesh] = shape
			var body := StaticBody3D.new()
			body.collision_layer = 1
			body.collision_mask = 0
			var cs := CollisionShape3D.new()
			cs.shape = shape
			body.add_child(cs)
			mi.add_child(body)
		_walk(c)
