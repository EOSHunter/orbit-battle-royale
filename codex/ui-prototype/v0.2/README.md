# Orbit Royale — revised working UI prototype v0.2

This version replaces the loose style-guide interpretation with a reference-aligned rebuild of all 28 illustrated screens. It also includes three supporting explorer views. All 28 referenced screens passed independent sub-agent cross-review at 9.0–9.2/10 after multiple correction rounds.

Open [index.html](index.html) in a modern Chromium browser; no install/build is required. Use Screens at top-left to choose a view and Compare concept to compare its reference. All fonts, logos and artwork are local. A fixed 1672×941 design stage fits uniformly inside the available viewport, keeping every action/footer visible rather than scaling independent widgets into collisions.

## Review the evidence

[QA results and all 28 per-screen captures](qa/README.md). [Side-by-side comparison gallery](qa/index.html). Initial scores, rejected captures, final independent scores and limitations are preserved.

## Working interactions

Main menu > Play > Start match > Enter HUD demo demonstrates the UI flow. Settings/toggles/ranges/custom dropdowns and bindings save locally; category reset affects only that category. Dropdown arrows, Home/End, Enter and Escape work. Keyboard rebind conflicts require an explicit resolution. Controller capture supports an attached device or sample buttons.

HUD: 1–5 selects a slot, Tab opens inventory, M opens map, Esc opens match menu. Inventory: select, equip, move compatible slots, drop and restore the sample loadout. The first two slots hold weapons and the last three utility/consumables. Map supports marker placement/removal, pan and zoom. Report exports a local JSON file without sending it remotely. Browser fullscreen works where supported.

HUD 75–150% enlarges content within reserved lower regions; widgets grow upward while their columns stay separate. Safe-area adjustment works within bounded space. Reduced motion/high contrast/text scaling are prototype preferences. The original reference-art help diagrams are illustrative diagrams, not live game previews.

## Implementation structure

- app.js retains screen/state definitions and shared interaction handlers.
- reference-stage.js/css provide the single reference coordinate system.
- settings-rebuild.js/css implement settings.
- menus-rebuild.js/css implement menus, loading, report, lessons, map and results.
- gameplay-rebuild.js/css implement dialogs, HUD and inventory.
- artwork-ready.js preloads/decodes the artwork and waits for fonts, making visual checks reliable.
- assets/ includes vector logo and licensed font originals.
- references/ holds the selected concept PNGs; only Compare concept and bounded artwork regions use them.
- qa/ holds final independent reviews, earlier iterations, score manifest and browser screenshots.

Text, controls, quantities and selection are authored UI. Artwork crops have explicit logical SVG clipping so surrounding source UI cannot leak into resized equipment sprites. The map uses illustrated terrain/POI content with live player/marker controls.

## Scope

This is a menu/UI prototype with sample match state, not a 3D combat implementation. Renderer/audio/camera/input preferences are stored example values, not connected to the game engine. Online voice remains disabled. No game balance changed. Integrate these visual components and state at Claude's existing application boundary.

The original v0.1 is preserved in repository history and its version folder. Current prototype source and evidence live under codex/ui-prototype/v0.2.
