# Kong Royale design system (premium v3)

> Source: RET's Kong Royale feedback, design system v3 (10 Oct 2026).
> Files that go with it: `kong-logos.zip` (transparent PNG logo exports) and `kong-implementation-prompts.md`.
> Logos come as SVG (vector, in `svg/`) and transparent PNG, recoloured to the production saffron. The SVGs are auto-traced from the concept sheet; give them a designer pass for optical kerning and small-size variants before treating them as final masters.


Status: proposed design system accompanying premium v3 concepts. Earlier blue-panel v2 layouts are superseded. This is not an implemented game UI. The written rules below take precedence when a generated image varies from them.

## Direction

Kong is energetic, confident and playful. The interface is calm, readable and predictable. Let the gorilla characters, banana weapons, island art and audio deliver personality. Use brand yellow with purpose rather than outlining everything in it.

Studio quality comes from consistent components and complete interaction behavior as much as appearance. Every screen should share navigation, control placement, text hierarchy, input feedback and error handling.

## Brand architecture

The parent brand is KONG. KONG ROYALE and KONG OF DUTY are two game identities in the same family.

Keep a single master KONG wordmark asset. Its letterforms, brow motif in the O, proportions and spacing must never be regenerated per game. Use ROYALE or OF DUTY as a separate descriptor beneath it. Both descriptors use the same type treatment, height and baseline; do not stretch them to the same width.

The proposed brand concept uses a geometric wordmark with a gorilla-brow motif. The supplied logo image is a raster concept sheet. It still needs a deliberate vector redraw, optical kerning and small-size variants before becoming a production master. Do not crop the brand presentation and treat it as final logo artwork.

### Lockup rules

- Primary stacked lockup: KONG above the descriptor. Descriptor cap height approximately 16% of the KONG cap height; gap approximately 14% of the KONG cap height.
- Clear space: at least 25% of KONG cap height on every side.
- Use yellow KONG plus ivory descriptor on navy; use a single navy mark on light surfaces.
- Start testing full lockups at 160 logical pixels wide. Below that, use the KONG master or dedicated brow emblem; verify actual readability before fixing a minimum.
- Use the full brand on lobby and loading screens. Keep a compact brand in settings if needed. Omit it from routine in-match dialogs.
- No extrusion, bevels, crowns, planks, gradients or foliage attached to the mark.
- Background art can differ between Royale and Of Duty. The brand and core UI components stay consistent.
- Do not invent a new Of Duty palette until its art direction is known. Both games initially inherit the same core tokens.

## Color tokens

| Token | Value | Purpose |
|---|---|---|
| background | #101719 | Full-screen menu foundation |
| surface | #172022 | Panels and dialogs |
| surface-raised | #253033 | Hover and selected surfaces |
| border | #465052 | Subtle dividers and outlines |
| text-primary | #EEEADF | Labels, headings, important values |
| text-secondary | #A5B1A4 | Descriptions and supporting information |
| accent | #EABC39 | Primary action, active indication, health |
| text-on-accent | #101719 | Text inside yellow controls |
| shield | #58BCEB | Shield and associated icon |
| success | #7AD7A5 | Saved/connected state |
| warning | #FFC16E | Match continues and caution |
| danger | #FF8C88 | Errors, destructive confirmation |
| focus | #EEEADF | Visible input focus ring |

Use a label or icon with status colors. Rarity also needs a visible text label. Never communicate state solely through hue.

These are candidate tokens, not a claim of complete accessibility validation. Measure contrast on actual rendered backgrounds, including transparency and focus states. Prefer opaque panels behind controls; don't rely on blur for readability.

## Typography

Chosen families: **Changa One** for display (titles, headings, big HUD numbers) and **Barlow** / **Barlow Semi Condensed** for UI text. All are free Google Fonts under the SIL Open Font License, so they can be bundled with the game. Changa One ships in one weight (Regular, plus Italic): set display text at that weight and disable synthetic bold (`font-synthesis-weight: none`).

One display family and one readable UI family, selected and licensed once. Prefer a strong moderately condensed display with deliberate proportions; use the UI sans-serif for descriptions, settings, numbers and navigation. Do not stretch letterforms to fit. Bundle actual font files rather than relying on different machine fallbacks.

Logical sizes on a 1920×1080 reference canvas:

| Role | Size / line height | Weight |
|---|---|---|
| Lobby display | 96 / 96 | Changa One Regular |
| Settings/page title | 72 / 80 | Changa One Regular |
| Context heading | 28 / 34 | Semibold |
| Control label | 20 / 28 | Medium |
| Body/help | 18 / 27 | Regular |
| Category navigation | 16 / 22 | Semibold |
| Supporting text | 16 / 22 | Regular |
| Keycap | 16 / 20 | Semibold |
| Important HUD number | 36 / 40 | Changa One Regular |

Display hierarchy can be large while body copy remains comfortable. Use uppercase and restrained tracking for short navigation/eyebrows only. Keep descriptions and setting labels in sentence case. Use tabular numerals. Never shrink critical text to preserve a layout.

## Spacing and shape

Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64 logical pixels.

- Screen safe area: start at 48px on the reference canvas; respect platform safe areas and user scaling.
- Panel padding: 24px. Dialog padding: 32px.
- Columns: 24px gutters.
- Standard control height: 48px; major action height: 56px.
- Settings row: minimum 64px, expanding for content and text scaling.
- Button horizontal padding: 20–24px.
- Control radius: 2px; necessary panel radius: 4px; keycap radius: 2px. Most rows and navigation entries have no enclosing rectangle.
- Border: 1px. Focus ring: 2px with 2px offset.
- Avoid decorative corner cuts and per-screen radius variations.
- Align labels to a consistent left edge and numeric values to a consistent right edge.

## Reusable layout templates

### Settings shell

A typographic full-screen page: compact brand at top left, Back at top right, large Settings title, one horizontal category bar, one local section bar, continuous settings table and secondary help area. No category sidebar and no separate card for each row.

Category order is fixed: Mouse & keyboard, Controller, Audio, Video, Accessibility. Omit unrelated global navigation while inside Settings. Generative variants sometimes add it; do not implement that drift.

Reference geometry: 80px outer horizontal margins, bounded content width up to 1760px, table about 64% and contextual area about 27% with a generous gutter/divider. Rows start around 80px high, adjust for content. Short fixed tracks align as one control column. Select/focus uses a subtle flat row tint plus a slim accent marker; visible focus ring is available when needed.

All five categories must share title, category/tab baselines, row start, control column and footer. Only data and contextual content change. On ultrawide, center the bounded layout.

Local tabs show only their content. Mouse does not contain Behavior rows. Volume does not contain Voice options. Display does not contain Graphics options. Keep options reachable without dumping all sections into one long scroll.

On narrower layouts or enlarged text, collapse contextual help below the active row. Category navigation may wrap or horizontally scroll with explicit focus visibility. Preserve reading size rather than miniaturizing the entire screen.

### Overlay and guide shell

Match menu is left-aligned typographic navigation over a full-height scrim. No centered stack of button cards. Resume comes first, Leave match is separated, and Match continues is accurate.

Report replaces Menu with a dedicated form composition. Only one active overlay owns focus. Guide uses a full-screen educational layout with lesson index, authored instruction area, progress and footer actions. Routine exit/reset confirmations use a restrained compact dialog.

Keep controls inside safe areas. Content can scroll at enlarged text sizes. Back returns to the previous context and restores focus.

### Gameplay shell

Minimap top left, compass top center, match stats top right, health/shield bottom left, ammo and equipment bottom right.

Damage and healing feedback: damage is always red, whether it hits shield or health. Show a red arc around the crosshair pointing at the shooter, a red glow on that screen edge, and a short flinch; below 30 health keep a slow red vignette. Blue is reserved for healing: a glow around every screen edge while a heal runs, with health refilling gradually. Taking damage interrupts the heal and ends the blue glow.

Enemy hit numbers: hits on shield show a small shield icon in shield blue beside the number; the hit that empties the shield shows a larger cracked shield icon, a "Shield broken" confirmation and a distinct crack sound. Health hits are plain white numbers. Icons: `icons/kong-shield-hit.svg` and `icons/kong-shield-break.svg` (shield blue #58BCEB, dark crack line), shown at 28 px and 46 px on the 1920×1080 canvas.

Match stats are two rows of slanted translucent chips. Row one is match state: squads left (squad modes) and players left. Row two is the player's contribution: kills and damage, plus assists and combined squad kills in squad modes. A Match stats setting offers Auto, Personal, Squad and Hidden; Auto shows Squad in squad modes. Changed numbers pop briefly in saffron, and Eliminated / Assist confirmations appear briefly under the crosshair. Prefer typography and short gradient backplates to a collection of framed HUD cards. Use the same safe-area settings. Keep the center clear. Optional diagnostics occupy one dedicated region, hidden by default.

### Map shell

Map dominates the screen. Header shows match state and Close. Legend is a bounded side panel. Marker actions belong in a bottom keycap strip. Hide unrelated gameplay panels while the map is open.

### Lobby/loading shell

Artwork leads. Cinematic menu camera, confident editorial display typography, moderate-scale brand lockup, one clear action or progress state, and unboxed functional groups. Contextual hints change with the current screen.

Match results uses the same shell: outcome eyebrow and display headline, placement, one typographic stats row with new bests marked, a quiet personal-best line, optional 1–5 ratings and a single Back to lobby action. Celebration effects are a short one-shot burst and respect reduced motion.

## Component contracts

### Button

Primary: flat saffron fill with dark text, nearly square corners. Secondary: quiet charcoal treatment or text separated by a rule; avoid outlining every action. Tertiary: text with full focusable hit area. Destructive: neutral entry action; danger treatment in the confirmation dialog. Keep icons optional and consistently aligned.

No more than one dominant primary action per task region. Selected segmented controls are choices, not primary actions; use a subtle surface and slim accent indicator.

### Navigation and tabs

Inactive: secondary text. Active: primary text, raised surface and slim yellow marker. Focus: ivory ring in addition to the active marker. Category order, icon style and alignment never change between screens. Prefer typographic navigation; use icons only when they add meaning.

### Slider

Label, fixed-width track, numeric value. Support pointer drag, keyboard arrows and controller adjustment, plus direct numeric entry where appropriate. Display units. Track width typically 280–360px on the reference canvas. Use a comfortable hit area beyond the visible track.

### Switch

Label and explicit On/Off text. Thumb position and appearance convey state. Focus ring surrounds the full control. Do not depend on a white square whose meaning is unclear.

### Select/segmented choice

Use segmented choice for short sets; dropdown for longer lists. Selected styling follows the tab rules. Support input focus, expanded state, scrolling and selection confirmation.

### Binding control

Two consistent binding slots where supported. Capture state says Press a key or button. Show Cancel and Clear hints. Give useful feedback for a conflict. Keep existing conflict policy consistent rather than silently changing it.

### Inventory card

Slot index, item art, name, rarity label, relevant stat. Rarity tints the flat plane behind the item art with a soft radial gradient and a 2px rule underneath: common green (rgb 92,184,104), rare blue (rgb 74,140,232). The rarity label uses the same hue. Keep the card itself charcoal so rarity never competes with the selected outline. Selection uses ivory outline; equipped uses a separate badge. Empty slots remain quiet. Equip, Move and Drop are explicit alternatives to drag. Treat selected, equipped and rare as separate states.

### Keycaps and icons

One shared input-prompt system renders keyboard, mouse and controller glyphs based on the actual binding/device. Do not hard-code shortcuts into screen art. Icons use the same stroke weight and optical size, typically a 24px box and 2px stroke. Pair unfamiliar icons with labels.

### Toast/status

Short, specific feedback, one location per context. Saved is a quiet checkmark and text, not a yellow button. Error feedback explains what happened and how to recover. Connection/FPS alerts should be actionable and avoid repeated telemetry.

## Required interaction states

Every interactive component needs default, hover, focus, pressed, selected/checked where relevant, disabled and error states. Forms also need submitting and success states.

- Hover raises the surface slightly.
- Focus uses the ivory ring and remains visible with keyboard/controller input.
- Pressed darkens the surface or slightly shifts its appearance without moving surrounding layout.
- Disabled retains readable text and a clear disabled cue; avoid blanket low opacity.
- Invalid input has an error icon, concise message and recovery path.
- Report submission shows Sending, prevents duplicate submission, then confirmation or retry.
- Unsaved behavior must be explicit. Current settings apply instantly and save on this device; keep that model.
- Reset confirms the affected category before restoring it.
- Leave match requires confirmation and clearly communicates the consequence.

## Input, motion and responsive behavior

Esc goes back one layer. On the root match menu it resumes gameplay. Opening a dialog moves focus inside it; closing restores focus to the trigger. Gameplay controls must not fire through an open menu. Keep controller focus order predictable and restore the last selected setting.

Settings sliders support fine adjustments. Focused rows stay in view. Inventory actions support keyboard/controller alternatives to drag. Map controls respect the current bindings and avoid conflicting with gameplay input.

Motion tokens: fast 120ms, standard 180ms, slow 240ms, ease-out. Use brief opacity/surface transitions; avoid constant pulsing, large zooms and layout shifts. Reduced motion removes nonessential animations.

Use a logical reference canvas with responsive constraints rather than uniformly scaling everything to the viewport. Test 16:9, 16:10, ultrawide, smaller window sizes, and increased text/HUD scales. Constrain reading width on ultrawide screens; HUD anchors remain at safe edges.

## Implementation discipline for a vibe-coded game

Build shared components first: ScreenShell, SettingsShell, DialogShell, Button, Tabs, SettingRow, Slider, Switch, Select, Keycap, Status, InventoryCard and HUDGroup. Screens compose them instead of defining their own styles.

Reference semantic tokens instead of raw colors or one-off sizes. Use one overlay manager and one input-focus manager. Keep settings configuration separate from presentation so labels, defaults, values, units and explanations stay consistent.

A screen is ready when its states work, navigation is coherent, focus is visible, text scales without clipping, controller/pointer behavior is tested, and it matches the shared tokens. A screenshot alone cannot establish usability.

## Implementation order

1. Finalize the logo vector master and shared token names.
2. Build button, typography, focus, keycap and settings row primitives.
3. Implement the common settings shell and one category.
4. Implement Menu, Report and Guide through one dialog system.
5. Apply the gameplay HUD, map and inventory templates.
6. Finish lobby/loading art presentation and input hints.
7. Review every screen together for drift and test real input paths.

## Concept limitations and final consistency pass

Image generation is useful for art direction but can drift in logo proportions, surface opacity, category geometry, selection styling and tab contents. Treat the images as screen compositions; use this document and tokens.css as the implementation source of truth.

Normalize all settings titles, horizontal category navigation, tab positions, table columns, footer placement and descriptor lockups during implementation. Reject extra navigation introduced in individual generated variants. Keep setting-table backgrounds calm and opaque enough for consistent contrast. Atmospheric art can sit behind the overall scrim, but not create bright texture behind labels. Do not adopt generated values, shortcuts or controller mappings without verifying the actual game.


## Art direction and content constraints

Premium v3 uses warm dusk lighting, controlled contrast and cinematic menu composition. This is a presentation direction, not an instruction to change the core game into a different visual genre. Character/weapon identity remains playful and stylized. Use real game assets and approved key art.

The lobby illustration proposes a new camera and lighting setup; it must not misrepresent what gameplay looks like. Loading can use separate authored key art. Gameplay HUD concepts should remain faithful to the actual renderer.

Use one restrained hero statement only where marketing copy is appropriate. Do not spread slogans through settings and utility screens. The proposed Rule the island line is optional copy, not a new game feature.

## Component appearance override for premium v3

Use continuous rows and thin rules rather than stacked cards. Allow intentional negative space. Primary color is reserved for an action or a meaningful selection marker. Metadata and attachment summaries remain quiet. Individual screens can have distinct compositions while sharing typography, tokens, focus and input language.

The same KONG master appears in Royale and Of Duty. The initial logo sheet uses brighter yellow as a brand exploration; production UI uses saffron #EABC39. Normalize the final master to the approved accent color rather than using two competing yellows.

## Acceptance review

Review screens as one set: title baselines, navigation order, body size, control alignment, footer treatment, accent frequency and logo geometry. Verify real keyboard/controller paths, editable values, binding capture, loading/error/success states, actual attachment data, adaptive scaling and combat readability.

Images are art direction, not pixel-exact component specifications. Any generated shortcut, hardware spec, stat or mapping is illustrative until verified against code. The source tokens and documented component contracts define implementation.


## Tokens (CSS)

```css
/* Kong premium v3 — proposed semantic tokens. Framework-neutral handoff;
   not installed in a game. Sizes use a 1920x1080 logical reference canvas. */
:root {
  --kong-bg: #101719;
  --kong-surface: #172022;
  --kong-surface-raised: #253033;
  --kong-border: #465052;
  --kong-text: #EEEADF;
  --kong-text-muted: #A5B1A4;
  --kong-accent: #EABC39;
  --kong-on-accent: #101719;
  --kong-shield: #58BCEB;
  --kong-success: #7AD7A5;
  --kong-warning: #FFC16E;
  --kong-danger: #FF8C88;
  --kong-focus: #EEEADF;
  --kong-space-1: 4px;
  --kong-space-2: 8px;
  --kong-space-3: 12px;
  --kong-space-4: 16px;
  --kong-space-6: 24px;
  --kong-space-8: 32px;
  --kong-space-12: 48px;
  --kong-space-16: 64px;
  --kong-control-height: 48px;
  --kong-primary-height: 56px;
  --kong-setting-row-min: 80px;
  --kong-control-radius: 2px;
  --kong-panel-radius: 4px;
  --kong-border-width: 1px;
  --kong-focus-width: 2px;
  --kong-focus-offset: 2px;
  --kong-motion-fast: 120ms;
  --kong-motion-standard: 180ms;
  --kong-motion-slow: 240ms;
  --kong-ease: cubic-bezier(0.2, 0.8, 0.2, 1);
}
/* Resolve actual licensed font assets before implementation.
   Do not use generated screenshot fonts as production source files. */
@media (prefers-reduced-motion: reduce) {
  :root {
    --kong-motion-fast: 0ms;
    --kong-motion-standard: 0ms;
    --kong-motion-slow: 0ms;
  }
}

```

## Logo files

Each file below comes as `.png` (transparent) and as `svg/<name>.svg` (vector).

| File | Use |
|---|---|
| kong-royale-lockup.png | Primary stacked lockup on dark surfaces (lobby, loading) |
| kong-of-duty-lockup.png | Kong of Duty lockup on dark surfaces |
| kong-royale-lockup-navy.png / kong-of-duty-lockup-navy.png | One-colour lockups on light surfaces |
| kong-wordmark-saffron.png | Parent KONG master, compact headers |
| kong-wordmark-ivory.png | One-colour master on dark |
| kong-wordmark-navy.png | One-colour master on light |
| kong-brow-icon.png | Small icon / avatar, below 160px wide |
| kong-brand-family-concept-sheet.png | Original concept sheet (brighter exploration yellow) |
