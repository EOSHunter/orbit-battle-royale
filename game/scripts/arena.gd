extends Node3D
## Combat slice: loot on the ground, three bots, elimination feed, win or lose,
## and F5 to play again. Bots hear the player's gunfire within their range.

## Falling below this height respawns the player at the spawn point.
@export var kill_height := -60.0
## Bots in the round; names and weapons cycle through BOT_SETUP.
@export var bot_count := 3
const BOT_SETUP := [
	{"name": "Bot Rhea", "weapon": &"ar7"},
	{"name": "Bot Ivo", "weapon": &"sg4"},
	{"name": "Bot Kade", "weapon": &"ar7"},
]
## Loot placed on the LootSpots markers, in order. Placeholder amounts.
const LOOT := [
	{"item": &"ar7"}, {"ammo": &"medium", "n": 90}, {"item": &"shield_cell", "n": 2},
	{"item": &"sg4"}, {"ammo": &"shells", "n": 16}, {"item": &"field_patch", "n": 3},
	{"item": &"shield_pack", "n": 2}, {"ammo": &"medium", "n": 60}, {"item": &"field_patch", "n": 2},
	{"item": &"shield_cell", "n": 4}, {"ammo": &"shells", "n": 12}, {"item": &"shield_pack", "n": 1},
]

@onready var player: Player = $Player
@onready var hud: CanvasLayer = $HUD
@onready var inventory_screen: CanvasLayer = $InventoryScreen
@onready var _loot: Node3D = $Loot
@onready var _markers: Node3D = $Markers

var _bots_alive := 0
var _ended := false


func _ready() -> void:
	hud.bind(player)
	inventory_screen.player = player
	inventory_screen.world_parent = _loot
	inventory_screen.closed.connect(_recapture)
	player.eliminated.connect(_on_player_eliminated)
	player.weapons.fired.connect(func(_w: WeaponDef) -> void:
		for b in get_tree().get_nodes_in_group("bots"):
			(b as Bot).hear(player.global_position))
	start_round()


func start_round() -> void:
	_ended = false
	hud.show_center("")
	for c in _loot.get_children():
		c.queue_free()
	for b in get_tree().get_nodes_in_group("bots"):
		b.queue_free()
	var spots := _markers.get_node("LootSpots").get_children()
	for i in spots.size():
		var entry: Dictionary = LOOT[i % LOOT.size()]
		var at := (spots[i] as Node3D).global_position
		if entry.has("ammo"):
			Pickup.spawn_ammo(_loot, entry.ammo, int(entry.n), at)
		else:
			Pickup.spawn_stack(_loot, ItemCatalog.stack(entry.item, int(entry.get("n", 1))), at)
	var cover: Array[Vector3] = []
	for m in _markers.get_node("Cover").get_children():
		cover.append((m as Node3D).global_position)
	var spawns := _markers.get_node("BotSpawns").get_children()
	_bots_alive = 0
	for i in bot_count:
		var setup: Dictionary = BOT_SETUP[i % BOT_SETUP.size()].duplicate()
		if i >= BOT_SETUP.size():
			setup.name = "%s %d" % [setup.name, i / BOT_SETUP.size() + 1]
		var bot := _make_bot(setup)
		add_child(bot)
		bot.global_position = (spawns[i % spawns.size()] as Node3D).global_position
		bot.target = player
		bot.cover_points = cover
		bot.eliminated.connect(_on_bot_eliminated)
		_bots_alive += 1
	player.respawn((_markers.get_node("PlayerSpawn") as Node3D).global_transform)
	hud.alive_count = _bots_alive + 1
	hud.eliminations = 0
	hud.toast("Find a weapon. %d bots are on the field." % bot_count)


func _make_bot(setup: Dictionary) -> Bot:
	var bot := Bot.new()
	bot.name = String(setup.name).replace(" ", "")
	bot.display_name = setup.name
	bot.weapon_id = setup.weapon
	var h := Health.new()
	h.name = "Health"
	bot.add_child(h)
	return bot


func _on_bot_eliminated(bot: Bot, attacker: Node) -> void:
	_bots_alive -= 1
	hud.alive_count = _bots_alive + (1 if player.is_alive() else 0)
	if attacker == player:
		hud.eliminations += 1
		var w := player.weapons.weapon()
		hud.feed("You eliminated %s%s" % [bot.display_name, " · " + w.display_name if w else ""])
	else:
		hud.feed("%s was eliminated" % bot.display_name)
	# Drop what the bot carried: its weapon, some ammo, unused heals.
	var at := bot.global_position
	Pickup.spawn_stack(_loot, ItemStack.new(bot.weapon, 1, bot.mag), at + Vector3(0.6, 0.1, 0))
	Pickup.spawn_ammo(_loot, bot.weapon.ammo_type, mini(bot.reserve, 60), at + Vector3(-0.6, 0.1, 0))
	if bot.heals > 0:
		Pickup.spawn_stack(_loot, ItemCatalog.stack(&"field_patch", bot.heals), at + Vector3(0, 0.1, 0.6))
	if _bots_alive <= 0 and player.is_alive():
		_ended = true
		hud.show_center("Last one standing\nF5 to play again")


func _on_player_eliminated(attacker: Node) -> void:
	_ended = true
	var by := (attacker as Bot).display_name if attacker is Bot else "the field"
	hud.alive_count = _bots_alive
	hud.feed("%s eliminated you" % by)
	hud.show_center("Eliminated by %s\nF5 to play again" % by)
	if inventory_screen.is_open():
		inventory_screen.close()


func _unhandled_input(event: InputEvent) -> void:
	var button := event as InputEventMouseButton
	if button and button.pressed and button.button_index == MOUSE_BUTTON_LEFT and not MouseLock.is_captured() and player.combat_input and not inventory_screen.is_open():
		get_viewport().set_input_as_handled()
		player.input_grace = 0.25
		_recapture()
	elif event.is_action_pressed("inventory") and not inventory_screen.is_open() and player.is_alive():
		inventory_screen.open()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("respawn"):
		start_round()
	elif event.is_action_pressed("ui_cancel") and not inventory_screen.is_open():
		MouseLock.release()


func _recapture() -> void:
	MouseLock.capture()


func _physics_process(_delta: float) -> void:
	if player.global_position.y < kill_height:
		player.teleport_to((_markers.get_node("PlayerSpawn") as Node3D).global_transform)
