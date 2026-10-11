class_name HealDef
extends ItemDef
## Healing item data. Used up only when the use timer completes.

enum Pool { HEALTH, SHIELD, BOTH }

@export var pool := Pool.HEALTH
## Points restored; use a large number for "full".
@export_range(1.0, 200.0, 1.0) var amount := 25.0
@export_range(0.5, 15.0, 0.1, "suffix:s") var use_time := 2.0
## Walking speed multiplier while using.
@export_range(0.1, 1.0, 0.05) var move_scale := 0.45
