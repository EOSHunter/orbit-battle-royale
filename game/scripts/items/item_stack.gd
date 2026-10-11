class_name ItemStack
extends RefCounted
## One slot's contents: an item, how many, and (for weapons) rounds loaded.

var def: ItemDef
var qty := 1
var mag := 0


func _init(item: ItemDef = null, count := 1, loaded := -1) -> void:
	def = item
	qty = count
	if item is WeaponDef:
		mag = (item as WeaponDef).magazine if loaded < 0 else loaded


func copy() -> ItemStack:
	return ItemStack.new(def, qty, mag)


func _to_string() -> String:
	return "%s×%d" % [def.id if def else &"empty", qty]
