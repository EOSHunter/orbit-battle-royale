extends Control
## Main menu / lobby. Layout from the menu designs: the wordmark top-left,
## PLAY · TRAINING · SETTINGS tabs on a rule, the callsign top-right, a 136 px
## title over the left gradient with mode, the big Play button, status line
## and links, and key hints at the bottom left. Play counts down
## ("STARTING 0:03", Esc cancels) and loads Ringfall.

const MATCH_SCENE := "res://scenes/ringfall.tscn"
const RANGE_SCENE := "res://scenes/firing_range.tscn"
const COUNTDOWN := 3.0

var _tab := 0
var _tabs: Array[Button] = []
var _ink: ColorRect
var _main: Control
var _foot: Control
var _play: Button
var _callsign: Label
var _starting := -1.0
var _first: Control


func _ready() -> void:
	theme = UIStyle.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	MouseLock.release()
	get_tree().paused = false
	add_child(UIStyle.fill(UIStyle.BG))
	var art := UIStyle.key_art(true)
	add_child(art)
	add_child(UIStyle.gradient([[0.0, Color(UIStyle.BG, 0.98)], [0.27, Color(UIStyle.BG, 0.96)], [0.36, Color(UIStyle.BG, 0.55)], [0.48, Color(UIStyle.BG, 0.0)]]))
	add_child(UIStyle.gradient([[0.0, Color(UIStyle.BG, 0.55)], [0.16, Color(UIStyle.BG, 0.0)], [0.8, Color(UIStyle.BG, 0.0)], [1.0, Color(UIStyle.BG, 0.6)]], true))
	_drift(art)

	UIStyle.place(self, UIStyle.logo(400), 84, 44)

	# Tabs on a rule, from x 640 to 380 px from the right edge.
	var nav := Control.new()
	UIStyle.place(self, nav, 640, 46, 380, -1, 0, 54)
	var nav_rule := UIStyle.rule(UIStyle.LINE)
	UIStyle.place(nav, nav_rule, 0, 53, 0, -1, 0, 1)
	var tabs := UIStyle.hbox(64)
	UIStyle.place(nav, tabs, 0, 0)
	for i in 3:
		var t := Button.new()
		t.text = ["Play", "Training", "Settings"][i].to_upper()
		t.focus_mode = Control.FOCUS_NONE
		t.add_theme_font_override("font", UIStyle.tracked_font(20, 0.2))
		t.add_theme_font_size_override("font_size", 20)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0, 0, 0, 0)
		sb.content_margin_top = 14
		sb.content_margin_bottom = 16
		for s in ["normal", "hover", "pressed", "focus"]:
			t.add_theme_stylebox_override(s, sb)
		t.pressed.connect(func() -> void: _on_tab(i))
		tabs.add_child(t)
		_tabs.append(t)
	_ink = ColorRect.new()
	_ink.color = UIStyle.ACCENT
	nav.add_child(_ink)

	# Callsign block, top right.
	var id := UIStyle.hbox(28)
	UIStyle.place(self, id, -1, 44, 64)
	var cs := UIStyle.vbox(2)
	var cs_small := UIStyle.tracked("Callsign", 14, 0.2, UIStyle.TEXT_2)
	cs_small.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	cs.add_child(cs_small)
	_callsign = UIStyle.label(GameSettings.callsign(), "display", 44, UIStyle.TEXT)
	_callsign.add_theme_font_override("font", UIStyle.font("display"))
	_callsign.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	cs.add_child(_callsign)
	id.add_child(cs)
	id.add_child(UIStyle.rule(UIStyle.LINE_STRONG, true, 52))
	var edit := UIStyle.link("Edit callsign", "pencil", 15, 0.16, true)
	edit.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	edit.pressed.connect(_edit_callsign)
	id.add_child(edit)

	_main = Control.new()
	UIStyle.place(self, _main, 84, 228, -1, -1, 560, 700)
	_foot = Control.new()
	UIStyle.place(self, _foot, 84, -1, -1, 52, 900, 30)
	_show_tab(0)
	Menus.play_music()


func _drift(art: TextureRect) -> void:
	# A slow push-in on the key art; skipped with reduced motion.
	if GameSettings.b("reduce_motion"):
		return
	art.pivot_offset = Vector2(1920, 1080) * 0.5
	var t := create_tween().set_loops()
	t.tween_property(art, "scale", Vector2(1.05, 1.05), 24.0).set_trans(Tween.TRANS_SINE)
	t.tween_property(art, "scale", Vector2(1.0, 1.0), 24.0).set_trans(Tween.TRANS_SINE)


func _place_ink() -> void:
	var t := _tabs[_tab]
	_ink.position = Vector2(t.position.x, 51)
	_ink.size = Vector2(t.size.x, 3)


func _show_tab(i: int) -> void:
	_tab = i
	for t in _tabs.size():
		var on := t == i
		_tabs[t].add_theme_color_override("font_color", UIStyle.TEXT if on else UIStyle.TEXT_2)
		_tabs[t].add_theme_font_override("font", UIStyle.tracked_font(20, 0.2, on))
	_place_ink.call_deferred()
	for c in _main.get_children():
		c.queue_free()
	var col := UIStyle.vbox(0)
	col.custom_minimum_size.x = 560
	_main.add_child(col)
	if i == 0:
		_build_play(col)
	else:
		_build_training(col)
	for c in _foot.get_children():
		c.queue_free()
	_foot.add_child(UIStyle.hint_bar([["Enter", "Play" if i == 0 else "Firing range"], ["Esc", "Settings"]]))
	focus_default()


func _build_play(col: VBoxContainer) -> void:
	col.add_child(UIStyle.dash_eyebrow("Battle royale"))
	col.add_child(UIStyle.spacer(20))
	col.add_child(UIStyle.title("Rule the\nring.", 136, 0.86))
	col.add_child(UIStyle.spacer(26))
	col.add_child(UIStyle.tracked("Ringfall  ·  solo vs bots", 18, 0.22, UIStyle.TEXT_2))
	col.add_child(UIStyle.spacer(36))
	# Mode selector: Solo now, Squads later.
	var modes := UIStyle.hbox(56)
	for m: Array in [["Solo", true], ["Squads", false]]:
		var mb := UIStyle.vbox(0)
		mb.custom_minimum_size.x = 140 if not m[1] else 100
		var l := UIStyle.tracked(m[0] if m[1] else "Squads · later", 22, 0.18, UIStyle.ACCENT if m[1] else UIStyle.TEXT_3, true)
		mb.add_child(l)
		mb.add_child(UIStyle.spacer(12 if m[1] else 14))
		var u := ColorRect.new()
		u.color = UIStyle.ACCENT if m[1] else UIStyle.LINE
		u.custom_minimum_size.y = 3 if m[1] else 1
		mb.add_child(u)
		modes.add_child(mb)
	col.add_child(modes)
	col.add_child(UIStyle.spacer(28))
	_play = UIStyle.primary_button("Play", 512)
	_play.pressed.connect(_on_play)
	col.add_child(_play)
	_first = _play
	col.add_child(UIStyle.spacer(22))
	var live := UIStyle.hbox(12)
	live.add_child(Glyph.new("dot", UIStyle.SUCCESS, 10))
	live.add_child(UIStyle.tracked("Offline bot match  ·  Ringfall", 15, 0.2, UIStyle.TEXT_2))
	col.add_child(live)
	col.add_child(UIStyle.spacer(36))
	col.add_child(UIStyle.rule(UIStyle.LINE))
	var links := UIStyle.hbox(36)
	links.custom_minimum_size.y = 76
	var range_link := UIStyle.link("Firing range", "target")
	range_link.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	range_link.pressed.connect(_go_range)
	links.add_child(range_link)
	links.add_child(UIStyle.rule(UIStyle.LINE, true, 30))
	var learn := UIStyle.link("Learn controls", "book")
	learn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	learn.pressed.connect(_learn)
	links.add_child(learn)
	col.add_child(links)
	col.add_child(UIStyle.rule(UIStyle.LINE))
	_play.focus_neighbor_bottom = _play.get_path_to(range_link)
	range_link.focus_neighbor_top = range_link.get_path_to(_play)
	learn.focus_neighbor_top = learn.get_path_to(_play)


func _build_training(col: VBoxContainer) -> void:
	col.add_child(UIStyle.dash_eyebrow("Training"))
	col.add_child(UIStyle.spacer(20))
	col.add_child(UIStyle.title("Sharpen\nup.", 136, 0.86))
	col.add_child(UIStyle.spacer(40))
	col.add_child(UIStyle.rule(UIStyle.LINE))
	var a := _training_entry("Firing range", "Every weapon, infinite ammo, targets at 10–100 m. Try your settings.", _go_range)
	col.add_child(a)
	col.add_child(UIStyle.rule(UIStyle.LINE))
	col.add_child(_training_entry("Learn controls", "Eight short lessons. Keys follow your bindings.", _learn))
	col.add_child(UIStyle.rule(UIStyle.LINE))
	_first = a


## A training row: 40 px display title, 18 px description, an arrow at right.
func _training_entry(title: String, text: String, action: Callable) -> Button:
	var b := Button.new()
	b.custom_minimum_size = Vector2(560, 124)
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(0, 0, 0, 0)
	var focus := normal.duplicate() as StyleBoxFlat
	focus.border_color = UIStyle.ACCENT
	focus.border_width_left = 4
	focus.expand_margin_left = 24
	for s in ["normal", "pressed"]:
		b.add_theme_stylebox_override(s, normal)
	b.add_theme_stylebox_override("hover", focus)
	b.add_theme_stylebox_override("focus", focus)
	var t := UIStyle.title(title, 40, 1.0)
	UIStyle.place(b, t, 0, 26)
	var d := UIStyle.body(text, 18, UIStyle.TEXT_2)
	UIStyle.place(b, d, 0, 74, 60)
	var arr := UIStyle.label("→", "ui_medium", 30, UIStyle.TEXT_2)
	UIStyle.place(b, arr, -1, 40, 0)
	var on := func(v: bool) -> void:
		t.add_theme_color_override("font_color", UIStyle.ACCENT if v else UIStyle.TEXT)
		arr.add_theme_color_override("font_color", UIStyle.ACCENT if v else UIStyle.TEXT_2)
	b.focus_entered.connect(on.bind(true))
	b.focus_exited.connect(on.bind(false))
	b.mouse_entered.connect(b.grab_focus)
	b.pressed.connect(func() -> void:
		Menus.sound("confirm")
		action.call())
	return b


func _on_tab(i: int) -> void:
	if i == 2:
		Menus.sound("confirm")
		Menus.push(SettingsScreen.new())
		return
	if i != _tab:
		Menus.sound("navigate")
		_show_tab(i)


func focus_default() -> void:
	if Menus.is_open() or _first == null:
		return
	_first.call_deferred("grab_focus")


func on_reveal() -> void:
	focus_default()


func _on_play() -> void:
	if _starting >= 0.0:
		return
	Menus.sound("confirm")
	_starting = COUNTDOWN


func _cancel_start() -> void:
	_starting = -1.0
	_play.text = "PLAY"
	var arrow := _play.get_meta("arrow") as Label
	arrow.text = "→"
	arrow.add_theme_font_override("font", UIStyle.font("ui_medium"))
	arrow.add_theme_font_size_override("font_size", 28)
	arrow.offset_left = -72
	Menus.sound("back")


func _process(delta: float) -> void:
	if _starting < 0.0:
		return
	_starting -= delta
	_play.text = "STARTING  0:%02d" % ceili(maxf(_starting, 0.0))
	var arrow := _play.get_meta("arrow") as Label
	arrow.text = "ESC CANCEL"
	arrow.add_theme_font_override("font", UIStyle.tracked_font(16, 0.16, true))
	arrow.add_theme_font_size_override("font_size", 16)
	arrow.offset_left = -220
	if _starting <= 0.0:
		_starting = -1.0
		Menus.stop_music()
		LoadingScreen.go(MATCH_SCENE, "Battle royale  ·  solo", "The ring\nawaits.", "Loading Ringfall")


func _go_range() -> void:
	Menus.stop_music()
	LoadingScreen.go(RANGE_SCENE, "Training", "Firing\nrange.", "Loading firing range")


func _learn() -> void:
	Menus.push(LearnControls.new())


func _edit_callsign() -> void:
	Menus.push(CallsignDialog.new(func(name: String) -> void: _callsign.text = name))


func _unhandled_input(event: InputEvent) -> void:
	if Menus.is_open():
		return
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		if _starting >= 0.0:
			_cancel_start()
		else:
			_on_tab(2)
		return
	var key := event as InputEventKey
	if key and key.pressed and not key.echo:
		if key.physical_keycode == KEY_Q and _tab != 0:
			_on_tab(0)
		elif key.physical_keycode == KEY_E and _tab != 1:
			_on_tab(1)
