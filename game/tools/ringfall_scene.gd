extends RefCounted
## Assembles scenes/ringfall.tscn: sky and light, terrain and water, the seven
## locations built from the kits, scattered vegetation and rocks, and the
## gameplay nodes (player, HUD, loot, bots, storm). Run through
## tools/build_ringfall.gd -- scene. Layouts are data in this file so the map
## can be rebuilt and tuned; everything snaps to the baked terrain heights.

const DIR := "res://maps/ringfall"
const M := "res://assets/models/"
const COL := M + "colony-kit/"
const PROP := M + "props/"
const RUIN := M + "ruins-kit/"
const VEG := M + "vegetation/"
const TER := M + "terrain-kit/"
const LOC := M + "locations/"
const PICK := M + "pickups/"
const CELL := 64.0

var _root: Node3D
var _data: TerrainData
var _markers: Node3D
var _rng := RandomNumberGenerator.new()
var _parts_cache := {}
## Location centers keep scatter out of built-up areas: [center, radius].
var _keep_clear: Array = []


func build() -> void:
	_rng.seed = 4242
	_data = load(DIR + "/terrain.res")
	_root = Node3D.new()
	_root.name = "Ringfall"
	_root.set_script(load("res://scripts/arena.gd"))
	_root.set("kill_height", -40.0)
	_root.set("bot_count", 8)
	_environment()
	_terrain()
	_markers = _node(_root, "Markers")
	for g in ["PlayerSpawn", "BotSpawns", "LootSpots", "Cover"]:
		if g != "PlayerSpawn":
			_node(_markers, g)
	_anchorport()
	_relay_nine()
	_crown_observatory()
	_glass_basin()
	_the_spine()
	_hollow_array()
	_bloomwild()
	_scatter_all()
	_gameplay()
	var scene := PackedScene.new()
	var err := scene.pack(_root)
	if err == OK:
		err = ResourceSaver.save(scene, "res://scenes/ringfall.tscn")
	print("res://scenes/ringfall.tscn: ", "saved" if err == OK else "FAILED (%d)" % err)
	_root.free()


# ------------------------------------------------------------------ helpers

func _add(parent: Node, child: Node, n := "") -> Node:
	if n != "":
		child.name = n
	parent.add_child(child, true)
	child.owner = _root
	return child


func _node(parent: Node, n: String) -> Node3D:
	return _add(parent, Node3D.new(), n) as Node3D


func _ground(x: float, z: float) -> float:
	return _data.height_at(x, z)


## A location root at a world point, standing on the ground there (or at y).
func _location(n: String, x: float, z: float, keep_clear: float, y := NAN) -> Node3D:
	var loc := Node3D.new()
	loc.set_script(load("res://scripts/world/auto_collide.gd"))
	_add(_root, loc, n)
	loc.position = Vector3(x, _ground(x, z) if is_nan(y) else y, z)
	_keep_clear.append([Vector2(x, z), keep_clear])
	return loc


## Place a model in a location at local (lx, lz). snap puts it on the terrain.
func _put(loc: Node3D, path: String, lx: float, lz: float, yaw := 0.0, snap := true, dy := 0.0, scl := Vector3.ONE, tilt := Vector2.ZERO) -> Node3D:
	var node := (load(path) as PackedScene).instantiate() as Node3D
	var y := (_ground(loc.position.x + lx, loc.position.z + lz) - loc.position.y) if snap else 0.0
	node.position = Vector3(lx, y + dy, lz)
	node.rotation_degrees = Vector3(tilt.x, yaw, tilt.y)
	node.scale = scl
	_add(loc, node)
	return node


func _mark(group: String, world: Vector3, lift := 0.3) -> void:
	var m := Marker3D.new()
	var g: Node = _markers.get_node(group) if group != "PlayerSpawn" else _markers
	_add(g, m, group.trim_suffix("s") if group != "PlayerSpawn" else "PlayerSpawn")
	m.position = world + Vector3.UP * lift


## Marker at a location's local point, on the ground unless y is given.
func _mark_at(group: String, loc: Node3D, lx: float, lz: float, ly := NAN) -> void:
	var wx := loc.position.x + lx
	var wz := loc.position.z + lz
	var y := _ground(wx, wz) if is_nan(ly) else loc.position.y + ly
	_mark(group, Vector3(wx, y, wz))


## Meshes of a model with their transforms relative to its root (for MultiMesh and sizes).
func _parts(path: String) -> Array:
	if _parts_cache.has(path):
		return _parts_cache[path]
	var inst := (load(path) as PackedScene).instantiate()
	var out: Array = []
	_collect(inst, Transform3D.IDENTITY, out)
	inst.free()
	_parts_cache[path] = out
	return out


func _collect(n: Node, xf: Transform3D, out: Array) -> void:
	for c in n.get_children():
		var n3 := c as Node3D
		if n3 == null:
			continue
		var t := xf * n3.transform
		var mi := c as MeshInstance3D
		if mi and mi.mesh:
			out.append([mi.mesh, t])
		_collect(c, t, out)


func _aabb(path: String) -> AABB:
	var box := AABB()
	var first := true
	for p: Array in _parts(path):
		var b: AABB = (p[1] as Transform3D) * (p[0] as Mesh).get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box


## A closed colony building: w x d modules of 4 m, door module(s) on the +z side.
func _building(loc: Node3D, cx: float, cz: float, w: int, d: int, yaw: float, big_door := false) -> Node3D:
	var b := _node(loc, "Building")
	b.position = Vector3(cx, _ground(loc.position.x + cx, loc.position.z + cz) - loc.position.y, cz)
	b.rotation_degrees.y = yaw
	var hw := w * 2.0
	var hd := d * 2.0
	var i := 0
	while i < w:
		var x := -hw + 2.0 + 4.0 * i
		if big_door and w >= 2 and i == w / 2 - 1:
			_put(b, COL + "colony-warehouse-door.glb", x + 2.0, hd, 0.0, false)
			i += 2
			continue
		var front := COL + ("colony-wall-door.glb" if (not big_door and i == w / 2) else "colony-wall.glb")
		_put(b, front, x, hd, 0.0, false)
		i += 1
	for j in w:
		_put(b, COL + ("colony-wall-window.glb" if j % 2 == 1 else "colony-wall.glb"), -hw + 2.0 + 4.0 * j, -hd, 180.0, false)
	for j in d:
		var z := -hd + 2.0 + 4.0 * j
		_put(b, COL + ("colony-wall-window.glb" if j == d / 2 else "colony-wall.glb"), hw, z, 90.0, false)
		_put(b, COL + "colony-wall.glb", -hw, z, -90.0, false)
	for c in [Vector2(-hw, -hd), Vector2(hw, -hd), Vector2(-hw, hd), Vector2(hw, hd)]:
		_put(b, COL + "colony-corner.glb", c.x, c.y, 0.0, false)
	for ix in w:
		for iz in d:
			_put(b, COL + "colony-roof.glb", -hw + 2.0 + 4.0 * ix, -hd + 2.0 + 4.0 * iz, 0.0, false, 4.0)
			_put(b, COL + "colony-floor.glb", -hw + 2.0 + 4.0 * ix, -hd + 2.0 + 4.0 * iz, 0.0, false, 0.05)
	return b


func _container_stack(loc: Node3D, lx: float, lz: float, yaw: float, high: int) -> void:
	for k in high:
		_put(loc, COL + "colony-cargo-container.glb", lx, lz, yaw + _rng.randf_range(-4, 4), true, k * 2.6)


# --------------------------------------------------------------- locations

func _anchorport() -> void:
	# Coastal cargo port: two warehouses, container yard, cargo pads, a grounded
	# transport and a pier out into the sea.
	var a := _location("Anchorport", 15, 352, 95.0)
	_building(a, -24, -10, 4, 3, 0.0, true)
	_building(a, 24, -18, 3, 3, 90.0)
	for p in [Vector3(-4, 10, 0), Vector3(4, 10, 0), Vector3(-4, 18, 1), Vector3(10, 22, 90), Vector3(-14, 22, 90), Vector3(18, 4, 0)]:
		_container_stack(a, p.x, p.y, p.z, 1 + _rng.randi() % 2)
	_put(a, COL + "colony-cargo-pad.glb", 44, 10)
	_put(a, COL + "colony-cargo-pad.glb", -46, 14)
	_put(a, M + "drop-transport/drop-transport.glb", -52, -38, 32.0, true, 1.5, Vector3.ONE * 0.75, Vector2(4, -3))
	# Pier: deck tiles out over the water, railings and lamps along it.
	# Start the pier just before the shoreline south of the yard and run it out to sea.
	var z := 34.0
	while z < 200.0 and _ground(a.position.x, a.position.z + z) > 0.8:
		z += 2.0
	z = maxf(34.0, z - 10.0)
	var pier_end := z + 76.0
	while z < pier_end:
		for x: float in [-2.0, 2.0]:
			_put(a, COL + "colony-floor.glb", x, z, 0.0, false, 0.3)
		_put(a, COL + "colony-railing.glb", -4.0, z, 90.0, false, 0.3)
		_put(a, COL + "colony-railing.glb", 4.0, z, 90.0, false, 0.3)
		if int(z) % 16 == 2:
			_put(a, PROP + "prop-lamp-post.glb", 3.4, z, 0.0, false, 0.3)
		z += 4.0
	_put(a, COL + "colony-cargo-pad.glb", 0, pier_end + 6.0, 0.0, false, -0.7)
	_mark_at("LootSpots", a, 0, pier_end + 4.0, 0.6)
	for p in [Vector2(-10, -30), Vector2(30, 30), Vector2(-34, 30)]:
		_put(a, COL + "colony-work-light.glb", p.x, p.y, _rng.randf_range(0, 360))
	_put(a, PROP + "prop-vehicle-spawn-pad.glb", 36, -42)
	_put(a, PROP + "prop-vehicle-spawn-pad.glb", 48, -30)
	_put(a, PROP + "prop-generator.glb", 8, -34, 90.0)
	_put(a, PROP + "prop-terminal.glb", -30, 8, 180.0)
	_props_ring(a, Vector2(0, 0), 38.0, 18, [PROP + "prop-crate-small.glb", PROP + "prop-crate-large.glb", PROP + "prop-barrel.glb", PROP + "prop-fuel-canister.glb", PROP + "prop-barrier.glb"])
	for p in [Vector2(-24, -10), Vector2(-30, -14), Vector2(24, -18), Vector2(0, 14), Vector2(10, 26), Vector2(44, 10), Vector2(-46, 14), Vector2(-50, -30), Vector2(30, -40)]:
		_mark_at("LootSpots", a, p.x, p.y)
	for p in [Vector2(-8, 12), Vector2(14, 6), Vector2(-20, 24), Vector2(28, 26)]:
		_mark_at("Cover", a, p.x, p.y)
	_mark("PlayerSpawn", Vector3(a.position.x, _ground(a.position.x, a.position.z + 40) + 0.2, a.position.z + 40))
	_mark_at("BotSpawns", a, -40, -20)


func _relay_nine() -> void:
	# Power station: the core in a square gantry ring with stairs, pipe runs to
	# two maintenance huts, comms masts and a fenced perimeter.
	var r := _location("RelayNine", 285, -215, 70.0)
	_put(r, LOC + "relay-power-core.glb", 0, 0)
	for k in 6:
		var z := -10.0 + 4.0 * k
		_put(r, COL + "colony-gantry.glb", 12, z, 0.0, false)
		_put(r, COL + "colony-gantry.glb", -12, z, 0.0, false)
		_put(r, COL + "colony-gantry.glb", z, 12, 90.0, false)
		_put(r, COL + "colony-gantry.glb", z, -12, 90.0, false)
	_put(r, COL + "colony-stairs.glb", 19, 2, -90.0, false)
	_put(r, COL + "colony-stairs.glb", -19, -2, 90.0, false)
	for side: float in [1.0, -1.0]:
		for k in 4:
			_put(r, COL + "colony-pipe-straight.glb", side * (8.2 + 4.0 * k), 0, 0.0, false)
		_building(r, side * 28.0, 0, 2, 2, 90.0 * side)
	for p in [Vector2(22, 24), Vector2(-24, -26)]:
		_put(r, COL + "colony-comms-mast.glb", p.x, p.y)
	for p in [Vector2(16, -26), Vector2(-14, 24), Vector2(30, -14)]:
		_put(r, PROP + "prop-generator.glb", p.x, p.y, _rng.randf_range(0, 360))
	_put(r, PROP + "prop-terminal.glb", 6, 18, 180.0)
	_put(r, PROP + "prop-cable-reel.glb", -6, 20)
	for p in [Vector2(14, 30), Vector2(-30, 14), Vector2(32, -30)]:
		_put(r, COL + "colony-work-light.glb", p.x, p.y, _rng.randf_range(0, 360))
	_fence_ring(r, 44.0, 36)
	_props_ring(r, Vector2(0, 0), 34.0, 12, [PROP + "prop-barrel.glb", PROP + "prop-crate-small.glb", PROP + "prop-barrier.glb", PROP + "prop-sandbag-wall.glb"])
	for p in [Vector2(28, 0), Vector2(-28, 0), Vector2(6, 6), Vector2(-20, 20), Vector2(20, -20)]:
		_mark_at("LootSpots", r, p.x, p.y)
	for p in [Vector2(12, 0), Vector2(-12, 6), Vector2(4, 12)]:  # up on the gantry ring
		_mark_at("LootSpots", r, p.x, p.y, 4.1)
	for p in [Vector2(10, -20), Vector2(-16, 10), Vector2(24, 12)]:
		_mark_at("Cover", r, p.x, p.y)
	_mark_at("BotSpawns", r, 36, 30)


func _crown_observatory() -> void:
	# Hilltop observatory: three telescope domes, the fractured dish, a habitat
	# and a landing pad, railings along the cliff side.
	var c := _location("CrownObservatory", -315, -255, 60.0)
	_put(c, LOC + "observatory-dome.glb", 0, -12, 160.0)
	_put(c, LOC + "observatory-dome.glb", -24, 12, 200.0, true, 0.0, Vector3.ONE * 0.8)
	_put(c, LOC + "observatory-dome.glb", 22, 14, 130.0, true, 0.0, Vector3.ONE * 0.7)
	_put(c, LOC + "comms-dish.glb", 4, 36, 20.0)
	_put(c, COL + "colony-habitat-module.glb", -32, -22, 30.0)
	_put(c, COL + "colony-cargo-pad.glb", 32, -24)
	_put(c, COL + "colony-comms-mast.glb", -8, 30)
	for k in 6:
		_put(c, COL + "colony-railing.glb", -20 + 4.0 * k, -40, 0.0)
	for p in [Vector2(12, -30), Vector2(-14, -2)]:
		_put(c, COL + "colony-work-light.glb", p.x, p.y, _rng.randf_range(0, 360))
	_props_ring(c, Vector2(0, 0), 30.0, 10, [PROP + "prop-crate-small.glb", PROP + "prop-crate-large.glb", PROP + "prop-terminal.glb", PROP + "prop-cable-reel.glb"])
	for p in [Vector2(0, -2), Vector2(-24, 22), Vector2(22, 22), Vector2(4, 30), Vector2(-32, -14), Vector2(32, -24), Vector2(-6, -30), Vector2(14, 2)]:
		_mark_at("LootSpots", c, p.x, p.y)
	for p in [Vector2(-10, 10), Vector2(10, -20)]:
		_mark_at("Cover", c, p.x, p.y)
	_mark_at("BotSpawns", c, 0, 20)


func _glass_basin() -> void:
	# The impact: a huge ring fragment buried in the crater island, black glass
	# spires around it and a supply crate for whoever dares the crossing.
	var g := _location("GlassBasin", 10, -5, 40.0)
	_put(g, TER + "ring-fragment.glb", 0, 0, 25.0, true, -1.5, Vector3.ONE * 3.0, Vector2(-14, 18))
	for k in 9:
		var a := TAU * k / 9.0 + _rng.randf_range(-0.2, 0.2)
		var d := _rng.randf_range(18.0, 30.0)
		_put(g, TER + ("glass-spire.glb" if k % 2 == 0 else "glass-shard-cluster.glb"), cos(a) * d, sin(a) * d, _rng.randf_range(0, 360), true, -0.5, Vector3.ONE * _rng.randf_range(1.0, 1.8))
	_put(g, PICK + "colony-supply-crate.glb", 8, -10, 40.0)
	_put(g, RUIN + "ruin-rubble.glb", -10, 12, 120.0)
	for p in [Vector2(8, -10), Vector2(-12, -8), Vector2(14, 14), Vector2(-6, 18)]:
		_mark_at("LootSpots", g, p.x, p.y)
	_mark_at("Cover", g, -10, 12)


func _the_spine() -> void:
	# The ancient bridge across the gap in the volcanic ridge, with ruins at both
	# ends. Deck height and span count come from the terrain on each side.
	var z0 := -322.0
	var left := 60.0
	var right := 175.0
	var deck := minf(_ground(left, z0), _ground(right, z0)) + 0.2
	# Walk inward from both shoulders to where the gap drops below the deck.
	while left < right and _ground(left + 2.0, z0) >= deck - 0.5:
		left += 2.0
	while right > left and _ground(right - 2.0, z0) >= deck - 0.5:
		right -= 2.0
	var spans := maxi(2, int(ceil((right - left + 8.0) / 8.0)))
	var start := (left + right) * 0.5 - spans * 4.0
	var s := _location("TheSpine", (left + right) * 0.5, z0, 50.0, deck)
	for k in spans:
		var x := start + 8.0 * k + 4.0 - s.position.x
		_put(s, RUIN + "ruin-bridge-span.glb", x, 0, 90.0, false)
		if k > 0 and k % 2 == 0:
			var px := start + 8.0 * k - s.position.x
			var gy := _ground(s.position.x + px, z0)
			var hgt := deck - gy
			if hgt > 2.0:
				_put(s, RUIN + "ruin-bridge-pier.glb", px, 0, 90.0, false, gy - deck, Vector3(1, hgt / 12.0, 1))
	for side: float in [-1.0, 1.0]:
		var ex := side * (spans * 4.0 + 8.0)
		_put(s, RUIN + "ruin-pillar.glb", ex, -5, 0.0)
		_put(s, RUIN + "ruin-pillar-broken.glb", ex, 5, 90.0)
		_put(s, RUIN + "ruin-wall-broken.glb", ex + side * 8.0, -8, 15.0)
		_put(s, RUIN + "ruin-floor-slab.glb", ex, 0, 0.0)
		_mark_at("LootSpots", s, ex + side * 6.0, 0)
	_mark_at("LootSpots", s, 0, 0, 0.2)
	_mark_at("Cover", s, spans * 4.0 + 8.0, -5)
	_mark_at("BotSpawns", s, -(spans * 4.0 + 16.0), 6)


func _hollow_array() -> void:
	# Ruins along the canyon floor: walls and arches hugging the walls, the great
	# ring-arch gate across the middle, monoliths on the rim above.
	var h := _location("HollowArray", 275, 228, 120.0)
	var pts: Array = RingfallGen.CANYON
	var k := 0
	for i in pts.size() - 1:
		var a: Vector2 = pts[i]
		var b: Vector2 = pts[i + 1]
		var dir := (b - a).normalized()
		var side := Vector2(-dir.y, dir.x)
		var yaw := rad_to_deg(atan2(dir.x, dir.y))
		var n := int(a.distance_to(b) / 10.0)
		for j in range(1, n):
			var p := a + dir * (10.0 * j)
			var lp := p - Vector2(h.position.x, h.position.z)
			for sgn: float in [-1.0, 1.0]:
				var q: Vector2 = lp + side * sgn * _rng.randf_range(7.0, 9.0)
				var pick := (k + int(sgn)) % 5
				var path: String = [RUIN + "ruin-wall.glb", RUIN + "ruin-wall-broken.glb", RUIN + "ruin-pillar.glb", RUIN + "ruin-arch.glb", RUIN + "ruin-pillar-broken.glb"][pick]
				_put(h, path, q.x, q.y, yaw + 90.0 + _rng.randf_range(-6, 6))
			if j % 3 == 0:
				_put(h, RUIN + "ruin-floor-slab.glb", lp.x, lp.y, yaw)
				_put(h, RUIN + "ruin-rubble.glb", lp.x + side.x * 3.0, lp.y + side.y * 3.0, _rng.randf_range(0, 360))
				_mark_at("LootSpots", h, lp.x, lp.y)
			if j % 4 == 2:
				_mark_at("Cover", h, lp.x - side.x * 4.0, lp.y - side.y * 4.0)
			k += 1
	var mid: Vector2 = pts[1] - Vector2(h.position.x, h.position.z)
	var d0: Vector2 = (pts[2] - pts[0]).normalized()
	_put(h, RUIN + "ruin-canyon-arch.glb", mid.x, mid.y, rad_to_deg(atan2(d0.x, d0.y)), true, -0.5, Vector3(1.7, 1.5, 1.5))
	for p in [Vector2(-40, -50), Vector2(55, -30), Vector2(-60, 40), Vector2(40, 60)]:
		_put(h, RUIN + "ruin-array-monolith.glb", p.x, p.y, _rng.randf_range(0, 360))
		_mark_at("LootSpots", h, p.x + 4.0, p.y)
	_put(h, RUIN + "ruin-stairs.glb", -20, -6, 40.0)
	_mark_at("BotSpawns", h, 30, -30)


func _bloomwild() -> void:
	# The forest itself is scatter (see _scatter_all); this places the giant
	# blooms that serve as landmarks and a small overgrown research outpost.
	var b := _location("Bloomwild", -320, 90, 0.0)
	for p in [Vector2(0, 0), Vector2(-40, -50), Vector2(35, 60), Vector2(-60, 70), Vector2(50, -30)]:
		var s := _rng.randf_range(1.3, 1.8)
		_put(b, VEG + "veg-bloom-stalk.glb", p.x, p.y, _rng.randf_range(0, 360), true, 0.0, Vector3.ONE * s)
		_put(b, VEG + "veg-bloom-cap.glb", p.x, p.y, _rng.randf_range(0, 360), true, 0.0, Vector3.ONE * s)
	_put(b, COL + "colony-habitat-module.glb", 20, 20, 70.0)
	_put(b, COL + "colony-work-light.glb", 28, 30, 200.0)
	_put(b, RUIN + "ruin-arch.glb", -24, 26, 30.0)
	_put(b, PICK + "colony-supply-crate.glb", -18, -12, 10.0)
	for p in [Vector2(20, 26), Vector2(-18, -12), Vector2(-40, 10), Vector2(10, -40), Vector2(60, 20), Vector2(-50, 60), Vector2(30, 70), Vector2(-70, -20)]:
		_mark_at("LootSpots", b, p.x, p.y)
	for p in [Vector2(-10, 30), Vector2(40, -10)]:
		_mark_at("Cover", b, p.x, p.y)
	_mark_at("BotSpawns", b, -30, 40)


## Scatter small props around a location center at random spots, snapped to ground.
func _props_ring(loc: Node3D, center: Vector2, radius: float, count: int, paths: Array) -> void:
	for i in count:
		var a := _rng.randf() * TAU
		var d := sqrt(_rng.randf()) * radius
		var p := center + Vector2(cos(a), sin(a)) * d
		_put(loc, paths[_rng.randi() % paths.size()], p.x, p.y, _rng.randf_range(0, 360))


func _fence_ring(loc: Node3D, radius: float, gaps: int) -> void:
	var length := maxf(_aabb(PROP + "prop-fence.glb").size.x, 1.0)
	var n := int(TAU * radius / length)
	for i in n:
		if i % (n / 4) == 0:
			continue  # gates
		var a := TAU * (i + 0.5) / n
		_put(loc, PROP + "prop-fence.glb", cos(a) * radius, sin(a) * radius, rad_to_deg(-a) + 90.0)


# ------------------------------------------------------------------ scatter

## Rules: model paths (placed together), density per 10,000 m², visibility
## range, scale range, collision ("", "box" or "cyl") and a placement test.
func _scatter_all() -> void:
	var holder := _node(_root, "Scatter")
	holder.set_script(load("res://scripts/world/scatter.gd"))
	var col := StaticBody3D.new()
	col.collision_layer = 1
	col.collision_mask = 0
	_add(holder, col, "ScatterCollision")
	var bloom := func(p: Vector2, h: float, _s: float) -> float: return smoothstep(160.0, 90.0, p.distance_to(Vector2(-320, 90))) if h > 0.5 else 0.0
	var grassy := func(_p: Vector2, h: float, s: float) -> float: return 1.0 if h > 0.8 and h < 40.0 and s < 0.35 else 0.0
	var rocky := func(_p: Vector2, h: float, s: float) -> float: return 1.0 if h > 1.0 and s > 0.45 else 0.0
	var ridge := func(p: Vector2, h: float, s: float) -> float: return 1.0 if h > 30.0 and p.y < -220.0 and s < 0.8 else 0.0
	var shore := func(p: Vector2, h: float, _s: float) -> float: return 1.0 if p.length() < 175.0 and h > -3.0 and h < 8.0 else 0.0
	var sea_rocks := func(p: Vector2, h: float, _s: float) -> float: return 1.0 if h < -1.0 and h > -12.0 and p.length() > 300.0 else 0.0
	var rules := [
		{"paths": [VEG + "veg-grass-clump.glb"], "density": 60.0, "vis": 70.0, "scale": Vector2(0.8, 1.4), "test": grassy},
		{"paths": [VEG + "veg-fern.glb"], "density": 14.0, "vis": 120.0, "scale": Vector2(0.8, 1.5), "test": bloom},
		{"paths": [VEG + "veg-glow-shrub.glb"], "density": 10.0, "vis": 220.0, "scale": Vector2(0.8, 1.6), "test": bloom},
		{"paths": [VEG + "veg-glow-shrub.glb"], "density": 0.8, "vis": 220.0, "scale": Vector2(0.7, 1.2), "test": grassy},
		{"paths": [VEG + "veg-mushroom-cluster.glb"], "density": 6.0, "vis": 140.0, "scale": Vector2(0.8, 1.6), "test": bloom},
		{"paths": [VEG + "veg-luminous-roots.glb"], "density": 3.0, "vis": 200.0, "scale": Vector2(1.0, 1.8), "test": bloom},
		{"paths": [VEG + "veg-giant-leaf.glb"], "density": 4.0, "vis": 220.0, "scale": Vector2(1.0, 1.8), "test": bloom},
		{"paths": [VEG + "veg-bloom-flower.glb"], "density": 3.0, "vis": 260.0, "scale": Vector2(1.0, 1.6), "test": bloom},
		{"paths": [VEG + "veg-tree-trunk.glb", VEG + "veg-tree-canopy.glb"], "density": 7.0, "vis": 700.0, "scale": Vector2(0.9, 1.4), "test": bloom, "collide": "cyl"},
		{"paths": [VEG + "veg-tree-trunk.glb", VEG + "veg-tree-canopy.glb"], "density": 0.35, "vis": 700.0, "scale": Vector2(0.8, 1.2), "test": grassy, "collide": "cyl"},
		{"paths": [TER + "rock-boulder-a.glb"], "density": 1.6, "vis": 450.0, "scale": Vector2(0.8, 2.2), "test": rocky, "collide": "box"},
		{"paths": [TER + "rock-boulder-b.glb"], "density": 1.0, "vis": 450.0, "scale": Vector2(0.8, 2.0), "test": grassy, "collide": "box"},
		{"paths": [TER + "rock-basalt-columns.glb"], "density": 2.5, "vis": 600.0, "scale": Vector2(0.9, 1.8), "test": ridge, "collide": "box"},
		{"paths": [TER + "rock-cliff-chunk.glb"], "density": 0.6, "vis": 800.0, "scale": Vector2(1.0, 1.6), "test": rocky, "collide": "box"},
		{"paths": [TER + "glass-shard-cluster.glb"], "density": 6.0, "vis": 450.0, "scale": Vector2(0.8, 1.8), "test": shore, "collide": "box"},
		{"paths": [TER + "glass-spire.glb"], "density": 1.5, "vis": 700.0, "scale": Vector2(1.0, 2.2), "test": shore, "collide": "box"},
		{"paths": [TER + "rock-boulder-a.glb"], "density": 0.5, "vis": 700.0, "scale": Vector2(2.0, 4.0), "test": sea_rocks, "collide": "box"},
	]
	var total := 0
	for rule: Dictionary in rules:
		total += _scatter(holder, col, rule)
	print("scatter: %d instances" % total)


func _blocked(p: Vector2) -> bool:
	for k: Array in _keep_clear:
		if p.distance_to(k[0]) < k[1]:
			return true
	return false


func _scatter(holder: Node3D, col: StaticBody3D, rule: Dictionary) -> int:
	var size := _data.world_size()
	var tries := int(rule.density * size * size / 10000.0)
	var cells := {}
	var test: Callable = rule.test
	var sc: Vector2 = rule.scale
	var placed := 0
	for i in tries:
		var p := Vector2(_rng.randf_range(-size * 0.5, size * 0.5), _rng.randf_range(-size * 0.5, size * 0.5))
		if _blocked(p):
			continue
		var h := _ground(p.x, p.y)
		var nrm := _data.normal_at(p.x, p.y)
		var slope := 1.0 - nrm.y
		if _rng.randf() > float(test.call(p, h, slope)):
			continue
		var s := _rng.randf_range(sc.x, sc.y)
		var basis := Basis(Vector3.UP, _rng.randf() * TAU).scaled(Vector3.ONE * s)
		# Tilt small things with the slope; keep trees and spires upright.
		if s < 2.0 and not rule.has("collide"):
			basis = Basis(Quaternion(Vector3.UP, nrm)) * basis
		var xf := Transform3D(basis, Vector3(p.x, h - 0.1, p.y))
		var key := Vector2i(floori(p.x / CELL), floori(p.y / CELL))
		if not cells.has(key):
			cells[key] = []
		cells[key].append(xf)
		placed += 1
		if rule.has("collide"):
			_scatter_collision(col, rule, xf)
	# One batch per model per cell; scripts/world/scatter.gd builds the MultiMeshes at load.
	var batches: Array[Dictionary] = holder.get("batches")
	for key: Vector2i in cells:
		var packed := PackedFloat32Array()
		for xf: Transform3D in cells[key]:
			_pack(xf, packed)
		for path: String in rule.paths:
			batches.append({"path": path, "vis": float(rule.vis), "shadow": float(rule.vis) >= 150.0, "xforms": packed})
	holder.set("batches", batches)
	return placed


func _pack(xf: Transform3D, into: PackedFloat32Array) -> void:
	for v: Vector3 in [xf.basis.x, xf.basis.y, xf.basis.z, xf.origin]:
		into.append(v.x)
		into.append(v.y)
		into.append(v.z)


func _scatter_collision(col: StaticBody3D, rule: Dictionary, xf: Transform3D) -> void:
	var path: String = rule.paths[0]
	var box := _aabb(path)
	var cs := CollisionShape3D.new()
	if rule.collide == "cyl":
		var c := CylinderShape3D.new()
		c.radius = maxf(0.2, minf(box.size.x, box.size.z) * 0.35)
		c.height = box.size.y
		cs.shape = c
		cs.transform = Transform3D(xf.basis.orthonormalized(), xf.origin) * Transform3D(Basis.IDENTITY, box.get_center())
		cs.scale = Vector3.ONE * xf.basis.get_scale().x
	else:
		var b := BoxShape3D.new()
		b.size = box.size * 0.85
		cs.shape = b
		cs.transform = xf * Transform3D(Basis.IDENTITY, box.get_center())
	_add(col, cs, "Shape")


# ---------------------------------------------------------------- gameplay

func _gameplay() -> void:
	var storm := Node3D.new()
	storm.set_script(load("res://scripts/world/ion_storm.gd"))
	storm.set("start_radius", 560.0)
	var phases: Array[Dictionary] = [
		{"wait": 120.0, "shrink": 60.0, "radius": 380.0, "dps": 1.0},
		{"wait": 90.0, "shrink": 50.0, "radius": 240.0, "dps": 2.0},
		{"wait": 75.0, "shrink": 45.0, "radius": 140.0, "dps": 4.0},
		{"wait": 60.0, "shrink": 40.0, "radius": 70.0, "dps": 7.0},
		{"wait": 45.0, "shrink": 30.0, "radius": 25.0, "dps": 10.0},
		{"wait": 30.0, "shrink": 30.0, "radius": 0.0, "dps": 15.0},
	]
	storm.set("phases", phases)
	_add(_root, storm, "IonStorm")
	_add(_root, Node3D.new(), "Loot")
	var player: Node = load("res://scenes/player.tscn").instantiate()
	player.set("water_level", 0.0)
	_add(_root, player, "Player")
	var hud := CanvasLayer.new()
	hud.set_script(load("res://scripts/ui/combat_hud.gd"))
	_add(_root, hud, "HUD")
	var inv := CanvasLayer.new()
	inv.set_script(load("res://scripts/ui/inventory_screen.gd"))
	_add(_root, inv, "InventoryScreen")


# ---------------------------------------------------------------- the world

func _environment() -> void:
	var we := WorldEnvironment.new()
	var env := Environment.new()
	var sky := Sky.new()
	var mat := ShaderMaterial.new()
	mat.shader = load("res://shaders/ringed_sky.gdshader")
	sky.sky_material = mat
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.fog_enabled = true
	env.fog_light_color = Color("8a93b8")
	env.fog_density = 0.0007
	env.fog_sky_affect = 0.0
	we.environment = env
	_add(_root, we, "WorldEnvironment")
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-42, -35, 0)
	sun.light_color = Color("ffe3c2")
	sun.light_energy = 1.25
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 90.0
	_add(_root, sun, "Sun")


func _terrain() -> void:
	var t := Node3D.new()
	t.set_script(load("res://scripts/world/ringfall_terrain.gd"))
	t.set("heightmap", load(DIR + "/height.png"))
	t.set("splatmap", load(DIR + "/splat.png"))
	t.set("data", _data)
	_add(_root, t, "Terrain")
