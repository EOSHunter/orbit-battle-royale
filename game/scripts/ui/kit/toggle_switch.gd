class_name ToggleSwitch
extends Control
## On/off switch, 56 × 30: a track with a 22 px knob that slides 26 px. Off is
## a dark track with a muted knob; on is an accent-tinted track with an accent
## outline and an accent knob.

signal toggled(on: bool)

var on := false:
	set(v):
		on = v
		queue_redraw()


func _init() -> void:
	custom_minimum_size = Vector2(56, 30)
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	focus_mode = Control.FOCUS_NONE


func _gui_input(event: InputEvent) -> void:
	var m := event as InputEventMouseButton
	if m and m.pressed and m.button_index == MOUSE_BUTTON_LEFT:
		on = not on
		toggled.emit(on)
		accept_event()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, Vector2(56, 30))
	_pill(r, Color(UIStyle.ACCENT, 0.3) if on else UIStyle.TRACK)
	if on:
		_pill_outline(r, UIStyle.ACCENT)
	draw_circle(Vector2(41.0 if on else 15.0, 15.0), 11.0, UIStyle.ACCENT if on else UIStyle.TEXT_2)


func _pill(r: Rect2, color: Color) -> void:
	var rad := r.size.y * 0.5
	draw_circle(Vector2(r.position.x + rad, r.get_center().y), rad, color)
	draw_circle(Vector2(r.end.x - rad, r.get_center().y), rad, color)
	draw_rect(Rect2(r.position.x + rad, r.position.y, r.size.x - rad * 2.0, r.size.y), color)


func _pill_outline(r: Rect2, color: Color) -> void:
	var rad := r.size.y * 0.5 - 0.5
	draw_arc(Vector2(r.position.x + rad + 0.5, r.get_center().y), rad, PI * 0.5, PI * 1.5, 16, color, 1.0, true)
	draw_arc(Vector2(r.end.x - rad - 0.5, r.get_center().y), rad, -PI * 0.5, PI * 0.5, 16, color, 1.0, true)
	draw_line(Vector2(r.position.x + rad, 0.5), Vector2(r.end.x - rad, 0.5), color, 1.0)
	draw_line(Vector2(r.position.x + rad, r.end.y - 0.5), Vector2(r.end.x - rad, r.end.y - 0.5), color, 1.0)
