class_name GameMenu
extends Control
## The in-match menu (Esc). Layout from the menu designs: the game keeps
## running behind a scrim that is solid on the left 30% and clear past 40%;
## a 560 px column at 96 px in holds the mode eyebrow on a rule, a 172 px
## "MENU", "• MATCH CONTINUES" in the warning color, 36 px entries (Resume,
## Settings, Practice analytics or Match stats, Report a problem), Leave match
## under a rule near the bottom, and key hints.

const MAIN_MENU := "res://scenes/main_menu.tscn"

## The frame just before the menu opened, attached to problem reports.
static var screenshot: Image

var _context := ""
var _practice := false
var _items: Array[Button] = []


## Open the menu over the match. `context` names the mode ("Ringfall",
## "Firing range"); `practice` switches stats to practice analytics.
static func open(context: String, practice := false) -> void:
	if Menus.is_open():
		return
	var tree := Engine.get_main_loop() as SceneTree
	screenshot = tree.root.get_texture().get_image() if tree and tree.root and DisplayServer.get_name() != "headless" else null
	Menus.push(GameMenu.new(context, practice))


func _init(context: String, practice: bool) -> void:
	_context = context
	_practice = practice
	theme = UIStyle.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	add_child(UIStyle.gradient([[0.0, Color(UIStyle.BG, 0.97)], [0.3, Color(UIStyle.BG, 0.96)], [0.4, Color(UIStyle.BG, 0.3)], [1.0, Color(UIStyle.BG, 0.15)]]))
	var mn := Control.new()
	UIStyle.place(self, mn, 96, 96, -1, 72, 560, 0)

	var top := UIStyle.vbox(0)
	UIStyle.place(mn, top, 0, 0, 0, -1)
	var ctx := UIStyle.hbox(24)
	ctx.add_child(UIStyle.eyebrow(_context))
	var line := UIStyle.rule(Color(UIStyle.TEXT, 0.5))
	line.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	line.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	ctx.add_child(line)
	top.add_child(ctx)
	top.add_child(UIStyle.spacer(40))
	top.add_child(UIStyle.title("Menu", 172, 0.8))
	top.add_child(UIStyle.spacer(26))
	var sub := UIStyle.hbox(12)
	sub.add_child(Glyph.new("dot", UIStyle.WARNING, 10))
	sub.add_child(UIStyle.tracked("Match continues", 20, 0.26, UIStyle.WARNING))
	top.add_child(sub)
	top.add_child(UIStyle.spacer(80))
	var list := UIStyle.vbox(4)
	top.add_child(_outdent(list))
	_items.append(_item(list, "Resume", 36, _do_resume))
	_items.append(_item(list, "Settings", 36, func() -> void: Menus.push(SettingsScreen.new())))
	_items.append(_item(list, "Practice analytics" if _practice else "Match stats", 36, func() -> void: Menus.push(AnalyticsPanel.new(_practice))))
	_items.append(_item(list, "Report a problem", 36, func() -> void: Menus.push(ReportScreen.new(_context))))

	var bottom := UIStyle.vbox(0)
	UIStyle.place(mn, bottom, 0, -1, 0, 0)
	bottom.add_child(UIStyle.rule(Color(UIStyle.TEXT, 0.4)))
	bottom.add_child(UIStyle.spacer(14))
	var leave_box := UIStyle.vbox(0)
	bottom.add_child(_outdent(leave_box))
	_items.append(_item(leave_box, "Leave match", 28, _confirm_leave))
	bottom.add_child(UIStyle.spacer(40))
	bottom.add_child(UIStyle.hint_bar([["Esc", "Resume"], ["↑↓", "Select", false], ["Enter", "Open", false]]))
	for i in _items.size():
		var a: Button = _items[i]
		var b: Button = _items[(i + 1) % _items.size()]
		a.focus_neighbor_bottom = a.get_path_to(b)
		b.focus_neighbor_top = b.get_path_to(a)


## Entries hang 24 px left so their text lines up with the column.
func _outdent(c: Control) -> MarginContainer:
	var m := MarginContainer.new()
	m.add_theme_constant_override("margin_left", -24)
	m.add_child(c)
	return m


func _item(parent: Control, text: String, size: int, action: Callable) -> Button:
	var b := UIStyle.menu_item(text.to_upper(), size)
	b.pressed.connect(func() -> void:
		Menus.sound("confirm")
		action.call())
	parent.add_child(b)
	return b


func focus_default() -> void:
	_items[0].grab_focus()


func on_reveal() -> void:
	focus_default()


func _do_resume() -> void:
	Menus.pop()
	MouseLock.capture()


## Esc resumes, capturing the mouse again (the key press is a user gesture
## the browser accepts).
func on_back() -> bool:
	_do_resume()
	return true


func _confirm_leave() -> void:
	Menus.push(ConfirmDialog.new("Leave match?",
		"You'll return to the main menu. %s" % ("Your practice stats for this session are cleared." if _practice else "The match ends for you and doesn't count."),
		"Leave match", func() -> void:
			Menus.clear()
			(Engine.get_main_loop() as SceneTree).change_scene_to_file(MAIN_MENU)))
