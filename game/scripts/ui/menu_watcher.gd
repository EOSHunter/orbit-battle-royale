class_name MenuWatcher
extends Node
## Opens the in-match menu when the player presses Esc, or when the browser
## takes the mouse back on its own (Esc while the pointer is locked never
## reaches the page; alt-tab and focus loss also release it). Add one to any
## scene with a player.

var context := ""
var practice := false
var _player: Player
var _was_captured := false


func _init(p_context: String, p_practice := false) -> void:
	context = p_context
	practice = p_practice


func _ready() -> void:
	_player = get_tree().get_first_node_in_group("player") as Player


func _blocked() -> bool:
	# Inventory, the F1 tuning panel and menus turn combat input off while open.
	return Menus.is_open() or _player == null or not _player.is_alive() or not _player.combat_input


func _process(_delta: float) -> void:
	var captured := MouseLock.is_captured()
	if _was_captured and not captured and not _blocked():
		GameMenu.open(context, practice)
	_was_captured = captured


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel") and not _blocked():
		get_viewport().set_input_as_handled()
		GameMenu.open(context, practice)
