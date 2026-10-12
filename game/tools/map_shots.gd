extends SceneTree
## Screenshots of a map scene from named viewpoints, for reviewing the layout
## in the real renderer. Needs a window (not --headless):
##   godot --path game -s res://tools/map_shots.gd -- <out_dir> [scene] [view ...]
## Views are "name:x,y,z:tx,ty,tz" (camera position and target); a default set
## covers the whole island and each location.

const DEFAULT_VIEWS := [
	"overview:0,620,560:0,0,40",
	"glass-basin:-120,60,-110:10,4,-5",
	"crown-observatory:-220,90,-160:-315,44,-255",
	"the-spine:160,70,-200:115,40,-322",
	"relay-nine:200,60,-120:285,15,-215",
	"bloomwild:-220,40,140:-320,6,70",
	"anchorport:100,40,230:15,3,330",
	"hollow-array:200,70,140:278,20,228",
]


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var out_dir: String = args[0] if args.size() > 0 else OS.get_user_data_dir()
	var scene_path: String = args[1] if args.size() > 1 else "res://scenes/ringfall.tscn"
	var views: Array = args.slice(2) if args.size() > 2 else DEFAULT_VIEWS
	DirAccess.make_dir_recursive_absolute(out_dir)
	root.size = Vector2i(1280, 720)
	var scene := (load(scene_path) as PackedScene).instantiate()
	# Keep the gameplay from running: only the world is wanted.
	for n in ["Player", "HUD", "InventoryScreen"]:
		var node := scene.get_node_or_null(n)
		if node:
			node.queue_free()
	root.add_child(scene)
	var cam := Camera3D.new()
	cam.fov = 70
	cam.far = 4000
	root.add_child(cam)
	cam.make_current()
	for v: String in views:
		var parts := v.split(":")
		var p := parts[1].split_floats(",")
		var t := parts[2].split_floats(",")
		cam.position = Vector3(p[0], p[1], p[2])
		cam.look_at_from_position(Vector3(p[0], p[1], p[2]), Vector3(t[0], t[1], t[2]))
		for i in 6:
			await process_frame
		await RenderingServer.frame_post_draw
		var path := out_dir.path_join(parts[0] + ".png")
		root.get_texture().get_image().save_png(path)
		print("SHOT ", path)
	quit()
