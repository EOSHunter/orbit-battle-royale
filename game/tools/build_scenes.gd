extends SceneTree
## Generates scenes/player.tscn and scenes/playground.tscn from code, so the
## greybox stays reviewable and reproducible. Scenes remain editable in Godot;
## re-running this overwrites them.
## Run: godot --headless --path game -s res://tools/build_scenes.gd

const GRID_SHADER := "res://shaders/grid.gdshader"
const WORLD_LAYER := 1
const GRAPPLE_LAYER := 2
const PLAYER_LAYER := 4

var _root: Node


func _initialize() -> void:
	_save(_build_player(), "res://scenes/player.tscn")
	_save(_build_playground(), "res://scenes/playground.tscn")
	quit()


func _save(root: Node, path: String) -> void:
	var scene := PackedScene.new()
	var err := scene.pack(root)
	if err == OK:
		err = ResourceSaver.save(scene, path)
	print("%s: %s" % [path, "saved" if err == OK else "FAILED (%d)" % err])
	root.free()


func _add(parent: Node, child: Node) -> Node:
	parent.add_child(child)
	child.owner = _root
	return child


# ---------------------------------------------------------------- materials

func _grid(base: Color, line: Color, accent := 0.0) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(GRID_SHADER)
	m.set_shader_parameter("base_color", base)
	m.set_shader_parameter("line_color", line)
	m.set_shader_parameter("accent_strength", accent)
	return m


func _unshaded(color: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = color
	if color.a < 1.0:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.disable_fog = true
	return m


func _solid(color: Color, rough := 0.6, metal := 0.2) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = rough
	m.metallic = metal
	return m


# ---------------------------------------------------------------- player

func _build_player() -> Node:
	var p := CharacterBody3D.new()
	_root = p
	p.name = "Player"
	p.set_script(load("res://scripts/player.gd"))
	p.collision_layer = PLAYER_LAYER
	p.collision_mask = WORLD_LAYER | GRAPPLE_LAYER
	p.floor_max_angle = deg_to_rad(46.0)
	p.floor_snap_length = 0.35

	var shape := CollisionShape3D.new()
	shape.name = "CollisionShape3D"
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.35
	capsule.height = 1.8
	shape.shape = capsule
	shape.position.y = 0.9
	_add(p, shape)

	var head := Node3D.new()
	head.name = "Head"
	head.position.y = 1.62
	_add(p, head)

	var cam := Camera3D.new()
	cam.name = "Camera3D"
	cam.near = 0.05
	cam.far = 9000.0
	cam.fov = 90.0
	_add(head, cam)

	# Placeholder Tethercaster launcher until the real viewmodel exists.
	var launcher := Node3D.new()
	launcher.name = "Launcher"
	launcher.position = Vector3(0.24, -0.22, -0.52)
	launcher.scale = Vector3(0.7, 0.7, 0.7)
	_add(cam, launcher)
	_mesh(launcher, "Body", BoxMesh, Vector3(0.07, 0.085, 0.32), Vector3.ZERO, _solid(Color("2b3550"), 0.45, 0.6))
	_mesh(launcher, "Stripe", BoxMesh, Vector3(0.072, 0.02, 0.1), Vector3(0, 0.03, -0.06), _unshaded(Color("c5f277")))
	_mesh(launcher, "Light", BoxMesh, Vector3(0.074, 0.012, 0.03), Vector3(0, 0.0, 0.08), _unshaded(Color("ffb45c")))

	var tether := Node3D.new()
	tether.name = "Tethercaster"
	tether.set_script(load("res://scripts/tethercaster.gd"))
	_add(cam, tether)

	var cable := MeshInstance3D.new()
	cable.name = "Cable"
	var cyl := CylinderMesh.new()
	cyl.top_radius = 0.018
	cyl.bottom_radius = 0.018
	cyl.height = 1.0
	cyl.radial_segments = 6
	cyl.rings = 1
	cable.mesh = cyl
	cable.material_override = _unshaded(Color("c5f277"))
	cable.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_add(tether, cable)

	var marker := MeshInstance3D.new()
	marker.name = "AnchorMarker"
	var sphere := SphereMesh.new()
	sphere.radius = 0.14
	sphere.height = 0.28
	marker.mesh = sphere
	marker.material_override = _unshaded(Color("c5f277"))
	marker.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_add(tether, marker)
	return p


func _mesh(parent: Node, n: String, kind, size: Vector3, pos: Vector3, mat: Material) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.name = n
	var m: BoxMesh = kind.new()
	m.size = size
	mi.mesh = m
	mi.position = pos
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_add(parent, mi)
	return mi


# ---------------------------------------------------------------- playground

var _course: Node3D
var _mat := {}


func _build_playground() -> Node:
	var root := Node3D.new()
	_root = root
	root.name = "Playground"
	root.set_script(load("res://scripts/playground.gd"))

	_mat = {
		"ground": _grid(Color("1d2338"), Color("3a4560")),
		"block": _grid(Color("3a4560"), Color("5a6a85")),
		"hook": _grid(Color("2b3550"), Color("4a5878"), 0.9),
		"glass": _glass(),
	}

	_environment(root)
	_sky(root)

	_course = Node3D.new()
	_course.name = "Course"
	_add(root, _course)
	_build_course()

	var markers := Node3D.new()
	markers.name = "Markers"
	_add(root, markers)
	# Order matters: keys 1–4 teleport to these in order.
	for m: Array in [["Spawn", Vector3(0, 0.05, 8)], ["Towers", Vector3(-30, 10.05, -20)], ["Gap", Vector3(40, 12.05, -14)], ["Range", Vector3(0, 0.05, -58)]]:
		var mk := Marker3D.new()
		mk.name = m[0]
		mk.position = m[1]
		_add(markers, mk)

	var player: Node = load("res://scenes/player.tscn").instantiate()
	player.name = "Player"
	_add(root, player)

	var hud := CanvasLayer.new()
	hud.name = "HUD"
	hud.set_script(load("res://scripts/hud.gd"))
	_add(root, hud)
	return root


func _glass() -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(0.44, 0.84, 1.0, 0.28)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.roughness = 0.05
	m.metallic = 0.3
	return m


func _environment(root: Node) -> void:
	var we := WorldEnvironment.new()
	we.name = "WorldEnvironment"
	var env := Environment.new()
	var sky := Sky.new()
	var mat := ProceduralSkyMaterial.new()
	mat.sky_top_color = Color("141a35")
	mat.sky_horizon_color = Color("6b5a8e")
	mat.ground_horizon_color = Color("3a2d56")
	mat.ground_bottom_color = Color("0b101b")
	mat.sun_angle_max = 20.0
	sky.sky_material = mat
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.9
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.fog_enabled = true
	env.fog_light_color = Color("6b5a8e")
	env.fog_density = 0.0012
	env.fog_sky_affect = 0.0
	we.environment = env
	_add(root, we)

	var sun := DirectionalLight3D.new()
	sun.name = "Sun"
	sun.rotation_degrees = Vector3(-48, -35, 0)
	sun.light_color = Color("ffe3c2")
	sun.light_energy = 1.25
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 120.0
	_add(root, sun)


func _sky(root: Node) -> void:
	# Veyra's rings: a flattened torus far away, plus the neighbouring planet.
	var sky := Node3D.new()
	sky.name = "SkyObjects"
	_add(root, sky)
	var rings := MeshInstance3D.new()
	rings.name = "Rings"
	var torus := TorusMesh.new()
	torus.inner_radius = 2900.0
	torus.outer_radius = 3700.0
	torus.rings = 128
	torus.ring_segments = 8
	rings.mesh = torus
	rings.scale = Vector3(1.0, 0.004, 1.0)
	rings.rotation_degrees = Vector3(16, 0, -14)
	rings.position = Vector3(0, -500, -2600)
	rings.material_override = _unshaded(Color(0.93, 0.9, 1.0, 0.5))
	rings.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_add(sky, rings)
	var planet := MeshInstance3D.new()
	planet.name = "Planet"
	var sphere := SphereMesh.new()
	sphere.radius = 700.0
	sphere.height = 1400.0
	planet.mesh = sphere
	var pm := StandardMaterial3D.new()
	pm.albedo_color = Color("3a2d6e")
	pm.emission_enabled = true
	pm.emission = Color("2a2350")
	pm.disable_fog = true
	planet.material_override = pm
	planet.position = Vector3(2400, 700, -5600)
	planet.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_add(sky, planet)


func _box(n: String, center: Vector3, size: Vector3, mat: String, hookable := false, rot := Vector3.ZERO, group := "") -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = n
	body.position = center
	body.rotation_degrees = rot
	body.collision_layer = GRAPPLE_LAYER if hookable else WORLD_LAYER
	body.collision_mask = 0
	if group != "":
		body.add_to_group(group, true)
	_add(_course, body)
	var mi := MeshInstance3D.new()
	mi.name = "Mesh"
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = _mat[mat]
	_add(body, mi)
	var cs := CollisionShape3D.new()
	cs.name = "Shape"
	var bs := BoxShape3D.new()
	bs.size = size
	cs.shape = bs
	_add(body, cs)
	return body


func _sign(text: String, pos: Vector3, size := 72) -> void:
	var l := Label3D.new()
	l.name = "Sign_" + text.validate_node_name().replace(" ", "_").left(24)
	l.text = text
	l.position = pos
	l.font_size = size
	l.pixel_size = 0.01
	l.outline_size = 12
	l.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	l.modulate = Color("f3f5fa")
	l.outline_modulate = Color(0.04, 0.06, 0.1, 0.9)
	_add(_course, l)


func _strip(pos: Vector3, size: Vector3, color: Color) -> void:
	var mi := MeshInstance3D.new()
	mi.name = "Strip"
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.position = pos
	mi.material_override = _unshaded(color)
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_add(_course, mi)


func _build_course() -> void:
	_box("Ground", Vector3(0, -0.5, -40), Vector3(280, 1, 280), "ground")

	# Speed lane: distance strips every 10 m ahead of spawn.
	for i in range(1, 6):
		_strip(Vector3(0, 0.01, 8 - i * 10), Vector3(6, 0.02, 0.15), Color("b4bfd0"))
		_sign("%d m" % (i * 10), Vector3(-4, 0.8, 8 - i * 10), 48)

	# Step heights: what you can walk, jump, or must climb.
	for i in 4:
		var h := 0.5 * (i + 1)
		_box("Step_%s" % str(h), Vector3(8, h / 2.0, 4 - i * 3.5), Vector3(2.5, h, 2.5), "block")
	_sign("Steps 0.5 · 1 · 1.5 · 2 m", Vector3(11, 3, -1))

	# Slopes: the controller walks up to 46°.
	for r: Array in [[20.0, -8.0], [35.0, -14.0], [50.0, -20.0]]:
		var a: float = r[0]
		_box("Ramp_%d" % int(a), Vector3(r[1], 5.0 * sin(deg_to_rad(a)), -2), Vector3(4, 0.4, 10), "block", false, Vector3(a, 0, 0))
		_sign("%d°%s" % [int(a), " · too steep" if a > 46.0 else ""], Vector3(r[1], 5.0 * sin(deg_to_rad(a)) * 2.0 + 1.5, -7), 48)

	# Tower field: hookable, for pulls and no-fall-damage drops.
	for t: Array in [[10.0, Vector3(-30, 0, -20)], [20.0, Vector3(-42, 0, -34)], [30.0, Vector3(-56, 0, -48)], [50.0, Vector3(-74, 0, -64)]]:
		var h: float = t[0]
		var base: Vector3 = t[1]
		_box("Tower_%d" % int(h), base + Vector3(0, h / 2.0, 0), Vector3(5, h, 5), "hook", true)
		_sign("%d m" % int(h), base + Vector3(0, h + 2.0, 0))
	_sign("Tower field · jump off anything, no fall damage", Vector3(-30, 14, -10), 56)

	# Hook eligibility: glass blocks the tether, the striped panel takes it.
	_box("Glass", Vector3(14, 5, -30), Vector3(10, 10, 0.3), "glass", false, Vector3.ZERO, "no_grapple")
	_sign("Glass · can't hook", Vector3(14, 11.5, -30))
	_box("HookPanel", Vector3(27, 5, -30), Vector3(10, 10, 0.3), "hook", true)
	_sign("Lime stripes · hookable", Vector3(27, 11.5, -30))

	# Swing gap: two cliffs 35 m apart with a hookable beam overhead.
	_box("CliffNear", Vector3(40, 6, -20), Vector3(20, 12, 20), "block")
	_box("CliffFar", Vector3(40, 6, -75), Vector3(20, 12, 20), "block")
	_box("SwingBeam", Vector3(40, 30, -47.5), Vector3(24, 1.5, 1.5), "hook", true)
	_box("BeamPillarL", Vector3(28.5, 15, -47.5), Vector3(1.5, 30, 1.5), "block")
	_box("BeamPillarR", Vector3(51.5, 15, -47.5), Vector3(1.5, 30, 1.5), "block")
	_sign("Swing gap · 35 m", Vector3(40, 15, -12))

	# Overhang: hook the underside and swing.
	_box("Overhang", Vector3(-24, 16, 18), Vector3(14, 1, 14), "hook", true)
	_sign("Hook the underside", Vector3(-24, 18.5, 18))

	# Range test: stand on the line, the near wall is in range, the far one isn't.
	_strip(Vector3(0, 0.01, -60), Vector3(12, 0.02, 0.25), Color("c5f277"))
	_sign("Range line", Vector3(0, 1.2, -60), 48)
	_box("Wall40", Vector3(-7, 6, -100), Vector3(10, 12, 1), "hook", true)
	_sign("40 m · in range", Vector3(-7, 13.5, -100))
	_box("Wall65", Vector3(7, 6, -125), Vector3(10, 12, 1), "hook", true)
	_sign("65 m · out of range", Vector3(7, 13.5, -125))
