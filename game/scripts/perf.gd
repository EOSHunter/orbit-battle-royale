extends Node
## Performance probe (autoload "Perf").
## - F3 toggles an on-screen frame-time readout.
## - A scripted benchmark visits fixed views of the playground and reports frame
##   time, CPU time, draw calls and triangles. Start it with `-- --bench` on
##   desktop, or by opening the web build with `#bench` at the end of the URL.
##   Results print as a `BENCH {...}` line and, on the web, land in
##   `window.orbitPerf` for tools to read.

const WARMUP := 1.0
const SAMPLE_SECONDS := 3.0

var _label: Label
var _frames: PackedFloat32Array = []
var _refresh := 0.0
var _first_frame_done := false
var _web := OS.has_feature("web")


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var layer := CanvasLayer.new()
	layer.layer = 100
	add_child(layer)
	_label = Label.new()
	_label.visible = GameSettings.b("show_fps")
	GameSettings.listen(func(id: String) -> void:
		if id == "" or id == "show_fps":
			_label.visible = GameSettings.b("show_fps"))
	_label.add_theme_font_size_override("font_size", 15)
	_label.add_theme_color_override("font_color", Color("c5f277"))
	_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
	_label.add_theme_constant_override("shadow_offset_y", 1)
	_label.anchor_left = 1.0
	_label.anchor_right = 1.0
	_label.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_label.offset_left = -24
	_label.offset_right = -24
	_label.offset_top = 24
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	layer.add_child(_label)
	if _bench_requested():
		_run_bench.call_deferred()


func _bench_requested() -> bool:
	if "--bench" in OS.get_cmdline_user_args():
		return true
	if _web:
		return str(JavaScriptBridge.eval("location.hash")) == "#bench"
	return false


func _unhandled_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key and key.pressed and not key.echo and key.physical_keycode == KEY_F3:
		GameSettings.set_value("show_fps", not _label.visible)


func _process(delta: float) -> void:
	if not _first_frame_done:
		_first_frame_done = true
		var info := {"engineStartToFirstFrameMs": Time.get_ticks_msec()}
		if _web:
			info["pageLoadToFirstFrameMs"] = float(JavaScriptBridge.eval("performance.now()"))
		_publish("firstFrame", info)
		print("FIRST_FRAME ", JSON.stringify(info))
	_frames.append(delta * 1000.0)
	if _frames.size() > 240:
		_frames = _frames.slice(_frames.size() - 240)
	_refresh -= delta
	if _label.visible and _refresh <= 0.0:
		_refresh = 0.25
		var s := _stats(_frames)
		_label.text = "%.0f fps · %.1f ms avg · %.1f ms worst\nCPU %.1f ms · %d draw calls · %dk triangles" % [
			s.fps, s.avg, s.max, _cpu_ms(),
			Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
			int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME) / 1000.0)]


## Main-thread time for the last frame (scripts, scene and render submission).
func _cpu_ms() -> float:
	return Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0


func _stats(samples: PackedFloat32Array) -> Dictionary:
	if samples.is_empty():
		return {"avg": 0.0, "p95": 0.0, "max": 0.0, "fps": 0.0}
	var sorted := samples.duplicate()
	sorted.sort()
	var total := 0.0
	for v in sorted:
		total += v
	var avg := total / sorted.size()
	return {
		"avg": snappedf(avg, 0.01),
		"p95": snappedf(sorted[int(sorted.size() * 0.95)], 0.01),
		"max": snappedf(sorted[-1], 0.01),
		"fps": snappedf(1000.0 / avg, 0.1),
	}


func _publish(key: String, value: Variant) -> void:
	if _web:
		JavaScriptBridge.eval("window.orbitPerf = window.orbitPerf || {}; window.orbitPerf[%s] = %s;" % [JSON.stringify(key), JSON.stringify(value)])


func _run_bench() -> void:
	var tree := get_tree()
	if not _web:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	# The benchmark views are positions in the movement playground.
	if tree.current_scene == null or tree.current_scene.name != "Playground":
		tree.change_scene_to_file("res://scenes/playground.tscn")
		await tree.process_frame
		await tree.process_frame
	await tree.create_timer(WARMUP).timeout
	var scene := tree.current_scene
	var player := scene.get_node_or_null("Player") as Player
	if player == null:
		push_error("Benchmark needs the playground scene")
		return
	var views := [
		{"name": "Spawn lane", "at": Vector3(0, 0.05, 8), "look": Vector3(0, 1.6, -40)},
		{"name": "Tower field", "at": Vector3(-10, 0.05, 10), "look": Vector3(-50, 10, -40)},
		{"name": "Course overview from the 50 m tower", "at": Vector3(-74, 50.05, -64), "look": Vector3(10, 0, -30)},
		{"name": "Swing gap, tethered", "at": Vector3(40, 12.05, -14), "look": Vector3(40, 29.25, -47.5), "tether": true},
	]
	var results := []
	for v: Dictionary in views:
		player.teleport_to(Transform3D(Basis.IDENTITY, v.at))
		await tree.create_timer(0.3).timeout
		var d: Vector3 = v.look - player.camera.global_position
		player.rotation.y = atan2(-d.x, -d.z)
		player.head.rotation.x = atan2(d.y, Vector2(d.x, d.z).length())
		await tree.process_frame
		if v.get("tether", false):
			player.tether.try_attach()
		await tree.create_timer(0.5).timeout
		var frames: PackedFloat32Array = []
		var cpu := 0.0
		var draws := 0.0
		var tris := 0.0
		var t := 0.0
		while t < SAMPLE_SECONDS:
			await tree.process_frame
			var dt := get_process_delta_time()
			t += dt
			frames.append(dt * 1000.0)
			cpu += _cpu_ms()
			draws += Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
			tris += Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
		var s := _stats(frames)
		var n := float(frames.size())
		s["view"] = v.name
		s["cpuMs"] = snappedf(cpu / n, 0.01)
		s["drawCalls"] = int(draws / n)
		s["triangles"] = int(tris / n)
		results.append(s)
	var report := {
		"platform": OS.get_name() + (" (web)" if _web else ""),
		"renderer": RenderingServer.get_video_adapter_name(),
		"window": "%dx%d" % [get_viewport().get_visible_rect().size.x, get_viewport().get_visible_rect().size.y],
		"vsync": "browser-locked" if _web else "off",
		"views": results,
		"staticMemoryMB": snappedf(Performance.get_monitor(Performance.MEMORY_STATIC) / 1048576.0, 0.1),
	}
	print("BENCH ", JSON.stringify(report))
	_publish("bench", report)
	if "--bench" in OS.get_cmdline_user_args():
		tree.quit()
