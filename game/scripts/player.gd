class_name Player
extends CharacterBody3D
## First-person player: movement (walk, sprint, crouch, jump, no fall damage,
## Tethercaster rope physics) and combat (five-slot inventory, weapons,
## healing with use time and interruption, looting).
## Air movement only adds speed up to `air_speed` in the wished direction, so
## momentum from a swing carries until you land.

signal landed(drop_height: float, impact_speed: float)
signal eliminated(attacker: Node)
signal heal_started(def: HealDef)
signal heal_finished(def: HealDef)
signal heal_interrupted(reason: String)
signal notice(text: String)

enum State { GROUND, AIR, TETHERED, DEAD }

const STAND_HEIGHT := 1.8
const CROUCH_HEIGHT := 1.1
const HEAD_FROM_TOP := 0.18
## Swimming: feet this far below the surface means deep water (head stays above).
const SWIM_DEPTH := 1.35
const SWIM_SPEED := 3.0
const AIM_SENSITIVITY := 0.7

@export var tuning: MoveTuning
## Load the values saved by the tuning panel. Tests turn this off to use defaults.
static var use_saved_tuning := true
## Items given on spawn: "id" or "id:qty"; ammunition as "ammo:type:amount".
@export var start_loadout := PackedStringArray(["tethercaster"])

var state := State.GROUND
var crouching := false
var sprinting := false
## Ignore gameplay input briefly, e.g. after the click that captures the mouse.
var input_grace := 0.0
## False while a menu (like the inventory screen) owns the mouse.
var combat_input := true

## Healing in progress.
var using: HealDef
var use_left := 0.0
var _use_slot := -1
## The pickup the player is looking at and close enough to take.
var focused_pickup: Pickup

var _coyote := 0.0
var _jump_buffer := 0.0
var _peak_y := 0.0
var _was_on_floor := true
## Water surface height for swimming; the default keeps maps without water dry.
@export var water_level := -10000.0
var in_water := false
var _aura: CPUParticles3D
var _dust_left := 0.0
var _land_dip := 0.0
var _swing_mode := false

@onready var head: Node3D = $Head
@onready var camera: Camera3D = $Head/Camera3D
@onready var tether: Tethercaster = $Head/Camera3D/Tethercaster
@onready var weapons: WeaponController = $Head/Camera3D/Weapons
@onready var health: Health = $Health
@onready var inventory: Inventory = $Inventory
@onready var _shape: CapsuleShape3D = $CollisionShape3D.shape
@onready var _shape_node: CollisionShape3D = $CollisionShape3D


func _ready() -> void:
	add_to_group("player")
	if tuning == null:
		tuning = MoveTuning.load_saved() if use_saved_tuning else MoveTuning.new()
	tether.tuning = tuning
	camera.fov = tuning.fov
	_peak_y = global_position.y
	weapons.setup(self, inventory)
	health.damaged.connect(func(_a: float, _f: Vector3, _by: Node) -> void: _interrupt_use("Took damage"))
	health.died.connect(_die)
	inventory.selected_changed.connect(func(_i: int) -> void: _interrupt_use("Switched items"))
	give_loadout()


func give_loadout() -> void:
	inventory.clear()
	for entry in start_loadout:
		var parts := entry.split(":")
		if parts[0] == "ammo" and parts.size() == 3:
			inventory.add_ammo(StringName(parts[1]), int(parts[2]))
		else:
			var s := ItemCatalog.stack(StringName(parts[0]), int(parts[1]) if parts.size() > 1 else 1)
			if s.def:
				inventory.add(s)
	var first := inventory.slot_of(&"tethercaster")
	for i in Inventory.SLOT_COUNT:
		if inventory.get_slot(i) and inventory.get_slot(i).def.is_weapon():
			first = i
			break
	inventory.select(maxi(first, 0))


func respawn(where: Transform3D) -> void:
	health.reset()
	_interrupt_use("")
	weapons.cancel_reload()
	give_loadout()
	state = State.GROUND
	head.rotation.z = 0.0
	teleport_to(where)


func is_alive() -> bool:
	return state != State.DEAD


func can_auto_pickup() -> bool:
	return is_alive()


func has_tether() -> bool:
	return inventory.has_item(&"tethercaster")


func _unhandled_input(event: InputEvent) -> void:
	var motion := event as InputEventMouseMotion
	if motion == null or not combat_input:
		return
	# Only a locked pointer turns the camera; a free cursor never does.
	_turn(MouseLock.look_delta(motion) * 0.0022 * tuning.mouse_sensitivity * (AIM_SENSITIVITY if weapons.aiming else 1.0))


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
	if state == State.DEAD:
		velocity.x = move_toward(velocity.x, 0.0, delta * 20.0)
		velocity.z = move_toward(velocity.z, 0.0, delta * 20.0)
		velocity.y -= tuning.gravity * delta
		move_and_slide()
		head.rotation.z = move_toward(head.rotation.z, 0.5, delta)
		return
	var accepts_input := input_grace == 0.0
	var combat := accepts_input and combat_input

	if combat_input:
		var look := Input.get_vector("look_left", "look_right", "look_up", "look_down")
		if look != Vector2.ZERO:
			_turn(look * look.length() * tuning.stick_sensitivity * (AIM_SENSITIVITY if weapons.aiming else 1.0) * delta)

	var move := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var wish := global_basis * Vector3(move.x, 0.0, move.y)
	wish.y = 0.0
	wish = wish.limit_length(1.0)

	_update_crouch(delta)
	sprinting = Input.is_action_pressed("sprint") and move.y < -0.3 and not crouching and using == null and not weapons.aiming

	var on_floor := is_on_floor()
	_coyote = tuning.coyote_time if on_floor else _coyote - delta
	if accepts_input and Input.is_action_just_pressed("jump"):
		_jump_buffer = tuning.jump_buffer
	else:
		_jump_buffer -= delta

	_combat(delta, combat, move.length())

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

	_swim(delta)
	var fall_speed := -velocity.y
	move_and_slide()
	_track_landing(fall_speed)
	_land_dip = move_toward(_land_dip, 0.0, delta * 0.6)
	head.position.y = _shape.height - HEAD_FROM_TOP - _land_dip
	var fov_target := tuning.fov * (weapons.weapon().aim_fov_scale if weapons.aiming and weapons.weapon() else 1.0)
	camera.fov = lerpf(camera.fov, fov_target, minf(1.0, delta * 14.0))


# ---------------------------------------------------------------- combat

func _combat(delta: float, combat: bool, move_amount: float) -> void:
	if combat:
		for i in Inventory.SLOT_COUNT:
			if Input.is_action_just_pressed("slot_%d" % (i + 1)):
				inventory.select(i)
		if Input.is_action_just_pressed("slot_next"):
			inventory.select((inventory.selected + 1) % Inventory.SLOT_COUNT)
		if Input.is_action_just_pressed("slot_prev"):
			inventory.select((inventory.selected + Inventory.SLOT_COUNT - 1) % Inventory.SLOT_COUNT)
		if Input.is_action_just_pressed("reload"):
			weapons.start_reload()
		if Input.is_action_just_pressed("interact"):
			interact()
		if Input.is_action_just_pressed("grapple") and has_tether():
			_toggle_tether()

	var sel := inventory.selected_stack()
	var fire_pressed := combat and Input.is_action_just_pressed("fire")
	var fire_held := combat and Input.is_action_pressed("fire")
	var aim_held := combat and Input.is_action_pressed("aim")
	var moving_ratio := clampf(horizontal_speed() / maxf(0.1, tuning.walk_speed), 0.0, 1.0) * clampf(move_amount * 2.0, 0.0, 1.0)
	if sel and sel.def is HealDef:
		if fire_pressed and using == null:
			start_use(inventory.selected)
		weapons.tick(delta, false, false, false, moving_ratio)
	elif sel and sel.def.id == &"tethercaster":
		if fire_pressed:
			_toggle_tether()
		weapons.tick(delta, false, false, false, moving_ratio)
	else:
		weapons.tick(delta, fire_pressed, fire_held, aim_held, moving_ratio)

	if using:
		use_left -= delta
		var s := inventory.get_slot(_use_slot)
		if s == null or s.def != using:
			_interrupt_use("Item gone")
		elif use_left <= 0.0:
			var def := using
			using = null
			health.apply_heal(def)
			inventory.consume(_use_slot)
			Fx.stop_aura(_aura)
			heal_finished.emit(def)
	_update_focus()


func start_use(slot: int) -> bool:
	var s := inventory.get_slot(slot)
	var def: HealDef = s.def as HealDef if s else null
	if def == null:
		return false
	if not health.can_use(def):
		notice.emit("Health is full" if def.pool == HealDef.Pool.HEALTH else "Shields are full")
		return false
	using = def
	use_left = def.use_time
	_use_slot = slot
	Fx.stop_aura(_aura)
	_aura = Fx.heal_aura(self, def.pool != HealDef.Pool.HEALTH)
	heal_started.emit(def)
	return true


func _interrupt_use(reason: String) -> void:
	if using == null:
		return
	using = null
	Fx.stop_aura(_aura)
	if reason != "":
		heal_interrupted.emit(reason)


func _toggle_tether() -> void:
	if tether.is_attached():
		tether.release()
	elif tether.try_attach():
		_interrupt_use("Fired the Tethercaster")


func interact() -> void:
	if focused_pickup == null:
		return
	var item_name := focused_pickup.display_name()
	if not focused_pickup.collect_into(inventory):
		var full: bool = not focused_pickup.is_ammo() and inventory.preview(focused_pickup.stack).full
		notice.emit("Carrying the maximum of %s" % focused_pickup.stack.def.display_name if full
			else "No free slot for %s · open the inventory to replace" % item_name)


func _update_focus() -> void:
	focused_pickup = null
	var best := Pickup.INTERACT_RANGE
	var eye := camera.global_position
	var fwd := -camera.global_basis.z
	for node in get_tree().get_nodes_in_group(Pickup.GROUP):
		var p := node as Pickup
		var to := p.global_position + Vector3(0, 0.5, 0) - eye
		var d := to.length()
		if d < best and fwd.dot(to / d) > 0.55:
			best = d
			focused_pickup = p


func _die(attacker: Node) -> void:
	state = State.DEAD
	_interrupt_use("")
	tether.reset()
	weapons.cancel_reload()
	eliminated.emit(attacker)


# ---------------------------------------------------------------- movement

func _target_speed() -> float:
	var speed := tuning.crouch_speed if crouching else (tuning.sprint_speed if sprinting else tuning.walk_speed)
	if using:
		speed *= using.move_scale
	return speed


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


## Deep water: float with the head above the surface, move slowly, no sprint.
## Crossing open water is meant to be slow and exposed. Shallow water (below
## the chest) is waded through normally.
func _swim(delta: float) -> void:
	in_water = global_position.y < water_level - SWIM_DEPTH
	if not in_water or tether.is_attached():
		return
	sprinting = false
	var depth := water_level - SWIM_DEPTH - global_position.y
	# Cancel this frame's gravity, then ease toward floating at the surface.
	velocity.y += tuning.gravity * delta
	velocity.y = move_toward(velocity.y, clampf(depth * 3.0, -1.5, 2.5), delta * 40.0)
	var flat := Vector2(velocity.x, velocity.z).limit_length(SWIM_SPEED)
	velocity.x = flat.x
	velocity.z = flat.y
	if Input.is_action_just_pressed("jump") and depth < 0.3:
		velocity.y = tuning.jump_velocity * 0.6


func _track_landing(fall_speed: float) -> void:
	var on_floor := is_on_floor()
	if not on_floor:
		_peak_y = maxf(_peak_y, global_position.y)
	elif not _was_on_floor:
		var drop := _peak_y - global_position.y
		if drop > 1.0:
			landed.emit(drop, fall_speed)
			Fx.landing_dust(get_world_3d(), global_position, clampf(fall_speed / 20.0, 0.0, 1.0))
			# No fall damage, but a short camera dip so big drops still read as big.
			_land_dip = clampf(fall_speed * 0.012, 0.0, 0.18)
		_peak_y = global_position.y
	else:
		_peak_y = global_position.y
		if sprinting:
			_dust_left -= get_physics_process_delta_time()
			if _dust_left <= 0.0:
				_dust_left = 0.18
				Fx.sprint_dust(get_world_3d(), global_position)
	_was_on_floor = on_floor
