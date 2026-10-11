class_name Bot
extends CharacterBody3D
## Phase 1 bot: patrols cover points, notices the player only by line of sight
## or by hearing gunfire (no wallhacks), engages after a reaction delay with
## imperfect aim, retreats out of sight to heal when hurt, and drops its loot.

signal eliminated(bot: Bot, attacker: Node)

enum Mode { PATROL, ENGAGE, SEARCH, RETREAT, HEAL, DEAD }

const THINK_INTERVAL := 0.15
const EYE_HEIGHT := 1.55

@export var display_name := "Bot"
@export var weapon_id: StringName = &"ar7"
@export var walk_speed := 3.2
@export var run_speed := 5.0
@export var vision_range := 60.0
@export_range(30.0, 180.0) var vision_fov := 120.0
@export var hearing_range := 35.0
## Seconds between first seeing the player and opening fire.
@export var reaction_time := 0.6
## Base aim error cone; grows with distance and target speed.
@export var aim_error := 3.5
## Bots deal less damage than players while the slice is tuned.
@export var damage_scale := 0.55
@export var heals := 2
@export var start_shield := 50.0

var mode := Mode.PATROL
var target: Player
var cover_points: Array[Vector3] = []
var weapon: WeaponDef
var mag := 0
var reserve := 120

var _has_los := false
var _seen_for := 0.0
var _last_known := Vector3.ZERO
var _goal := Vector3.ZERO
var _think := 0.0
var _fire_cd := 0.0
var _burst_left := 0
var _reload_left := 0.0
var _heal_left := 0.0
var _strafe := 1.0
var _strafe_timer := 0.0
var _stuck := 0.0
var _search_timer := 0.0
var _gravity := 20.0
var _visor: MeshInstance3D

@onready var health: Health = $Health


func _ready() -> void:
	add_to_group("bots")
	collision_layer = Hitscan.BOTS
	collision_mask = Hitscan.WORLD | Hitscan.GRAPPABLE | Hitscan.PLAYER | Hitscan.BOTS
	weapon = ItemCatalog.get_def(weapon_id) as WeaponDef
	mag = weapon.magazine
	health.max_shield = 100.0
	health.start_shield = start_shield
	health.reset()
	health.damaged.connect(_on_damaged)
	health.died.connect(_on_died)
	_goal = global_position
	_build_body()


func _build_body() -> void:
	var shape := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.35
	cap.height = 1.8
	shape.shape = cap
	shape.position.y = 0.9
	add_child(shape)
	var body := MeshInstance3D.new()
	var mesh := CapsuleMesh.new()
	mesh.radius = 0.34
	mesh.height = 1.78
	body.mesh = mesh
	body.position.y = 0.9
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color("2b3550")
	mat.metallic = 0.4
	mat.roughness = 0.5
	body.material_override = mat
	add_child(body)
	_visor = MeshInstance3D.new()
	var visor := BoxMesh.new()
	visor.size = Vector3(0.42, 0.12, 0.2)
	_visor.mesh = visor
	_visor.position = Vector3(0, EYE_HEIGHT, -0.24)
	var vmat := StandardMaterial3D.new()
	vmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	vmat.albedo_color = Color("ffb45c")
	_visor.material_override = vmat
	add_child(_visor)
	var gun := MeshInstance3D.new()
	var gm := BoxMesh.new()
	gm.size = Vector3(0.08, 0.1, 0.6)
	gun.mesh = gm
	gun.position = Vector3(0.28, 1.2, -0.35)
	var gmat := StandardMaterial3D.new()
	gmat.albedo_color = Color("1a2135")
	gun.material_override = gmat
	add_child(gun)


func eye_position() -> Vector3:
	return global_position + Vector3.UP * EYE_HEIGHT


## Gunfire or other noise at `pos`.
func hear(pos: Vector3) -> void:
	if mode == Mode.DEAD or global_position.distance_to(pos) > hearing_range:
		return
	_last_known = pos
	if mode == Mode.PATROL:
		mode = Mode.SEARCH
		_search_timer = 6.0


func _physics_process(delta: float) -> void:
	if mode == Mode.DEAD:
		return
	if not is_on_floor():
		velocity.y -= _gravity * delta
	_fire_cd = maxf(0.0, _fire_cd - delta)
	if _reload_left > 0.0:
		_reload_left -= delta
		if _reload_left <= 0.0:
			var take := mini(weapon.magazine - mag, reserve)
			mag += take
			reserve -= take
	_think -= delta
	if _think <= 0.0:
		_think = THINK_INTERVAL
		_perceive()
		_decide()

	var move := Vector3.ZERO
	var speed := walk_speed
	var face := Vector3.ZERO
	match mode:
		Mode.PATROL:
			move = _toward(_goal)
			face = move
			if global_position.distance_to(_goal) < 1.5 or _stuck > 1.0:
				_pick_patrol_goal()
		Mode.ENGAGE:
			face = target.global_position - global_position
			move = _engage_move(delta)
			speed = walk_speed
			_try_fire()
		Mode.SEARCH:
			move = _toward(_last_known)
			face = move
			speed = run_speed
			_search_timer -= delta
			if global_position.distance_to(_last_known) < 2.0 or _search_timer <= 0.0 or _stuck > 1.5:
				mode = Mode.PATROL
				_pick_patrol_goal()
		Mode.RETREAT:
			move = _toward(_goal)
			face = move
			speed = run_speed
			if global_position.distance_to(_goal) < 1.5 or _stuck > 1.5:
				mode = Mode.HEAL
				_heal_left = 2.0
		Mode.HEAL:
			_heal_left -= delta
			if _heal_left <= 0.0:
				health.apply_heal(ItemCatalog.get_def(&"field_patch") as HealDef)
				heals -= 1
				_heal_left = 2.0
				if heals <= 0 or health.health >= 90.0:
					mode = Mode.SEARCH if _last_known != Vector3.ZERO else Mode.PATROL
					_search_timer = 6.0

	velocity.x = move.x * speed
	velocity.z = move.z * speed
	var before := global_position
	move_and_slide()
	var moved := (global_position - before).length()
	_stuck = _stuck + delta if move != Vector3.ZERO and moved < speed * delta * 0.2 else 0.0
	face.y = 0.0
	if face.length() > 0.01:
		var want := atan2(-face.x, -face.z)
		rotation.y = lerp_angle(rotation.y, want, minf(1.0, delta * 8.0))


func _toward(point: Vector3) -> Vector3:
	var d := point - global_position
	d.y = 0.0
	return d.normalized() if d.length() > 0.3 else Vector3.ZERO


func _engage_move(delta: float) -> Vector3:
	# Strafe across the player's view and hold a preferred range for the weapon.
	_strafe_timer -= delta
	if _strafe_timer <= 0.0 or _stuck > 0.5:
		_strafe = -_strafe if randf() < 0.6 else _strafe
		_strafe_timer = randf_range(0.8, 2.0)
		_stuck = 0.0
	var to := target.global_position - global_position
	to.y = 0.0
	var dist := to.length()
	var dir := to / maxf(dist, 0.01)
	var side := Vector3(-dir.z, 0.0, dir.x) * _strafe
	var preferred := 7.0 if weapon.pellets > 1 else 20.0
	var radial := 0.0
	if dist > preferred + 4.0:
		radial = 1.0
	elif dist < preferred - 4.0:
		radial = -0.7
	return (side + dir * radial).normalized()


func _perceive() -> void:
	if target == null or not target.is_alive():
		_has_los = false
		_seen_for = 0.0
		return
	var eye := eye_position()
	var aim_at := target.camera.global_position
	var to := aim_at - eye
	var dist := to.length()
	var forward := -global_basis.z
	var in_cone := forward.dot(to / dist) > cos(deg_to_rad(vision_fov * 0.5)) or dist < 8.0 or mode == Mode.ENGAGE
	var visible := false
	if dist < vision_range and in_cone:
		var q := PhysicsRayQueryParameters3D.create(eye, aim_at, Hitscan.WORLD | Hitscan.GRAPPABLE, [get_rid()])
		visible = get_world_3d().direct_space_state.intersect_ray(q).is_empty()
	_has_los = visible
	if visible:
		_last_known = target.global_position
		_seen_for += THINK_INTERVAL
	else:
		_seen_for = 0.0


func _decide() -> void:
	var hurt := health.shield <= 0.0 and health.health < 50.0
	if hurt and heals > 0 and mode in [Mode.ENGAGE, Mode.SEARCH, Mode.PATROL]:
		mode = Mode.RETREAT
		_goal = _pick_cover_away()
		return
	if mode in [Mode.RETREAT, Mode.HEAL]:
		return
	if _has_los:
		mode = Mode.ENGAGE
	elif mode == Mode.ENGAGE:
		mode = Mode.SEARCH
		_search_timer = 6.0


func _try_fire() -> void:
	if not _has_los or _seen_for < reaction_time or _fire_cd > 0.0 or _reload_left > 0.0:
		return
	if mag <= 0:
		if reserve > 0:
			_reload_left = weapon.reload_time * 1.2
		return
	if _burst_left <= 0:
		_burst_left = 1 if weapon.pellets > 1 else randi_range(3, 6)
	_burst_left -= 1
	_fire_cd = weapon.fire_interval * (1.25 if _burst_left > 0 else randf_range(3.0, 6.0))
	mag -= 1
	var eye := eye_position()
	var aim_at := target.global_position + Vector3.UP * randf_range(0.9, 1.5)
	var dist := eye.distance_to(aim_at)
	var error := aim_error * (1.0 + target.horizontal_speed() / 6.0) * clampf(dist / 20.0, 0.6, 2.0)
	if _seen_for < reaction_time + 0.6:
		error *= 1.5
	var muzzle := global_position + global_basis * Vector3(0.28, 1.2, -0.7)
	Hitscan.fire(get_world_3d(), eye, (aim_at - eye).normalized(), muzzle, weapon, error, self, [get_rid()], damage_scale)


func _pick_patrol_goal() -> void:
	_stuck = 0.0
	if cover_points.is_empty():
		_goal = global_position + Vector3(randf_range(-15, 15), 0, randf_range(-15, 15))
	else:
		_goal = cover_points[randi() % cover_points.size()]


func _pick_cover_away() -> Vector3:
	# The cover point farthest from the threat that the threat can't see.
	var threat := _last_known if _last_known != Vector3.ZERO else global_position
	var best := global_position - (threat - global_position).normalized() * 10.0
	var best_score := -INF
	var space := get_world_3d().direct_space_state
	for p in cover_points:
		var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * 1.2, threat + Vector3.UP * 1.5, Hitscan.WORLD | Hitscan.GRAPPABLE)
		var hidden := not space.intersect_ray(q).is_empty()
		var score := p.distance_to(threat) - p.distance_to(global_position) * 0.6 + (30.0 if hidden else 0.0)
		if score > best_score:
			best_score = score
			best = p
	return best


func _on_damaged(_amount: float, from: Vector3, attacker: Node) -> void:
	if mode == Mode.HEAL:
		mode = Mode.ENGAGE if _has_los else Mode.SEARCH
	if attacker is Node3D:
		_last_known = (attacker as Node3D).global_position
		if mode == Mode.PATROL:
			mode = Mode.SEARCH
			_search_timer = 6.0
	elif from != Vector3.ZERO:
		_last_known = from


func _on_died(attacker: Node) -> void:
	mode = Mode.DEAD
	collision_layer = 0
	collision_mask = Hitscan.WORLD | Hitscan.GRAPPABLE
	_visor.visible = false
	eliminated.emit(self, attacker)
	var t := create_tween()
	t.tween_property(self, "rotation:x", -PI / 2.0, 0.4).set_ease(Tween.EASE_IN)
	t.tween_interval(3.0)
	t.tween_callback(queue_free)
