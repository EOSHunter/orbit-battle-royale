# Orbit Royale menu concepts v0.1

26 selected screen concepts generated using the built-in image_gen tool. Seven earlier drafts are retained alongside their refined selections, for 33 PNG files total.

## Browse

Open [index.html](index.html) in a browser. Filter by Settings, Menus, or Dialogs; search by name; click a preview for the full-size image. The gallery has keyboard focus and native dialog close behavior.

- [manifest.json](manifest.json): selected images and retained first drafts.
- [prompts.md](prompts.md): exact generation and refinement prompts.
- [reference-notes.md](reference-notes.md): observed Hybrid structure and Orbit adaptations.

## Coverage

Settings: Mouse tuning, mouse behavior, keyboard bindings; controller layout, look, deadzones and bindings; audio volume and planned voice; video display and graphics; accessibility readability and comfort; gameplay HUD.

Menus: main menu, solo lobby, downloading assets, preparing match, match menu, report a problem, learn controls, map, victory results, elimination results.

Dialogs: reset one settings category; leave the current match.

The existing first-person POV and inventory screen are retained in the earlier gameplay concept set. This set does not replace them or implement any screen.

## Visual review

All selected images were visually inspected. Refinements corrected the Controller Bindings active tab, help/row selection alignment for Audio and Gameplay, the accessibility preview's two weapon slots, a mixed-quality preset label, main-menu title hierarchy/stray trademark marks, and unwanted navigation on match loading.

The anchor is the Mouse settings screen. All settings views were generated from it to maintain title/tab/control/footer geometry. Non-settings screens use the same visual family with compositions appropriate to their tasks.

## Implementation handoff

- Use current shared tokens/components and approved asset geometry rather than tracing generated pixels into new one-off components.
- These are visual references, not Godot screenshots, functional settings, real asset downloads, or performance measurements.
- Values, keycaps, controller assignments, progress, placement, and statistics are examples. Compare with current game bindings and data before implementation. Several concept bindings describe the eventual shooter and differ from the current movement playground.
- Global settings categories retain Orbit's Gameplay category beyond the five categories in the Kong reference.
- Voice is illustrated as an unavailable planned online feature. A report screen is a proposed local feedback flow; no capture, logging, submission, microphone permission, or service is implemented by these images.
- Match-menu copy illustrates a match that continues. Actual local bot pause behavior remains a separate rules decision.
- Settings apply/save indicators depict intended behavior only. Real saving/error/unsaved states must be implemented and tested.
- Several simplified HUD preview glyphs remain illustrative and must be replaced by final weapons, grapple, and healing silhouettes. All production input prompts must derive from current bindings and input device.
- The dialogs' generated lime focus outlines must be normalized to the shared white focus token; focus and selected states must remain distinguishable.
- Typography, background opacity, scaled text, panel bounds, device glyphs, and small-size icons need implementation QA. The richer rendered-world art is a visual target, not a browser performance promise.
- The top-down map's location placement is illustrative; reconcile it with the final level. Do not infer new volcanos, mechanics, or approved map geometry from artwork.
- Main menu branding remains typographic exploration; use eventual approved vector logo masters for production.

Review the screens together for alignment and consistency, then verify keyboard, mouse, controller, focus restoration, no gameplay input through overlays, text/HUD scaling, and real state. Do not adopt proposed new settings as implemented features.
