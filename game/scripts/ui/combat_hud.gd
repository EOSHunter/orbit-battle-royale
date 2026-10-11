extends CanvasLayer
## Match HUD for the combat slice, following the prototype and design system:
## health and shield meters, the five-slot strip, ammunition, crosshair with
## hit markers, directional damage arcs with an edge glow toward the attacker,
## the healing ring with a cyan (shields) or mint (health) edge glow, a pulsing
## low-health warning, interact prompts, the elimination feed and end screens.

const ACCENT := Color("c5f277")
const TEXT := Color("f3f5fa")
const TEXT_2 := Color("b4bfd0")
const DANGER := Color("ff797f")
const WARNING := Color("ffd18a")
const HEALTH := Color("ff8d7f")
const SHIELD := Color("70d6ff")
const MINT := Color("8de0b0")
const SURFACE := Color("141d2d")
const SCRIM := Color(0.043, 0.063, 0.106, 0.72)
const ARC_LIFE := 1.4

var player: Player
var alive_count := 0
var eliminations := 0

var _root: Control
var _crosshair: Control
var _meters: Control
var _slots: Control
var _caption: Label
var _ammo: Label
var _weapon_name: Label
var _ammo_hint: Label
var _prompt: Label
var _status: Label
var _stats: Label
var _feed: VBoxContainer
var _toast: Label
var _center: Label
var _help: Label
var _help_time := 15.0
var _damage_glow: ColorRect
var _heal_glow: ColorRect
var _low_glow: ColorRect
var _arcs: Array[Dictionary] = []
var _hit_time := 0.0
var _hit_kill := false
var _toast_time := 0.0
var _status_time := 0.0
var _heal_done_time := 0.0
var _t := 0.0


func _ready() -> void:
	_root = Control.new()
	_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root)

	_damage_glow = _glow_rect(DANGER)
	_heal_glow = _glow_rect(SHIELD)
	_low_glow = _glow_rect(DANGER)

	_crosshair = _canvas(_draw_crosshair)
	_crosshair.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	_meters = _canvas(_draw_meters)
	_meters.custom_minimum_size = Vector2(360, 76)
	_pin(_meters, Vector2(0, 1), Vector2i(Control.GROW_DIRECTION_END, Control.GROW_DIRECTION_BEGIN), Vector2(28, -28))

	_status = _label(17, SHIELD)
	_pin(_status, Vector2(0, 1), Vector2i(Control.GROW_DIRECTION_END, Control.GROW_DIRECTION_BEGIN), Vector2(28, -112))

	_slots = _canvas(_draw_slots)
	_slots.custom_minimum_size = Vector2(5 * 76 + 4 * 8 + 14, 76)
	_pin(_slots, Vector2(0.5, 1), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_BEGIN), Vector2(0, -28))
	_caption = _label(17, TEXT)
	_caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_caption.custom_minimum_size = Vector2(500, 0)
	_pin(_caption, Vector2(0.5, 1), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_BEGIN), Vector2(0, -114))

	var ammo_box := VBoxContainer.new()
	ammo_box.alignment = BoxContainer.ALIGNMENT_END
	ammo_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(ammo_box)
	_pin(ammo_box, Vector2(1, 1), Vector2i(Control.GROW_DIRECTION_BEGIN, Control.GROW_DIRECTION_BEGIN), Vector2(-32, -28))
	_ammo = _label(46, TEXT, ammo_box)
	_ammo.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_weapon_name = _label(16, TEXT_2, ammo_box)
	_weapon_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_ammo_hint = _label(16, WARNING, ammo_box)
	_ammo_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	_stats = _label(22, TEXT)
	_stats.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_pin(_stats, Vector2(1, 0), Vector2i(Control.GROW_DIRECTION_BEGIN, Control.GROW_DIRECTION_END), Vector2(-28, 24))
	_feed = VBoxContainer.new()
	_feed.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_feed.alignment = BoxContainer.ALIGNMENT_BEGIN
	_root.add_child(_feed)
	_pin(_feed, Vector2(1, 0), Vector2i(Control.GROW_DIRECTION_BEGIN, Control.GROW_DIRECTION_END), Vector2(-28, 62))

	_prompt = _label(18, TEXT)
	_prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt.custom_minimum_size = Vector2(600, 0)
	_pin(_prompt, Vector2(0.5, 0.5), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_END), Vector2(0, 70))

	_toast = _label(18, WARNING)
	_toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_toast.custom_minimum_size = Vector2(700, 0)
	_pin(_toast, Vector2(0.5, 0), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_END), Vector2(0, 28))

	_help = _label(15, TEXT_2)
	_help.text = "WASD move · Space jump · Shift sprint · C crouch
Click fire · Right-click aim · R reload · 1–5 or wheel switch slots
E pick up · Tab inventory · Q or mouse side button: Tethercaster
F1 tuning · F5 restart · F10 movement playground · H hide this help"
	_pin(_help, Vector2(0, 0), Vector2i(Control.GROW_DIRECTION_END, Control.GROW_DIRECTION_END), Vector2(28, 24))

	_center = _label(44, TEXT)
	_center.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_center.custom_minimum_size = Vector2(900, 0)
	_center.visible = false
	_pin(_center, Vector2(0.5, 0.5), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_BOTH), Vector2(0, -60))


func bind(p: Player) -> void:
	player = p
	p.health.damaged.connect(_on_damaged)
	p.weapons.hit_confirmed.connect(func(_d: float, killed: bool) -> void:
		_hit_time = 0.22
		_hit_kill = killed)
	p.heal_finished.connect(func(def: HealDef) -> void:
		_heal_done_time = 0.6
		_show_status("%s used" % def.display_name, MINT if def.pool == HealDef.Pool.HEALTH else SHIELD))
	p.heal_interrupted.connect(func(reason: String) -> void: _show_status("Interrupted · %s. Item kept." % reason, WARNING))
	p.notice.connect(toast)
	p.landed.connect(func(drop: float, _s: float) -> void:
		if drop > 6.0:
			_show_status("Landed from %.0f m · no fall damage" % drop, TEXT_2))


# ---------------------------------------------------------------- helpers

func _label(size: int, color: Color, parent: Control = null) -> Label:
	var l := Label.new()
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.65))
	l.add_theme_constant_override("shadow_offset_y", 1)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	(parent if parent else _root).add_child(l)
	return l


func _canvas(draw_fn: Callable) -> Control:
	var c := Control.new()
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.draw.connect(draw_fn)
	_root.add_child(c)
	return c


func _glow_rect(color: Color) -> ColorRect:
	var r := ColorRect.new()
	r.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/edge_glow.gdshader")
	m.set_shader_parameter("glow_color", color)
	m.set_shader_parameter("strength", 0.0)
	r.material = m
	_root.add_child(r)
	return r


func _pin(c: Control, anchor: Vector2, grow: Vector2i, offset: Vector2) -> void:
	c.anchor_left = anchor.x
	c.anchor_right = anchor.x
	c.anchor_top = anchor.y
	c.anchor_bottom = anchor.y
	c.grow_horizontal = grow.x as Control.GrowDirection
	c.grow_vertical = grow.y as Control.GrowDirection
	c.offset_left = offset.x
	c.offset_right = offset.x
	c.offset_top = offset.y
	c.offset_bottom = offset.y


func toast(text: String) -> void:
	_toast.text = text
	_toast_time = 3.0


func _show_status(text: String, color: Color) -> void:
	_status.text = text
	_status.add_theme_color_override("font_color", color)
	_status_time = 2.6


func feed(text: String) -> void:
	var l := _label(16, TEXT, _feed)
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	var t := l.create_tween()
	t.tween_interval(6.0)
	t.tween_property(l, "modulate:a", 0.0, 0.6)
	t.tween_callback(l.queue_free)
	while _feed.get_child_count() > 4:
		_feed.get_child(0).free()


func show_center(text: String) -> void:
	_center.text = text
	_center.visible = text != ""


# ---------------------------------------------------------------- damage feedback

func _on_damaged(amount: float, from: Vector3, _attacker: Node) -> void:
	if amount <= 0.0 or from == Vector3.ZERO:
		return
	_arcs.append({"from": from, "age": 0.0})
	if _arcs.size() > 6:
		_arcs.remove_at(0)
	# Edge glow toward the attacker, in screen space (x right, y down).
	var rel := _relative_angle(from)
	var m := _damage_glow.material as ShaderMaterial
	m.set_shader_parameter("direction", Vector2(sin(rel), -cos(rel)))
	m.set_shader_parameter("strength", 0.85)


func _relative_angle(from: Vector3) -> float:
	var to := from - player.global_position
	var bearing := atan2(to.x, -to.z)
	var facing := atan2(-player.global_basis.z.x, player.global_basis.z.z)
	return wrapf(bearing - facing, -PI, PI)


# ---------------------------------------------------------------- frame

func _process(delta: float) -> void:
	if player == null:
		return
	_t += delta
	_hit_time = maxf(0.0, _hit_time - delta)
	_toast_time = maxf(0.0, _toast_time - delta)
	_status_time = maxf(0.0, _status_time - delta)
	_heal_done_time = maxf(0.0, _heal_done_time - delta)
	_help_time = maxf(0.0, _help_time - delta)
	_help.modulate.a = clampf(_help_time, 0.0, 1.0)
	_toast.visible = _toast_time > 0.0
	_toast.modulate.a = clampf(_toast_time, 0.0, 1.0)
	if player.using:
		_status.text = "Using %s · %.1f s" % [player.using.display_name, maxf(0.0, player.use_left)]
		_status.add_theme_color_override("font_color", MINT if player.using.pool == HealDef.Pool.HEALTH else SHIELD)
		_status.modulate.a = 1.0
	else:
		_status.modulate.a = clampf(_status_time, 0.0, 1.0)

	for a in _arcs:
		a.age = float(a.age) + delta
	_arcs.assign(_arcs.filter(func(a: Dictionary) -> bool: return float(a.age) < ARC_LIFE))
	var dm := _damage_glow.material as ShaderMaterial
	dm.set_shader_parameter("strength", maxf(0.0, float(dm.get_shader_parameter("strength")) - delta * 1.1))

	var hm := _heal_glow.material as ShaderMaterial
	var healing := player.using != null
	if healing:
		hm.set_shader_parameter("glow_color", MINT if player.using.pool == HealDef.Pool.HEALTH else SHIELD)
	var heal_strength := (0.45 + 0.2 * sin(_t * 4.5)) if healing else _heal_done_time
	hm.set_shader_parameter("strength", heal_strength)
	hm.set_shader_parameter("width", 0.35)

	var lm := _low_glow.material as ShaderMaterial
	var low := player.is_alive() and player.health.health <= 25.0
	lm.set_shader_parameter("strength", (0.35 + 0.2 * sin(_t * 4.0)) if low else 0.0)

	_update_ammo()
	_update_prompt()
	_stats.text = "%d alive  ·  %d eliminated" % [alive_count, eliminations]
	_crosshair.queue_redraw()
	_meters.queue_redraw()
	_slots.queue_redraw()


func _update_ammo() -> void:
	var w := player.weapons.weapon()
	var s := player.inventory.selected_stack()
	_ammo_hint.text = ""
	if w and s:
		_ammo.text = "%d / %d" % [s.mag, player.inventory.ammo_count(w.ammo_type)]
		_weapon_name.text = "%s · %s" % [w.display_name, AmmoTypes.display_name(w.ammo_type)]
		if player.weapons.is_reloading():
			_ammo_hint.text = "Reloading…"
		elif s.mag == 0 and player.inventory.ammo_count(w.ammo_type) == 0:
			_ammo_hint.text = "No %s ammunition" % AmmoTypes.display_name(w.ammo_type).to_lower()
			_ammo_hint.add_theme_color_override("font_color", DANGER)
		elif s.mag <= w.magazine / 4:
			_ammo_hint.text = "R  Reload"
			_ammo_hint.add_theme_color_override("font_color", WARNING)
		_ammo.add_theme_color_override("font_color", WARNING if s.mag <= w.magazine / 4 else TEXT)
	elif s:
		_ammo.text = ""
		_weapon_name.text = s.def.display_name
	else:
		_ammo.text = ""
		_weapon_name.text = ""
	var cap := ""
	if s:
		cap = s.def.display_name
		if s.def is HealDef:
			var h := s.def as HealDef
			cap += "  ·  %d  ·  %s · %.1f s  ·  Click to use" % [s.qty, h.description.trim_suffix("."), h.use_time]
		elif s.def.id == &"tethercaster":
			var t := player.tether
			cap += "  ·  %s" % ("attached" if t.is_attached() else ("ready · Click or Q" if t.charge() >= 1.0 else "recharging %.1f s" % t.cooldown_left))
	_caption.text = cap


func _update_prompt() -> void:
	var p := player.focused_pickup
	if not player.is_alive():
		_prompt.text = ""
	elif p:
		var verb := "Pick up"
		if not p.is_ammo():
			var pv := player.inventory.preview(p.stack)
			if pv.full:
				verb = "Can't carry more ·"
			elif pv.blocked:
				verb = "Slots full · Tab to replace ·"
		_prompt.text = "E  %s %s" % [verb, p.display_name()]
		_prompt.add_theme_color_override("font_color", TEXT)
	else:
		_prompt.text = ""


# ---------------------------------------------------------------- drawing

func _draw_crosshair() -> void:
	# Center on the viewport itself, wherever the drawing layer sits.
	var c := _crosshair.get_viewport_rect().size * 0.5 - _crosshair.global_position
	var color := TEXT
	var gap := 6.0 + player.weapons.spread_now * 3.0
	if player.inventory.selected_stack() and player.inventory.selected_stack().def.id == &"tethercaster":
		gap = 6.0
		if player.tether.aim == Tethercaster.Aim.IN_RANGE and player.tether.charge() >= 1.0:
			color = ACCENT
	if player.weapons.aiming:
		_crosshair.draw_circle(c, 2.0, color)
	else:
		for d: Vector2 in [Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT]:
			_crosshair.draw_line(c + d * gap, c + d * (gap + 9.0), Color(0, 0, 0, 0.5), 4.0)
			_crosshair.draw_line(c + d * gap, c + d * (gap + 9.0), color, 2.0)
	if _hit_time > 0.0:
		var hc := DANGER if _hit_kill else TEXT
		hc.a = _hit_time / 0.22
		for d: Vector2 in [Vector2(1, 1), Vector2(-1, 1), Vector2(1, -1), Vector2(-1, -1)]:
			_crosshair.draw_line(c + d.normalized() * 8.0, c + d.normalized() * 17.0, hc, 2.5)
	# Damage direction arcs around the crosshair, tracking as the player turns.
	for a in _arcs:
		var rel := _relative_angle(a.from) - PI / 2.0
		var fade := 1.0 - float(a.age) / ARC_LIFE
		var col := DANGER
		col.a = fade
		_crosshair.draw_arc(c, 110.0, rel - 0.32, rel + 0.32, 24, Color(0, 0, 0, 0.35 * fade), 9.0, true)
		_crosshair.draw_arc(c, 110.0, rel - 0.3, rel + 0.3, 24, col, 6.0, true)
	# Healing progress ring.
	if player.using:
		var k := 1.0 - player.use_left / player.using.use_time
		var rc := MINT if player.using.pool == HealDef.Pool.HEALTH else SHIELD
		_crosshair.draw_arc(c, 34.0, 0.0, TAU, 48, Color(0, 0, 0, 0.4), 4.0, true)
		_crosshair.draw_arc(c, 34.0, -PI / 2.0, -PI / 2.0 + TAU * clampf(k, 0.0, 1.0), 48, rc, 4.0, true)
	if player.weapons.is_reloading():
		_crosshair.draw_arc(c, 26.0, -PI / 2.0, -PI / 2.0 + TAU * player.weapons.reload_progress(), 40, TEXT_2, 3.0, true)


func _draw_meters() -> void:
	var h := player.health
	_meters.draw_rect(Rect2(Vector2.ZERO, _meters.size), SCRIM)
	_meter(Vector2(14, 14), h.shield, h.max_shield, SHIELD)
	_meter(Vector2(14, 44), h.health, h.max_health, DANGER if h.health <= 25.0 else HEALTH)


func _meter(at: Vector2, value: float, max_value: float, color: Color) -> void:
	var seg_w := 60.0
	for i in 4:
		var x := at.x + i * (seg_w + 4.0)
		_meters.draw_rect(Rect2(x, at.y, seg_w, 14), Color("213047"))
		var fill := clampf((value - i * max_value / 4.0) / (max_value / 4.0), 0.0, 1.0)
		if fill > 0.0:
			_meters.draw_rect(Rect2(x, at.y, seg_w * fill, 14), color)
	_meters.draw_string(ThemeDB.fallback_font, Vector2(at.x + 4 * (seg_w + 4.0) + 8, at.y + 14), str(int(ceil(value))), HORIZONTAL_ALIGNMENT_LEFT, -1, 22, color)


func _draw_slots() -> void:
	var inv := player.inventory
	var font := ThemeDB.fallback_font
	var x := 0.0
	for i in Inventory.SLOT_COUNT:
		if i == 2:
			x += 14.0
		var r := Rect2(x, 0, 76, 76)
		var s := inv.get_slot(i)
		var selected := inv.selected == i
		_slots.draw_rect(r, SCRIM if s else Color(0, 0, 0, 0.25))
		var border := ACCENT if selected else (Color("7083a0") if s else Color("46566d"))
		_slots.draw_rect(r, border, false, 2.0 if selected else 1.0)
		_slots.draw_string(font, r.position + Vector2(6, 16), str(i + 1), HORIZONTAL_ALIGNMENT_LEFT, -1, 13, TEXT_2)
		if i < 2:
			_slots.draw_rect(Rect2(r.position + Vector2(62, 6), Vector2(7, 7)), TEXT_2, false, 1.0)
		if s:
			var col := s.def.color
			_slots.draw_rect(Rect2(r.position + Vector2(22, 26), Vector2(32, 24)), col.darkened(0.2))
			var short := s.def.display_name.split(" ")[0]
			_slots.draw_string(font, r.position + Vector2(4, 70), short, HORIZONTAL_ALIGNMENT_CENTER, 68, 12, TEXT)
			var qty := ""
			if s.def.is_weapon():
				qty = str(s.mag)
			elif s.def.stack_max > 1:
				qty = str(s.qty)
			if qty != "":
				_slots.draw_string(font, r.position + Vector2(40, 16), qty, HORIZONTAL_ALIGNMENT_RIGHT, 32, 15, TEXT)
			if s.def.id == &"tethercaster":
				var ch := player.tether.charge()
				_slots.draw_rect(Rect2(r.position + Vector2(6, 56), Vector2(64 * ch, 3)), ACCENT if ch >= 1.0 else TEXT_2)
		x += 84.0


func _unhandled_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key and key.pressed and not key.echo and key.physical_keycode == KEY_H:
		_help_time = 0.0 if _help_time > 0.0 else 9999.0
