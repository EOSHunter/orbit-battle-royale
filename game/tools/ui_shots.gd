extends SceneTree
## Screenshots of every menu screen and the HUD at 1920×1080 in the real
## renderer, for comparing against the menu designs. Needs a window:
##   godot --path game -s res://tools/ui_shots.gd -- <out_dir>


func _initialize() -> void:
	_run()


func _frames(n: int) -> void:
	for i in n:
		await process_frame


func _shot(out_dir: String, name: String) -> void:
	await _frames(24)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_jpg("%s/%s.jpg" % [out_dir, name], 0.88)
	print("SHOT ", name)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var out_dir: String = args[0] if args.size() > 0 else OS.get_user_data_dir()
	DirAccess.make_dir_recursive_absolute(out_dir)
	Player.use_saved_tuning = false
	GameSettings.use_saved = false
	DisplayServer.window_set_size(Vector2i(1920, 1080))
	root.size = Vector2i(1920, 1080)
	for a: Array in [["Controls", "res://scripts/controls.gd"], ["MouseLockTicker", "res://scripts/mouse_lock.gd"], ["MenuLayer", "res://scripts/ui/menus.gd"]]:
		if root.get_node_or_null(a[0]) == null:
			var n: Node = load(a[1]).new()
			n.name = a[0]
			root.add_child(n)
	await _frames(3)

	var main: Control = load("res://scenes/main_menu.tscn").instantiate()
	root.add_child(main)
	await _shot(out_dir, "01-lobby")
	main.call("_show_tab", 1)
	await _shot(out_dir, "02-training")
	Menus.push(SettingsScreen.new())
	await _shot(out_dir, "03-settings-mouse")
	var s := Menus.top()
	s.call("_show_category", 3)
	await _shot(out_dir, "04-settings-video")
	s.call("_show_category", 0)
	s.set("_sec", 2)
	s.call("_build_rows")
	await _shot(out_dir, "05-settings-bindings")
	Menus.pop()
	Menus.push(LearnControls.new())
	await _shot(out_dir, "06-learn-controls")
	Menus.pop()
	Menus.push(CallsignDialog.new(func(_n: String) -> void: pass))
	await _shot(out_dir, "07-callsign")
	Menus.clear()
	main.queue_free()

	var loading: Control = load("res://scripts/ui/screens/loading_screen.gd").new()
	root.add_child(loading)
	await _shot(out_dir, "08-loading")
	loading.queue_free()

	var range_scene: Node3D = load("res://scenes/firing_range.tscn").instantiate()
	root.add_child(range_scene)
	await _frames(10)
	var player := range_scene.get_node("Player") as Player
	player.weapons.hit_detail.emit(24.0, "shield")
	player.weapons.hit_detail.emit(24.0, "break")
	await _shot(out_dir, "09-hud-range")
	(range_scene.get_node("InventoryScreen") as CanvasLayer).call("open")
	await _shot(out_dir, "10-inventory")
	(range_scene.get_node("InventoryScreen") as CanvasLayer).call("close")
	GameMenu.open("Firing range", true)
	await _shot(out_dir, "11-match-menu")
	Menus.push(AnalyticsPanel.new(true))
	await _shot(out_dir, "12-analytics")
	Menus.pop()
	Menus.push(ReportScreen.new("Firing range"))
	await _shot(out_dir, "13-report")
	Menus.pop()
	Menus.top().call("_confirm_leave")
	await _shot(out_dir, "14-leave-dialog")
	Menus.clear()
	Menus.push(ResultsScreen.new(true, 1, 9, "", func() -> void: pass))
	await _frames(80)
	await _shot(out_dir, "15-results")
	quit()
