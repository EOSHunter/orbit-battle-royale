class_name SettingsScreen
extends Control
## Settings. Layout from the menu designs, inside 80/40 px margins: the
## wordmark (160 px) and "BACK · ESC" on top, a 110 px "Settings" title,
## category tabs (Q/E) on a rule, section sub-tabs (Tab), then a 1040 px rows
## column, a divider, and the help column (eyebrow, 40 px heading, 18 px text,
## live visual). Footer: Restore defaults, select/adjust hints, saved status.
## Key art fades in at the right at 32%.

var _cat := 0
var _sec := 0
var _tabs: Array[Button] = []
var _tab_ink: ColorRect
var _tabs_row: HBoxContainer
var _sub_box: HBoxContainer
var _rows_box: VBoxContainer
var _scroll: ScrollContainer
var _help_eyebrow: Label
var _help_title: Label
var _help_body: Label
var _viz: SettingViz
var _msg: Label
var _msg_time := 0.0
var _saved: Label
var _saved_icon: Glyph
var _selected: SettingRow


func _init(start_category := "mk") -> void:
	theme = UIStyle.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for i in GameSettings.CATEGORIES.size():
		if GameSettings.CATEGORIES[i].id == start_category:
			_cat = i


func _ready() -> void:
	GameSettings.ensure_loaded()
	add_child(UIStyle.fill(UIStyle.BG))
	# Key art on the right 900 px at 32%, fading in from its left edge.
	var art_box := Control.new()
	art_box.clip_contents = true
	UIStyle.place(self, art_box, -1, 0, 0, 0, 900)
	var art := UIStyle.key_art()
	art.modulate.a = 0.32
	art_box.add_child(art)
	art_box.add_child(UIStyle.gradient([[0.0, UIStyle.BG], [0.7, Color(UIStyle.BG, 0.0)]]))

	var col := UIStyle.vbox(0)
	UIStyle.place(self, col, 80, 40, 80, 40)

	var top := UIStyle.hbox(0)
	col.add_child(top)
	var logo := UIStyle.logo(160)
	logo.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	top.add_child(logo)
	top.add_child(UIStyle.expander(false))
	var back_wrap := UIStyle.hbox(28)
	back_wrap.add_child(UIStyle.rule(UIStyle.BORDER, true, 40))
	var back := Button.new()
	back.text = "BACK  ·  ESC"
	back.focus_mode = Control.FOCUS_NONE
	back.add_theme_font_override("font", UIStyle.tracked_font(17, 0.2))
	back.add_theme_font_size_override("font_size", 17)
	back.pressed.connect(Menus.pop)
	back_wrap.add_child(back)
	back_wrap.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	top.add_child(back_wrap)

	var t := UIStyle.label("Settings", "display", 110, UIStyle.TEXT)
	t.add_theme_constant_override("line_spacing", -20)
	col.add_child(UIStyle.spacer(6))
	col.add_child(t)
	col.add_child(UIStyle.spacer(12))

	# Category tabs on a rule, with Q / E at the right.
	var cats := Control.new()
	cats.custom_minimum_size.y = 58
	col.add_child(cats)
	UIStyle.place(cats, UIStyle.rule(UIStyle.BORDER), 0, 57, 0, -1, 0, 1)
	_tabs_row = UIStyle.hbox(84)
	UIStyle.place(cats, _tabs_row, 0, 0)
	for i in GameSettings.CATEGORIES.size():
		var b := Button.new()
		b.text = String(GameSettings.CATEGORIES[i].name).to_upper()
		b.focus_mode = Control.FOCUS_NONE
		b.add_theme_font_size_override("font_size", 18)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0, 0, 0, 0)
		sb.content_margin_top = 18
		sb.content_margin_bottom = 16
		for s in ["normal", "hover", "pressed", "focus"]:
			b.add_theme_stylebox_override(s, sb)
		b.pressed.connect(func() -> void: _show_category(i))
		_tabs_row.add_child(b)
		_tabs.append(b)
	_tab_ink = ColorRect.new()
	_tab_ink.color = UIStyle.ACCENT
	cats.add_child(_tab_ink)
	var qe := UIStyle.hbox(8)
	qe.add_child(UIStyle.keycap("Q"))
	qe.add_child(UIStyle.keycap("E"))
	UIStyle.place(cats, qe, -1, 14, 0)

	col.add_child(UIStyle.spacer(24))
	_sub_box = UIStyle.hbox(0)
	_sub_box.custom_minimum_size.y = 44
	col.add_child(_sub_box)
	col.add_child(UIStyle.spacer(18))

	var body := UIStyle.hbox(56)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	col.add_child(body)
	_scroll = ScrollContainer.new()
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_scroll.custom_minimum_size.x = 1040
	_scroll.follow_focus = true
	body.add_child(_scroll)
	var table := UIStyle.vbox(0)
	table.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(table)
	table.add_child(UIStyle.rule(Color(UIStyle.BORDER, 0.6)))
	_rows_box = UIStyle.vbox(0)
	_rows_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	table.add_child(_rows_box)
	_msg = UIStyle.body("", 16, UIStyle.WARNING)
	table.add_child(_msg)
	body.add_child(UIStyle.rule(UIStyle.BORDER, true))
	var help := UIStyle.vbox(14)
	help.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_child(help)
	help.add_child(UIStyle.spacer(14))
	_help_eyebrow = UIStyle.eyebrow("")
	help.add_child(_help_eyebrow)
	_help_title = UIStyle.label("", "heading", 40, UIStyle.TEXT)
	help.add_child(_help_title)
	_help_body = UIStyle.body("", 18, Color("d9dde6"))
	_help_body.custom_minimum_size.x = 460
	_help_body.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	help.add_child(_help_body)
	help.add_child(UIStyle.spacer(6))
	_viz = SettingViz.new()
	_viz.custom_minimum_size = Vector2(520, 300)
	help.add_child(_viz)

	col.add_child(UIStyle.spacer(16))
	col.add_child(UIStyle.rule(UIStyle.BORDER))
	col.add_child(UIStyle.spacer(24))
	var foot := UIStyle.hbox(0)
	col.add_child(foot)
	var restore := Button.new()
	restore.focus_mode = Control.FOCUS_NONE
	restore.add_child(UIStyle.key_hint("R", "Restore defaults", false))
	restore.custom_minimum_size = Vector2(260, 30)
	restore.pressed.connect(_confirm_restore)
	foot.add_child(restore)
	foot.add_child(UIStyle.expander(false))
	foot.add_child(UIStyle.hint_bar([["↑↓", "Select", false], ["←→", "Adjust", false]], 28))
	foot.add_child(UIStyle.expander(false))
	_saved_icon = Glyph.new("check", UIStyle.ACCENT, 18)
	foot.add_child(_saved_icon)
	foot.add_child(UIStyle.spacer(0, 12))
	_saved = UIStyle.tracked("", 16, 0.16, UIStyle.TEXT_2)
	foot.add_child(_saved)
	_show_category(_cat)


func focus_default() -> void:
	_focus_first_row()


func _show_category(i: int) -> void:
	_cat = i
	_sec = 0
	for t in _tabs.size():
		var on := t == i
		_tabs[t].add_theme_color_override("font_color", UIStyle.TEXT if on else UIStyle.TEXT_2)
		_tabs[t].add_theme_font_override("font", UIStyle.tracked_font(18, 0.2, on))
	_place_ink.call_deferred()
	_build_sections()
	_build_rows()
	Menus.sound("navigate")


func _place_ink() -> void:
	var t := _tabs[_cat]
	_tab_ink.position = Vector2(t.position.x, 55)
	_tab_ink.size = Vector2(t.size.x, 3)


func _build_sections() -> void:
	for c in _sub_box.get_children():
		c.queue_free()
	var sections: Array = GameSettings.CATEGORIES[_cat].sections
	for i in sections.size():
		if i > 0:
			_sub_box.add_child(UIStyle.spacer(0, 18))
			_sub_box.add_child(UIStyle.rule(UIStyle.BORDER, true, 20))
			_sub_box.add_child(UIStyle.spacer(0, 18))
		var on := i == _sec
		var v := UIStyle.vbox(0)
		var b := Button.new()
		b.text = String(sections[i].name).to_upper()
		b.focus_mode = Control.FOCUS_NONE
		b.add_theme_font_override("font", UIStyle.tracked_font(16, 0.2, on))
		b.add_theme_font_size_override("font_size", 16)
		b.add_theme_color_override("font_color", UIStyle.TEXT if on else UIStyle.TEXT_2)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0, 0, 0, 0)
		sb.content_margin_top = 10
		sb.content_margin_bottom = 8
		for s in ["normal", "hover", "pressed", "focus"]:
			b.add_theme_stylebox_override(s, sb)
		b.pressed.connect(func() -> void:
			_sec = i
			_build_sections()
			_build_rows())
		v.add_child(b)
		var ink := ColorRect.new()
		ink.color = UIStyle.ACCENT if on else Color(0, 0, 0, 0)
		ink.custom_minimum_size = Vector2(40, 3)
		ink.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
		v.add_child(ink)
		v.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		_sub_box.add_child(v)
	if sections.size() > 1:
		_sub_box.add_child(UIStyle.spacer(0, 28))
		_sub_box.add_child(UIStyle.keycap("Tab"))


func _build_rows() -> void:
	for c in _rows_box.get_children():
		_rows_box.remove_child(c)
		c.queue_free()
	_selected = null
	var section: Dictionary = GameSettings.CATEGORIES[_cat].sections[_sec]
	if section.id == "bindings":
		var intro := UIStyle.body("Select a binding, then press a key or a mouse button (side buttons and the wheel work too). Escape cancels; Delete clears the alternate. A key already in use moves here from its old action.", 16, UIStyle.TEXT_2)
		var pad := MarginContainer.new()
		pad.add_theme_constant_override("margin_left", 40)
		pad.add_theme_constant_override("margin_top", 14)
		pad.add_theme_constant_override("margin_bottom", 14)
		pad.add_theme_constant_override("margin_right", 24)
		pad.add_child(intro)
		_rows_box.add_child(pad)
	for r: Dictionary in section.rows:
		var row := SettingRow.new(r)
		row.selected.connect(_on_row_selected)
		row.notice.connect(func(text: String) -> void:
			_msg.text = text
			_msg_time = 4.0)
		_rows_box.add_child(row)
	_scroll.scroll_vertical = 0
	_focus_first_row()


func _focus_first_row() -> void:
	for c in _rows_box.get_children():
		if c is SettingRow:
			_focus_later.call_deferred(c)
			return


func _focus_later(c: Control) -> void:
	if is_instance_valid(c) and c.is_inside_tree() and not c.is_queued_for_deletion():
		c.grab_focus()


func _on_row_selected(row: SettingRow) -> void:
	_selected = row
	var r := row.data
	_help_eyebrow.text = String(r.get("eyebrow", GameSettings.CATEGORIES[_cat].name)).to_upper()
	_help_title.text = r.label
	_help_body.text = r.help
	_viz.show_row(r)


func _process(delta: float) -> void:
	_msg_time = maxf(0.0, _msg_time - delta)
	_msg.modulate.a = clampf(_msg_time, 0.0, 1.0)
	_saved_icon.color = UIStyle.ACCENT if GameSettings.save_ok else UIStyle.DANGER
	_saved.text = "Saved on this device" if GameSettings.save_ok else "Couldn't save: settings last this session"


func _capturing() -> bool:
	return _selected != null and _selected.is_capturing()


# _input, not _unhandled_input: Tab would otherwise move GUI focus first.
func _input(event: InputEvent) -> void:
	if _capturing() or Menus.top() != self:
		return
	var key := event as InputEventKey
	if key and key.pressed and not key.echo:
		match key.physical_keycode:
			KEY_Q:
				_show_category((_cat + GameSettings.CATEGORIES.size() - 1) % GameSettings.CATEGORIES.size())
			KEY_E:
				_show_category((_cat + 1) % GameSettings.CATEGORIES.size())
			KEY_TAB:
				var n: int = GameSettings.CATEGORIES[_cat].sections.size()
				_sec = (_sec + (n - 1 if key.shift_pressed else 1)) % n
				_build_sections()
				_build_rows()
				Menus.sound("navigate")
			KEY_R:
				_confirm_restore()
			_:
				return
		get_viewport().set_input_as_handled()
	var pad := event as InputEventJoypadButton
	if pad and pad.pressed:
		if pad.button_index == JOY_BUTTON_LEFT_SHOULDER:
			_show_category((_cat + GameSettings.CATEGORIES.size() - 1) % GameSettings.CATEGORIES.size())
		elif pad.button_index == JOY_BUTTON_RIGHT_SHOULDER:
			_show_category((_cat + 1) % GameSettings.CATEGORIES.size())


## Esc while rebinding cancels the rebind instead of closing the screen.
func on_back() -> bool:
	return _capturing()


func _confirm_restore() -> void:
	var cat: Dictionary = GameSettings.CATEGORIES[_cat]
	Menus.push(ConfirmDialog.new("Restore %s?" % cat.name.to_lower(),
		"Resets every %s setting to its default. Other categories keep their values." % cat.name.to_lower(),
		"Restore defaults", func() -> void:
			GameSettings.reset_category(cat.id)
			_build_rows(), false))


func on_reveal() -> void:
	for c in _rows_box.get_children():
		if c is SettingRow:
			(c as SettingRow).refresh()
