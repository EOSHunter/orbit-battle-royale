extends Node
## Default input bindings, registered at startup so they live in code review
## rather than in project.godot. Rebinding UI comes in Phase 2; the
## prototype's settings screen is the reference for how it should behave.


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

	# Combat
	_bind("fire", [_mouse(MOUSE_BUTTON_LEFT)], [_axis(JOY_AXIS_TRIGGER_RIGHT, 1.0)])
	_bind("aim", [_mouse(MOUSE_BUTTON_RIGHT)], [_axis(JOY_AXIS_TRIGGER_LEFT, 1.0)])
	_bind("reload", [_key(KEY_R)], [_button(JOY_BUTTON_X)])
	_bind("interact", [_key(KEY_E), _key(KEY_F)], [_button(JOY_BUTTON_Y)])
	_bind("inventory", [_key(KEY_TAB), _key(KEY_I)], [_button(JOY_BUTTON_BACK)])
	for i in 5:
		_bind("slot_%d" % (i + 1), [_key((KEY_1 + i) as Key)], [])
	_bind("slot_next", [_mouse(MOUSE_BUTTON_WHEEL_DOWN)], [_button(JOY_BUTTON_RIGHT_SHOULDER)])
	_bind("slot_prev", [_mouse(MOUSE_BUTTON_WHEEL_UP)], [_button(JOY_BUTTON_LEFT_SHOULDER)])
	# Quick-fire the Tethercaster from any slot, as long as it's carried.
	_bind("grapple", [_key(KEY_Q)], [_button(JOY_BUTTON_RIGHT_STICK)])

	# Session
	_bind("respawn", [_key(KEY_F5)], [_button(JOY_BUTTON_DPAD_DOWN)])
	_bind("toggle_tuning", [_key(KEY_F1)], [_button(JOY_BUTTON_START)])
	for i in 4:
		_bind("teleport_%d" % (i + 1), [_key((KEY_F6 + i) as Key)], [])


const SCENES := ["res://scenes/arena.tscn", "res://scenes/playground.tscn"]


## F10 switches between the combat arena and the movement playground.
func _unhandled_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key and key.pressed and not key.echo and key.physical_keycode == KEY_F10:
		var current := get_tree().current_scene.scene_file_path
		get_tree().change_scene_to_file(SCENES[1] if current == SCENES[0] else SCENES[0])


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
