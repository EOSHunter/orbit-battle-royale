class_name Menus
extends CanvasLayer
## The overlay manager (autoload "MenuLayer"). Menu screens are pushed onto one
## stack drawn above the game; Esc (or controller B) closes one layer at a time,
## gameplay input stops while any screen is open, and the mouse is released.
## Also plays interface sounds and menu music on their mixer buses.
##
## Everything is static so gameplay scripts (and headless tests, where the
## autoload may not exist) can call Menus.push() / Menus.is_open() safely.

const SOUNDS := {
	"navigate": "res://assets/audio/ui-audio/interface-sounds/navigate.wav",
	"confirm": "res://assets/audio/ui-audio/interface-sounds/confirm.wav",
	"back": "res://assets/audio/ui-audio/interface-sounds/back.wav",
	"toggle": "res://assets/audio/ui-audio/interface-sounds/toggle.wav",
	"tick": "res://assets/audio/ui-audio/interface-sounds/slider-tick.wav",
	"error": "res://assets/audio/ui-audio/interface-sounds/error.wav",
}
const MENU_MUSIC := "res://assets/audio/music/main-menu-theme/main-menu-theme-loop.wav"

static var _inst: Menus
var _stack: Array[Control] = []
var _players: Array[AudioStreamPlayer] = []
var _streams := {}
var _music: AudioStreamPlayer
var _music_tween: Tween
var _last_nav := 0


func _ready() -> void:
	_inst = self
	layer = 60
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in 4:
		var p := AudioStreamPlayer.new()
		p.bus = "UI"
		add_child(p)
		_players.append(p)
	_music = AudioStreamPlayer.new()
	_music.bus = "Music"
	add_child(_music)
	get_viewport().gui_focus_changed.connect(_on_focus_changed)


# ---------------------------------------------------------------- stack

static func push(screen: Control) -> void:
	if _inst == null:
		return
	_inst._push(screen)


static func pop() -> void:
	if _inst and not _inst._stack.is_empty():
		_inst._pop()


## Close every screen (e.g. when leaving the match).
static func clear() -> void:
	if _inst == null:
		return
	while not _inst._stack.is_empty():
		var s: Control = _inst._stack.pop_back()
		s.queue_free()
	_inst._update_gameplay()


static func is_open() -> bool:
	return _inst != null and not _inst._stack.is_empty()


static func top() -> Control:
	return _inst._stack.back() if is_open() else null


func _push(screen: Control) -> void:
	# Dialogs (meta "overlay") sit over the screen beneath; full screens replace it.
	if not _stack.is_empty() and not screen.get_meta("overlay", false):
		_stack.back().visible = false
	_stack.append(screen)
	add_child(screen)
	_update_gameplay()
	_fade_in(screen)
	_focus(screen)


func _pop() -> void:
	var s: Control = _stack.pop_back()
	s.queue_free()
	sound("back")
	if not _stack.is_empty():
		var under: Control = _stack.back()
		under.visible = true
		if under.has_method("on_reveal"):
			under.call("on_reveal")
		_focus(under)
	_update_gameplay()


func _focus(screen: Control) -> void:
	if screen.has_method("focus_default"):
		screen.call_deferred("focus_default")


func _fade_in(screen: Control) -> void:
	if GameSettings.b("reduce_motion"):
		return
	screen.modulate.a = 0.0
	create_tween().tween_property(screen, "modulate:a", 1.0, 0.14)


## While any screen is open the player can't act and the mouse is free.
func _update_gameplay() -> void:
	var open := not _stack.is_empty()
	for p in get_tree().get_nodes_in_group("player"):
		if "combat_input" in p:
			p.combat_input = not open
			if not open and "input_grace" in p:
				p.input_grace = 0.2
	if open:
		MouseLock.release()


func _unhandled_input(event: InputEvent) -> void:
	if _stack.is_empty():
		return
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		var s: Control = _stack.back()
		if s.has_method("on_back") and s.call("on_back"):
			return
		_pop()


# ---------------------------------------------------------------- sound

static func sound(name: String) -> void:
	if _inst == null or not SOUNDS.has(name):
		return
	_inst._play(name)


func _play(name: String) -> void:
	if not _streams.has(name):
		_streams[name] = load(SOUNDS[name]) if ResourceLoader.exists(SOUNDS[name]) else null
	var stream: AudioStream = _streams[name]
	if stream == null:
		return
	for p in _players:
		if not p.playing:
			p.stream = stream
			p.play()
			return
	_players[0].stream = stream
	_players[0].play()


func _on_focus_changed(c: Control) -> void:
	# A short tick when keyboard/controller focus moves between controls.
	var now := Time.get_ticks_msec()
	if c is BaseButton and now - _last_nav > 60:
		_last_nav = now
		_play("navigate")


static func play_music(fade := 1.5) -> void:
	if _inst == null:
		return
	var m := _inst._music
	if m.playing:
		return
	if m.stream == null and ResourceLoader.exists(MENU_MUSIC):
		var s := load(MENU_MUSIC) as AudioStreamWAV
		if s:
			s.loop_mode = AudioStreamWAV.LOOP_FORWARD
			if s.loop_end <= 0:
				s.loop_end = int(s.get_length() * s.mix_rate)
		m.stream = s
	if m.stream == null:
		return
	m.volume_db = -40.0
	m.play()
	if _inst._music_tween:
		_inst._music_tween.kill()
	_inst._music_tween = _inst.create_tween()
	_inst._music_tween.tween_property(m, "volume_db", 0.0, fade)


static func stop_music(fade := 1.2) -> void:
	if _inst == null or not _inst._music.playing:
		return
	var m := _inst._music
	if _inst._music_tween:
		_inst._music_tween.kill()
	_inst._music_tween = _inst.create_tween()
	_inst._music_tween.tween_property(m, "volume_db", -40.0, fade)
	_inst._music_tween.tween_callback(m.stop)
