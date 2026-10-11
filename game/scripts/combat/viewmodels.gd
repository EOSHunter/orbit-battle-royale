class_name Viewmodels
extends RefCounted
## First-person models. Items with a production model (ItemDef.model_path) use
## it; the rest get placeholder shapes built from boxes until theirs arrive.

const GRAPHITE := Color("2b3550")
const DARK := Color("1a2135")
const LIME := Color("c5f277")
const AMBER := Color("ffb45c")


static func build(def: ItemDef) -> Node3D:
	var root := Node3D.new()
	root.name = "Viewmodel"
	var model := def.instantiate_model()
	if model:
		model.position = def.view_offset
		model.rotation_degrees += def.view_rotation
		no_shadows(model)
		root.add_child(model)
		return root
	var hand := Vector3(0.24, -0.22, -0.48)
	match def.id:
		&"ar7":
			_box(root, hand + Vector3(0, 0, -0.08), Vector3(0.07, 0.09, 0.55), GRAPHITE, 0.6)
			_box(root, hand + Vector3(0, -0.08, 0.02), Vector3(0.05, 0.12, 0.08), DARK, 0.2)
			_box(root, hand + Vector3(0, 0.07, -0.05), Vector3(0.03, 0.04, 0.14), DARK, 0.4)
			_glow(root, hand + Vector3(0.036, 0.015, -0.12), Vector3(0.004, 0.012, 0.18), LIME)
			_glow(root, hand + Vector3(0.036, 0.02, 0.05), Vector3(0.004, 0.01, 0.04), AMBER)
		&"sg4":
			_box(root, hand + Vector3(0, 0, -0.04), Vector3(0.09, 0.1, 0.46), Color("4a3f3a"), 0.3)
			_box(root, hand + Vector3(0, -0.07, -0.18), Vector3(0.07, 0.05, 0.18), Color("5b4a3a"), 0.2)
			_box(root, hand + Vector3(0, 0.02, -0.32), Vector3(0.06, 0.06, 0.2), DARK, 0.6)
			_glow(root, hand + Vector3(0.046, 0.03, 0.06), Vector3(0.004, 0.012, 0.05), AMBER)
		&"tethercaster":
			_box(root, hand, Vector3(0.07, 0.085, 0.32), GRAPHITE, 0.6)
			_glow(root, hand + Vector3(0, 0.03, -0.06), Vector3(0.072, 0.02, 0.1), LIME)
			_glow(root, hand + Vector3(0, 0.0, 0.08), Vector3(0.074, 0.012, 0.03), AMBER)
		_:
			# Healing items: a canister with a window in the item's color.
			_box(root, hand + Vector3(-0.04, 0.02, 0.02), Vector3(0.09, 0.15, 0.09), DARK, 0.4)
			_glow(root, hand + Vector3(-0.04, 0.02, -0.025), Vector3(0.06, 0.1, 0.004), def.color)
	return root


## Field of view the first-person model is drawn for, independent of the
## player's (wide) camera FOV, so weapons don't stretch at the screen edges.
const VIEW_FOV := 62.0


## Squash a viewmodel sideways and vertically so that, seen through a camera
## with `camera_fov`, it looks as if drawn with VIEW_FOV. Call every frame
## (the camera FOV changes when aiming).
static func fit_fov(viewmodel: Node3D, camera_fov: float) -> void:
	var k := tan(deg_to_rad(camera_fov) * 0.5) / tan(deg_to_rad(VIEW_FOV) * 0.5)
	viewmodel.scale = Vector3(k, k, 1.0)


## Blend a model viewmodel between its hip pose and aiming down sights
## (ads 0..1). Aimed, the model's "sight" marker sits on the camera axis with
## the bore parallel to the view, so the rear sight and the front post line up
## on the screen center, where hitscan shots go.
static func pose(viewmodel: Node3D, def: ItemDef, ads: float) -> void:
	if viewmodel.get_child_count() == 0 or def.model_path.is_empty():
		return
	var model := viewmodel.get_child(0) as Node3D
	var sight := model.find_child("sight", true, false) as Node3D
	var e := smoothstep(0.0, 1.0, ads) if sight else 0.0
	var turn := Basis(Vector3.UP, PI)
	var ads_pos := Vector3(0.0, 0.0, -def.ads_eye) - turn * sight.position if sight else def.view_offset
	model.position = def.view_offset.lerp(ads_pos, e)
	model.rotation_degrees = Vector3(0.0, 180.0, 0.0) + def.view_rotation * (1.0 - e)


## The model's muzzle (or the Tethercaster's hook) marker, if it has one.
static func muzzle(viewmodel: Node3D) -> Node3D:
	if viewmodel == null:
		return null
	var m := viewmodel.find_child("muzzle", true, false) as Node3D
	return m if m else viewmodel.find_child("hook", true, false) as Node3D


## First-person models shouldn't throw shadows onto the world from the camera.
static func no_shadows(node: Node) -> void:
	if node is GeometryInstance3D:
		(node as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for c in node.get_children():
		no_shadows(c)


static func _box(parent: Node3D, pos: Vector3, size: Vector3, color: Color, metal := 0.3) -> void:
	var mi := MeshInstance3D.new()
	var m := BoxMesh.new()
	m.size = size
	mi.mesh = m
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.metallic = metal
	mat.roughness = 0.45
	mi.material_override = mat
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)


static func _glow(parent: Node3D, pos: Vector3, size: Vector3, color: Color) -> void:
	var mi := MeshInstance3D.new()
	var m := BoxMesh.new()
	m.size = size
	mi.mesh = m
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = color
	mi.material_override = mat
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(mi)
