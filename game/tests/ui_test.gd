extends SceneTree
## Headless checks for the menus: the main menu builds, every settings
## category and section builds, settings change and apply, rebinding moves a
## key between actions, the guide steps through, the in-match menu, stats,
## report and leave-confirmation open over the firing range, and Esc closes
## one layer at a time.
## Run: godot --headless --path game -s res://tests/ui_test.gd

var failures := 0


func _initialize() -> void:
	Player.use_saved_tuning = false
	GameSettings.use_saved = false
	_run()


func _check(name: String, ok: bool, detail := "") -> void:
	if not ok:
		failures += 1
	print("%s  %s%s" % ["PASS" if ok else "FAIL", name, "  (" + detail + ")" if detail != "" else ""])


func _frames(n := 3) -> void:
	for i in n:
		await process_frame


func _esc() -> void:
	var e := InputEventAction.new()
	e.action = "ui_cancel"
	e.pressed = true
	root.push_input(e)
	await _frames(2)


func _run() -> void:
	await _frames(2)
	# Script runs (-s) may start without autoloads; add the ones menus need.
	for a: Array in [["Controls", "res://scripts/controls.gd"], ["MouseLockTicker", "res://scripts/mouse_lock.gd"], ["MenuLayer", "res://scripts/ui/menus.gd"]]:
		if root.get_node_or_null(a[0]) == null:
			var n: Node = load(a[1]).new()
			n.name = a[0]
			root.add_child(n)
	await _frames(2)
	_check("Menu layer is running", root.get_node_or_null("MenuLayer") != null and not Menus.is_open())

	# Main menu.
	var main: Control = load("res://scenes/main_menu.tscn").instantiate()
	root.add_child(main)
	await _frames(3)
	_check("Main menu builds", main.get_child_count() > 3)

	# Settings: every category and section.
	var settings := SettingsScreen.new()
	Menus.push(settings)
	await _frames(2)
	_check("Settings opens on the menu stack", Menus.top() == settings)
	var rows := 0
	for c in GameSettings.CATEGORIES.size():
		settings.call("_show_category", c)
		var sections: Array = GameSettings.CATEGORIES[c].sections
		for s in sections.size():
			settings.set("_sec", s)
			settings.call("_build_rows")
			await _frames(1)
			for r in (settings.get("_rows_box") as Node).get_children():
				if r is SettingRow:
					rows += 1
	_check("Every settings row builds", rows == GameSettings.ROWS.size(), "%d of %d" % [rows, GameSettings.ROWS.size()])

	GameSettings.set_value("fov", 95)
	_check("FOV setting applies", is_equal_approx(GameSettings.f("fov"), 95.0))
	GameSettings.set_value("fov", 500)
	_check("Sliders clamp to their range", is_equal_approx(GameSettings.f("fov"), 120.0))
	GameSettings.set_value("res3d", 70)
	_check("3D resolution applies to the viewport", is_equal_approx(root.scaling_3d_scale, 0.7))
	GameSettings.set_value("preset", "Low")
	_check("Quality preset sets the graphics rows", GameSettings.s("shadows") == "Low" and GameSettings.s("foliage") == "Low")
	GameSettings.set_value("shadows", "High")
	_check("Changing a graphics row makes the preset Custom", GameSettings.s("preset") == "Custom")
	GameSettings.set_value("vol_music", 0)
	_check("Music bus exists and mutes at 0%", AudioServer.get_bus_index("Music") >= 0 and AudioServer.is_bus_mute(AudioServer.get_bus_index("Music")))

	# Rebinding: put Jump on R; Reload loses R.
	var r_key := InputEventKey.new()
	r_key.physical_keycode = KEY_R
	var took := GameSettings.rebind("jump", 0, r_key)
	_check("Rebinding moves a key from another action", took == "Reload" and GameSettings.key_for("jump") == "R", "took from '%s'" % took)
	GameSettings.reset_category("mk")
	_check("Restore defaults puts bindings back", GameSettings.key_for("jump") == "Space" and GameSettings.key_for("reload") == "R")

	await _esc()
	_check("Esc closes settings", not Menus.is_open())

	# Learn controls.
	var guide := LearnControls.new()
	Menus.push(guide)
	await _frames(2)
	for i in LearnControls.STEPS.size():
		guide.call("_go", i)
	await _frames(1)
	_check("The guide steps through every step", guide.get("_step") == LearnControls.STEPS.size() - 1)
	await _esc()
	_check("Esc closes the guide", not Menus.is_open())
	main.queue_free()
	await _frames(2)

	# Firing range with the in-match menu.
	var range_scene: Node3D = load("res://scenes/firing_range.tscn").instantiate()
	root.add_child(range_scene)
	await _frames(5)
	var targets := get_nodes_in_group("targets")
	_check("Firing range builds targets", targets.size() == 12, "%d targets" % targets.size())
	var player := range_scene.get_node("Player") as Player
	_check("Range loadout has both weapons", player.inventory.has_item(&"ar7") and player.inventory.has_item(&"sg4"))
	var t := targets[0] as TargetDummy
	t.health.take_damage(500.0, Vector3.ZERO, player)
	await _frames(2)
	_check("A target goes down", not t.health.alive)

	GameMenu.open("Firing range", true)
	await _frames(2)
	var gm := Menus.top()
	_check("In-match menu opens", gm is GameMenu)
	_check("Player input stops under the menu", not player.combat_input)
	Menus.push(AnalyticsPanel.new(true))
	await _frames(2)
	_check("Practice analytics show over the menu", Menus.top() is AnalyticsPanel and gm.visible)
	await _esc()
	_check("Esc leaves analytics first", Menus.top() == gm)
	Menus.push(ReportScreen.new("Firing range"))
	await _frames(2)
	_check("Report a problem opens over the menu", Menus.top() is ReportScreen)
	await _esc()
	_check("Esc returns to the menu", Menus.top() == gm)
	gm.call("_confirm_leave")
	await _frames(2)
	_check("Leave match asks for confirmation", Menus.top() is ConfirmDialog)
	await _esc()
	await _esc()
	_check("Esc twice resumes the match", not Menus.is_open() and player.combat_input)

	var results := ResultsScreen.new(false, 4, 9, "Bot Rhea", func() -> void: pass)
	Menus.push(results)
	await _frames(2)
	_check("Results screen opens", Menus.top() == results)
	await _esc()
	_check("Esc doesn't dismiss the results", Menus.top() == results)
	Menus.clear()

	print("ALL PASSED: %d failed" % failures if failures == 0 else "FAILED: %d failed" % failures)
	quit(1 if failures > 0 else 0)
