extends CanvasLayer
## Movement and Tethercaster tuning (autoload "TuningPanel"), available in every
## scene with F1. Changes apply live to the player and are saved on this device
## (user://move_tuning.tres; browser storage on the web), so the values you set
## are the ones you play with next time.

const TEXT := Color("f3f5fa")
const TEXT_2 := Color("b4bfd0")
const SAVE_DELAY := 0.5

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

var _panel: PanelContainer
var _status: Label
var _save_in := -1.0


func _ready() -> void:
	layer = 50
	process_mode = Node.PROCESS_MODE_ALWAYS
	_panel = PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color("141d2d")
	sb.border_color = Color("46566d")
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(8)
	sb.set_content_margin_all(16)
	_panel.add_theme_stylebox_override("panel", sb)
	_panel.visible = false
	_panel.anchor_left = 1.0
	_panel.anchor_right = 1.0
	_panel.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_panel.offset_left = -24
	_panel.offset_right = -24
	_panel.offset_top = 24
	_panel.custom_minimum_size = Vector2(420, 0)
	add_child(_panel)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	_panel.add_child(box)
	box.add_child(_label("Tuning · F1 closes", 20, TEXT))
	for t: Array in TUNABLES:
		var row := HBoxContainer.new()
		var name_l := _label(t[1], 15, TEXT_2)
		name_l.custom_minimum_size = Vector2(170, 0)
		var value_l := _label("", 15, TEXT)
		value_l.custom_minimum_size = Vector2(56, 0)
		value_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		var slider := HSlider.new()
		slider.min_value = t[2]
		slider.max_value = t[3]
		slider.step = t[4]
		slider.custom_minimum_size = Vector2(160, 24)
		slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		slider.set_meta("prop", t[0])
		slider.value_changed.connect(func(v: float) -> void:
			var p := _player()
			if p:
				p.tuning.set(t[0], v)
			value_l.text = str(snappedf(v, t[4]))
			_save_in = SAVE_DELAY)
		row.add_child(name_l)
		row.add_child(slider)
		row.add_child(value_l)
		box.add_child(row)
	var reset := Button.new()
	reset.text = "Reset to defaults"
	reset.pressed.connect(_reset)
	box.add_child(reset)
	_status = _label("", 14, TEXT_2)
	box.add_child(_status)


func _label(text: String, size: int, color: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	return l


func _player() -> Player:
	return get_tree().get_first_node_in_group("player") as Player


func is_open() -> bool:
	return _panel.visible


func _input(event: InputEvent) -> void:
	if event.is_action_pressed("toggle_tuning"):
		toggle()
		get_viewport().set_input_as_handled()
	elif _panel.visible and event.is_action_pressed("ui_cancel"):
		toggle()
		get_viewport().set_input_as_handled()


func toggle() -> void:
	var p := _player()
	if p == null:
		return
	_panel.visible = not _panel.visible
	p.combat_input = not _panel.visible
	if _panel.visible:
		_sync(p)
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		_status.text = "Saved on this device" if MoveTuning.has_saved() else "Using defaults"
	else:
		p.input_grace = 0.2


func _sync(p: Player) -> void:
	for slider: HSlider in _panel.find_children("*", "HSlider", true, false):
		slider.set_value_no_signal(p.tuning.get(slider.get_meta("prop")))
		slider.value_changed.emit(slider.value)
	_save_in = -1.0


func _reset() -> void:
	var p := _player()
	if p == null:
		return
	var fresh := MoveTuning.new()
	for t: Array in TUNABLES:
		p.tuning.set(t[0], fresh.get(t[0]))
	_sync(p)
	MoveTuning.clear_saved()
	_status.text = "Defaults restored"


func _process(delta: float) -> void:
	if _save_in < 0.0:
		return
	_save_in -= delta
	if _save_in < 0.0:
		var p := _player()
		if p:
			_status.text = "Saved on this device" if p.tuning.save_to_device() else "Couldn't save on this device"
