class_name ResultsScreen
extends Control
## End of match. Layout from the menu designs: key art behind a left
## gradient; the mode eyebrow at 84/56; at 84/116 (800 px) a 20 px result
## eyebrow with a rule, a 124 px title, the placement, a row of 64 px stats
## between rules (counting up), personal bests, "How did that match feel?"
## with 1–5 ratings, and an 80 px button. Victory adds falling confetti.

const MAIN_MENU := "res://scenes/main_menu.tscn"
const FEEL := [["smoothness", "Smoothness"], ["hit_reg", "Hit registration"], ["fun", "Fun"]]

var _victory: bool
var _placement: int
var _field: int
var _by: String
var _replay: Callable
var _feel := {}
var _feel_rows := {}
var _thanks: Control
var _play: Button
var _counters: Array[Dictionary] = []
var _t := 0.0
var _confetti: Array[Dictionary] = []
var _confetti_layer: Control


## `placement` 1 is a win; `field` is how many started; `by` names who
## eliminated the player; `replay` restarts the match.
func _init(victory: bool, placement: int, field: int, by: String, replay: Callable) -> void:
	_victory = victory
	_placement = placement
	_field = field
	_by = by
	_replay = replay
	theme = UIStyle.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	add_child(UIStyle.fill(UIStyle.BG))
	add_child(UIStyle.key_art(true))
	add_child(UIStyle.gradient([[0.0, Color(UIStyle.BG, 0.98)], [0.36, Color(UIStyle.BG, 0.95)], [0.48, Color(UIStyle.BG, 0.55)], [0.62, Color(UIStyle.BG, 0.0)]]))
	add_child(UIStyle.gradient([[0.0, Color(UIStyle.BG, 0.5)], [0.18, Color(UIStyle.BG, 0.0)], [0.8, Color(UIStyle.BG, 0.0)], [1.0, Color(UIStyle.BG, 0.55)]], true))
	_confetti_layer = Control.new()
	_confetti_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	_confetti_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_confetti_layer.draw.connect(_draw_confetti)
	add_child(_confetti_layer)
	UIStyle.place(self, UIStyle.eyebrow("Battle royale  ·  solo  ·  Ringfall"), 84, 56)

	var main := UIStyle.vbox(0)
	UIStyle.place(self, main, 84, 116, -1, -1, 800, 0)
	var eb := UIStyle.hbox(18)
	var line := ColorRect.new()
	var eb_color := UIStyle.ACCENT if _victory else UIStyle.DANGER
	line.color = eb_color
	line.custom_minimum_size = Vector2(44, 2)
	line.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	eb.add_child(line)
	eb.add_child(UIStyle.tracked("Victory" if _victory else "Eliminated by %s" % _by, 20, 0.3, eb_color, true))
	main.add_child(eb)
	main.add_child(UIStyle.spacer(14))
	main.add_child(UIStyle.title("Last one\nstanding." if _victory else "Better luck\nnext drop.", 124, 0.88))
	main.add_child(UIStyle.spacer(16))
	var place := UIStyle.hbox(10)
	place.add_child(UIStyle.label("#%d" % _placement, "display", 36, UIStyle.ACCENT))
	var of := UIStyle.tracked("of %d players" % _field, 20, 0.22, UIStyle.TEXT_2)
	of.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	place.add_child(of)
	main.add_child(place)
	main.add_child(UIStyle.spacer(38))

	var bests := _update_bests()
	main.add_child(UIStyle.rule(UIStyle.LINE))
	var stats := UIStyle.hbox(0)
	main.add_child(stats)
	main.add_child(UIStyle.rule(UIStyle.LINE))
	var cells := [["kills", "Kills", MatchStats.kills, "n"], ["damage", "Damage", roundi(MatchStats.damage), "n"], ["time", "Time in match", int(MatchStats.seconds()), "time"], ["accuracy", "Accuracy", roundi(MatchStats.accuracy() * 100.0), "pct"]]
	for i in cells.size():
		if i > 0:
			stats.add_child(UIStyle.rule(UIStyle.LINE, true))
		var cell := MarginContainer.new()
		cell.add_theme_constant_override("margin_left", 0 if i == 0 else 36)
		cell.add_theme_constant_override("margin_right", 36)
		cell.add_theme_constant_override("margin_top", 18)
		cell.add_theme_constant_override("margin_bottom", 18)
		var v := UIStyle.vbox(10)
		cell.add_child(v)
		var n := UIStyle.label(_fmt(0, cells[i][3]), "display", 64, UIStyle.TEXT)
		v.add_child(n)
		v.add_child(UIStyle.tracked(cells[i][1], 14, 0.2, UIStyle.TEXT_2))
		if bests.has(cells[i][0]):
			v.add_child(UIStyle.tracked("New best", 14, 0.14, UIStyle.ACCENT))
		stats.add_child(cell)
		_counters.append({"label": n, "to": cells[i][2], "fmt": cells[i][3]})

	main.add_child(UIStyle.spacer(28))
	var best_h := UIStyle.hbox(16)
	if not bests.is_empty():
		var badge := UIStyle.panel(Color(UIStyle.ACCENT, 0.16), 0, Color(0, 0, 0, 0), 2)
		var bl := UIStyle.tracked("New personal best", 14, 0.16, UIStyle.ACCENT, true)
		var bm := MarginContainer.new()
		for side: Array in [["left", 10], ["right", 10], ["top", 5], ["bottom", 5]]:
			bm.add_theme_constant_override("margin_" + side[0], side[1])
		bm.add_child(bl)
		badge.add_child(bm)
		best_h.add_child(badge)
	best_h.add_child(UIStyle.label("Best: %d kills  ·  %d damage  ·  #%d" % [GameSettings.profile("best_kills", 0), GameSettings.profile("best_damage", 0), GameSettings.profile("best_place", _placement)], "ui_bold", 20, UIStyle.TEXT))
	main.add_child(best_h)
	main.add_child(UIStyle.spacer(8))
	var saved := UIStyle.hbox(12)
	saved.add_child(Glyph.new("check", UIStyle.ACCENT, 18))
	saved.add_child(UIStyle.tracked("Personal bests saved on this device", 16, 0.16, UIStyle.TEXT_2))
	main.add_child(saved)

	main.add_child(UIStyle.spacer(30))
	main.add_child(_feel_panel())
	main.add_child(UIStyle.spacer(34))
	var acts := UIStyle.hbox(32)
	main.add_child(acts)
	_play = UIStyle.primary_button("Play again", 440)
	_play.pressed.connect(func() -> void:
		_save_feel()
		Menus.sound("confirm")
		Menus.clear()
		_replay.call()
		MouseLock.capture())
	acts.add_child(_play)
	var menu := UIStyle.secondary_button("BACK TO MENU", 260)
	menu.custom_minimum_size.y = 80
	menu.pressed.connect(func() -> void:
		_save_feel()
		Menus.clear()
		get_tree().change_scene_to_file(MAIN_MENU))
	acts.add_child(menu)
	if _victory and not GameSettings.b("reduce_motion"):
		_spawn_confetti()


func focus_default() -> void:
	_play.grab_focus()


## Esc doesn't dismiss the results; pick an action.
func on_back() -> bool:
	return true


func _fmt(v: float, kind: String) -> String:
	match kind:
		"time":
			return "%d:%02d" % [int(v) / 60, int(v) % 60]
		"pct":
			return "%d%%" % roundi(v)
	return str(roundi(v))


func _process(delta: float) -> void:
	_t += delta
	# Count the stats up over 1.1 s.
	var k := 1.0 if GameSettings.b("reduce_motion") else clampf(_t / 1.1, 0.0, 1.0)
	var e := 1.0 - pow(1.0 - k, 3.0)
	for c in _counters:
		(c.label as Label).text = _fmt(float(c.to) * e, c.fmt)
	if not _confetti.is_empty():
		for p in _confetti:
			p.pos += p.vel * delta * 60.0 + Vector2(sin((_t * 1000.0 + p.rot * 400.0) / 500.0) * 0.6, 0)
			p.rot += p.spin
		_confetti_layer.queue_redraw()
		if _t > 3.6:
			_confetti.clear()
			_confetti_layer.queue_redraw()


func _spawn_confetti() -> void:
	var cols := [UIStyle.ACCENT, UIStyle.TEXT, UIStyle.ACCENT.lightened(0.2), UIStyle.TEXT_2]
	for i in 170:
		_confetti.append({"pos": Vector2(randf() * 1920.0, -randf() * 700.0 - 20.0), "vel": Vector2(randf_range(-0.8, 0.8), randf_range(2.2, 5.2)),
			"rot": randf() * TAU, "spin": randf_range(-0.1, 0.1), "w": randf_range(6, 14), "h": randf_range(3, 7), "c": cols[i % cols.size()]})


func _draw_confetti() -> void:
	var fade := clampf((3.6 - _t) / 0.7, 0.0, 1.0)
	for p in _confetti:
		var c: Color = p.c
		c.a = fade
		_confetti_layer.draw_set_transform(p.pos, p.rot, Vector2.ONE)
		_confetti_layer.draw_rect(Rect2(-p.w * 0.5, -p.h * 0.5, p.w, p.h * absf(cos(p.rot * 2.0))), c)
	_confetti_layer.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _update_bests() -> Array[String]:
	var news: Array[String] = []
	if MatchStats.kills > int(GameSettings.profile("best_kills", 0)):
		news.append("kills")
		GameSettings.set_profile("best_kills", MatchStats.kills)
	if roundi(MatchStats.damage) > int(GameSettings.profile("best_damage", 0)):
		news.append("damage")
		GameSettings.set_profile("best_damage", roundi(MatchStats.damage))
	if _placement < int(GameSettings.profile("best_place", 999)):
		news.append("placement")
		GameSettings.set_profile("best_place", _placement)
	return news


func _feel_panel() -> Control:
	var v := UIStyle.vbox(14)
	v.custom_minimum_size.x = 780
	var head := UIStyle.hbox(0)
	head.add_child(UIStyle.eyebrow("How did that match feel?", UIStyle.TEXT))
	head.add_child(UIStyle.expander(false))
	head.add_child(UIStyle.eyebrow("Optional  ·  3 taps"))
	v.add_child(head)
	var rates := UIStyle.hbox(30)
	v.add_child(rates)
	for f: Array in FEEL:
		var col := UIStyle.vbox(8)
		col.add_child(UIStyle.tracked(f[1], 14, 0.16, UIStyle.TEXT_2))
		var seg := UIStyle.hbox(4)
		var buttons: Array[Button] = []
		for n in 5:
			var b := Button.new()
			b.text = str(n + 1)
			b.custom_minimum_size = Vector2(40, 38)
			b.add_theme_font_override("font", UIStyle.tracked_font(16, 0.0, true))
			b.pressed.connect(func() -> void:
				_feel[f[0]] = n + 1
				Menus.sound("toggle")
				_refresh_feel())
			seg.add_child(b)
			buttons.append(b)
		_feel_rows[f[0]] = buttons
		col.add_child(seg)
		rates.add_child(col)
	_thanks = UIStyle.hbox(12)
	_thanks.add_child(Glyph.new("check", UIStyle.ACCENT, 18))
	_thanks.add_child(UIStyle.tracked("Thanks. Ratings saved with this match.", 16, 0.16, UIStyle.TEXT_2))
	_thanks.visible = false
	v.add_child(_thanks)
	_refresh_feel()
	return v


func _refresh_feel() -> void:
	for id: String in _feel_rows:
		var buttons: Array = _feel_rows[id]
		for i in buttons.size():
			var on: bool = _feel.get(id, 0) == i + 1
			var b := buttons[i] as Button
			var sb := UIStyle.box(UIStyle.RAISED if on else Color(UIStyle.RAISED, 0.75), 2)
			if on:
				sb.border_color = UIStyle.ACCENT
				sb.border_width_bottom = 2
			var hover := sb.duplicate() as StyleBoxFlat
			hover.bg_color = UIStyle.RAISED.lightened(0.06)
			b.add_theme_stylebox_override("normal", sb)
			b.add_theme_stylebox_override("hover", hover)
			b.add_theme_stylebox_override("pressed", sb)
			b.add_theme_color_override("font_color", UIStyle.TEXT if on else UIStyle.TEXT_2)
	_thanks.visible = _feel.size() == FEEL.size()


func _save_feel() -> void:
	if _feel.is_empty():
		return
	var all: Array = GameSettings.profile("feedback", [])
	all.append({"time": Time.get_datetime_string_from_system(), "victory": _victory, "placement": _placement, "ratings": _feel})
	GameSettings.set_profile("feedback", all.slice(-50))
