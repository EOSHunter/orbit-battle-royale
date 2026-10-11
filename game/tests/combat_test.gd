extends SceneTree
## Headless checks for the combat slice, driving the real arena scene:
## looting, firing, damage and elimination, reloading, healing and its
## interruption, and bot perception (line of sight, no shooting through walls).
## Run: godot --headless --path game -s res://tests/combat_test.gd

var scene: Node3D
var player: Player
var failures := 0


func _initialize() -> void:
	scene = load("res://scenes/arena.tscn").instantiate()
	root.add_child(scene)
	player = scene.get_node("Player")
	_run()


func _check(name: String, ok: bool, detail := "") -> void:
	if not ok:
		failures += 1
	print("%s  %s%s" % ["PASS" if ok else "FAIL", name, "  (" + detail + ")" if detail != "" else ""])


func _wait(seconds: float) -> void:
	for i in int(seconds * Engine.physics_ticks_per_second):
		await physics_frame


func _bots() -> Array[Bot]:
	var out: Array[Bot] = []
	for b in get_nodes_in_group("bots"):
		var bot := b as Bot
		if bot.mode != Bot.Mode.DEAD:
			out.append(bot)
	return out


func _freeze_bots() -> void:
	for b in _bots():
		b.set_physics_process(false)


func _aim_at(point: Vector3) -> void:
	var d := point - player.camera.global_position
	player.rotation.y = atan2(-d.x, -d.z)
	player.head.rotation.x = atan2(d.y, Vector2(d.x, d.z).length())


func _place_player(at: Vector3) -> void:
	player.teleport_to(Transform3D(Basis.IDENTITY, at))
	await _wait(0.3)


func _run() -> void:
	await _wait(0.5)
	_freeze_bots()
	var inv := player.inventory
	_check("Starts with only the Tethercaster", inv.has_item(&"tethercaster") and inv.get_slot(0) == null)

	# Looting: walking over the AR-7 and the ammo picks them up.
	await _place_player(Vector3(-3, 0.05, 50))
	await _place_player(Vector3(3, 0.05, 50))
	_check("Walking over the AR-7 picks it up into slot 1", inv.get_slot(0) and inv.get_slot(0).def.id == &"ar7")
	_check("Walking over ammo fills the reserve", inv.ammo_count(&"medium") == 90, "%d medium" % inv.ammo_count(&"medium"))
	await _place_player(Vector3(0, 0.05, 46))
	_check("Shield Cells go to an item slot", inv.count(&"shield_cell") == 2)

	# Shooting a bot until it is eliminated.
	# Open lane along the west side: nothing between z = 55 and z = -40 at x = -60.
	await _place_player(Vector3(-60, 0.05, 50))
	inv.select(0)
	await _wait(0.6)
	var bot: Bot = _bots()[0]
	bot.global_position = Vector3(-60, 0.1, 35)
	await _wait(0.2)
	var start_hp := bot.health.health + bot.health.shield
	var hits := [0]
	player.weapons.hit_confirmed.connect(func(_d: float, _k: bool) -> void: hits[0] += 1)
	var eliminated := [false]
	bot.eliminated.connect(func(_b: Bot, by: Node) -> void: eliminated[0] = by == player)
	_aim_at(bot.global_position + Vector3(0, 1.2, 0))
	var mag_before := inv.get_slot(0).mag
	Input.action_press("fire")
	for i in 120:
		await physics_frame
		_aim_at(bot.global_position + Vector3(0, 1.2, 0))
		if eliminated[0]:
			break
	Input.action_release("fire")
	_check("Automatic fire uses rounds", inv.get_slot(0).mag < mag_before, "%d → %d" % [mag_before, inv.get_slot(0).mag])
	_check("Shots hit and damage the bot", hits[0] > 0, "%d hits on %d health+shield" % [hits[0], int(start_hp)])
	_check("The bot is eliminated and credited to the player", eliminated[0])
	await _wait(0.2)
	var drops := 0
	for p in get_nodes_in_group(Pickup.GROUP):
		if (p as Pickup).global_position.distance_to(bot.global_position) < 2.0:
			drops += 1
	_check("Eliminated bot drops its loot", drops >= 2, "%d pickups" % drops)

	# Reloading draws from the reserve.
	var s := inv.get_slot(0)
	var reserve := inv.ammo_count(&"medium")
	var missing := 30 - s.mag
	_check("Reload starts", player.weapons.start_reload())
	await _wait(2.1)
	_check("Reload fills the magazine from the reserve", s.mag == 30 and inv.ammo_count(&"medium") == reserve - missing, "mag %d, reserve %d → %d" % [s.mag, reserve, inv.ammo_count(&"medium")])

	# Healing: completes after its use time, interrupted by damage keeps the item.
	player.health.shield = 0.0
	player.health.health = 40.0
	var cell_slot := inv.slot_of(&"shield_cell")
	inv.select(cell_slot)
	_check("Healing starts", player.start_use(cell_slot))
	await _wait(2.2)
	_check("Shield Cell restores 25 shields when the timer completes", is_equal_approx(player.health.shield, 25.0) and inv.count(&"shield_cell") == 1, "shield %.0f, cells %d" % [player.health.shield, inv.count(&"shield_cell")])
	player.start_use(cell_slot)
	await _wait(0.6)
	player.health.take_damage(5.0, player.global_position + Vector3(10, 0, 0))
	_check("Damage interrupts healing", player.using == null)
	await _wait(2.0)
	_check("An interrupted heal keeps the item", inv.count(&"shield_cell") == 1 and player.health.shield < 25.0)
	player.health.shield = 100.0
	player.health.health = 100.0
	_check("A full pool refuses its healing item", not player.start_use(cell_slot))

	# Bot perception: no line of sight through a wall, and it fights when it can see.
	var b2: Bot = _bots()[0]
	b2.set_physics_process(true)
	b2.mode = Bot.Mode.PATROL
	await _place_player(Vector3(0, 0.05, 46))
	b2.global_position = Vector3(0, 0.1, 34)
	b2.rotation.y = PI
	await _wait(0.1)
	b2.set_physics_process(false)
	b2._perceive()
	_check("A bot can't see through the tall wall", not b2._has_los)
	await _place_player(Vector3(-60, 0.05, 50))
	b2.global_position = Vector3(-60, 0.1, 28)
	b2.look_at(Vector3(player.global_position.x, b2.global_position.y, player.global_position.z))
	await physics_frame
	b2._perceive()
	_check("A bot with a clear line sees the player", b2._has_los)
	var hp_before := player.health.health + player.health.shield
	# Start it looking and walking toward the player, so its next look finds them.
	b2._think = 0.0
	b2._goal = player.global_position
	b2.set_physics_process(true)
	# Its aim is imperfect by design, so give it up to 12 s to land a hit.
	for i in 12 * Engine.physics_ticks_per_second:
		await physics_frame
		if player.health.health + player.health.shield < hp_before:
			break
	_check("A bot that sees the player engages and deals damage", player.health.health + player.health.shield < hp_before, "%.0f → %.0f" % [hp_before, player.health.health + player.health.shield])

	print("\n%s: %d failed" % ["ALL PASSED" if failures == 0 else "FAILURES", failures])
	quit(1 if failures else 0)
