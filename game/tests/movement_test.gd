extends SceneTree
## Headless behaviour checks for the movement playground. Drives the real
## scene with simulated input and prints PASS/FAIL per check.
## Run: godot --headless --path game -s res://tests/movement_test.gd

var scene: Node3D
var player: Player
var failures := 0
var _drops: Array[float] = []


func _initialize() -> void:
	Player.use_saved_tuning = false
	scene = load("res://scenes/playground.tscn").instantiate()
	root.add_child(scene)
	player = scene.get_node("Player")
	player.landed.connect(func(drop: float, _s: float) -> void: _drops.append(drop))
	_run()


func _check(name: String, ok: bool, detail := "") -> void:
	if not ok:
		failures += 1
	print("%s  %s%s" % ["PASS" if ok else "FAIL", name, "  (" + detail + ")" if detail != "" else ""])


func _wait(seconds: float) -> void:
	var frames := int(seconds * Engine.physics_ticks_per_second)
	for i in frames:
		await physics_frame


func _place(at: Vector3, look_at_point: Vector3) -> void:
	player.teleport_to(Transform3D(Basis.IDENTITY, at))
	await _wait(0.6)
	var eye := player.camera.global_position
	var d := look_at_point - eye
	player.rotation.y = atan2(-d.x, -d.z)
	player.head.rotation.x = atan2(d.y, Vector2(d.x, d.z).length())
	await _wait(0.1)


func _hold(actions: Array, seconds: float) -> void:
	for a: String in actions:
		Input.action_press(a)
	await _wait(seconds)
	for a: String in actions:
		Input.action_release(a)


func _run() -> void:
	await _wait(1.0)
	_check("Spawns standing on the ground", player.is_on_floor(), "y=%.2f" % player.global_position.y)

	# Walking and sprinting reach their tuned speeds.
	await _place(Vector3(0, 0.05, 8), Vector3(0, 1.6, -40))
	await _hold(["move_forward"], 1.2)
	var walk := player.horizontal_speed()
	_check("Walk speed reaches tuning", absf(walk - player.tuning.walk_speed) < 0.3, "%.2f m/s" % walk)
	await _place(Vector3(0, 0.05, 8), Vector3(0, 1.6, -40))
	await _hold(["move_forward", "sprint"], 1.2)
	var sprint := player.horizontal_speed()
	_check("Sprint speed reaches tuning", absf(sprint - player.tuning.sprint_speed) < 0.3, "%.2f m/s" % sprint)

	# Jump height matches v² / 2g.
	await _place(Vector3(0, 0.05, 8), Vector3(0, 1.6, -40))
	var start_y := player.global_position.y
	Input.action_press("jump")
	await _wait(0.05)
	Input.action_release("jump")
	var peak := start_y
	for i in 90:
		await physics_frame
		peak = maxf(peak, player.global_position.y)
	var expected := pow(player.tuning.jump_velocity, 2) / (2.0 * player.tuning.gravity)
	_check("Jump height matches tuning", absf((peak - start_y) - expected) < 0.12, "%.2f m, expected %.2f" % [peak - start_y, expected])

	# Hook eligibility: in range, out of range, not hookable.
	await _place(Vector3(0, 0.05, -60), Vector3(-7, 6, -99.5))
	_check("40 m wall reads as in range", player.tether.aim == Tethercaster.Aim.IN_RANGE, "%.1f m" % player.tether.aim_distance)
	await _place(Vector3(0, 0.05, -60), Vector3(7, 6, -124.5))
	_check("65 m wall reads as out of range", player.tether.aim == Tethercaster.Aim.OUT_OF_RANGE, "%.1f m" % player.tether.aim_distance)
	await _place(Vector3(20, 0.05, -18), Vector3(20, 5, -30))
	_check("Glass can be hooked", player.tether.aim == Tethercaster.Aim.IN_RANGE and player.tether.try_attach())
	player.tether.reset()
	await _place(Vector3(0, 0.05, 8), Vector3(0, 0, -6))
	_check("The ground can be hooked", player.tether.aim == Tethercaster.Aim.IN_RANGE and player.tether.try_attach())
	player.tether.reset()

	# Swing across the gap: hook the beam, ride the rope, release with a jump.
	_drops.clear()
	await _place(Vector3(40, 12.05, -14), Vector3(40, 29.25, -47.5))
	var attached := player.tether.try_attach()
	_check("Tether attaches to the swing beam", attached, "%.1f m" % player.tether.rope_length)
	var start_rope := player.tether.rope_length
	await _wait(1.6)
	_check("Rope reels in", player.tether.rope_length < start_rope - 5.0, "%.1f → %.1f m" % [start_rope, player.tether.rope_length])
	_check("Player is carried over the gap", player.global_position.z < -32.0, "z=%.1f" % player.global_position.z)
	var speed_before := player.velocity.length()
	Input.action_press("jump")
	await physics_frame
	await physics_frame
	Input.action_release("jump")
	_check("Jump releases the tether", not player.tether.is_attached())
	_check("Release starts the recharge", player.tether.cooldown_left > 0.0, "%.1f s" % player.tether.cooldown_left)
	await _wait(0.1)
	_check("Momentum carries after release", player.velocity.length() > speed_before * 0.7, "%.1f → %.1f m/s" % [speed_before, player.velocity.length()])
	_check("Can't re-fire while recharging", not player.tether.try_attach())
	await _wait(4.0)
	_check("Lands after the swing", player.is_on_floor(), "at z=%.1f y=%.1f" % [player.global_position.z, player.global_position.y])
	_check("Tether recharged", player.tether.charge() >= 1.0)

	# No fall damage: walk off the 50 m tower.
	_drops.clear()
	await _place(Vector3(-74, 50.05, -64), Vector3(-74, 50, -90))
	await _hold(["move_forward"], 4.0)
	await _wait(1.0)
	var drop: float = _drops.max() if not _drops.is_empty() else 0.0
	_check("50 m drop lands with no damage", drop > 45.0 and player.is_on_floor(), "drop %.1f m" % drop)

	# Respawn returns to the last teleport marker.
	Input.action_press("respawn")
	await physics_frame
	await physics_frame
	Input.action_release("respawn")
	await _wait(0.2)
	_check("Respawn works", player.global_position.distance_to(Vector3(0, 0.05, -58)) < 2.0 or player.global_position.distance_to(Vector3(0, 0.05, 8)) < 2.0, str(player.global_position))

	print("\n%s: %d failed" % ["ALL PASSED" if failures == 0 else "FAILURES", failures])
	quit(1 if failures else 0)
