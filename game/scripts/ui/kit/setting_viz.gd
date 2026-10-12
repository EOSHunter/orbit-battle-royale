class_name SettingViz
extends Control
## The picture under a setting's explanation: a mouse with its speed, the FOV
## cone, the stick response curve, a live deadzone circle, volume meter, the
## graphics preset bars, a HUD preview at the chosen scale, or the bound key.

var _row: Dictionary = {}
var _font: Font
var _mono: Font


func _ready() -> void:
	_font = UIStyle.tracked_font(15, 0.16)
	_mono = UIStyle.font("mono")
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func show_row(row: Dictionary) -> void:
	_row = row
	queue_redraw()


func _process(_delta: float) -> void:
	# Redraw continuously: values change with the row, and the deadzone view is live.
	if not _row.is_empty() and is_visible_in_tree():
		queue_redraw()


func _draw() -> void:
	if _row.is_empty():
		return
	match _row.get("viz", ""):
		"mouse":
			_draw_mouse()
		"fov":
			_draw_fov()
		"curve":
			_draw_curve()
		"deadzone":
			_draw_deadzone()
		"volume":
			_draw_volume()
		"preset":
			_draw_preset()
		"hud":
			_draw_hud()
		"key":
			_draw_key()


func _caption(text: String, at: Vector2, color := UIStyle.TEXT_2, size := 15) -> void:
	draw_string(_font, at, text.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)


func _draw_mouse() -> void:
	var c := Vector2(110, 110)
	var v := GameSettings.f(_row.id)
	# Mouse body.
	var body := PackedVector2Array()
	for i in 33:
		var a := TAU * i / 32.0
		body.append(c + Vector2(cos(a) * 24, sin(a) * 38))
	draw_polyline(body, UIStyle.TEXT, 2.0, true)
	draw_line(c + Vector2(0, -38), c + Vector2(0, -8), UIStyle.TEXT, 2.0)
	draw_rect(Rect2(c + Vector2(-3, -26), Vector2(6, 11)), UIStyle.TEXT, false, 1.5)
	# Speed arcs: wider with higher sensitivity.
	var spread := clampf(v / 3.0, 0.08, 1.0) * 1.3
	draw_arc(c, 62, -PI / 2 - spread, -PI / 2 + spread, 32, UIStyle.ACCENT, 2.0, true)
	draw_arc(c, 62, -PI / 2 - 1.3, -PI / 2 + 1.3, 32, Color(1, 1, 1, 0.12), 1.0, true)
	for side in [-1.0, 1.0]:
		var a: float = -PI / 2 + spread * side
		draw_circle(c + Vector2(cos(a), sin(a)) * 62, 3.0, UIStyle.ACCENT)
	var tag := "Standard" if absf(v - float(_row.def)) < 0.001 else ("Faster" if v > float(_row.def) else "Slower")
	_caption("%s  ·  %s" % [SettingRow.format_value(_row, v), tag], Vector2(54, 200))


func _draw_fov() -> void:
	var fov := deg_to_rad(GameSettings.f("fov"))
	var o := Vector2(150, 200)
	var r := 150.0
	var pts := PackedVector2Array([o])
	for i in 25:
		var a := -PI / 2 - fov / 2 + fov * i / 24.0
		pts.append(o + Vector2(cos(a), sin(a)) * r)
	pts.append(o)
	draw_colored_polygon(pts, Color(UIStyle.ACCENT, 0.12))
	draw_polyline(pts, UIStyle.ACCENT, 2.0, true)
	# Dashed 90° reference.
	for side in [-1.0, 1.0]:
		var a: float = -PI / 2 + side * PI / 4
		var d := Vector2(cos(a), sin(a))
		var t := 0.0
		while t < r:
			draw_line(o + d * t, o + d * minf(t + 7.0, r), Color(1, 1, 1, 0.45), 1.0)
			t += 13.0
	draw_circle(o, 4.0, UIStyle.TEXT)
	_caption("%d° horizontal  ·  dashed 90°" % roundi(GameSettings.f("fov")), Vector2(58, 232))


func _draw_curve() -> void:
	var box := Rect2(20, 10, 210, 170)
	draw_line(box.position + Vector2(0, box.size.y), box.end, Color(1, 1, 1, 0.3), 1.0)
	draw_line(box.position, box.position + Vector2(0, box.size.y), Color(1, 1, 1, 0.3), 1.0)
	var pts := PackedVector2Array()
	for i in 41:
		var x := i / 40.0
		var y := GameSettings.shape_stick(Vector2(x, 0)).x
		pts.append(box.position + Vector2(x * box.size.x, (1.0 - y) * box.size.y))
	draw_polyline(pts, UIStyle.ACCENT, 2.5, true)
	_caption("Stick input  →  turn speed", Vector2(20, 206))


func _draw_deadzone() -> void:
	var c := Vector2(110, 100)
	var r := 80.0
	var dz := GameSettings.f(_row.id) / 100.0
	draw_arc(c, r, 0, TAU, 64, UIStyle.TEXT, 2.0, true)
	draw_circle(c, r * dz, Color(UIStyle.ACCENT, 0.18))
	draw_arc(c, r * dz, 0, TAU, 48, Color(UIStyle.ACCENT, 0.8), 1.5, true)
	var left: bool = _row.id == "dz_left"
	var stick := Vector2(Input.get_joy_axis(0, JOY_AXIS_LEFT_X if left else JOY_AXIS_RIGHT_X), Input.get_joy_axis(0, JOY_AXIS_LEFT_Y if left else JOY_AXIS_RIGHT_Y))
	draw_circle(c + stick * r, 6.0, UIStyle.TEXT if stick.length() > dz else UIStyle.TEXT_3)
	var pads := Input.get_connected_joypads()
	_caption("Shaded area is ignored" if pads.size() > 0 else "Connect a controller to test drift", Vector2(20, 214))


func _draw_volume() -> void:
	var v := GameSettings.f(_row.id) / 100.0
	for i in 20:
		var on := i < roundi(v * 20.0)
		var h := 20.0 + i * 5.0
		draw_rect(Rect2(20 + i * 14, 140 - h, 9, h), UIStyle.ACCENT if on else Color(1, 1, 1, 0.12))
	_caption("%d%%" % roundi(v * 100.0), Vector2(20, 172), UIStyle.TEXT, 18)


func _draw_preset() -> void:
	var rows := [["Shadows", "shadows"], ["Foliage density", "foliage"], ["View distance", "view_distance"], ["Anti-aliasing", "aa"]]
	var y := 16.0
	for r: Array in rows:
		var v := GameSettings.s(r[1])
		var level := ["Low", "Medium", "High", "Ultra"].find(v) + 1
		if r[1] == "aa":
			level = ["Off", "MSAA 2x", "MSAA 4x"].find(v) * 2
		_caption(r[0], Vector2(0, y + 4), UIStyle.TEXT_2, 14)
		for i in 4:
			draw_rect(Rect2(150 + i * 34, y - 6, 28, 5), UIStyle.ACCENT if i < level else Color(1, 1, 1, 0.12))
		y += 30.0
	_caption("Preset: %s" % GameSettings.s("preset"), Vector2(0, y + 10), UIStyle.TEXT_3, 14)


func _draw_hud() -> void:
	var panel := Rect2(0, 0, 380, 190)
	draw_rect(panel, Color(0, 0, 0, 0.3))
	draw_rect(panel, Color(1, 1, 1, 0.1), false, 1.0)
	_caption("Preview", Vector2(16, 24), UIStyle.TEXT_3, 14)
	var k := GameSettings.f("hud_scale") / 100.0
	var o := Vector2(20, 50)
	draw_circle(o + Vector2(6, 8) * k, 5 * k, UIStyle.HEALTH)
	draw_rect(Rect2(o + Vector2(18, 5) * k, Vector2(150, 6) * k), UIStyle.HEALTH)
	draw_string(_mono, o + Vector2(178, 13) * k, "100", HORIZONTAL_ALIGNMENT_LEFT, -1, int(16 * k), UIStyle.TEXT)
	draw_circle(o + Vector2(6, 32) * k, 5 * k, UIStyle.SHIELD)
	draw_rect(Rect2(o + Vector2(18, 29) * k, Vector2(150, 6) * k), Color(1, 1, 1, 0.12))
	draw_string(_mono, o + Vector2(178, 37) * k, "0", HORIZONTAL_ALIGNMENT_LEFT, -1, int(16 * k), UIStyle.TEXT)
	for i in 5:
		var at := o + Vector2(i * 34, 56) * k
		draw_rect(Rect2(at, Vector2(26, 26) * k), Color(1, 1, 1, 0.08 if i > 1 else 0.18))
		if i == 0:
			draw_rect(Rect2(at + Vector2(0, 28) * k, Vector2(26, 2) * k), UIStyle.ACCENT)
	if GameSettings.b("damage_direction"):
		draw_arc(Vector2(300, 95), 34, -2.2, -1.2, 16, UIStyle.DANGER, 4.0, true)
	draw_string(_font, Vector2(20, 175), "The storm closes in 30 seconds. Move to the safe zone.", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, UIStyle.TEXT_2)


func _draw_key() -> void:
	var events := GameSettings.binding_events(_row.get("action", ""))
	var x := 0.0
	for i in events.size():
		var t := GameSettings.event_label(events[i]).to_upper()
		var w := maxf(56.0, t.length() * 16.0 + 28.0)
		var r := Rect2(x, 20, w, 56)
		draw_rect(r, Color(0, 0, 0, 0.35))
		draw_rect(r, UIStyle.TEXT, false, 2.0)
		draw_string(_mono, Vector2(x, 58), t, HORIZONTAL_ALIGNMENT_CENTER, w, 20, UIStyle.TEXT)
		_caption("Primary" if i == 0 else "Alternate", Vector2(x, 100), UIStyle.TEXT_3, 14)
		x += w + 18.0
	if events.is_empty():
		_caption("Unbound", Vector2(0, 50), UIStyle.WARNING, 16)
