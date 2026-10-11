# Asset list

Generated from `asset-hub/asset-list.js` (78 assets). Track progress in the Asset Hub; edit this list in the script and regenerate.

Budgets are proposals for a browser target and change once hardware and performance targets are agreed. Items marked **Decision needed** depend on open design decisions in [claude-handoff.md](claude-handoff.md).

## Characters

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Operator (third-person) | Combat and inventory | Concept sheet; Base mesh; Materials and textures; Rig and skinning; LODs; Bot variants (gear and color swaps) | 5k–15k tris · 2048² baked textures | `game/assets/models/characters/operator-third-person.glb` |
| Bot operator | Combat and inventory | Mesh; Materials and color variants; Rig matching the operator skeleton | 1k–3k tris · 512² baked textures | `game/assets/models/characters/bot-operator.glb` |
| First-person arms<br>**Decision needed:** Combat camera: first-person combat is proposed, not approved. | Traversal | Mesh; Materials; Rig matching the operator skeleton | Part of the 5k–15k character budget · 1024² baked textures | `game/assets/models/characters/first-person-arms.glb` |
| Locomotion set | Traversal | Idle; Walk; Sprint; Crouch and crouch-walk; Jump, fall, land; Slow walk while healing | — | `game/assets/animations/characters/locomotion-set.glb` |
| Tethercaster traversal set | Traversal | Fire hook; Reel in; Swing loop; Release and momentum carry | — | `game/assets/animations/characters/tethercaster-traversal-set.glb` |
| Weapon handling set | Combat and inventory | Equip and holster per weapon; Hip and aim poses; Fire and recoil; Reload per weapon; Grenade throw | — | `game/assets/animations/characters/weapon-handling-set.glb` |
| Healing use set | Combat and inventory | Field Patch / Trauma Kit (apply); Shield Cell / Pack / Core (insert); Phoenix Capsule (inject); Interrupted exit | — | `game/assets/animations/characters/healing-use-set.glb` |
| Freefall and landing<br>**Decision needed:** Drop rules: how players slow down after jumping (glider, thruster pack, or none) is undecided. | Match loop | Exit transport; Freefall pose and steering; Descent device deploy; Landing | — | `game/assets/animations/characters/freefall-and-landing.glb` |
| Vehicle set | Equipment and rotation | Enter and exit (ground vehicles); Driver sit and steer; Kestrel pilot; Airborne exit | — | `game/assets/animations/characters/vehicle-set.glb` |
| Elimination | Match loop | Elimination fall; Results screen pose | — | `game/assets/animations/characters/elimination.glb` |

## Weapons

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| AR-7 Wayfarer (Assault rifle) | Combat and inventory | Concept and silhouette; First-person viewmodel mesh; World / pickup mesh + LODs; Materials and textures; Rig (magazine, bolt, trigger); Animations: equip, fire, reload, sprint; Inventory and HUD icon; Fire VFX: muzzle, tracer, casing | 500–1.5k tris (one model for view, pickup and bots) · 1024² baked textures | `game/assets/models/weapons/ar-7-wayfarer.glb` |
| SG-4 Breaker (Shotgun) | Combat and inventory | Concept and silhouette; First-person viewmodel mesh; World / pickup mesh + LODs; Materials and textures; Rig (magazine, bolt, trigger); Animations: equip, fire, reload, sprint; Inventory and HUD icon; Fire VFX: muzzle, tracer, casing | 500–1.5k tris (one model for view, pickup and bots) · 1024² baked textures | `game/assets/models/weapons/sg-4-breaker.glb` |
| P-12 Spark (Pistol) | Equipment and rotation | Concept and silhouette; First-person viewmodel mesh; World / pickup mesh + LODs; Materials and textures; Rig (magazine, bolt, trigger); Animations: equip, fire, reload, sprint; Inventory and HUD icon; Fire VFX: muzzle, tracer, casing | 500–1.5k tris (one model for view, pickup and bots) · 1024² baked textures | `game/assets/models/weapons/p-12-spark.glb` |
| S-9 Wisp (SMG) | Equipment and rotation | Concept and silhouette; First-person viewmodel mesh; World / pickup mesh + LODs; Materials and textures; Rig (magazine, bolt, trigger); Animations: equip, fire, reload, sprint; Inventory and HUD icon; Fire VFX: muzzle, tracer, casing | 500–1.5k tris (one model for view, pickup and bots) · 1024² baked textures | `game/assets/models/weapons/s-9-wisp.glb` |
| SR-8 Longview (Sniper) | Equipment and rotation | Concept and silhouette; First-person viewmodel mesh; World / pickup mesh + LODs; Materials and textures; Rig (magazine, bolt, trigger); Animations: equip, fire, reload, sprint; Inventory and HUD icon; Fire VFX: muzzle, tracer, casing | 500–1.5k tris (one model for view, pickup and bots) · 1024² baked textures | `game/assets/models/weapons/sr-8-longview.glb` |

## Weapon audio

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| AR-7 Wayfarer audio (Assault rifle) | Combat and inventory | Fire (close); Fire (distant tail); Reload; Equip; Dry fire | WAV 48 kHz mono one-shots (QOA-compressed on import) | `game/assets/audio/weapon-audio/ar-7-wayfarer-audio/` |
| SG-4 Breaker audio (Shotgun) | Combat and inventory | Fire (close); Fire (distant tail); Reload; Equip; Dry fire | WAV 48 kHz mono one-shots (QOA-compressed on import) | `game/assets/audio/weapon-audio/sg-4-breaker-audio/` |
| P-12 Spark audio (Pistol) | Equipment and rotation | Fire (close); Fire (distant tail); Reload; Equip; Dry fire | WAV 48 kHz mono one-shots (QOA-compressed on import) | `game/assets/audio/weapon-audio/p-12-spark-audio/` |
| S-9 Wisp audio (SMG) | Equipment and rotation | Fire (close); Fire (distant tail); Reload; Equip; Dry fire | WAV 48 kHz mono one-shots (QOA-compressed on import) | `game/assets/audio/weapon-audio/s-9-wisp-audio/` |
| SR-8 Longview audio (Sniper) | Equipment and rotation | Fire (close); Fire (distant tail); Reload; Equip; Dry fire | WAV 48 kHz mono one-shots (QOA-compressed on import) | `game/assets/audio/weapon-audio/sr-8-longview-audio/` |

## Healing items

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Field Patch (+25 health · stack 6) | Combat and inventory | Pickup mesh; Held mesh; Materials; Inventory icon; Use VFX | 500–1.5k tris · 1024² baked textures | `game/assets/models/healing-items/field-patch.glb` |
| Shield Cell (+25 shields · stack 6) | Equipment and rotation | Pickup mesh; Held mesh; Materials; Inventory icon; Use VFX | 500–1.5k tris · 1024² baked textures | `game/assets/models/healing-items/shield-cell.glb` |
| Shield Pack (+50 shields · stack 3) | Combat and inventory | Pickup mesh; Held mesh; Materials; Inventory icon; Use VFX | 500–1.5k tris · 1024² baked textures | `game/assets/models/healing-items/shield-pack.glb` |
| Shield Core (Full shields · stack 1) | Equipment and rotation | Pickup mesh; Held mesh; Materials; Inventory icon; Use VFX | 500–1.5k tris · 1024² baked textures | `game/assets/models/healing-items/shield-core.glb` |
| Trauma Kit (Full health · stack 1) | Equipment and rotation | Pickup mesh; Held mesh; Materials; Inventory icon; Use VFX | 500–1.5k tris · 1024² baked textures | `game/assets/models/healing-items/trauma-kit.glb` |
| Phoenix Capsule (Full health and shields · stack 1) | Equipment and rotation | Pickup mesh; Held mesh; Materials; Inventory icon; Use VFX | 500–1.5k tris · 1024² baked textures | `game/assets/models/healing-items/phoenix-capsule.glb` |

## Item audio

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Healing item audio | Combat and inventory | Use loop per item (6); Use complete; Use interrupted; Pickup | — | `game/assets/audio/item-audio/healing-item-audio/` |
| Grenade audio | Equipment and rotation | Pin and throw; Bounce; Frag detonation (close / distant); Arc burst; Veil hiss and cloud | — | `game/assets/audio/item-audio/grenade-audio/` |
| Tethercaster audio | Traversal | Fire; Anchor hit; Reel loop; Release; Recharge complete | — | `game/assets/audio/item-audio/tethercaster-audio/` |

## Grenades

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Fragmentation grenade (Timed explosive) | Equipment and rotation | Mesh; Materials; Inventory icon; Detonation VFX | 500–1.5k tris · 1024² baked textures | `game/assets/models/grenades/fragmentation-grenade.glb` |
| Arc grenade (Shield and vehicle disruption) | Equipment and rotation | Mesh; Materials; Inventory icon; Detonation VFX | 500–1.5k tris · 1024² baked textures | `game/assets/models/grenades/arc-grenade.glb` |
| Veil grenade (Concealment cloud) | Equipment and rotation | Mesh; Materials; Inventory icon; Detonation VFX | 500–1.5k tris · 1024² baked textures | `game/assets/models/grenades/veil-grenade.glb` |

## Utility

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Tethercaster (Grapple) | Traversal | Viewmodel mesh; Pickup mesh; Hook head; Cable material and shader; Rig; Inventory icon; Recharge indicator | 500–1.5k tris · 1024² baked textures | `game/assets/models/utility/tethercaster.glb` |

## Pickups

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Ammunition boxes | Combat and inventory | Light; Medium; Heavy; Shells | 100–800 tris each (prop) | `game/assets/models/pickups/ammunition-boxes.glb` |
| Colony supply crate | Combat and inventory | Mesh; Open animation; Loot glow VFX | 100–800 tris (prop) | `game/assets/models/pickups/colony-supply-crate.glb` |

## Vehicles

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Mule (Colony buggy · reliable, loud) | Equipment and rotation | Concept and silhouette; Blockout and scale test; Exterior mesh + LODs; Seat and controls; Damage states; Materials and textures; Rig: wheels, suspension, doors; Dust and exhaust VFX | 4k–8k tris · 2048² baked textures | `game/assets/models/vehicles/mule.glb` |
| Skimmer (One-seat hover bike · fast, exposed) | Equipment and rotation | Concept and silhouette; Blockout and scale test; Exterior mesh + LODs; Seat and controls; Damage states; Materials and textures; Rig: hover pads, handlebars; Dust and exhaust VFX | 3k–6k tris · 2048² baked textures | `game/assets/models/vehicles/skimmer.glb` |
| Strider (Heavy survey rover · slow, durable) | Equipment and rotation | Concept and silhouette; Blockout and scale test; Exterior mesh + LODs; Seat and controls; Damage states; Materials and textures; Rig: wheels, suspension, doors; Dust and exhaust VFX | 4k–8k tris · 2048² baked textures | `game/assets/models/vehicles/strider.glb` |
| Kestrel (Unarmed utility rotorcraft)<br>**Decision needed:** Seating, flight ceiling, energy and airborne exit rules are open. | Equipment and rotation | Concept and silhouette; Blockout and scale test; Exterior mesh + LODs; Cockpit interior; Damage states; Materials and textures; Rig: rotors, skids, doors; Rotor wash VFX | 4k–8k tris · 2048² baked textures | `game/assets/models/vehicles/kestrel.glb` |

## Vehicle audio

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Mule audio | Equipment and rotation | Engine loop (idle / load / high); Distant pass-by (audible warning); Enter / exit; Impacts; Destroyed | Ogg Vorbis 48 kHz · seamless loops | `game/assets/audio/vehicle-audio/mule-audio/` |
| Skimmer audio | Equipment and rotation | Engine loop (idle / load / high); Distant pass-by (audible warning); Enter / exit; Impacts; Destroyed | Ogg Vorbis 48 kHz · seamless loops | `game/assets/audio/vehicle-audio/skimmer-audio/` |
| Strider audio | Equipment and rotation | Engine loop (idle / load / high); Distant pass-by (audible warning); Enter / exit; Impacts; Destroyed | Ogg Vorbis 48 kHz · seamless loops | `game/assets/audio/vehicle-audio/strider-audio/` |
| Kestrel audio | Equipment and rotation | Engine loop (idle / load / high); Distant pass-by (audible warning); Enter / exit; Impacts; Destroyed | Ogg Vorbis 48 kHz · seamless loops | `game/assets/audio/vehicle-audio/kestrel-audio/` |

## Drop transport

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Drop transport (Start-of-match carrier (working name needed))<br>**Decision needed:** Deployment: transport route, jump window and drop rules are undecided. | Match loop | Concept and silhouette; Blockout and scale (60 jumpers); Exterior mesh + LODs; Interior hold and rear ramp; Materials and textures; Rig: ramp, engines, landing gear; Flight-path and ramp-open animation; Engine contrail VFX | 8k–15k tris · 2048² baked textures | `game/assets/models/drop-transport/drop-transport.glb` |
| Descent device<br>**Decision needed:** Whether players use a glider, thruster pack or nothing (no fall damage) is undecided. | Match loop | Concept; Mesh; Deploy animation; Trail VFX | 500–1.5k tris (main item) | `game/assets/models/drop-transport/descent-device.glb` |
| Drop transport audio | Match loop | Engine loop (exterior, distant); Hold interior ambience; Ramp open; Jump-out wind gust; Freefall wind loop; Landing | — | `game/assets/audio/drop-transport/drop-transport-audio/` |

## Environment

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Ringed sky dome | Visual slice | Ring band texture and shader; Planet and moon; Stars and haze; Fixed lighting setup | Sky shader + 4096² ring texture | `game/assets/models/environment/ringed-sky-dome.glb` |
| Ringfall terrain<br>**Decision needed:** Map size and final location layout are undecided. | Visual slice | Greybox heightmap; Crater lake basin; Final heightmap; Terrain materials: basalt, grassland, black glass, sand; Water shader (turquoise lakes) | Heightmap + 4 splat layers | `game/assets/models/environment/ringfall-terrain.glb` |
| Luminous vegetation kit | Visual slice | Pale grass cards; Glowing shrubs; Giant Bloomwild plants; Luminous roots; Emissive material | 100–800 tris per plant (prop) · instanced | `game/assets/models/environment/luminous-vegetation-kit.glb` |
| Colony structure kit | Visual slice | Habitat module; Warehouse; Cargo pad; Comms mast; Gantries and stairs; Pipes and cables; Amber work lights | Modular pieces under 1k tris each where possible | `game/assets/models/environment/colony-structure-kit.glb` |
| Ancient ruins kit | Full local match | Wall and arch pieces; Pillars; Bridge spans (The Spine); Canyon ruin set (Hollow Array) | Modular pieces under 1k tris each where possible | `game/assets/models/environment/ancient-ruins-kit.glb` |
| Prop kit | Visual slice | Crates and barrels; Fences and barriers; Lamps; Debris; Vehicle spawn pads | 100–800 tris each | `game/assets/models/environment/prop-kit.glb` |

## Locations

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Crown Observatory | Full local match | Layout blockout; Telescope domes; Fractured comms dish; Landmark silhouette pass | — | `game/assets/models/locations/crown-observatory.glb` |
| Anchorport | Full local match | Layout blockout; Grounded transports; Warehouses; Cargo containers; Landmark silhouette pass | — | `game/assets/models/locations/anchorport.glb` |
| Glass Basin | Visual slice | Layout blockout; Black glass formations; Islands; Ring fragment impact; Landmark silhouette pass | — | `game/assets/models/locations/glass-basin.glb` |
| Relay Nine | Full local match | Layout blockout; Power station; Maintenance tunnels; Gantry network; Landmark silhouette pass | — | `game/assets/models/locations/relay-nine.glb` |
| The Spine | Full local match | Layout blockout; Ancient bridge; Cliff high ground; Landmark silhouette pass | — | `game/assets/models/locations/the-spine.glb` |
| Hollow Array | Full local match | Layout blockout; Canyon ruins; Array structures; Landmark silhouette pass | — | `game/assets/models/locations/hollow-array.glb` |
| Bloomwild | Full local match | Layout blockout; Giant plant canopy; Streams; Landmark silhouette pass | — | `game/assets/models/locations/bloomwild.glb` |

## VFX

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Ion storm | Match loop | Storm wall shader; Clouds and particles; Distant lightning; Boundary interference (screen) | — | `game/assets/vfx/vfx/ion-storm.glb` |
| Combat impacts | Combat and inventory | Bullet impacts: basalt, grass, metal, glass, water; Shield hit; Shield break; Health hit | — | `game/assets/vfx/vfx/combat-impacts.glb` |
| Healing effects | Combat and inventory | Health heal particles; Shield recharge shimmer | — | `game/assets/vfx/vfx/healing-effects.glb` |
| Traversal effects | Traversal | Landing dust; Sprint dust; Water splash | — | `game/assets/vfx/vfx/traversal-effects.glb` |

## Brand and UI

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| ORBIT logo masters | Visual slice | Stacked lockup; Horizontal lockup; Orbital emblem; Monochrome dark / light; Favicon; Small-size variants | — | `game/assets/ui/brand-and-ui/orbit-logo-masters/` |
| Item and weapon icons | Combat and inventory | 5 weapons; 6 healing items; 3 grenades; Tethercaster; 4 ammo types | — | `game/assets/ui/brand-and-ui/item-and-weapon-icons/` |
| HUD icon set | Combat and inventory | Health; Shield; Survivors; Eliminations; Storm; Map markers; Status: success / warning / error | — | `game/assets/ui/brand-and-ui/hud-icon-set/` |
| Controller and key glyphs | Match loop | Keyboard and mouse; Xbox; PlayStation | — | `game/assets/ui/brand-and-ui/controller-and-key-glyphs/` |
| Ringfall map illustration | Match loop | Top-down render; Location labels; Minimap version | 4096² top-down | `game/assets/art/brand-and-ui/ringfall-map-illustration.png` |
| Loading and menu key art | Visual slice | Ringfall vista; Menu composition; Loading variants | 3840×2160 | `game/assets/art/brand-and-ui/loading-and-menu-key-art.png` |
| Font files | Visual slice | Compare specimens; Display family; UI family; License check and bundling | — | `game/assets/ui/brand-and-ui/font-files/` |

## Music

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Main menu theme | Match loop | Composition; Loop edit; Mix | Loopable · stereo | `game/assets/audio/music/main-menu-theme/` |
| Match stingers | Match loop | Drop start; Storm closing; Final survivors; Victory; Eliminated | — | `game/assets/audio/music/match-stingers/` |

## Ambience

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Ringfall ambience | Visual slice | Wind (open ground); Bloomwild wildlife; Glass Basin water; Colony hum; Interior tone | — | `game/assets/audio/ambience/ringfall-ambience/` |
| Ion storm audio | Match loop | Storm wall loop; Thunder (distant / close); Inside-storm damage tone | — | `game/assets/audio/ambience/ion-storm-audio/` |

## UI audio

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Interface sounds | Match loop | Navigate; Confirm; Back; Toggle; Slider tick; Error | — | `game/assets/audio/ui-audio/interface-sounds/` |
| Match feedback sounds | Combat and inventory | Hit marker; Elimination confirm; Shield break; Low health; Pickup; Inventory full; Storm warning | — | `game/assets/audio/ui-audio/match-feedback-sounds/` |

## Foley

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Footsteps | Traversal | Basalt; Grass; Metal; Glass; Shallow water; Jump and land | — | `game/assets/audio/foley/footsteps/` |

## Voice

| Asset | Milestone | Deliverables | Budget | File |
|---|---|---|---|---|
| Announcer callouts<br>**Decision needed:** Whether the game has announcer voice lines is undecided (subtitles are planned). | Full local match | Storm closing; Survivors remaining; Victory | — | `game/assets/audio/voice/announcer-callouts/` |
