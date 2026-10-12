class_name SceneGraphics
extends RefCounted
## Applies the Graphics settings to the loaded scene: sun shadows, foliage
## density (vegetation MultiMeshes in the "foliage" group) and how far the
## camera draws. The player calls this when it spawns and whenever one of
## those settings changes.

const SHADOW_DISTANCE := {"Medium": 50.0, "High": 90.0, "Ultra": 160.0}
const FOLIAGE := {"Low": 0.3, "Medium": 0.6, "High": 1.0, "Ultra": 1.0}
const VIEW := {"Low": 900.0, "Medium": 1800.0, "High": 4000.0, "Ultra": 9000.0}


static func apply(tree: SceneTree) -> void:
	if tree == null or tree.current_scene == null:
		return
	var scene := tree.current_scene
	var shadows := GameSettings.s("shadows")
	for n in scene.find_children("*", "DirectionalLight3D", true, false):
		var light := n as DirectionalLight3D
		light.shadow_enabled = shadows != "Low"
		light.directional_shadow_max_distance = SHADOW_DISTANCE.get(shadows, 90.0)
	var density: float = FOLIAGE.get(GameSettings.s("foliage"), 1.0)
	for n in tree.get_nodes_in_group("foliage"):
		var mm := (n as MultiMeshInstance3D).multimesh
		if mm:
			mm.visible_instance_count = -1 if density >= 1.0 else int(mm.instance_count * density)
	var far: float = VIEW.get(GameSettings.s("view_distance"), 4000.0)
	for n in scene.find_children("*", "Camera3D", true, false):
		(n as Camera3D).far = far
