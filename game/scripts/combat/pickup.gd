class_name Pickup
extends Area3D
## Ground loot: an item stack or an ammunition bundle. Walking over it picks up
## whatever fits without replacing anything; the interact key does the same
## from a short distance, and the inventory screen can replace a slot with it.

signal emptied

const GROUP := "pickups"
const INTERACT_RANGE := 2.6

@export var item_id: StringName
@export var qty := 1
## Rounds loaded, for weapons. -1 means a full magazine.
@export var mag := -1
## Set instead of item_id for an ammunition bundle.
@export var ammo_type: StringName
@export var ammo_amount := 0

var stack: ItemStack
var _visual: Node3D
var _label: Label3D
var _t := 0.0


func _ready() -> void:
	add_to_group(GROUP)
	collision_layer = 0
	collision_mask = Hitscan.PLAYER
	monitoring = true
	var shape := CollisionShape3D.new()
	var sphere := SphereShape3D.new()
	sphere.radius = 1.1
	shape.shape = sphere
	add_child(shape)
	if item_id != &"" and stack == null:
		stack = ItemStack.new(ItemCatalog.get_def(item_id), qty, mag)
	_build_visual()
	body_entered.connect(_on_body_entered)


func is_ammo() -> bool:
	return stack == null and ammo_type != &""


func display_name() -> String:
	if is_ammo():
		return "%s ammo ×%d" % [AmmoTypes.display_name(ammo_type), ammo_amount]
	var n := stack.def.display_name
	return n if stack.qty <= 1 else "%s ×%d" % [n, stack.qty]


func color() -> Color:
	return Color("ffd18a") if is_ammo() else stack.def.color


func _build_visual() -> void:
	_visual = Node3D.new()
	add_child(_visual)
	_visual.position.y = 0.5
	var model := AmmoTypes.instantiate_model(ammo_type) if is_ammo() else stack.def.instantiate_model()
	if model:
		_visual.add_child(model)
	else:
		_build_placeholder()
	_label = Label3D.new()
	_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_label.font_size = 40
	_label.pixel_size = 0.005
	_label.outline_size = 10
	_label.modulate = color().lightened(0.3)
	_label.position.y = 1.05
	_label.no_depth_test = false
	add_child(_label)
	_refresh_label()


func _build_placeholder() -> void:
	var mi := MeshInstance3D.new()
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color().darkened(0.35)
	mat.emission_enabled = true
	mat.emission = color()
	mat.emission_energy_multiplier = 0.6
	if is_ammo():
		var box := BoxMesh.new()
		box.size = Vector3(0.4, 0.25, 0.3)
		mi.mesh = box
	elif stack.def.is_weapon():
		var box := BoxMesh.new()
		box.size = Vector3(0.12, 0.14, 0.8)
		mi.mesh = box
		mat.albedo_color = Color("2b3550")
	else:
		var cyl := CylinderMesh.new()
		cyl.top_radius = 0.14
		cyl.bottom_radius = 0.14
		cyl.height = 0.32
		mi.mesh = cyl
	mi.material_override = mat
	_visual.add_child(mi)


func _refresh_label() -> void:
	if _label:
		_label.text = display_name()


func _process(delta: float) -> void:
	_t += delta
	_visual.rotation.y += delta * 1.2
	_visual.position.y = 0.5 + sin(_t * 2.0) * 0.06


func _on_body_entered(body: Node3D) -> void:
	var p := body as Player
	if p and p.can_auto_pickup():
		collect_into(p.inventory, true)


## Moves whatever fits into `inv`. Returns true if anything was taken.
func collect_into(inv: Inventory, automatic := false) -> bool:
	var took := 0
	if is_ammo():
		took = inv.add_ammo(ammo_type, ammo_amount)
		ammo_amount -= took
	elif not automatic or _auto_allowed():
		took = inv.add(stack)
	if took > 0:
		if (is_ammo() and ammo_amount <= 0) or (not is_ammo() and stack.qty <= 0):
			emptied.emit()
			queue_free()
		else:
			_refresh_label()
	return took > 0


## Called after the inventory screen replaced a slot with this pickup.
func after_replace() -> void:
	if stack.qty <= 0:
		emptied.emit()
		queue_free()
	else:
		_refresh_label()


func _auto_allowed() -> bool:
	# Weapons and items are picked up on contact; the design keeps replacing explicit.
	return true


## Drops a stack on the ground near `pos`.
static func spawn_stack(parent: Node, s: ItemStack, pos: Vector3) -> Pickup:
	var p := Pickup.new()
	p.stack = s
	p.item_id = s.def.id
	parent.add_child(p)
	p.global_position = pos
	return p


static func spawn_ammo(parent: Node, type: StringName, amount: int, pos: Vector3) -> Pickup:
	var p := Pickup.new()
	p.ammo_type = type
	p.ammo_amount = amount
	parent.add_child(p)
	p.global_position = pos
	return p
