# Polish plan: from prototype to a finished-looking game

The bar is the Kong Royale match recording (dontdie.wtf, 12.6 minutes, reviewed at one frame every 5 seconds). It is a browser game like ours, so everything in it is achievable on the web. We match its **quality and density**, not its style: Ringfall keeps its own sci-fi ringworld look.

Reference frames are in [references/kong-royale/](references/kong-royale/):

| File | What it shows |
|---|---|
| `map-screen.jpg` | Painted map, POI icons, flight path, legend, controls bar |
| `freefall-hud.jpg` | Freefall from the transport: compass, altitude bar, squad list, visible hands |
| `vehicle-hud.jpg` | Driving: speed, seats, hull, radio, hotbar with rarity colours |
| `settings.jpg` | Settings layout: five tabs, sliders, toggles, rebinding with alternates |
| `victory.jpg` | Results: stats, personal best, quick feedback, Back to lobby |
| `sheet-03.jpg` | Temple exterior, open field, vehicles, storm banner |
| `sheet-07.jpg` | Rock, river and bridge detail; ground textures up close |
| `sheet-09.jpg` | Plantation: crop rows, barn, water tower, loot beams, ammo spill |
| `sheet-11.jpg` | Enterable farmhouse interior, resurgence banners |
| `sheet-12.jpg` | Jungle floor density: ferns, flowers, leaf litter, trees, lightning |

## Where we are versus the reference

| Area | Kong Royale | Ringfall today |
|---|---|---|
| Ground | Every square metre has grass blades, ferns, flowers, leaf litter; textured dirt paths link every POI | Flat, untextured green; sparse tufts |
| Trees and cover | Dense canopy, several species and sizes, mossy boulders everywhere | Scattered trees in open fields; few rocks |
| Locations | Each POI has a distinct silhouette and **enterable interiors** with furniture, lights and loot | Closed boxes on grass, few props, nothing to enter |
| Textures | Tiling stone, brick, wood and leaf textures, detailed up close, carved trim | Baked 512 px atlases, flat terrain colour |
| Atmosphere | Painted clouds, lightning in the storm, drifting leaves, torches with flicker, warm sun and strong AO | Starry sky, flat lighting, no particles in the air |
| Map | Painted illustrated map with icons and roads | Heightmap render |
| Front end | Custom loading, menus, settings, results | Godot boot screen, F-key toggles |

## Step 1 · Fix the mouse (first, small)

**What is happening:** when the browser refuses pointer lock once, the game falls back for the rest of the session to a mode where the cursor is only hidden. A hidden cursor can still leave the canvas, and when it rests near an edge the "edge turn" helper keeps rotating the view, so the camera spins and stops responding.

The usual trigger: Chrome refuses a new pointer lock for about a second after Esc releases it, so clicking straight back in after Esc flips the game into the fallback permanently.

**Fix:**
- Remove the hidden-cursor fallback and the edge-turn helper entirely.
- Losing pointer lock (Esc, alt-tab, a refused request) always opens the pause menu.
- Clicking Resume asks for the lock again, retrying after the browser's cooldown instead of giving up.
- Request raw input (`unadjustedMovement`) where the browser supports it, so sensitivity matches the settings.
- Drop any single mouse movement larger than a sane limit, which browsers occasionally report when the lock is regained.

Done when you can press Esc and click back in repeatedly, alt-tab, or resize, and looking never sticks or spins.

## Step 2 · Front end and screens

Replicate the menu designs from your layout video (frames in [references/menu-design/](references/menu-design/)) screen for screen, in Godot. The look changes to ours:
- the Orbit Royale wordmark
- our key art: the operator, Ringfall, the drop transport
- our design-system colours instead of the Kong yellow

The layout, hierarchy, type scale, keyboard hints and behaviour stay as designed. One overlay manager handles every screen: gameplay input never leaks into menus, Esc always closes one layer, and every screen works by keyboard, mouse or controller.

**Shared layout rules from the designs**
- Wordmark top-left.
- A huge condensed title, such as "RULE THE RING." or "Settings".
- Small letter-spaced labels.
- A thin rule under the tabs.
- The selected row gets a left accent bar and a lighter background.
- A footer of key hints (`ENTER Play · ESC Settings`, `↑↓ Select · ←→ Adjust`).
- "✓ Saved on this device" at the bottom right of settings.

**The screens**

1. **Loading screen (replaces the Godot screen):**
   - full-bleed key art (Ringfall with the drop transport)
   - mode label ("BATTLE ROYALE · SOLO") and a big title ("THE RING AWAITS.")
   - "LOADING ISLAND" with a thin progress bar and percentage
   - a rotating drop tip on the right ("SHIFT Dive / X Deploy glider")
   - a Learn controls link
   - real download progress, and Retry if the download fails
   - Built as the custom HTML shell, so it shows before the engine starts.
2. **Main menu:**
   - top tabs: Play, Training, Settings
   - your callsign top right, with Edit callsign
   - the operator hero art on the right
   - **Play tab:** title, "BOT MATCH · RESURGENCE", Solo mode, a big Play button and status line, then links to Firing range and Learn controls
   - **Training tab:** "SHARPEN UP." with Firing range and Learn controls
   - Pressing Play shows "STARTING 0:03" in the button, with Esc to cancel, in place of the designs' "Searching", then goes to the loading screen.
3. **Firing range:**
   - a practice map with distance-marked lanes (10/30/50 m), target dummies, a tower and the weapons laid out
   - infinite ammo
   - a practice checklist on the left (fire at a target, reload, open inventory, open map, take a hit, heal)
   - damage numbers on targets
4. **Learn controls:** a 10-step guide.
   - Steps: Move, Sprint/slide/crouch, Mantle, Take a weapon, Aim and fire, Reload, Heal, Map pins, Inventory, Jump from the transport.
   - Layout: numbered list on the left with ticks, step title and description, the keys drawn as keycaps, and hero art.
   - Actions: Next / Back, Skip guide, Practice in firing range.
5. **In-match menu (Esc):**
   - "MENU" with a "• MATCH CONTINUES" label
   - items: Resume, Settings, Practice analytics (in the firing range) or Match stats, Report a problem, and Leave match with a confirmation dialog
   - the game blurs and darkens on the right
   - The menu does not pause the match.
6. **Practice analytics / match stats:** shots, hits, accuracy, damage, reloads, time.
7. **Report a problem:**
   - issue type chips (lag, hit registration, bug, visual, audio, stuck, cheater, other) and a text box
   - automatically attached: a screenshot, your position and recent logs
   - Send report
   - It saves locally until we have a backend.
8. **Settings:** five tabs with sub-tabs (Tab cycles the sub-tabs).
   - **Mouse & keyboard:** Mouse (sensitivity, aim, scope, invert), Behaviour (toggle aim, crouch and sprint, auto sprint), Bindings (primary and alternate keys).
   - **Controller:** Layout (button prompts Auto/Xbox/PlayStation/Nintendo, layout, swap sticks, vibration), Look (look and aim sensitivity, response curve, invert), Deadzones (left and right, with a live stick preview).
   - **Audio:** master, effects, music, voice and UI volumes.
   - **Video:** Display (frame rate limit, 3D resolution, dynamic resolution, FOV, show FPS, match stats), Graphics (quality preset, shadows, textures, foliage density, effects, anti-aliasing).
   - **Accessibility:** reduced camera motion, HUD scale and text scale, each with a live HUD preview.
   - A right-hand panel explains the selected row and shows a visual: mouse speed, FOV cone, response curve, deadzone circle or preset bars.
   - Restore defaults (R). Every change applies instantly and is saved in the browser.
9. **Inventory (Tab):**
   - "INVENTORY 2/5" over a widescreen strip of the scene
   - five cards with item art, name, rarity label and damage, with the equipped one marked
   - the actions Equip, Move and Drop
   - ammo reserve bars along the bottom
10. **HUD restyle to match the designs:**
    - minimap top-left with the mode label
    - compass top-centre
    - kills, damage and Resurgence status top-right
    - thin health and shield bars bottom-left
    - large ammo count, weapon name and the five slot icons bottom-right
    - "Click to capture the cursor · Esc for menu" when the mouse isn't locked
11. **Map screen (M):** illustrated top-down map, POI names, safe zone and storm, transport path, your drop marker, legend.
12. **Results:** Victory or Eliminated, with placement, kills, damage, time survived, respawns used, personal bests, and Play again or Back to menu.

## Step 3 · Map art pass (the biggest gap)

**Bloomwild first.** Bring it to final quality, check the frame rate on your PC, then roll the same treatment out island-wide. Keep the sci-fi ringworld look and make it more stylized: bolder shapes, saturated glowing plants, painterly colour variation, and strong rim and sky light.

**More realistic terrain (whole island)**
- Regenerate the heightmap with erosion simulation, so slopes get gullies, ridges, talus fans and riverbeds instead of smooth blobs.
- Use real landform features:
  - valleys cut by rivers that flow to the sea or the crater lake
  - cliff bands with rock faces
  - rolling foothills
  - plateaus for POIs
  - beaches and coves
- Double the height resolution in the playable core (1 m spacing), keeping 2 m far out.
- Rock cliff meshes and outcrops placed on steep slopes, so cliffs read as rock, not stretched ground.
- A flow and wetness map baked from the erosion pass. It decides where mud, moss, streams and lush plants go.

**Ground**
- A terrain texture set: tiling 1–2k colour, normal and roughness for grass, moss, dirt path, sand, basalt, black glass and wet rock.
- Slope-based cliffs using triplanar mapping so they don't stretch.
- A detail layer up close and a colour variation layer far away, so the ground never looks flat.
- Paths and roads painted into the splat map between every POI, readable from the air.

**Ground cover**
- GPU-instanced grass across all walkable land, with a wind shader, and fade it out by distance.
- Ferns, flowers, small glowing plants, pebbles and fallen debris scattered by biome rules: slope, height, distance to water and to paths.
- Density is set by the vegetation slider in Video settings.

**Trees, rocks and cover**
- 3–4 species per biome at several sizes, with clusters and clearings instead of an even spread.
- Mossy rock sets from pebble to cliff boulder, used as cover in every open field.
- Distant trees become cheap camera-facing billboards.

**Locations rebuilt to be entered**
- Every POI gets 2–6 buildings with real interiors:
  - doors, stairs, second floors, rooftops
  - furniture and clutter
  - interior lights
  - loot spots inside
- A modular interior kit (walls, floors, door and window frames, stairs, railings) with trim-sheet textures.
- Each POI gets a landmark visible from the transport, such as the observatory dome, the crashed hull at Anchorport, or the power core glow at Relay Nine.
- Relay Nine gets its maintenance tunnels.

**Water**
- Rivers that cut through the island, with bridges.
- Lakes with docks and boats.
- Better shoreline foam and wet sand.

**Atmosphere**
- Painted volumetric-looking clouds, lightning inside the ion storm, and drifting particles (spores, leaves, ash) in the air.
- Ambient creatures and birds in the distance.
- Light shafts, height fog, and stronger ambient occlusion so objects sit on the ground.
- Flickering lights in interiors.

**Illustrated map:** render a top-down image of the finished island and paint over it for the map screen and minimap.

## Step 4 · Model and texture quality pass

- Raise hero textures (weapons, operator, vehicles) to 1–2k. Our earlier 512 limit was a download-size choice.
- Switch to Basis Universal (KTX2) compression so higher resolution doesn't blow up the download.
- Add trim sheets and tiling materials for architecture, instead of one baked atlas per building, so large walls stay crisp up close.
- Add a stylization pass on materials: stronger edge highlights, hand-painted-looking colour variation, rim light on characters.
- Add first-person arms and hands to every viewmodel, and visible hands in freefall and gliding, as the reference shows.
- Add the Tethercaster on the wrist.

## Step 5 · Match loop

- **Drop transport:**
  - flies a random path across the map, shown on the map
  - auto-jump countdown, and Space to jump
  - place your drop marker on the map
- **Freefall:**
  - dive (Shift) and steer
  - an altitude meter and speed readout
  - deploy the descent device, glide, cut it away, and land
- **Ion storm phases:**
  - "Storm phase N" and "The storm is closing in" banners
  - a timer that shows when the storm closes or shrinks, with the players-alive count
  - storm damage
  - lightning inside the storm wall
- **Compass bar** with bearings, the safe zone direction and squad markers.
- **POI name banner** when you enter a location. The minimap shows where you are.
- **Bots that use the map:** drop with the transport, loot buildings, rotate with the storm, use cover.

## Step 6 · Resurgence (solo, with bots)

Modelled on Warzone's Resurgence, in its solo form (Rebirth Resurgence Solos). What Warzone does:
- Your first redeploy is free.
- After you redeploy you must survive a countdown before you earn another one.
- Kills and opening supply crates cut the countdown.
- The countdown only runs once you've landed.
- Early deaths come back fast, later ones slower.
- Respawning switches off for good at a later storm closure, setting up a final, every-death-counts showdown.

Exact Warzone numbers have changed patch to patch. Where sources disagree, ours below are starting values to tune.

**Our rules**
- **Respawn token:**
  - Every player and bot starts the match with one token ready ("RESURGENCE · READY").
  - Dying with a ready token is not an elimination: you redeploy.
  - Dying without one eliminates you.
- **Redeploy delay:**
  - 10 s during storm phase 1, 20 s during phase 2, 30 s during phase 3.
  - The screen shows who eliminated you, a countdown, and the map so you can watch where you'll come in.
- **Redeploy:**
  - You drop from high over a random point inside the current safe zone, away from enemies, with the descent device.
  - You get a basic kit: the P-12 sidearm, two magazines and one Field Patch.
  - Everything you carried drops where you died, so you can race back for it.
- **Earning the next token:**
  - After you redeploy (or after your first landing), a recharge countdown of 60 s starts, shown as a ring by the Resurgence status.
  - Each kill takes off 10 s, and each supply crate opened takes off 5 s.
  - The countdown only runs while you're on the ground.
- **Cutoff:**
  - Resurgence switches off when storm phase 4 starts closing.
  - A 20 s warning banner ("RESURGENCE ENDS IN 20 SECONDS · After that, eliminations are final").
  - Then "RESURGENCE OFF · ELIMINATIONS ARE FINAL", and a red status label stays on the HUD.
- **Bots** play by the same rules, so the alive count only drops once tokens run out or after the cutoff.
- **Players-alive count** counts everyone still in the match, including anyone waiting to redeploy.
- **Results** add respawns used.
- **Main menu label:** "BOT MATCH · RESURGENCE".

## Step 7 · Features seen in the reference worth adding (solo)

**Doing**
- **Loot rarity:**
  - coloured tiers on items, slots and ground beams
  - a light beam over ground loot
  - an outline highlight on what you're looking at
- **Pickup prompts and toasts:** "E Swap for …" and "Picked up …".
- **Supply crates:** open to spill loot. Opening one also speeds up your Resurgence recharge.
- **Eliminated players drop their loot.**
- **Hit feedback:**
  - damage numbers
  - hit marker and headshot marker
  - an "Eliminated <name> · N kills" popup
  - kill feed with weapon icons
- **Use timer:** a ring at the crosshair for reloading and healing ("Field Patch 1.6 s").
- **Drivable vehicles:**
  - enter and exit with E, swap seat
  - speed, hull and fuel readouts
  - a radio station as an extra
- **Ping:** middle mouse marks a spot or item on the map and compass. Useful solo as a waypoint.
- **One legendary item per match.**

**Later**
- Squads with bot teammates, currency and vendors, text chat (these are your decisions from 2026-10-12).
- Voice chat and network stats once there is multiplayer.

## Step 8 · Audio
Real sounds for:
- weapons, footsteps by surface, vehicles, the transport, wind in freefall
- storm thunder
- ambience per biome
- menu music

## Step 9 · Performance (runs alongside every step)

The reference holds 30 fps with far denser scenes, so density is affordable if we build it the right way.
- **Rendering:** instance everything that repeats, use LODs and impostors, add occlusion culling for interiors, and tune one shadow setup for the browser.
- **Quality presets** (Low to High) from the Video settings, with measured frame times on your PC after every step.
- **Download:** Basis textures, Ogg audio, and possibly streaming the map so you can reach the menu before everything has downloaded.

## Order

| # | Work | Why this order |
|---|---|---|
| 1 | Mouse fix | Blocks playtesting today |
| 2 | Loading screen, main menu, in-match menu, settings, learn controls | From your designs; every later build feels like a game, and settings are needed for perf testing |
| 3 | Realistic terrain regeneration + Bloomwild at final quality + perf check | Proves the look before mass production |
| 4 | Roll the map pass out island-wide, rebuild POIs with interiors | The biggest visible gap |
| 5 | Match loop: transport, freefall, storm phases, map screen, compass | Turns the island into a match |
| 6 | Resurgence | Depends on the storm phases and redeploying from the air |
| 7 | Firing range, inventory and HUD restyle, report a problem, results | Completes the designed screens |
| 8 | Loot rarity, crates, feedback, vehicles, ping | Moment-to-moment feel |
| 9 | Model and texture upgrade, first-person arms | Polish |
| 10 | Audio | Final layer |

## Decisions (2026-10-12)

1. Solo only, with bots. Squads later.
2. Resurgence modelled on Warzone's, as in Step 6.
3. No currency or vendors yet.
4. Bloomwild first, and the whole island gets more realistic terrain.
5. Keep the sci-fi ringworld look and make it more stylized.

Sources for the Resurgence research:
- [Blizzard: Rebirth Resurgence Solos](https://news.blizzard.com/en-gb/article/23785636/rebirth-resurgence-solos)
- [Pro Game Guides: Rebirth Resurgence Solos](https://progameguides.com/call-of-duty/how-does-the-rebirth-resurgence-solos-mode-work-in-call-of-duty-warzone/)
- [Prima Games: reducing the respawn time](https://primagames.com/gaming/how-to-reduce-the-respawn-time-in-warzone-resurgence)
