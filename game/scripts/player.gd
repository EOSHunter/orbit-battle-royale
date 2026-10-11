class_name Player
extends CharacterBody3D
## First-person movement: walk, sprint, crouch, jump, no fall damage, and
## Tethercaster rope physics. Air movement only adds speed up to `air_speed`
## in the wished direction, so momentum from a swing carries until you land.

signal landed(drop_height: float, impact_speed: float)

enum State { GROUND, AIR, TETHERED }

const STAND_HEIGHT := 1.8
const CROUCH_HEIGHT := 1.1
const HEAD_FROM_TOP := 0.18

@export var tuning: MoveTuning

var state := State.GROUND
var crouching := false
var sprinting := false
## Ignore gameplay input briefly, e.g. after the click that captures the mouse.
var input_grace := 0.0

var _coyote := 0.0
var _jump_buffer := 0.0
var _peak_y := 0.0
var _was_on_floor := true
var _land_dip := 0.0
var _swing_mode := false

@onready var head: Node3D = $Head
@onready var camera: Camera3D = $Head/Camera3D
@onready var tether: Tethercaster = $Head/Camera3D/Tethercaster
@onready var _shape: CapsuleShape3D = $CollisionShape3D.shape
@onready var _shape_node: CollisionShape3D = $CollisionShape3D


func _ready() -> void:
	if tuning == null:
		tuning = MoveTuning.new()
	tether.tuning = tuning
	camera.fov = tuning.fov
	_peak_y = global_position.y


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		_turn((event as InputEventMouseMotion).screen_relative * 0.0022 * tuning.mouse_sensitivity)


func _turn(by: Vector2) -> void:
	rotation.y -= by.x
	head.rotation.x = clampf(head.rotation.x - by.y, deg_to_rad(-89.0), deg_to_rad(89.0))


func horizontal_speed() -> float:
	return Vector2(velocity.x, velocity.z).length()


func teleport_to(where: Transform3D) -> void:
	tether.reset()
	global_position = where.origin
	rotation = Vector3(0.0, where.basis.get_euler().y, 0.0)
	head.rotation.x = 0.0
	velocity = Vector3.ZERO
	_peak_y = global_position.y


func _physics_process(delta: float) -> void:
	input_grace = maxf(0.0, input_grace - delta)
	camera.fov = tuning.fov
	var accepts_input := input_grace == 0.0

	var look := Input.get_vector("look_left", "look_right", "look_up", "look_down")
	if look != Vector2.ZERO:
		_turn(look * look.length() * tuning.stick_sensitivity * delta)

	var move := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var wish := global_basis * Vector3(move.x, 0.0, move.y)
	wish.y = 0.0
	wish = wish.limit_length(1.0)

	_update_crouch(delta)
	sprinting = Input.is_action_pressed("sprint") and move.y < -0.3 and not crouching

	var on_floor := is_on_floor()
	_coyote = tuning.coyote_time if on_floor else _coyote - delta
	if accepts_input and Input.is_action_just_pressed("jump"):
		_jump_buffer = tuning.jump_buffer
	else:
		_jump_buffer -= delta

	if accepts_input and Input.is_action_just_pressed("grapple"):
		if tether.is_attached():
			tether.release()
		else:
			tether.try_attach()

	if tether.is_attached():
		state = State.TETHERED
		_tethered_move(delta, wish)
	else:
		state = State.GROUND if on_floor else State.AIR
		if on_floor:
			_ground_move(delta, wish)
		else:
			_air_move(delta, wish)
			velocity.y -= tuning.gravity * delta
		if _jump_buffer > 0.0 and _coyote > 0.0:
			velocity.y = tuning.jump_velocity
			_jump_buffer = 0.0
			_coyote = 0.0

	var fall_speed := -velocity.y
	move_and_slide()
	_track_landing(fall_speed)
	_land_dip = move_toward(_land_dip, 0.0, delta * 0.6)
	head.position.y = _shape.height - HEAD_FROM_TOP - _land_dip


func _target_speed() -> float:
	if crouching:
		return tuning.crouch_speed
	return tuning.sprint_speed if sprinting else tuning.walk_speed


func _ground_move(delta: float, wish: Vector3) -> void:
	var flat := Vector3(velocity.x, 0.0, velocity.z)
	var target := wish * _target_speed()
	var rate := tuning.ground_accel
	if wish == Vector3.ZERO:
		rate = tuning.ground_decel
	elif flat.length() > _target_speed() + 0.1:
		# Coming in hot from a swing: let the extra speed bleed off instead of snapping.
		rate = tuning.overspeed_friction
	flat = flat.move_toward(target, rate * delta)
	velocity.x = flat.x
	velocity.z = flat.z
	if velocity.y < 0.0:
		velocity.y = 0.0


func _air_move(delta: float, wish: Vector3) -> void:
	if wish == Vector3.ZERO:
		return
	var dir := wish.normalized()
	var current := Vector3(velocity.x, 0.0, velocity.z).dot(dir)
	var room := tuning.air_speed * wish.length() - current
	if room > 0.0:
		var add := dir * minf(room, tuning.air_accel * delta)
		velocity.x += add.x
		velocity.z += add.z


func _tethered_move(delta: float, wish: Vector3) -> void:
	var to_anchor := tether.anchor - global_position
	var distance := to_anchor.length()
	if distance < 0.01:
		return
	var dir := to_anchor / distance

	# Crouch while tethered stops reeling: a pure pendulum swing.
	_swing_mode = Input.is_action_pressed("crouch")
	velocity.y -= tuning.gravity * delta
	if not _swing_mode:
		velocity += dir * tuning.reel_accel * delta
		tether.rope_length = maxf(tuning.min_rope, minf(tether.rope_length, distance) - tuning.reel_speed * delta)
	velocity += wish * tuning.swing_steer * delta

	# Rope constraint: no moving away from the anchor beyond the rope length.
	var outward := -velocity.dot(dir)
	if distance >= tether.rope_length and outward > 0.0:
		velocity += dir * outward
	if distance > tether.rope_length + 0.25:
		velocity += dir * (distance - tether.rope_length) * 8.0 * delta
	velocity = velocity.limit_length(tuning.grapple_max_speed)

	if _jump_buffer > 0.0:
		_jump_buffer = 0.0
		tether.release(true)
		velocity.y += tuning.release_boost
	elif distance <= tuning.min_rope + 0.2 and is_on_floor():
		tether.release()


func _update_crouch(delta: float) -> void:
	var want := Input.is_action_pressed("crouch") and not tether.is_attached()
	if not want and crouching:
		# Stand only if there is headroom.
		var lift := Vector3.UP * (STAND_HEIGHT - CROUCH_HEIGHT)
		if test_move(global_transform, lift):
			want = true
	crouching = want
	var target := CROUCH_HEIGHT if crouching else STAND_HEIGHT
	_shape.height = move_toward(_shape.height, target, delta * 6.0)
	_shape_node.position.y = _shape.height * 0.5


func _track_landing(fall_speed: float) -> void:
	var on_floor := is_on_floor()
	if not on_floor:
		_peak_y = maxf(_peak_y, global_position.y)
	elif not _was_on_floor:
		var drop := _peak_y - global_position.y
		if drop > 1.0:
			landed.emit(drop, fall_speed)
			# No fall damage, but a short camera dip so big drops still read as big.
			_land_dip = clampf(fall_speed * 0.012, 0.0, 0.18)
		_peak_y = global_position.y
	else:
		_peak_y = global_position.y
	_was_on_floor = on_floor
