class_name AmmoTypes
extends RefCounted
## Ammunition reserves: carried separately, never in a slot. Caps are placeholders.

const TYPES := {
	&"medium": {"name": "Medium", "cap": 240, "model": "res://assets/models/pickups/ammo-medium.glb"},
	&"shells": {"name": "Shells", "cap": 30, "model": "res://assets/models/pickups/ammo-shells.glb"},
	&"light": {"name": "Light", "cap": 240, "model": "res://assets/models/pickups/ammo-light.glb"},
	&"heavy": {"name": "Heavy", "cap": 30, "model": "res://assets/models/pickups/ammo-heavy.glb"},
}


static func cap(type: StringName) -> int:
	return int(TYPES[type]["cap"]) if TYPES.has(type) else 0


static func display_name(type: StringName) -> String:
	return str(TYPES[type]["name"]) if TYPES.has(type) else str(type)


## The ammo box model for a type, facing -Z, or null if it isn't imported.
static func instantiate_model(type: StringName) -> Node3D:
	var path: String = str(TYPES[type].get("model", "")) if TYPES.has(type) else ""
	if path.is_empty() or not ResourceLoader.exists(path):
		return null
	var model := (load(path) as PackedScene).instantiate() as Node3D
	model.rotation.y = PI
	return model
