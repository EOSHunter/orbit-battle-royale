# Orbit Royale: Godot project

Godot 4.7 (GL Compatibility renderer, so it exports to the web). The first milestone is the movement and Tethercaster playground: a greybox course for tuning traversal before any production art or combat.

## Open and play

1. Open `game/project.godot` in Godot 4.7.2 and press Play (F5), or
2. Export for the web and serve it locally:

```bash
godot --headless --path game --export-release "Web" build/web/index.html
node prototype/serve.js game/build/web 5175
```

Then open http://localhost:5175 and click to play. The web export is single-threaded, so it needs no special server headers.

## Controls

| Action | Keyboard and mouse | Controller |
|---|---|---|
| Move / look | WASD / mouse | Left stick / right stick |
| Sprint, crouch, jump | Shift, C or Ctrl, Space | L3, B, A |
| Fire or release the Tethercaster | Left click or Q | RT |
| Release with a boost | Jump while tethered | A while tethered |
| Swing without reeling in | Hold crouch while tethered | Hold B |
| Teleport to Spawn, Towers, Gap, Range | 1–4 | — |
| Respawn, tuning panel, performance readout | R, F1, F3 | Back, Start, — |

## The course

- **Speed lane** with 10 m markers, **steps** of 0.5–2 m, and **ramps** at 20°, 35° and 50° (the controller climbs up to 46°).
- **Tower field** at 10, 20, 30 and 50 m: hook them for pulls and jump off for no-fall-damage drops.
- **Hook eligibility:** glass blocks the tether; surfaces with lime stripes take it.
- **Swing gap:** two cliffs 35 m apart under a hookable beam.
- **Overhang** to hook from below, and a **range test** with walls at 40 m (in range) and 65 m (out of range).

## How it is built

| Path | What |
|---|---|
| `scripts/player.gd` | First-person controller: ground, air and tethered movement, crouch, landing detection |
| `scripts/tethercaster.gd` | Aim, hook eligibility, attach and release, recharge, cable visual |
| `scripts/move_tuning.gd` | Every movement and grapple number in one resource; F1 edits it live |
| `scripts/hud.gd` | Crosshair eligibility, speed and state, landing readout, charge bar, tuning panel |
| `scripts/controls.gd` | Default keyboard, mouse and controller bindings (autoload) |
| `scripts/perf.gd` | F3 frame-time readout and the scripted benchmark (autoload); see [performance-baseline.md](../docs/performance-baseline.md) |
| `tools/build_scenes.gd` | Generates `scenes/player.tscn` and `scenes/playground.tscn` from code |
| `tests/movement_test.gd` | Headless checks that drive the real scene with simulated input |

Physics layers: 1 `world` (blocks the tether), 2 `grappable` (takes the tether), 3 `player`. Anything in the `no_grapple` group refuses the tether even on layer 2.

After changing the course or player structure, rebuild the scenes and run the checks:

```bash
godot --headless --path game -s res://tools/build_scenes.gd
godot --headless --path game -s res://tests/movement_test.gd
```

## Not decided yet

Every number in `MoveTuning` is a starting point for playtesting. Tether range (45 m), recharge (3 s), reel speed and the swing feel all need hands-on tuning. Combat camera (first-person is assumed here), vehicle attachment for the Tethercaster, and drop behavior are still open, as listed in [docs/claude-handoff.md](../docs/claude-handoff.md).
