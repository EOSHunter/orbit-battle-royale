class_name IonStorm
extends Node3D
## The closing ion storm: a glowing wall around a safe circle that shrinks in
## phases. Anyone outside takes damage that bypasses shields. Add it to a level
## and set `phases`; it starts at `start_radius` around its own position.

signal phase_started(index: int, target_radius: float, duration: float)
signal closed

## Each phase: wait (s), then shrink to `radius` over `shrink` (s), dealing `dps` outside.
@export var phases: Array[Dictionary] = [
	{"wait": 60.0, "shrink": 45.0, "radius": 600.0, "dps": 1.0},
	{"wait": 45.0, "shrink": 40.0, "radius": 350.0, "dps": 2.0},
	{"wait": 40.0, "shrink": 35.0, "radius": 180.0, "dps": 4.0},
	{"wait": 30.0, "shrink": 30.0, "radius": 80.0, "dps": 7.0},
	{"wait": 25.0, "shrink": 25.0, "radius": 25.0, "dps": 10.0},
	{"wait": 20.0, "shrink": 20.0, "radius": 0.0, "dps": 15.0},
]
@export var start_radius := 900.0
@export var wall_height := 400.0
@export var active := true

var radius := 0.0
var dps := 0.5
var _phase := -1
var _timer := 0.0
var _from := 0.0
var _shrinking := false
var _wall: MeshInstance3D
var _mesh: CylinderMesh
var _tick := 0.0


func _ready() -> void:
	radius = start_radius
	_mesh = CylinderMesh.new()
	_mesh.cap_top = false
	_mesh.cap_bottom = false
	_mesh.radial_segments = 96
	_mesh.rings = 1
	_mesh.height = wall_height
	_wall = MeshInstance3D.new()
	_wall.mesh = _mesh
	var mat := ShaderMaterial.new()
	mat.shader = load("res://shaders/ion_storm.gdshader")
	mat.set_shader_parameter("height", wall_height)
	_wall.material_override = mat
	_wall.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_wall.position.y = wall_height * 0.5 - 20.0
	add_child(_wall)
	_apply_radius()
	_next_phase()


## Is a world position outside the safe circle?
func is_outside(pos: Vector3) -> bool:
	var d := Vector2(pos.x - global_position.x, pos.z - global_position.z)
	return d.length() > radius


## Seconds until the next change and what it is, for the HUD.
func status() -> Dictionary:
	return {"phase": _phase, "shrinking": _shrinking, "seconds": _timer, "radius": radius}


func _next_phase() -> void:
	_phase += 1
	if _phase >= phases.size():
		closed.emit()
		set_physics_process(false)
		return
	var p: Dictionary = phases[_phase]
	_timer = float(p.wait)
	_shrinking = false
	phase_started.emit(_phase, float(p.radius), float(p.wait) + float(p.shrink))


func _physics_process(delta: float) -> void:
	if not active or _phase < 0 or _phase >= phases.size():
		return
	var p: Dictionary = phases[_phase]
	_timer -= delta
	if not _shrinking and _timer <= 0.0:
		_shrinking = true
		_from = radius
		_timer = float(p.shrink)
		dps = float(p.dps)
	elif _shrinking:
		var k := 1.0 - clampf(_timer / maxf(float(p.shrink), 0.01), 0.0, 1.0)
		radius = lerpf(_from, float(p.radius), k)
		_apply_radius()
		if _timer <= 0.0:
			_next_phase()
	# The wall is a big translucent surface: skip drawing it when it is far away.
	var cam := get_viewport().get_camera_3d()
	if cam:
		var d := Vector2(cam.global_position.x - global_position.x, cam.global_position.z - global_position.z).length()
		_wall.visible = absf(d - radius) < 450.0
	_tick -= delta
	if _tick <= 0.0:
		_tick = 1.0
		_damage_outside()


func _damage_outside() -> void:
	for group in ["player", "bots"]:
		for n in get_tree().get_nodes_in_group(group):
			var body := n as Node3D
			var health: Health = body.get_node_or_null("Health") as Health if body else null
			if health and health.alive and is_outside(body.global_position):
				health.take_damage(dps, global_position, self, true)


func _apply_radius() -> void:
	var r := maxf(radius, 0.01)
	_mesh.top_radius = r
	_mesh.bottom_radius = r
