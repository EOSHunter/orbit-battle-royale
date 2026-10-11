extends Node
## Default input bindings, registered at startup so they live in code review
## rather than in project.godot. Rebinding UI comes later; the prototype's
## settings screen is the reference for how it should behave.


func _ready() -> void:
	_bind("move_forward", [_key(KEY_W)], [_axis(JOY_AXIS_LEFT_Y, -1.0)])
	_bind("move_back", [_key(KEY_S)], [_axis(JOY_AXIS_LEFT_Y, 1.0)])
	_bind("move_left", [_key(KEY_A)], [_axis(JOY_AXIS_LEFT_X, -1.0)])
	_bind("move_right", [_key(KEY_D)], [_axis(JOY_AXIS_LEFT_X, 1.0)])
	_bind("look_left", [], [_axis(JOY_AXIS_RIGHT_X, -1.0)])
	_bind("look_right", [], [_axis(JOY_AXIS_RIGHT_X, 1.0)])
	_bind("look_up", [], [_axis(JOY_AXIS_RIGHT_Y, -1.0)])
	_bind("look_down", [], [_axis(JOY_AXIS_RIGHT_Y, 1.0)])
	_bind("jump", [_key(KEY_SPACE)], [_button(JOY_BUTTON_A)])
	_bind("sprint", [_key(KEY_SHIFT)], [_button(JOY_BUTTON_LEFT_STICK)])
	_bind("crouch", [_key(KEY_C), _key(KEY_CTRL)], [_button(JOY_BUTTON_B)])
	_bind("grapple", [_mouse(MOUSE_BUTTON_LEFT), _key(KEY_Q)], [_axis(JOY_AXIS_TRIGGER_RIGHT, 1.0)])
	_bind("respawn", [_key(KEY_R)], [_button(JOY_BUTTON_BACK)])
	_bind("toggle_tuning", [_key(KEY_F1), _key(KEY_T)], [_button(JOY_BUTTON_START)])
	for i in 4:
		_bind("teleport_%d" % (i + 1), [_key((KEY_1 + i) as Key)], [])


func _bind(action: StringName, keys: Array, pad: Array, deadzone := 0.2) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action, deadzone)
	for event: InputEvent in keys + pad:
		InputMap.action_add_event(action, event)


func _key(code: Key) -> InputEventKey:
	var e := InputEventKey.new()
	e.physical_keycode = code
	return e


func _mouse(button: MouseButton) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = button
	return e


func _button(button: JoyButton) -> InputEventJoypadButton:
	var e := InputEventJoypadButton.new()
	e.button_index = button
	return e


func _axis(axis: JoyAxis, value: float) -> InputEventJoypadMotion:
	var e := InputEventJoypadMotion.new()
	e.axis = axis
	e.axis_value = value
	return e
