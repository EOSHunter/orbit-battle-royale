class_name Glyph
extends Control
## Small line icons drawn in code (the UI fonts have no symbol glyphs):
## "dot", "check", "target", "book", "pencil", "spinner".

var kind := "dot"
var color := UIStyle.TEXT:
	set(v):
		color = v
		queue_redraw()
var _t := 0.0


func _init(p_kind := "dot", p_color := UIStyle.TEXT, p_size := 14.0) -> void:
	kind = p_kind
	color = p_color
	custom_minimum_size = Vector2(p_size, p_size)
	size_flags_vertical = Control.SIZE_SHRINK_CENTER
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_process(kind == "spinner")


func _process(delta: float) -> void:
	_t += delta
	queue_redraw()


func _draw() -> void:
	var s := minf(size.x, size.y)
	var c := size * 0.5
	var w := maxf(1.5, s * 0.11)
	match kind:
		"dot":
			draw_circle(c, s * 0.5, color)
		"check":
			draw_polyline(PackedVector2Array([c + Vector2(-0.36, 0.02) * s, c + Vector2(-0.1, 0.28) * s, c + Vector2(0.38, -0.26) * s]), color, w, true)
		"target":
			draw_arc(c, s * 0.32, 0, TAU, 24, color, w, true)
			for d: Vector2 in [Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT]:
				draw_line(c + d * s * 0.2, c + d * s * 0.5, color, w)
		"book":
			draw_rect(Rect2(c + Vector2(-0.45, -0.32) * s, Vector2(0.42, 0.64) * s), color, false, w)
			draw_rect(Rect2(c + Vector2(0.03, -0.32) * s, Vector2(0.42, 0.64) * s), color, false, w)
		"pencil":
			draw_line(c + Vector2(-0.36, 0.36) * s, c + Vector2(0.3, -0.3) * s, color, w * 1.6)
			draw_line(c + Vector2(-0.44, 0.44) * s, c + Vector2(-0.36, 0.36) * s, color, w)
		"spinner":
			draw_arc(c, s * 0.36, _t * 6.0, _t * 6.0 + 4.2, 20, color, w * 1.2, true)
		"shield", "shield_break":
			draw_shield(self, Vector2.ZERO, s, color, kind == "shield_break")


## The shield from the hit-number icons (a 24-unit path), filled in `color`;
## the broken one has a dark crack down the middle.
static func draw_shield(ci: CanvasItem, at: Vector2, s: float, color: Color, cracked: bool) -> void:
	var k := s / 24.0
	var pts := PackedVector2Array([Vector2(12, 2), Vector2(20, 5), Vector2(20, 11)])
	_cubic(pts, Vector2(20, 11), Vector2(20, 16.2), Vector2(16.6, 20.4), Vector2(12, 22))
	_cubic(pts, Vector2(12, 22), Vector2(7.4, 20.4), Vector2(4, 16.2), Vector2(4, 11))
	pts.append(Vector2(4, 5))
	for i in pts.size():
		pts[i] = at + pts[i] * k
	ci.draw_colored_polygon(pts, color)
	if cracked:
		var crack := PackedVector2Array([Vector2(12.5, 3.5), Vector2(10.5, 8.5), Vector2(13.5, 11), Vector2(10, 15), Vector2(12, 17.5), Vector2(10.5, 21)])
		for i in crack.size():
			crack[i] = at + crack[i] * k
		ci.draw_polyline(crack, UIStyle.BG, 2.0 * k, true)


static func _cubic(out: PackedVector2Array, p0: Vector2, p1: Vector2, p2: Vector2, p3: Vector2) -> void:
	for i in range(1, 9):
		var t := i / 8.0
		out.append(p0.bezier_interpolate(p1, p2, p3, t))
