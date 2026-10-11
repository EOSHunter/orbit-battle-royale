extends CanvasLayer
## Playground HUD: crosshair with Tethercaster eligibility, speed and state,
## landing readout, tether charge, controls help, and the live tuning panel.
## Colors come from the Orbit Royale design tokens.

const ACCENT := Color("c5f277")
const TEXT := Color("f3f5fa")
const TEXT_2 := Color("b4bfd0")
const DANGER := Color("ff797f")
const WARNING := Color("ffd18a")
const SHIELD := Color("70d6ff")
const SCRIM := Color(0.043, 0.063, 0.106, 0.72)

## [property, label, min, max, step]
const TUNABLES := [
	["walk_speed", "Walk speed", 1.0, 15.0, 0.1],
	["sprint_speed", "Sprint speed", 1.0, 20.0, 0.1],
	["jump_velocity", "Jump velocity", 2.0, 15.0, 0.1],
	["gravity", "Gravity", 5.0, 40.0, 0.5],
	["air_speed", "Air control speed", 1.0, 15.0, 0.1],
	["air_accel", "Air acceleration", 1.0, 100.0, 1.0],
	["grapple_range", "Tether range", 10.0, 120.0, 1.0],
	["reel_speed", "Reel speed", 0.0, 40.0, 0.5],
	["reel_accel", "Reel pull", 0.0, 80.0, 1.0],
	["swing_steer", "Swing steering", 0.0, 40.0, 0.5],
	["grapple_max_speed", "Tether max speed", 10.0, 80.0, 1.0],
	["release_boost", "Jump-release boost", 0.0, 15.0, 0.1],
	["grapple_cooldown", "Tether recharge", 0.0, 15.0, 0.1],
	["mouse_sensitivity", "Mouse sensitivity", 0.1, 3.0, 0.05],
	["fov", "Field of view", 60.0, 120.0, 1.0],
]

var player: Player

var _crosshair: Control
var _aim_label: Label
var _speed: Label
var _state: Label
var _landing: Label
var _charge_bar: ColorRect
var _charge_fill: ColorRect
var _charge_label: Label
var _help: Label
var _capture_hint: Label
var _tuning: PanelContainer
var _landing_time := 0.0


func _ready() -> void:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	_crosshair = Control.new()
	_pin(_crosshair, Vector2(0.5, 0.5), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_BOTH), Vector2.ZERO)
	_crosshair.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_crosshair.draw.connect(_draw_crosshair)
	root.add_child(_crosshair)

	_aim_label = _label(18, TEXT)
	_aim_label.custom_minimum_size = Vector2(400, 28)
	_pin(_aim_label, Vector2(0.5, 0.5), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_END), Vector2(0, 34))
	_aim_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	root.add_child(_aim_label)

	var readout := _panel(root, Vector2(0, 0), Vector2i(Control.GROW_DIRECTION_END, Control.GROW_DIRECTION_END), Vector2(24, 24))
	var box := VBoxContainer.new()
	readout.add_child(box)
	_speed = _label(40, TEXT)
	_state = _label(16, TEXT_2)
	_landing = _label(16, ACCENT)
	box.add_child(_speed)
	box.add_child(_state)
	box.add_child(_landing)

	var charge := _panel(root, Vector2(0.5, 1), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_BEGIN), Vector2(0, -32))
	var cbox := VBoxContainer.new()
	cbox.custom_minimum_size = Vector2(320, 0)
	charge.add_child(cbox)
	_charge_label = _label(16, TEXT)
	cbox.add_child(_charge_label)
	_charge_bar = ColorRect.new()
	_charge_bar.color = Color("213047")
	_charge_bar.custom_minimum_size = Vector2(320, 6)
	cbox.add_child(_charge_bar)
	_charge_fill = ColorRect.new()
	_charge_fill.color = ACCENT
	_charge_fill.size = Vector2(320, 6)
	_charge_bar.add_child(_charge_fill)

	var help_panel := _panel(root, Vector2(0, 1), Vector2i(Control.GROW_DIRECTION_END, Control.GROW_DIRECTION_BEGIN), Vector2(24, -24))
	_help = _label(15, TEXT_2)
	_help.text = "WASD move · Shift sprint · C crouch · Space jump\nClick / Q fire or release tether · Space while tethered: release with boost\nHold C while tethered: swing without reeling\n1–4 teleport · R respawn · F1 tuning · Esc free the mouse\nController: sticks, A jump, RT tether, B crouch, L3 sprint, Start tuning"
	help_panel.add_child(_help)

	_capture_hint = _label(22, TEXT)
	_capture_hint.text = "Click to play"
	_capture_hint.custom_minimum_size = Vector2(400, 32)
	_pin(_capture_hint, Vector2(0.5, 0.5), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_END), Vector2(0, 80))
	_capture_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	root.add_child(_capture_hint)

	_build_tuning(root)


func _label(size: int, color: Color) -> Label:
	var l := Label.new()
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	l.add_theme_constant_override("shadow_offset_y", 1)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


## Pin a control to an anchor point and let it grow away from it, so it holds
## its place at any window size.
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


func _panel(parent: Control, anchor: Vector2, grow: Vector2i, offset: Vector2) -> PanelContainer:
	var p := PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = SCRIM
	sb.set_corner_radius_all(4)
	sb.set_content_margin_all(12)
	p.add_theme_stylebox_override("panel", sb)
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(p)
	_pin(p, anchor, grow, offset)
	return p


func _build_tuning(root: Control) -> void:
	_tuning = PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color("141d2d")
	sb.border_color = Color("46566d")
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(8)
	sb.set_content_margin_all(16)
	_tuning.add_theme_stylebox_override("panel", sb)
	_tuning.visible = false
	root.add_child(_tuning)
	_pin(_tuning, Vector2(1, 0), Vector2i(Control.GROW_DIRECTION_BEGIN, Control.GROW_DIRECTION_END), Vector2(-24, 24))
	_tuning.custom_minimum_size = Vector2(396, 0)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	_tuning.add_child(box)
	var title := _label(20, TEXT)
	title.text = "Tuning (live, not saved)"
	box.add_child(title)
	for t: Array in TUNABLES:
		var row := HBoxContainer.new()
		var name_l := _label(15, TEXT_2)
		name_l.text = t[1]
		name_l.custom_minimum_size = Vector2(170, 0)
		var value_l := _label(15, TEXT)
		value_l.custom_minimum_size = Vector2(56, 0)
		value_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		var slider := HSlider.new()
		slider.min_value = t[2]
		slider.max_value = t[3]
		slider.step = t[4]
		slider.custom_minimum_size = Vector2(150, 24)
		slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		slider.set_meta("prop", t[0])
		slider.value_changed.connect(func(v: float) -> void:
			player.tuning.set(t[0], v)
			value_l.text = str(snappedf(v, t[4])))
		row.add_child(name_l)
		row.add_child(slider)
		row.add_child(value_l)
		box.add_child(row)
	var reset := Button.new()
	reset.text = "Reset to defaults"
	reset.pressed.connect(func() -> void:
		var fresh := MoveTuning.new()
		for t: Array in TUNABLES:
			player.tuning.set(t[0], fresh.get(t[0]))
		_sync_sliders())
	box.add_child(reset)


func _sync_sliders() -> void:
	for slider: HSlider in _tuning.find_children("*", "HSlider", true, false):
		slider.set_value_no_signal(player.tuning.get(slider.get_meta("prop")))
		slider.value_changed.emit(slider.value)


var _lock_refused := false


func set_lock_refused(refused: bool) -> void:
	_lock_refused = refused
	if refused:
		_capture_hint.text = "This browser view blocks mouse capture.\nHold right-click and move the mouse to look. Left click or Q fires the tether.\nFor full mouse control, open the game in Chrome, Edge or Firefox."
		_capture_hint.add_theme_font_size_override("font_size", 17)
		_capture_hint.custom_minimum_size = Vector2(760, 0)
		_pin(_capture_hint, Vector2(0.5, 0), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_END), Vector2(0, 24))
	else:
		_capture_hint.text = "Click to play"
		_capture_hint.add_theme_font_size_override("font_size", 22)
		_capture_hint.custom_minimum_size = Vector2(400, 32)
		_pin(_capture_hint, Vector2(0.5, 0.5), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_END), Vector2(0, 80))


func is_tuning_open() -> bool:
	return _tuning.visible


func toggle_tuning() -> void:
	_tuning.visible = not _tuning.visible
	if _tuning.visible:
		_sync_sliders()
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func show_landing(drop: float) -> void:
	_landing.text = "Landed from %.1f m · no fall damage" % drop
	_landing_time = 3.0


func _process(delta: float) -> void:
	if player == null:
		return
	var captured := Input.mouse_mode == Input.MOUSE_MODE_CAPTURED
	_capture_hint.visible = not captured and not _tuning.visible
	_speed.text = "%.1f m/s" % player.horizontal_speed()
	var state_name: String = ["On ground", "In air", "Tethered"][player.state]
	if player.state == Player.State.TETHERED:
		state_name += " · rope %.1f m%s" % [player.tether.rope_length, " · swinging" if Input.is_action_pressed("crouch") else ""]
	if player.sprinting:
		state_name += " · sprinting"
	if player.crouching:
		state_name += " · crouched"
	_state.text = "%s · height %.1f m" % [state_name, player.global_position.y]
	_landing_time = maxf(0.0, _landing_time - delta)
	_landing.modulate.a = clampf(_landing_time, 0.0, 1.0)

	var t := player.tether
	var c := t.charge()
	_charge_fill.size.x = _charge_bar.size.x * c
	_charge_fill.color = ACCENT if c >= 1.0 else TEXT_2
	if t.is_attached():
		_charge_label.text = "Tethercaster · attached"
	elif c < 1.0:
		_charge_label.text = "Tethercaster · recharging %.1f s" % t.cooldown_left
	else:
		_charge_label.text = "Tethercaster · ready"

	match t.aim:
		Tethercaster.Aim.IN_RANGE:
			_aim_label.text = "%.0f m" % t.aim_distance
			_aim_label.add_theme_color_override("font_color", ACCENT if c >= 1.0 else TEXT_2)
		Tethercaster.Aim.OUT_OF_RANGE:
			_aim_label.text = "Out of range · %.0f m" % t.aim_distance
			_aim_label.add_theme_color_override("font_color", TEXT_2)
		Tethercaster.Aim.NOT_HOOKABLE:
			_aim_label.text = "Can't hook this surface"
			_aim_label.add_theme_color_override("font_color", DANGER)
		_:
			_aim_label.text = ""
	if t.is_attached():
		_aim_label.text = ""
	_crosshair.queue_redraw()


func _draw_crosshair() -> void:
	if player == null:
		return
	var t := player.tether
	var color := TEXT
	if not t.is_attached():
		if t.aim == Tethercaster.Aim.IN_RANGE and t.charge() >= 1.0:
			color = ACCENT
		elif t.aim == Tethercaster.Aim.NOT_HOOKABLE:
			color = DANGER
	var gap := 6.0
	var arm := 9.0
	for d: Vector2 in [Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT]:
		_crosshair.draw_line(d * gap, d * (gap + arm), Color(0, 0, 0, 0.5), 4.0)
		_crosshair.draw_line(d * gap, d * (gap + arm), color, 2.0)
	# Hook-ready ring around the crosshair.
	if t.aim == Tethercaster.Aim.IN_RANGE and not t.is_attached():
		_crosshair.draw_arc(Vector2.ZERO, 22.0, 0.0, TAU * t.charge(), 48, color, 2.0, true)
