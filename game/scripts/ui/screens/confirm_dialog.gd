class_name ConfirmDialog
extends Control
## Compact dialog over a 72% scrim. Layout from the menu designs: 680 px
## wide on the surface color, 40 px padding, a 44 px display title, 18 px
## body, and Cancel plus the confirm button (red for destructive actions) at
## the bottom right.

var _title: String
var _body: String
var _ok_text: String
var _on_ok: Callable
var _danger: bool
var _cancel: Button


func _init(title: String, body: String, ok_text: String, on_ok: Callable, danger := true) -> void:
	_title = title
	_body = body
	_ok_text = ok_text
	_on_ok = on_ok
	_danger = danger
	set_meta("overlay", true)
	theme = UIStyle.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	add_child(UIStyle.fill(Color(0.03, 0.045, 0.07, 0.72)))
	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	var p := UIStyle.panel(UIStyle.SURFACE, 40, Color(0, 0, 0, 0), 4)
	p.custom_minimum_size.x = 680
	center.add_child(p)
	var v := UIStyle.vbox(20)
	p.add_child(v)
	var t := UIStyle.title(_title, 44, 1.0)
	v.add_child(t)
	var b := UIStyle.body(_body, 18)
	b.custom_minimum_size.x = 600
	v.add_child(b)
	var row := UIStyle.hbox(16)
	row.alignment = BoxContainer.ALIGNMENT_END
	v.add_child(UIStyle.spacer(0))
	v.add_child(row)
	_cancel = UIStyle.secondary_button("CANCEL", 180)
	_cancel.pressed.connect(func() -> void: Menus.pop())
	row.add_child(_cancel)
	var ok := UIStyle.solid_button(_ok_text.to_upper(), UIStyle.DANGER, 240) if _danger else UIStyle.primary_button(_ok_text.to_upper(), 280, false, "")
	ok.pressed.connect(func() -> void:
		Menus.sound("confirm")
		Menus.pop()
		_on_ok.call())
	row.add_child(ok)
	_cancel.focus_neighbor_right = _cancel.get_path_to(ok)
	ok.focus_neighbor_left = ok.get_path_to(_cancel)


func focus_default() -> void:
	_cancel.grab_focus()
