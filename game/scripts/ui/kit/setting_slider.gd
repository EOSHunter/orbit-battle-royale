class_name SettingSlider
extends Control
## Settings slider, 360 × 32: a 4 px track, accent fill, and an 18 px knob
## with a dark ring that grows a little on hover and while dragging.

signal changed(value: float)

var min_value := 0.0
var max_value := 1.0
var step := 0.01
var value := 0.0:
	set(v):
		value = v
		queue_redraw()
var _drag := false
var _hover := false


func _init(lo := 0.0, hi := 1.0, p_step := 0.01) -> void:
	min_value = lo
	max_value = hi
	step = p_step
	custom_minimum_size = Vector2(360, 32)
	size_flags_vertical = Control.SIZE_SHRINK_CENTER
	focus_mode = Control.FOCUS_NONE
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	mouse_entered.connect(func() -> void:
		_hover = true
		queue_redraw())
	mouse_exited.connect(func() -> void:
		_hover = false
		queue_redraw())


func _ratio() -> float:
	return clampf((value - min_value) / maxf(max_value - min_value, 0.0001), 0.0, 1.0)


func _set_from_x(x: float) -> void:
	var v := min_value + clampf(x / size.x, 0.0, 1.0) * (max_value - min_value)
	v = snappedf(v, step)
	if not is_equal_approx(v, value):
		value = v
		changed.emit(v)


func _gui_input(event: InputEvent) -> void:
	var m := event as InputEventMouseButton
	if m and m.button_index == MOUSE_BUTTON_LEFT:
		_drag = m.pressed
		if m.pressed:
			_set_from_x(m.position.x)
		queue_redraw()
		accept_event()
	var mm := event as InputEventMouseMotion
	if mm and _drag:
		_set_from_x(mm.position.x)
		accept_event()


func _draw() -> void:
	var y := size.y * 0.5
	draw_rect(Rect2(0, y - 2, size.x, 4), UIStyle.TRACK)
	draw_rect(Rect2(0, y - 2, size.x * _ratio(), 4), UIStyle.ACCENT)
	var x := size.x * _ratio()
	var k := 1.2 if _hover or _drag else 1.0
	draw_circle(Vector2(x, y), 13.0 * k, Color(UIStyle.BG, 0.6))
	draw_circle(Vector2(x, y), 9.0 * k, UIStyle.TEXT)
