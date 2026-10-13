# Orbit Royale — sci-fi UI v0.2

This collection applies the angular main-menu direction to the remaining 27 screens. The matching main menu is included as the 28th reference. User direction: make the interface itself feel more sci-fi; the background will be replaced.

Open [the gallery](index.html) to filter and view all selected screens. [Manifest](manifest.json) identifies selected files; [prompts](prompts.md) records built-in image_gen generation and refinement instructions. Six initial drafts are retained alongside selected refinements for traceability.

## Coverage

- 14 settings views: mouse tuning, behavior, keyboard bindings; controller layout, look, deadzones, bindings; audio volume and planned voice; video display and graphics; accessibility readability and comfort; gameplay HUD settings.
- 10 menus: main menu, solo lobby, asset download, match preparation, match menu, local problem report, controls guide, map, victory, elimination.
- 2 confirmations: reset category and leave match.
- 2 gameplay views: HUD and five-slot inventory.

## Visual system for Claude

Use the selected PNGs as composition targets and rebuild the UI as real components. Prefer the main menu for branding and the mouse settings screen for the shared settings shell. Suggested values below are the prompt specification; generated pixels can vary.

| Role | Color |
| --- | --- |
| Canvas | #0B101B |
| Panel | #141D2D |
| Selected panel | #213047 |
| Primary text | #F3F5FA |
| Secondary text | #B4BFD0 |
| Selection / brand | #C5F277 |
| Health | #FF8D7F |
| Shields | #70D6FF |

Square-shouldered, extended geometric display lettering carries headings; readable technical sans carries labels and help; monospace is reserved for indices and numeric readouts. Select licensed production fonts with similar proportions; the raster lettering is not a font asset.

Use restrained chamfered corners, thin structural rules, continuous setting tables, aligned slider tracks and values, and thick lime selection brackets. White outlines add keyboard focus independently of selection. Coral denotes destructive actions. Icons, text and shapes must communicate states together.

Settings share six horizontal categories, local tabs, a large continuous controls table and a narrower contextual help panel. Keep the same footer and row baseline system across categories. Cancel/Stay receives initial modal focus. The settings shell remains visible behind the reset dialog.

The HUD leaves the center clear except for a small crosshair. Place minimap upper-left, compass top-center, remaining players/eliminations upper-right, health/shields lower-left, five-slot hotbar lower-center, weapon ammunition lower-right. Inventory has exactly five slots: two weapon slots, three utility/consumable slots. Ammo reserves are informational, not additional slots. Shown stacks are examples from prior planning, not a newly approved balance change.

## Review and implementation notes

All selected images were visually reviewed. Six refinements corrected settings preview slots, lobby character clutter, match-loading scenery, match-menu scenery, reset-shell consistency and the missing HUD crosshair. The plain navy canvas is opaque; these are not transparent overlays.

Use the full inventory and HUD as the authority for item shapes. Tiny settings-preview icons remain schematic and may resemble generic tools; replace them with the approved Tethercaster and FieldPatch icons. Generated slider positions, focus hints, weapon thumbnails and map silhouettes are illustrative; rebuild them from live state and canonical assets. Match menu's extra “F Open” footer hint is a generated artifact and should be omitted. Simplified HUD beneath the leave dialog is backdrop context, not a second hotbar specification.

No gameplay code changed. These images propose UI appearance, not implemented features or new rules. Voice is explicitly a planned online feature. Report is a local export concept. Use actual download progress, browser capabilities, current bindings, connected-controller state, and persisted settings in implementation.

Kong Hybrid supplied the earlier screen-flow structure. Orbit Royale branding, palette and this angular treatment are separate visual proposals. Current shared docs and explicit user requirements take precedence over decorative details in generated art.

## Selected screen files

- [Mouse & keyboard — Mouse](01-mouse-tuning.png)
- [Mouse & keyboard — Behavior](02-mouse-behavior.png)
- [Mouse & keyboard — Bindings](03-keyboard-bindings.png)
- [Controller — Layout](04-controller-layout.png)
- [Controller — Look](05-controller-look.png)
- [Controller — Deadzones](06-controller-deadzones.png)
- [Controller — Bindings](07-controller-bindings.png)
- [Audio — Volume](08-audio-volume.png)
- [Audio — Voice](09-audio-voice.png)
- [Video — Display](10-video-display.png)
- [Video — Graphics](11-video-graphics.png)
- [Accessibility — Readability](12-accessibility-readability-refined.png)
- [Accessibility — Comfort](13-accessibility-comfort.png)
- [Gameplay — HUD](14-gameplay-hud.png)
- [Main menu](15-main-menu.png)
- [Solo lobby](16-lobby-refined.png)
- [Downloading assets](17-asset-loading.png)
- [Preparing match](18-match-loading-refined.png)
- [Match menu](19-match-menu-refined.png)
- [Report a problem](20-report.png)
- [Learn controls](21-learn-controls.png)
- [Ringfall map screen](22-map-screen.png)
- [Victory results](23-victory-results.png)
- [Elimination results](24-elimination-results.png)
- [Reset settings confirmation](25-reset-confirmation-refined.png)
- [Leave match confirmation](26-leave-confirmation.png)
- [Gameplay HUD](27-gameplay-hud-refined.png)
- [Inventory screen](28-inventory-screen.png)
