class_name TargetDummy
extends StaticBody3D
## A firing-range target: a bot operator standing (or strafing) with health
## and a shield. Hits flinch it (the HUD shows the hit numbers); a "kill"
## plays the elimination and the target resets.

signal downed(dummy: TargetDummy)

const RESET_TIME := 2.5

@export var shield := 50.0
## Side-to-side movement in meters (0 stands still) and its speed.
@export var strafe := 0.0
@export var strafe_speed := 2.2
@export var variant := 0

var health: Health
var _anim: AnimationPlayer
var _origin := Vector3.ZERO
var _t := 0.0
var _reset_in := 0.0


func _ready() -> void:
	add_to_group("targets")
	collision_layer = Hitscan.BOTS
	collision_mask = 0
	_origin = position
	_t = randf() * TAU
	health = Health.new()
	health.name = "Health"
	health.max_shield = 100.0
	health.start_shield = shield
	add_child(health)
	health.damaged.connect(_on_damaged)
	health.died.connect(_on_died)
	var shape := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.35
	cap.height = 1.8
	shape.shape = cap
	shape.position.y = 0.9
	add_child(shape)
	var path: String = Bot.BODY_MODELS[variant % Bot.BODY_MODELS.size()]
	if ResourceLoader.exists(path):
		var body := (load(path) as PackedScene).instantiate() as Node3D
		body.rotation.y = PI
		add_child(body)
		_anim = body.find_child("AnimationPlayer", true, false) as AnimationPlayer
		_play("idle")


func _play(clip: String) -> void:
	if _anim == null:
		return
	for n in _anim.get_animation_list():
		if n.begins_with(clip):
			_anim.play(n, 0.15)
			return


func _physics_process(delta: float) -> void:
	if _reset_in > 0.0:
		_reset_in -= delta
		if _reset_in <= 0.0:
			health.reset()
			_play("idle")
			rotation.z = 0.0
		return
	if strafe > 0.0:
		_t += delta * strafe_speed / maxf(strafe, 0.1)
		var x := sin(_t) * strafe
		var moving := cos(_t)
		position = _origin + Vector3(x, 0, 0)
		_play("walk" if absf(moving) > 0.25 else "idle")


func _on_damaged(_amount: float, _from: Vector3, _attacker: Node) -> void:
	# A small flinch.
	var tw := create_tween()
	tw.tween_property(self, "rotation:x", -0.06, 0.05)
	tw.tween_property(self, "rotation:x", 0.0, 0.12)


func _on_died(_attacker: Node) -> void:
	_play("death")
	_reset_in = RESET_TIME
	downed.emit(self)
