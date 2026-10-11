class_name Inventory
extends Node
## Five slots (1–2 weapons, 3–5 items) plus separate ammunition reserves.
## All rules live here so they can be tested without a scene:
## - matching pickups fill existing stacks first, then empty eligible slots
## - an item's carry cap counts across all slots, so splitting or replacing
##   can never exceed it
## - automatic pickup never replaces an occupied slot; replacing is explicit
## - quantities are conserved: nothing is created or destroyed by moving items

signal changed
signal selected_changed(index: int)

const SLOT_COUNT := 5

var slots: Array[ItemStack] = []
var selected := 0
var ammo: Dictionary = {}


func _init() -> void:
	slots.resize(SLOT_COUNT)


# ---------------------------------------------------------------- queries

func get_slot(index: int) -> ItemStack:
	return slots[index] if index >= 0 and index < SLOT_COUNT else null


func selected_stack() -> ItemStack:
	return slots[selected]


func count(id: StringName) -> int:
	var n := 0
	for s in slots:
		if s and s.def.id == id:
			n += s.qty
	return n


func has_item(id: StringName) -> bool:
	return count(id) > 0


func slot_of(id: StringName) -> int:
	for i in SLOT_COUNT:
		if slots[i] and slots[i].def.id == id:
			return i
	return -1


func space_for(def: ItemDef) -> int:
	return maxi(0, def.carry_cap - count(def.id))


## What picking up `stack` would do, without changing anything.
## {taken, slot, full (carry cap reached), blocked (no slot free)}
func preview(stack: ItemStack) -> Dictionary:
	var result := {"taken": 0, "slot": -1, "full": false, "blocked": false}
	var def := stack.def
	if space_for(def) <= 0:
		result.full = true
		return result
	if def.is_weapon():
		var empty := _first_empty(def)
		if empty < 0:
			result.blocked = true
		else:
			result.taken = 1
			result.slot = empty
		return result
	var want := mini(stack.qty, space_for(def))
	var room := 0
	for i in SLOT_COUNT:
		var s := slots[i]
		if s and s.def == def and s.qty < def.stack_max:
			room += def.stack_max - s.qty
			if result.slot < 0:
				result.slot = i
		elif s == null and def.fits_slot(i):
			room += def.stack_max
			if result.slot < 0:
				result.slot = i
	result.taken = mini(want, room)
	result.blocked = result.taken == 0
	return result


func _first_empty(def: ItemDef) -> int:
	for i in SLOT_COUNT:
		if slots[i] == null and def.fits_slot(i):
			return i
	return -1


# ---------------------------------------------------------------- changes

## Takes as much of `stack` as the rules allow; `stack.qty` is reduced by the
## amount taken, which is returned. Never replaces an occupied slot.
func add(stack: ItemStack) -> int:
	var def := stack.def
	var take := mini(stack.qty, space_for(def))
	if take <= 0:
		return 0
	var placed := 0
	if def.is_weapon():
		var empty := _first_empty(def)
		if empty < 0:
			return 0
		slots[empty] = ItemStack.new(def, 1, stack.mag)
		placed = 1
	else:
		for i in SLOT_COUNT:
			var s := slots[i]
			if placed < take and s and s.def == def and s.qty < def.stack_max:
				var add_n := mini(take - placed, def.stack_max - s.qty)
				s.qty += add_n
				placed += add_n
		for i in SLOT_COUNT:
			if placed < take and slots[i] == null and def.fits_slot(i):
				var add_n := mini(take - placed, def.stack_max)
				slots[i] = ItemStack.new(def, add_n)
				placed += add_n
	stack.qty -= placed
	if placed > 0:
		changed.emit()
	return placed


## Puts `stack` into slot `index`, returning whatever was there (or null).
## Respects slot eligibility and the carry cap; `stack.qty` is reduced by the
## amount placed. Returns null and changes nothing if the slot can't take it.
func replace(index: int, stack: ItemStack) -> ItemStack:
	var def := stack.def
	if not def.fits_slot(index):
		return null
	var old := slots[index]
	var space_after := def.carry_cap - count(def.id) + (old.qty if old and old.def == def else 0)
	var take := 1 if def.is_weapon() else mini(mini(stack.qty, def.stack_max), space_after)
	if take <= 0:
		return null
	slots[index] = ItemStack.new(def, take, stack.mag)
	stack.qty -= take
	changed.emit()
	return old


## Removes and returns the whole stack in `index`.
func remove(index: int) -> ItemStack:
	var old := slots[index]
	slots[index] = null
	if old:
		changed.emit()
	return old


## Uses up `n` of the item in `index`; clears the slot when it runs out.
func consume(index: int, n := 1) -> void:
	var s := slots[index]
	if s == null:
		return
	s.qty -= n
	if s.qty <= 0:
		slots[index] = null
	changed.emit()


## Moves half a stack into the first empty item slot.
func split(index: int) -> bool:
	var s := slots[index]
	if s == null or s.qty < 2:
		return false
	var empty := _first_empty(s.def)
	if empty < 0:
		return false
	var half := s.qty / 2
	s.qty -= half
	slots[empty] = ItemStack.new(s.def, half)
	changed.emit()
	return true


## Swaps two slots if both items stay eligible where they land.
func swap(a: int, b: int) -> bool:
	var sa := slots[a]
	var sb := slots[b]
	if (sa and not sa.def.fits_slot(b)) or (sb and not sb.def.fits_slot(a)):
		return false
	slots[a] = sb
	slots[b] = sa
	if selected == a:
		selected = b
	elif selected == b:
		selected = a
	changed.emit()
	return true


func select(index: int) -> void:
	index = clampi(index, 0, SLOT_COUNT - 1)
	if index != selected:
		selected = index
		selected_changed.emit(index)


func clear() -> void:
	for i in SLOT_COUNT:
		slots[i] = null
	ammo.clear()
	selected = 0
	changed.emit()


# ---------------------------------------------------------------- ammunition

func ammo_count(type: StringName) -> int:
	return int(ammo.get(type, 0))


## Adds up to the reserve cap; returns how much was taken.
func add_ammo(type: StringName, n: int) -> int:
	var cap := AmmoTypes.cap(type)
	var take := clampi(n, 0, cap - ammo_count(type))
	ammo[type] = ammo_count(type) + take
	if take > 0:
		changed.emit()
	return take


## Removes up to `n` from the reserve; returns how much was removed.
func take_ammo(type: StringName, n: int) -> int:
	var take := mini(n, ammo_count(type))
	ammo[type] = ammo_count(type) - take
	if take > 0:
		changed.emit()
	return take
