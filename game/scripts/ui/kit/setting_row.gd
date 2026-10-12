class_name SettingRow
extends PanelContainer
## One settings row built from a GameSettings schema entry. Sizes from the
## menu designs: at least 80 px tall, padding 12/24/12/40, the 20 px label on
## the left and the control in a 560 px column on the right (360 px slider
## with value, "‹ value ›", segmented options, 56 × 30 switch, or two
## 150 × 44 key bindings). The row takes focus: ↑↓ between rows, ←→ adjust,
## Enter toggles or starts rebinding. Selected: raised background and a 4 px
## accent bar on the left.

signal selected(row: SettingRow)
signal notice(text: String)

var data: Dictionary
var _label: Label
var _value_label: Label
var _slider: SettingSlider
var _switch: ToggleSwitch
var _seg_buttons: Array[Button] = []
var _bind_buttons: Array[Button] = []
var _capturing := -1
var _pulse := 0.0
var _styles := {}


func _init(row: Dictionary) -> void:
	data = row
	focus_mode = Control.FOCUS_ALL
	custom_minimum_size = Vector2(0, 80)
	for state in ["normal", "hover", "sel"]:
		var sb := StyleBoxFlat.new()
		sb.bg_color = {"normal": Color(0, 0, 0, 0), "hover": Color(UIStyle.RAISED, 0.45), "sel": Color(UIStyle.RAISED, 0.85)}[state]
		sb.border_color = Color(UIStyle.BORDER, 0.6)
		sb.border_width_bottom = 1
		sb.content_margin_left = 40
		sb.content_margin_right = 24
		sb.content_margin_top = 12
		sb.content_margin_bottom = 12
		if state == "sel":
			sb.border_width_left = 4
			sb.border_color = UIStyle.ACCENT
			sb.border_width_bottom = 0
			sb.content_margin_left = 36
		_styles[state] = sb
	add_theme_stylebox_override("panel", _styles.normal)
	var h := UIStyle.hbox(24)
	add_child(h)
	_label = UIStyle.label(row.label, "ui_medium", 20, UIStyle.TEXT)
	_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	h.add_child(_label)
	var ctl := UIStyle.hbox(20)
	ctl.alignment = BoxContainer.ALIGNMENT_END
	ctl.custom_minimum_size.x = 560
	h.add_child(ctl)
	match row.type:
		"slider":
			_slider = SettingSlider.new(float(row.min), float(row.max), float(row.step))
			_slider.changed.connect(func(v: float) -> void:
				grab_focus()
				GameSettings.set_value(row.id, v)
				Menus.sound("tick")
				refresh())
			ctl.add_child(_slider)
			_value_label = UIStyle.label("", "ui_medium", 20, UIStyle.TEXT)
			_value_label.custom_minimum_size.x = 96
			_value_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			ctl.add_child(_value_label)
		"switch":
			_value_label = UIStyle.label("", "ui_medium", 20, UIStyle.TEXT)
			_value_label.custom_minimum_size.x = 40
			ctl.add_child(_value_label)
			_switch = ToggleSwitch.new()
			_switch.size_flags_vertical = Control.SIZE_SHRINK_CENTER
			_switch.toggled.connect(func(on: bool) -> void:
				grab_focus()
				_apply_value(on))
			ctl.add_child(_switch)
		"choice":
			var cycle := UIStyle.hbox(0)
			cycle.add_child(_arrow("‹", -1))
			_value_label = UIStyle.label("", "ui_medium", 20, UIStyle.TEXT)
			_value_label.custom_minimum_size.x = 160
			_value_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			_value_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
			cycle.add_child(_value_label)
			cycle.add_child(_arrow("›", 1))
			ctl.add_child(cycle)
		"seg":
			var seg := UIStyle.hbox(0)
			for opt: String in row.options:
				var b := Button.new()
				b.text = opt
				b.focus_mode = Control.FOCUS_NONE
				b.add_theme_font_override("font", UIStyle.font("ui_medium"))
				b.add_theme_font_size_override("font_size", 17)
				b.pressed.connect(func() -> void:
					grab_focus()
					_apply_value(opt))
				seg.add_child(b)
				_seg_buttons.append(b)
			ctl.add_child(seg)
		"bind":
			for i in 2:
				var b := UIStyle.outline_button("", UIStyle.TEXT, 150)
				b.focus_mode = Control.FOCUS_NONE
				b.pressed.connect(func() -> void:
					grab_focus()
					_start_capture(i))
				ctl.add_child(b)
				_bind_buttons.append(b)
	focus_entered.connect(func() -> void:
		_restyle()
		selected.emit(self))
	focus_exited.connect(func() -> void:
		_restyle()
		_cancel_capture())
	mouse_entered.connect(func() -> void:
		if _capturing < 0 and not has_focus():
			grab_focus())
	refresh()


func _restyle() -> void:
	add_theme_stylebox_override("panel", _styles.sel if has_focus() else _styles.normal)
	_label.add_theme_font_override("font", UIStyle.font("ui_bold" if has_focus() else "ui_medium"))


func _arrow(glyph: String, dir: int) -> Button:
	var b := Button.new()
	b.text = glyph
	b.focus_mode = Control.FOCUS_NONE
	b.custom_minimum_size = Vector2(44, 44)
	b.add_theme_font_override("font", UIStyle.font("ui_medium"))
	b.add_theme_font_size_override("font_size", 22)
	b.pressed.connect(func() -> void:
		grab_focus()
		_step(dir))
	return b


## Update the control from the saved value.
func refresh() -> void:
	var v: Variant = GameSettings.value(data.id) if data.type != "bind" else null
	match data.type:
		"slider":
			_slider.value = float(v)
			_value_label.text = format_value(data, float(v))
		"switch":
			_switch.on = bool(v)
			_value_label.text = "On" if v else "Off"
		"choice":
			_value_label.text = str(v)
		"seg":
			for b in _seg_buttons:
				var on := b.text == str(v)
				b.add_theme_color_override("font_color", UIStyle.TEXT if on else UIStyle.TEXT_2)
				b.add_theme_font_override("font", UIStyle.font("ui_bold" if on else "ui_medium"))
				var sb := StyleBoxFlat.new()
				sb.bg_color = UIStyle.RAISED if on else Color(0, 0, 0, 0)
				sb.border_color = UIStyle.ACCENT
				sb.border_width_bottom = 2 if on else 0
				sb.content_margin_left = 18
				sb.content_margin_right = 18
				sb.content_margin_top = 10
				sb.content_margin_bottom = 10
				var hover := sb.duplicate() as StyleBoxFlat
				if not on:
					hover.bg_color = Color(UIStyle.RAISED, 0.6)
				b.add_theme_stylebox_override("normal", sb)
				b.add_theme_stylebox_override("hover", hover)
				b.add_theme_stylebox_override("pressed", sb)
		"bind":
			var events := GameSettings.binding_events(data.action)
			for i in 2:
				var b := _bind_buttons[i]
				var capture := i == _capturing
				var empty := i >= events.size()
				b.text = "Press a key" if capture else ("—" if empty else GameSettings.event_label(events[i]))
				b.text = b.text.to_upper()
				var color := UIStyle.ACCENT if capture else (UIStyle.TEXT_3 if empty else UIStyle.TEXT)
				for s in ["font_color", "font_hover_color", "font_focus_color", "font_pressed_color"]:
					b.add_theme_color_override(s, color)
				var sb := (b.get_theme_stylebox("normal") as StyleBoxFlat).duplicate() as StyleBoxFlat
				sb.border_color = UIStyle.ACCENT if capture else UIStyle.BORDER
				b.add_theme_stylebox_override("normal", sb)


static func format_value(row: Dictionary, v: float) -> String:
	match row.unit:
		"x":
			return "%.2f×" % v
		"%":
			return "%d%%" % roundi(v)
		"°":
			return "%d°" % roundi(v)
	return str(v)


func _apply_value(v: Variant) -> void:
	GameSettings.set_value(data.id, v)
	Menus.sound("toggle")
	refresh()
	# The preset changes other rows.
	if data.id == "preset" or data.get("group", "") == "gfx":
		for r in get_parent().get_children():
			if r is SettingRow and r != self:
				(r as SettingRow).refresh()


func _step(dir: int) -> void:
	match data.type:
		"slider":
			GameSettings.set_value(data.id, GameSettings.f(data.id) + dir * float(data.step))
			Menus.sound("tick")
			refresh()
		"switch":
			_apply_value(not GameSettings.b(data.id))
		"choice", "seg":
			var opts: Array = data.options
			var i := opts.find(GameSettings.value(data.id))
			_apply_value(opts[(i + dir + opts.size()) % opts.size()])


func _gui_input(event: InputEvent) -> void:
	if _capturing >= 0:
		return
	if event.is_action_pressed("ui_left"):
		_step(-1)
		accept_event()
	elif event.is_action_pressed("ui_right"):
		_step(1)
		accept_event()
	elif event.is_action_pressed("ui_accept"):
		if data.type == "switch":
			_step(1)
		elif data.type == "bind":
			_start_capture(0)
		accept_event()


func _notification(what: int) -> void:
	if what == NOTIFICATION_MOUSE_ENTER and not has_focus():
		add_theme_stylebox_override("panel", _styles.hover)
	elif what == NOTIFICATION_MOUSE_EXIT:
		_restyle()


# ---------------------------------------------------------------- rebinding

func is_capturing() -> bool:
	return _capturing >= 0


func _start_capture(slot: int) -> void:
	_capturing = slot
	refresh()
	Menus.sound("confirm")
	# Wait a frame so the click that started this isn't captured.
	await get_tree().process_frame
	set_process_input(true)


func _cancel_capture() -> void:
	if _capturing >= 0:
		_capturing = -1
		set_process_input(false)
		refresh()


func _ready() -> void:
	set_process_input(false)


func _process(delta: float) -> void:
	if _capturing < 0:
		return
	_pulse += delta
	var b := _bind_buttons[_capturing]
	var sb := (b.get_theme_stylebox("normal") as StyleBoxFlat)
	sb.bg_color = Color(UIStyle.ACCENT, 0.12 * (0.5 + 0.5 * sin(_pulse * 5.2)))


func _input(event: InputEvent) -> void:
	if _capturing < 0:
		return
	var key := event as InputEventKey
	var mouse := event as InputEventMouseButton
	if key and key.pressed and not key.echo:
		get_viewport().set_input_as_handled()
		if key.physical_keycode == KEY_ESCAPE:
			_cancel_capture()
			return
		if key.physical_keycode == KEY_DELETE or key.physical_keycode == KEY_BACKSPACE:
			_finish(null if _capturing == 1 else _capture_event(key))
			return
		_finish(_capture_event(key))
	elif mouse and mouse.pressed:
		get_viewport().set_input_as_handled()
		var m := InputEventMouseButton.new()
		m.button_index = mouse.button_index
		_finish(m)


func _capture_event(key: InputEventKey) -> InputEventKey:
	var k := InputEventKey.new()
	k.physical_keycode = key.physical_keycode
	return k


func _finish(event: InputEvent) -> void:
	var slot := _capturing
	_capturing = -1
	set_process_input(false)
	var took := GameSettings.rebind(data.action, slot, event)
	Menus.sound("confirm")
	if took != "":
		notice.emit("%s was unbound from %s." % [GameSettings.event_label(event), took])
	for r in get_parent().get_children():
		if r is SettingRow:
			(r as SettingRow).refresh()
