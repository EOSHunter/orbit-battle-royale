extends Node3D
## Playground flow: mouse capture, teleports between test areas, respawn, and
## catching falls below the course.

const KILL_HEIGHT := -60.0

@onready var player: Player = $Player
@onready var hud: CanvasLayer = $HUD
@onready var _markers: Node3D = $Markers

var _last_marker := "Spawn"


func _ready() -> void:
	hud.player = player
	player.landed.connect(func(drop: float, _speed: float) -> void: hud.show_landing(drop))
	teleport("Spawn")


func _unhandled_input(event: InputEvent) -> void:
	var button := event as InputEventMouseButton
	if button and button.pressed and button.button_index == MOUSE_BUTTON_LEFT and not MouseLock.is_captured() and player.combat_input:
		get_viewport().set_input_as_handled()
		player.input_grace = 0.25
		MouseLock.capture()
	elif event.is_action_pressed("ui_cancel"):
		MouseLock.release()


func _physics_process(_delta: float) -> void:
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
