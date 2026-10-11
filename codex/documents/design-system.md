# Orbit Royale — design system and gameplay foundations v0.1

Status: concept draft, not implemented. User-confirmed requirements are distinguished from proposed design and balance values. This document uses the structure and interaction discipline of Kong Royale premium v3 as a reference; Kong branding, assets, colors, fonts, and game-specific behavior are not adopted.

## Confirmed requirements

- Browser battle royale called Orbit Royale.
- Alien planet with prominent rings visible in the sky; expansive military science-fiction atmosphere inspired by the user's Halo Reach reference, with original assets and identity.
- 60 combatants per match. Initially one human and 59 bots; eventually fill missing human places with bots.
- Five initial weapon types: assault rifle, pistol, SMG, shotgun, sniper.
- Custom weapon and item models.
- Five inventory slots: slots 1–2 are weapons; slots 3–5 are flexible carried-item slots. No building or crafting.
- Six healing items: 25 health, 25 shields, 50 shields, full shields, full health, full health plus shields.
- Limited healing stack and carry quantities.
- No fall damage. Grapple item hooks onto objects and supports swinging toward them.
- Multiple grenade types, ground vehicles, and an unarmed helicopter-like vehicle for rotation.
- Asset-loading screen, main menu, lobby, and settings for mouse/keyboard, controller, accessibility, audio, and video.
- Premium presentation and game feel are the quality goal. This is not a claim that the complete game has been built or validated.

## Proposed world and identity

Planet: Veyra. First map: Ringfall. Both remain working names.

Frontier colony infrastructure sits among basalt cliffs, crater lakes, pale alien grasslands, luminous vegetation, and ancient ruins. Enormous planetary rings form a memorable diagonal across the sky. Warm equipment lighting contrasts with a cool natural environment.

Brand personality: confident, exploratory, precise. Menus feel like sophisticated expedition equipment. Landscape and sound provide atmosphere; controls remain calm and legible.

Proposed camera: first-person combat, third-person vehicles. This needs a decision before production character animation and camera-sensitive weapon work.

## Inventory contract

Five visible numbered slots form one horizontal HUD strip. Slots 1–2 accept weapons. Slots 3–5 accept healing, grenades, a grapple, and future eligible utility items. Weapons stay in the first two slots under this interpretation; confirm before implementation if flexible slots should also accept extra weapons.

Each flexible slot contains one item type and its stack. Matching pickups fill an existing stack first. A remaining quantity can enter another empty flexible slot, subject to the item-type carry cap. No hidden healing bag or extra grenade pocket.

Proposed launch limits:

| Item | Effect | Maximum per stack | Total carry cap | Use time |
|---|---|---:|---:|---:|
| Field Patch | +25 health | 6 | 6 | 2 s |
| Shield Cell | +25 shields | 6 | 6 | 2 s |
| Shield Pack | +50 shields | 3 | 3 | 3.5 s |
| Shield Core | Full shields | 1 | 1 | 6 s |
| Trauma Kit | Full health | 1 | 1 | 6 s |
| Phoenix Capsule | Full health and shields | 1 | 1 | 9 s |
| Fragmentation grenade | Timed explosive | 3 | 3 | — |
| Arc grenade | Shield/vehicle disruption | 2 | 2 | — |
| Veil grenade | Concealment cloud | 2 | 2 | — |
| Tethercaster | Rechargeable grapple | 1 | 1 | — |

Carry caps apply across all slots, preventing duplicated stacks from bypassing the intended limit. These are starting balance values, not final tuning.

Example: assault rifle / shotgun / grapple / three Shield Packs / six Field Patches. Carrying grenades then requires replacing a flexible item. A player may choose three healing types and give up the grapple and grenades.

Proposed health model: 100 health plus 100 shields. Healing restores up to the normal maximum. Items are consumed only when use completes. Slow walking is allowed during use; damage, firing, and grappling interrupt it. Cannot begin a single-pool heal when that pool is full. Phoenix can be used if either pool is missing points.

Automatic pickup never replaces an occupied slot. Manual replacement clearly previews the dropped item. Support moving, dropping, splitting stacks, and swapping without dragging. Swaps must preserve slot eligibility and carry caps. Ammunition uses a separate bounded reserve shown beside the selected weapon; it does not consume one of the five slots. Ammunition caps remain to be tuned.

## Vehicles

| Vehicle | Role | Tradeoff |
|---|---|---|
| Mule | Colony buggy for reliable ground rotation | Loud and visible |
| Skimmer | Fast one-seat hover bike | Exposed rider and light protection |
| Strider | Heavy survey rover | Slow and conspicuous |
| Kestrel | Unarmed colony utility rotorcraft | Fast aerial rotation, scarce availability, strong sound signature |

Kestrel concept: compact cockpit, enclosed lift rotors, landing skids, and an expedition silhouette. No mounted weapons. Initially one pilot seat for solo play, with room in the design for passenger seats if team modes arrive. Proposed: no personal weapon firing while seated.

Aircraft should offer repositioning while preserving contested landings. Use a bounded flight ceiling, a finite flight-energy supply, visible damage feedback, and safe-zone pressure. Engine sound must give ground players useful advance warning. No guaranteed stealth or invulnerability. Values need flight testing against map size.

Resolve exits early: no fall damage means an airborne exit can be viable, but terrain clearance, exit placement, vehicle velocity inheritance, and destroyed-aircraft behavior need explicit rules and tests. Aircraft damage and storm damage still apply; no fall damage does not imply immunity to either.

## Brand and logo direction

Create an original ORBIT wordmark with ROYALE as a subordinate descriptor. Explore a planetary O crossed by one orbital arc. Preserve readable letters: the ring must not obscure the counter or become a crosshair.

Required eventual masters: stacked lockup, horizontal lockup, compact orbital emblem, monochrome dark/light variants, favicon, and small-size variants. One fixed vector master per variant; do not regenerate the logo for each screen.

Provisional clear space: half the emblem diameter. Determine minimum sizes through actual legibility tests. Avoid bevels, metallic extrusion, glow baked into the asset, and excessively fine lines. No logo artwork or final font assets are included in this draft.

## Candidate color tokens

| Token | Value | Role |
|---|---|---|
| background | #0B101B | Menu foundation |
| surface | #141D2D | Opaque panels and dialogs |
| surface-raised | #213047 | Hover/selection surface |
| border | #46566D | Rules and boundaries |
| text-primary | #F3F5FA | Main text |
| text-secondary | #B4BFD0 | Supporting text |
| accent | #C5F277 | Primary actions and selected markers |
| text-on-accent | #0B101B | Text on accent fill |
| health | #FF8D7F | Health meter and health-item cue |
| shield | #70D6FF | Shield meter and shield-item cue |
| success | #8DE0B0 | Saved/connected feedback |
| warning | #FFD18A | Caution |
| danger | #FF797F | Damage/errors/destructive feedback |
| focus | #FFFFFF | Keyboard/controller focus |

Pale lime is the brand/action accent; cyan belongs to shields. Violet is an environmental and illustration color, not a default control color. Color tokens are candidates and require contrast checks in rendered interfaces. Use icons and text alongside color. Gameplay items also require distinct silhouettes.

## Typography direction

Display: a moderately extended geometric sans with distinctive but readable letterforms. UI: a neutral sans with open counters, strong small-size readability, and tabular numerals. Avoid novelty science-fiction fonts in controls and body text. The logo should have custom vector lettering independent of the heading font.

Select font families after comparing rendered specimens and checking distribution rights. Bundle approved files. Do not synthesize unavailable weights or stretch text.

Reference hierarchy at a 1920×1080 logical canvas: hero 80/88, page title 56/64, section heading 28/36, control label 20/28, body 18/27, supporting text 16/24, important HUD number 32/36. Responsive layout and text scaling take precedence over preserving this geometry.

## Spacing, shape, and components

Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64. Start with 48 safe-area inset, 24 panel padding, 32 dialog padding, 48 control height, 56 primary-action height, and settings rows at least 72 high. Use 4-radius controls, 8-radius necessary panels, thin rules, and a visible 2-pixel focus ring.

Use continuous rows and intentional empty space instead of a card around every setting. Avoid decorative corner cuts and fine-print telemetry. One dominant action per task region.

Shared components: ScreenShell, SettingsShell, Dialog, Button, Tabs, SettingRow, Slider, Switch, Select, BindingCapture, Keycap, Toast, InventorySlot, HUDGroup, LoadingProgress.

Every component specifies default, hover, focus, pressed, selected/checked, disabled, and error where applicable. Async actions include pending, success, and retry states. Selection and focus remain distinguishable.

## Screen contracts

Asset loading: show actual progress when totals are known, current stage, and recovery from a failed download. Separate downloading, preparing assets, and ready states. Never invent progress percentages. Loading artwork features the rings and an original Ringfall vista.

Main menu: cinematic Ringfall view, primary Play action, Settings, and Credits. Keep the game's identity visible without crowding navigation. Browser entry should explain the action needed to start audio and enter the game view when necessary.

Lobby: player/character presentation, solo mode information, start action, and accurate human/bot counts. Do not imply online human matchmaking exists during the local bot phase. Avoid nonfunctional store, progression, and social navigation.

Settings: one consistent full-screen shell with top category navigation and local section tabs. Categories: Mouse & keyboard, Controller, Audio, Video, Accessibility, Gameplay. Continuous setting rows; aligned controls; contextual help collapses below rows on narrow displays. Settings apply immediately and persist on this device where supported. Category reset confirms its scope.

Gameplay: minimap top left, compass top center, survivor/elimination stats top right, health/shields bottom left, five-slot inventory bottom center, selected-weapon ammo bottom right. Vehicle controls appear contextually using actual bindings. Keep the aiming region clear.

Inventory slots: binding glyph, item silhouette, quantity, and an optional charge/use indicator. Slots 1–2 have discreet weapon eligibility marks. Empty flexible slots are quiet. Selected equipment has a clear border and label; full stack feedback explains why a pickup cannot be carried.

Map: large map, readable storm boundary, location labels, player marker, bounded legend, and binding-aware controls. Hide unrelated HUD groups while open.

Pause: Resume first; Settings; separated Leave match action. In future live multiplayer the match continues. Decide and accurately communicate pause behavior in the initial local bot mode.

Results: placement, eliminations, damage, survival time, Play again, and Return to lobby. Use a short optional celebration that respects reduced motion.

## Accessibility, input, motion, and responsive rules

Use one overlay manager and one input-focus manager. Gameplay input must not pass through menus. Back closes one layer and restores focus. Controller navigation has a predictable order and visible selection. Binding capture includes cancel, clear, and explicit conflict resolution. Provide non-drag inventory actions.

Accessibility includes text/HUD scaling, color-independent status, reduced motion, adjustable shake and flashes, hold/toggle controls, subtitles for meaningful spoken content, and separate aiming sensitivities. Key prompts derive from the actual binding and current device.

Proposed motion: 120 ms fast, 180 ms standard, 240 ms slow. Prefer short fades and surface changes; avoid perpetual pulsing and moving control layouts. Reduced motion removes nonessential transitions.

Test 16:9, 16:10, ultrawide, smaller windows, and enlarged text. Layouts reflow instead of uniformly shrinking. Constrain menu reading widths and keep HUD within adjustable safe areas.

## Handoff and implementation sequence

1. Decide combat camera and clarify whether flexible slots permit extra weapons.
2. Prototype movement, grappling, combat, and five-slot inventory with primitive assets.
3. Playtest proposed healing/stack rules and bot behavior.
4. Compare visual directions; choose font assets and produce original vector logo masters.
5. Implement shared tokens, components, focus, and settings.
6. Polish one Ringfall area, two weapons, one healing item, and the complete menu-to-results loop.
7. Add remaining equipment, ground driving, and unarmed flight; test flight against the map.
8. Expand the map and population to 60; profile gameplay and asset downloads on agreed target hardware.
9. Design online authority, human matchmaking, and bot filling as a separate implementation milestone.

Acceptance checks include item duplication/cap prevention, complete inventory navigation, consistent healing interruption, readable aircraft cues, no-fall-damage exits, reliable loading recovery, coherent focus, scaled text, controller bindings, and honest match population display.

Outstanding decisions: final camera; extra weapons in flexible slots; target hardware/browser and performance budget; pause behavior in bot mode; final fonts/logo; exact damage/recoil; ammunition caps; flight ceiling/energy; map scale. These must not be silently treated as approved values in implementation.
