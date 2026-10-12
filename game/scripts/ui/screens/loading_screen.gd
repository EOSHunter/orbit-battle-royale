class_name LoadingScreen
extends Control
## Loading screen. Layout from the menu designs: full-bleed key art, the
## wordmark at the top left, the mode eyebrow, a 116 px title and the load
## phase at the bottom left over a 3 px progress bar with the percentage, and
## a rotating tip at the bottom right. LoadingScreen.go() switches here and
## loads the target scene in the background.

const SCENE := "res://scenes/loading.tscn"
const MIN_TIME := 1.6
## [[keys or "@action"], name, text]
const TIPS := [
	[["@sprint"], "Sprint", "Sprint to cover ground between fights. You can't sprint while aiming or healing."],
	[["@grapple"], "Tethercaster", "Fire the Tethercaster at high ground, then jump to let go and keep your momentum."],
	[["@inventory"], "Inventory", "Open your inventory to move, equip or drop items without leaving cover."],
	[["@reload"], "Reload", "Reload behind cover. Switching slots cancels a reload."],
	[["@fire"], "Heal out of sight", "Select a healing item and fire to use it. Sprinting, firing or switching stops it, and you keep the item."],
	[["@crouch"], "Crouch", "Crouching steadies your aim and keeps you low in Bloomwild's plants."],
]

static var _target := ""
static var _eyebrow := ""
static var _title := ""
static var _status := ""

var _bar_fill: ColorRect
var _bar: Control
var _pct: Label
var _tip_box: VBoxContainer
var _tip := 0
var _tip_time := 0.0
var _time := 0.0
var _shown := 0.0
var _requested := false
var _failed := false


## Show the loading screen and load `scene_path` behind it.
static func go(scene_path: String, eyebrow: String, title: String, status: String) -> void:
	_target = scene_path
	_eyebrow = eyebrow
	_title = title
	_status = status
	Menus.clear()
	(Engine.get_main_loop() as SceneTree).change_scene_to_file(SCENE)


func _ready() -> void:
	theme = UIStyle.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	MouseLock.release()
	add_child(UIStyle.fill(UIStyle.BG))
	add_child(UIStyle.key_art())
	add_child(UIStyle.gradient([[0.0, Color(UIStyle.BG, 0.0)], [0.52, Color(UIStyle.BG, 0.0)], [0.78, Color(UIStyle.BG, 0.78)], [1.0, Color(UIStyle.BG, 0.96)]], true))
	add_child(UIStyle.gradient([[0.0, Color(UIStyle.BG, 0.5)], [0.4, Color(UIStyle.BG, 0.0)]]))
	UIStyle.place(self, UIStyle.logo(320), 64, 48)

	var copy := UIStyle.vbox(14)
	UIStyle.place(self, copy, 64, -1, -1, 150, 1200, 0)
	copy.add_child(UIStyle.dash_eyebrow(_eyebrow if _eyebrow != "" else "Loading", UIStyle.TEXT_2, 16, 44, 1))
	copy.add_child(UIStyle.title((_title if _title != "" else "Loading.").replace("\n", " "), 116, 0.9))
	copy.add_child(UIStyle.tracked(_status if _status != "" else "Loading", 20, 0.24, UIStyle.TEXT))

	_pct = UIStyle.tracked("0%", 24, 0.0, UIStyle.ACCENT, true)
	UIStyle.place(self, _pct, -1, -1, 560, 112)
	_bar = Control.new()
	UIStyle.place(self, _bar, 64, -1, 560, 98, 0, 3)
	var back := ColorRect.new()
	back.color = Color(UIStyle.TEXT, 0.22)
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	_bar.add_child(back)
	_bar_fill = ColorRect.new()
	_bar_fill.color = UIStyle.ACCENT
	_bar_fill.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	_bar_fill.offset_right = 0
	_bar.add_child(_bar_fill)

	var learn := UIStyle.link("Learn controls", "book", 16, 0.16, true)
	learn.pressed.connect(func() -> void: Menus.push(LearnControls.new(false)))
	UIStyle.place(self, learn, 64, -1, -1, 40)

	var tip_wrap := HBoxContainer.new()
	tip_wrap.add_theme_constant_override("separation", 32)
	UIStyle.place(self, tip_wrap, -1, -1, 64, 76, 420, 0)
	tip_wrap.add_child(UIStyle.rule(Color(UIStyle.TEXT, 0.3), true))
	_tip_box = UIStyle.vbox(10)
	_tip_box.custom_minimum_size.x = 388
	tip_wrap.add_child(_tip_box)
	_tip = randi() % TIPS.size()
	_show_tip()


func _show_tip() -> void:
	for c in _tip_box.get_children():
		c.queue_free()
	var t: Array = TIPS[_tip]
	_tip_box.add_child(UIStyle.eyebrow("Tip", UIStyle.TEXT_2))
	var keys := UIStyle.hbox(10)
	for k: String in t[0]:
		keys.add_child(UIStyle.keycap(GameSettings.key_for(k.substr(1)) if k.begins_with("@") else k, 16, true))
	keys.add_child(UIStyle.tracked(t[1], 20, 0.14, UIStyle.TEXT))
	_tip_box.add_child(keys)
	_tip_box.add_child(UIStyle.body(t[2], 18, UIStyle.TEXT_2))
	var dots := UIStyle.hbox(6)
	for i in TIPS.size():
		var d := ColorRect.new()
		d.color = UIStyle.ACCENT if i == _tip else Color(UIStyle.TEXT, 0.25)
		d.custom_minimum_size = Vector2(18, 2)
		dots.add_child(d)
	_tip_box.add_child(dots)


func _process(delta: float) -> void:
	_time += delta
	_tip_time += delta
	if _tip_time > 3.2:
		_tip_time = 0.0
		_tip = (_tip + 1) % TIPS.size()
		_show_tip()
	if _target == "" or _failed:
		return
	# Let the screen draw once before loading starts.
	if not _requested:
		if _time > 0.05:
			_requested = true
			if ResourceLoader.load_threaded_request(_target) != OK:
				_fail()
		return
	var progress := []
	var status := ResourceLoader.load_threaded_get_status(_target, progress)
	var real: float = progress[0] if progress.size() > 0 else 0.0
	if status == ResourceLoader.THREAD_LOAD_FAILED or status == ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
		_fail()
		return
	# Ease toward the real progress, held under 100% for the minimum time.
	var cap := 1.0 if _time > MIN_TIME else lerpf(0.0, 0.92, _time / MIN_TIME)
	_shown = move_toward(_shown, minf(real, cap), delta * 1.5)
	_bar_fill.offset_right = _bar.size.x * _shown
	_pct.text = "%d%%" % roundi(_shown * 100.0)
	if status == ResourceLoader.THREAD_LOAD_LOADED and _shown >= 0.999:
		var scene := ResourceLoader.load_threaded_get(_target) as PackedScene
		_target = ""
		get_tree().change_scene_to_packed(scene)


func _fail() -> void:
	_failed = true
	_pct.text = "FAILED"
	_pct.add_theme_color_override("font_color", UIStyle.DANGER)
	var back := UIStyle.secondary_button("BACK TO MENU", 260)
	back.pressed.connect(func() -> void: get_tree().change_scene_to_file("res://scenes/main_menu.tscn"))
	UIStyle.place(self, back, -1, -1, 560, 140)
	back.grab_focus()
