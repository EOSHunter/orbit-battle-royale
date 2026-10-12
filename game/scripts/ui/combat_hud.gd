extends CanvasLayer
## Match HUD. Layout and sizes from the menu designs, in our design system:
## the mode label top-left, a 760 px compass top-center, alive / kills /
## damage chips top-right with the feed under them, a key-hint list at
## 44/320, the crosshair with hit markers and hit numbers (shield icon on
## shield hits, a cracked shield and "SHIELD BROKEN" on the break, plain
## white on health), vitals bottom-left (28 px icons, 280 × 12 bars, 36 px
## numbers), ammunition, weapon name and five slots bottom-right, and edge
## glows for damage, healing and low health. HUD scale scales it all.

const ARC_LIFE := 1.4
const ICONS := "res://assets/ui/brand-and-ui/hud-icon-set/%s.svg"
const DEFAULT_HINTS := [
	{"id": "move", "keys": ["@move_forward", "@move_left", "@move_back", "@move_right"], "text": "Move"},
	{"id": "fire", "keys": ["@fire"], "text": "Fire"},
	{"id": "aim", "keys": ["@aim"], "text": "Aim"},
	{"id": "reload", "keys": ["@reload"], "text": "Reload"},
	{"id": "pickup", "keys": ["@interact"], "text": "Pick up"},
	{"id": "inventory", "keys": ["@inventory"], "text": "Inventory"},
	{"id": "grapple", "keys": ["@grapple"], "text": "Tethercaster"},
	{"id": "menu", "keys": ["Esc"], "text": "Menu"},
]

var player: Player
var alive_count := 0
var eliminations := 0

var _root: Control
var _crosshair: Control
var _compass: Control
var _status: Label
var _status_time := 5.0
var _mode_title: Label
var _mode_sub: Label
var _chip_alive: Label
var _chip_kills: Label
var _chip_damage: Label
var _feed: VBoxContainer
var _hints_box: VBoxContainer
var _hint_rows := {}
var _hints_fade := 0.0
var _vitals: Control
var _heal_label: Label
var _ammo_mag: Label
var _ammo_reserve: Label
var _weapon_name: Label
var _reloading: Label
var _slots: Control
var _prompt: PanelContainer
var _prompt_key: Label
var _prompt_text: Label
var _toast: PanelContainer
var _toast_label: Label
var _toast_time := 0.0
var _center: Label
var _capture_hint: PanelContainer
var _capture_label: Label
var _elim: Label
var _elim_time := 0.0
var _damage_glow: ColorRect
var _heal_glow: ColorRect
var _low_glow: ColorRect
var _icons := {}
var _arcs: Array[Dictionary] = []
var _hit_time := 0.0
var _hit_kill := false
var _numbers: Array[Dictionary] = []
var _heal_done_time := 0.0
var _t := 0.0


func _ready() -> void:
	_root = Control.new()
	_root.theme = UIStyle.theme()
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root)

	_damage_glow = _glow_rect(UIStyle.DANGER)
	_heal_glow = _glow_rect(UIStyle.SHIELD)
	_low_glow = _glow_rect(UIStyle.DANGER)

	_crosshair = _canvas(_draw_crosshair)
	_crosshair.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	# Top left: mode.
	var mode := UIStyle.vbox(4)
	UIStyle.place(_root, mode, 40, 36)
	var mt := UIStyle.hbox(12)
	_mode_title = _shadowed(UIStyle.tracked("Ringfall", 16, 0.14, UIStyle.TEXT, true))
	mt.add_child(_mode_title)
	var dash := ColorRect.new()
	dash.color = UIStyle.TEXT
	dash.custom_minimum_size = Vector2(22, 1.5)
	dash.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	mt.add_child(dash)
	mode.add_child(mt)
	_mode_sub = _shadowed(UIStyle.tracked("Solo", 16, 0.06, Color(UIStyle.TEXT, 0.85)))
	_mode_sub.uppercase = false
	mode.add_child(_mode_sub)

	# Top center: compass and status.
	_compass = Control.new()
	_compass.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_compass.draw.connect(_draw_compass)
	UIStyle.place(_root, _compass, -1, 20, -1, -1, 760, 48)
	_compass.anchor_left = 0.5
	_compass.anchor_right = 0.5
	_compass.offset_left = -380
	_compass.offset_right = 380
	_status = _shadowed(UIStyle.tracked("", 15, 0.26, UIStyle.TEXT))
	_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	UIStyle.place(_root, _status, -1, 80, -1, -1, 900, 24)
	_status.anchor_left = 0.5
	_status.anchor_right = 0.5
	_status.offset_left = -450
	_status.offset_right = 450

	# Top right: chips, then the feed.
	var chips := UIStyle.vbox(8)
	chips.alignment = BoxContainer.ALIGNMENT_END
	UIStyle.place(_root, chips, -1, 36, 44)
	var row1 := UIStyle.hbox(8)
	row1.alignment = BoxContainer.ALIGNMENT_END
	chips.add_child(row1)
	_chip_alive = _chip(row1, "survivors", "Alive")
	var row2 := UIStyle.hbox(8)
	row2.alignment = BoxContainer.ALIGNMENT_END
	chips.add_child(row2)
	_chip_kills = _chip(row2, "eliminations", "Kills")
	_chip_damage = _chip(row2, "marker-danger", "Damage")
	_feed = UIStyle.vbox(6)
	_feed.alignment = BoxContainer.ALIGNMENT_BEGIN
	UIStyle.place(_root, _feed, -1, 140, 44, -1, 600, 0)

	# Left: key hints.
	_hints_box = UIStyle.vbox(12)
	UIStyle.place(_root, _hints_box, 44, 320)
	set_hints(DEFAULT_HINTS)
	_hints_fade = 15.0

	# Bottom left: vitals.
	UIStyle.place(_root, _fade_rect(false), 0, -1, -1, 0, 640, 220)
	_vitals = Control.new()
	_vitals.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_vitals.draw.connect(_draw_vitals)
	UIStyle.place(_root, _vitals, 0, -1, -1, 0, 620, 150)
	_heal_label = _shadowed(UIStyle.tracked("", 15, 0.2, UIStyle.SUCCESS, true))
	UIStyle.place(_root, _heal_label, 44, -1, -1, 14)

	# Bottom right: ammunition, weapon name and slots, over a right-to-left fade.
	UIStyle.place(_root, _fade_rect(true), -1, -1, 0, 0, 700, 280)
	var load := UIStyle.vbox(0)
	load.alignment = BoxContainer.ALIGNMENT_END
	UIStyle.place(_root, load, -1, -1, 44, 40)
	var ammo := UIStyle.hbox(10)
	ammo.alignment = BoxContainer.ALIGNMENT_END
	load.add_child(ammo)
	_ammo_mag = _shadowed(UIStyle.label("", "display", 64, UIStyle.TEXT))
	ammo.add_child(_ammo_mag)
	_ammo_reserve = _shadowed(UIStyle.label("", "display", 34, Color(UIStyle.TEXT, 0.85)))
	_ammo_reserve.size_flags_vertical = Control.SIZE_SHRINK_END
	ammo.add_child(_ammo_reserve)
	_weapon_name = _shadowed(UIStyle.tracked("", 17, 0.22, UIStyle.TEXT, true))
	_weapon_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	load.add_child(UIStyle.spacer(8))
	load.add_child(_weapon_name)
	_reloading = _shadowed(UIStyle.tracked("Reloading…", 16, 0.22, UIStyle.WARNING, true))
	_reloading.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	load.add_child(_reloading)
	load.add_child(UIStyle.spacer(22))
	_slots = Control.new()
	_slots.custom_minimum_size = Vector2(84 * 5, 66)
	_slots.size_flags_horizontal = Control.SIZE_SHRINK_END
	_slots.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_slots.draw.connect(_draw_slots)
	load.add_child(_slots)

	# Interact prompt below the crosshair.
	_prompt = UIStyle.panel(Color(UIStyle.BG, 0.7), 0)
	var pm := MarginContainer.new()
	for side: Array in [["left", 14], ["right", 18], ["top", 8], ["bottom", 8]]:
		pm.add_theme_constant_override("margin_" + side[0], side[1])
	_prompt.add_child(pm)
	var ph := UIStyle.hbox(12)
	pm.add_child(ph)
	var pk := UIStyle.keycap("E", 16, true)
	_prompt_key = pk.get_child(0) as Label
	ph.add_child(pk)
	_prompt_text = UIStyle.tracked("", 16, 0.16, UIStyle.TEXT, true)
	ph.add_child(_prompt_text)
	_root.add_child(_prompt)

	# Toast: top center, accent bar on the left.
	_toast = PanelContainer.new()
	var tsb := UIStyle.box(Color(UIStyle.BG, 0.94))
	tsb.border_color = UIStyle.ACCENT
	tsb.border_width_left = 3
	tsb.content_margin_left = 22
	tsb.content_margin_right = 22
	tsb.content_margin_top = 14
	tsb.content_margin_bottom = 14
	_toast.add_theme_stylebox_override("panel", tsb)
	_toast_label = UIStyle.label("", "ui", 18, UIStyle.TEXT)
	_toast.add_child(_toast_label)
	_root.add_child(_toast)

	_center = _shadowed(UIStyle.title("", 72, 1.0))
	_center.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_center.visible = false
	_root.add_child(_center)

	_elim = _shadowed(UIStyle.tracked("", 18, 0.3, UIStyle.ACCENT, true))
	_elim.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_root.add_child(_elim)

	_capture_hint = UIStyle.panel(Color(UIStyle.BG, 0.7), 0)
	var cm := MarginContainer.new()
	for side: Array in [["left", 18], ["right", 18], ["top", 10], ["bottom", 10]]:
		cm.add_theme_constant_override("margin_" + side[0], side[1])
	_capture_hint.add_child(cm)
	_capture_label = UIStyle.tracked("", 16, 0.2, UIStyle.TEXT)
	cm.add_child(_capture_label)
	_root.add_child(_capture_hint)


func bind(p: Player) -> void:
	player = p
	p.health.damaged.connect(_on_damaged)
	p.weapons.hit_confirmed.connect(func(_d: float, killed: bool) -> void:
		_hit_time = 0.26
		_hit_kill = killed
		if killed:
			_elim.text = "Eliminated"
			_elim_time = 1.3)
	p.weapons.hit_detail.connect(_hit_number)
	p.heal_finished.connect(func(def: HealDef) -> void:
		_heal_done_time = 0.6
		toast("%s used" % def.display_name))
	p.heal_interrupted.connect(func(reason: String) -> void: toast("Interrupted · %s. Item kept." % reason))
	p.notice.connect(toast)


## Top-left mode label, e.g. ("Practice", "Infinite ammo").
func set_mode(title: String, sub: String) -> void:
	_mode_title.text = title
	_mode_sub.text = sub


## The status line under the compass; fades after a few seconds.
func set_status(text: String) -> void:
	_status.text = text
	_status_time = 5.0


## Hints at the left: [{id, keys: ["@action" or key], text}]. Done hints dim.
func set_hints(items: Array) -> void:
	for c in _hints_box.get_children():
		c.queue_free()
	_hint_rows.clear()
	for it: Dictionary in items:
		var row := UIStyle.hbox(12)
		for k: String in it.keys:
			var cap := UIStyle.keycap(GameSettings.key_for(k.substr(1)) if k.begins_with("@") else k, 15)
			var sb := (cap.get_theme_stylebox("panel") as StyleBoxFlat).duplicate() as StyleBoxFlat
			sb.bg_color = Color(UIStyle.BG, 0.55)
			cap.add_theme_stylebox_override("panel", sb)
			row.add_child(cap)
		row.add_child(_shadowed(UIStyle.tracked(it.text, 15, 0.16, UIStyle.TEXT)))
		_hints_box.add_child(row)
		_hint_rows[it.id] = row
	_hints_fade = 0.0


func mark_hint(id: String) -> void:
	if _hint_rows.has(id):
		(_hint_rows[id] as Control).modulate.a = 0.35


## Hints stay up for `seconds`, then fade (0 keeps them).
func fade_hints_after(seconds: float) -> void:
	_hints_fade = seconds


# ---------------------------------------------------------------- helpers

func _shadowed(l: Label) -> Label:
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.7))
	l.add_theme_constant_override("shadow_offset_y", 1)
	l.add_theme_constant_override("shadow_outline_size", 4)
	return l


## A skewed stat chip: 40 px tall, dark backing, 2 px left edge, icon and a
## 26 px number.
func _chip(parent: Control, icon: String, tip: String) -> Label:
	var chip := Control.new()
	chip.custom_minimum_size = Vector2(110, 40)
	chip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	chip.tooltip_text = tip
	var h := UIStyle.hbox(8)
	UIStyle.place(chip, h, 22, 0, 18, 0)
	h.alignment = BoxContainer.ALIGNMENT_CENTER
	var ic := TextureRect.new()
	ic.texture = _icon(ICONS % icon)
	ic.custom_minimum_size = Vector2(22, 22)
	ic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	ic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	ic.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	ic.modulate = Color(UIStyle.TEXT, 0.9)
	h.add_child(ic)
	var n := UIStyle.label("0", "display", 26, UIStyle.TEXT)
	n.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	h.add_child(n)
	chip.draw.connect(func() -> void:
		var sk := 10.0
		var w := chip.size.x
		chip.draw_colored_polygon(PackedVector2Array([Vector2(sk, 0), Vector2(w, 0), Vector2(w - sk, 40), Vector2(0, 40)]), Color(UIStyle.BG, 0.62))
		chip.draw_line(Vector2(sk, 0), Vector2(0, 40), UIStyle.LINE, 2.0))
	n.resized.connect(func() -> void:
		chip.custom_minimum_size.x = maxf(110.0, n.size.x + 22 + 8 + 22 + 18)
		chip.queue_redraw())
	parent.add_child(chip)
	return n


## A soft dark backing that fades away from the left or right screen edge.
func _fade_rect(from_right: bool) -> ColorRect:
	var r := ColorRect.new()
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/hud_fade.gdshader")
	m.set_shader_parameter("from_right", from_right)
	r.material = m
	return r


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


func _icon(path: String) -> Texture2D:
	if not _icons.has(path):
		_icons[path] = load(path) if path != "" and ResourceLoader.exists(path) else null
	return _icons[path]


func toast(text: String) -> void:
	_toast_label.text = text
	_toast_time = 3.0


func feed(text: String) -> void:
	var l := _shadowed(UIStyle.tracked(text, 15, 0.12, UIStyle.TEXT, true))
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	l.custom_minimum_size.x = 600
	_feed.add_child(l)
	var t := l.create_tween()
	t.tween_interval(6.0)
	t.tween_property(l, "modulate:a", 0.0, 0.6)
	t.tween_callback(l.queue_free)
	while _feed.get_child_count() > 5:
		_feed.get_child(0).free()


func show_center(text: String) -> void:
	_center.text = text
	_center.visible = text != ""


# ---------------------------------------------------------------- feedback

func _on_damaged(amount: float, from: Vector3, _attacker: Node) -> void:
	if amount <= 0.0 or from == Vector3.ZERO or not GameSettings.b("damage_direction"):
		return
	_arcs.append({"from": from, "age": 0.0})
	if _arcs.size() > 6:
		_arcs.remove_at(0)
	var rel := _relative_angle(from)
	var m := _damage_glow.material as ShaderMaterial
	m.set_shader_parameter("direction", Vector2(sin(rel), -cos(rel)))
	m.set_shader_parameter("strength", 0.85)


func _relative_angle(from: Vector3) -> float:
	var to := from - player.global_position
	var bearing := atan2(to.x, -to.z)
	var facing := atan2(-player.global_basis.z.x, player.global_basis.z.z)
	return wrapf(bearing - facing, -PI, PI)


## A hit number by the crosshair: 34 px, white; a 28 px shield before it on
## shield hits, a 46 px cracked shield (and "SHIELD BROKEN") on the break.
func _hit_number(amount: float, kind: String) -> void:
	_numbers.append({"n": roundi(amount), "kind": kind, "age": 0.0, "x": randf_range(30.0, 60.0)})
	if _numbers.size() > 8:
		_numbers.remove_at(0)
	if kind == "break":
		_elim.text = "Shield broken"
		_elim_time = 1.1


# ---------------------------------------------------------------- frame

func _process(delta: float) -> void:
	if player == null:
		return
	# The HUD hides under menus (the in-match menu, settings, results).
	_root.visible = not Menus.is_open()
	var k := GameSettings.f("hud_scale") / 100.0
	var view := get_viewport().get_visible_rect().size
	_root.scale = Vector2(k, k)
	_root.size = view / k
	var c := _root.size * 0.5
	_t += delta

	_capture_hint.visible = not MouseLock.is_captured() and player.combat_input and player.is_alive()
	_capture_label.text = "Capturing the cursor…" if MouseLock.is_pending() else "Click to capture the cursor  ·  Esc for menu"
	_capture_hint.position = Vector2(c.x - _capture_hint.size.x * 0.5, _root.size.y * 0.62)

	_status_time = maxf(0.0, _status_time - delta)
	_status.modulate.a = clampf(_status_time / 0.6, 0.0, 1.0)
	if _hints_fade > 0.0:
		_hints_fade = maxf(0.0, _hints_fade - delta)
		_hints_box.modulate.a = clampf(_hints_fade / 0.8, 0.0, 1.0)
		if _hints_fade == 0.0:
			_hints_box.modulate.a = 0.0

	_toast_time = maxf(0.0, _toast_time - delta)
	_toast.visible = _toast_time > 0.0
	_toast.modulate.a = clampf(_toast_time / 0.3, 0.0, 1.0)
	_toast.position = Vector2(c.x - _toast.size.x * 0.5, 96)
	_center.position = Vector2(c.x - _center.size.x * 0.5, c.y - 160)
	_elim_time = maxf(0.0, _elim_time - delta)
	_elim.modulate.a = clampf(_elim_time / 0.3, 0.0, 1.0) * clampf((1.3 - _elim_time) / 0.15, 0.0, 1.0) if _elim_time > 0.0 else 0.0
	_elim.position = Vector2(c.x - _elim.size.x * 0.5, c.y + 46)
	_hit_time = maxf(0.0, _hit_time - delta)
	_heal_done_time = maxf(0.0, _heal_done_time - delta)
	for n in _numbers:
		n.age = float(n.age) + delta
	_numbers.assign(_numbers.filter(func(n: Dictionary) -> bool: return float(n.age) < (1.1 if n.kind == "break" else 0.7)))

	for a in _arcs:
		a.age = float(a.age) + delta
	_arcs.assign(_arcs.filter(func(a: Dictionary) -> bool: return float(a.age) < ARC_LIFE))
	var dm := _damage_glow.material as ShaderMaterial
	dm.set_shader_parameter("strength", maxf(0.0, float(dm.get_shader_parameter("strength")) - delta * 1.1))
	var hm := _heal_glow.material as ShaderMaterial
	var healing := player.using != null
	hm.set_shader_parameter("glow_color", UIStyle.SHIELD)
	hm.set_shader_parameter("strength", (0.45 + 0.15 * sin(_t * 5.2)) if healing else _heal_done_time)
	hm.set_shader_parameter("width", 0.35)
	var lm := _low_glow.material as ShaderMaterial
	var low := player.is_alive() and player.health.health <= 30.0 and GameSettings.b("low_health")
	var pulse := 0.0 if GameSettings.b("reduce_motion") else 0.15 * sin(_t * 3.9)
	lm.set_shader_parameter("strength", (0.4 + pulse) if low else 0.0)
	_heal_label.text = "Healing…  %.1f s" % maxf(0.0, player.use_left) if healing else ""

	_update_loadout()
	_update_prompt(c)
	_chip_alive.text = str(alive_count)
	_chip_kills.text = str(eliminations)
	_chip_damage.text = str(roundi(MatchStats.damage))
	_crosshair.queue_redraw()
	_compass.queue_redraw()
	_vitals.queue_redraw()
	_slots.queue_redraw()


func _update_loadout() -> void:
	var w := player.weapons.weapon()
	var s := player.inventory.selected_stack()
	_reloading.visible = player.weapons.is_reloading()
	if w and s:
		_ammo_mag.text = str(s.mag)
		_ammo_reserve.text = "/ %d" % player.inventory.ammo_count(w.ammo_type)
		_weapon_name.text = w.display_name
		_ammo_mag.add_theme_color_override("font_color", UIStyle.DANGER if s.mag == 0 else UIStyle.TEXT)
	elif s:
		_ammo_mag.text = str(s.qty) if s.def.stack_max > 1 else "–"
		_ammo_reserve.text = ""
		_weapon_name.text = s.def.display_name
		_ammo_mag.add_theme_color_override("font_color", UIStyle.TEXT)
	else:
		_ammo_mag.text = "–"
		_ammo_reserve.text = ""
		_weapon_name.text = "Unarmed"


func _update_prompt(c: Vector2) -> void:
	var p := player.focused_pickup
	_prompt.visible = player.is_alive() and p != null
	if not _prompt.visible:
		return
	var verb := "Pick up"
	if not p.is_ammo():
		var pv := player.inventory.preview(p.stack)
		if pv.full:
			verb = "Can't carry more ·"
		elif pv.blocked:
			verb = "Swap for"
	_prompt_key.text = GameSettings.key_for("interact").to_upper()
	_prompt_text.text = "%s %s" % [verb, p.display_name()]
	_prompt.position = Vector2(c.x - _prompt.size.x * 0.5, c.y + 90)


# ---------------------------------------------------------------- drawing

func _draw_crosshair() -> void:
	var c := _crosshair.size * 0.5
	var color := Color(1, 1, 1, 0.95)
	var gap := 8.0 + player.weapons.spread_now * 3.0
	if player.inventory.selected_stack() and player.inventory.selected_stack().def.id == &"tethercaster":
		gap = 8.0
		if player.tether.aim == Tethercaster.Aim.IN_RANGE and player.tether.charge() >= 1.0:
			color = UIStyle.ACCENT
	if not player.weapons.aiming:
		for d: Vector2 in [Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT]:
			_crosshair.draw_line(c + d * gap, c + d * (gap + 16.0), Color(0, 0, 0, 0.6), 4.0)
			_crosshair.draw_line(c + d * gap, c + d * (gap + 16.0), color, 2.0)
	_crosshair.draw_circle(c, 3.0, Color(0, 0, 0, 0.6))
	_crosshair.draw_circle(c, 2.0, color)
	# Hit marker: a 44 px X with an open middle.
	if _hit_time > 0.0:
		var a := _hit_time / 0.26
		var hc := UIStyle.DANGER if _hit_kill else Color(1, 1, 1)
		hc.a = a
		var grow := 1.0 + 0.25 * a
		for d: Vector2 in [Vector2(1, 1), Vector2(-1, 1), Vector2(1, -1), Vector2(-1, -1)]:
			var n := d.normalized()
			_crosshair.draw_line(c + n * 8.8 * grow, c + n * 22.0 * grow, hc, 3.0)
	# Hit numbers rising from just right of the crosshair.
	var font := UIStyle.font("display")
	for n in _numbers:
		var life := 1.1 if n.kind == "break" else 0.7
		var k := float(n.age) / life
		var at := c + Vector2(float(n.x), -70.0 - 50.0 * k)
		var alpha := clampf(1.0 - k, 0.0, 1.0)
		var x := at.x
		if n.kind == "shield":
			Glyph.draw_shield(_crosshair, Vector2(x, at.y - 30), 28.0, Color(UIStyle.SHIELD, alpha), false)
			x += 34.0
		elif n.kind == "break":
			var pop := minf(1.0, float(n.age) / 0.42)
			var s := 46.0 * (0.4 + 0.85 * pop if pop < 0.6 else 1.25 - 0.25 * (pop - 0.6) / 0.4)
			Glyph.draw_shield(_crosshair, Vector2(x + (46.0 - s) * 0.5, at.y - 38 + (46.0 - s) * 0.5), s, Color(UIStyle.SHIELD, alpha), true)
			x += 52.0
		_crosshair.draw_string_outline(font, Vector2(x, at.y), str(n.n), HORIZONTAL_ALIGNMENT_LEFT, -1, 34, 6, Color(0, 0, 0, 0.5 * alpha))
		_crosshair.draw_string(font, Vector2(x, at.y), str(n.n), HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Color(UIStyle.TEXT, alpha))
	# Damage direction arcs.
	for a in _arcs:
		var rel := _relative_angle(a.from) - PI / 2.0
		var fade := 1.0 - float(a.age) / ARC_LIFE
		var col := UIStyle.DANGER
		col.a = fade
		_crosshair.draw_arc(c, 100.0, rel - 0.42, rel + 0.42, 24, Color(UIStyle.DANGER, 0.35 * fade), 15.0, true)
		_crosshair.draw_arc(c, 100.0, rel - 0.4, rel + 0.4, 24, col, 9.0, true)
	# Healing and reload rings.
	if player.using:
		var hk := 1.0 - player.use_left / player.using.use_time
		_crosshair.draw_arc(c, 36.0, 0.0, TAU, 48, Color(0, 0, 0, 0.4), 4.0, true)
		_crosshair.draw_arc(c, 36.0, -PI / 2.0, -PI / 2.0 + TAU * clampf(hk, 0.0, 1.0), 48, UIStyle.SHIELD, 4.0, true)
	if player.weapons.is_reloading():
		_crosshair.draw_arc(c, 30.0, 0.0, TAU, 40, Color(0, 0, 0, 0.35), 3.0, true)
		_crosshair.draw_arc(c, 30.0, -PI / 2.0, -PI / 2.0 + TAU * player.weapons.reload_progress(), 40, UIStyle.WARNING, 3.0, true)


## 760 px compass: a tick label every 15°, cardinal letters in the display
## face, fading toward the ends, with a 2 × 12 marker at the center.
func _draw_compass() -> void:
	var w := _compass.size.x
	var heading := fposmod(-rad_to_deg(player.rotation.y), 360.0)
	var ppd := 5.4
	var names := {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW"}
	var lf := UIStyle.tracked_font(15, 0.0)
	var df := UIStyle.font("display")
	var start := int(floor((heading - w / ppd * 0.5) / 15.0)) * 15
	for d in range(start, start + int(w / ppd) + 30, 15):
		var x := w * 0.5 + (d - heading) * ppd
		if x < 0.0 or x > w:
			continue
		var edge := minf(x, w - x) / (w * 0.18)
		var a := clampf(edge, 0.0, 1.0)
		var n := posmod(d, 360)
		if names.has(n):
			var txt: String = names[n]
			var fs := 28
			var tw := df.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			_compass.draw_string_outline(df, Vector2(x - tw * 0.5, 34), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, 4, Color(0, 0, 0, 0.45 * a))
			_compass.draw_string(df, Vector2(x - tw * 0.5, 34), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(UIStyle.TEXT, a))
		else:
			var txt2 := str(n)
			var tw2 := lf.get_string_size(txt2, HORIZONTAL_ALIGNMENT_LEFT, -1, 15).x
			_compass.draw_string_outline(lf, Vector2(x - tw2 * 0.5, 30), txt2, HORIZONTAL_ALIGNMENT_LEFT, -1, 15, 4, Color(0, 0, 0, 0.45 * a))
			_compass.draw_string(lf, Vector2(x - tw2 * 0.5, 30), txt2, HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color(UIStyle.TEXT, 0.85 * a))
	_compass.draw_rect(Rect2(w * 0.5 - 1, 0, 2, 12), UIStyle.TEXT)


## Vitals: two rows (28 px icon, 280 × 12
## bar, 36 px number).
func _draw_vitals() -> void:
	var h := player.health
	_vital_row(40.0, _icon(ICONS % "health"), h.health, h.max_health, UIStyle.HEALTH, h.health <= 30.0)
	_vital_row(82.0, _icon(ICONS % "shield"), h.shield, h.max_shield, UIStyle.SHIELD, false)


func _vital_row(y: float, icon: Texture2D, value: float, max_value: float, color: Color, low: bool) -> void:
	if icon:
		_vitals.draw_texture_rect(icon, Rect2(44, y, 28, 28), false, color)
	var bar := Rect2(44 + 30 + 16, y + 8, 280, 12)
	_vitals.draw_rect(bar, Color(UIStyle.BG, 0.7))
	_vitals.draw_rect(Rect2(bar.position, Vector2(bar.size.x * clampf(value / max_value, 0.0, 1.0), bar.size.y)), color)
	var f := UIStyle.font("display")
	var p := Vector2(bar.end.x + 16, y + 30)
	_vitals.draw_string_outline(f, p, str(int(ceil(value))), HORIZONTAL_ALIGNMENT_LEFT, -1, 36, 6, Color(0, 0, 0, 0.4))
	_vitals.draw_string(f, p, str(int(ceil(value))), HORIZONTAL_ALIGNMENT_LEFT, -1, 36, UIStyle.DANGER if low else UIStyle.TEXT)


## Five 84 × 66 slots split by 1 px rules: line icon (56 × 28), the number,
## and a 60 × 4 accent bar under the equipped slot.
func _draw_slots() -> void:
	var inv := player.inventory
	var lf := UIStyle.tracked_font(16, 0.0)
	# Right-to-left fade backing behind the loadout.
	for i in Inventory.SLOT_COUNT:
		var x := i * 84.0
		var s := inv.get_slot(i)
		var on := inv.selected == i
		if i > 0:
			_slots.draw_rect(Rect2(x, 4, 1, 58), UIStyle.LINE)
		var col := UIStyle.TEXT if on else Color(UIStyle.TEXT, 0.7)
		if s:
			var icon := _icon(UIStyle.item_icon(s.def.id))
			if icon:
				_slots.draw_texture_rect(icon, Rect2(x + 24, 0, 36, 36), false, col)
			if s.def.is_weapon() or s.def.stack_max > 1:
				var q := str(s.mag) if s.def.is_weapon() else "×%d" % s.qty
				_slots.draw_string(lf, Vector2(x + 50, 30), q, HORIZONTAL_ALIGNMENT_LEFT, 34, 12, Color(col, 0.8))
			if s.def.id == &"tethercaster":
				var ch := player.tether.charge()
				_slots.draw_rect(Rect2(x + 14, 33, 56 * ch, 2), UIStyle.ACCENT if ch >= 1.0 else UIStyle.TEXT_2)
		else:
			_slots.draw_rect(Rect2(x + 31, 15, 22, 2), Color(UIStyle.TEXT, 0.5))
		var num := str(i + 1)
		var tw := lf.get_string_size(num, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		_slots.draw_string(lf, Vector2(x + 42 - tw * 0.5, 54), num, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, col)
		if on:
			_slots.draw_rect(Rect2(x + 12, 60, 60, 4), UIStyle.ACCENT)


func _unhandled_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key and key.pressed and not key.echo and key.physical_keycode == KEY_H:
		var showing := _hints_box.modulate.a > 0.5
		_hints_box.modulate.a = 0.0 if showing else 1.0
		_hints_fade = 0.0
