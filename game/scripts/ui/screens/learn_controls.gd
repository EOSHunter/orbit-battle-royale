class_name LearnControls
extends Control
## The controls guide. Layout from the menu designs: the wordmark at 72/40,
## a "Learn controls" header rule from x 600, the step list (380 px, 23 px
## entries) at 72/220, the lesson at 520/220 (progress, 150 px title, a 460 px
## rule that fills as you go, 25 px text), 64 px keycaps in captioned groups
## at y 700, and a 300 × 92 NEXT button with Skip guide / Practice links at
## the bottom right. Keys follow the player's current bindings.

## [title, text, [[rows of keys], caption]...]. "@action" shows the bound key;
## "MOUSE" draws the mouse.
const STEPS := [
	["Move", "Move around and look with the mouse. Click the game to capture the cursor; Esc opens the menu.",
		[[[["@move_forward"], ["@move_left", "@move_back", "@move_right"]], "Move"], [[["MOUSE"]], "Look around"]]],
	["Sprint, crouch and jump", "Sprint across open ground, crouch to steady your aim and stay low, and jump onto ledges. There's no fall damage.",
		[[[["@sprint"]], "Sprint"], [[["@crouch"]], "Crouch"], [[["@jump"]], "Jump"]]],
	["Tethercaster", "Fire it at terrain or a structure to reel yourself in. Hold crouch to swing instead; jump to let go with a boost.",
		[[[["@grapple"]], "Fire / release"], [[["@crouch"]], "Swing"], [[["@jump"]], "Let go"]]],
	["Take a weapon", "Walk over a weapon and interact to pick it up. Weapons go in slots 1 and 2, everything else in 3 to 5.",
		[[[["@interact"]], "Pick up"], [[["1", "2", "3", "4", "5"]], "Slots"]]],
	["Aim and fire", "Aim down the iron sights for accuracy: shots land where the sights meet the crosshair. Moving spreads your shots.",
		[[[["@aim"]], "Aim"], [[["@fire"]], "Fire"]]],
	["Reload", "Reload behind cover. Switching slots cancels a reload. Ammunition is shared by every weapon of the same type.",
		[[[["@reload"]], "Reload"]]],
	["Heal", "Select a healing item and fire to use it. Sprinting, firing or switching stops it, and you keep the item.",
		[[[["3", "4", "5"]], "Select"], [[["@fire"]], "Use"]]],
	["Inventory", "Open your inventory to equip, move, split or drop items, and to swap what's on the ground for what you carry.",
		[[[["@inventory"]], "Inventory"], [[["M", "S", "X"]], "Move · split · drop"]]],
]
const SEEN_KEY := "guide_seen"

var _from_menu := true
var _step := 0
var _seen: Array = []
var _list: VBoxContainer
var _list_bar: ColorRect
var _rows: Array[Button] = []
var _prog: Label
var _title: Label
var _rule_fill: ColorRect
var _text: Label
var _keys: HBoxContainer
var _next: Button
var _lesson: Control


func _init(from_menu := true) -> void:
	_from_menu = from_menu
	theme = UIStyle.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	_seen = GameSettings.profile(SEEN_KEY, [])
	add_child(UIStyle.fill(UIStyle.BG))
	add_child(UIStyle.key_art(true))
	add_child(UIStyle.gradient([[0.0, Color(UIStyle.BG, 0.97)], [0.24, Color(UIStyle.BG, 0.94)], [0.38, Color(UIStyle.BG, 0.78)], [0.58, Color(UIStyle.BG, 0.25)], [0.75, Color(UIStyle.BG, 0.05)]]))
	add_child(UIStyle.gradient([[0.0, Color(UIStyle.BG, 0.0)], [0.7, Color(UIStyle.BG, 0.0)], [1.0, Color(UIStyle.BG, 0.7)]], true))
	UIStyle.place(self, UIStyle.logo(340), 72, 40)

	var head := UIStyle.vbox(16)
	UIStyle.place(self, head, 600, 52, -1, -1, 840, 0)
	head.add_child(UIStyle.label("Learn controls", "ui_medium", 26, UIStyle.TEXT))
	head.add_child(UIStyle.rule(Color(UIStyle.TEXT, 0.4)))
	var close := Button.new()
	close.focus_mode = Control.FOCUS_NONE
	close.add_child(UIStyle.key_hint("Esc", "Close"))
	close.custom_minimum_size = Vector2(160, 30)
	close.pressed.connect(Menus.pop)
	UIStyle.place(self, close, -1, 52, 72, -1, 160, 30)

	# Step list with a right rule.
	var list_wrap := UIStyle.hbox(30)
	UIStyle.place(self, list_wrap, 72, 220, -1, -1, 380, 0)
	_list = UIStyle.vbox(0)
	_list.custom_minimum_size.x = 349
	list_wrap.add_child(_list)
	list_wrap.add_child(UIStyle.rule(Color(UIStyle.TEXT, 0.25), true))
	for i in STEPS.size():
		var b := Button.new()
		b.focus_mode = Control.FOCUS_NONE
		b.custom_minimum_size = Vector2(349, 58)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0, 0, 0, 0)
		for s in ["normal", "hover", "pressed", "focus"]:
			b.add_theme_stylebox_override(s, sb)
		var num := UIStyle.tracked("%02d" % (i + 1), 23, 0.0, UIStyle.TEXT_2)
		UIStyle.place(b, num, 30, 15)
		var name := UIStyle.label(STEPS[i][0], "ui", 23, Color(UIStyle.TEXT, 0.85))
		UIStyle.place(b, name, 90, 13)
		var check := Glyph.new("check", UIStyle.SUCCESS, 18)
		UIStyle.place(b, check, -1, 20, 0, -1, 18, 18)
		b.set_meta("num", num)
		b.set_meta("name", name)
		b.set_meta("check", check)
		b.pressed.connect(func() -> void: _go(i))
		_list.add_child(b)
		_rows.append(b)
	_list_bar = ColorRect.new()
	_list_bar.color = UIStyle.ACCENT
	add_child(_list_bar)

	_lesson = Control.new()
	UIStyle.place(self, _lesson, 520, 220, -1, -1, 620, 460)
	var v := UIStyle.vbox(0)
	_lesson.add_child(v)
	_prog = UIStyle.tracked("", 26, 0.0, UIStyle.TEXT)
	v.add_child(_prog)
	v.add_child(UIStyle.spacer(8))
	_title = UIStyle.title("", 150, 0.86)
	v.add_child(_title)
	var rule := Control.new()
	rule.custom_minimum_size = Vector2(460, 5)
	var rl := ColorRect.new()
	rl.color = Color(UIStyle.TEXT, 0.35)
	UIStyle.place(rule, rl, 0, 2, -1, -1, 460, 1)
	_rule_fill = ColorRect.new()
	_rule_fill.color = UIStyle.ACCENT
	UIStyle.place(rule, _rule_fill, 0, 0, -1, -1, 0, 5)
	v.add_child(UIStyle.spacer(34))
	v.add_child(rule)
	v.add_child(UIStyle.spacer(30))
	_text = UIStyle.body("", 25, UIStyle.TEXT)
	_text.custom_minimum_size.x = 520
	_text.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	v.add_child(_text)

	_keys = UIStyle.hbox(60)
	UIStyle.place(self, _keys, 520, 700)

	var acts := UIStyle.vbox(34)
	UIStyle.place(self, acts, -1, -1, 72, 60)
	var buttons := UIStyle.hbox(12)
	buttons.alignment = BoxContainer.ALIGNMENT_END
	acts.add_child(buttons)
	var prev := UIStyle.secondary_button("←", 92)
	prev.custom_minimum_size.y = 92
	prev.add_theme_font_override("font", UIStyle.font("ui_medium"))
	prev.add_theme_font_size_override("font_size", 30)
	prev.pressed.connect(func() -> void: _go(_step - 1))
	buttons.add_child(prev)
	_next = UIStyle.primary_button("Next", 300)
	_next.custom_minimum_size.y = 92
	_next.add_theme_font_size_override("font_size", 46)
	_next.pressed.connect(func() -> void:
		if _step >= STEPS.size() - 1:
			_finish()
		else:
			_go(_step + 1))
	buttons.add_child(_next)
	var links := UIStyle.hbox(40)
	links.alignment = BoxContainer.ALIGNMENT_END
	acts.add_child(links)
	var skip := UIStyle.link("Skip guide", "", 16, 0.22)
	skip.pressed.connect(_finish)
	links.add_child(skip)
	if _from_menu:
		links.add_child(UIStyle.rule(Color(UIStyle.TEXT, 0.3), true, 36))
		var practice := UIStyle.link("Practice in firing range", "", 16, 0.22)
		practice.pressed.connect(func() -> void:
			Menus.clear()
			Menus.stop_music()
			LoadingScreen.go("res://scenes/firing_range.tscn", "Training", "Firing\nrange.", "Loading firing range"))
		links.add_child(practice)
	_go(0)


func focus_default() -> void:
	_next.grab_focus()


func _go(i: int) -> void:
	_step = clampi(i, 0, STEPS.size() - 1)
	if not _seen.has(_step):
		_seen.append(_step)
		GameSettings.set_profile(SEEN_KEY, _seen)
	var s: Array = STEPS[_step]
	_prog.text = "%d / %d" % [_step + 1, STEPS.size()]
	_title.text = s[0]
	_text.text = s[1]
	_next.text = "DONE" if _step == STEPS.size() - 1 else "NEXT"
	var w := 460.0 * (_step + 1) / STEPS.size()
	if GameSettings.b("reduce_motion"):
		_rule_fill.size.x = w
	else:
		create_tween().tween_property(_rule_fill, "size:x", w, 0.36).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	for c in _keys.get_children():
		c.queue_free()
	var groups: Array = s[2]
	for gi in groups.size():
		if gi > 0:
			_keys.add_child(UIStyle.rule(Color(UIStyle.TEXT, 0.25), true))
		_keys.add_child(_key_group(groups[gi][0], groups[gi][1]))
	for r in _rows.size():
		var on := r == _step
		var b := _rows[r]
		(b.get_meta("num") as Label).add_theme_color_override("font_color", UIStyle.ACCENT if on else UIStyle.TEXT_2)
		(b.get_meta("name") as Label).add_theme_color_override("font_color", UIStyle.ACCENT if on else Color(UIStyle.TEXT, 0.85))
		(b.get_meta("check") as Glyph).visible = _seen.has(r) and not on
	_place_bar.call_deferred()
	if not GameSettings.b("reduce_motion"):
		_lesson.modulate.a = 0.0
		create_tween().tween_property(_lesson, "modulate:a", 1.0, 0.26)
	Menus.sound("navigate")


func _place_bar() -> void:
	var b := _rows[_step]
	_list_bar.position = b.global_position - global_position + Vector2(0, 8)
	_list_bar.size = Vector2(4, b.size.y - 16)


## Keycap rows centered above a caption with an underline.
func _key_group(rows: Array, caption: String) -> Control:
	var g := UIStyle.vbox(22)
	var caps := UIStyle.vbox(10)
	for row: Array in rows:
		var h := UIStyle.hbox(10)
		h.alignment = BoxContainer.ALIGNMENT_CENTER
		for k: String in row:
			if k == "MOUSE":
				h.add_child(_mouse_icon())
			else:
				h.add_child(UIStyle.big_key(GameSettings.key_for(k.substr(1)) if k.begins_with("@") else k))
		caps.add_child(h)
	g.add_child(caps)
	var cap := UIStyle.vbox(8)
	var l := UIStyle.tracked(caption, 16, 0.24, Color(UIStyle.TEXT, 0.85))
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	cap.add_child(l)
	cap.add_child(UIStyle.rule(Color(UIStyle.TEXT, 0.4)))
	g.add_child(cap)
	return g


func _mouse_icon() -> Control:
	var c := Control.new()
	c.custom_minimum_size = Vector2(110, 96)
	c.draw.connect(func() -> void:
		var o := Vector2(55, 48)
		var pts := PackedVector2Array()
		for i in 41:
			var a := TAU * i / 40.0
			pts.append(o + Vector2(cos(a) * 20, sin(a) * 32))
		c.draw_polyline(pts, UIStyle.TEXT, 2.0, true)
		c.draw_line(o + Vector2(0, -32), o + Vector2(0, -8), UIStyle.TEXT, 2.0)
		for d in [Vector2(-1, 0), Vector2(1, 0)]:
			c.draw_line(o + d * 30, o + d * 46, UIStyle.TEXT_2, 2.0)
			c.draw_line(o + d * 46, o + d * 40 + Vector2(0, -6), UIStyle.TEXT_2, 2.0)
			c.draw_line(o + d * 46, o + d * 40 + Vector2(0, 6), UIStyle.TEXT_2, 2.0))
	return c


func _finish() -> void:
	Menus.sound("confirm")
	Menus.pop()


# _input: arrow keys would otherwise move button focus first.
func _input(event: InputEvent) -> void:
	if Menus.top() != self:
		return
	if event.is_action_pressed("ui_right"):
		_go(_step + 1)
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("ui_left"):
		_go(_step - 1)
		get_viewport().set_input_as_handled()
