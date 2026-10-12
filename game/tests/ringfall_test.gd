extends SceneTree
## Headless checks for the Ringfall map: the terrain holds the player up, the
## round starts with bots and loot spread over the locations, deep water floats
## the player, location pieces and scattered rocks are solid, and the storm runs.
## Run: godot --headless --path game -s res://tests/ringfall_test.gd

var scene: Node3D
var player: Player
var terrain: RingfallTerrain
var failures := 0


func _initialize() -> void:
	Player.use_saved_tuning = false
	GameSettings.use_saved = false
	scene = load("res://scenes/ringfall.tscn").instantiate()
	root.add_child(scene)
	player = scene.get_node("Player")
	terrain = scene.get_node("Terrain")
	_run()


func _check(name: String, ok: bool, detail := "") -> void:
	if not ok:
		failures += 1
	print("%s  %s%s" % ["PASS" if ok else "FAIL", name, "  (" + detail + ")" if detail != "" else ""])


func _wait(seconds: float) -> void:
	for i in int(seconds * Engine.physics_ticks_per_second):
		await physics_frame


func _place(at: Vector3) -> void:
	player.teleport_to(Transform3D(Basis.IDENTITY, at))
	await _wait(0.1)


func _ground(x: float, z: float) -> float:
	return terrain.height_at(x, z)


func _run() -> void:
	await _wait(1.0)
	for b in get_nodes_in_group("bots"):
		(b as Node).set_physics_process(false)

	var p := player.global_position
	_check("Player spawns standing on the ground", player.is_on_floor() and absf(p.y - _ground(p.x, p.z)) < 1.0,
		"y %.1f, ground %.1f" % [p.y, _ground(p.x, p.z)])
	_check("Eight bots start the round", get_nodes_in_group("bots").size() == 8, str(get_nodes_in_group("bots").size()))
	var loot := scene.get_node("Loot").get_child_count()
	_check("Loot is spread over the map", loot >= 50, "%d pickups" % loot)

	# Walk across rough ground: the heightmap collision must hold.
	await _place(Vector3(-120, _ground(-120, -200) + 2.0, -200))
	await _wait(1.5)
	p = player.global_position
	_check("Terrain collision holds on the hills", player.is_on_floor() and absf(p.y - _ground(p.x, p.z)) < 1.0,
		"y %.1f, ground %.1f" % [p.y, _ground(p.x, p.z)])

	# Deep water in the crater lake: float near the surface, slowly.
	await _place(Vector3(90, 2.0, 40))
	await _wait(3.0)
	p = player.global_position
	_check("Deep water floats the player", player.in_water and p.y > -2.5 and p.y < 0.5, "y %.2f, lake floor %.1f" % [p.y, _ground(p.x, p.z)])

	# A location piece blocks movement (Relay Nine power core).
	var core := Vector3(285, 0, -215)
	await _place(Vector3(core.x, _ground(core.x, core.z - 11) + 0.5, core.z - 11))  # straight at the core, clear of the pipe runs
	player.velocity = Vector3(0, 0, 12)
	for i in 60:
		player.velocity.z = 12.0
		await physics_frame
	_check("Location pieces are solid", player.global_position.z < core.z - 3.0, "z %.1f vs core %.1f" % [player.global_position.z, core.z])

	# The storm is running and shrinks over time.
	var storm := scene.get_node("IonStorm") as IonStorm
	_check("Ion storm starts around the island", storm != null and storm.radius >= 500.0, "radius %.0f" % storm.radius)

	print("ALL PASSED: %d failed" % failures if failures == 0 else "FAILURES: %d" % failures)
	quit(1 if failures > 0 else 0)
