class_name ItemCatalog
extends RefCounted
## Item catalogue: every ItemDef under data/items/, loaded once on first use.
## Look items up by id: ItemCatalog.get_def(&"ar7"). Ammunition types live in AmmoTypes.

const DATA_DIR := "res://data/items/"

static var _defs: Dictionary = {}


static func _ensure() -> void:
	if not _defs.is_empty():
		return
	for file in ResourceLoader.list_directory(DATA_DIR):
		if file.ends_with(".tres"):
			var def := load(DATA_DIR + file) as ItemDef
			if def:
				_defs[def.id] = def


static func get_def(id: StringName) -> ItemDef:
	_ensure()
	if not _defs.has(id):
		push_error("Unknown item id: %s" % id)
		return null
	return _defs[id]


static func stack(id: StringName, qty := 1) -> ItemStack:
	return ItemStack.new(get_def(id), qty)


static func all_ids() -> Array:
	_ensure()
	return _defs.keys()
