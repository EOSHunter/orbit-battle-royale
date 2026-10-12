extends SceneTree
## Builds the Ringfall map in two steps (the images must be imported between them):
##   godot --headless --path game -s res://tools/build_ringfall.gd -- maps
##   godot --headless --path game --import
##   godot --headless --path game -s res://tools/build_ringfall.gd -- scene
## "maps" bakes maps/ringfall/height.png (16-bit split over R and G), splat.png
## and terrain.res (collision heights). "scene" assembles scenes/ringfall.tscn.

const DIR := "res://maps/ringfall"

## The heightmap must stay exact: lossless, no mipmaps, no 3D detection.
const HEIGHT_IMPORT := """[remap]

importer="texture"
type="CompressedTexture2D"

[deps]

source_file="res://maps/ringfall/height.png"

[params]

compress/mode=0
compress/high_quality=false
compress/lossy_quality=0.7
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=false
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/fix_alpha_border=false
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit=0
detect_3d/compress_to=0
"""


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var step: String = args[0] if args.size() > 0 else "maps"
	DirAccess.make_dir_recursive_absolute(DIR)
	if step == "maps":
		_bake_maps()
	else:
		var builder: Object = load("res://tools/ringfall_scene.gd").new()
		builder.call("build")
	quit()


## Colour-coded top-down map for reviewing the layout (not used by the game):
## sea blues below 0, greens to browns to white with height, contour every 10 m.
func _save_preview(heights: PackedFloat32Array, size: int) -> void:
	var img := Image.create(size, size, false, Image.FORMAT_RGB8)
	var ramp := Gradient.new()
	ramp.offsets = PackedFloat32Array([0.0, 0.18, 0.21, 0.3, 0.5, 0.75, 1.0])
	ramp.colors = PackedColorArray([Color("0b2a4a"), Color("2a8fb0"), Color("d8cc9a"), Color("7aa35a"), Color("6b5a3a"), Color("8a8a8a"), Color("ffffff")])
	for i in heights.size():
		var h := heights[i]
		var c := ramp.sample(clampf((h + 25.0) / 120.0, 0.0, 1.0))
		if fposmod(h, 10.0) < 0.6 and h > 0.0:
			c = c.darkened(0.35)
		img.set_pixel(i % size, i / size, c)
	img.save_png("user://ringfall_preview.png")
	print("preview: ", ProjectSettings.globalize_path("user://ringfall_preview.png"))


func _bake_maps() -> void:
	var t0 := Time.get_ticks_msec()
	var gen := RingfallGen.new()
	var out := gen.generate()
	var heights: PackedFloat32Array = out.heights
	var data := TerrainData.new()
	data.size = RingfallGen.SIZE
	data.spacing = RingfallGen.SPACING
	data.heights = heights
	var lo := INF
	var hi := -INF
	for h in heights:
		lo = minf(lo, h)
		hi = maxf(hi, h)
	print("height range %.1f .. %.1f m" % [lo, hi])
	var img := Image.create(data.size, data.size, false, Image.FORMAT_RGB8)
	for i in heights.size():
		var v := int(round(clampf((heights[i] - data.height_min) / data.height_range, 0.0, 1.0) * 65535.0))
		img.set_pixel(i % data.size, i / data.size, Color8(v >> 8, v & 255, 0))
	img.save_png(DIR + "/height.png")
	var f := FileAccess.open(DIR + "/height.png.import", FileAccess.WRITE)
	f.store_string(HEIGHT_IMPORT)
	f.close()
	(out.splat as Image).save_png(DIR + "/splat.png")
	_save_preview(heights, data.size)
	ResourceSaver.save(data, DIR + "/terrain.res", ResourceSaver.FLAG_COMPRESS)
	print("maps baked in %.1f s" % ((Time.get_ticks_msec() - t0) / 1000.0))
