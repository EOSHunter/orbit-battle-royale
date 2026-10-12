extends SceneTree
## Converts every PNG in a folder to a JPEG no wider than max_width, for light
## review copies (Asset Hub thumbnails and screenshots).
##   godot --headless --path game -s res://tools/convert_images.gd -- <src_dir> <dst_dir> <max_width> [quality 0-1]


func _initialize() -> void:
	var a := OS.get_cmdline_user_args()
	var src: String = a[0]
	var dst: String = a[1]
	var max_w := int(a[2])
	var q := float(a[3]) if a.size() > 3 else 0.85
	DirAccess.make_dir_recursive_absolute(dst)
	var n := 0
	for f in DirAccess.get_files_at(src):
		if not f.to_lower().ends_with(".png"):
			continue
		var img := Image.load_from_file(src.path_join(f))
		if img.get_width() > max_w:
			img.resize(max_w, int(img.get_height() * float(max_w) / img.get_width()), Image.INTERPOLATE_LANCZOS)
		img.convert(Image.FORMAT_RGB8)
		img.save_jpg(dst.path_join(f.get_basename() + ".jpg"), q)
		n += 1
	print("converted ", n)
	quit()
