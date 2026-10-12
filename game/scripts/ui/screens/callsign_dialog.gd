class_name CallsignDialog
extends Control
## Edit callsign, as a popover under the callsign at the top right (from the
## menu designs): 420 px on the surface color, a 56 px field in the bold label
## face, help text and Cancel / Save. 3–16 letters, numbers or dashes, saved
## on this device.

var _on_saved: Callable
var _field: LineEdit
var _help: Label


func _init(on_saved: Callable) -> void:
	_on_saved = on_saved
	set_meta("overlay", true)
	theme = UIStyle.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	var catcher := UIStyle.fill(Color(0, 0, 0, 0.25))
	catcher.mouse_filter = Control.MOUSE_FILTER_STOP
	catcher.gui_input.connect(func(e: InputEvent) -> void:
		var m := e as InputEventMouseButton
		if m and m.pressed:
			Menus.pop())
	add_child(catcher)
	var p := UIStyle.panel(UIStyle.SURFACE, 28, Color(0, 0, 0, 0), 4)
	UIStyle.place(self, p, -1, 120, 64, -1, 420, 0)
	var v := UIStyle.vbox(14)
	p.add_child(v)
	v.add_child(UIStyle.tracked("Callsign", 14, 0.2, UIStyle.TEXT_2))
	_field = LineEdit.new()
	_field.text = GameSettings.callsign()
	_field.max_length = 16
	_field.custom_minimum_size.y = 56
	_field.add_theme_font_override("font", UIStyle.tracked_font(26, 0.12, true))
	_field.add_theme_font_size_override("font_size", 26)
	var sb := UIStyle.box(UIStyle.BG, 2)
	sb.border_color = UIStyle.BORDER
	sb.set_border_width_all(1)
	sb.content_margin_left = 16
	sb.content_margin_right = 16
	_field.add_theme_stylebox_override("normal", sb)
	var sbf := sb.duplicate() as StyleBoxFlat
	sbf.border_color = UIStyle.TEXT
	sbf.set_border_width_all(2)
	_field.add_theme_stylebox_override("focus", sbf)
	_field.text_submitted.connect(func(_t: String) -> void: _save())
	_field.text_changed.connect(func(_t: String) -> void:
		_help.text = "3 to 16 letters, numbers or dashes."
		_help.add_theme_color_override("font_color", UIStyle.TEXT_2))
	v.add_child(_field)
	_help = UIStyle.body("3 to 16 letters, numbers or dashes.", 16, UIStyle.TEXT_2)
	v.add_child(_help)
	var row := UIStyle.hbox(12)
	row.alignment = BoxContainer.ALIGNMENT_END
	v.add_child(row)
	var cancel := UIStyle.secondary_button("CANCEL", 150)
	cancel.pressed.connect(Menus.pop)
	row.add_child(cancel)
	var save := UIStyle.primary_button("SAVE", 150, false, "")
	save.pressed.connect(_save)
	row.add_child(save)


func focus_default() -> void:
	_field.grab_focus()
	_field.select_all()


func _save() -> void:
	var name := _field.text.strip_edges().to_upper()
	if RegEx.create_from_string("^[A-Z0-9-]{3,16}$").search(name) == null:
		_help.text = "Use 3 to 16 letters, numbers or dashes."
		_help.add_theme_color_override("font_color", UIStyle.DANGER)
		var sb := (_field.get_theme_stylebox("normal") as StyleBoxFlat).duplicate() as StyleBoxFlat
		sb.border_color = UIStyle.DANGER
		_field.add_theme_stylebox_override("normal", sb)
		Menus.sound("error")
		return
	GameSettings.set_callsign(name)
	Menus.sound("confirm")
	Menus.pop()
	_on_saved.call(name)
