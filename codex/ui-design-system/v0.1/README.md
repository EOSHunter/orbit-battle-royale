# Orbit Royale — menu and UI design system v0.1

A concrete visual system derived from the angular sci-fi main menu and the 28-screen UI concept collection. Scope: menus, settings, loading, dialogs, inventory and HUD presentation. This does not define world art, models, gameplay balance or rendering.

## Start here

- [Visual style guide and interactive component samples](index.html).
- [Primary transparent SVG logo](logos/orbit-royale-primary.svg).
- [Color, type, spacing and motion tokens](tokens.json).
- [Browser CSS and bundled local fonts](tokens.css).
- [Font provenance and licenses](fonts/README.md).
- [Logo preview](logo-preview.png).

The logo is a deliberate vector reconstruction of the concept's ORBIT / ROYALE lettering and orbital O. It is not a pixel-perfect trace. All lettering is drawn geometry; no installed font, raster image or external resource is required. SVG backgrounds are transparent. Artwork is flat, with no baked glow or bevel.

## Logo masters

| Asset | Use |
| --- | --- |
| orbit-royale-primary.svg | Ivory lettering / lime ring on dark UI; default stacked lockup |
| orbit-royale-dark.svg | Navy lettering / dark green ring on a light surface |
| orbit-royale-mono-light.svg | All ivory on dark surfaces |
| orbit-royale-mono-dark.svg | All navy on light surfaces |
| orbit-royale-horizontal.svg | Wide headers with smaller ROYALE to the right |
| orbit-emblem-primary.svg | Compact planetary O and ring |
| orbit-emblem-dark.svg | Dark emblem for light surfaces |
| orbit-emblem-mono-light.svg | Single-color light emblem |
| orbit-emblem-mono-dark.svg | Single-color dark emblem |

Files live in logos/. Use the same SVG master across screens. Default stacked aspect ratio is 980:340. Keep at least 42 SVG units of additional clear space outside the asset bounds, equivalent to the ORBIT stroke thickness. Reserve 16px around compact emblems at typical header size.

Proposed minimum stacked display width: 220 CSS px. Below that, switch to the emblem rather than forcing ROYALE to become unreadable. Emblem minimum: 48px. These are initial usage limits; verify at actual game scale and displays. Do not stretch, skew, recolor individual letters, animate the ring continuously, or place a thin unbacked logo over a busy scene.

## Typography

The generated lettering is not a usable font. These production font choices interpret its proportions and mood:

| Role | Family | Weight | Use |
| --- | --- | --- | --- |
| Display | Oxanium | 700; 800 for hero | Screen titles, headings, major actions |
| Interface | Barlow | 400 / 500 / 600 | Help text, labels, secondary actions |
| Numeric | IBM Plex Mono | 500 | Ammo, sensitivity, timers, indices, key prompts |

Five original TTF files are bundled with their licenses. Oxanium is variable (200–800); use 700/800 in the UI. No network request is needed by the preview. Fallbacks are included in CSS. Preserve each font's included OFL license when shipping.

| Style | Size / line height | Tracking | Case |
| --- | --- | --- | --- |
| Hero / result title | 64px / 1.05 | .02em | Uppercase |
| Screen title | 48px / 1.10 | .02em | Uppercase |
| Section heading | 28px / 1.15 | .02em | Uppercase |
| Primary menu action | 24px / 1.20 | .06em | Uppercase |
| Setting / item label | 20px / 1.30 | Normal | Sentence case |
| Help / paragraph | 18px / 1.50 | Normal | Sentence case |
| Caption / status | 14px / 1.40 | .08em | Short uppercase labels only |
| Numeric readout | 24px / 1.20 | Normal | Tabular numbers |

Sizes are reference values for a 1920×1080 desktop layout, not mandatory physical pixels on every viewport. Scale layout intentionally, keep readable labels at least 16px on compact layouts, and support user text/HUD scaling without clipping. Do not compress text horizontally or add large tracking to paragraphs. Larger accessibility text may require fewer visible rows and scrolling.

## Colors and semantics

| Token | Hex | Purpose |
| --- | --- | --- |
| canvas | #0B101B | Foundation |
| surface | #141D2D | Solid menus, settings, dialogs |
| raised | #213047 | Hover / selection surface |
| border | #73849B | Meaningful control outlines |
| borderQuiet | #33445B | Decorative rules and separators |
| text | #F3F5FA | Primary labels |
| muted | #B4BFD0 | Help and secondary labels |
| accent | #C5F277 | Selection, primary action, brand |
| onAccent | #0B101B | Text on lime or coral fill |
| danger | #FF8D7F | Destructive actions and health |
| shield | #70D6FF | Shields |
| focus | #FFFFFF | Keyboard/controller focus |
| scrim | rgba(5,8,14,.82) | Dialog separation |

Lime communicates selection; white communicates focus. A selected item can retain lime while a different control has white focus. Health and shields always include distinct icons and labels alongside color.

Calculated opaque color pairs: primary text on surface 15.48:1, muted text on surface 9.09:1, muted on raised 7.16:1, navy on lime 14.80:1. These are numerical checks of these pairs, not a certification of every screen. The meaningful border token was brightened from the art so controls remain distinct on raised surfaces. Quiet rules are decorative and cannot be the only control boundary. Back actual UI with a stable dark surface when the background becomes scenic.

## Geometry and spacing

Use the 4px grid: 4, 8, 12, 16, 24, 32, 48, 64 and 96px. Default panel padding 24px, section gap 32px, row height 64px, control height 48px. Minimum pointer target 44×44px. Separate adjacent destructive and safe actions by at least 16px.

Panel chamfer: 16px. Control chamfer: 8px. Structural rule: 1px. Selected boundary: 2px lime with a 5px left bracket. Focus: 3px white outline offset 5px. Keep corners and bracket sizes consistent; they do not scale with every panel's width. Avoid bevels, noisy scanlines, heavy glow and unrelated decorative telemetry.

The included CSS panel clip is a starting sample. For production, use an SVG/nine-slice frame or a separate decorative frame layer if perfect continuous corner strokes are needed. Keep focus outlines on an unclipped interactive wrapper; never clip a focused child at a panel boundary. Browser controls in the preview stay native and accessible; reskin their geometry only while preserving semantics and keyboard behavior.

## Component contract

| Component | Required states and behavior |
| --- | --- |
| Menu action | Default, hover, pressed, selected, focus, disabled; title and optional decorative index/arrow |
| Category tabs | One selected category; labeled icons; local tabs below; arrow-key navigation in a proper tab implementation |
| Setting row | Label, real value, control; aligned tracks; selected/help relationship; focus stays visible |
| Slider | Label and numeric output; keyboard adjustment; bounded min/max; visible thumb; current value persists |
| Choice / toggle | Explicit value such as On/Off; shape/text alongside color; no ambiguous light alone |
| Binding row | Action, current binding, rebind and clear; capture prompt; conflict message with resolve/cancel |
| Dialog | Heading, short consequence, safe and destructive actions; focus trap; Escape cancels; restore trigger focus |
| Progress | Actual percentage if known; indeterminate otherwise; named loading stage; retry/cancel on failure |
| Inventory slot | Slot number, approved item icon, ammo/quantity; selected frame; compatible move/drop actions |
| Status / toast | Icon plus plain text; quiet confirmation; explicit error guidance; no unexplained code alone |

Disabled controls show a reason, not merely faded styling. Hover uses raised surface and a brighter outline. Pressed uses a slightly darker fill without shifting position. Never imply unavailable multiplayer/voice is active. Rebinding must support cancellation and detect conflicts; choose a clear action instead of silently overwriting.

## Screen layouts

Main menu: dominant stacked logo upper-left; left navigation stack; right space reserved for the user's background. Keep only current actions; indices are decorative. Lobby: mode/map/population, primary Start Match, callsign and controls link. Present population truthfully from current lobby state.

Settings: six horizontal categories (Mouse & keyboard, Controller, Audio, Video, Accessibility, Gameplay), local tabs, one continuous left controls table, contextual help at right, and stable footer. Desktop content ratio approximately 64% controls / 28% help / 8% gap. Below 1000px, move help beneath controls and let category navigation scroll; do not shrink all labels. On short displays, scroll the rows while keeping navigation and actions available.

Loading: distinguish asset download from match preparation. Do not fabricate network speeds, performance counters or completion percentages. Use a checklist and determinate/indeterminate progress appropriately.

Match menu: Resume, Settings, Learn Controls, Report a Problem and Leave Match. Describe whether the simulation continues according to actual runtime behavior. Do not copy the generated extra “F Open” prompt.

Map: functional map content inside the frame; symbol/text legend, player marker, zones and timer. Do not reveal unseen opponents. HUD: minimap upper-left, compass top-center, population/eliminations upper-right, health/shields lower-left, five-slot hotbar lower-center, ammunition lower-right, small white center crosshair. Inventory: two weapon slots, then three utility/consumable slots; separate ammo-reserve readout.

Results: placement and real match statistics, Play Again and Return to Lobby. Confirmations: safe Cancel/Stay is initially focused; destructive action is coral and explicit. All examples preserve existing mechanics; no balance values are changed here.

## Input, accessibility and motion

All controls must be reachable with mouse, keyboard and controller. Reflect the active input device in prompts using the player's current binds. Tab/Shift+Tab move focus through browser UI controls. A production settings tablist uses Left/Right, Home/End and Enter/Space as appropriate; the style-guide tabs are a visual category selector, not a complete game settings implementation.

Use labeled controls, visible focus, icons with text, distinct health/shield shapes, adjustable text/HUD scale, reduced motion and high-contrast presentation. Help should stay available when a controller focuses a row. Avoid making hover the only way to discover information.

Base hover transition 120ms, panel reveal 180ms, maximum ordinary menu transition 220ms. Respect prefers-reduced-motion and the game's own accessibility setting by removing nonessential animation. Avoid flashes, looping logo effects and moving backgrounds inside settings tables. Accessibility support must be validated in the actual game.

## Implementation handoff

1. Pull codex/ui-design-system/v0.1 and read this document.
2. Import SVG masters; use consistent sizing and clear space.
3. Import bundled fonts, preserving licenses. For Godot, load the TTFs as font resources and recreate these semantic tokens in a Theme. CSS is a browser reference, not a Godot theme file.
4. Implement tokens centrally, then reusable menu action, frame, tabs, setting row, readout and modal.
5. Rebuild images as UI, not flattened screen textures. Replace schematic/generated icons with approved assets.
6. Connect controls to actual saved settings and runtime state; verify text scale, focus, controller prompts, small displays, and overlay contrast.

The guide is scoped to menu/UI presentation. It complements shared project documents and does not replace Claude's live game or the existing global planning documents.

## Font sources

Bundled originals downloaded 2026-10-13 from the Google Fonts repository:
- [Oxanium](https://github.com/google/fonts/tree/main/ofl/oxanium).
- [Barlow](https://github.com/google/fonts/tree/main/ofl/barlow).
- [IBM Plex Mono](https://github.com/google/fonts/tree/main/ofl/ibmplexmono).

Each repository directory includes its OFL license, preserved in fonts/. Font choices are design decisions, not exact identifications of AI-generated lettering.
