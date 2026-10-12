class_name RingfallGen
extends RefCounted
## Shapes the Ringfall island (codex/concepts/v0.2/47-ringfall-map.png): an
## island in a turquoise sea, a crater lake with an island at its center where
## the ring fragment struck, a volcanic ridge to the north (The Spine) and
## location pads around the rim. World axes: x east, z south, y up, meters.
## Used only at build time by tools/build_ringfall.gd.

const SIZE := 513
const SPACING := 2.0
const HALF := 512.0
const SEA := 0.0

## Location pads: center (x, z), flat radius, blend width, height.
const LOCATIONS := {
	"glass-basin": {"at": Vector2(10, -5), "r": 34.0, "blend": 22.0, "h": 6.0},
	"crown-observatory": {"at": Vector2(-315, -255), "r": 40.0, "blend": 55.0, "h": 46.0},
	"the-spine": {"at": Vector2(115, -318), "r": 0.0, "blend": 0.0, "h": 0.0},
	"relay-nine": {"at": Vector2(285, -215), "r": 58.0, "blend": 45.0, "h": 15.0},
	"bloomwild": {"at": Vector2(-320, 70), "r": 0.0, "blend": 0.0, "h": 0.0},
	"anchorport": {"at": Vector2(15, 352), "r": 60.0, "blend": 40.0, "h": 3.0},
	"hollow-array": {"at": Vector2(278, 228), "r": 0.0, "blend": 0.0, "h": 0.0},
}
const CRATER_R := 150.0
## The Spine: ridge polyline and the gap the ancient bridge spans.
const RIDGE := [Vector2(-170, -300), Vector2(-40, -360), Vector2(110, -330), Vector2(235, -290)]
const SPINE_GAP := Vector2(115, -322)
## Hollow Array canyon, south-west to north-east through the red plateau.
const CANYON := [Vector2(190, 330), Vector2(275, 228), Vector2(370, 130)]
## Bloomwild streams, inland to the western sea.
const STREAMS := [
	[Vector2(-230, 10), Vector2(-300, 45), Vector2(-370, 40), Vector2(-470, 70)],
	[Vector2(-260, 150), Vector2(-330, 170), Vector2(-400, 230), Vector2(-470, 260)],
]

var _coast := FastNoiseLite.new()
var _detail := FastNoiseLite.new()
var _hills := FastNoiseLite.new()


func _init() -> void:
	_coast.seed = 7
	_coast.frequency = 0.004
	_coast.fractal_octaves = 3
	_detail.seed = 11
	_detail.frequency = 0.02
	_detail.fractal_octaves = 4
	_hills.seed = 23
	_hills.frequency = 0.006
	_hills.fractal_octaves = 3


static func _gauss(d: float, w: float) -> float:
	return exp(-(d * d) / (w * w))


static func _seg_dist(p: Vector2, a: Vector2, b: Vector2) -> float:
	var ab := b - a
	var t := clampf((p - a).dot(ab) / maxf(ab.length_squared(), 0.0001), 0.0, 1.0)
	return p.distance_to(a + ab * t)


static func _line_dist(p: Vector2, pts: Array) -> float:
	var d := INF
	for i in pts.size() - 1:
		d = minf(d, _seg_dist(p, pts[i], pts[i + 1]))
	return d


## Island mask: 1 on land, 0 out at sea.
func land(x: float, z: float) -> float:
	var p := Vector2(x, z)
	var r := p.length()
	var coast := 405.0 + 65.0 * _coast.get_noise_2d(x, z) + 25.0 * _coast.get_noise_2d(x * 3.0, z * 3.0)
	return smoothstep(coast + 45.0, coast - 35.0, r)


func height(x: float, z: float) -> float:
	var p := Vector2(x, z)
	var r := p.length()
	var l := land(x, z)
	var detail := _detail.get_noise_2d(x, z)
	var h := lerpf(-24.0 + 4.0 * detail, 6.0 + 4.0 * detail + 9.0 * maxf(0.0, _hills.get_noise_2d(x, z)), l)

	# Crater rim and bowl (Glass Basin): a steep inner cliff, gentler outside.
	var cr := CRATER_R + 14.0 * _coast.get_noise_2d(x * 2.0 + 300.0, z * 2.0)
	h += 26.0 * _gauss(r - (cr + 18.0), 34.0) * l
	h = lerpf(h, -11.0 + 3.0 * detail, smoothstep(cr + 4.0, cr - 32.0, r))

	# The Spine: volcanic ridge across the north, peak in the middle, a gap for the bridge.
	var dr := _line_dist(p, RIDGE)
	h += 52.0 * _gauss(dr, 48.0) * (0.75 + 0.25 * detail)
	h += 40.0 * _gauss(p.distance_to(Vector2(-40, -365)), 70.0)
	var gap := absf(p.x - SPINE_GAP.x + (p.y - SPINE_GAP.y) * 0.25)
	h -= 48.0 * _gauss(gap, 16.0) * _gauss(dr, 60.0)

	# Crown Observatory hill.
	h += 34.0 * _gauss(p.distance_to(LOCATIONS["crown-observatory"].at), 115.0)

	# Hollow Array: a red plateau with a canyon cut through it.
	var ha: Vector2 = Vector2(278, 228)
	var plateau := smoothstep(170.0, 115.0, p.distance_to(ha) + 30.0 * _hills.get_noise_2d(x * 2.5, z * 2.5)) * l
	h = lerpf(h, 30.0 + 3.0 * detail, plateau * 0.9)
	var canyon := smoothstep(26.0, 12.0, _line_dist(p, CANYON)) * plateau
	h = lerpf(h, 7.0 + 1.5 * detail, canyon)

	# Bloomwild: low forest floor with streams running to the western sea.
	var bw := smoothstep(180.0, 90.0, p.distance_to(Vector2(-320, 90))) * l
	h = lerpf(h, 4.5 + 2.5 * detail, bw * 0.8)
	for s in STREAMS:
		var ds := _line_dist(p + 14.0 * Vector2(_detail.get_noise_2d(x * 0.6, z * 0.6), _detail.get_noise_2d(x * 0.6 + 90.0, z * 0.6)), s)
		h = lerpf(h, -1.4, smoothstep(9.0, 3.5, ds) * l)

	# Flat pads where locations are built.
	for key in LOCATIONS:
		var loc: Dictionary = LOCATIONS[key]
		if loc.r <= 0.0:
			continue
		# Ragged edges so pads read as ground, not discs.
		var d := p.distance_to(loc.at) + 16.0 * _hills.get_noise_2d(x * 3.0, z * 3.0)
		var t := smoothstep(loc.r + loc.blend, loc.r, d)
		h = lerpf(h, loc.h + 0.3 * detail, t)
	# Anchorport sits right on the coast: keep the sea south of the pad.
	return h


## Ground type weights (grass, rock, sand, glass) for a sample, from height, slope and region.
## Only grass, rock and sand are stored; the shader derives glass from what is left.
func splat(x: float, z: float, h: float, slope: float) -> Color:
	var p := Vector2(x, z)
	var r := p.length()
	var rock := smoothstep(0.55, 0.9, slope) + smoothstep(40.0, 60.0, h)
	var sand := smoothstep(3.0, 0.8, h) * (1.0 - smoothstep(0.4, 0.7, slope))
	var glass := 0.0
	if r < CRATER_R + 20.0:
		glass = smoothstep(4.5, -1.0, h) * 1.2 + 0.3 * smoothstep(0.35, 0.6, slope)
	# Relay Nine's grey ash plain reads as rock.
	rock += 0.6 * smoothstep(150.0, 90.0, p.distance_to(Vector2(285, -215)))
	var grass := maxf(0.0, 1.0 - rock - sand - glass)
	var c := Color(grass, minf(rock, 1.0), sand, minf(glass, 1.0))
	var total := c.r + c.g + c.b + c.a
	return Color(c.r / total, c.g / total, c.b / total, c.a / total)


## The whole grid: heights, then splat from heights and slopes.
func generate() -> Dictionary:
	var heights := PackedFloat32Array()
	heights.resize(SIZE * SIZE)
	for iz in SIZE:
		for ix in SIZE:
			heights[iz * SIZE + ix] = height(ix * SPACING - HALF, iz * SPACING - HALF)
	var splats := Image.create(SIZE, SIZE, false, Image.FORMAT_RGB8)
	for iz in SIZE:
		for ix in SIZE:
			var h := heights[iz * SIZE + ix]
			var hx := heights[iz * SIZE + mini(ix + 1, SIZE - 1)] - heights[iz * SIZE + maxi(ix - 1, 0)]
			var hz := heights[mini(iz + 1, SIZE - 1) * SIZE + ix] - heights[maxi(iz - 1, 0) * SIZE + ix]
			var slope := Vector2(hx, hz).length() / (2.0 * SPACING)
			var w := splat(ix * SPACING - HALF, iz * SPACING - HALF, h, slope)
			splats.set_pixel(ix, iz, Color(w.r, w.g, w.b))  # glass = 1 - r - g - b
	return {"heights": heights, "splat": splats}
