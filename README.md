# Orbit Royale

A browser battle royale on an alien planet whose enormous rings dominate the sky. Scavenge, grapple through vertical terrain, and rotate by ground vehicle or unarmed aircraft to become the last survivor.

**Status: preproduction.** This repository contains concept/design documents, a UI prototype, and an asset hub. The complete battle royale is not implemented. Premium presentation and responsive gameplay are the quality goal.

## Start here

- [Build plan](docs/plan.md): where the project stands and the phases, decisions and tasks ahead.
- [Godot game](game/README.md): the movement and Tethercaster playground, how to run it, and its tests.
- [Codex workspace](codex/README.md): concept art, generation prompts, and original planning snapshots for Claude and other collaborators.
- [Game concept](docs/game-concept.md): world, Ringfall map, combat, equipment, vehicles, bots, and match flow.
- [Design system v0.1](docs/design-system.md): confirmed requirements, proposed inventory limits, brand direction, UI contracts, accessibility, and implementation sequence.
- [Development roadmap and Claude handoff](docs/claude-handoff.md): priorities, unresolved decisions, and milestone acceptance criteria.
- [Reference notes](docs/references/README.md): context for the supplied Kong design system.

## Current foundations

- 60 combatants: initially one human and 59 bots; future online lobbies fill missing human places with bots.
- Five weapon types: assault rifle, pistol, SMG, shotgun, and sniper.
- Five inventory slots: two for weapons, three for carried items.
- Six healing types, bounded stacks, multiple grenade types, and a grapple item.
- No fall damage, building, or crafting.
- Driveable ground vehicles and an unarmed helicopter-like aircraft for rotation.
- Custom weapon/item models and an original Orbit Royale identity.
- Asset loading, main menu, lobby, match HUD, results, and comprehensive input/audio/video/accessibility settings.

Working names, exact balance values, camera perspective, fonts, and logo geometry remain proposals unless explicitly confirmed. See the documents before implementing them.
