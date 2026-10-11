// Writes components/<Name>/preview.html and README.md for the Orbit Royale design system.
// Run: node design-system/scripts/write-components.js
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..', 'project', 'components');

const doc = (marker, body, script = '') =>
  `${marker}\n<!doctype html>\n<html>\n<head><meta charset="utf-8"><title>preview</title></head>\n<body>\n${body}\n${script ? `<script>\n${script}\n</script>\n` : ''}</body>\n</html>\n`;
const ic = (name, cls) => `<span data-icon="${name}" data-cls="${cls || ''}"></span>`;
const iconScript = `document.querySelectorAll('[data-icon]').forEach(function (el) { el.outerHTML = Orbit.icon(el.dataset.icon, el.dataset.cls); });`;

const C = {};

C.ScreenShell = {
  marker: '<!-- @dsCard group="Layout" height=420 subtitle="Every full-screen menu: title, content, input prompts" -->',
  body: `<div class="or-shell" style="min-height:400px">
  <div class="or-shell__top">
    <div><div class="or-eyebrow">Solo · Ringfall</div><h1 class="or-shell__title">Lobby</h1></div>
    <button class="or-btn or-btn--ghost">Settings</button>
  </div>
  <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:24px;flex-wrap:wrap">
    <p style="margin:0;max-width:52ch;color:var(--text-secondary)">1 player and 59 bots. Online matchmaking is not available yet.</p>
    <button class="or-btn or-btn--primary">Start match</button>
  </div>
  <div class="or-shell__foot">
    <div class="or-shell__prompts">
      <span class="or-prompt"><span class="or-keycap">Enter</span> Select</span>
      <span class="or-prompt"><span class="or-keycap">Esc</span> Back</span>
    </div>
    <span class="or-eyebrow">v0.1 preproduction</span>
  </div>
</div>`,
  readme: `# ScreenShell

The full-screen frame for loading, main menu, lobby, results and pause: a title row, a content region and a footer of input prompts.

**Consumer provides:** eyebrow (mode or context), title, one dominant action per region, footer prompts built from the player's current bindings.

- Inset content by \`space-12\` (48px at 1920x1080); keep the same inset across screens so titles never jump.
- Title in \`page-title\` (Archivo expanded). The main menu replaces it with the logo lockup once logo masters exist.
- One \`Button--primary\` per screen region. Secondary actions are ghost buttons.
- Footer prompts show the binding for the device in use: keyboard keycaps, or controller face buttons once a pad sends input.
- Back closes one layer and restores focus to the control that opened it.
- Reflow, don't shrink: under 1280px wide, stack the content region and keep body text at 18px.
`
};

C.SettingsShell = {
  marker: '<!-- @dsCard group="Layout" height=520 subtitle="Category tabs, section tabs, continuous rows" -->',
  body: `<div class="or-shell" style="min-height:500px;gap:24px">
  <div class="or-shell__top"><h1 class="or-shell__title">Settings</h1><button class="or-btn or-btn--danger">Reset Audio</button></div>
  <div class="or-settings">
    <div class="or-tabs" role="tablist">
      <span class="or-keycap or-keycap--sm or-tabs-bumper">Q</span>
      <button class="or-tab" role="tab">Mouse &amp; keyboard</button><button class="or-tab" role="tab">Controller</button>
      <button class="or-tab" role="tab" aria-selected="true">Audio</button><button class="or-tab" role="tab">Video</button>
      <button class="or-tab" role="tab">Accessibility</button><button class="or-tab" role="tab">Gameplay</button>
      <span class="or-keycap or-keycap--sm or-tabs-bumper">E</span>
    </div>
    <div class="or-tabs or-tabs--local" role="tablist"><button class="or-tab" role="tab" aria-selected="true">Volume</button><button class="or-tab" role="tab">Output</button><button class="or-tab" role="tab">Subtitles</button></div>
    <div class="or-setting-list">
      <div class="or-setting-row"><div><div class="or-setting-row__label">Master volume</div></div><div class="or-setting-row__control"><div class="or-slider"><div class="or-slider__track"><div class="or-slider__fill" style="width:80%"></div><div class="or-slider__thumb" style="left:80%"></div></div><span class="or-slider__value">80</span></div></div></div>
      <div class="or-setting-row is-hover"><div><div class="or-setting-row__label">Vehicle and aircraft cues</div><div class="or-setting-row__help">Boosts engine and rotor sounds of approaching vehicles.</div></div><div class="or-setting-row__control"><span class="or-switch-state">On</span><button class="or-switch" role="switch" aria-checked="true"></button></div></div>
    </div>
  </div>
</div>`,
  readme: `# SettingsShell

One full-screen shell for every settings category: page title, top category tabs, local section tabs, then continuous SettingRows.

**Consumer provides:** the six categories in this order — Mouse & keyboard, Controller, Audio, Video, Accessibility, Gameplay — the local sections of the active category, and its rows.

- Category tabs switch with the bumpers / Q and E; show those keycaps at the ends of the tab bar.
- Settings apply immediately and persist on this device. There is no Save button; confirm with a \`Toast--success\` only when persistence fails or succeeds after a delay.
- "Reset <category>" is a \`Button--danger\` in the title row and opens a Dialog naming exactly what resets.
- Constrain the content to 1120px wide; rows run edge to edge inside it. No card around each setting.
- Help text collapses below the label on narrow displays (SettingRow handles this).
`
};

C.Button = {
  marker: '<!-- @dsCard group="Actions" height=220 subtitle="Primary, secondary, ghost, danger; every state" -->',
  body: `<div class="or-stack">
  <div class="or-row" style="padding:0"><button class="or-btn or-btn--primary">Play</button><button class="or-btn or-btn--primary is-hover">Hover</button><button class="or-btn or-btn--primary" style="outline:2px solid var(--focus);outline-offset:2px">Focus</button><button class="or-btn or-btn--primary" disabled>Disabled</button></div>
  <div class="or-row" style="padding:0"><button class="or-btn">Settings</button><button class="or-btn is-hover">Hover</button><button class="or-btn is-pending">Connecting</button><button class="or-btn" disabled>Disabled</button></div>
  <div class="or-row" style="padding:0"><button class="or-btn or-btn--ghost">Credits</button><button class="or-btn or-btn--danger">Leave match</button><button class="or-btn or-btn--danger is-hover">Leave match</button></div>
</div>`,
  readme: `# Button

Triggers one action. Labels are verbs that say exactly what happens: "Play", "Start match", "Leave match", "Retry download".

**Consumer provides:** label, variant (\`or-btn--primary\`, default, \`or-btn--ghost\`, \`or-btn--danger\`), and an \`is-pending\` class while an async action runs.

- One \`--primary\` per task region, at \`primary-height\` (56px), \`accent\` fill with \`text-on-accent\`.
- Default buttons are \`surface\` with a \`border-control\` outline at \`control-height\` (48px).
- \`--danger\` for destructive or match-ending actions; always separated from Resume / Cancel by space or position.
- Focus is a 2px \`focus\` (white) ring offset 2px, so focus and the accent-filled selection never look alike.
- Pending keeps the button's width and swaps in a spinner; success and failure report through Toast, and failure offers Retry.
- Do not put icons alone in a button without a visible label, except the close button in a Dialog title row.
`
};

C.Tabs = {
  marker: '<!-- @dsCard group="Navigation" height=150 subtitle="Category tabs and local section tabs" -->',
  body: `<div class="or-stack">
  <div class="or-tabs" role="tablist"><button class="or-tab" role="tab">Mouse &amp; keyboard</button><button class="or-tab" role="tab" aria-selected="true">Controller</button><button class="or-tab is-hover" role="tab">Audio</button><button class="or-tab" role="tab" style="outline:2px solid var(--focus);outline-offset:-2px">Video</button></div>
  <div class="or-tabs or-tabs--local" role="tablist"><button class="or-tab" role="tab" aria-selected="true">Bindings</button><button class="or-tab" role="tab">Sensitivity</button><button class="or-tab" role="tab">Vibration</button></div>
</div>`,
  readme: `# Tabs

Switches between sibling views without leaving the screen. Used for settings categories (top) and sections within a category (local).

**Consumer provides:** tab labels in a fixed order and the selected index.

- Selected tab: \`text-primary\` label and a 3px \`accent\` underline. Unselected: \`text-secondary\`.
- Hover lifts to \`surface-raised\`; focus adds the white ring. Selection and focus stay distinguishable.
- Local tabs (\`or-tabs--local\`) are 40px tall at 18px so the hierarchy reads at a glance.
- On narrow screens the strip scrolls horizontally; never wrap tabs onto two lines.
`
};

C.SettingRow = {
  marker: '<!-- @dsCard group="Settings" height=330 subtitle="Label, help, and an aligned control column" -->',
  body: `<div class="or-setting-list" style="margin:24px">
  <div class="or-setting-row"><div><div class="or-setting-row__label">Field of view</div><div class="or-setting-row__help">Horizontal degrees. Higher values show more of Ringfall.</div></div><div class="or-setting-row__control"><div class="or-slider"><div class="or-slider__track"><div class="or-slider__fill" style="width:55%"></div><div class="or-slider__thumb" style="left:55%"></div></div><span class="or-slider__value">95°</span></div></div></div>
  <div class="or-setting-row is-hover is-modified"><div><div class="or-setting-row__label">Reduce motion</div><div class="or-setting-row__help">Removes nonessential menu transitions and camera shake.</div></div><div class="or-setting-row__control"><span class="or-switch-state">On</span><button class="or-switch" role="switch" aria-checked="true"></button></div></div>
  <div class="or-setting-row"><div><div class="or-setting-row__label">Quality preset</div></div><div class="or-setting-row__control"><select class="or-select"><option>High</option></select></div></div>
  <div class="or-setting-row"><div><div class="or-setting-row__label" style="color:var(--text-disabled)">Ray-traced shadows</div><div class="or-setting-row__help">Not supported by this browser.</div></div><div class="or-setting-row__control"><span class="or-switch-state">Off</span><button class="or-switch" role="switch" aria-checked="false" disabled></button></div></div>
</div>`,
  readme: `# SettingRow

One setting: a label and optional help on the left, its control in an aligned right column. Rows stack into a continuous list with hairline \`border\` rules.

**Consumer provides:** label, optional help text (one sentence, \`supporting\` style), one control (Switch, Slider, Select, stepper, BindingCapture), and \`is-modified\` when the value differs from the default.

- Minimum height \`row-min-height\` (72px); padding \`space-3\` / \`space-6\`.
- The whole row highlights \`surface-raised\` on hover and when its control has focus; the row is the controller navigation target.
- Disabled rows say why in the help text ("Not supported by this browser").
- Under 720px wide the control drops below the label.
- Never wrap a single row in its own card.
`
};

C.Switch = {
  marker: '<!-- @dsCard group="Settings" height=100 subtitle="On / off with a text state" -->',
  body: `<div class="or-row"><span class="or-switch-state">On</span><button class="or-switch" role="switch" aria-checked="true"></button><span class="or-switch-state">Off</span><button class="or-switch" role="switch" aria-checked="false"></button><button class="or-switch" role="switch" aria-checked="true" style="outline:2px solid var(--focus);outline-offset:2px"></button><button class="or-switch" role="switch" aria-checked="false" disabled></button></div>`,
  script: `document.querySelectorAll('.or-switch:not([disabled])').forEach(function (s) { s.onclick = function () { s.setAttribute('aria-checked', s.getAttribute('aria-checked') === 'true' ? 'false' : 'true'); var t = s.previousElementSibling; if (t && t.classList.contains('or-switch-state')) t.textContent = s.getAttribute('aria-checked') === 'true' ? 'On' : 'Off'; }; });`,
  readme: `# Switch

A binary setting that applies immediately (subtitles, reduce motion, toggle-to-aim).

**Consumer provides:** checked state; an \`or-switch-state\` label ("On" / "Off") beside it so state never depends on color.

- On: \`accent\` track, \`text-on-accent\` thumb. Off: \`background\` track with \`border-control\` outline.
- For hold-versus-toggle choices use a Select, not a switch: both options need names.
`
};

C.Slider = {
  marker: '<!-- @dsCard group="Settings" height=120 subtitle="Continuous values with a numeric readout" -->',
  body: `<div class="or-stack" style="max-width:420px"><div class="or-slider" id="s"><div class="or-slider__track"><div class="or-slider__fill" style="width:40%"></div><div class="or-slider__thumb" style="left:40%"></div></div><span class="or-slider__value">0.40</span></div></div>`,
  script: `var s = document.getElementById('s'), tr = s.querySelector('.or-slider__track');
function set(e) { var r = tr.getBoundingClientRect(); var p = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)); s.querySelector('.or-slider__fill').style.width = p * 100 + '%'; s.querySelector('.or-slider__thumb').style.left = p * 100 + '%'; s.querySelector('.or-slider__value').textContent = p.toFixed(2); }
tr.addEventListener('pointerdown', function (e) { set(e); tr.setPointerCapture(e.pointerId); tr.onpointermove = set; tr.onpointerup = function () { tr.onpointermove = null; }; });`,
  readme: `# Slider

Sets a value on a continuous or fine-stepped range: volumes, sensitivities, field of view, HUD scale.

**Consumer provides:** min, max, step, current value and a formatted readout ("95°", "0.40", "80").

- Always show the numeric value in \`tabular-nums\` to the right so it can be read and compared exactly.
- Left/right (keyboard or d-pad) moves one step; holding accelerates. Separate hip-fire and aim-down-sight sensitivities are two sliders.
- Fill in \`accent\`, track in \`border-control\`.
`
};

C.Select = {
  marker: '<!-- @dsCard group="Settings" height=120 subtitle="Pick one of several named options" -->',
  body: `<div class="or-row" style="max-width:720px"><div style="flex:1;min-width:200px"><select class="or-select"><option>Hold</option><option>Toggle</option></select></div><div style="flex:1;min-width:200px"><div class="or-stepper"><button aria-label="Previous">‹</button><span>1920 × 1080</span><button aria-label="Next">›</button></div></div></div>`,
  readme: `# Select

Chooses one named option: quality preset, resolution, aim mode (Hold / Toggle), subtitle size.

**Consumer provides:** options with names and the current value.

- Mouse users get a dropdown (\`or-select\`). Controller users get the stepper variant (\`or-stepper\`), cycling with left/right without opening a list.
- Keep option names short and literal ("Hold", "Toggle"), never "Option A".
`
};

C.BindingCapture = {
  marker: '<!-- @dsCard group="Settings" height=230 subtitle="Primary and alternate bindings with conflict resolution" -->',
  body: `<div class="or-stack" style="max-width:620px">
  <div class="or-binding"><button class="or-binding__slot"><span class="or-keycap">F</span></button><button class="or-binding__slot is-empty">Add alternate</button></div>
  <div class="or-binding"><button class="or-binding__slot is-listening">Press a key · Esc cancels · Del clears</button></div>
  <div class="or-binding"><button class="or-binding__slot is-conflict"><span class="or-keycap">Q</span></button><button class="or-binding__slot is-empty">Add alternate</button></div>
  <div class="or-conflict" role="alert"><strong>Q is already Grapple.</strong> Swap the bindings? <button class="or-btn" style="height:40px;font-size:16px">Swap</button><button class="or-btn or-btn--ghost" style="height:40px;font-size:16px">Cancel</button></div>
</div>`,
  readme: `# BindingCapture

Rebinds one action. Each action has a primary and an alternate slot.

**Consumer provides:** action name (in the SettingRow label), current bindings, and the conflicting action when a new binding is already used.

- Activating a slot enters listening (\`is-listening\`): accent outline and the instruction "Press a key · Esc cancels · Del clears". Mouse buttons count.
- A conflict never silently steals: show the warning-outlined slot plus an \`or-conflict\` row naming the other action, with Swap and Cancel.
- Controller bindings use pad glyphs (\`or-keycap--pad\`).
`
};

C.Keycap = {
  marker: '<!-- @dsCard group="Input" height=120 subtitle="Binding glyphs for keyboard, mouse and controller" -->',
  body: `<div class="or-row"><span class="or-keycap">E</span><span class="or-keycap">Tab</span><span class="or-keycap or-keycap--wide">Space</span><span class="or-keycap">M1</span><span class="or-keycap or-keycap--pad">A</span><span class="or-keycap or-keycap--pad">Y</span><span class="or-keycap">LB</span><span class="or-prompt"><span class="or-keycap">E</span> Enter Kestrel</span><span class="or-prompt"><span class="or-keycap">H</span> Hold to heal</span></div>`,
  readme: `# Keycap

Shows the input that triggers an action. Every prompt derives its glyph from the actual binding and the device that last sent input.

**Consumer provides:** the bound key or button label. Never hard-code "E" in copy.

- Keys: \`or-keycap\` (square, raised bottom edge). Wide keys: \`--wide\`. Controller face buttons: \`--pad\` (round).
- Prompts pair a keycap with a verb phrase: "Enter Kestrel", "Hold to heal", "Swap Shield Pack".
- Production should replace pad letters with licensed controller glyphs per platform.
`
};

C.Dialog = {
  marker: '<!-- @dsCard group="Overlays" height=330 subtitle="Modal confirmation with a scoped consequence" -->',
  body: `<div class="or-backdrop" style="min-height:310px;box-sizing:border-box"><div class="or-dialog" role="dialog" aria-labelledby="t"><h2 id="t">Leave match?</h2><p>You'll be eliminated and returned to the lobby. Bots keep playing.</p><div class="or-dialog__actions"><button class="or-btn or-btn--ghost">Stay</button><button class="or-btn or-btn--danger">Leave match</button></div></div></div>`,
  readme: `# Dialog

A modal decision on top of a screen or the match: confirm leave, confirm reset, failed download.

**Consumer provides:** title as a question or statement, one sentence of consequence, and two actions.

- Opens on \`scrim\`; panel is \`surface\` with \`radius-panel\` and \`space-8\` padding.
- Focus moves to the safe action first (Stay / Cancel). Back or Esc closes it and returns focus to the opener.
- The destructive action names the outcome ("Leave match", "Reset Audio"), never "OK".
- One overlay at a time; gameplay input never passes through.
`
};

C.Toast = {
  marker: '<!-- @dsCard group="Overlays" height=200 subtitle="Brief feedback, with icon and words" -->',
  body: `<div class="or-stack">
  <div class="or-toast or-toast--success">${ic('check', 'or-toast__icon')}Bindings saved on this device</div>
  <div class="or-toast or-toast--warning">${ic('warning', 'or-toast__icon')}Storm closing in 0:30</div>
  <div class="or-toast or-toast--danger">${ic('error', 'or-toast__icon')}Ringfall terrain failed to download<button class="or-toast__action">Retry</button></div>
</div>`,
  script: iconScript,
  readme: `# Toast

Brief, non-blocking feedback about something that just happened. Appears bottom-center in menus, top-center under the compass in a match.

**Consumer provides:** tone (success, warning, danger), a sentence that names the thing, and an optional single action.

- Every tone carries an icon and words; success and danger are close in lightness so color alone never encodes status.
- Errors say what failed and offer the fix as the action ("Retry").
- Auto-dismiss after 4s unless it carries an action. One at a time; newer replaces older.
`
};

C.LoadingProgress = {
  marker: '<!-- @dsCard group="Status" height=330 subtitle="Honest progress through download, prepare, ready" -->',
  body: `<div class="or-stack">
  <div class="or-loading"><div class="or-loading__head"><span class="or-loading__stage">Downloading Ringfall terrain</span><span class="or-loading__count">412 / 768 MB</span></div><div class="or-loading__bar"><div class="or-loading__fill" style="width:53.6%"></div></div><div class="or-loading__steps"><span class="is-active">1 Download</span><span>2 Prepare assets</span><span>3 Ready</span></div></div>
  <div class="or-loading"><div class="or-loading__head"><span class="or-loading__stage">Preparing assets</span><span class="or-loading__count">Compiling shaders</span></div><div class="or-loading__bar is-indeterminate"><div class="or-loading__fill"></div></div></div>
  <div class="or-loading is-error"><div class="or-loading__head"><span class="or-loading__stage" style="color:var(--danger)">Download stopped at 412 MB</span><span class="or-loading__count">Connection lost</span></div><div class="or-loading__bar"><div class="or-loading__fill" style="width:53.6%"></div></div><div><button class="or-btn">Retry download</button></div></div>
</div>`,
  readme: `# LoadingProgress

Shows where asset loading is: download, prepare, ready. Sits bottom-left over the ringed-sky loading art.

**Consumer provides:** current stage, bytes loaded and total when known, and an error with a retry handler.

- Determinate bar only when the total is known; otherwise use \`is-indeterminate\` and name the step instead of a percentage. Never invent progress.
- Show units ("412 / 768 MB"), \`tabular-nums\`.
- On failure keep the reached progress visible, say what stopped and why, and offer "Retry download".
- Reduced motion replaces the indeterminate sweep with a static dimmed bar.
`
};

C.HUDGroup = {
  marker: '<!-- @dsCard group="HUD" height=260 subtitle="Health and shields, ammo, survivor and elimination counts" -->',
  body: `<div class="or-row" style="align-items:flex-end;justify-content:space-between;background:linear-gradient(160deg,var(--surface-raised),var(--background) 70%)">
  <div class="or-hud">
    <div class="or-meter or-meter--shield">${ic('shield', 'or-meter__icon')}<div class="or-meter__track" data-v="70"></div><span class="or-meter__value">70</span></div>
    <div class="or-meter or-meter--health">${ic('health', 'or-meter__icon')}<div class="or-meter__track" data-v="100"></div><span class="or-meter__value">100</span></div>
  </div>
  <div class="or-hud" style="flex-direction:row;gap:24px"><span class="or-stat">${ic('survivors')}23</span><span class="or-stat">${ic('eliminations')}4</span></div>
  <div class="or-hud" style="align-items:flex-end"><span class="or-eyebrow">AR-7 Wayfarer</span><div class="or-ammo"><span class="or-ammo__mag">24</span><span class="or-ammo__reserve">/ 150</span></div></div>
</div>`,
  script: `document.querySelectorAll('.or-meter__track').forEach(function (t) { t.innerHTML = Orbit.meterSegments(+t.dataset.v); });\n${iconScript}`,
  readme: `# HUDGroup

A cluster of live match information on a \`scrim\` backing so it reads over any part of Ringfall.

**Consumer provides:** values (health 0-100, shields 0-100, magazine / reserve, survivors, eliminations) and the selected weapon name.

- Placement: minimap top-left, compass top-center, survivors and eliminations top-right, health and shields bottom-left, inventory bottom-center, ammo bottom-right. Keep the aiming region clear.
- Meters are four 25-point segments with the number beside them; shield sits above health. \`shield\` cyan and \`health\` coral are only used here and on matching items.
- Low ammo turns the magazine \`warning\` (\`is-low\`) and keeps the number.
- HUD respects the HUD scale and safe-area settings; all groups move together.
`
};

C.InventorySlot = {
  marker: '<!-- @dsCard group="HUD" height=260 subtitle="Five slots: two weapons, three flexible items" -->',
  body: `<div class="or-stack" style="align-items:center;background:linear-gradient(160deg,var(--surface-raised),var(--background) 70%)">
  <div class="or-inventory">
    <button class="or-slot"><span class="or-keycap or-keycap--sm or-slot__key">1</span><span class="or-slot__weapon-mark"></span>${ic('rifle', 'or-slot__icon')}</button>
    <button class="or-slot is-selected"><span class="or-keycap or-keycap--sm or-slot__key">2</span><span class="or-slot__weapon-mark"></span>${ic('shotgun', 'or-slot__icon')}</button>
    <span class="or-inventory__sep"></span>
    <button class="or-slot"><span class="or-keycap or-keycap--sm or-slot__key">3</span>${ic('grapple', 'or-slot__icon')}<span class="or-slot__charge"><i style="width:60%"></i></span></button>
    <button class="or-slot or-slot--shield is-full"><span class="or-keycap or-keycap--sm or-slot__key">4</span>${ic('shield', 'or-slot__icon')}<span class="or-slot__qty">3</span></button>
    <button class="or-slot is-empty"><span class="or-keycap or-keycap--sm or-slot__key">5</span></button>
  </div>
  <div class="or-slot-label">SG-4 Breaker<small>Shield Pack 3/3 · full</small></div>
</div>`,
  script: iconScript,
  readme: `# InventorySlot

One of five numbered slots in a single horizontal strip, bottom-center of the HUD. Slots 1-2 hold weapons; slots 3-5 hold healing, grenades and the Tethercaster.

**Consumer provides:** slot number and its current binding, item icon, quantity, optional charge (Tethercaster cooldown, heal progress), and state.

- Slots 1-2 carry a small diamond weapon-eligibility mark; a gap separates them from 3-5.
- Selected: 2px \`accent\` border and the item name under the strip. Empty: dashed \`border\`, no icon.
- Quantity bottom-right in \`tabular-nums\`. Healing icons take \`health\` or \`shield\` tint; everything else stays \`text-primary\`.
- \`is-full\` (\`warning\` border) appears with a message when a pickup cannot be carried: "Shield Pack 3/3 · full".
- Every move, drop, split and swap works without dragging: select a slot, then press the action's binding.
- Distinct silhouettes per item; never rely on tint to tell items apart.
`
};

for (const [name, c] of Object.entries(C)) {
  const dir = path.join(root, name);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'preview.html'), doc(c.marker, c.body, c.script || ''));
  fs.writeFileSync(path.join(dir, 'README.md'), c.readme);
}
console.log('wrote', Object.keys(C).length, 'components');
