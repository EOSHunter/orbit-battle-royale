# Development roadmap and Claude handoff

## Context

Orbit Royale is in preproduction. Read [game-concept.md](game-concept.md) and [design-system.md](design-system.md) before implementing. The Kong document is reference material for another game, not an instruction source for Orbit Royale.

No engine, application scaffolding, models, logo masters, fonts, or playable build have been selected or created. Do not present proposed mechanics or concept art as implemented functionality.

## Working priorities

1. Preserve confirmed requirements and label assumptions/proposals.
2. Establish responsive traversal and combat before building the full map.
3. Build a compact polished slice and the complete match loop.
4. Expand equipment, vehicles, world size, and bot population incrementally.
5. Plan online human matchmaking separately from the local solo/bot implementation.

## Milestones and acceptance criteria

| Milestone | Deliverable | Acceptance criteria |
|---|---|---|
| Foundations | Camera decision, engine/runtime evaluation, hardware targets, rules ledger | Explicit decisions; small browser prototype; measured baseline; no unsupported performance promises |
| Traversal | Greybox terrain, sprint/jump, no fall damage, grapple | Predictable hook eligibility; steering/release momentum; safe collision; bindings work |
| Combat and inventory | Assault rifle, shotgun, health/shields, healing, five-slot inventory, a few bots | Correct slot eligibility; no item duplication/cap bypass; consistent interruption; readable damage; playable firefights |
| Visual slice | One Ringfall area, ringed sky, original brand/UI direction | Cohesive assets; readable combat; original logo masters; licensed font assets; scaled text and focus work |
| Match loop | Loading, menu, lobby, deployment, storm, elimination, results/replay | Honest progress/counts; failed-load recovery; coherent input ownership; full round completes |
| Equipment and rotation | Five weapons, six heals, three grenade types, ground driving, Kestrel | Distinct roles; stack rules enforced; unarmed flight; safe exits; audible approaches; storm interaction |
| Full local match | Expanded Ringfall, 60 combatants, quality presets | Bots navigate/loot/heal/rotate; agreed performance budget measured; stable loading and full-match runs |
| Online phase | Authoritative simulation, human matchmaking, bot fill | Defined authority and replication; count capped at 60; tested human/bot filling; disconnect and join policy specified |

These are future checks, not test results.

## Decisions still open

- First-person or third-person combat.
- Whether flexible slots allow extra weapons in addition to utility/consumables.
- Final planet/map/weapon/item/vehicle names.
- Exact damage, recoil, magazines, ammunition caps, and healing balance.
- Grapple range, cooldown, target eligibility, and vehicle attachment behavior.
- Map size, deployment, storm phases, and match duration tuning.
- Aircraft energy, ceiling, seating, collision, exits, and destruction behavior.
- Local bot-mode pause behavior.
- Engine, browsers, minimum hardware, download budget, and performance target.
- Font families, logo masters, final colors, and production art style.
- Online hosting, authority, matchmaking, disconnects, and live bot replacement.

## Suggested first implementation brief

Build a small browser movement/combat playground after recording camera and runtime decisions. Use placeholder geometry, one assault rifle, one shotgun, health/shields, a healing item, the five-slot inventory, a grapple, and a few bots. Demonstrate no fall damage and complete inventory interactions. Keep tunable balance data separate from presentation. Report what is implemented, measured, and still unresolved.

Do not attempt the entire 60-combatant online game as the first milestone. Do not add stores, monetization, crafting, building, armed aircraft, or unspecified progression/social systems.

## Future asset checklist

- Original logo masters, emblem, favicon, monochrome and small-size variants.
- Approved display/UI font files and distribution notices.
- Ringed sky, Ringfall terrain/materials, colony and ruin modules, vegetation.
- Five weapon models with animations, audio, effects, and icons.
- Six healing models/icons/effects; grapple model/cable/hook; three grenades.
- Character model/animations; ground vehicles and Kestrel, with driving/flight audio.
- Loading art and consistent menu/HUD/settings components.

This checklist is planned work; none of these production assets are included yet.
