Orbit Royale's interface should feel like sophisticated expedition equipment: confident, exploratory, precise. The landscape and sound carry the atmosphere; menus and HUD stay calm and legible on top of it. Everything here is v0.1: candidate values from `docs/design-system.md`, to be checked in rendered screens before they are final.

## Status of this system

- **Confirmed by the game's brief:** five inventory slots (two weapons, three flexible), six healing items, 100 health plus 100 shields as the proposed model, and the screens: loading, main menu, lobby, settings (mouse & keyboard, controller, audio, video, accessibility, gameplay), match HUD, results.
- **Candidates, not final:** every color, the fonts, the type scale and the item names. Fonts are Google-hosted stand-ins (Archivo, IBM Plex Sans, IBM Plex Mono, all OFL) chosen to match the written direction; compare specimens before committing.
- **Not made yet:** the ORBIT wordmark and emblem. Until vector masters exist, set "Orbit Royale" in `hero` type and never draw a stand-in logo.
- **Placeholder icons:** `Orbit.icon(name)` in `components/bundle.js` draws simple 24px glyphs (health, shield, five weapons, grapple, grenade, survivors, eliminations, storm, check, warning, error). Replace them with production silhouettes; keep the names.

## Voice and copy

- Write like a field manual: short, literal, present tense. "Start match", "Retry download", "Leave match?".
- Buttons are verbs naming the outcome. Never "OK", "Submit" or "Confirm" alone.
- Say what is true about the match. Solo lobby copy reads "1 player and 59 bots"; never imply online matchmaking during the local bot phase.
- Errors name what failed and the fix: "Ringfall terrain failed to download. Retry".
- Sentence case for labels and buttons. Uppercase only for `or-eyebrow` labels (16px, 0.08em tracking).
- Use the working names exactly: Veyra, Ringfall, Kestrel, Tethercaster, Field Patch, Shield Cell, Shield Pack, Shield Core, Trauma Kit, Phoenix Capsule, AR-7 Wayfarer, P-12 Spark, S-9 Wisp, SG-4 Breaker, SR-8 Longview.
- No emoji anywhere in the interface.

## Color

- Build every screen on `background`; put panels and dialogs on opaque `surface`; use `surface-raised` for hover and selected rows.
- Over the 3D world (HUD, pause, map), use `scrim` behind text instead of opaque panels.
- `accent` (pale lime) is the brand and action color: the one primary button per region, selected tab underline, selected inventory slot, progress fill. Text on it is `text-on-accent`.
- `shield` cyan and `health` coral belong to the health model only: meters, healing items, damage numbers. Never use them for navigation or brand.
- `storm` violet and `colony-amber` are environmental colors for the map, minimap storm boundary and illustration. They are never control colors.
- `success`, `warning` and `danger` always come with an icon and a word. Success and danger are close in lightness, and danger is close in hue to health, so color alone never carries status.
- Use `border` for hairline rules between rows and around panels. Outline interactive controls with `border-control`, which meets 3:1 on every surface; `border` does not.

## Typography

- `hero`, `page-title` and `section-heading` use the display family (Archivo, set expanded with `font-stretch: 112–125%`). Use them for screen titles and headlines only, never for controls.
- Everything you operate or read in running text uses the UI family (IBM Plex Sans): `control-label` for buttons, tabs and setting labels; `body` for paragraphs; `supporting` for help text.
- `supporting` (16px) is the smallest text. No fine-print telemetry, no decorative micro-labels.
- Numbers that change or line up (health, ammo, counts, sliders, download sizes) use `font-variant-numeric: tabular-nums`; `hud-number` is the default for HUD values.
- Keycaps use the mono family.
- Sizes are specified at a 1920×1080 logical canvas. Responsive layout and the player's text-scale setting take precedence: reflow rather than shrink.

## Spacing, shape and layout

- Spacing steps are `space-1` through `space-16` (4, 8, 12, 16, 24, 32, 48, 64). Do not use values between them.
- Inset screens by `space-12` (48px) at 1920×1080, adjustable by the HUD safe-area setting.
- Controls are `control-height` (48px); the one primary action is `primary-height` (56px); setting rows are at least `row-min-height` (72px).
- `radius-control` (4px) on controls, keycaps, slots and toasts; `radius-panel` (8px) only on panels that must be panels. No decorative corner cuts.
- Prefer continuous rows and empty space over a card around every setting.
- Keep the center of the screen clear during a match.

## Focus, states and input

- Focus is a 2px white `focus` ring with a 2px offset on every focusable element, so it can never be confused with `accent` selection.
- Every component defines default, hover, focus, pressed, selected, disabled and, where it applies, error. Async actions show pending, then success or a Retry.
- One overlay manager and one focus manager: gameplay input never passes through menus. Back closes one layer and restores focus to what opened it.
- Prompts derive from the player's actual binding and the device that last sent input (`or-keycap` for keys, `or-keycap--pad` for controller buttons).
- Inventory actions (move, drop, split, swap) all work without dragging.

## Motion

- Durations: 120ms fast (hover, press), 180ms standard (tab change, toast), 240ms slow (screen transitions). Declared as `--motion-fast`, `--motion-standard`, `--motion-slow` in `components/bundle.css`.
- Prefer short fades and surface changes. No perpetual pulsing, no layouts that move under the cursor.
- `prefers-reduced-motion` and the in-game Reduce motion setting set all three to 0 and replace spinners and sweeps with static states.

## Iconography and imagery

- Icons are solid 24px glyphs in `currentColor`, readable at HUD scale. Items must be distinguishable by silhouette, not tint.
- Loading and menu art feature the rings sweeping diagonally across Ringfall's sky, warm amber colony lights against cool blue and violet landscape. Original art only; nothing from the Halo Reach reference or the Kong reference system.

## Using the components

The components are plain HTML and CSS. Load `tokens.css` and `components/bundle.css`, then `components/bundle.js` for `Orbit.icon()` and `Orbit.meterSegments()`. Class prefix is `or-`. Each component's guideline lists what the screen must supply.
