class_name UIStyle
extends RefCounted
## Orbit Royale's design system for every menu and the HUD: our color tokens
## (design-system/project/tokens.json) and fonts (Archivo for display and
## labels, IBM Plex for body text). Layout and sizes follow the menu designs
## on the same 1920×1080 canvas: huge condensed display titles, letter-spaced
## uppercase labels, 1 px rules, outlined keycaps, 56/80 px buttons, 80 px
## settings rows with a 4 px accent bar on the selected one.

# ---------------------------------------------------------------- color tokens

const BG := Color("0b101b")
const SURFACE := Color("141d2d")
const RAISED := Color("213047")
const BORDER := Color("46566d")
const BORDER_CONTROL := Color("7083a0")
const TEXT := Color("f3f5fa")
const TEXT_2 := Color("b4bfd0")
const TEXT_3 := Color("7d889b")
const ACCENT := Color("c5f277")
const ON_ACCENT := Color("0b101b")
const DANGER := Color("ff797f")
const SUCCESS := Color("8de0b0")
const WARNING := Color("ffd18a")
const HEALTH := Color("ff8d7f")
const SHIELD := Color("70d6ff")
const STORM := Color("a98bff")
## Hairlines over art: text color at low alpha.
const LINE := Color(0.953, 0.961, 0.98, 0.22)
const LINE_STRONG := Color(0.953, 0.961, 0.98, 0.4)
## Track behind sliders, switches and bars.
const TRACK := Color("2a3850")

const KEY_ART := "res://assets/ui/menu-art/key-art.jpg"
const LOGO := "res://assets/ui/brand-and-ui/orbit-logo-masters/logo-horizontal.svg"
const EMBLEM := "res://assets/ui/brand-and-ui/orbit-logo-masters/emblem.svg"

const _ARCHIVO := "res://assets/fonts/Archivo-Variable.ttf"
const _PLEX := "res://assets/fonts/IBMPlexSans-Variable.ttf"
const _PLEX_MONO := "res://assets/fonts/IBMPlexMono-SemiBold.ttf"

static var _fonts := {}
static var _theme: Theme


# ---------------------------------------------------------------- fonts

## Font roles:
## "display": heavy condensed titles (always uppercase in use).
## "heading": bold condensed headings (settings help titles, card names).
## "label" / "label_bold": the uppercase label face; prefer tracked(), which
##   sets letter spacing for the size.
## "ui" / "ui_medium" / "ui_bold": IBM Plex body text. "mono": tight numbers.
static func font(kind: String) -> Font:
	if _fonts.has(kind):
		return _fonts[kind]
	var f: FontVariation
	match kind:
		"display":
			f = _variation(_ARCHIVO, 860, 78, 0)
		"heading":
			f = _variation(_ARCHIVO, 800, 82, 0)
		"label":
			f = _variation(_ARCHIVO, 600, 88, 0)
		"label_bold":
			f = _variation(_ARCHIVO, 700, 88, 0)
		"ui_bold":
			f = _variation(_PLEX, 600, 100, 0)
		"ui_medium":
			f = _variation(_PLEX, 500, 100, 0)
		"mono":
			f = FontVariation.new()
			f.base_font = load(_PLEX_MONO)
		_:
			f = _variation(_PLEX, 420, 100, 0)
	_fonts[kind] = f
	return f


## The label face at `size` with letter spacing of `em` × size (".2em").
static func tracked_font(size: int, em: float, bold := false) -> Font:
	var key := "t%d_%d_%s" % [size, roundi(em * 100), bold]
	if _fonts.has(key):
		return _fonts[key]
	var f := _variation(_ARCHIVO, 700 if bold else 600, 88, roundi(size * em))
	_fonts[key] = f
	return f


static func _variation(path: String, weight: int, width: int, spacing: int) -> FontVariation:
	var ts := TextServerManager.get_primary_interface()
	var f := FontVariation.new()
	f.base_font = load(path)
	f.variation_opentype = {ts.name_to_tag("wght"): weight, ts.name_to_tag("wdth"): width}
	f.spacing_glyph = spacing
	return f


## Theme applied to every screen root: default font, scroll bars, text fields.
static func theme() -> Theme:
	if _theme:
		return _theme
	var t := Theme.new()
	t.default_font = font("ui")
	t.default_font_size = 18
	t.set_color("font_color", "Label", TEXT)
	for b in ["Button", "LinkButton"]:
		t.set_color("font_color", b, TEXT_2)
		t.set_color("font_hover_color", b, TEXT)
		t.set_color("font_focus_color", b, TEXT)
		t.set_color("font_pressed_color", b, TEXT)
		t.set_color("font_disabled_color", b, TEXT_3)
		t.set_font("font", b, tracked_font(16, 0.16))
		t.set_font_size("font_size", b, 16)
	var empty := StyleBoxEmpty.new()
	for s in ["normal", "hover", "pressed", "focus", "disabled"]:
		t.set_stylebox(s, "Button", empty)
	var bar := box(Color(1, 1, 1, 0.0))
	bar.content_margin_left = 3
	bar.content_margin_right = 3
	t.set_stylebox("scroll", "VScrollBar", bar)
	t.set_stylebox("grabber", "VScrollBar", box(BORDER, 2))
	t.set_stylebox("grabber_highlight", "VScrollBar", box(BORDER_CONTROL, 2))
	t.set_stylebox("grabber_pressed", "VScrollBar", box(ACCENT, 2))
	var field := box(Color(0, 0, 0, 0), 2)
	field.border_color = Color(TEXT, 0.6)
	field.set_border_width_all(1)
	field.content_margin_left = 24
	field.content_margin_right = 24
	field.content_margin_top = 20
	field.content_margin_bottom = 20
	var field_focus := field.duplicate() as StyleBoxFlat
	field_focus.border_color = TEXT
	field_focus.set_border_width_all(2)
	for c in ["LineEdit", "TextEdit"]:
		t.set_stylebox("normal", c, field)
		t.set_stylebox("focus", c, field_focus)
		t.set_stylebox("read_only", c, field)
		t.set_color("font_color", c, TEXT)
		t.set_color("font_placeholder_color", c, TEXT_3)
		t.set_color("caret_color", c, ACCENT)
		t.set_color("selection_color", c, Color(ACCENT, 0.35))
		t.set_font_size("font_size", c, 20)
	t.set_stylebox("panel", "PanelContainer", StyleBoxEmpty.new())
	_theme = t
	return t


static func box(color: Color, radius := 0) -> StyleBoxFlat:
	var b := StyleBoxFlat.new()
	b.bg_color = color
	b.set_corner_radius_all(radius)
	return b


# ---------------------------------------------------------------- text

static func label(text: String, kind := "ui", size := 18, color := TEXT) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font(kind))
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


## Uppercase letter-spaced label ("BATTLE ROYALE", "CALLSIGN").
static func tracked(text: String, size := 16, em := 0.2, color := TEXT_2, bold := false) -> Label:
	var l := Label.new()
	l.text = text
	l.uppercase = true
	l.add_theme_font_override("font", tracked_font(size, em, bold))
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


## The design's eyebrow: 16 px at .24em, muted.
static func eyebrow(text: String, color := TEXT_2, size := 16) -> Label:
	return tracked(text, size, 0.24, color)


## Eyebrow with a short leading rule ("—— BATTLE ROYALE").
static func dash_eyebrow(text: String, color := TEXT_2, size := 16, line_w := 44.0, thick := 1.0) -> HBoxContainer:
	var h := hbox(20)
	h.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var d := ColorRect.new()
	d.color = color
	d.custom_minimum_size = Vector2(line_w, thick)
	d.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	d.mouse_filter = Control.MOUSE_FILTER_IGNORE
	h.add_child(d)
	h.add_child(eyebrow(text, color, size))
	return h


## Huge condensed display title; `line` is the line-height factor.
static func title(text: String, size := 136, line := 0.88) -> Label:
	var l := label(text, "display", size, TEXT)
	l.uppercase = true
	l.add_theme_constant_override("line_spacing", roundi(size * (line - 1.18)))
	return l


## Wrapping body text.
static func body(text: String, size := 18, color := TEXT_2) -> Label:
	var l := label(text, "ui", size, color)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return l


## A 1 px rule (horizontal, or vertical with `vertical`).
static func rule(color := LINE, vertical := false, length := 0.0) -> ColorRect:
	var r := ColorRect.new()
	r.color = color
	r.custom_minimum_size = Vector2(1, length) if vertical else Vector2(length, 1)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if vertical:
		r.size_flags_vertical = Control.SIZE_SHRINK_CENTER if length > 0.0 else Control.SIZE_FILL
	return r


# ---------------------------------------------------------------- keys

## Keycap: 30 px tall at the default 16 px, outlined or solid.
static func keycap(text: String, size := 16, solid := false) -> PanelContainer:
	var h := roundi(size * 1.875)
	var p := PanelContainer.new()
	var sb := box(TEXT if solid else Color(0, 0, 0, 0), 2)
	sb.border_color = TEXT if solid else Color(TEXT, 0.55)
	sb.set_border_width_all(1)
	sb.content_margin_left = roundi(size * 0.5)
	sb.content_margin_right = roundi(size * 0.5)
	p.add_theme_stylebox_override("panel", sb)
	var l := tracked(text, size, 0.06, BG if solid else TEXT, true)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.custom_minimum_size = Vector2(h - size, h)
	p.add_child(l)
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	p.custom_minimum_size = Vector2(h, h)
	return p


## 64 px keycap for the controls guide.
static func big_key(text: String) -> PanelContainer:
	var p := PanelContainer.new()
	var sb := box(Color(BG, 0.6), 4)
	sb.border_color = Color(TEXT, 0.55)
	sb.set_border_width_all(2)
	sb.content_margin_left = 14
	sb.content_margin_right = 14
	p.add_theme_stylebox_override("panel", sb)
	var l := tracked(text, 26, 0.06, TEXT, true)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.custom_minimum_size = Vector2(36, 64)
	p.add_child(l)
	p.custom_minimum_size = Vector2(64, 64)
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return p


## "[ESC] SETTINGS": keycap, 12 px gap, 16 px label at .16em.
static func key_hint(key: String, text: String, solid := true, color := TEXT_2, size := 16) -> HBoxContainer:
	var h := hbox(12)
	h.add_child(keycap(key, size, solid))
	h.add_child(tracked(text, size, 0.16, color))
	h.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return h


## A row of key hints, 36 px apart: [["Enter", "Play"], ["Esc", "Settings"]].
## A third element `false` draws the keycap outlined instead of solid.
static func hint_bar(pairs: Array, gap := 36) -> HBoxContainer:
	var h := hbox(gap)
	for p: Array in pairs:
		h.add_child(key_hint(p[0], p[1], p[2] if p.size() > 2 else true))
	h.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return h


# ---------------------------------------------------------------- buttons

static func _button_states(b: Button, normal: StyleBox, hover: StyleBox, pressed: StyleBox, focus: StyleBox) -> void:
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", pressed)
	b.add_theme_stylebox_override("focus", focus)
	b.add_theme_stylebox_override("disabled", normal)


static func _focus_ring(base: StyleBoxFlat) -> StyleBoxFlat:
	var f := base.duplicate() as StyleBoxFlat
	f.border_color = TEXT
	f.set_border_width_all(2)
	f.expand_margin_left = 2
	f.expand_margin_right = 2
	f.expand_margin_top = 2
	f.expand_margin_bottom = 2
	return f


## Accent button: 56 px with a 20 px label, or `big` 80 px with a 44 px
## display label. An arrow sits at the right edge unless `arrow` is "".
static func primary_button(text: String, width := 330.0, big := true, arrow := "→") -> Button:
	var b := Button.new()
	b.text = text.to_upper()
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.custom_minimum_size = Vector2(width, 80 if big else 56)
	if big:
		b.add_theme_font_override("font", font("display"))
		b.add_theme_font_size_override("font_size", 44)
	else:
		b.add_theme_font_override("font", tracked_font(20, 0.14, true))
		b.add_theme_font_size_override("font_size", 20)
	for s in ["font_color", "font_hover_color", "font_focus_color", "font_pressed_color", "font_disabled_color"]:
		b.add_theme_color_override(s, ON_ACCENT)
	var normal := box(ACCENT, 2)
	normal.content_margin_left = 32 if big else 24
	normal.content_margin_right = 32 if big else 24
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = ACCENT.lightened(0.15)
	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.bg_color = ACCENT.darkened(0.1)
	_button_states(b, normal, hover, pressed, _focus_ring(hover))
	if arrow != "":
		var a := label(arrow, "ui_medium", 28, ON_ACCENT)
		a.set_anchors_and_offsets_preset(Control.PRESET_RIGHT_WIDE)
		a.offset_left = -(32 if big else 24) - 40
		a.offset_right = -(32 if big else 24)
		a.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		a.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		b.add_child(a)
		b.set_meta("arrow", a)
	return b


## Raised secondary button, 56 px.
static func secondary_button(text: String, width := 160.0) -> Button:
	var b := Button.new()
	b.text = text.to_upper()
	b.custom_minimum_size = Vector2(width, 56)
	b.add_theme_font_override("font", tracked_font(20, 0.14, true))
	b.add_theme_font_size_override("font_size", 20)
	for s in ["font_color", "font_hover_color", "font_focus_color", "font_pressed_color"]:
		b.add_theme_color_override(s, TEXT)
	var normal := box(RAISED, 2)
	normal.content_margin_left = 24
	normal.content_margin_right = 24
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = RAISED.lightened(0.08)
	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.bg_color = SURFACE
	_button_states(b, normal, hover, pressed, _focus_ring(hover))
	return b


## Solid colored button, 56 px (the red "LEAVE MATCH" in a dialog).
static func solid_button(text: String, color: Color, width := 160.0) -> Button:
	var b := secondary_button(text, width)
	for s in ["font_color", "font_hover_color", "font_focus_color", "font_pressed_color"]:
		b.add_theme_color_override(s, ON_ACCENT)
	var normal := box(color, 2)
	normal.content_margin_left = 24
	normal.content_margin_right = 24
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = color.lightened(0.12)
	_button_states(b, normal, hover, normal, _focus_ring(hover))
	return b


## Outlined button: 44 px, 1 px border, 16 px bold label (key bindings, chips).
static func outline_button(text: String, color := TEXT, width := 0.0) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(width, 44)
	b.add_theme_font_override("font", tracked_font(16, 0.08, true))
	b.add_theme_font_size_override("font_size", 16)
	for s in ["font_color", "font_hover_color", "font_focus_color", "font_pressed_color"]:
		b.add_theme_color_override(s, color)
	var normal := box(Color(0, 0, 0, 0), 2)
	normal.border_color = BORDER
	normal.set_border_width_all(1)
	normal.content_margin_left = 14
	normal.content_margin_right = 14
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = RAISED
	_button_states(b, normal, hover, hover, _focus_ring(hover))
	return b


## Large menu entry (RESUME, SETTINGS...): 36 px label face at .1em, 70%
## white, bright and nudged right with a 4 px accent bar on hover or focus.
static func menu_item(text: String, size := 36, color := Color(TEXT, 0.7)) -> Button:
	var b := Button.new()
	b.text = text
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.add_theme_font_override("font", tracked_font(size, 0.1, true))
	b.add_theme_font_size_override("font_size", size)
	b.add_theme_color_override("font_color", color)
	for s in ["font_hover_color", "font_focus_color", "font_pressed_color"]:
		b.add_theme_color_override(s, TEXT)
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(0, 0, 0, 0)
	normal.content_margin_left = 24
	normal.content_margin_top = 14
	normal.content_margin_bottom = 14
	var active := normal.duplicate() as StyleBoxFlat
	active.border_color = ACCENT
	active.border_width_left = 4
	active.content_margin_left = 30
	_button_states(b, normal, active, active, active)
	b.mouse_entered.connect(b.grab_focus)
	return b


## Uppercase link with an optional drawn icon ("⌖ FIRING RANGE").
static func link(text: String, glyph := "", size := 16, em := 0.18, underline := false) -> Button:
	var b := Button.new()
	b.text = text.to_upper()
	b.add_theme_font_override("font", tracked_font(size, em))
	b.add_theme_font_size_override("font_size", size)
	b.add_theme_color_override("font_color", TEXT)
	b.add_theme_color_override("font_hover_color", ACCENT)
	b.add_theme_color_override("font_focus_color", ACCENT)
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(0, 0, 0, 0)
	normal.content_margin_left = 36 if glyph != "" else 0
	normal.content_margin_top = 6
	normal.content_margin_bottom = 6
	if underline:
		normal.border_color = LINE_STRONG
		normal.border_width_bottom = 1
	var hover := normal.duplicate() as StyleBoxFlat
	hover.border_color = ACCENT
	hover.border_width_bottom = 1
	_button_states(b, normal, hover, hover, hover)
	if glyph != "":
		var g := Glyph.new(glyph, TEXT, 20)
		g.anchor_top = 0.5
		g.anchor_bottom = 0.5
		g.offset_top = -10
		g.offset_bottom = 10
		g.offset_right = 20
		b.add_child(g)
	b.mouse_entered.connect(b.grab_focus)
	return b


# ---------------------------------------------------------------- art and layout

## The Orbit Royale wordmark at a given width.
static func logo(width := 400.0) -> TextureRect:
	var r := TextureRect.new()
	r.texture = load(LOGO)
	r.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	r.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT
	var tex_size: Vector2 = r.texture.get_size()
	r.custom_minimum_size = Vector2(width, width * tex_size.y / tex_size.x)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r


## Full-rect key art, optionally mirrored so the operator stands on the right.
static func key_art(mirrored := false) -> TextureRect:
	var r := TextureRect.new()
	r.texture = load(KEY_ART)
	r.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	r.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	r.flip_h = mirrored
	r.set_anchors_preset(Control.PRESET_FULL_RECT)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r


## A gradient overlay. `stops` are [offset, Color] pairs; `vertical` runs top
## to bottom, otherwise left to right.
static func gradient(stops: Array, vertical := false) -> TextureRect:
	var g := Gradient.new()
	g.offsets = PackedFloat32Array(stops.map(func(s: Array) -> float: return s[0]))
	g.colors = PackedColorArray(stops.map(func(s: Array) -> Color: return s[1]))
	var tex := GradientTexture2D.new()
	tex.gradient = g
	tex.width = 8 if vertical else 512
	tex.height = 512 if vertical else 8
	tex.fill_to = Vector2(0, 1) if vertical else Vector2(1, 0)
	var r := TextureRect.new()
	r.texture = tex
	r.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	r.stretch_mode = TextureRect.STRETCH_SCALE
	r.set_anchors_preset(Control.PRESET_FULL_RECT)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r


## Solid full-rect color.
static func fill(color: Color) -> ColorRect:
	var r := ColorRect.new()
	r.color = color
	r.set_anchors_preset(Control.PRESET_FULL_RECT)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r


## A full-rect Control with the theme applied, as the root of a screen.
static func screen_root() -> Control:
	var c := Control.new()
	c.theme = theme()
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	return c


## Add `c` to `parent` at design coordinates. Give `left` and/or `right`
## (distance from that edge; -1 = unset) and `top` and/or `bottom`. With one
## edge set, `width`/`height` give the size (0 lets it size itself).
static func place(parent: Control, c: Control, left := -1.0, top := -1.0, right := -1.0, bottom := -1.0, width := 0.0, height := 0.0) -> Control:
	parent.add_child(c)
	var has_l := left >= 0.0
	var has_r := right >= 0.0
	var has_t := top >= 0.0
	var has_b := bottom >= 0.0
	c.anchor_left = 0.0 if has_l else 1.0
	c.anchor_right = 1.0 if has_r else 0.0
	c.anchor_top = 0.0 if has_t else 1.0
	c.anchor_bottom = 1.0 if has_b else 0.0
	c.grow_horizontal = Control.GROW_DIRECTION_BEGIN if (has_r and not has_l) else Control.GROW_DIRECTION_END
	c.grow_vertical = Control.GROW_DIRECTION_BEGIN if (has_b and not has_t) else Control.GROW_DIRECTION_END
	if has_l:
		c.offset_left = left
		c.offset_right = -right if has_r else left + width
	else:
		c.offset_right = -right
		c.offset_left = -right - width
	if has_t:
		c.offset_top = top
		c.offset_bottom = -bottom if has_b else top + height
	else:
		c.offset_bottom = -bottom
		c.offset_top = -bottom - height
	return c


static func safe_area(left := 64, top := 44, right := 64, bottom := 40) -> MarginContainer:
	var m := MarginContainer.new()
	m.set_anchors_preset(Control.PRESET_FULL_RECT)
	m.add_theme_constant_override("margin_left", left)
	m.add_theme_constant_override("margin_top", top)
	m.add_theme_constant_override("margin_right", right)
	m.add_theme_constant_override("margin_bottom", bottom)
	m.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return m


static func vbox(sep := 0) -> VBoxContainer:
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", sep)
	return v


static func hbox(sep := 0) -> HBoxContainer:
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", sep)
	return h


static func spacer(h := 0.0, w := 0.0) -> Control:
	var c := Control.new()
	c.custom_minimum_size = Vector2(w, h)
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return c


static func expander(vertical := true) -> Control:
	var c := Control.new()
	if vertical:
		c.size_flags_vertical = Control.SIZE_EXPAND_FILL
	else:
		c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return c


## A panel with background, optional 1 px border and padding.
static func panel(bg: Color, pad := 0, border := Color(0, 0, 0, 0), radius := 0) -> PanelContainer:
	var p := PanelContainer.new()
	var sb := box(bg, radius)
	if border.a > 0.0:
		sb.border_color = border
		sb.set_border_width_all(1)
	sb.set_content_margin_all(pad)
	p.add_theme_stylebox_override("panel", sb)
	return p


const _ITEM_ICONS := {
	&"ar7": "ar-7-wayfarer", &"sg4": "sg-4-breaker", &"p12": "p-12-spark", &"s9": "s-9-wisp", &"sr8": "sr-8-longview",
	&"field_patch": "field-patch", &"trauma_kit": "trauma-kit", &"shield_cell": "shield-cell", &"shield_pack": "shield-pack",
	&"shield_core": "shield-core", &"phoenix_capsule": "phoenix-capsule", &"tethercaster": "tethercaster",
}


## Path of the line icon for an item id ("" if there isn't one).
static func item_icon(id: StringName) -> String:
	return "res://assets/ui/brand-and-ui/item-and-weapon-icons/%s.svg" % _ITEM_ICONS[id] if _ITEM_ICONS.has(id) else ""
