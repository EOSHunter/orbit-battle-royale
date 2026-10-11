class_name MoveTuning
extends Resource
## Every number the movement and Tethercaster feel depends on. Kept apart from
## the code so it can be tuned live (F1 in the playground) and saved as data.
## Defaults are the first playtested pass (2026-10-11), not final balance.

@export_group("Ground")
@export_range(1.0, 15.0, 0.1, "suffix:m/s") var walk_speed := 3.6
@export_range(1.0, 20.0, 0.1, "suffix:m/s") var sprint_speed := 6.3
@export_range(0.5, 8.0, 0.1, "suffix:m/s") var crouch_speed := 3.0
@export_range(5.0, 150.0, 1.0, "suffix:m/s²") var ground_accel := 60.0
@export_range(5.0, 150.0, 1.0, "suffix:m/s²") var ground_decel := 45.0
## How quickly speed above the run limit bleeds off after landing from a swing.
@export_range(1.0, 60.0, 0.5, "suffix:m/s²") var overspeed_friction := 10.0

@export_group("Air")
@export_range(5.0, 40.0, 0.5, "suffix:m/s²") var gravity := 23.5
@export_range(2.0, 15.0, 0.1, "suffix:m/s") var jump_velocity := 7.9
@export_range(1.0, 15.0, 0.1, "suffix:m/s") var air_speed := 8.3
@export_range(1.0, 100.0, 1.0, "suffix:m/s²") var air_accel := 3.0
@export_range(0.0, 0.4, 0.01, "suffix:s") var coyote_time := 0.12
@export_range(0.0, 0.4, 0.01, "suffix:s") var jump_buffer := 0.12

@export_group("Tethercaster")
@export_range(10.0, 120.0, 1.0, "suffix:m") var grapple_range := 45.0
@export_range(0.0, 40.0, 0.5, "suffix:m/s") var reel_speed := 12.0
@export_range(0.0, 80.0, 1.0, "suffix:m/s²") var reel_accel := 28.0
@export_range(0.0, 40.0, 0.5, "suffix:m/s²") var swing_steer := 24.0
@export_range(0.5, 10.0, 0.1, "suffix:m") var min_rope := 3.0
@export_range(10.0, 80.0, 1.0, "suffix:m/s") var grapple_max_speed := 30.0
@export_range(0.0, 15.0, 0.1, "suffix:m/s") var release_boost := 9.0
@export_range(0.0, 15.0, 0.1, "suffix:s") var grapple_cooldown := 3.0

@export_group("Look")
@export_range(0.1, 3.0, 0.05) var mouse_sensitivity := 1.0
@export_range(0.5, 8.0, 0.1, "suffix:rad/s") var stick_sensitivity := 3.2
@export_range(60.0, 120.0, 1.0, "suffix:°") var fov := 110.0
