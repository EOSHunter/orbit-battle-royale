class_name TerrainData
extends Resource
## Baked terrain heights for collision and gameplay queries (spawning, scatter,
## water depth). The same heights drive the GPU terrain through the heightmap
## image; this copy avoids decoding the image at runtime.

## Samples per side (the grid is size x size).
@export var size := 513
## Meters between samples.
@export var spacing := 2.0
## Height of every sample in meters, row-major (z then x), north-west first.
@export var heights := PackedFloat32Array()
## Range used to encode the 16-bit heightmap image: height = min + v * range.
@export var height_min := -30.0
@export var height_range := 140.0


func world_size() -> float:
	return (size - 1) * spacing


## Bilinear height at a world position (x, z), with the map centered on 0.
func height_at(x: float, z: float) -> float:
	var half := world_size() * 0.5
	var gx := clampf((x + half) / spacing, 0.0, size - 1.001)
	var gz := clampf((z + half) / spacing, 0.0, size - 1.001)
	var ix := int(gx)
	var iz := int(gz)
	var fx := gx - ix
	var fz := gz - iz
	var a := heights[iz * size + ix]
	var b := heights[iz * size + ix + 1]
	var c := heights[(iz + 1) * size + ix]
	var d := heights[(iz + 1) * size + ix + 1]
	return lerpf(lerpf(a, b, fx), lerpf(c, d, fx), fz)


func normal_at(x: float, z: float) -> Vector3:
	var e := spacing
	var hx := height_at(x + e, z) - height_at(x - e, z)
	var hz := height_at(x, z + e) - height_at(x, z - e)
	return Vector3(-hx, 2.0 * e, -hz).normalized()
