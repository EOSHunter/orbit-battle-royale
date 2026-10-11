# Orbit Royale build plan

The working plan from today's state to a full local match, then online play. It breaks the milestones in [claude-handoff.md](claude-handoff.md) into tasks we can tick off. Each phase lists the decisions it needs first, the work, and how we know it is done. Sizes are relative effort (S, M, L, XL), not dates.

Last updated: 2026-10-11.

## Where we are

| Area | State |
|---|---|
| Concept and rules | Game concept, design system v0.1, roadmap |
| Design system | Tokens, 15 components and brand book, published as a Design System page |
| UI prototype | Clickable HTML prototype of every screen, including damage and healing feedback |
| Asset Hub | 77 tracked assets, 48 with concept art, 3D model and audio previews |
| Concept art | 48 v0.2 concepts in `codex/concepts/v0.2/` |
| Game | Godot 4.7 movement and Tethercaster playground, 19 passing headless checks, runs in the browser |

Nothing is tuned or production-ready yet. Every balance number is a starting point.

## How we work

- **One phase at a time,** each ending in something playable in the browser.
- **Decisions before building:** each phase starts by settling its open decisions, then records them in [claude-handoff.md](claude-handoff.md).
- **Tests grow with the game:** every system gets headless checks in `game/tests/`, run before each merge.
- **Data apart from code:** balance values live in Godot resources (like `MoveTuning`) so they can be tuned without code changes.
- **Assets flow through the Asset Hub:** concept → Blender source in `assets/source/` → `.glb` in `assets/models/` → preview attached in the hub → imported into Godot.
- **Branch per phase,** merged to `main` when its exit checks pass.

---

## Phase 0 · Lock the foundations (S–M)

Settle what everything else depends on, and make every build tested and downloadable.

**Decisions**
- [x] Combat camera: **first-person** (decided 2026-10-11). Vehicles third-person as proposed.
- [x] Browsers: **latest Chrome, Edge and Firefox** (decided 2026-10-11).
- [ ] Target hardware and frame-rate goal, e.g. "a 2020 mid-range laptop with integrated graphics, 60 fps at 1080p on Medium."
- [ ] Download budget for first play (e.g. under 60 MB compressed, game playable before the full map streams in).
- [ ] Confirm Godot 4 after this phase's measurements.

**Work**
- [x] Playtest the movement playground and lock first-pass `MoveTuning` values (2026-10-11).
- [x] Measure a baseline: see [performance-baseline.md](performance-baseline.md). Re-run on the target hardware once chosen.
- [x] Continuous integration on GitHub Actions: headless tests and web export on every push that touches `game/`, with the build kept as a downloadable artifact for 14 days.
- [x] First CI runs pass on GitHub (53 s: tests and web export).
- [x] Repo conventions: `game/assets/` and `art/` layout, Git LFS rules, naming and export settings in [asset-pipeline.md](asset-pipeline.md).

**Done when** the decisions are recorded, every push is tested and produces a downloadable build, and we have measured numbers to hold later phases against.

**Hosting (decided, later):** the game will be published at `orbitroyale.r7orbit.io`, a subdomain of r7orbit.io, once it is ready to launch. Until then, builds stay private: play them locally or download them from CI. The host will need to serve `.wasm` as `application/wasm` and compress it with Brotli or gzip. The single-threaded export needs no cross-origin isolation headers.

---

## Phase 1 · Combat and inventory slice (L) · in progress

The first real firefight: two weapons, health and shields, healing, the 5-slot inventory, and a few simple bots, all in greybox.

**Decisions**
- [x] Flexible slots 3–5 hold items only (assumed for Phase 1 per the design system; revisit after playtests).
- [x] Hitscan for the AR-7 and SG-4 (assumed for Phase 1). No headshot multiplier yet.
- [ ] Storm damage bypassing shields (proposed): confirm for later phases.

**Work**
- [x] Weapon framework: weapon data resources (damage, fire rate, magazine, reserve type, spread, recoil, reload time), with placeholder values clearly marked.
- [x] AR-7 Wayfarer and SG-4 Breaker with placeholder models, muzzle flash, tracers, impacts, hit markers.
- [x] Health and shields: shields absorb damage first, readable damage feedback, plus the directional damage arc and edge glow designed in the prototype.
- [x] Healing: Field Patch and Shield Pack with use time, slow walk while using, interruption by damage, firing or grappling, and the item kept on interruption.
- [x] 5-slot inventory with the prototype's rules: slot eligibility, stack and carry caps, matching pickups fill stacks first, replace with preview, move, split, drop, all without dragging.
- [x] Ground loot: pickups with interact prompts, auto-pickup that never replaces an occupied slot.
- [x] Separate ammunition reserves shown next to the weapon.
- [x] The Tethercaster becomes a slot item instead of always equipped.
- [x] Bots v1: wander, spot, engage, take cover, heal, with believable mistakes and no wallhacks.
- [x] In-game HUD ported from the prototype: meters, slot strip, ammo, crosshair, damage feedback.
- [x] Headless tests for inventory rules (no duplication or cap bypass), damage order, and heal interruption.

**Done when** you can loot, fight two or three bots, heal under pressure and win or lose a firefight in the browser, and the inventory tests prove no duplication or cap bypass.

**Status (2026-10-11):** first pass built and tested headless (65 checks across three suites). Next: a hands-on playtest to tune weapon feel, bot difficulty and healing times. Healing items in the slice: Field Patch, Shield Cell, Shield Pack.

---

## Phase 2 · Game UI in Godot (M)

Bring the prototype's screens into the game so the flow is real, not mocked.

**Work**
- [ ] Godot UI theme generated from the design tokens: colors, spacing, radii, focus ring, button states.
- [ ] Fonts bundled after a specimen comparison and license check.
- [ ] Custom web loading page: real download progress, Prepare → Ready stages, a Retry after a failed download.
- [ ] Main menu, lobby, settings, pause and results built from the prototype layouts.
- [ ] Settings that persist: all six categories, starting with sensitivity, FOV, volume, HUD scale, reduce motion, damage indicator options.
- [ ] Key and button rebinding with conflict resolution, and prompts that follow the device in use.
- [ ] One input-focus and overlay manager: gameplay input never leaks into menus, Back closes one layer.
- [ ] Controller navigation across every screen.

**Done when** the browser build goes loading → menu → lobby → playground or firefight → pause → settings and back, entirely by keyboard, mouse or controller, with settings that survive a reload.

---

## Phase 3 · Visual slice (L–XL)

One small corner of Ringfall at target quality, to prove the art direction and the browser performance budget together.

**Decisions**
- [ ] Which area: Glass Basin and its shoreline is a strong candidate (crater lake, black glass, rings overhead).
- [ ] Art style lock from the concepts: what we keep, and the map drift to fix (no volcano, no palm trees).
- [ ] Logo direction (versions 1 and 3 of the exploration fit best), so vector masters can be drawn.

**Work**
- [ ] Art pipeline guide: Blender scale (1 unit = 1 m), glTF export settings, collision naming, LODs, texture sizes, compression.
- [ ] Ringed sky dome shader: rings, planet and moon, fixed lighting matched to the key art.
- [ ] Terrain for the slice area with basalt, grassland, black glass and sand materials, plus a water shader.
- [ ] Luminous vegetation and a colony structure kit, with first instanced props.
- [ ] Operator model, rigged, with the locomotion set.
- [ ] Production AR-7, SG-4, Tethercaster, Field Patch and Shield Pack models and icons.
- [ ] First audio: footsteps, weapon fire, Tethercaster, healing, ambience.
- [ ] Performance pass against the Phase 0 budget, with quality presets.
- [ ] Vector logo masters and the final wordmark in the menus.

**Done when** the slice looks and sounds like the key art at the target frame rate on the target machine.

---

## Phase 4 · Full match loop (L)

A complete round from drop to results, on a small map with fewer bots.

**Decisions**
- [ ] Drop transport name, flight path rules and jump window.
- [ ] Descent device: glider, thruster pack, parachute, or none.
- [ ] Storm phases and timings for a 15–18 minute match, scaled down for the small map first.
- [ ] Pause behavior in solo bot mode: match continues (as prototyped) or freezes.

**Work**
- [ ] Drop transport: model, flight across the map, jump out, freefall, descent device, landing.
- [ ] Ion storm: shrinking safe zones, visible wall, storm damage, minimap and full map.
- [ ] Map screen with markers, and the compass.
- [ ] Elimination, spectating the eliminating bot (optional), results with placement and stats.
- [ ] Match flow: lobby → deploy → match → results → play again or return to lobby.
- [ ] Twenty or so bots that loot, rotate with the storm and fight each other.

**Done when** a whole round plays out start to finish in the browser and ends in correct results.

---

## Phase 5 · Equipment and rotation (XL)

The rest of the arsenal and all the vehicles.

**Work**
- [ ] P-12 Spark, S-9 Wisp and SR-8 Longview, with a scope view for the Longview.
- [ ] Shield Cell, Shield Core, Trauma Kit and Phoenix Capsule.
- [ ] Fragmentation, Arc and Veil grenades with throw arcs.
- [ ] Mule, Skimmer and Strider: driving, seats, enter and exit, damage, audible approach.
- [ ] Kestrel: unarmed flight with ceiling, energy, safe exits and destruction rules (decisions first).
- [ ] Tethercaster and vehicle interaction rules.
- [ ] Bots that use vehicles, heals and grenades sensibly.

**Done when** every weapon, item and vehicle has a distinct role in playtests and the stack rules still hold.

---

## Phase 6 · Full local match (XL)

The real map and all 60 combatants.

**Work**
- [ ] Full Ringfall layout: all 7 locations, routes, sightlines and escape paths.
- [ ] Streaming or chunked loading so the game is playable before the whole map downloads.
- [ ] Bot navigation across the full map, and 59 bots running within the frame budget.
- [ ] Quality presets and settings measured on the target hardware.
- [ ] Long-run stability: full matches without crashes, leaks or stalls.
- [ ] Accessibility pass: text and HUD scaling, color-independent status, reduce motion, subtitles.

**Done when** full 60-player matches run start to finish on the target machine within budget.

---

## Phase 7 · Online (XL)

Real players, with bots filling empty places. Planned separately; nothing here is decided.

**Decisions**
- [ ] Authority model: dedicated headless Godot servers (likely), WebSocket transport for browser clients.
- [ ] Hosting, regions, cost, matchmaking service.
- [ ] Disconnects, late joins, and live bot replacement.

**Work**
- [ ] Networked movement, combat and inventory with server authority and client prediction.
- [ ] Matchmaking with bot fill up to 60.
- [ ] Anti-cheat basics and server validation.
- [ ] Load testing.

**Done when** humans and bots share a match, capped at 60, with tested join, disconnect and fill behavior.

---

## Always on

- Keep [docs/asset-list.md](asset-list.md) and the Asset Hub in step as assets move from concept to engine.
- Keep the design system and the prototype as the UI reference until the Godot UI replaces them.
- Every phase ends with a playable browser build, passing tests, and an update to this plan.
