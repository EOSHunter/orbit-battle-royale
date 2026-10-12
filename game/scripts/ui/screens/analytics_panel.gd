class_name AnalyticsPanel
extends Control
## Practice analytics / match stats, opened from the in-match menu. Layout
## from the menu designs: an 88% scrim from x 640 to the right edge (the menu
## stays visible on the left), and at 720/300 an eyebrow, a 72 px title and a
## three-column grid of 54 px numbers between rules.

var _practice := false


func _init(practice: bool) -> void:
	_practice = practice
	set_meta("overlay", true)
	theme = UIStyle.theme()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _ready() -> void:
	var scrim := ColorRect.new()
	scrim.color = Color(UIStyle.BG, 0.88)
	UIStyle.place(self, scrim, 640, 0, 0, 0)
	var an := UIStyle.vbox(28)
	UIStyle.place(self, an, 720, 300, -1, -1, 700, 0)
	an.add_child(UIStyle.eyebrow("This session" if _practice else "This match"))
	an.add_child(UIStyle.title("Practice analytics" if _practice else "Match stats", 72, 1.0))
	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 0)
	grid.add_theme_constant_override("v_separation", 0)
	var wrap := UIStyle.vbox(0)
	wrap.add_child(UIStyle.rule(UIStyle.BORDER))
	wrap.add_child(grid)
	an.add_child(wrap)
	var cells := [
		["Shots", str(MatchStats.shots)], ["Hits", str(MatchStats.hits)], ["Accuracy", "%d%%" % roundi(MatchStats.accuracy() * 100.0)],
		["Damage", str(roundi(MatchStats.damage))], ["Reloads" if _practice else "Kills", str(MatchStats.reloads if _practice else MatchStats.kills)], ["Time", MatchStats.time_text()],
	]
	for c: Array in cells:
		var cell := UIStyle.vbox(4)
		cell.custom_minimum_size = Vector2(233, 0)
		cell.add_child(UIStyle.spacer(18))
		cell.add_child(UIStyle.tracked(c[0], 15, 0.2, UIStyle.TEXT_2))
		cell.add_child(UIStyle.label(c[1], "display", 54, UIStyle.TEXT))
		cell.add_child(UIStyle.spacer(18))
		cell.add_child(UIStyle.rule(UIStyle.BORDER))
		grid.add_child(cell)
	an.add_child(UIStyle.body("Counts from this %s. A hit is a shot that damaged a %s." % ["practice session" if _practice else "match", "target" if _practice else "bot"], 16, UIStyle.TEXT_3))
	var back := UIStyle.hint_bar([["Esc", "Back"]])
	UIStyle.place(self, back, 720, -1, -1, 72)
