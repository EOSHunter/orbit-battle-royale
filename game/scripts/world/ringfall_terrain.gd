class_name RingfallTerrain
extends Node3D
## Builds the terrain at load: GPU-displaced chunks (two levels of detail) from
## the heightmap image, heightmap collision from the baked TerrainData, and the
## sea and lake water plane. Nothing heavy ships in the scene file.

const CHUNK := 128.0
const NEAR_END := 180.0

@export var heightmap: Texture2D
@export var splatmap: Texture2D
@export var data: TerrainData
@export var water_level := 0.0

var _material: ShaderMaterial


func _ready() -> void:
	_material = ShaderMaterial.new()
	_material.shader = load("res://shaders/terrain.gdshader")
	_set_common(_material)
	_material.set_shader_parameter("splatmap", splatmap)
	_build_chunks()
	_build_collision()
	_build_water()


func _set_common(m: ShaderMaterial) -> void:
	m.set_shader_parameter("heightmap", heightmap)
	m.set_shader_parameter("map_half", data.world_size() * 0.5)
	m.set_shader_parameter("spacing", data.spacing)
	m.set_shader_parameter("height_min", data.height_min)
	m.set_shader_parameter("height_range", data.height_range)
	m.set_shader_parameter("samples", data.size)


func _build_chunks() -> void:
	var near := PlaneMesh.new()
	near.size = Vector2(CHUNK, CHUNK)
	near.subdivide_width = int(CHUNK / data.spacing) - 1
	near.subdivide_depth = near.subdivide_width
	var far := PlaneMesh.new()
	far.size = near.size
	far.subdivide_width = int(CHUNK / (data.spacing * 4.0)) - 1
	far.subdivide_depth = far.subdivide_width
	var n := int(data.world_size() / CHUNK)
	var half := data.world_size() * 0.5
	var aabb := AABB(Vector3(-CHUNK * 0.5, data.height_min, -CHUNK * 0.5), Vector3(CHUNK, data.height_range, CHUNK))
	for cz in n:
		for cx in n:
			var center := Vector3(-half + (cx + 0.5) * CHUNK, 0.0, -half + (cz + 0.5) * CHUNK)
			for lod in 2:
				var mi := MeshInstance3D.new()
				mi.mesh = near if lod == 0 else far
				mi.material_override = _material
				mi.custom_aabb = aabb
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF  # the sun is high; terrain self-shadowing costs more than it shows
				mi.position = center
				if lod == 0:
					mi.visibility_range_end = NEAR_END
					mi.visibility_range_end_margin = 20.0
				else:
					mi.visibility_range_begin = NEAR_END
					mi.visibility_range_begin_margin = 20.0
				add_child(mi)


func _build_collision() -> void:
	var body := StaticBody3D.new()
	body.name = "TerrainBody"
	body.collision_layer = 1
	body.collision_mask = 0
	var shape := HeightMapShape3D.new()
	shape.map_width = data.size
	shape.map_depth = data.size
	shape.map_data = data.heights
	var cs := CollisionShape3D.new()
	cs.shape = shape
	cs.scale = Vector3(data.spacing, 1.0, data.spacing)
	body.add_child(cs)
	add_child(body)


func _build_water() -> void:
	var water := MeshInstance3D.new()
	water.name = "Water"
	var plane := PlaneMesh.new()
	plane.size = Vector2(9000, 9000)
	plane.subdivide_width = 8
	plane.subdivide_depth = 8
	water.mesh = plane
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/water.gdshader")
	_set_common(m)
	water.material_override = m
	water.position.y = water_level
	water.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(water)


func height_at(x: float, z: float) -> float:
	return data.height_at(x, z)
