class_name Viewmodels
extends RefCounted
## Placeholder first-person models built from boxes, one per item, until the
## production viewmodels from the asset list arrive. Shapes follow the concept
## silhouettes loosely so items are told apart at a glance.

const GRAPHITE := Color("2b3550")
const DARK := Color("1a2135")
const LIME := Color("c5f277")
const AMBER := Color("ffb45c")


static func build(def: ItemDef) -> Node3D:
	var root := Node3D.new()
	root.name = "Viewmodel"
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
