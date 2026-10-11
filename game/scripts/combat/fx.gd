class_name Fx
extends RefCounted
## Placeholder combat effects: tracers, impact sparks, muzzle flashes.
## Short-lived nodes added under the scene root; production VFX replace these.

static var _tracer_mat: StandardMaterial3D
static var _spark_mat: StandardMaterial3D
static var _hit_mat: StandardMaterial3D
static var _tracer_mesh: BoxMesh
static var _spark_mesh: SphereMesh


static func _ensure() -> void:
	if _tracer_mat:
		return
	_tracer_mat = _unshaded(Color(1.0, 0.85, 0.6, 0.9))
	_spark_mat = _unshaded(Color(1.0, 0.75, 0.4, 1.0))
	_hit_mat = _unshaded(Color(1.0, 0.47, 0.5, 1.0))
	_tracer_mesh = BoxMesh.new()
	_tracer_mesh.size = Vector3(0.025, 0.025, 1.0)
	_spark_mesh = SphereMesh.new()
	_spark_mesh.radius = 0.06
	_spark_mesh.height = 0.12
	_spark_mesh.radial_segments = 6
	_spark_mesh.rings = 3


static func _unshaded(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = c
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.disable_fog = true
	return m


static func _root(world: World3D) -> Node:
	# Effects live under the current scene; World3D has no node of its own.
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree and tree.current_scene else (tree.root if tree else null)


static func tracer(world: World3D, from: Vector3, to: Vector3) -> void:
	_ensure()
	var root := _root(world)
	var length := from.distance_to(to)
	if root == null or length < 0.5:
		return
	var mi := MeshInstance3D.new()
	mi.mesh = _tracer_mesh
	mi.material_override = _tracer_mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.add_child(mi)
	var dir := (to - from) / length
	mi.global_transform = Transform3D(Basis.looking_at(dir, Vector3.UP if absf(dir.y) < 0.99 else Vector3.FORWARD), from + dir * length * 0.5)
	mi.scale = Vector3(1, 1, length)
	_fade_and_free(mi, 0.06)


static func impact(world: World3D, pos: Vector3, normal: Vector3, flesh: bool) -> void:
	_ensure()
	var root := _root(world)
	if root == null:
		return
	var mi := MeshInstance3D.new()
	mi.mesh = _spark_mesh
	mi.material_override = _hit_mat if flesh else _spark_mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.add_child(mi)
	mi.global_position = pos + normal * 0.03
	var t := mi.create_tween()
	t.tween_property(mi, "scale", Vector3.ONE * (2.2 if flesh else 1.6), 0.12)
	t.tween_callback(mi.queue_free)


static func muzzle_flash(parent: Node3D) -> void:
	var light := OmniLight3D.new()
	light.light_color = Color(1.0, 0.75, 0.45)
	light.light_energy = 2.5
	light.omni_range = 4.0
	parent.add_child(light)
	_fade_and_free(light, 0.05)


static func _fade_and_free(node: Node, seconds: float) -> void:
	var t := node.create_tween()
	t.tween_interval(seconds)
	t.tween_callback(node.queue_free)
