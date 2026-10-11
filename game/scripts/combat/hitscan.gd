class_name Hitscan
extends RefCounted
## Shared instant-hit shooting for players and bots: spread, pellets, falloff,
## damage to anything with a Health child, tracers and impacts.

const WORLD := 1
const GRAPPABLE := 2
const PLAYER := 4
const BOTS := 8
const SHOT_MASK := WORLD | GRAPPABLE | PLAYER | BOTS


## Fires one shot of `def` from `origin` along `forward` with a spread cone
## of `spread_deg`. Returns {hits: int, damage: float, kills: int}.
static func fire(world: World3D, origin: Vector3, forward: Vector3, muzzle: Vector3, def: WeaponDef,
		spread_deg: float, shooter: Node, exclude: Array[RID], damage_scale := 1.0) -> Dictionary:
	var result := {"hits": 0, "damage": 0.0, "kills": 0}
	var space := world.direct_space_state
	var basis := Basis.looking_at(forward, Vector3.UP if absf(forward.y) < 0.99 else Vector3.FORWARD)
	for i in def.pellets:
		var dir := _spread(basis, spread_deg)
		var to := origin + dir * def.max_range
		var query := PhysicsRayQueryParameters3D.create(origin, to, SHOT_MASK, exclude)
		var hit := space.intersect_ray(query)
		var end := to
		if not hit.is_empty():
			end = hit.position
			var body := hit.collider as Node
			var health: Health = null
			if body:
				health = body.get_node_or_null("Health") as Health
			if health and health.alive:
				var shielded := health.shield > 0.0
				var dealt := health.take_damage(def.damage_at(origin.distance_to(end)) * damage_scale, origin, shooter)
				result.hits += 1
				result.damage += dealt
				if not health.alive:
					result.kills += 1
				if shielded:
					Fx.shield_hit(world, end, hit.normal)
					if health.shield <= 0.0 and body is Node3D:
						Fx.shield_break(world, (body as Node3D).global_position + Vector3.UP * 1.0)
				else:
					Fx.impact(world, end, hit.normal, true)
			else:
				Fx.impact(world, end, hit.normal, false)
		if i < 3:
			Fx.tracer(world, muzzle, end)
	return result


static func _spread(basis: Basis, spread_deg: float) -> Vector3:
	# Uniform over the cone's disc so pellets don't clump in the middle.
	var r := tan(deg_to_rad(spread_deg)) * sqrt(randf())
	var a := randf() * TAU
	return (basis * Vector3(cos(a) * r, sin(a) * r, -1.0)).normalized()
