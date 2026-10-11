# HUDGroup

A cluster of live match information on a `scrim` backing so it reads over any part of Ringfall.

**Consumer provides:** values (health 0-100, shields 0-100, magazine / reserve, survivors, eliminations) and the selected weapon name.

- Placement: minimap top-left, compass top-center, survivors and eliminations top-right, health and shields bottom-left, inventory bottom-center, ammo bottom-right. Keep the aiming region clear.
- Meters are four 25-point segments with the number beside them; shield sits above health. `shield` cyan and `health` coral are only used here and on matching items.
- Low ammo turns the magazine `warning` (`is-low`) and keeps the number.
- HUD respects the HUD scale and safe-area settings; all groups move together.
