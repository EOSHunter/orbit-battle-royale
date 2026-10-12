extends CanvasLayer
## Playground HUD: crosshair with Tethercaster eligibility, speed and state,
## landing readout, tether charge and controls help. Tuning lives in TuningPanel (F1).
## Colors come from the Orbit Royale design tokens.

const ACCENT := Color("c5f277")
const TEXT := Color("f3f5fa")
const TEXT_2 := Color("b4bfd0")
const DANGER := Color("ff797f")
const WARNING := Color("ffd18a")
const SHIELD := Color("70d6ff")
const SCRIM := Color(0.043, 0.063, 0.106, 0.72)

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
var _landing_time := 0.0


func _ready() -> void:
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
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
	_help.text = "WASD move · Shift sprint · C crouch · Space jump\nClick, Q or a mouse side button: fire or release the tether · Space while tethered: release with boost\nHold C while tethered: swing without reeling\nF6–F9 teleport · F5 respawn · F1 tuning (saved) · F10 next scene · Esc menu\nController: sticks, A jump, RT or R3 tether, B crouch, L3 sprint, Start tuning"
	help_panel.add_child(_help)

	_capture_hint = _label(22, TEXT)
	_capture_hint.text = "Click to capture the cursor · Esc for menu"
	_capture_hint.custom_minimum_size = Vector2(640, 32)
	_pin(_capture_hint, Vector2(0.5, 0.5), Vector2i(Control.GROW_DIRECTION_BOTH, Control.GROW_DIRECTION_END), Vector2(0, 80))
	_capture_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	root.add_child(_capture_hint)



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


func show_landing(drop: float) -> void:
	_landing.text = "Landed from %.1f m · no fall damage" % drop
	_landing_time = 3.0


func _process(delta: float) -> void:
	if player == null:
		return
	_capture_hint.visible = not MouseLock.is_captured() and player.combat_input
	_capture_hint.text = "Capturing the cursor…" if MouseLock.is_pending() else "Click to capture the cursor · Esc for menu"
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
