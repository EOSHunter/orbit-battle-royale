extends Node3D
## Playground flow: mouse capture (with a free-look fallback where the browser
## refuses pointer lock), teleports between test areas, respawn, and catching
## falls below the course.

const KILL_HEIGHT := -60.0
## How long to wait for the browser to grant pointer lock before falling back.
const LOCK_TIMEOUT := 0.6

@onready var player: Player = $Player
@onready var hud: CanvasLayer = $HUD
@onready var _markers: Node3D = $Markers

var _last_marker := "Spawn"
var _lock_wait := 0.0
var _lock_refused := false


func _ready() -> void:
	hud.player = player
	player.landed.connect(func(drop: float, _speed: float) -> void: hud.show_landing(drop))
	teleport("Spawn")


func _unhandled_input(event: InputEvent) -> void:
	var button := event as InputEventMouseButton
	var playing := Input.mouse_mode == Input.MOUSE_MODE_CAPTURED or (_lock_refused and Input.mouse_mode == Input.MOUSE_MODE_HIDDEN)
	if button and button.pressed and button.button_index == MOUSE_BUTTON_LEFT and not playing and not hud.is_tuning_open():
		get_viewport().set_input_as_handled()
		player.input_grace = 0.25
		if _lock_refused:
			_enter_free_look()
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
			_lock_wait = LOCK_TIMEOUT
	elif event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		player.free_look = false
	elif event.is_action_pressed("toggle_tuning"):
		hud.toggle_tuning()
		player.free_look = false


func _enter_free_look() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_HIDDEN
	player.free_look = true


func _physics_process(delta: float) -> void:
	if _lock_wait > 0.0:
		_lock_wait -= delta
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			_lock_wait = 0.0
		elif _lock_wait <= 0.0:
			# This browser view won't lock the pointer: play with a hidden cursor instead.
			_lock_refused = true
			hud.set_lock_refused(true)
			_enter_free_look()

	if Input.is_action_just_pressed("respawn"):
		teleport(_last_marker)
	for i in _markers.get_child_count():
		if i < 4 and Input.is_action_just_pressed("teleport_%d" % (i + 1)):
			teleport(_markers.get_child(i).name)
	if player.global_position.y < KILL_HEIGHT:
		teleport(_last_marker)


func teleport(marker_name: String) -> void:
	var marker := _markers.get_node_or_null(marker_name) as Node3D
	if marker == null:
		return
	_last_marker = marker_name
	player.teleport_to(marker.global_transform)
