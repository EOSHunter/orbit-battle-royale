# Orbit Royale — game concept

Status: preproduction concept. User-confirmed foundations are recorded in [the design system](design-system.md). Names and balance suggestions here remain proposals.

## Pitch and atmosphere

Sixty combatants drop onto an abandoned frontier colony beneath enormous planetary rings. Scavenge equipment, grapple across alien terrain, commandeer vehicles, and survive a closing atmospheric disturbance.

Working tagline: **One world. One survivor.**

Use the user's Halo Reach reference for expansive military science-fiction atmosphere, monumental landscapes, and lonely infrastructure. Develop original architecture, silhouettes, characters, weapons, materials, sound, and branding.

Working planet name: **Veyra**. Working first-map name: **Ringfall**.

Dark basalt mountains, pale grasslands, turquoise water, luminous alien vegetation, practical human colony structures, and ancient ruins create the world. Warm amber equipment lights contrast with cool blue/violet landscapes. Huge rings sweep diagonally across the sky and remain visible from most outdoor locations.

## Ringfall map

A massive crater lake marks where a ring fragment struck the colony. Connected routes circle the crater; dangerous shortcuts cross its center. Build recognizable landmarks so players can navigate visually.

| Location | Appearance | Gameplay role |
|---|---|---|
| Crown Observatory | Mountain telescopes and fractured communications dish | Long sightlines, sniper opportunities, exposed escapes |
| Anchorport | Cargo pads, warehouses, grounded transports | Dense fights, supplies, vehicles |
| Glass Basin | Crater lake, black glass formations, small islands | Risky crossings and grapple opportunities |
| Bloomwild | Giant alien plants, luminous roots, shallow streams | Cover, ambushes, quieter looting |
| Relay Nine | Power station, gantries, pipes, maintenance tunnels | Vertical combat with multiple approaches |
| The Spine | Elevated cliffs and ancient bridge | Fast traversal and contested high ground |
| Hollow Array | Ruins embedded in a canyon | Close combat and sheltered rotations |

Every powerful elevated position should have at least two practical attack routes and an escape route. Prototype grapple range and momentum before finalizing heights and gaps. Aircraft require reachable landing spaces and exposed approaches.

Start with fixed sky and lighting so visibility and atmosphere can be tuned deliberately. Map dimensions and final location layout remain undecided.

## Match and combat proposals

- Solo mode first; 60 total combatants.
- First-person combat and third-person driving are proposed, not approved.
- 100 health and 100 shields.
- Target match length of approximately 15–18 minutes.
- No fall damage. Sprinting, jumping, and expressive grappling define traversal.
- A closing ion storm forces movement through successive safe zones.
- Proposed storm damage bypasses shields and damages health; test this before final balancing.
- Begin without attachments or weapon rarity tiers; make five core weapons satisfying first.

The storm uses ionized clouds, particles, distant lightning, and boundary interference. Its edge must remain unmistakable in a firefight.

## Launch weapons

| Type | Working name | Role |
|---|---|---|
| Assault rifle | AR-7 Wayfarer | Dependable midrange automatic weapon |
| Pistol | P-12 Spark | Accurate, fast-handling backup |
| SMG | S-9 Wisp | Close-range tracking and aggressive movement |
| Shotgun | SG-4 Breaker | Strong close bursts; missed shots are costly |
| Sniper | SR-8 Longview | Precision at range with slow follow-up shots |

Custom models must be supported by recognizable silhouettes, firing/reload animations, distinct sound, readable recoil, and impact feedback. Exact damage, magazine sizes, ammunition reserves, recoil, and headshot behavior require testing.

## Inventory and healing

The user requested five slots: two weapons and three flexible carried-item slots, with no building or crafting. The current proposal places healing, grenades, and the grapple in slots 3–5. Whether those slots may also carry extra weapons remains an explicit interpretation to resolve.

The healing set is Field Patch (+25 health), Shield Cell (+25 shields), Shield Pack (+50 shields), Shield Core (full shields), Trauma Kit (full health), and Phoenix Capsule (full health and shields).

See [the inventory contract](design-system.md#inventory-contract) for proposed stack/carry caps, timings, pickup behavior, and healing interruption. These values have not been playtested.

## Grappling and grenades

**Tethercaster:** hooks onto eligible solid terrain/structures, pulls toward the anchor, allows steering and swinging, and releases manually to preserve momentum. Proposed visible range limit and rechargeable cooldown. It occupies one of the three flexible slots; it is not free permanent equipment.

**Fragmentation grenade:** bounces and explodes after a short fuse.

**Arc grenade:** strong against shields and briefly disrupts vehicles. Avoid lengthy loss of player control.

**Veil grenade:** creates a readable concealment cloud for crossing open ground, healing, or breaking sightlines.

## Vehicles

- **Mule:** rugged colony buggy, reliable on rough ground, loud and visible.
- **Skimmer:** fast one-seat hover bike with an exposed rider.
- **Strider:** durable heavy survey rover, slow and conspicuous.
- **Kestrel:** unarmed helicopter-like colony utility aircraft for rotation, with enclosed lift rotors and landing skids.

Ground vehicles and an unarmed aircraft are user requirements; vehicle names, seating, energy limits, and handling are proposals. No mounted weapons on Kestrel. See [vehicle rules](design-system.md#vehicles) for the proposed tradeoffs and airborne-exit questions.

## Bots and future online play

Initially support one human and 59 bots. Future online matchmaking should count accepted human participants and fill remaining match places with bots, preserving the total of 60. Disconnect handling, late joins, and replacing bots during a live match are not yet defined.

Bots should loot, navigate, rotate with the storm, seek cover, heal, and make believable mistakes. Difficulty should come from decision quality and reaction time rather than perfect player-location knowledge. Vehicle and grapple competence should be introduced and tested progressively.

Local bot simulation is an initial milestone, not evidence that networked multiplayer exists. Online authority, replication, matchmaking, and bot placement need their own architecture and tests.

## Screens and experience

Complete flow: asset loading → main menu → lobby → deployment → match → results → replay/lobby.

Deployment should give an overview of Ringfall and a drop-selection interaction; transport, drop physics, and exact entry rules remain undecided. Include pause, inventory, map, contextual vehicle controls, and mouse/keyboard, controller, accessibility, audio, video, and gameplay settings.

See [screen contracts](design-system.md#screen-contracts) for presentation and behavior.

## Quality target

The user wants the branding and mechanics to feel comparable in quality to a $60 Steam game. Prioritize responsive movement/aiming, cohesive assets, animation and sound, readable combat, stable performance, believable bots, and a smooth menu-to-match flow.

Browser delivery needs deliberate asset downloads, recoverable loading failures, scalable quality settings, and agreed target hardware/performance budgets. Do not select an engine or promise performance without evaluating a playable prototype.
