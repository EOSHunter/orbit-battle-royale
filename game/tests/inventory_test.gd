extends SceneTree
## Inventory and health rules, checked without a scene.
## Run: godot --headless --path game -s res://tests/inventory_test.gd

var failures := 0
var items := ItemCatalog


func _initialize() -> void:
	_run.call_deferred()


func _check(name: String, ok: bool, detail := "") -> void:
	if not ok:
		failures += 1
	print("%s  %s%s" % ["PASS" if ok else "FAIL", name, "  (" + detail + ")" if detail != "" else ""])


func _stack(id: StringName, qty := 1) -> ItemStack:
	return items.stack(id, qty)


func _total(inv: Inventory, ground: Array[ItemStack], id: StringName) -> int:
	var n := inv.count(id)
	for s in ground:
		if s and s.def.id == id:
			n += s.qty
	return n


func _run() -> void:

	var inv := Inventory.new()
	root.add_child(inv)

	# Slot eligibility
	inv.add(_stack(&"ar7"))
	inv.add(_stack(&"sg4"))
	_check("Weapons go to slots 1 and 2", inv.get_slot(0) and inv.get_slot(1) and inv.get_slot(0).def.id == &"ar7")
	var third := _stack(&"ar7")
	_check("A third weapon is not auto-picked into an item slot", inv.add(third) == 0 and third.qty == 1)
	_check("Preview says both weapon slots are full", inv.preview(_stack(&"ar7")).blocked)
	_check("Weapons can't be placed in slots 3–5", inv.replace(3, _stack(&"ar7")) == null and inv.get_slot(3) == null)

	# Stacking and carry caps
	var packs := _stack(&"shield_pack", 2)
	inv.add(packs)
	_check("Shield Packs go to the first item slot", inv.get_slot(2) and inv.get_slot(2).qty == 2)
	var more := _stack(&"shield_pack", 2)
	var took := inv.add(more)
	_check("Matching pickup fills the stack to the carry cap", took == 1 and inv.count(&"shield_pack") == 3 and more.qty == 1, "took %d, carrying %d, left %d" % [took, inv.count(&"shield_pack"), more.qty])
	_check("Full stack refuses more and preview says full", inv.add(_stack(&"shield_pack")) == 0 and inv.preview(_stack(&"shield_pack")).full)

	var patches := _stack(&"field_patch", 4)
	inv.add(patches)
	_check("Field Patches take the next empty item slot", inv.get_slot(3) and inv.get_slot(3).qty == 4)
	inv.add(_stack(&"tethercaster"))
	_check("Tethercaster fills the last item slot", inv.get_slot(4) and inv.get_slot(4).def.id == &"tethercaster")
	var cells := _stack(&"shield_cell", 4)
	_check("No free slot: pickup is blocked, not forced", inv.add(cells) == 0 and inv.preview(cells).blocked)

	# Explicit replace
	var ground: Array[ItemStack] = []
	var dropped := inv.replace(4, cells)
	ground.append(dropped)
	_check("Replace swaps in the new item and returns the old one", inv.get_slot(4).def.id == &"shield_cell" and dropped.def.id == &"tethercaster")
	_check("Replace takes the whole stack when it fits", inv.get_slot(4).qty == 4 and cells.qty == 0)

	# Split and caps: splitting can't exceed the carry cap
	inv.remove(3)
	_check("Split needs an empty item slot", inv.split(4) and inv.get_slot(3) and inv.get_slot(3).qty == 2 and inv.get_slot(4).qty == 2)
	var extra := _stack(&"shield_cell", 6)
	inv.add(extra)
	_check("Split stacks still respect the carry cap", inv.count(&"shield_cell") == 6, "carrying %d" % inv.count(&"shield_cell"))

	# Swaps keep eligibility
	_check("Can't swap a weapon into an item slot", not inv.swap(0, 3))
	_check("Can swap the two weapon slots", inv.swap(0, 1) and inv.get_slot(0).def.id == &"sg4")
	_check("Can swap two item slots", inv.swap(2, 4))

	# Conservation: shuffling items never creates or destroys any
	var before := _total(inv, ground, &"shield_cell")
	inv.split(2)
	inv.swap(2, 3)
	var out := inv.remove(3)
	if out:
		ground.append(out)
	for s in ground.duplicate():
		if s and s.qty > 0:
			inv.add(s)
	_check("Quantities are conserved through split, swap, drop and pickup", _total(inv, ground, &"shield_cell") == before, "%d → %d" % [before, _total(inv, ground, &"shield_cell")])

	# Ammunition reserves
	var got := inv.add_ammo(&"medium", 1000)
	_check("Ammo reserve is capped", got == AmmoTypes.cap(&"medium") and inv.ammo_count(&"medium") == AmmoTypes.cap(&"medium"))
	_check("Taking ammo can't go below zero", inv.take_ammo(&"shells", 5) == 0)

	# Health and shields
	var hp := Health.new()
	root.add_child(hp)
	hp.shield = 50.0
	hp.take_damage(30.0)
	_check("Shields absorb damage first", hp.shield == 20.0 and hp.health == 100.0)
	var broke := [false]
	hp.shield_broken.connect(func() -> void: broke[0] = true)
	hp.take_damage(50.0)
	_check("Overflow goes to health and breaks shields", hp.shield == 0.0 and hp.health == 70.0 and broke[0])
	hp.take_damage(10.0, Vector3.ZERO, null, true)
	_check("Storm-style damage can bypass shields", hp.health == 60.0)
	var patch := items.get_def(&"field_patch") as HealDef
	hp.apply_heal(patch)
	hp.apply_heal(patch)
	_check("Healing stops at the maximum", hp.health == 100.0)
	_check("A full pool refuses its healing item", not hp.can_use(patch))
	_check("Shield items still usable at full health", hp.can_use(items.get_def(&"shield_pack") as HealDef))
	var dead := [false]
	hp.died.connect(func(_a: Node) -> void: dead[0] = true)
	hp.take_damage(500.0)
	_check("Lethal damage kills once", dead[0] and not hp.alive and hp.take_damage(10.0) == 0.0)

	print("\n%s: %d failed" % ["ALL PASSED" if failures == 0 else "FAILURES", failures])
	quit(1 if failures else 0)
