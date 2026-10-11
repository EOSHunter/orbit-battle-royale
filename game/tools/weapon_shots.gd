extends SceneTree
## Saves first-person and pickup screenshots of every item with a model, for
## reviewing art in the real renderer. Needs a window (not --headless):
##   godot --path game -s res://tools/weapon_shots.gd -- <out_dir>

const ITEMS := [&"ar7", &"sg4"]
const EXTRA_MODELS := [
	"res://assets/models/weapons/p-12-spark.glb",
	"res://assets/models/weapons/s-9-wisp.glb",
	"res://assets/models/weapons/sr-8-longview.glb",
]


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var out_dir: String = args[0] if args.size() > 0 else OS.get_user_data_dir()
	DirAccess.make_dir_recursive_absolute(out_dir)
	root.size = Vector2i(1280, 720)

	var world := Node3D.new()
	root.add_child(world)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color("1b2333")
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color("8090b0")
	env.environment.ambient_light_energy = 0.6
	world.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-40, 30, 0)
	world.add_child(sun)
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(40, 40)
	floor_mesh.mesh = plane
	world.add_child(floor_mesh)

	var cam := Camera3D.new()
	cam.fov = 110
	cam.position = Vector3(0, 1.6, 3)
	world.add_child(cam)
	cam.make_current()

	var hud := CanvasLayer.new()
	root.add_child(hud)
	var dot := ColorRect.new()
	dot.color = Color(1, 0.2, 0.2)
	dot.size = Vector2(3, 3)
	dot.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	dot.visible = false
	hud.add_child(dot)

	for id: StringName in ITEMS:
		var def := ItemCatalog.get_def(id)
		var vm := Viewmodels.build(def)
		cam.add_child(vm)
		Viewmodels.fit_fov(vm, cam.fov)
		Viewmodels.pose(vm, def, 0.0)
		await _save(out_dir.path_join("view_%s.png" % id))
		cam.fov = 110.0 * (def as WeaponDef).aim_fov_scale
		Viewmodels.fit_fov(vm, cam.fov)
		Viewmodels.pose(vm, def, 1.0)
		dot.visible = true
		await _save(out_dir.path_join("ads_%s.png" % id))
		dot.visible = false
		cam.fov = 110.0
		vm.queue_free()

	# Pickup-style close-ups of every model, side on.
	cam.fov = 40
	var paths: Array[String] = []
	for id: StringName in ITEMS:
		paths.append(ItemCatalog.get_def(id).model_path)
	paths.append_array(EXTRA_MODELS)
	for path in paths:
		var model := (load(path) as PackedScene).instantiate() as Node3D
		world.add_child(model)
		model.position = Vector3(0, 1.6, 1.4)
		model.rotation_degrees = Vector3(0, -70, 0)
		await _save(out_dir.path_join("model_%s.png" % path.get_file().get_basename()))
		model.queue_free()
	quit()


func _save(path: String) -> void:
	for i in 4:
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(path)
	print("SHOT ", path)
