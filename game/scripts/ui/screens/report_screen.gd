class_name ReportScreen
extends Control
## Report a problem. Layout from the menu designs: "← BACK" and "CLOSE ESC"
## across the top at 72 px margins; on the left (1180 px) the eyebrow, a
## 128 px title, intro, a 4-column grid of issue types and the description
## box; on the right, from x 1360 behind a rule, what's attached
## (screenshot, position, system) and an 88 px Send report button.
## There's no server yet: reports are saved on this device under
## user://reports/ (browser storage on the web) and printed to the console.

const ISSUES := ["Lag / stutter", "Hit registration", "Bug / glitch", "Visual", "Audio", "Stuck", "Bot behavior", "Other"]
const MAX_CHARS := 1000

var _context := ""
var _issue := -1
var _cats: Array[Button] = []
var _text: TextEdit
var _count: Label
var _send: Button
var _position := ""
var _done: Control


func _init(context: String) -> void:
	_context = context
	theme = UIStyle.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	var player := get_tree().get_first_node_in_group("player") as Node3D
	if player:
		var p := player.global_position
		_position = "%.0f, %.0f, %.0f" % [p.x, p.y, p.z]
	add_child(UIStyle.fill(UIStyle.BG))

	var back := _top_button("←   Back")
	UIStyle.place(self, back, 72, 48)
	var close := _top_button("Close   Esc")
	UIStyle.place(self, close, -1, 48, 72)

	var left := UIStyle.vbox(0)
	UIStyle.place(self, left, 72, 150, -1, -1, 1180, 0)
	left.add_child(UIStyle.eyebrow("Report"))
	left.add_child(UIStyle.spacer(12))
	left.add_child(UIStyle.title("Report a problem", 128, 0.9))
	left.add_child(UIStyle.spacer(24))
	left.add_child(UIStyle.body("Help us keep Orbit Royale fair, stable and fun. Tell us what happened; the details on the right are attached for you.", 22, UIStyle.TEXT_2))
	left.add_child(UIStyle.spacer(44))
	left.add_child(UIStyle.eyebrow("What type of issue?"))
	left.add_child(UIStyle.spacer(18))
	var grid := GridContainer.new()
	grid.columns = 4
	grid.add_theme_constant_override("h_separation", 0)
	grid.add_theme_constant_override("v_separation", 0)
	left.add_child(grid)
	for i in ISSUES.size():
		var b := Button.new()
		b.text = ISSUES[i].to_upper()
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.custom_minimum_size = Vector2(295, 84)
		b.add_theme_font_size_override("font_size", 20)
		b.pressed.connect(func() -> void: _pick(i))
		b.mouse_entered.connect(b.grab_focus)
		grid.add_child(b)
		_cats.append(b)
	left.add_child(UIStyle.spacer(40))
	var lab := UIStyle.hbox(18)
	lab.add_child(UIStyle.eyebrow("What happened?", UIStyle.TEXT))
	lab.add_child(UIStyle.eyebrow("Optional"))
	left.add_child(lab)
	left.add_child(UIStyle.spacer(16))
	_text = TextEdit.new()
	_text.placeholder_text = "Describe what you saw and what you expected."
	_text.custom_minimum_size = Vector2(0, 220)
	_text.wrap_mode = TextEdit.LINE_WRAPPING_BOUNDARY
	_text.text_changed.connect(_on_text)
	left.add_child(_text)
	left.add_child(UIStyle.spacer(8))
	_count = UIStyle.tracked("0 / %d" % MAX_CHARS, 15, 0.14, UIStyle.TEXT_2)
	_count.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	left.add_child(_count)

	var right := UIStyle.hbox(56)
	UIStyle.place(self, right, 1360, 150, 72, 72)
	right.add_child(UIStyle.rule(UIStyle.BORDER, true))
	var rc := UIStyle.vbox(0)
	rc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right.add_child(rc)
	rc.add_child(UIStyle.eyebrow("Automatically attached"))
	rc.add_child(UIStyle.spacer(20))
	rc.add_child(UIStyle.rule(UIStyle.BORDER))
	var shot := TextureRect.new()
	shot.custom_minimum_size = Vector2(0, 230)
	shot.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	shot.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	if GameMenu.screenshot:
		shot.texture = ImageTexture.create_from_image(GameMenu.screenshot)
	rc.add_child(UIStyle.spacer(24))
	rc.add_child(shot)
	rc.add_child(_attached("Screenshot", "Captured when you opened the menu."))
	rc.add_child(_attached("Position", "%s at %s" % [_context, _position] if _position != "" else _context))
	rc.add_child(_attached("System", _system_line()))
	rc.add_child(UIStyle.expander())
	_send = UIStyle.primary_button("Send report", 0, true, "")
	_send.custom_minimum_size.y = 88
	_send.add_theme_font_size_override("font_size", 34)
	var side := UIStyle.tracked("Ctrl+Enter", 14, 0.12, UIStyle.ON_ACCENT, true)
	UIStyle.place(_send, side, -1, 0, 24, 0)
	side.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_send.pressed.connect(_submit)
	rc.add_child(_send)
	rc.add_child(UIStyle.spacer(18))
	var cancel := UIStyle.link("Cancel")
	cancel.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	cancel.add_theme_color_override("font_color", UIStyle.TEXT_2)
	cancel.pressed.connect(Menus.pop)
	rc.add_child(cancel)
	back.pressed.connect(Menus.pop)
	close.pressed.connect(Menus.pop)
	_refresh()


func _top_button(text: String) -> Button:
	var b := Button.new()
	b.text = text.to_upper()
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_font_override("font", UIStyle.tracked_font(18, 0.22))
	b.add_theme_font_size_override("font_size", 18)
	return b


func _attached(name: String, text: String) -> Control:
	var v := UIStyle.vbox(6)
	v.add_child(UIStyle.spacer(12))
	v.add_child(UIStyle.tracked(name, 15, 0.2, UIStyle.TEXT))
	v.add_child(UIStyle.body(text, 17, UIStyle.TEXT_2))
	v.add_child(UIStyle.spacer(12))
	v.add_child(UIStyle.rule(UIStyle.BORDER))
	return v


func _system_line() -> String:
	var gpu := RenderingServer.get_video_adapter_name()
	return "%s · %s · %d fps" % [OS.get_name(), gpu if gpu != "" else "unknown GPU", Engine.get_frames_per_second()]


func focus_default() -> void:
	_cats[0].grab_focus()


func _pick(i: int) -> void:
	_issue = i
	Menus.sound("toggle")
	_refresh()


func _on_text() -> void:
	if _text.text.length() > MAX_CHARS:
		_text.text = _text.text.left(MAX_CHARS)
	_count.text = "%d / %d" % [_text.text.length(), MAX_CHARS]


## Issue cells: 1 px dividers between columns and under the first row; the
## chosen one gets a raised background and a 4 px accent bar along its foot.
func _refresh() -> void:
	for i in _cats.size():
		var b := _cats[i]
		var on := i == _issue
		var first_col := i % 4 == 0
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(UIStyle.RAISED, 0.7) if on else Color(0, 0, 0, 0)
		sb.border_color = UIStyle.BORDER
		sb.border_width_left = 0 if first_col else 1
		sb.border_width_bottom = 1 if i < 4 else 0
		sb.content_margin_left = 8 if first_col else 24
		sb.content_margin_right = 20
		var hover := sb.duplicate() as StyleBoxFlat
		if not on:
			hover.bg_color = Color(UIStyle.RAISED, 0.5)
		for s in ["normal", "pressed"]:
			b.add_theme_stylebox_override(s, sb)
		b.add_theme_stylebox_override("hover", hover)
		b.add_theme_stylebox_override("focus", hover)
		b.add_theme_font_override("font", UIStyle.tracked_font(20, 0.14, on))
		b.add_theme_color_override("font_color", UIStyle.TEXT)
		var bar: ColorRect = b.get_meta("bar") if b.has_meta("bar") else null
		if bar == null:
			bar = ColorRect.new()
			bar.color = UIStyle.ACCENT
			UIStyle.place(b, bar, 8 if first_col else 24, -1, 24, 0, 0, 4)
			b.set_meta("bar", bar)
		bar.visible = on
	_send.modulate.a = 1.0 if _issue >= 0 else 0.45


func _submit() -> void:
	if _issue < 0:
		Menus.sound("error")
		_cats[0].grab_focus()
		return
	var stamp := Time.get_datetime_string_from_system().replace(":", "-")
	DirAccess.make_dir_recursive_absolute("user://reports")
	var report := {
		"time": Time.get_datetime_string_from_system(), "issue": ISSUES[_issue], "text": _text.text,
		"context": _context, "position": _position, "system": _system_line(), "callsign": GameSettings.callsign(),
	}
	var f := FileAccess.open("user://reports/%s.json" % stamp, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(report, "  "))
		f.close()
	if GameMenu.screenshot:
		GameMenu.screenshot.save_jpg("user://reports/%s.jpg" % stamp, 0.8)
	print("REPORT ", JSON.stringify(report))
	Menus.sound("confirm")
	_show_done()


## Sent state: a check, a 120 px title and what happens next.
func _show_done() -> void:
	_done = UIStyle.fill(UIStyle.BG)
	_done.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(_done)
	var v := UIStyle.vbox(24)
	UIStyle.place(_done, v, 72, 300, -1, -1, 1000, 0)
	var chk := Control.new()
	chk.custom_minimum_size = Vector2(80, 80)
	chk.draw.connect(func() -> void: chk.draw_circle(Vector2(40, 40), 40, Color(UIStyle.SUCCESS, 0.14)))
	var g := Glyph.new("check", UIStyle.SUCCESS, 36)
	UIStyle.place(chk, g, 22, 22, -1, -1, 36, 36)
	v.add_child(chk)
	v.add_child(UIStyle.title("Report saved.", 120, 0.9))
	v.add_child(UIStyle.body("Thanks. It's stored on this device with the screenshot until reports can be sent online.", 22, UIStyle.TEXT_2))
	v.add_child(UIStyle.hint_bar([["Esc", "Back to the menu"]]))


func _input(event: InputEvent) -> void:
	if Menus.top() != self or _done != null:
		return
	var key := event as InputEventKey
	if key and key.pressed and key.ctrl_pressed and key.keycode == KEY_ENTER:
		get_viewport().set_input_as_handled()
		_submit()
