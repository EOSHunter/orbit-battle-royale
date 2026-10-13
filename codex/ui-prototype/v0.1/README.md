# Orbit Royale — working UI prototype v0.1

Local, buildless HTML/CSS/JavaScript implementation of the sci-fi UI concepts. Open [index.html](index.html) in a modern Chromium browser. No install or build is required. All fonts, SVG logos and concept references are bundled. The prototype also works from a static HTTP server.

This implements all 28 concept screens as interactive code, plus the previously unillustrated Gameplay > Interaction tab, Training menu and Credits screen (31 explorer views total). Backgrounds remain plain navy.

## Use the prototype

- The top-left **Screens** dropdown opens any view. Adjacent arrows cycle through the views.
- **Compare concept** shows the matching source image beside the live UI. The live screens are DOM/CSS/SVG, not flattened screenshots.
- Main menu > Play > Start match > Enter HUD demo demonstrates the match flow. Loading progression is explicitly a manual demo.
- On the HUD: 1–5 selects a slot, Tab opens inventory, M opens the map, Escape opens the match menu. Rebinding Inventory/Map updates their HUD shortcuts.
- Inventory: select a row, Equip to show the selection in the HUD, Move to swap compatible slots, Drop to clear a slot. An empty selected slot offers **Restore sample loadout**. Exactly two weapon slots and three utility slots are retained.
- Map: click to place a marker, drag to pan, scroll or use buttons to zoom; arrow keys pan when the map is focused.
- Settings: sliders, segmented choices, toggles and custom navy/lime dropdowns work. Settings, keyboard/controller bindings and callsign persist in localStorage when the browser allows it. Saved defaults are isolated to the current category.
- Keyboard rebinding captures a key (or mouse input inside the capture region). Conflicts display the existing action and require explicitly moving the binding. Escape cancels. Controller rebinding can receive an attached gamepad button or use labeled sample buttons.
- Report exports a local JSON file. It sends nothing to a remote service. The optional reference checkbox includes a description of the displayed map, not a captured screenshot or binary attachment.
- Fullscreen uses the browser API when available; embedded browser policies may require their own fullscreen control.

## What changed from the style guide

The HUD now follows the authored layout: minimap, compass, counters, small center crosshair, cyan/coral four-segment meters, exactly five SVG item slots and weapon ammunition. Inventory uses five large numbered modules, selected-item detail, outline equipment previews, separate ammo reserves and Equip/Move/Drop/Close actions.

Native select menus are replaced by an anchored popover listbox with matching surfaces, lime selection brackets/checkmarks, white focus, outside-click dismissal and ArrowUp/ArrowDown/Home/End/Enter/Escape interaction. Sliders have square thumbs and aligned tracks/values. Chamfered frames are drawn at the actual rendered size using SVG rather than clipping away their border diagonals.

The main menu, lobby, loading stages, match menu, report, lessons, map, results and confirmations have their own layouts. All 14 original settings views preserve the shared category/table/help/footer structure. Reduced motion, high-contrast UI, text scaling and HUD scaling affect the prototype presentation.

## Scope

This is a working menu/UI prototype, not the battle royale engine. Renderer, audio mixing, raw input, vibration, camera and combat preferences are stored demo values; they do not control a game simulation here. Figures such as 23 remaining, 4 eliminations, ammunition and match results are illustrative. Online voice remains disabled.

Equipment SVGs, map geometry and line diagrams are authored interface approximations of the concept artwork, not final 3D assets or a pixel-perfect tracing. The seven-location map retains the functional composition but is a simplified schematic. Fonts use the menu design system's bundled licensed families. Gamepad capture is supported in code; no physical controller was available for hardware validation.

## Files for Claude

- index.html: explorer toolbar, viewport, shared dropdown, dialog and comparison panel.
- style.css: local fonts, tokens, responsive layouts, controls, chamfered frames, HUD and inventory.
- app.js: screen definitions, SVG icon/map drawings, view rendering, navigation, local persistence and interactions.
- assets/: logo SVGs, five font files and font licenses.
- references/: selected source PNGs and manifest, used only by Compare concept.

Integrate shared components and state into the existing game at its own application boundary. This standalone prototype does not modify the Godot project or Claude's live implementation.

## Verification

Browser checks covered all 31 views: nonempty rendering, navigation, no horizontal overflow at the current desktop viewport, and no console errors. Interaction checks covered dropdown keyboard selection and persistence after reload, category reset, rebinding conflicts and resolution, callsign editing, lobby flow, inventory move/equip/Tab navigation, and a downloaded local report. Screenshot review covered main menu, settings/dropdown, HUD and inventory; observed frame/spacing and Tab navigation errors were repaired.

Responsive CSS is supplied for compact layouts; viewport-specific mobile and physical controller validation remain for integration. No backend, combat, frame-rate, or game rendering performance claims are made by these checks.
