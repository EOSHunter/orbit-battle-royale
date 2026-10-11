class_name Fx
extends RefCounted
## Combat, healing and traversal effects: muzzle flashes, tracers, impacts,
## shield hits and breaks, healing auras, landing and sprint dust, splashes.
## Everything is procedural (gradient textures and CPU particles), so effects add
## nothing to the download and run in the Compatibility renderer.
## Assets: "Combat impacts", "Healing effects", "Traversal effects" in the asset list.

const SPARK := Color(1.0, 0.78, 0.45)
const FLESH := Color(1.0, 0.47, 0.5)
const SHIELD := Color(0.44, 0.84, 1.0)
const HEALTH := Color(1.0, 0.55, 0.5)
const DUST := Color(0.62, 0.6, 0.66, 0.55)

static var _glow_tex: GradientTexture2D
static var _star_tex: GradientTexture2D
static var _tracer_mat: StandardMaterial3D
static var _flash_mat: StandardMaterial3D
static var _tracer_mesh: BoxMesh
static var _flash_mesh: QuadMesh


static func _ensure() -> void:
	if _glow_tex:
		return
	_glow_tex = _radial([Color(1, 1, 1, 1), Color(1, 1, 1, 0.35), Color(1, 1, 1, 0)], [0.0, 0.35, 1.0])
	_star_tex = _radial([Color(1, 1, 1, 1), Color(1, 0.9, 0.7, 0.6), Color(1, 0.6, 0.3, 0)], [0.0, 0.2, 1.0], 0.5)
	_tracer_mat = _additive(Color(1.0, 0.82, 0.55, 0.85), null)
	_tracer_mesh = BoxMesh.new()
	_tracer_mesh.size = Vector3(0.018, 0.018, 1.0)
	_flash_mat = _additive(Color(1.0, 0.8, 0.5, 1.0), _star_tex)
	_flash_mat.billboard_mode = BaseMaterial3D.BILLBOARD_DISABLED
	_flash_mesh = QuadMesh.new()
	_flash_mesh.size = Vector2(0.22, 0.22)


static func _radial(colors: Array, offsets: Array, squash := 0.0) -> GradientTexture2D:
	var g := Gradient.new()
	g.colors = PackedColorArray(colors)
	g.offsets = PackedFloat32Array(offsets)
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5)
	t.fill_to = Vector2(0.5, 0.0 + squash * 0.5)
	t.width = 64
	t.height = 64
	return t


static func _additive(c: Color, tex: Texture2D, billboard := true) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = c
	m.albedo_texture = tex
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.vertex_color_use_as_albedo = true
	m.disable_fog = true
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	if billboard:
		m.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	return m


static func _alpha(c: Color, tex: Texture2D) -> StandardMaterial3D:
	var m := _additive(c, tex)
	m.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
	return m


static func _root(_world: World3D) -> Node:
	# Effects live under the current scene; World3D has no node of its own.
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree and tree.current_scene else (tree.root if tree else null)


## One-shot particle burst. Frees itself when done.
static func _burst(root: Node, pos: Vector3, dir: Vector3, amount: int, color: Color, material: Material,
		speed: Vector2, life: float, size: Vector2, spread: float, gravity := Vector3(0, -9.8, 0), damping := 0.0) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	p.one_shot = true
	p.explosiveness = 0.95
	p.amount = amount
	p.lifetime = life
	p.local_coords = false
	var q := QuadMesh.new()
	q.size = Vector2.ONE
	q.material = material
	p.mesh = q
	p.direction = dir
	p.spread = spread
	p.initial_velocity_min = speed.x
	p.initial_velocity_max = speed.y
	p.gravity = gravity
	p.damping_min = damping
	p.damping_max = damping
	p.scale_amount_min = size.x
	p.scale_amount_max = size.y
	var curve := Curve.new()
	curve.add_point(Vector2(0, 1))
	curve.add_point(Vector2(1, 0))
	p.scale_amount_curve = curve
	var ramp := Gradient.new()
	ramp.colors = PackedColorArray([color, Color(color, 0.0)])
	p.color_ramp = ramp
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.add_child(p)
	p.global_position = pos
	p.emitting = true
	_fade_and_free(p, life + 0.1)
	return p


# ------------------------------------------------------------------- weapons

static func tracer(world: World3D, from: Vector3, to: Vector3) -> void:
	_ensure()
	var root := _root(world)
	var length := from.distance_to(to)
	if root == null or length < 0.5:
		return
	var mi := MeshInstance3D.new()
	mi.mesh = _tracer_mesh
	mi.material_override = _tracer_mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.add_child(mi)
	var dir := (to - from) / length
	# A short bright streak that travels most of the way, not a laser line.
	var streak := minf(length * 0.6, 7.0)
	mi.global_transform = Transform3D(Basis.looking_at(dir, Vector3.UP if absf(dir.y) < 0.99 else Vector3.FORWARD), from + dir * streak * 0.5)
	mi.scale = Vector3(1, 1, streak)
	var t := mi.create_tween()
	t.tween_property(mi, "global_position", to - dir * streak * 0.5, minf(0.08, length / 900.0))
	t.tween_callback(mi.queue_free)


static func muzzle_flash(parent: Node3D) -> void:
	_ensure()
	var light := OmniLight3D.new()
	light.light_color = Color(1.0, 0.75, 0.45)
	light.light_energy = 2.5
	light.omni_range = 4.0
	parent.add_child(light)
	_fade_and_free(light, 0.05)
	# Two crossed star cards along the barrel and one facing the camera.
	for i in 3:
		var q := MeshInstance3D.new()
		q.mesh = _flash_mesh
		q.material_override = _flash_mat
		q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		parent.add_child(q)
		match i:
			0: q.rotation = Vector3(0, PI / 2.0, randf() * TAU)
			1: q.rotation = Vector3(PI / 2.0, 0, randf() * TAU)
			_: q.rotation = Vector3(0, 0, randf() * TAU)
		var s := randf_range(0.7, 1.2)
		q.scale = Vector3(s, s * (1.6 if i < 2 else 1.0), s)
		q.position = Vector3(0, 0, -0.06 * s) if i < 2 else Vector3.ZERO
		_fade_and_free(q, 0.04)


static func impact(world: World3D, pos: Vector3, normal: Vector3, flesh: bool) -> void:
	_ensure()
	var root := _root(world)
	if root == null:
		return
	var at := pos + normal * 0.03
	if flesh:
		_burst(root, at, normal, 10, FLESH, _alpha(Color.WHITE, _glow_tex), Vector2(1.5, 3.5), 0.3, Vector2(0.06, 0.12), 40.0)
		return
	_burst(root, at, normal, 12, SPARK, _additive(Color.WHITE, _glow_tex), Vector2(3.0, 8.0), 0.35, Vector2(0.02, 0.05), 55.0)
	_burst(root, at, normal, 5, DUST, _alpha(Color.WHITE, _glow_tex), Vector2(0.3, 1.0), 0.8, Vector2(0.18, 0.35), 35.0, Vector3(0, 0.4, 0), 2.0)
	_burst(root, at, normal, 1, Color(1.0, 0.85, 0.6, 0.9), _additive(Color.WHITE, _glow_tex), Vector2.ZERO, 0.06, Vector2(0.25, 0.25), 0.0, Vector3.ZERO)


## Cyan crackle where a shot lands on a shield.
static func shield_hit(world: World3D, pos: Vector3, normal: Vector3) -> void:
	_ensure()
	var root := _root(world)
	if root:
		_burst(root, pos + normal * 0.05, normal, 14, SHIELD, _additive(Color.WHITE, _glow_tex), Vector2(1.0, 3.0), 0.25, Vector2(0.03, 0.07), 70.0, Vector3.ZERO, 3.0)
		_burst(root, pos + normal * 0.05, normal, 1, Color(SHIELD, 0.8), _additive(Color.WHITE, _glow_tex), Vector2.ZERO, 0.12, Vector2(0.5, 0.5), 0.0, Vector3.ZERO)


## Shield shattering around a body: a ring of cyan shards.
static func shield_break(world: World3D, center: Vector3) -> void:
	_ensure()
	var root := _root(world)
	if root:
		_burst(root, center, Vector3.UP, 36, SHIELD, _additive(Color.WHITE, _glow_tex), Vector2(2.0, 5.0), 0.6, Vector2(0.04, 0.09), 180.0, Vector3(0, -4.0, 0), 1.5)
		_burst(root, center, Vector3.UP, 1, Color(SHIELD, 0.9), _additive(Color.WHITE, _glow_tex), Vector2.ZERO, 0.2, Vector2(1.6, 1.6), 0.0, Vector3.ZERO)


# ------------------------------------------------------------------- healing

## Rising particles around a body while a heal is used. Returns the emitter so the
## caller can stop it when the heal ends or is interrupted.
static func heal_aura(parent: Node3D, shield: bool) -> CPUParticles3D:
	_ensure()
	var p := CPUParticles3D.new()
	p.amount = 24
	p.lifetime = 1.0
	p.local_coords = true
	var q := QuadMesh.new()
	q.size = Vector2.ONE
	q.material = _additive(Color.WHITE, _glow_tex)
	p.mesh = q
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_RING
	p.emission_ring_axis = Vector3.UP
	p.emission_ring_radius = 0.45
	p.emission_ring_inner_radius = 0.3
	p.emission_ring_height = 0.1
	p.direction = Vector3.UP
	p.spread = 10.0
	p.gravity = Vector3(0, 0.8, 0)
	p.initial_velocity_min = 0.4
	p.initial_velocity_max = 0.9
	p.scale_amount_min = 0.04
	p.scale_amount_max = 0.09
	var c := SHIELD if shield else HEALTH
	var ramp := Gradient.new()
	ramp.colors = PackedColorArray([Color(c, 0.0), c, Color(c, 0.0)])
	ramp.offsets = PackedFloat32Array([0.0, 0.3, 1.0])
	p.color_ramp = ramp
	p.position = Vector3(0, 0.2, 0)
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	parent.add_child(p)
	p.emitting = true
	return p


static func stop_aura(p: CPUParticles3D) -> void:
	if is_instance_valid(p):
		p.emitting = false
		_fade_and_free(p, p.lifetime + 0.1)


# ----------------------------------------------------------------- traversal

static func landing_dust(world: World3D, pos: Vector3, strength: float) -> void:
	_ensure()
	var root := _root(world)
	if root == null:
		return
	var n := int(lerpf(6.0, 20.0, clampf(strength, 0.0, 1.0)))
	var p := _burst(root, pos + Vector3.UP * 0.05, Vector3.UP, n, DUST, _alpha(Color.WHITE, _glow_tex), Vector2(1.0, 2.5 + strength * 2.0), 0.9, Vector2(0.25, 0.5), 80.0, Vector3(0, -0.6, 0), 3.0)
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_RING
	p.emission_ring_axis = Vector3.UP
	p.emission_ring_radius = 0.35
	p.emission_ring_inner_radius = 0.2
	p.emission_ring_height = 0.0
	p.flatness = 0.85


static func sprint_dust(world: World3D, pos: Vector3) -> void:
	_ensure()
	var root := _root(world)
	if root:
		_burst(root, pos + Vector3.UP * 0.05, Vector3.UP, 2, Color(DUST, 0.35), _alpha(Color.WHITE, _glow_tex), Vector2(0.2, 0.6), 0.6, Vector2(0.15, 0.3), 60.0, Vector3(0, 0.2, 0), 2.0)


static func water_splash(world: World3D, pos: Vector3, strength: float) -> void:
	_ensure()
	var root := _root(world)
	if root:
		_burst(root, pos, Vector3.UP, int(10 + 20 * strength), Color(0.75, 0.95, 1.0, 0.8), _alpha(Color.WHITE, _glow_tex), Vector2(2.0, 4.0 + 3.0 * strength), 0.7, Vector2(0.05, 0.12), 25.0, Vector3(0, -9.8, 0))


static func _fade_and_free(node: Node, seconds: float) -> void:
	var t := node.create_tween()
	t.tween_interval(seconds)
	t.tween_callback(node.queue_free)
