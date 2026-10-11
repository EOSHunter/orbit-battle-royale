class_name Health
extends Node
## Health and shields. Shields absorb damage first; anything left goes to
## health. Storm damage can bypass shields. Healing never exceeds the maximum.

signal damaged(amount: float, from: Vector3, attacker: Node)
signal shield_broken
signal healed(amount: float)
signal died(attacker: Node)

@export var max_health := 100.0
@export var max_shield := 100.0
@export var start_shield := 0.0

var health := 100.0
var shield := 0.0
var alive := true
var last_attacker: Node


func _ready() -> void:
	reset()


func reset() -> void:
	health = max_health
	shield = start_shield
	alive = true
	last_attacker = null


## Returns the damage actually dealt. `from` is the attacker's position, used
## for the directional damage indicator.
func take_damage(amount: float, from := Vector3.ZERO, attacker: Node = null, bypass_shield := false) -> float:
	if not alive or amount <= 0.0:
		return 0.0
	var had_shield := shield > 0.0
	var to_shield := 0.0 if bypass_shield else minf(shield, amount)
	shield -= to_shield
	var to_health := minf(health, amount - to_shield)
	health -= to_health
	last_attacker = attacker
	var dealt := to_shield + to_health
	damaged.emit(dealt, from, attacker)
	if had_shield and shield <= 0.0 and to_shield > 0.0:
		shield_broken.emit()
	if health <= 0.0:
		alive = false
		died.emit(attacker)
	return dealt


## True if the item would restore anything right now.
func can_use(def: HealDef) -> bool:
	if not alive:
		return false
	match def.pool:
		HealDef.Pool.HEALTH:
			return health < max_health
		HealDef.Pool.SHIELD:
			return shield < max_shield
		_:
			return health < max_health or shield < max_shield


func apply_heal(def: HealDef) -> float:
	var before := health + shield
	match def.pool:
		HealDef.Pool.HEALTH:
			health = minf(max_health, health + def.amount)
		HealDef.Pool.SHIELD:
			shield = minf(max_shield, shield + def.amount)
		_:
			health = max_health
			shield = max_shield
	var gained := health + shield - before
	if gained > 0.0:
		healed.emit(gained)
	return gained
