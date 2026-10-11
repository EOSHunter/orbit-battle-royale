class_name WeaponController
extends Node3D
## Runs the weapon in the player's selected slot: equip delay, fire rate,
## spread, recoil, aim-down-sights and reloading from the ammo reserve.
## Sits under the camera so shots leave from the crosshair.

signal fired(def: WeaponDef)
signal hit_confirmed(damage: float, killed: bool)
signal reload_started(seconds: float)
signal reload_finished

@export var muzzle_offset := Vector3(0.22, -0.18, -0.7)

var inventory: Inventory
var player: Player
var aiming := false
var spread_now := 0.0

var _cooldown := 0.0
var _equip_left := 0.0
var _reload_left := 0.0
var _recoil_kick := Vector2.ZERO
var _viewmodel: Node3D
var _viewmodel_for: ItemDef
var _exclude: Array[RID] = []


func setup(owner_player: Player, inv: Inventory) -> void:
	player = owner_player
	inventory = inv
	_exclude = [player.get_rid()]
	inventory.selected_changed.connect(func(_i: int) -> void: _on_equip())
	inventory.changed.connect(_refresh_viewmodel)
	_on_equip()


func weapon() -> WeaponDef:
	var s: ItemStack = inventory.selected_stack() if inventory else null
	return s.def as WeaponDef if s else null


func stack() -> ItemStack:
	return inventory.selected_stack() if inventory else null


func is_reloading() -> bool:
	return _reload_left > 0.0


func reload_progress() -> float:
	var w := weapon()
	return 1.0 - _reload_left / w.reload_time if w and _reload_left > 0.0 else 0.0


func is_ready() -> bool:
	return _equip_left <= 0.0 and _reload_left <= 0.0 and _cooldown <= 0.0


func _on_equip() -> void:
	_reload_left = 0.0
	var w := weapon()
	_equip_left = w.equip_time if w else 0.0
	_refresh_viewmodel()


## Call every physics frame with the fire button state.
func tick(delta: float, fire_pressed: bool, fire_held: bool, aim_held: bool, moving_ratio: float) -> void:
	_cooldown = maxf(0.0, _cooldown - delta)
	_equip_left = maxf(0.0, _equip_left - delta)
	var w := weapon()
	aiming = aim_held and w != null and _reload_left <= 0.0
	if _reload_left > 0.0:
		_reload_left -= delta
		if _reload_left <= 0.0:
			_finish_reload()
	if w == null:
		spread_now = 0.0
		return
	spread_now = (w.spread_aim if aiming else w.spread_hip) + w.spread_moving * clampf(moving_ratio, 0.0, 1.0) * (0.4 if aiming else 1.0)
	var wants := fire_held if w.automatic else fire_pressed
	if wants and is_ready():
		var s := stack()
		if s.mag > 0:
			_fire(w, s)
		elif fire_pressed:
			start_reload()
	# Recoil recovers toward the original aim.
	if _recoil_kick != Vector2.ZERO:
		var back := _recoil_kick * minf(1.0, delta * 9.0)
		_recoil_kick -= back
		player.head.rotation.x -= back.y
		player.rotation.y -= back.x


func _fire(w: WeaponDef, s: ItemStack) -> void:
	s.mag -= 1
	_cooldown = w.fire_interval
	var cam := player.camera
	var muzzle := cam.global_transform * muzzle_offset
	var result := Hitscan.fire(get_world_3d(), cam.global_position, -cam.global_basis.z, muzzle, w, spread_now, player, _exclude)
	fired.emit(w)
	if int(result.hits) > 0:
		hit_confirmed.emit(float(result.damage), int(result.kills) > 0)
	# Kick the view; most of it recovers, a little stays (aim drifts up under sustained fire).
	var kick := Vector2(deg_to_rad(randf_range(-w.recoil_yaw, w.recoil_yaw)), deg_to_rad(w.recoil_pitch)) * (0.6 if aiming else 1.0)
	player.head.rotation.x = clampf(player.head.rotation.x + kick.y, deg_to_rad(-89.0), deg_to_rad(89.0))
	player.rotation.y += kick.x
	_recoil_kick += kick * 0.75
	if _viewmodel:
		Fx.muzzle_flash(_viewmodel)
		_viewmodel.position.z += 0.05
	inventory.changed.emit()
	if s.mag == 0 and inventory.ammo_count(w.ammo_type) > 0:
		start_reload()


func start_reload() -> bool:
	var w := weapon()
	var s := stack()
	if w == null or _reload_left > 0.0 or s.mag >= w.magazine or inventory.ammo_count(w.ammo_type) <= 0:
		return false
	_reload_left = w.reload_time
	reload_started.emit(w.reload_time)
	return true


func cancel_reload() -> void:
	_reload_left = 0.0


func _finish_reload() -> void:
	_reload_left = 0.0
	var w := weapon()
	var s := stack()
	if w == null or s == null:
		return
	s.mag += inventory.take_ammo(w.ammo_type, w.magazine - s.mag)
	reload_finished.emit()
	inventory.changed.emit()


func _process(delta: float) -> void:
	if _viewmodel:
		var rest := Vector3(0.0, -0.06 if aiming else 0.0, 0.0)
		var target := rest + Vector3(0.0, -0.25 if _reload_left > 0.0 else 0.0, 0.0) + Vector3(0.0, -0.3 * clampf(_equip_left * 3.0, 0.0, 1.0), 0.0)
		_viewmodel.position = _viewmodel.position.lerp(target, minf(1.0, delta * 14.0))


func _refresh_viewmodel() -> void:
	var s := stack()
	var def: ItemDef = s.def if s else null
	if def == _viewmodel_for and _viewmodel:
		return
	_viewmodel_for = def
	if _viewmodel:
		_viewmodel.queue_free()
		_viewmodel = null
	if def == null:
		return
	_viewmodel = Viewmodels.build(def)
	add_child(_viewmodel)
	_viewmodel.position = Vector3(0, -0.3, 0)
