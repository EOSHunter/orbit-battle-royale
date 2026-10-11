class_name WeaponDef
extends ItemDef
## Hitscan weapon data. Every number is a placeholder for playtesting.

@export_group("Damage")
@export_range(1.0, 200.0, 0.5) var damage := 20.0
## Rays per shot (shotguns fire several).
@export_range(1, 20) var pellets := 1
@export_range(5.0, 300.0, 1.0, "suffix:m") var max_range := 150.0
## Damage starts dropping at this distance and reaches `falloff_min` at `max_range`.
@export_range(1.0, 300.0, 1.0, "suffix:m") var falloff_start := 60.0
@export_range(0.0, 1.0, 0.05) var falloff_min := 0.6

@export_group("Handling")
@export var automatic := true
@export_range(0.03, 2.0, 0.01, "suffix:s") var fire_interval := 0.1
@export_range(1, 200) var magazine := 30
@export var ammo_type: StringName = &"medium"
@export_range(0.2, 6.0, 0.05, "suffix:s") var reload_time := 1.9
@export_range(0.1, 2.0, 0.05, "suffix:s") var equip_time := 0.45

@export_group("Accuracy")
## Cone half-angle while firing from the hip and standing still.
@export_range(0.0, 15.0, 0.1, "suffix:°") var spread_hip := 2.0
@export_range(0.0, 15.0, 0.1, "suffix:°") var spread_aim := 0.4
## Added while moving at full speed.
@export_range(0.0, 15.0, 0.1, "suffix:°") var spread_moving := 2.5
@export_range(0.0, 10.0, 0.05, "suffix:°") var recoil_pitch := 0.7
@export_range(0.0, 10.0, 0.05, "suffix:°") var recoil_yaw := 0.3
## Field of view multiplier while aiming down sights.
@export_range(0.3, 1.0, 0.05) var aim_fov_scale := 0.75


func damage_at(distance: float) -> float:
	if distance <= falloff_start or max_range <= falloff_start:
		return damage
	var t := clampf((distance - falloff_start) / (max_range - falloff_start), 0.0, 1.0)
	return damage * lerpf(1.0, falloff_min, t)
