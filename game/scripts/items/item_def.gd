class_name ItemDef
extends Resource
## Base data for anything that can sit in an inventory slot. Balance values
## live in the .tres files under data/items/, never in code.

enum Kind { WEAPON, HEAL, GRENADE, UTILITY }

@export var id: StringName
@export var display_name := ""
@export var kind := Kind.HEAL
## How many fit in one slot.
@export_range(1, 99) var stack_max := 1
## How many can be carried in total across all slots.
@export_range(1, 99) var carry_cap := 1
## HUD and pickup tint until production icons exist.
@export var color := Color("f3f5fa")
@export_multiline var description := ""


func is_weapon() -> bool:
	return kind == Kind.WEAPON


## Slots 1–2 take weapons, slots 3–5 take everything else (Phase 1 rule).
func fits_slot(index: int) -> bool:
	return index < 2 if is_weapon() else index >= 2
