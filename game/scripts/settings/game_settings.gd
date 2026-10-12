class_name GameSettings
extends RefCounted
## Every player setting: the schema the settings screen is built from, the
## saved values (user://settings.cfg, browser storage on the web) and applying
## them to the engine. Gameplay code reads values with GameSettings.f()/b()/s().
##
## Categories and sections follow the menu designs: Mouse & keyboard (Mouse,
## Behavior, Bindings), Controller (Layout, Look, Deadzones), Audio, Video
## (Display, Graphics) and Accessibility.

const PATH := "user://settings.cfg"
const Q := ["Low", "Medium", "High", "Ultra"]

## Rebindable actions, in the order the Bindings section lists them.
const BINDABLE := [
	["move_forward", "Move forward"], ["move_back", "Move back"], ["move_left", "Move left"], ["move_right", "Move right"],
	["jump", "Jump"], ["sprint", "Sprint"], ["crouch", "Crouch"],
	["fire", "Fire / use item"], ["aim", "Aim down sights"], ["reload", "Reload"],
	["interact", "Interact / pick up"], ["inventory", "Inventory"], ["grapple", "Tethercaster"],
	["slot_1", "Slot 1 (weapon)"], ["slot_2", "Slot 2 (weapon)"], ["slot_3", "Slot 3"], ["slot_4", "Slot 4"], ["slot_5", "Slot 5"],
]

static var CATEGORIES: Array = _schema()
static var ROWS := {}
static var _values := {}
static var _loaded := false
static var _listeners: Array[Callable] = []
## Default keyboard/mouse events per action, captured before saved bindings
## are applied, for Restore defaults.
static var _default_binds := {}
static var save_ok := true
## Tests turn this off to play with the defaults and never write the file.
static var use_saved := true


static func _row(id: String, label: String, type: String, def: Variant, help: String, extra := {}) -> Dictionary:
	var r := {"id": id, "label": label, "type": type, "def": def, "help": help}
	r.merge(extra)
	return r


static func _slider(id: String, label: String, lo: float, hi: float, step: float, def: float, unit: String, help: String, extra := {}) -> Dictionary:
	var e := {"min": lo, "max": hi, "step": step, "unit": unit}
	e.merge(extra)
	return _row(id, label, "slider", def, help, e)


static func _schema() -> Array:
	var binds: Array = []
	for b: Array in BINDABLE:
		binds.append(_row("bind." + b[0], b[1], "bind", "", "Select, then press a key or mouse button. Escape cancels; Delete clears the alternate.", {"action": b[0], "viz": "key"}))
	return [
		{"id": "mk", "name": "Mouse & keyboard", "sections": [
			{"id": "mouse", "name": "Mouse", "rows": [
				_slider("sens", "Mouse sensitivity", 0.1, 3.0, 0.05, 1.0, "x", "Rotation speed when looking around (raw input: no OS acceleration).", {"viz": "mouse", "eyebrow": "Input"}),
				_slider("aim_sens", "Aim sensitivity", 0.1, 2.0, 0.05, 0.7, "x", "Multiplier while aiming down sights (on top of the zoom's own scaling).", {"viz": "mouse", "eyebrow": "Input"}),
				_slider("scope_sens", "Scope sensitivity", 0.1, 2.0, 0.05, 1.0, "x", "Multiplier applied when using a magnified scope. Lower values steady long-range shots.", {"viz": "mouse", "eyebrow": "Input"}),
				_row("invert_mouse", "Invert vertical look", "switch", false, "Move the mouse forward to look down.", {"eyebrow": "Input"}),
			]},
			{"id": "behavior", "name": "Behavior", "rows": [
				_row("aim_mode", "Aim", "seg", "Hold", "Hold: aim while the button is held. Toggle: press once to aim, again to stop.", {"options": ["Hold", "Toggle"]}),
				_row("crouch_mode", "Crouch", "seg", "Hold", "How the crouch binding behaves.", {"options": ["Hold", "Toggle"]}),
				_row("sprint_mode", "Sprint", "seg", "Hold", "Auto sprints whenever you move forward. Your sprint key still steadies the scope.", {"options": ["Hold", "Toggle", "Auto"]}),
			]},
			{"id": "bindings", "name": "Bindings", "rows": binds},
		]},
		{"id": "pad", "name": "Controller", "sections": [
			{"id": "layout", "name": "Layout", "rows": [
				_row("swap_sticks", "Swap sticks", "switch", false, "Move with the right stick and look with the left.", {"viz": "pad"}),
			]},
			{"id": "look", "name": "Look", "rows": [
				_slider("pad_look", "Look sensitivity", 0.2, 3.0, 0.05, 1.0, "x", "How fast the camera turns at full stick deflection.", {"viz": "curve"}),
				_slider("pad_aim", "Aim sensitivity", 0.2, 2.0, 0.05, 0.7, "x", "Multiplier while aiming down sights.", {"viz": "curve"}),
				_row("curve", "Response curve", "seg", "Standard", "Standard gives fine control near the centre of the stick. Linear maps stick movement directly to turn speed. Dynamic ramps up sharply at the edge.", {"options": ["Standard", "Linear", "Dynamic"], "viz": "curve"}),
				_row("invert_pad", "Invert vertical look", "switch", false, "Push the stick up to look down."),
			]},
			{"id": "deadzones", "name": "Deadzones", "rows": [
				_slider("dz_left", "Left stick deadzone", 0, 40, 1, 20, "%", "Ignores small stick movement to stop drift. Lower it until your character moves on its own, then raise it slightly.", {"viz": "deadzone"}),
				_slider("dz_right", "Right stick deadzone", 0, 40, 1, 20, "%", "Ignores small stick movement to stop the camera drifting.", {"viz": "deadzone"}),
			]},
		]},
		{"id": "audio", "name": "Audio", "sections": [
			{"id": "volume", "name": "Volume", "rows": [
				_slider("vol_master", "Master volume", 0, 100, 1, 80, "%", "Overall loudness. Every other channel is mixed beneath it.", {"viz": "volume"}),
				_slider("vol_effects", "Combat and world", 0, 100, 1, 100, "%", "Gunfire, footsteps, impacts, vehicles and grenades.", {"viz": "volume"}),
				_slider("vol_ambience", "Ringfall ambience", 0, 100, 1, 70, "%", "Wind, wildlife, the ion storm and distant thunder.", {"viz": "volume"}),
				_slider("vol_music", "Music", 0, 100, 1, 50, "%", "Menu and end-of-match music.", {"viz": "volume"}),
				_slider("vol_ui", "Interface", 0, 100, 1, 80, "%", "Menu sounds, pickups and alerts.", {"viz": "volume"}),
			]},
		]},
		{"id": "video", "name": "Video", "sections": [
			{"id": "display", "name": "Display", "rows": [
				_row("window_mode", "Window mode", "choice", "Browser window", "Fullscreen hides the browser's interface. Esc leaves fullscreen.", {"options": ["Browser window", "Fullscreen"], "eyebrow": "Display"}),
				_row("fps_limit", "Frame rate limit", "choice", "Unlimited", "Caps how many frames are drawn each second. Unlimited follows your display's refresh rate in the browser.", {"options": ["30", "60", "120", "144", "240", "Unlimited"], "eyebrow": "Display"}),
				_slider("res3d", "3D resolution", 50, 100, 5, 100, "%", "Renders the world below native resolution and scales it up. The interface stays sharp.", {"eyebrow": "Display"}),
				_row("dynamic_res", "Dynamic resolution", "switch", false, "Lowers 3D resolution automatically during heavy scenes to hold the frame rate limit.", {"eyebrow": "Display"}),
				_slider("fov", "Field of view", 70, 120, 1, 110, "°", "How much of the world you see horizontally. Wider shows more at the edges; narrower makes targets larger.", {"viz": "fov", "eyebrow": "Display"}),
				_row("show_fps", "Show FPS", "switch", false, "A small frame-time readout in the top-right corner (F3 also toggles it).", {"eyebrow": "Display"}),
			]},
			{"id": "graphics", "name": "Graphics", "rows": [
				_row("preset", "Quality preset", "choice", "High", "Sets every option below. Changing one option switches the preset to Custom.", {"options": Q + ["Custom"], "viz": "preset", "eyebrow": "Graphics"}),
				_row("shadows", "Shadows", "choice", "High", "Shadow resolution and how far shadows are drawn.", {"options": Q, "viz": "preset", "group": "gfx", "eyebrow": "Graphics"}),
				_row("foliage", "Foliage density", "choice", "High", "How much grass and small vegetation is drawn. Lower settings can reveal players hiding in Bloomwild.", {"options": Q, "viz": "preset", "group": "gfx", "eyebrow": "Graphics"}),
				_row("view_distance", "View distance", "choice", "High", "How far terrain detail, props and structures are drawn.", {"options": Q, "viz": "preset", "group": "gfx", "eyebrow": "Graphics"}),
				_row("aa", "Anti-aliasing", "choice", "Off", "Smooths jagged edges on geometry. Costs frame rate, more at 4x. Not part of the preset.", {"options": ["Off", "MSAA 2x", "MSAA 4x"], "viz": "preset", "eyebrow": "Graphics"}),
			]},
		]},
		{"id": "access", "name": "Accessibility", "sections": [
			{"id": "comfort", "name": "Comfort & readability", "rows": [
				_row("reduce_motion", "Reduced camera motion", "switch", false, "Removes non-essential menu animation and screen effects.", {"viz": "hud", "eyebrow": "Comfort"}),
				_slider("hud_scale", "HUD scale", 70, 130, 5, 100, "%", "Size of every HUD group. They move together and stay inside the safe area.", {"viz": "hud", "eyebrow": "Readability"}),
				_row("damage_direction", "Damage direction indicator", "switch", true, "A red arc around the crosshair points toward whoever hit you.", {"viz": "hud", "eyebrow": "Readability"}),
				_row("low_health", "Low-health warning", "switch", true, "Red screen edges while health is low.", {"viz": "hud", "eyebrow": "Readability"}),
			]},
		]},
	]


# ---------------------------------------------------------------- values

static func ensure_loaded() -> void:
	if _loaded:
		return
	_loaded = true
	for cat: Dictionary in CATEGORIES:
		for sec: Dictionary in cat.sections:
			for r: Dictionary in sec.rows:
				r.cat = cat.id
				r.sec = sec.id
				ROWS[r.id] = r
				if r.type != "bind":
					_values[r.id] = r.def
	var cfg := ConfigFile.new()
	if use_saved and cfg.load(PATH) == OK:
		for id in cfg.get_section_keys("settings") if cfg.has_section("settings") else PackedStringArray():
			if ROWS.has(id) and ROWS[id].type != "bind":
				_values[id] = cfg.get_value("settings", id)
		if cfg.has_section("bindings"):
			for action in cfg.get_section_keys("bindings"):
				_values["bind." + action] = cfg.get_value("bindings", action)
		if cfg.has_section("profile"):
			for k in cfg.get_section_keys("profile"):
				_values["profile." + k] = cfg.get_value("profile", k)


static func value(id: String) -> Variant:
	ensure_loaded()
	return _values.get(id, ROWS[id].def if ROWS.has(id) else null)


static func f(id: String) -> float:
	return float(value(id))


static func b(id: String) -> bool:
	return bool(value(id))


static func s(id: String) -> String:
	return str(value(id))


static func set_value(id: String, v: Variant) -> void:
	ensure_loaded()
	var r: Dictionary = ROWS.get(id, {})
	if r.get("type", "") == "slider":
		v = clampf(snappedf(float(v), float(r.step)), float(r.min), float(r.max))
	if _values.get(id) == v:
		return
	_values[id] = v
	# The quality preset sets the graphics rows; changing one of them makes it Custom.
	if id == "preset" and v != "Custom":
		for g in ["shadows", "foliage", "view_distance"]:
			_values[g] = v
	elif r.get("group", "") == "gfx":
		_values["preset"] = "Custom"
	save()
	apply(id)


static func reset_category(cat_id: String) -> void:
	ensure_loaded()
	for id: String in ROWS:
		var r: Dictionary = ROWS[id]
		if r.cat != cat_id:
			continue
		if r.type == "bind":
			_values.erase(id)
		else:
			_values[id] = r.def
	if cat_id == "mk":
		_apply_bindings()
	save()
	apply("")


## Callables run with the changed setting id ("" for many at once).
static func listen(callable: Callable) -> void:
	if not _listeners.has(callable):
		_listeners.append(callable)


static func unlisten(callable: Callable) -> void:
	_listeners.erase(callable)


static func save() -> void:
	if not use_saved:
		return
	var cfg := ConfigFile.new()
	for id: String in _values:
		if id.begins_with("bind."):
			cfg.set_value("bindings", id.substr(5), _values[id])
		elif id.begins_with("profile."):
			cfg.set_value("profile", id.substr(8), _values[id])
		else:
			cfg.set_value("settings", id, _values[id])
	save_ok = cfg.save(PATH) == OK


# ---------------------------------------------------------------- profile

static func callsign() -> String:
	ensure_loaded()
	return str(_values.get("profile.callsign", "NOMAD-7"))


static func set_callsign(name: String) -> void:
	ensure_loaded()
	_values["profile.callsign"] = name.strip_edges().to_upper().left(16)
	save()


static func profile(key: String, default: Variant) -> Variant:
	ensure_loaded()
	return _values.get("profile." + key, default)


static func set_profile(key: String, v: Variant) -> void:
	ensure_loaded()
	_values["profile." + key] = v
	save()


# ---------------------------------------------------------------- bindings

## Keyboard/mouse events bound to an action, primary first (at most two).
static func binding_events(action: String) -> Array[InputEvent]:
	var out: Array[InputEvent] = []
	if not InputMap.has_action(action):
		return out
	for e in InputMap.action_get_events(action):
		if e is InputEventKey or e is InputEventMouseButton:
			out.append(e)
	return out


## Bind `event` as the primary (slot 0) or alternate (slot 1) for `action`.
## A key already used by another action is taken from it. Returns the label of
## the action that lost it, or "".
static func rebind(action: String, slot: int, event: InputEvent) -> String:
	ensure_loaded()
	var took_from := ""
	if event:
		for other: Array in BINDABLE:
			if other[0] == action:
				continue
			for e in binding_events(other[0]):
				if _same(e, event):
					InputMap.action_erase_event(other[0], e)
					took_from = other[1]
					_store_binding(other[0])
	var current := binding_events(action)
	var keep: Array[InputEvent] = []
	for i in 2:
		if i == slot:
			if event:
				keep.append(event)
		elif i < current.size():
			keep.append(current[i])
	for e in current:
		InputMap.action_erase_event(action, e)
	for e in keep:
		InputMap.action_add_event(action, e)
	_store_binding(action)
	save()
	apply("bindings")
	return took_from


static func _same(a: InputEvent, b2: InputEvent) -> bool:
	if a is InputEventKey and b2 is InputEventKey:
		return (a as InputEventKey).physical_keycode == (b2 as InputEventKey).physical_keycode
	if a is InputEventMouseButton and b2 is InputEventMouseButton:
		return (a as InputEventMouseButton).button_index == (b2 as InputEventMouseButton).button_index
	return false


static func _store_binding(action: String) -> void:
	var codes: Array = []
	for e in binding_events(action):
		codes.append(event_code(e))
	_values["bind." + action] = codes


## "k:87" for a physical key, "m:1" for a mouse button.
static func event_code(e: InputEvent) -> String:
	if e is InputEventKey:
		return "k:%d" % (e as InputEventKey).physical_keycode
	if e is InputEventMouseButton:
		return "m:%d" % (e as InputEventMouseButton).button_index
	return ""


static func event_from_code(code: String) -> InputEvent:
	var parts := code.split(":")
	if parts.size() != 2:
		return null
	if parts[0] == "k":
		var k := InputEventKey.new()
		k.physical_keycode = int(parts[1]) as Key
		return k
	if parts[0] == "m":
		var m := InputEventMouseButton.new()
		m.button_index = int(parts[1]) as MouseButton
		return m
	return null


## Short name of a key or button for keycaps: "W", "SHIFT", "LMB", "WHEEL ↓".
static func event_label(e: InputEvent) -> String:
	if e is InputEventKey:
		var code := (e as InputEventKey).physical_keycode
		match code:
			KEY_SPACE: return "Space"
			KEY_ESCAPE: return "Esc"
			KEY_CTRL: return "Ctrl"
			KEY_SHIFT: return "Shift"
			KEY_ALT: return "Alt"
			KEY_TAB: return "Tab"
			KEY_ENTER: return "Enter"
			KEY_BACKSPACE: return "Bksp"
			KEY_UP: return "↑"
			KEY_DOWN: return "↓"
			KEY_LEFT: return "←"
			KEY_RIGHT: return "→"
		# Physical keys are named by their US-layout position (W, A, S, D).
		return OS.get_keycode_string(code)
	if e is InputEventMouseButton:
		match (e as InputEventMouseButton).button_index:
			MOUSE_BUTTON_LEFT: return "LMB"
			MOUSE_BUTTON_RIGHT: return "RMB"
			MOUSE_BUTTON_MIDDLE: return "MMB"
			MOUSE_BUTTON_WHEEL_UP: return "Wheel ↑"
			MOUSE_BUTTON_WHEEL_DOWN: return "Wheel ↓"
			MOUSE_BUTTON_XBUTTON1: return "Mouse 4"
			MOUSE_BUTTON_XBUTTON2: return "Mouse 5"
	return "?"


## The primary key label for an action ("E"), for prompts and the guide.
static func key_for(action: String) -> String:
	var ev := binding_events(action)
	return event_label(ev[0]) if ev.size() > 0 else "—"


static func _apply_bindings() -> void:
	for b2: Array in BINDABLE:
		var action: String = b2[0]
		if not InputMap.has_action(action):
			continue
		if not _default_binds.has(action):
			_default_binds[action] = binding_events(action)
		var saved: Variant = _values.get("bind." + action)
		var events: Array[InputEvent] = []
		if saved is Array:
			for code: String in saved:
				var e := event_from_code(code)
				if e:
					events.append(e)
		else:
			events = _default_binds[action]
		for e in binding_events(action):
			InputMap.action_erase_event(action, e)
		for e in events:
			InputMap.action_add_event(action, e)


# ---------------------------------------------------------------- applying

## Apply engine-wide settings. Call once at startup (after the default input
## bindings exist); set_value() calls it again for each change.
static func apply(id := "") -> void:
	ensure_loaded()
	var all := id == ""
	if all or id == "bindings":
		_apply_bindings()
	if all or id.begins_with("vol_"):
		_apply_audio()
	if all or id == "fps_limit":
		var lim := s("fps_limit")
		Engine.max_fps = 0 if lim == "Unlimited" else int(lim)
	if all or id in ["dz_left", "dz_right", "swap_sticks"]:
		_apply_deadzones()
	if (all or id == "window_mode") and not Engine.is_embedded_in_editor():
		var want_full := s("window_mode") == "Fullscreen"
		var is_full := DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
		if want_full != is_full and not (all and OS.has_feature("web")):
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if want_full else DisplayServer.WINDOW_MODE_WINDOWED)
	var tree := Engine.get_main_loop() as SceneTree
	if tree and tree.root:
		if all or id in ["res3d", "aa", "preset"]:
			apply_viewport(tree.root)
	for l in _listeners.duplicate():
		if l.is_valid():
			l.call(id)
		else:
			_listeners.erase(l)


static func apply_viewport(vp: Viewport) -> void:
	vp.scaling_3d_scale = f("res3d") / 100.0
	var aa := s("aa")
	vp.msaa_3d = {"MSAA 2x": Viewport.MSAA_2X, "MSAA 4x": Viewport.MSAA_4X}.get(aa, Viewport.MSAA_DISABLED)


const BUSES := {"Effects": "vol_effects", "Ambience": "vol_ambience", "Music": "vol_music", "UI": "vol_ui"}


## Creates the mixer buses the first time, then sets their volumes.
static func _apply_audio() -> void:
	for bus: String in BUSES:
		if AudioServer.get_bus_index(bus) < 0:
			AudioServer.add_bus()
			var i := AudioServer.bus_count - 1
			AudioServer.set_bus_name(i, bus)
			AudioServer.set_bus_send(i, "Master")
	_set_bus("Master", f("vol_master"))
	for bus: String in BUSES:
		_set_bus(bus, f(BUSES[bus]))


static func _set_bus(bus: String, percent: float) -> void:
	var i := AudioServer.get_bus_index(bus)
	if i < 0:
		return
	AudioServer.set_bus_mute(i, percent <= 0.0)
	AudioServer.set_bus_volume_db(i, linear_to_db(maxf(percent, 0.01) / 100.0))


static func _apply_deadzones() -> void:
	var swap := b("swap_sticks")
	var move_dz := f("dz_right" if swap else "dz_left") / 100.0
	var look_dz := f("dz_left" if swap else "dz_right") / 100.0
	for a in ["move_forward", "move_back", "move_left", "move_right"]:
		if InputMap.has_action(a):
			InputMap.action_set_deadzone(a, maxf(move_dz, 0.01))
	for a in ["look_left", "look_right", "look_up", "look_down"]:
		if InputMap.has_action(a):
			InputMap.action_set_deadzone(a, maxf(look_dz, 0.01))
	# Swap sticks: move on the right stick, look on the left.
	var axes := {
		"move_forward": [JOY_AXIS_LEFT_Y, -1.0], "move_back": [JOY_AXIS_LEFT_Y, 1.0],
		"move_left": [JOY_AXIS_LEFT_X, -1.0], "move_right": [JOY_AXIS_LEFT_X, 1.0],
		"look_left": [JOY_AXIS_RIGHT_X, -1.0], "look_right": [JOY_AXIS_RIGHT_X, 1.0],
		"look_up": [JOY_AXIS_RIGHT_Y, -1.0], "look_down": [JOY_AXIS_RIGHT_Y, 1.0],
	}
	for a: String in axes:
		if not InputMap.has_action(a):
			continue
		for e in InputMap.action_get_events(a):
			if e is InputEventJoypadMotion:
				InputMap.action_erase_event(a, e)
		var m := InputEventJoypadMotion.new()
		var axis: int = axes[a][0]
		if swap:
			axis = {JOY_AXIS_LEFT_X: JOY_AXIS_RIGHT_X, JOY_AXIS_LEFT_Y: JOY_AXIS_RIGHT_Y, JOY_AXIS_RIGHT_X: JOY_AXIS_LEFT_X, JOY_AXIS_RIGHT_Y: JOY_AXIS_LEFT_Y}[axis]
		m.axis = axis as JoyAxis
		m.axis_value = axes[a][1]
		InputMap.action_add_event(a, m)


## Horizontal field of view in the settings, as the vertical FOV Godot's
## camera uses at the current aspect ratio.
static func vertical_fov(aspect: float) -> float:
	var h := deg_to_rad(f("fov"))
	return rad_to_deg(2.0 * atan(tan(h * 0.5) / maxf(aspect, 0.1)))


## Stick input shaped by the response curve setting.
static func shape_stick(v: Vector2) -> Vector2:
	var l := v.length()
	if l <= 0.0:
		return v
	var shaped: float
	match s("curve"):
		"Linear":
			shaped = l
		"Dynamic":
			shaped = pow(l, 3.0)
		_:
			shaped = l * l
	return v / l * shaped
