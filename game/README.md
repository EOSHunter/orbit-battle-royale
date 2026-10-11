# Orbit Royale: Godot project

Godot 4.7 (GL Compatibility renderer, so it exports to the web). Two greybox scenes so far: a combat slice with looting, two weapons, healing and three bots, and a movement playground for tuning traversal and the Tethercaster.

## Open and play

1. Open `game/project.godot` in Godot 4.7.2 and press Play (F5), or
2. Export for the web and serve it locally:

```bash
godot --headless --path game --export-release "Web" build/web/index.html
node prototype/serve.js game/build/web 5175
```

Then open http://localhost:5175 and click to play. The web export is single-threaded, so it needs no special server headers.

## Scenes

- **Combat arena** (`scenes/arena.tscn`, the main scene): find a weapon on the ground and fight three bots. F5 restarts, F10 switches to the playground.
- **Movement playground** (`scenes/playground.tscn`): the traversal course for tuning movement and the Tethercaster.

## Controls

| Action | Keyboard and mouse | Controller |
|---|---|---|
| Move / look | WASD / mouse | Left stick / right stick |
| Sprint, crouch, jump | Shift, C or Ctrl, Space | L3, B, A |
| Fire, aim down sights | Left click, right click | RT, LT |
| Reload | R | X |
| Pick up | E or F | Y |
| Switch slot | 1–5, mouse wheel | LB / RB |
| Inventory | Tab or I | View |
| Fire or release the Tethercaster | Q from any slot, or click with it selected | R3 |
| Release with a boost / swing without reeling | Jump / hold crouch while tethered | A / hold B |
| Restart round (arena) or respawn (playground) | F5 | D-pad down |
| Switch arena and playground | F10 | — |
| Teleport in the playground | F6–F9 | — |
| Tuning panel (playground), performance readout, controls help (arena) | F1, F3, H | Start |

Inventory screen: Enter uses or equips, M moves (then pick a slot to swap with), S splits a stack, X drops. Ground items within reach show what picking them up would do; when your slots are full, pick one to replace.

## The course

- **Speed lane** with 10 m markers, **steps** of 0.5–2 m, and **ramps** at 20°, 35° and 50° (the controller climbs up to 46°).
- **Tower field** at 10, 20, 30 and 50 m: hook them for pulls and jump off for no-fall-damage drops.
- **Hook eligibility:** glass blocks the tether; surfaces with lime stripes take it.
- **Swing gap:** two cliffs 35 m apart under a hookable beam.
- **Overhang** to hook from below, and a **range test** with walls at 40 m (in range) and 65 m (out of range).

## How it is built

| Path | What |
|---|---|
| `scripts/player.gd` | First-person controller: movement, slots, firing, healing with use time and interruption, looting, death |
| `scripts/combat/` | Inventory rules, health and shields, weapon controller, hitscan, pickups, bots, placeholder effects and viewmodels |
| `scripts/items/`, `data/items/` | Item definitions; every weapon and healing number lives in the `.tres` files |
| `scripts/ui/` | Combat HUD (damage arcs and edge glows, healing ring, meters, slots) and the inventory screen |
| `scripts/arena.gd` | Combat slice flow: loot, bots, feed, win and lose |
| `scripts/tethercaster.gd` | Aim, hook eligibility, attach and release, recharge, cable visual |
| `scripts/move_tuning.gd` | Every movement and grapple number in one resource; F1 edits it live |
| `scripts/hud.gd` | Crosshair eligibility, speed and state, landing readout, charge bar, tuning panel |
| `scripts/controls.gd` | Default keyboard, mouse and controller bindings (autoload) |
| `scripts/perf.gd` | F3 frame-time readout and the scripted benchmark (autoload); see [performance-baseline.md](../docs/performance-baseline.md) |
| `tools/build_scenes.gd` | Generates `scenes/player.tscn` and `scenes/playground.tscn` from code |
| `tests/` | Headless checks: movement (19), inventory and health rules (27), combat in the arena (19) |

Physics layers: 1 `world` (blocks the tether), 2 `grappable` (takes the tether), 3 `player`. Anything in the `no_grapple` group refuses the tether even on layer 2.

After changing the course or player structure, rebuild the scenes and run the checks:

```bash
godot --headless --path game -s res://tools/build_scenes.gd
godot --headless --path game -s res://tests/movement_test.gd
godot --headless --path game -s res://tests/inventory_test.gd
godot --headless --path game -s res://tests/combat_test.gd
```

## Not decided yet

Every number in `MoveTuning` is a starting point for playtesting. Tether range (45 m), recharge (3 s), reel speed and the swing feel all need hands-on tuning. Combat camera (first-person is assumed here), vehicle attachment for the Tethercaster, and drop behavior are still open, as listed in [docs/claude-handoff.md](../docs/claude-handoff.md).
