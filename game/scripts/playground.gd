extends Node3D
## Playground flow: mouse capture (with a fallback where the browser refuses
## pointer lock), teleports between test areas, respawn, and catching falls
## below the course.

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
	if button and button.pressed and button.button_index == MOUSE_BUTTON_LEFT \
			and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED and not hud.is_tuning_open():
		# Ask for pointer lock on every click; some browsers only grant it on a
		# later click. Until it is refused once, this click only captures.
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		_lock_wait = LOCK_TIMEOUT
		if not _lock_refused:
			player.input_grace = 0.25
			get_viewport().set_input_as_handled()
	elif event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	elif event.is_action_pressed("toggle_tuning"):
		hud.toggle_tuning()


func _physics_process(delta: float) -> void:
	if _lock_wait > 0.0:
		_lock_wait -= delta
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			_lock_wait = 0.0
			_set_lock_refused(false)
		elif _lock_wait <= 0.0:
			_set_lock_refused(true)

	if Input.is_action_just_pressed("respawn"):
		teleport(_last_marker)
	for i in _markers.get_child_count():
		if i < 4 and Input.is_action_just_pressed("teleport_%d" % (i + 1)):
			teleport(_markers.get_child(i).name)
	if player.global_position.y < KILL_HEIGHT:
		teleport(_last_marker)


func _set_lock_refused(refused: bool) -> void:
	_lock_refused = refused
	hud.set_lock_refused(refused)


func teleport(marker_name: String) -> void:
	var marker := _markers.get_node_or_null(marker_name) as Node3D
	if marker == null:
		return
	_last_marker = marker_name
	player.teleport_to(marker.global_transform)
