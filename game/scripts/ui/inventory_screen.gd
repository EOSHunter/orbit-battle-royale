extends CanvasLayer
## Inventory (Tab). Layout from the menu designs: a compact 1160 px panel
## centered over the dimmed match with "INVENTORY 2 / 5" and a close hint,
## five item cards (index, category, item art over a tint of the item's
## color, name, stat, EQUIPPED tag; the focused card gets a white border and
## an accent corner), the actions as key hints, what's on the ground within
## reach, and ammunition bars along the bottom. Replacing a slot is always
## explicit; everything works by mouse, keyboard or controller. The match
## keeps running while it's open.

signal closed

const ACCENT := UIStyle.ACCENT
const TEXT := UIStyle.TEXT
const TEXT_2 := UIStyle.TEXT_2
const TEXT_3 := UIStyle.TEXT_3
const WARNING := UIStyle.WARNING
const DANGER := UIStyle.DANGER
const NEARBY_RANGE := 3.5
const AMMO_COLORS := {&"light": Color("f3f5fa"), &"medium": Color("ffb45c"), &"shells": Color("ff8d7f"), &"heavy": Color("70d6ff")}
const AMMO_ICONS := {&"light": "ammo-light", &"medium": "ammo-medium", &"shells": "ammo-shells", &"heavy": "ammo-heavy"}

var player: Player
## Where dropped items are placed in the scene.
var world_parent: Node

var _slot_buttons: Array[Button] = []
var _cards: Array[Dictionary] = []
var _count: Label
var _detail: Label
var _mode_label: Label
var _actions: HBoxContainer
var _ammo_box: HBoxContainer
var _nearby: HBoxContainer
var _nearby_wrap: Control
var _focus_slot := 0
var _mode := ""              # "", "move", "replace"
var _move_from := -1
var _replace_pickup: Pickup


func _ready() -> void:
	layer = 20
	visible = false
	var root := UIStyle.screen_root()
	add_child(root)
	root.add_child(UIStyle.fill(Color(0.02, 0.03, 0.05, 0.55)))
	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_child(center)
	var p := PanelContainer.new()
	var sb := UIStyle.box(UIStyle.SURFACE.darkened(0.15), 4)
	sb.content_margin_left = 40
	sb.content_margin_right = 40
	sb.content_margin_top = 32
	sb.content_margin_bottom = 30
	sb.shadow_color = Color(0, 0, 0, 0.45)
	sb.shadow_size = 40
	sb.shadow_offset = Vector2(0, 30)
	p.add_theme_stylebox_override("panel", sb)
	p.custom_minimum_size.x = 1160
	center.add_child(p)
	var col := UIStyle.vbox(0)
	p.add_child(col)

	var head := UIStyle.hbox(30)
	col.add_child(head)
	head.add_child(UIStyle.title("Inventory", 64, 1.0))
	_count = UIStyle.label("", "display", 36, TEXT_2)
	_count.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	head.add_child(_count)
	var line := UIStyle.rule(UIStyle.BORDER)
	line.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	line.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	head.add_child(line)
	var close_b := Button.new()
	close_b.focus_mode = Control.FOCUS_NONE
	close_b.add_child(UIStyle.key_hint(GameSettings.key_for("inventory"), "Close"))
	close_b.custom_minimum_size = Vector2(140, 30)
	close_b.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	close_b.pressed.connect(close)
	head.add_child(close_b)

	col.add_child(UIStyle.spacer(22))
	var row := UIStyle.hbox(16)
	col.add_child(row)
	for i in Inventory.SLOT_COUNT:
		var card := _make_card(i)
		row.add_child(card.button)
		_cards.append(card)
		_slot_buttons.append(card.button)
	col.add_child(UIStyle.spacer(18))
	_actions = UIStyle.hbox(24)
	_actions.custom_minimum_size.y = 34
	col.add_child(_actions)
	_mode_label = UIStyle.tracked("", 15, 0.14, ACCENT)
	col.add_child(_mode_label)
	_detail = UIStyle.body("", 16, TEXT_2)
	col.add_child(_detail)

	_nearby_wrap = UIStyle.vbox(10)
	col.add_child(_nearby_wrap)
	_nearby_wrap.add_child(UIStyle.spacer(8))
	_nearby_wrap.add_child(UIStyle.eyebrow("On the ground  ·  within reach", TEXT_2, 14))
	_nearby = UIStyle.hbox(10)
	_nearby_wrap.add_child(_nearby)

	col.add_child(UIStyle.spacer(18))
	col.add_child(UIStyle.rule(UIStyle.BORDER))
	col.add_child(UIStyle.spacer(18))
	_ammo_box = UIStyle.hbox(0)
	col.add_child(_ammo_box)


func _make_card(i: int) -> Dictionary:
	var b := Button.new()
	b.custom_minimum_size = Vector2(203, 270)
	b.pressed.connect(_on_slot_pressed.bind(i))
	b.focus_entered.connect(func() -> void:
		_focus_slot = i
		_refresh_detail()
		_restyle_cards())
	b.focus_exited.connect(_restyle_cards)
	b.mouse_entered.connect(b.grab_focus)
	# Art area: the top of the card, tinted, with a 2 px bottom edge.
	var art := Control.new()
	art.mouse_filter = Control.MOUSE_FILTER_IGNORE
	art.clip_contents = true
	UIStyle.place(b, art, 0, 0, 0, -1, 0, 150)
	var icon := TextureRect.new()
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
	UIStyle.place(art, icon, 30, 30, 30, 10)
	var idx := UIStyle.tracked(str(i + 1), 18, 0.0, TEXT_2, true)
	UIStyle.place(b, idx, 16, 12)
	var tag := UIStyle.tracked("", 13, 0.16, TEXT_2, true)
	UIStyle.place(b, tag, -1, 15, 16)
	var plus := UIStyle.label("+", "ui", 44, TEXT_2)
	plus.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	UIStyle.place(b, plus, 0, 80, 0, -1, 0, 60)
	var name_label := UIStyle.label("", "display", 26, TEXT)
	name_label.uppercase = true
	name_label.clip_text = true
	UIStyle.place(b, name_label, 16, 162, 16, -1, 0, 32)
	var name_rule := UIStyle.rule(Color(UIStyle.BORDER, 0.9))
	UIStyle.place(b, name_rule, 16, 200, 16, -1, 0, 1)
	var stat_name := UIStyle.tracked("", 14, 0.14, TEXT_2)
	UIStyle.place(b, stat_name, 16, 210)
	var stat := UIStyle.label("", "display", 30, TEXT)
	UIStyle.place(b, stat, 16, 226)
	var eq := UIStyle.panel(ACCENT, 0, Color(0, 0, 0, 0), 2)
	var eqm := MarginContainer.new()
	for side: Array in [["left", 8], ["right", 8], ["top", 4], ["bottom", 4]]:
		eqm.add_theme_constant_override("margin_" + side[0], side[1])
	eqm.add_child(UIStyle.tracked("Equipped", 12, 0.14, UIStyle.ON_ACCENT, true))
	eq.add_child(eqm)
	eq.mouse_filter = Control.MOUSE_FILTER_IGNORE
	UIStyle.place(b, eq, -1, -1, 16, 16)
	art.draw.connect(func() -> void: _draw_art(i, art))
	b.draw.connect(func() -> void: _draw_corner(b))
	return {"button": b, "art": art, "tag": tag, "icon": icon, "plus": plus, "name": name_label, "name_rule": name_rule, "stat_name": stat_name, "stat": stat, "equipped": eq}


## Tint behind the item art in the item's color, with a 2 px edge.
func _draw_art(i: int, art: Control) -> void:
	if player == null:
		return
	var s := player.inventory.get_slot(i)
	if s == null:
		return
	var tint: Color = s.def.color
	var sz := art.size
	var c := Vector2(sz.x * 0.5, sz.y * 0.6)
	for r in range(10, 0, -1):
		var k := r / 10.0
		art.draw_circle(c, sz.x * 0.62 * k, Color(tint, 0.06 + 0.05 * (1.0 - k)))
	art.draw_rect(Rect2(0, sz.y - 2, sz.x, 2), Color(tint, 0.9))


## The focused card's accent corner.
func _draw_corner(b: Button) -> void:
	if not b.has_focus():
		return
	var w := b.size.x
	b.draw_colored_polygon(PackedVector2Array([Vector2(w - 22, 0), Vector2(w, 0), Vector2(w, 22)]), ACCENT)


func _restyle_cards() -> void:
	if player == null:
		return
	for i in _cards.size():
		var card: Dictionary = _cards[i]
		var b: Button = card.button
		var s := player.inventory.get_slot(i)
		var focused := b.has_focus()
		var sb := UIStyle.box(UIStyle.SURFACE if s else Color(0, 0, 0, 0))
		sb.border_color = TEXT if focused else Color(UIStyle.BORDER, 0.8 if s else 0.9)
		sb.set_border_width_all(2 if focused else 1)
		for st in ["normal", "hover", "focus", "pressed", "disabled"]:
			b.add_theme_stylebox_override(st, sb)
		(card.art as Control).queue_redraw()
		b.queue_redraw()


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
	var filled := 0
	for i in Inventory.SLOT_COUNT:
		var s := inv.get_slot(i)
		var card: Dictionary = _cards[i]
		var b: Button = card.button
		if s:
			filled += 1
		var icon_path := UIStyle.item_icon(s.def.id) if s else ""
		(card.icon as TextureRect).texture = load(icon_path) if icon_path != "" else null
		(card.plus as Label).visible = s == null
		var name_l := card.name as Label
		name_l.text = s.def.display_name if s else "Empty"
		name_l.add_theme_font_override("font", UIStyle.font("display") if s else UIStyle.tracked_font(18, 0.16))
		# Shrink long names to fit the card.
		var fs := 26 if s else 18
		while s and fs > 16 and UIStyle.font("display").get_string_size(name_l.text.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > 171.0:
			fs -= 1
		name_l.add_theme_font_size_override("font_size", fs)
		name_l.add_theme_color_override("font_color", TEXT if s else TEXT_2)
		(card.name_rule as Control).visible = s != null
		var tag := card.tag as Label
		tag.text = ("Weapon" if s.def.is_weapon() else "Item") if s else ""
		tag.add_theme_color_override("font_color", s.def.color.lightened(0.2) if s else TEXT_2)
		var stat_name := ""
		var stat := ""
		if s and s.def is WeaponDef:
			stat_name = "Damage"
			stat = str(roundi((s.def as WeaponDef).damage_at(0.0)))
		elif s and s.def.stack_max > 1:
			stat_name = "Carrying"
			stat = "×%d" % s.qty
		(card.stat_name as Label).text = stat_name
		(card.stat as Label).text = stat
		(card.equipped as Control).visible = s != null and i == inv.selected
		var eligible := true
		if _mode == "replace" and _replace_pickup:
			eligible = _replace_pickup.stack.def.fits_slot(i)
		elif _mode == "move" and _move_from >= 0:
			var a := inv.get_slot(_move_from)
			eligible = (a == null or a.def.fits_slot(i)) and (s == null or s.def.fits_slot(_move_from))
		b.disabled = not eligible
		b.modulate = Color(1, 1, 1, 1) if eligible else Color(1, 1, 1, 0.45)
	_restyle_cards()
	_count.text = "%d / %d" % [filled, Inventory.SLOT_COUNT]
	_build_ammo()
	_refresh_detail()
	_refresh_nearby()


## Four ammunition columns split by rules: icon, name, count / cap, 6 px bar.
func _build_ammo() -> void:
	var inv := player.inventory
	for c in _ammo_box.get_children():
		c.queue_free()
	var first := true
	for type: StringName in AmmoTypes.TYPES:
		if not first:
			_ammo_box.add_child(UIStyle.rule(UIStyle.BORDER, true))
		var cell := MarginContainer.new()
		cell.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		cell.add_theme_constant_override("margin_left", 0 if first else 22)
		cell.add_theme_constant_override("margin_right", 22)
		first = false
		var h := UIStyle.hbox(16)
		cell.add_child(h)
		var ic := TextureRect.new()
		ic.texture = load("res://assets/ui/brand-and-ui/item-and-weapon-icons/%s.svg" % AMMO_ICONS.get(type, "ammo-medium"))
		ic.custom_minimum_size = Vector2(30, 34)
		ic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		ic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		ic.modulate = AMMO_COLORS.get(type, TEXT)
		h.add_child(ic)
		var v := UIStyle.vbox(6)
		v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		h.add_child(v)
		var top := UIStyle.hbox(0)
		top.add_child(UIStyle.tracked(AmmoTypes.display_name(type), 15, 0.14, TEXT))
		top.add_child(UIStyle.expander(false))
		top.add_child(UIStyle.label(str(inv.ammo_count(type)), "label_bold", 15, TEXT))
		top.add_child(UIStyle.label(" / %d" % AmmoTypes.cap(type), "label", 15, TEXT_2))
		v.add_child(top)
		var bar := Control.new()
		bar.custom_minimum_size.y = 6
		var frac := float(inv.ammo_count(type)) / maxf(1.0, AmmoTypes.cap(type))
		var color: Color = AMMO_COLORS.get(type, TEXT)
		bar.draw.connect(func() -> void:
			bar.draw_rect(Rect2(Vector2.ZERO, bar.size), Color(1, 1, 1, 0.1))
			bar.draw_rect(Rect2(Vector2.ZERO, Vector2(bar.size.x * frac, bar.size.y)), color))
		v.add_child(bar)
		_ammo_box.add_child(cell)


func _refresh_detail() -> void:
	var inv := player.inventory
	var s := inv.get_slot(_focus_slot)
	for c in _actions.get_children():
		c.queue_free()
	if s == null:
		_detail.text = "Empty slot %d. %s" % [_focus_slot + 1, "Slots 1 and 2 hold weapons." if _focus_slot < 2 else "Slots 3 to 5 hold healing items and the Tethercaster."]
		return
	var d := s.def
	var extra := ""
	if d is WeaponDef:
		var w := d as WeaponDef
		extra = "  Magazine %d / %d · reserve %d %s." % [s.mag, w.magazine, inv.ammo_count(w.ammo_type), AmmoTypes.display_name(w.ammo_type).to_lower()]
	elif d is HealDef:
		var h := d as HealDef
		extra = "  Carrying %d / %d · use time %.1f s." % [inv.count(d.id), d.carry_cap, h.use_time]
	_detail.text = d.description + extra
	if _mode != "":
		return
	_action("Use" if d is HealDef else "Equip", "Enter", func() -> void: _use(_focus_slot))
	_action("Move", "M", func() -> void: _set_mode("move"))
	if s.qty > 1:
		_action("Split", "S", func() -> void: _split(_focus_slot))
	_action("Drop", "X", func() -> void: _drop(_focus_slot), true)


## An action as a keycap hint you can also click ("[M] MOVE"), with 1 px
## rules between actions.
func _action(label: String, key: String, fn: Callable, danger := false) -> void:
	if _actions.get_child_count() > 0:
		_actions.add_child(UIStyle.rule(UIStyle.BORDER, true, 26))
	var b := Button.new()
	b.focus_mode = Control.FOCUS_NONE
	b.add_child(UIStyle.key_hint(key, label, false, DANGER if danger else TEXT, 15))
	b.custom_minimum_size = Vector2(44 + label.length() * 14 + key.length() * 10, 34)
	b.pressed.connect(fn)
	_actions.add_child(b)


func _refresh_nearby() -> void:
	for c in _nearby.get_children():
		c.queue_free()
	var found := 0
	for node in get_tree().get_nodes_in_group(Pickup.GROUP):
		var p := node as Pickup
		if p.global_position.distance_to(player.global_position) > NEARBY_RANGE or found >= 4:
			continue
		found += 1
		var b := UIStyle.outline_button("", TEXT, 0)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.custom_minimum_size = Vector2(250, 56)
		b.add_theme_font_override("font", UIStyle.font("ui_bold"))
		b.add_theme_font_size_override("font_size", 14)
		b.text = "%s\n%s" % [p.display_name(), _preview_text(p)]
		b.pressed.connect(_on_nearby_pressed.bind(p))
		_nearby.add_child(b)
	_nearby_wrap.visible = found > 0


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
