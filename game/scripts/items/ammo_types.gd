class_name AmmoTypes
extends RefCounted
## Ammunition reserves: carried separately, never in a slot. Caps are placeholders.

const TYPES := {
	&"medium": {"name": "Medium", "cap": 240},
	&"shells": {"name": "Shells", "cap": 30},
	&"light": {"name": "Light", "cap": 240},
	&"heavy": {"name": "Heavy", "cap": 30},
}


static func cap(type: StringName) -> int:
	return int(TYPES[type]["cap"]) if TYPES.has(type) else 0


static func display_name(type: StringName) -> String:
	return str(TYPES[type]["name"]) if TYPES.has(type) else str(type)
