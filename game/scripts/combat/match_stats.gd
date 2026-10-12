class_name MatchStats
extends RefCounted
## The player's numbers for this match or practice session: shots, hits,
## damage, eliminations, reloads and time. Shown in the in-match menu and on
## the results screen.

static var shots := 0
static var hits := 0
static var damage := 0.0
static var kills := 0
static var reloads := 0
static var _start_ms := 0


static func reset() -> void:
	shots = 0
	hits = 0
	damage = 0.0
	kills = 0
	reloads = 0
	_start_ms = Time.get_ticks_msec()


## Count everything the player's weapons do from now on.
static func track(player: Player) -> void:
	reset()
	var w := player.weapons
	w.fired.connect(func(_d: WeaponDef) -> void: shots += 1)
	w.hit_confirmed.connect(func(dealt: float, killed: bool) -> void:
		hits += 1
		damage += dealt
		if killed:
			kills += 1)
	w.reload_started.connect(func(_s: float) -> void: reloads += 1)


static func accuracy() -> float:
	return float(hits) / shots if shots > 0 else 0.0


static func seconds() -> float:
	return (Time.get_ticks_msec() - _start_ms) / 1000.0


static func time_text() -> String:
	var t := int(seconds())
	return "%d:%02d" % [t / 60, t % 60]
