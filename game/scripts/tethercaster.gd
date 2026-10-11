class_name Tethercaster
extends Node3D
## The grapple. Lives under the camera: aims along the view, hooks any world
## surface within range (decided 2026-10-11: no eligibility rules), and draws
## the cable. The player controller reads `anchor` and `rope_length` to apply
## rope physics. Players and bots can't be hooked; the aim ray ignores them.

signal attached(point: Vector3)
signal released(boosted: bool)
signal recharged

enum Aim { NO_TARGET, IN_RANGE, OUT_OF_RANGE, NOT_HOOKABLE }

const GRAPPLE_LAYER := 2          # physics layer 2, "grappable"
const SIGHT_MASK := 1 | 2         # world and grappable surfaces block the line

@export var tuning: MoveTuning
## Where the cable leaves the launcher, in camera space.
@export var muzzle_offset := Vector3(0.26, -0.2, -0.55)

var anchor := Vector3.ZERO
var rope_length := 0.0
var cooldown_left := 0.0
var aim := Aim.NO_TARGET
var aim_distance := 0.0
var aim_point := Vector3.ZERO

var _attached := false
var _exclude: Array[RID] = []
@onready var _cable: MeshInstance3D = $Cable
@onready var _anchor_marker: MeshInstance3D = $AnchorMarker


func _ready() -> void:
	_cable.top_level = true
	_anchor_marker.top_level = true
	_cable.visible = false
	_anchor_marker.visible = false
	var body := owner as CollisionObject3D
	if body:
		_exclude = [body.get_rid()]


func is_attached() -> bool:
	return _attached


func charge() -> float:
	## 1.0 when ready, 0.0 just after release.
	if tuning == null or tuning.grapple_cooldown <= 0.0:
		return 1.0
	return clampf(1.0 - cooldown_left / tuning.grapple_cooldown, 0.0, 1.0)


func muzzle_position() -> Vector3:
	return global_transform * muzzle_offset


func _physics_process(delta: float) -> void:
	if cooldown_left > 0.0 and not _attached:
		cooldown_left = maxf(0.0, cooldown_left - delta)
		if cooldown_left == 0.0:
			recharged.emit()
	_update_aim()


func _process(_delta: float) -> void:
	_cable.visible = _attached
	_anchor_marker.visible = _attached
	if not _attached:
		return
	var from := muzzle_position()
	var span := anchor - from
	var length := span.length()
	if length < 0.01:
		return
	var dir := span / length
	var up := Vector3.UP if absf(dir.y) < 0.99 else Vector3.FORWARD
	# CylinderMesh runs along local Y; point -Z at the anchor, then tip Y onto that axis.
	var basis := Basis.looking_at(dir, up) * Basis(Vector3.RIGHT, PI / 2.0)
	_cable.global_transform = Transform3D(basis, from + span * 0.5)
	_cable.scale = Vector3(1.0, length, 1.0)
	_anchor_marker.global_position = anchor


func _update_aim() -> void:
	var cam := get_viewport().get_camera_3d()
	if cam == null or tuning == null:
		return
	var from := cam.global_position
	var to := from - cam.global_basis.z * tuning.grapple_range * 2.0
	var query := PhysicsRayQueryParameters3D.create(from, to, SIGHT_MASK, _exclude)
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		aim = Aim.NO_TARGET
		return
	aim_point = hit.position
	aim_distance = from.distance_to(aim_point)
	if not _is_hookable(hit.collider):
		aim = Aim.NOT_HOOKABLE
	elif aim_distance > tuning.grapple_range:
		aim = Aim.OUT_OF_RANGE
	else:
		aim = Aim.IN_RANGE


func _is_hookable(collider: Object) -> bool:
	# Any world geometry the aim ray reaches (it only tests world layers).
	return collider is CollisionObject3D


func try_attach() -> bool:
	if _attached or cooldown_left > 0.0 or aim != Aim.IN_RANGE:
		return false
	_attached = true
	anchor = aim_point
	rope_length = muzzle_position().distance_to(anchor)
	attached.emit(anchor)
	return true


func release(boosted := false, start_cooldown := true) -> void:
	if not _attached:
		return
	_attached = false
	if start_cooldown and tuning:
		cooldown_left = tuning.grapple_cooldown
	released.emit(boosted)


func reset() -> void:
	release(false, false)
	cooldown_left = 0.0
