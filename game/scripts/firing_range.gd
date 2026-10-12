extends Node3D
## Firing range (Training): lanes with targets at 10, 30, 50 and 100 m, some
## strafing, a loadout of every weapon with infinite ammo, a red pad to take a
## hit and a healing station, and a practice checklist. Esc opens the menu with
## practice analytics.

const LANES := [-9.0, 0.0, 9.0]
const DISTANCES := [10, 30, 50, 100]
const LOADOUT := ["ar7", "sg4", "field_patch:4", "shield_cell:4", "tethercaster", "ammo:medium:300", "ammo:shells:60"]
const AMMO := {&"medium": 240, &"shells": 30}
const PROP := "res://assets/models/%s.glb"
const HIT_PAD := Vector3(-14.0, 0.0, 6.0)
const SPAWN := Vector3(0.0, 0.1, 6.0)
## [id, text, key action or literal]
const CHECKLIST := [
	["fire", "Fire at a target", "@fire"],
	["aim", "Aim down sights", "@aim"],
	["reload", "Reload", "@reload"],
	["inventory", "Open your inventory", "@inventory"],
	["tether", "Fire the Tethercaster at the tower", "@grapple"],
	["hit", "Step on the red pad to take a hit", ""],
	["heal", "Heal to see the healing glow", "@fire"],
]

@onready var player: Player = $Player
@onready var hud: CanvasLayer = $HUD
@onready var inventory_screen: CanvasLayer = $InventoryScreen
@onready var _loot: Node3D = $Loot

var _done := {}
var _ammo_wait := 0.0
var _pad_wait := 0.0
var _complete_shown := false


func _ready() -> void:
	_build_environment()
	_build_ground()
	_build_lanes()
	_build_props()
	_build_targets()
	_build_hit_pad()
	player.start_loadout = PackedStringArray(LOADOUT)
	hud.bind(player)
	hud.alive_count = 1
	inventory_screen.player = player
	inventory_screen.world_parent = _loot
	inventory_screen.closed.connect(MouseLock.capture)
	player.respawn(Transform3D(Basis(), SPAWN))
	MatchStats.track(player)
	add_child(MenuWatcher.new("Firing range", true))
	_build_checklist()
	player.weapons.fired.connect(func(_w: WeaponDef) -> void: _tick("fire"))
	player.weapons.reload_started.connect(func(_s: float) -> void: _tick("reload"))
	player.health.healed.connect(func(_a: float) -> void: _tick("heal"))


func _unhandled_input(event: InputEvent) -> void:
	var button := event as InputEventMouseButton
	if button and button.pressed and button.button_index == MOUSE_BUTTON_LEFT and not MouseLock.is_captured() and player.combat_input:
		get_viewport().set_input_as_handled()
		player.input_grace = 0.25
		MouseLock.capture()
	elif event.is_action_pressed("inventory") and not inventory_screen.is_open() and player.is_alive() and player.combat_input:
		inventory_screen.open()
		get_viewport().set_input_as_handled()


func _process(delta: float) -> void:
	# Infinite ammo: keep the reserves topped up.
	_ammo_wait -= delta
	if _ammo_wait <= 0.0:
		_ammo_wait = 0.5
		for type: StringName in AMMO:
			var need: int = AMMO[type] - player.inventory.ammo_count(type)
			if need > 0:
				player.inventory.add_ammo(type, need)
	if player.weapons.aiming:
		_tick("aim")
	if inventory_screen.is_open():
		_tick("inventory")
	if player.state == Player.State.TETHERED:
		_tick("tether")
	_pad_wait = maxf(0.0, _pad_wait - delta)
	var feet := player.global_position
	if _pad_wait == 0.0 and Vector2(feet.x - HIT_PAD.x, feet.z - HIT_PAD.z).length() < 1.6 and feet.y < 1.0 and player.is_alive():
		_pad_wait = 2.0
		player.health.take_damage(15.0, HIT_PAD + Vector3(0, 1, -6), null)
		_tick("hit")
	if player.global_position.y < -30.0:
		player.teleport_to(Transform3D(Basis(), SPAWN))


# ---------------------------------------------------------------- checklist

## The practice checklist is the HUD's hint list; done items dim.
func _build_checklist() -> void:
	var items: Array = []
	for c: Array in CHECKLIST:
		items.append({"id": c[0], "keys": [c[2]] if c[2] != "" else ["Pad"], "text": c[1]})
	hud.set_hints(items)
	hud.set_mode("Practice", "Infinite ammo")
	hud.set_status("Firing range  ·  Infinite ammo")


func _tick(id: String) -> void:
	if _done.has(id):
		return
	_done[id] = true
	hud.mark_hint(id)
	Menus.sound("toggle")
	if _done.size() == CHECKLIST.size() and not _complete_shown:
		_complete_shown = true
		hud.toast("Practice complete. Esc, then Leave match, when you're ready to play.")


# ---------------------------------------------------------------- world

func _build_environment() -> void:
	var sky_mat := ShaderMaterial.new()
	sky_mat.shader = load("res://shaders/ringed_sky.gdshader")
	var sky := Sky.new()
	sky.sky_material = sky_mat
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.6
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.fog_enabled = true
	env.fog_light_color = Color(0.54, 0.58, 0.72)
	env.fog_density = 0.0012
	env.fog_sky_affect = 0.0
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.transform = Transform3D(Basis.from_euler(Vector3(deg_to_rad(-42), deg_to_rad(35), 0)), Vector3.ZERO)
	sun.light_color = Color(1, 0.89, 0.76)
	sun.light_energy = 1.25
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 80.0
	add_child(sun)


func _build_ground() -> void:
	var body := StaticBody3D.new()
	body.collision_layer = Hitscan.WORLD
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(260, 1, 460)
	shape.shape = box
	shape.position = Vector3(0, -0.5, -150)
	body.add_child(shape)
	add_child(body)
	var mi := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(260, 460)
	mi.mesh = plane
	mi.position = Vector3(0, 0, -150)
	mi.material_override = _grass_material()
	add_child(mi)
	# Concrete firing line.
	_slab(Vector3(0, 0.01, 4), Vector3(44, 0.02, 10), Color("5d636b"))


func _grass_material() -> StandardMaterial3D:
	var noise := FastNoiseLite.new()
	noise.frequency = 0.02
	noise.fractal_octaves = 4
	var ramp := Gradient.new()
	ramp.offsets = PackedFloat32Array([0.0, 0.5, 1.0])
	ramp.colors = PackedColorArray([Color("26361f"), Color("3a5129"), Color("4e6634")])
	var tex := NoiseTexture2D.new()
	tex.noise = noise
	tex.seamless = true
	tex.color_ramp = ramp
	tex.width = 512
	tex.height = 512
	var m := StandardMaterial3D.new()
	m.albedo_texture = tex
	m.uv1_scale = Vector3(18, 32, 1)
	m.roughness = 0.95
	return m


func _slab(pos: Vector3, size: Vector3, color: Color, unshaded := false) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = size
	mi.mesh = b
	mi.position = pos
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = 0.9
	if unshaded:
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mi.material_override = m
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)
	return mi


func _build_lanes() -> void:
	var paint := Color(0.92, 0.94, 0.9, 0.85)
	for x in [-13.5, -4.5, 4.5, 13.5]:
		_slab(Vector3(x, 0.015, -52), Vector3(0.18, 0.02, 108), paint, true)
	for d: int in DISTANCES:
		_slab(Vector3(0, 0.015, -d + 1.5), Vector3(27, 0.02, 0.25), paint, true)
		# Painted distance numbers and a sign at the side of the range.
		for lane: float in LANES:
			var n := Label3D.new()
			n.text = str(d)
			n.font = UIStyle.font("display")
			n.font_size = 256
			n.pixel_size = 0.012 if d < 100 else 0.02
			n.modulate = paint
			# Flat on the ground, reading upright from the firing line.
			n.rotation_degrees = Vector3(-90, 0, 0)
			n.position = Vector3(lane, 0.03, -d + 4.0 + (2.0 if d >= 100 else 0.0))
			n.shaded = false
			n.double_sided = false
			add_child(n)
		var sign := Label3D.new()
		sign.text = "%d M" % d
		sign.font = UIStyle.font("display")
		sign.font_size = 96
		sign.pixel_size = 0.012
		sign.modulate = UIStyle.ACCENT
		sign.outline_size = 12
		sign.outline_modulate = Color(0, 0, 0, 0.6)
		sign.position = Vector3(-16.5, 2.4, -d)
		sign.rotation_degrees.y = 25
		add_child(sign)
		var post := _slab(Vector3(-16.5, 1.0, -d), Vector3(0.12, 2.0, 0.12), Color("2a2f38"))
		post.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON


func _build_targets() -> void:
	var i := 0
	for d: int in DISTANCES:
		for lane: float in LANES:
			var t := TargetDummy.new()
			t.variant = i
			t.position = Vector3(lane, 0, -d)
			# Strafing targets in the right lane at 30 and 50 m.
			if lane > 0.0 and d in [30, 50]:
				t.strafe = 3.0
			add_child(t)
			t.downed.connect(func(_t: TargetDummy) -> void: hud.feed("Target down · %d m" % d))
			i += 1


func _build_hit_pad() -> void:
	var pad := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = 1.5
	cyl.bottom_radius = 1.5
	cyl.height = 0.04
	pad.mesh = cyl
	pad.position = HIT_PAD + Vector3(0, 0.03, 0)
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(UIStyle.DANGER, 0.85)
	m.emission_enabled = true
	m.emission = UIStyle.DANGER
	m.emission_energy_multiplier = 0.8
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	pad.material_override = m
	add_child(pad)
	var l := Label3D.new()
	l.text = "TAKE A HIT"
	l.font = UIStyle.font("label_bold")
	l.font_size = 48
	l.pixel_size = 0.01
	l.modulate = UIStyle.DANGER
	l.outline_size = 8
	l.outline_modulate = Color(0, 0, 0, 0.6)
	l.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	l.position = HIT_PAD + Vector3(0, 1.4, 0)
	add_child(l)


func _build_props() -> void:
	# Built as children of an auto-collision node so props get collision and
	# the tower is a Tethercaster anchor.
	var props := Node3D.new()
	props.set_script(load("res://scripts/world/auto_collide.gd"))
	props.name = "Props"
	var place := func(model: String, pos: Vector3, yaw := 0.0, scale := 1.0) -> void:
		var path := PROP % model
		if not ResourceLoader.exists(path):
			return
		var n := (load(path) as PackedScene).instantiate() as Node3D
		n.position = pos
		n.rotation_degrees.y = yaw
		n.scale = Vector3.ONE * scale
		props.add_child(n)
	# Firing line: sandbags between lanes, crates and a terminal behind.
	for x in [-13.5, -4.5, 4.5, 13.5]:
		place.call("props/prop-sandbag-wall", Vector3(x, 0, -0.2), 0.0)
	place.call("props/prop-crate-large", Vector3(-20, 0, 6), 15.0)
	place.call("props/prop-crate-small", Vector3(-19, 0, 8.5), -20.0)
	place.call("props/prop-terminal", Vector3(18, 0, 7), -90.0)
	place.call("props/prop-generator", Vector3(21, 0, 4), -80.0)
	place.call("props/prop-lamp-post", Vector3(-22, 0, 0))
	place.call("props/prop-lamp-post", Vector3(22, 0, 0))
	place.call("colony-kit/colony-work-light", Vector3(-22, 0, 10), 140.0)
	place.call("colony-kit/colony-work-light", Vector3(22, 0, 10), -140.0)
	# A watch tower to practice the Tethercaster on.
	place.call("colony-kit/colony-gantry", Vector3(-30, 0, -20), 90.0)
	place.call("colony-kit/colony-stairs", Vector3(-30, 0, -14), 0.0)
	place.call("colony-kit/colony-comms-mast", Vector3(30, 0, -26), 0.0)
	# Backstops and scenery past the 100 m line.
	for x in [-24, -12, 0, 12, 24]:
		place.call("props/prop-barrier", Vector3(x, 0, -112), 0.0, 1.4)
	place.call("colony-kit/colony-cargo-container", Vector3(-34, 0, -60), 80.0)
	place.call("colony-kit/colony-cargo-container", Vector3(36, 0, -45), -70.0)
	place.call("colony-kit/colony-habitat-module", Vector3(42, 0, 12), -120.0)
	for i in 26:
		var a := float(i) / 26.0 * TAU
		var r := 70.0 + float((i * 37) % 30)
		var pos := Vector3(cos(a) * r * 0.8, 0, -60.0 + sin(a) * r)
		if absf(pos.x) < 30.0 and pos.z > -115.0 and pos.z < 20.0:
			continue
		var k := 1.0 + float(i % 4) * 0.25
		# Canopies sit on their stalks and trunks, as on Ringfall.
		match i % 3:
			0:
				place.call("vegetation/veg-bloom-stalk", pos, float(i * 47), k)
				place.call("vegetation/veg-bloom-cap", pos, float(i * 47), k)
			1:
				place.call("vegetation/veg-tree-trunk", pos, float(i * 47), k)
				place.call("vegetation/veg-tree-canopy", pos, float(i * 47), k)
			_:
				place.call("vegetation/veg-glow-shrub", pos, float(i * 47), k)
	add_child(props)
	# Spare loot on the crates for practicing pickups and swaps.
	Pickup.spawn_stack(_loot, ItemCatalog.stack(&"shield_pack", 2), Vector3(-19.5, 1.2, 6.2))
	Pickup.spawn_stack(_loot, ItemCatalog.stack(&"field_patch", 3), Vector3(-19, 0.7, 8.4))
	Pickup.spawn_stack(_loot, ItemCatalog.stack(&"ar7"), Vector3(-17.5, 0.2, 9.5))
	Pickup.spawn_stack(_loot, ItemCatalog.stack(&"sg4"), Vector3(-16.0, 0.2, 9.5))
