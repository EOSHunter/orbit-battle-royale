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

@export_group("Model")
## Production model (.glb from art/<category>/models/). Empty, or not imported,
## falls back to the placeholder shapes.
@export_file("*.glb") var model_path := ""
## Where the model's origin (the grip, or the wrist) sits in first person, in camera space.
@export var view_offset := Vector3(0.14, -0.165, -0.38)
## Tilt in first person, in degrees: a little barrel-up and toward the center.
@export var view_rotation := Vector3(4.0, 4.0, 0.0)
## Aiming down sights: distance from the eye to the rear sight (the model's "sight" marker).
@export var ads_eye := 0.17


func load_model() -> PackedScene:
	if model_path.is_empty() or not ResourceLoader.exists(model_path):
		return null
	return load(model_path) as PackedScene


## A fresh copy of the model facing the node's -Z (glTF models face +Z), or null.
func instantiate_model() -> Node3D:
	var scene := load_model()
	if scene == null:
		return null
	var model := scene.instantiate() as Node3D
	model.rotation.y = PI
	return model


func is_weapon() -> bool:
	return kind == Kind.WEAPON


## Slots 1–2 take weapons, slots 3–5 take everything else (Phase 1 rule).
func fits_slot(index: int) -> bool:
	return index < 2 if is_weapon() else index >= 2
