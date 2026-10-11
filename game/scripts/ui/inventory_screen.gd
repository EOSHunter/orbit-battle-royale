extends CanvasLayer
## Inventory screen (Tab): five slots, item details, Use/Equip, Move, Split,
## Drop, ammunition reserves, and ground items within reach with a preview of
## what picking them up would do. Replacing a slot is always explicit.
## Everything works by mouse, keyboard or controller; nothing needs dragging.
## The match keeps running while it is open.

signal closed

const ACCENT := Color("c5f277")
const TEXT := Color("f3f5fa")
const TEXT_2 := Color("b4bfd0")
const WARNING := Color("ffd18a")
const DANGER := Color("ff797f")
const NEARBY_RANGE := 3.5

var player: Player
## Where dropped items are placed in the scene.
var world_parent: Node

var _panel: Control
var _slot_buttons: Array[Button] = []
var _detail: RichTextLabel
var _mode_label: Label
var _actions: HBoxContainer
var _ammo: Label
var _nearby: VBoxContainer
var _focus_slot := 0
var _mode := ""              # "", "move", "replace"
var _move_from := -1
var _replace_pickup: Pickup


func _ready() -> void:
	layer = 20
	visible = false
	var dim := ColorRect.new()
	dim.color = Color(0.043, 0.063, 0.106, 0.86)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	_panel = MarginContainer.new()
	_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]:
		_panel.add_theme_constant_override("margin_" + side, 48)
	add_child(_panel)
	var cols := HBoxContainer.new()
	cols.add_theme_constant_override("separation", 48)
	_panel.add_child(cols)

	var left := VBoxContainer.new()
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.add_theme_constant_override("separation", 18)
	cols.add_child(left)
	left.add_child(_text("Inventory", 44, TEXT))
	left.add_child(_text("The match keeps running · Tab or Esc closes", 16, TEXT_2))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	left.add_child(row)
	for i in Inventory.SLOT_COUNT:
		if i == 2:
			var gap := Control.new()
			gap.custom_minimum_size = Vector2(10, 0)
			row.add_child(gap)
		var b := Button.new()
		b.custom_minimum_size = Vector2(150, 110)
		b.toggle_mode = false
		b.add_theme_font_size_override("font_size", 16)
		b.pressed.connect(_on_slot_pressed.bind(i))
		b.focus_entered.connect(func() -> void:
			_focus_slot = i
			_refresh_detail())
		row.add_child(b)
		_slot_buttons.append(b)
	_mode_label = _text("", 17, WARNING)
	left.add_child(_mode_label)
	_detail = RichTextLabel.new()
	_detail.bbcode_enabled = true
	_detail.fit_content = true
	_detail.custom_minimum_size = Vector2(600, 120)
	_detail.add_theme_font_size_override("normal_font_size", 18)
	left.add_child(_detail)
	_actions = HBoxContainer.new()
	_actions.add_theme_constant_override("separation", 10)
	left.add_child(_actions)
	left.add_child(_text("Ammunition · carried separately, not in slots", 15, TEXT_2))
	_ammo = _text("", 20, TEXT)
	left.add_child(_ammo)

	var right := VBoxContainer.new()
	right.custom_minimum_size = Vector2(420, 0)
	right.add_theme_constant_override("separation", 10)
	cols.add_child(right)
	right.add_child(_text("On the ground · within reach", 15, TEXT_2))
	_nearby = VBoxContainer.new()
	_nearby.add_theme_constant_override("separation", 6)
	right.add_child(_nearby)


func _text(t: String, size: int, color: Color) -> Label:
	var l := Label.new()
	l.text = t
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return l


func is_open() -> bool:
	return visible


func open() -> void:
	if player == null or not player.is_alive():
		return
	visible = true
	_mode = ""
	_focus_slot = player.inventory.selected
	player.combat_input = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	player.inventory.changed.connect(_refresh)
	_refresh()
	_slot_buttons[_focus_slot].grab_focus()


func close() -> void:
	if not visible:
		return
	visible = false
	player.combat_input = true
	player.input_grace = 0.15
	if player.inventory.changed.is_connected(_refresh):
		player.inventory.changed.disconnect(_refresh)
	closed.emit()


func _input(event: InputEvent) -> void:
	# _input, not _unhandled_input: the UI would otherwise take Tab for focus moves.
	if not visible:
		return
	if event.is_action_pressed("inventory") or event.is_action_pressed("ui_cancel"):
		if _mode != "" and event.is_action_pressed("ui_cancel"):
			_set_mode("")
		else:
			close()
		get_viewport().set_input_as_handled()
		return
	var key := event as InputEventKey
	if key and key.pressed and not key.echo:
		match key.physical_keycode:
			KEY_X:
				_drop(_focus_slot)
				get_viewport().set_input_as_handled()
			KEY_S:
				_split(_focus_slot)
				get_viewport().set_input_as_handled()
			KEY_M:
				_set_mode("move")
				get_viewport().set_input_as_handled()


func _process(_delta: float) -> void:
	if visible and Engine.get_process_frames() % 15 == 0:
		_refresh_nearby()


# ---------------------------------------------------------------- render

func _refresh() -> void:
	if not visible:
		return
	var inv := player.inventory
	for i in Inventory.SLOT_COUNT:
		var s := inv.get_slot(i)
		var b := _slot_buttons[i]
		var label := "%d\n" % (i + 1)
		if s:
			label += s.def.display_name
			if s.def.is_weapon():
				label += "\n%d / %d" % [s.mag, (s.def as WeaponDef).magazine]
			elif s.def.stack_max > 1:
				label += "\n×%d" % s.qty
		else:
			label += "Weapon" if i < 2 else "Item"
			label += "\nempty"
		b.text = label
		var eligible := true
		if _mode == "replace" and _replace_pickup:
			eligible = _replace_pickup.stack.def.fits_slot(i)
		elif _mode == "move" and _move_from >= 0:
			var a := inv.get_slot(_move_from)
			eligible = (a == null or a.def.fits_slot(i)) and (s == null or s.def.fits_slot(_move_from))
		b.disabled = not eligible
		b.modulate = Color(1, 1, 1, 1) if eligible else Color(1, 1, 1, 0.4)
		b.add_theme_color_override("font_color", ACCENT if i == inv.selected else TEXT)
	var ammo_parts: Array[String] = []
	for type: StringName in AmmoTypes.TYPES:
		ammo_parts.append("%s %d / %d" % [AmmoTypes.display_name(type), inv.ammo_count(type), AmmoTypes.cap(type)])
	_ammo.text = "     ".join(ammo_parts)
	_refresh_detail()
	_refresh_nearby()


func _refresh_detail() -> void:
	var inv := player.inventory
	var s := inv.get_slot(_focus_slot)
	for c in _actions.get_children():
		c.queue_free()
	if s == null:
		_detail.text = "[color=#b4bfd0]Empty slot %d. %s[/color]" % [_focus_slot + 1, "Slots 1 and 2 hold weapons." if _focus_slot < 2 else "Slots 3 to 5 hold healing items and the Tethercaster."]
		return
	var d := s.def
	var lines: Array[String] = ["[font_size=26]%s[/font_size]" % d.display_name, "[color=#b4bfd0]%s[/color]" % d.description]
	if d is WeaponDef:
		var w := d as WeaponDef
		lines.append("Magazine %d / %d  ·  Reserve %d %s" % [s.mag, w.magazine, inv.ammo_count(w.ammo_type), AmmoTypes.display_name(w.ammo_type).to_lower()])
	elif d is HealDef:
		var h := d as HealDef
		lines.append("In this slot %d / %d  ·  Carrying %d / %d  ·  Use time %.1f s" % [s.qty, d.stack_max, inv.count(d.id), d.carry_cap, h.use_time])
	_detail.text = "\n".join(lines)
	if _mode != "":
		return
	_action("Use" if d is HealDef else "Equip", "Enter", func() -> void: _use(_focus_slot))
	_action("Move", "M", func() -> void: _set_mode("move"))
	if s.qty > 1:
		_action("Split", "S", func() -> void: _split(_focus_slot))
	_action("Drop", "X", func() -> void: _drop(_focus_slot), true)


func _action(label: String, key: String, fn: Callable, danger := false) -> void:
	var b := Button.new()
	b.text = "%s  %s" % [key, label]
	b.custom_minimum_size = Vector2(0, 44)
	b.add_theme_font_size_override("font_size", 16)
	if danger:
		b.add_theme_color_override("font_color", DANGER)
	b.pressed.connect(fn)
	_actions.add_child(b)


func _refresh_nearby() -> void:
	for c in _nearby.get_children():
		c.queue_free()
	var found := 0
	for node in get_tree().get_nodes_in_group(Pickup.GROUP):
		var p := node as Pickup
		if p.global_position.distance_to(player.global_position) > NEARBY_RANGE:
			continue
		found += 1
		var b := Button.new()
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.custom_minimum_size = Vector2(0, 56)
		b.add_theme_font_size_override("font_size", 16)
		b.text = "%s\n%s" % [p.display_name(), _preview_text(p)]
		b.pressed.connect(_on_nearby_pressed.bind(p))
		_nearby.add_child(b)
	if found == 0:
		_nearby.add_child(_text("Nothing within reach.", 16, TEXT_2))


func _preview_text(p: Pickup) -> String:
	if p.is_ammo():
		var room := AmmoTypes.cap(p.ammo_type) - player.inventory.ammo_count(p.ammo_type)
		return "Adds to the %s reserve" % AmmoTypes.display_name(p.ammo_type).to_lower() if room > 0 else "Reserve full"
	var pv := player.inventory.preview(p.stack)
	if pv.full:
		return "Carrying the maximum (%d)" % p.stack.def.carry_cap
	if pv.blocked:
		return "No free %s slot · choose one to replace" % ("weapon" if p.stack.def.is_weapon() else "item")
	var left := p.stack.qty - int(pv.taken)
	return "Goes to slot %d%s" % [int(pv.slot) + 1, " · %d stays on the ground" % left if left > 0 else ""]


# ---------------------------------------------------------------- actions

func _set_mode(mode: String) -> void:
	_mode = mode
	if mode == "move":
		_move_from = _focus_slot
		_mode_label.text = "Moving %s · choose a slot to swap with · Esc cancels" % (player.inventory.get_slot(_move_from).def.display_name if player.inventory.get_slot(_move_from) else "an empty slot")
	elif mode == "replace":
		_mode_label.text = "Replace with %s · choose a %s slot · Esc cancels" % [_replace_pickup.stack.def.display_name, "weapon" if _replace_pickup.stack.def.is_weapon() else "item"]
	else:
		_mode_label.text = ""
		_replace_pickup = null
	_refresh()


func _on_slot_pressed(i: int) -> void:
	_focus_slot = i
	if _mode == "move":
		if player.inventory.swap(_move_from, i):
			_set_mode("")
	elif _mode == "replace" and is_instance_valid(_replace_pickup):
		var old := player.inventory.replace(i, _replace_pickup.stack)
		if old:
			_drop_stack(old)
		_replace_pickup.after_replace()
		_set_mode("")
	else:
		_use(i)


func _use(i: int) -> void:
	var s := player.inventory.get_slot(i)
	if s == null:
		return
	player.inventory.select(i)
	if s.def is HealDef:
		close()
		player.start_use(i)
	else:
		close()


func _split(i: int) -> void:
	if not player.inventory.split(i):
		_mode_label.text = "Splitting needs a stack of 2 or more and an empty item slot"


func _drop(i: int) -> void:
	var s := player.inventory.remove(i)
	if s:
		_drop_stack(s)


func _drop_stack(s: ItemStack) -> void:
	var fwd := -player.global_basis.z
	fwd.y = 0.0
	Pickup.spawn_stack(world_parent, s, player.global_position + fwd.normalized() * 1.4 + Vector3(randf_range(-0.4, 0.4), 0.1, randf_range(-0.4, 0.4)))


func _on_nearby_pressed(p: Pickup) -> void:
	if not is_instance_valid(p):
		return
	if p.collect_into(player.inventory):
		_refresh()
		return
	if not p.is_ammo() and player.inventory.preview(p.stack).blocked:
		_replace_pickup = p
		_set_mode("replace")
		var first := 0 if p.stack.def.is_weapon() else 2
		_slot_buttons[first].grab_focus()
