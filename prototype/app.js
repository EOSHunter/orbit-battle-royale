// Orbit Royale UI prototype: screens, navigation, settings, input devices.
// The match lives in game.js. Nothing here is gameplay-final; values are placeholders.
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const icon = (n, c) => Orbit.icon(n, c);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }
  };

  // ---------------------------------------------------------------- settings
  const S = (id, label, type, o) => Object.assign({ id, label, type }, o);
  const sl = (id, label, min, max, step, def, unit, o) => S(id, label, 'slider', Object.assign({ min, max, step, def, unit }, o));
  const sw = (id, label, def, o) => S(id, label, 'switch', Object.assign({ def }, o));
  const sg = (id, label, options, def, o) => S(id, label, 'seg', Object.assign({ options, def }, o));
  const st = (id, label, options, def, o) => S(id, label, 'step', Object.assign({ options, def }, o));
  const bd = (id, label, def, o) => S('bind.' + id, label, 'bind', Object.assign({ def, viz: 'key', action: id }, o));
  const Q4 = ['Low', 'Medium', 'High', 'Ultra'];

  const CATS = [
    { id: 'mk', name: 'Mouse & keyboard', sections: [
      { id: 'mouse', name: 'Mouse', rows: [
        sl('sens', 'Look sensitivity', 0.1, 3, 0.05, 0.7, 'x', { viz: 'mouse', help: 'Rotation speed when looking around. Uses raw mouse input with no OS acceleration.', more: 'Higher values turn faster; lower values give finer control. Try it in a match: it applies immediately.' }),
        sl('adsSens', 'Aim sensitivity', 0.1, 2, 0.05, 1, 'x', { viz: 'mouse', help: 'Multiplier while aiming down sights.' }),
        sl('scopeSens', 'Scoped sensitivity', 0.1, 2, 0.05, 1, 'x', { viz: 'mouse', help: 'Multiplier while looking through the SR-8 Longview scope.' }),
        sw('invertMouse', 'Invert vertical look', false, { help: 'Moving the mouse forward looks down.' })
      ] },
      { id: 'behavior', name: 'Behavior', rows: [
        sg('aimMode', 'Aim', ['Hold', 'Toggle'], 'Hold', { help: 'Hold: aim while the button is held. Toggle: press once to aim, again to stop.' }),
        sg('sprintMode', 'Sprint', ['Hold', 'Toggle', 'Auto'], 'Hold', { help: 'Auto sprints whenever you move forward on open ground.' }),
        sg('crouchMode', 'Crouch', ['Hold', 'Toggle'], 'Toggle', { help: 'How the crouch binding behaves.' }),
        sg('healMode', 'Use healing', ['Tap', 'Hold'], 'Tap', { help: 'Tap: one press of Fire starts the full use. Hold: keep Fire held until the item finishes.', more: 'Either way, taking damage, firing or grappling interrupts the use and the item is kept.' })
      ] },
      { id: 'bindings', name: 'Bindings', rows: [
        bd('forward', 'Move forward', 'W'), bd('backward', 'Move back', 'S'), bd('left', 'Move left', 'A'), bd('right', 'Move right', 'D'),
        bd('jump', 'Jump', 'Space'), bd('sprint', 'Sprint', 'Shift'), bd('crouch', 'Crouch', 'C'), bd('reload', 'Reload', 'R'),
        bd('interact', 'Interact / enter vehicle', 'E'), bd('inventory', 'Inventory', 'Tab'), bd('map', 'Map', 'M'),
        bd('slot1', 'Slot 1 (weapon)', '1'), bd('slot2', 'Slot 2 (weapon)', '2'), bd('slot3', 'Slot 3', '3'), bd('slot4', 'Slot 4', '4'), bd('slot5', 'Slot 5', '5')
      ] }
    ] },
    { id: 'pad', name: 'Controller', sections: [
      { id: 'layout', name: 'Layout', rows: [
        sg('prompts', 'Button prompts', ['Auto', 'Xbox', 'PlayStation'], 'Auto', { viz: 'pad', help: 'Auto matches prompts to the controller you are using.' }),
        st('padLayout', 'Controller layout', ['Standard', 'Southpaw', 'Bumper jumper'], 'Standard', { viz: 'pad', help: 'Preset button arrangements. Rebind individual actions below in a future build.' }),
        sw('swapSticks', 'Swap sticks', false, { help: 'Move with the right stick and look with the left.' }),
        sw('vibration', 'Vibration', true, { help: 'Rumble for damage, landing and vehicle impacts.' })
      ] },
      { id: 'look', name: 'Look', rows: [
        sl('padLook', 'Look sensitivity', 0.2, 3, 0.05, 1.1, 'x', { viz: 'stick', help: 'How fast the camera turns at full stick deflection.' }),
        sl('padAim', 'Aim sensitivity', 0.2, 2, 0.05, 0.8, 'x', { viz: 'stick', help: 'Multiplier while aiming down sights.' }),
        sg('curve', 'Response curve', ['Standard', 'Linear', 'Dynamic'], 'Standard', { viz: 'stick', help: 'Standard eases in for precise small adjustments. Linear maps stick position directly to speed.' }),
        sw('invertPad', 'Invert vertical look', false, { help: 'Pushing the stick up looks down.' })
      ] },
      { id: 'deadzones', name: 'Deadzones', rows: [
        sl('dzLeft', 'Left stick deadzone', 0, 40, 1, 12, '%', { viz: 'stick', help: 'Ignores small stick movement to stop drift.', more: 'Lower it until your character moves on its own, then raise it slightly.' }),
        sl('dzRight', 'Right stick deadzone', 0, 40, 1, 14, '%', { viz: 'stick', help: 'Ignores small stick movement to stop the camera drifting.' })
      ] }
    ] },
    { id: 'audio', name: 'Audio', sections: [
      { id: 'volume', name: 'Volume', rows: [
        sl('master', 'Master volume', 0, 100, 1, 80, '%', { viz: 'volume', help: 'Overall loudness. Every other channel is mixed beneath it.', more: 'This prototype plays no sound yet; values are saved for the real build.' }),
        sl('combat', 'Combat and world', 0, 100, 1, 100, '%', { viz: 'volume', help: 'Gunfire, footsteps, impacts and grenades.' }),
        sl('vehicles', 'Vehicles and aircraft', 0, 100, 1, 100, '%', { viz: 'volume', help: 'Engines and the Kestrel\'s rotors.', more: 'Keep this high. Hearing a vehicle approach is a gameplay warning, not just atmosphere.' }),
        sl('ambience', 'Ringfall ambience', 0, 100, 1, 60, '%', { viz: 'volume', help: 'Wind, wildlife, the ion storm and distant thunder.' }),
        sl('uiVol', 'Interface', 0, 100, 1, 80, '%', { viz: 'volume', help: 'Menu sounds, pickups and alerts.' }),
        sl('music', 'Music', 0, 100, 1, 50, '%', { viz: 'volume', help: 'Menu and end-of-match music.' }),
        sg('range', 'Dynamic range', ['Full', 'Reduced', 'Night'], 'Full', { help: 'Night narrows the gap between quiet and loud sounds so you can play at low volume.' })
      ] },
      { id: 'subtitles', name: 'Subtitles', rows: [
        sw('subs', 'Subtitles', true, { help: 'Shows meaningful spoken lines and announcer callouts.' }),
        sg('subSize', 'Subtitle size', ['Small', 'Medium', 'Large'], 'Medium', { help: 'Text size for subtitles.' }),
        sw('speakers', 'Speaker names', true, { help: 'Prefix each line with who is speaking.' }),
        sl('subBg', 'Background opacity', 0, 100, 5, 60, '%', { help: 'Darkens the area behind subtitles.' })
      ] }
    ] },
    { id: 'video', name: 'Video', sections: [
      { id: 'display', name: 'Display', rows: [
        st('windowMode', 'Window mode', ['Fullscreen', 'Browser window'], 'Browser window', { help: 'Fullscreen hides the browser interface. Your browser asks before going fullscreen.' }),
        st('fpsLimit', 'Frame rate limit', ['Display', '30', '60', '120', '144', 'Unlimited'], 'Display', { help: 'Display matches your monitor\'s refresh rate.' }),
        sl('res3d', '3D resolution', 50, 100, 5, 100, '%', { help: 'Renders the world below native resolution and scales it up. The interface stays sharp.' }),
        sl('fov', 'Field of view', 70, 110, 1, 90, '°', { viz: 'fov', help: 'Horizontal degrees visible in first person. Applies in the match immediately.' }),
        sw('showFps', 'Show frame rate', false, { help: 'Small counter in the top-right corner.' })
      ] },
      { id: 'graphics', name: 'Graphics', rows: [
        st('preset', 'Quality preset', Q4.concat('Custom'), 'High', { viz: 'preset', help: 'Sets every option below. Changing one option switches the preset to Custom.' }),
        st('shadows', 'Shadows', Q4, 'High', { viz: 'preset', group: 'gfx', help: 'Shadow resolution and distance.' }),
        st('textures', 'Textures', Q4, 'High', { viz: 'preset', group: 'gfx', help: 'Texture detail. Higher settings download more data on first launch.' }),
        st('foliage', 'Luminous vegetation', Q4, 'High', { viz: 'preset', group: 'gfx', help: 'Density of Ringfall\'s glowing plants. Lower settings can reveal players hiding in Bloomwild.' }),
        st('effects', 'Effects', Q4, 'High', { viz: 'preset', group: 'gfx', help: 'Storm particles, explosions and lighting effects.' }),
        st('viewDist', 'View distance', Q4, 'High', { viz: 'preset', group: 'gfx', help: 'How far terrain detail and structures are drawn.' })
      ] }
    ] },
    { id: 'access', name: 'Accessibility', sections: [
      { id: 'comfort', name: 'Comfort', rows: [
        sw('reduceMotion', 'Reduce motion', false, { viz: 'hud', help: 'Removes nonessential menu transitions, weapon sway and pulsing effects.' }),
        sl('shake', 'Camera shake', 0, 100, 5, 100, '%', { help: 'Shake from explosions, landing and weapon recoil.' }),
        sl('flash', 'Flash intensity', 0, 100, 5, 100, '%', { help: 'Brightness of explosions and Arc grenade bursts.' })
      ] },
      { id: 'readability', name: 'Readability', rows: [
        sl('hudScale', 'HUD scale', 70, 130, 5, 100, '%', { viz: 'hud', help: 'Size of every HUD group. They move together and stay inside the safe area.' }),
        sl('textScale', 'Text scale', 90, 150, 10, 100, '%', { viz: 'hud', help: 'Size of menu and settings text. Layouts reflow instead of shrinking.' }),
        sw('solidHud', 'Solid HUD backing', false, { viz: 'hud', help: 'Replaces the translucent backing behind HUD text with an opaque panel.' })
      ] },
      { id: 'feedback', name: 'Damage & healing', rows: [
        sw('dmgDir', 'Damage direction indicator', true, { viz: 'damage', help: 'A red arc around the crosshair points toward whoever hit you.' }),
        sl('dmgIntensity', 'Damage glow intensity', 0, 100, 5, 100, '%', { viz: 'damage', help: 'Strength of the red glow at the screen edge facing the attacker, and of the low-health warning.' }),
        sw('healGlow', 'Healing edge glow', true, { viz: 'heal', help: 'Soft glow around the screen while a healing item is in use. Cyan for shields, mint for health.' }),
        sw('lowHealth', 'Low-health warning', true, { viz: 'damage', help: 'Pulsing red edges below 25 health. Respects Reduce motion.' })
      ] }
    ] },
    { id: 'gameplay', name: 'Gameplay', sections: [
      { id: 'hud', name: 'HUD', rows: [
        sw('mapRotate', 'Rotate minimap', false, { help: 'Keeps your facing direction at the top of the minimap.' }),
        sw('bearing', 'Show bearing number', true, { help: 'Degrees under the compass.' }),
        sw('feed', 'Elimination feed', true, { help: 'Recent eliminations under the survivor count.' }),
        sw('dmgNumbers', 'Damage numbers', true, { help: 'Shows damage dealt next to the crosshair.' }),
        sg('crosshair', 'Crosshair', ['Cross', 'Dot'], 'Cross', { help: 'Crosshair shape while not aiming.' })
      ] },
      { id: 'inventory', name: 'Inventory', rows: [
        sw('autoWeapons', 'Auto-pick up weapons', true, { help: 'Picks up weapons into an empty weapon slot. Never replaces an occupied slot.' }),
        sw('autoItems', 'Auto-pick up items', true, { help: 'Fills matching stacks first, then empty item slots. Never replaces an occupied slot.' }),
        sw('confirmDrop', 'Confirm before dropping', false, { help: 'Asks before dropping a stack from the inventory.' })
      ] }
    ] }
  ];
  const ROWS = {};
  CATS.forEach(c => c.sections.forEach(s => s.rows.forEach(r => { r.cat = c; r.sec = s; ROWS[r.id] = r; })));

  const defaults = () => Object.fromEntries(Object.values(ROWS).map(r => [r.id, r.def]));
  const V = Object.assign(defaults(), Object.fromEntries(Object.entries(store.get('orbit.settings', {})).filter(([k]) => ROWS[k])));
  const state = { screen: null, device: 'kb', padType: 'xbox', callsign: store.get('orbit.callsign', 'NOMAD-7'), saveOk: true, proto: { failDownload: false, botsShoot: true, pauseFreezes: false } };

  function setV(id, v) {
    const r = ROWS[id];
    if (r.type === 'slider') v = Math.min(r.max, Math.max(r.min, Math.round(v / r.step) * r.step));
    V[id] = v;
    if (id === 'preset' && v !== 'Custom') Object.values(ROWS).filter(x => x.group === 'gfx').forEach(x => (V[x.id] = v));
    else if (r.group === 'gfx') V.preset = 'Custom';
    state.saveOk = store.set('orbit.settings', V);
    applySettings();
  }
  function applySettings() {
    const root = document.documentElement;
    root.classList.toggle('reduce-motion', !!V.reduceMotion);
    root.classList.toggle('solid-hud', !!V.solidHud);
    root.style.setProperty('--hud-scale', V.hudScale / 100);
    root.style.setProperty('--text-scale', V.textScale / 100);
    root.style.setProperty('--fx-intensity', V.dmgIntensity / 100);
    refreshGlyphs();
  }
  const fmt = (r, v) => {
    if (r.type === 'slider') return r.unit === 'x' ? v.toFixed(2) + 'x' : Math.round(v) + r.unit;
    if (r.type === 'switch') return v ? 'On' : 'Off';
    if (r.type === 'bind') return v || 'Unbound';
    return v;
  };

  // ---------------------------------------------------------------- input glyphs
  const PAD = {
    xbox: { confirm: 'A', back: 'B', alt: 'X', alt2: 'Y', prevCat: 'LB', nextCat: 'RB', nav: 'D-pad', adjust: '◀▶', pause: '☰', map: '↑', inventory: '⧉', reload: 'X', fire: 'RT', slot: 'LB/RB', drop: 'X', split: 'Y', move: 'RB', jump: 'A', interact: 'X', forward: 'LS' },
    ps: { confirm: '✕', back: '○', alt: '□', alt2: '△', prevCat: 'L1', nextCat: 'R1', nav: 'D-pad', adjust: '◀▶', pause: '≡', map: '↑', inventory: '▭', reload: '□', fire: 'R2', slot: 'L1/R1', drop: '□', split: '△', move: 'R1', jump: '✕', interact: '□', forward: 'L3' }
  };
  const KB = { confirm: 'Enter', back: 'Esc', alt: 'R', alt2: 'Tab', prevCat: 'Q', nextCat: 'E', nav: '↑↓', adjust: '←→', pause: 'Esc', fire: 'M1', slot: '1–5', drop: 'X', split: 'S', move: 'Space' };
  function padStyle() { return V.prompts === 'PlayStation' ? 'ps' : V.prompts === 'Xbox' ? 'xbox' : state.padType; }
  function glyphText(a) {
    if (state.device === 'pad') return /^slot\d$/.test(a) ? a.slice(4) : (PAD[padStyle()][a] || PAD[padStyle()].confirm);
    if (V['bind.' + a]) return V['bind.' + a];
    return KB[a] || a;
  }
  function glyph(a, cls) {
    const t = glyphText(a);
    const round = state.device === 'pad' && t.length === 1;
    return `<span class="or-keycap${round ? ' or-keycap--pad' : ''}${t.length > 4 ? ' or-keycap--wide' : ''}${cls ? ' ' + cls : ''}" data-glyph="${a}">${esc(t)}</span>`;
  }
  function refreshGlyphs() {
    $$('[data-glyph]').forEach(el => {
      const t = glyphText(el.dataset.glyph);
      el.textContent = t;
      el.classList.toggle('or-keycap--pad', state.device === 'pad' && t.length === 1);
      el.classList.toggle('or-keycap--wide', t.length > 4);
    });
  }
  function setDevice(d, padId) {
    if (padId) state.padType = /054c|playstation|dualsense|dualshock/i.test(padId) ? 'ps' : 'xbox';
    if (state.device === d) return;
    state.device = d; refreshGlyphs();
    if (state.screen && SCREENS[state.screen].onDevice) SCREENS[state.screen].onDevice();
  }
  const prompt = (a, label) => `<button class="prompt" data-act="${a}">${glyph(a)}${esc(label)}</button>`;

  // ---------------------------------------------------------------- toasts and dialogs
  const dock = $('#toasts');
  function toast(tone, text, action) {
    const ic = { success: 'check', warning: 'warning', danger: 'error', info: 'check' }[tone];
    const el = document.createElement('div');
    el.className = `or-toast or-toast--${tone}`;
    el.setAttribute('role', tone === 'danger' ? 'alert' : 'status');
    el.innerHTML = `${icon(ic, 'or-toast__icon')}<span>${esc(text)}</span>${action ? `<button class="or-toast__action">${esc(action.label)}</button>` : ''}`;
    if (action) el.querySelector('button').onclick = () => { el.remove(); action.run(); };
    dock.innerHTML = ''; dock.appendChild(el);
    clearTimeout(toast.t);
    if (!action) toast.t = setTimeout(() => el.remove(), 4000);
  }
  const layer = $('#layer');
  let dialogState = null;
  function confirmDialog({ title, body, ok, cancel = 'Cancel', danger = true }) {
    return new Promise(res => {
      const opener = document.activeElement;
      layer.innerHTML = `<div class="or-backdrop" style="width:100%;height:100%;box-sizing:border-box"><div class="or-dialog" role="dialog" aria-modal="true" aria-labelledby="dlg-t"><h2 id="dlg-t">${esc(title)}</h2><p>${esc(body)}</p><div class="or-dialog__actions"><button class="or-btn or-btn--ghost" data-r="0">${glyph('back')}${esc(cancel)}</button><button class="or-btn ${danger ? 'or-btn--danger' : 'or-btn--primary'}" data-r="1">${esc(ok)}</button></div></div></div>`;
      layer.classList.add('is-open');
      const close = v => { layer.classList.remove('is-open'); layer.innerHTML = ''; dialogState = null; if (opener && opener.focus) opener.focus(); res(v); };
      $$('[data-r]', layer).forEach(b => (b.onclick = () => close(b.dataset.r === '1')));
      $('[data-r="0"]', layer).focus();
      dialogState = { close, buttons: $$('[data-r]', layer) };
    });
  }

  // ---------------------------------------------------------------- world background
  const worldCanvas = $('#world');
  const W = { mode: 'vista', offset: 30, planetX: 0.78 };
  function drawWorld() {
    if (W.mode === 'vista') Ringfall.vista(worldCanvas, W);
    else if (W.mode === 'game' && window.Match) Match.draw();
  }
  window.addEventListener('resize', () => { drawWorld(); if (state.screen && SCREENS[state.screen].resize) SCREENS[state.screen].resize(); });

  // ---------------------------------------------------------------- navigation
  const SCREENS = {};
  const history = [];
  function go(name, params, opts) {
    opts = opts || {};
    const cur = state.screen;
    if (cur && SCREENS[cur].exit) SCREENS[cur].exit(name);
    if (cur && !opts.replace && !opts.noHistory) history.push(cur);
    $$('.screen').forEach(s => s.classList.remove('is-active'));
    state.screen = name;
    const el = $('#s-' + name);
    el.classList.add('is-active');
    SCREENS[name].enter(el, params || {});
    dock.classList.toggle('in-game', name === 'game');
    drawWorld();
    $('#proto-screen').textContent = name;
  }
  function back() { const prev = history.pop(); if (prev) go(prev, { returning: true }, { noHistory: true }); }

  // Linear focus movement among [data-nav] elements of the active screen
  function moveFocus(root, dir) {
    const items = $$('[data-nav]', root).filter(e => e.offsetParent && !e.disabled);
    if (!items.length) return;
    let i = items.indexOf(document.activeElement);
    i = i < 0 ? 0 : (i + dir + items.length) % items.length;
    items[i].focus();
  }
  function focusFirst(root, sel) { const el = sel ? $(sel, root) : $('[data-nav]', root); if (el) el.focus({ preventScroll: true }); }
  function bindActs(root, map) {
    $$('[data-act]', root).forEach(b => b.addEventListener('click', e => { e.stopPropagation(); const f = map[b.dataset.act]; if (f) f(); }));
  }

  // ---------------------------------------------------------------- LOADING
  const TIPS = [
    { a: 'inventory', t: 'Five slots', d: 'Two weapons and three items. Matching pickups fill an existing stack before taking a new slot.' },
    { a: 'jump', t: 'No fall damage', d: 'Jump from any height. The ion storm and enemy fire still hurt.' },
    { a: 'fire', t: 'Healing takes time', d: 'Items are used up only when the timer finishes. Taking damage interrupts, and you keep the item.' },
    { a: 'interact', t: 'Kestrel', d: 'The utility rotorcraft carries no weapons, and its rotors are loud. Everyone below hears you coming.' },
    { a: 'map', t: 'Storm edge', d: 'The ion storm drains health and ignores shields. Watch the violet edge on your minimap.' }
  ];
  SCREENS.loading = {
    enter(el) {
      W.mode = 'vista'; W.offset = 30; W.planetX = 0.8;
      const L = this.L = { mb: 0, total: 768, stage: 'download', failed: false, tip: 0, prep: 0 };
      el.innerHTML = `<div class="pad left-fade" style="--x:0">
        <div style="position:relative"><span class="wordmark"><b>ORBIT</b><span>ROYALE</span></span></div>
        <div class="loading-bottom" style="position:relative">
          <div>
            <div class="or-eyebrow eyebrow-rule">Solo · Ringfall, Veyra</div>
            <h1 class="loading-hero">One world. One survivor.</h1>
            <div class="or-loading" id="ld"></div>
          </div>
          <aside class="tip" aria-live="polite" id="tip"></aside>
        </div></div>`;
      this.renderTip();
      this.tick = setInterval(() => this.step(), 100);
      this.tipT = setInterval(() => { L.tip = (L.tip + 1) % TIPS.length; this.renderTip(); }, 6000);
      this.render();
    },
    exit() { clearInterval(this.tick); clearInterval(this.tipT); },
    step() {
      const L = this.L;
      if (L.stage === 'download') {
        L.mb = Math.min(L.total, L.mb + 14 + Math.random() * 16);
        if (state.proto.failDownload && !L.failed && L.mb >= 412) { L.mb = 412; L.stage = 'error'; L.failed = true; }
        else if (L.mb >= L.total) { L.stage = 'prepare'; L.prepAt = Date.now(); }
      } else if (L.stage === 'prepare') {
        L.prep = Math.floor((Date.now() - L.prepAt) / 650);
        if (L.prep >= 4) { L.stage = 'ready'; }
      }
      this.render();
    },
    render() {
      const L = this.L, el = $('#ld');
      const steps = ['Download', 'Prepare assets', 'Ready'], si = { download: 0, error: 0, prepare: 1, ready: 2 }[L.stage];
      const stepHtml = `<div class="or-loading__steps">${steps.map((s, i) => `<span class="${i < si ? 'is-done' : i === si ? 'is-active' : ''}">${i < si ? '✓ ' : ''}${s}</span>`).join('')}</div>`;
      if (L.stage === 'download') {
        el.className = 'or-loading';
        el.innerHTML = `<div class="or-loading__head"><span class="or-loading__stage">Downloading Ringfall</span><span class="or-loading__count">${Math.round(L.mb)} / ${L.total} MB · ${Math.floor(L.mb / L.total * 100)}%</span></div><div class="or-loading__bar" role="progressbar" aria-valuemin="0" aria-valuemax="${L.total}" aria-valuenow="${Math.round(L.mb)}"><div class="or-loading__fill" style="width:${L.mb / L.total * 100}%"></div></div>${stepHtml}`;
      } else if (L.stage === 'error') {
        if (el.dataset.stage === 'error') return;
        el.className = 'or-loading is-error';
        el.innerHTML = `<div class="or-loading__head"><span class="or-loading__stage" style="color:var(--danger)">Download stopped at 412 MB</span><span class="or-loading__count">Connection lost</span></div><div class="or-loading__bar"><div class="or-loading__fill" style="width:${412 / 768 * 100}%"></div></div><div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap"><button class="or-btn" id="retry" data-nav>${glyph('confirm')}Retry download</button><span class="note">Already downloaded files are kept.</span></div>`;
        $('#retry').onclick = () => { L.stage = 'download'; this.render(); };
        $('#retry').focus();
      } else if (L.stage === 'prepare') {
        const sub = ['Unpacking terrain', 'Compiling shaders', 'Building luminous vegetation', 'Placing colony structures'][Math.min(3, L.prep)];
        el.className = 'or-loading';
        el.innerHTML = `<div class="or-loading__head"><span class="or-loading__stage">Preparing assets</span><span class="or-loading__count">${sub}</span></div><div class="or-loading__bar is-indeterminate"><div class="or-loading__fill"></div></div>${stepHtml}`;
      } else if (L.stage === 'ready' && el.dataset.stage !== 'ready') {
        el.className = 'or-loading';
        el.innerHTML = `<div class="or-loading__head"><span class="or-loading__stage">Ready</span><span class="or-loading__count">768 MB</span></div><div class="or-loading__bar"><div class="or-loading__fill" style="width:100%"></div></div>${stepHtml}<button class="loading-ready prompt" id="cont" data-nav style="color:var(--text-primary);margin-top:8px">${glyph('confirm')}Click or press any key to continue</button><p class="note">Sound starts after you continue.</p>`;
        $('#cont').onclick = () => go('menu', {}, { replace: true });
        $('#cont').focus();
      }
      el.dataset.stage = L.stage;
    },
    renderTip() {
      const t = TIPS[this.L.tip];
      $('#tip').innerHTML = `<div class="or-eyebrow">Field note</div><h3>${glyph(t.a)}${esc(t.t)}</h3><p>${esc(t.d)}</p><div class="tip-dots">${TIPS.map((_, i) => `<button aria-label="Tip ${i + 1}" aria-current="${i === this.L.tip}" data-tip="${i}"></button>`).join('')}</div>`;
      $$('[data-tip]').forEach(b => (b.onclick = () => { this.L.tip = +b.dataset.tip; this.renderTip(); }));
    },
    key(a, e) {
      if (a === 'left' || a === 'right') { this.L.tip = (this.L.tip + (a === 'left' ? -1 : 1) + TIPS.length) % TIPS.length; this.renderTip(); return; }
      if (this.L.stage === 'ready') go('menu', {}, { replace: true });
      else if (this.L.stage === 'error' && a === 'confirm') $('#retry').click();
    },
    pointer() { if (this.L.stage === 'ready') go('menu', {}, { replace: true }); }
  };

  // ---------------------------------------------------------------- MAIN MENU
  SCREENS.menu = {
    enter(el) {
      W.mode = 'vista'; W.offset = 8; W.planetX = 0.74;
      history.length = 0;
      el.innerHTML = `<div class="scale-root"><div class="pad left-fade">
        <div class="menu-top" style="position:relative">
          <span class="wordmark"><b>ORBIT</b><span>ROYALE</span></span>
          <nav class="menu-nav"><div class="or-tabs" role="tablist">
            <button class="or-tab" role="tab" aria-selected="true" data-nav data-act="play">Play</button>
            <button class="or-tab" role="tab" data-nav data-act="settings">Settings</button>
            <button class="or-tab" role="tab" data-nav data-act="credits">Credits</button></div></nav>
          <div class="callsign" id="cs"></div>
        </div>
        <div class="menu-main" style="position:relative">
          <div class="or-eyebrow eyebrow-rule">Battle royale · Veyra</div>
          <h1 class="menu-hero">Rings over Ringfall.</h1>
          <div class="menu-sub">60 combatants · Solo · Last one standing</div>
          <button class="or-btn or-btn--primary play-btn" id="play" data-nav data-act="play"><span>Play</span><svg viewBox="0 0 24 24"><path d="M4 12h15M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.5"/></svg></button>
          <div class="note"><span class="status-dot"></span>Local match: you and 59 bots. Online play comes later.</div>
          <div class="menu-links">
            <button class="or-btn or-btn--ghost" data-nav data-act="controls">${icon('rifle', '')}Controls</button>
            <button class="or-btn or-btn--ghost" data-nav data-act="access">Accessibility</button>
          </div>
        </div>
        <div class="menu-foot prompts" style="position:relative">${prompt('confirm', 'Play')}${prompt('back', 'Settings')}</div>
      </div></div>`;
      $$('.menu-links svg', el).forEach(s => (s.style.cssText = 'width:24px;height:24px'));
      this.renderCallsign();
      bindActs(el, {
        play: () => go('lobby'), settings: () => go('settings', { cat: 'mk' }), credits: () => go('credits'),
        controls: () => go('settings', { cat: 'mk', sec: 'bindings' }), access: () => go('settings', { cat: 'access' }),
        confirm: () => go('lobby'), back: () => go('settings', { cat: 'mk' })
      });
      focusFirst(el, '#play');
    },
    renderCallsign(edit) {
      const cs = $('#cs');
      if (edit) {
        cs.innerHTML = `<div><small>Callsign</small><input id="cs-in" maxlength="12" value="${esc(state.callsign)}" aria-label="Callsign" spellcheck="false"></div>`;
        const inp = $('#cs-in'); inp.focus(); inp.select();
        inp.onkeydown = e => {
          e.stopPropagation();
          if (e.key === 'Enter') { const v = inp.value.trim().toUpperCase(); if (v) { state.callsign = v; store.set('orbit.callsign', v); toast('success', `Callsign saved: ${v}`); } this.renderCallsign(); }
          if (e.key === 'Escape') this.renderCallsign();
        };
        inp.onblur = () => this.renderCallsign();
      } else {
        cs.innerHTML = `<div><small>Callsign</small><strong>${esc(state.callsign)}</strong></div><button class="or-btn or-btn--ghost" id="cs-edit" data-nav>Edit callsign</button>`;
        $('#cs-edit').onclick = () => this.renderCallsign(true);
      }
    },
    key(a) {
      const el = $('#s-menu');
      if (a === 'up' || a === 'left') moveFocus(el, -1);
      else if (a === 'down' || a === 'right') moveFocus(el, 1);
      else if (a === 'back') go('settings', { cat: 'mk' });
      else if (a === 'confirm' && state.device === 'pad') document.activeElement.click();
    }
  };

  // ---------------------------------------------------------------- LOBBY
  const OPERATOR = `<svg viewBox="0 0 200 420" aria-hidden="true"><defs><linearGradient id="suit" x1="0" x2="1"><stop offset="0" stop-color="#2b3550"/><stop offset=".6" stop-color="#1a2135"/><stop offset="1" stop-color="#0f1424"/></linearGradient><linearGradient id="visor" x1="0" x2="1"><stop offset="0" stop-color="#ffb45c"/><stop offset="1" stop-color="#ff8a3d"/></linearGradient></defs>
    <path d="M70 120 Q100 100 130 120 L150 200 L140 260 L128 400 L108 400 L102 290 L98 290 L92 400 L72 400 L60 260 L50 200 Z" fill="url(#suit)"/>
    <path d="M50 130 L30 220 L36 280 L48 278 L46 226 L66 160Z M150 130 L170 220 L164 280 L152 278 L154 226 L134 160Z" fill="#1a2135"/>
    <rect x="72" y="128" width="56" height="70" rx="6" fill="#2f3a58"/><rect x="80" y="140" width="40" height="6" rx="2" fill="#70d6ff" opacity=".7"/><rect x="80" y="152" width="24" height="4" rx="2" fill="#c5f277" opacity=".8"/>
    <ellipse cx="100" cy="82" rx="30" ry="36" fill="#212a42"/><path d="M76 78 Q100 64 124 78 L122 94 Q100 100 78 94Z" fill="url(#visor)"/>
    <path d="M128 140 l26 -40 l6 4 l-24 42z" fill="#46566d"/><rect x="64" y="250" width="72" height="8" rx="3" fill="#0b101b"/></svg>`;
  SCREENS.lobby = {
    enter(el) {
      W.mode = 'vista'; W.offset = 64; W.planetX = 0.3;
      el.innerHTML = `<div class="scale-root"><div class="pad dim">
        <div class="settings-head" style="position:relative"><div><div class="or-eyebrow">Solo · Ringfall</div><h1 class="settings-title">Lobby</h1></div><span class="wordmark wordmark--sm"><b>ORBIT</b><span>ROYALE</span></span></div>
        <div class="lobby-body" style="position:relative">
          <div class="operator">${OPERATOR}<div class="operator-plate"><span class="or-eyebrow">Callsign</span><strong>${esc(state.callsign)}</strong><span class="chip" style="color:var(--success)">${icon('check', '')} Ready</span></div></div>
          <section class="lobby-panel" aria-labelledby="mt">
            <h2 id="mt" class="section-heading" style="margin:0">Solo match</h2>
            <dl class="lobby-facts"><dt>Map</dt><dd>Ringfall, Veyra</dd><dt>Combatants</dt><dd>60</dd><dt>Players</dt><dd>1 (you)</dd><dt>Bots</dt><dd>59</dd><dt>Target length</dt><dd>15–18 min</dd></dl>
            <div><div class="roster" aria-label="1 player and 59 bots">${Array.from({ length: 60 }, (_, i) => `<i class="${i ? '' : 'you'}"></i>`).join('')}</div>
            <div class="roster-legend" style="margin-top:8px"><span class="you">You</span><span>Bot</span></div></div>
            <p class="note">Online matchmaking isn't available yet. Bots fill every place you don't.</p>
            <button class="or-btn or-btn--primary" style="width:100%" id="start" data-nav data-act="start">${glyph('confirm', 'or-keycap--sm')} Start match</button>
          </section>
        </div>
        <div class="prompts" style="position:relative">${prompt('confirm', 'Start match')}${prompt('back', 'Back')}</div>
      </div></div>`;
      $$('.operator-plate svg', el).forEach(s => (s.style.cssText = 'width:18px;height:18px'));
      bindActs(el, { start: () => go('deploy'), confirm: () => go('deploy'), back: () => back() });
      focusFirst(el, '#start');
    },
    key(a) { if (a === 'back') back(); else if (a === 'confirm' && state.device === 'pad') go('deploy'); }
  };

  // ---------------------------------------------------------------- CREDITS
  SCREENS.credits = {
    enter(el) {
      W.mode = 'vista'; W.offset = 140;
      el.innerHTML = `<div class="scale-root"><div class="pad dim"><div style="position:relative"><div class="or-eyebrow">Orbit Royale</div><h1 class="settings-title">Credits</h1>
        <div class="credits"><p class="note">Preproduction interface prototype. Names, balance and art are working proposals.</p>
        <dl><dt>World</dt><dd>Planet Veyra, map Ringfall (working names)</dd><dt>Typefaces</dt><dd>Archivo by Omnibus-Type; IBM Plex Sans and Mono by IBM. SIL Open Font License. Stand-ins pending final selection.</dd><dt>Art</dt><dd>Procedural placeholder scenery drawn in the browser.</dd><dt>Audio</dt><dd>None yet.</dd></dl></div></div>
        <div class="prompts" style="position:relative;margin-top:auto">${prompt('back', 'Back')}</div></div></div>`;
      bindActs(el, { back: () => back() });
    },
    key(a) { if (a === 'back') back(); }
  };

  // ---------------------------------------------------------------- SETTINGS
  SCREENS.settings = {
    enter(el, p) {
      if (W.mode !== 'game') { W.mode = 'vista'; W.offset = 100; W.planetX = 0.85; }
      this.el = el;
      if (!p.returning) { this.cat = p.cat || this.cat || 'mk'; this.sec = p.sec || null; this.row = 0; }
      this.capture = null;
      el.innerHTML = `<div class="scale-root"><div class="pad dim" id="set-pad"></div></div>`;
      this.render();
    },
    exit() { this.capture = null; },
    get C() { return CATS.find(c => c.id === this.cat); },
    get SEC() { const c = this.C; return c.sections.find(s => s.id === this.sec) || c.sections[0]; },
    render() {
      const c = this.C, sec = this.SEC; this.sec = sec.id;
      const rows = sec.rows; this.row = Math.min(this.row, rows.length - 1);
      $('#set-pad').innerHTML = `
        <div class="settings-head" style="position:relative"><div><span class="wordmark wordmark--sm"><b>ORBIT</b><span>ROYALE</span></span><h1 class="settings-title">Settings</h1></div>${prompt('back', 'Back')}</div>
        <div class="cat-bar" style="position:relative">${glyph('prevCat', 'or-keycap--sm')}<div class="or-tabs" role="tablist" aria-label="Settings categories">${CATS.map(x => `<button class="or-tab" role="tab" aria-selected="${x.id === c.id}" data-cat="${x.id}">${esc(x.name)}</button>`).join('')}</div>${glyph('nextCat', 'or-keycap--sm')}</div>
        <div class="sec-bar" style="position:relative"><div class="or-tabs or-tabs--local" role="tablist" aria-label="${esc(c.name)} sections">${c.sections.map(s => `<button class="or-tab" role="tab" aria-selected="${s.id === sec.id}" data-sec="${s.id}">${esc(s.name)}</button>`).join('')}</div>${c.sections.length > 1 ? glyph('alt2', 'or-keycap--sm') : ''}</div>
        <div class="settings-body" style="position:relative">
          <div class="rows" role="list" id="rows">${rows.map((r, i) => this.rowHtml(r, i)).join('')}</div>
          <aside class="detail" id="detail" aria-live="polite"></aside>
        </div>
        <div class="settings-foot" style="position:relative">
          ${prompt('alt', 'Restore ' + c.name)}
          <div class="prompts">${prompt('nav', 'Select')}${prompt('adjust', 'Adjust')}</div>
          <span class="saved ${state.saveOk ? '' : 'is-warn'}">${icon(state.saveOk ? 'check' : 'warning', '')}${state.saveOk ? 'Saved on this device' : 'Not saved: this browser blocks storage'}</span>
        </div>`;
      const pad = $('#set-pad');
      $$('[data-cat]', pad).forEach(b => (b.onclick = () => { this.cat = b.dataset.cat; this.sec = null; this.row = 0; this.render(); }));
      $$('[data-sec]', pad).forEach(b => (b.onclick = () => { this.sec = b.dataset.sec; this.row = 0; this.render(); }));
      bindActs(pad, { back: () => this.key('back'), alt: () => this.key('alt'), nav: () => {}, adjust: () => {} });
      $$('.srow', pad).forEach((rowEl, i) => this.wireRow(rowEl, rows[i], i));
      this.setRow(this.row, true);
    },
    rowHtml(r, i) {
      const v = V[r.id];
      let ctl = '';
      if (r.type === 'slider') { const p = (v - r.min) / (r.max - r.min) * 100; ctl = `<div class="or-slider"><div class="or-slider__track" role="slider" aria-label="${esc(r.label)}" aria-valuemin="${r.min}" aria-valuemax="${r.max}" aria-valuenow="${v}" aria-valuetext="${fmt(r, v)}"><div class="or-slider__fill" style="width:${p}%"></div><div class="or-slider__thumb" style="left:${p}%"></div></div><span class="or-slider__value">${fmt(r, v)}</span></div>`; }
      else if (r.type === 'switch') ctl = `<span class="or-switch-state">${v ? 'On' : 'Off'}</span><button class="or-switch" role="switch" aria-checked="${!!v}" aria-label="${esc(r.label)}" tabindex="-1"></button>`;
      else if (r.type === 'seg') ctl = `<div class="seg" role="radiogroup" aria-label="${esc(r.label)}">${r.options.map(o => `<button role="radio" aria-checked="${o === v}" tabindex="-1" data-opt="${esc(o)}">${esc(o)}</button>`).join('')}</div>`;
      else if (r.type === 'step') ctl = `<div class="step"><button tabindex="-1" data-d="-1" aria-label="Previous">‹</button><span>${esc(v)}</span><button tabindex="-1" data-d="1" aria-label="Next">›</button></div>`;
      else if (r.type === 'bind') {
        const cap = this.capture && this.capture.id === r.id;
        if (cap && this.capture.conflict) ctl = `<div class="or-conflict" role="alert"><strong>${esc(this.capture.key)} is ${esc(ROWS[this.capture.conflict].label)}.</strong><button class="or-btn" style="height:36px;font-size:16px" data-swap>Swap</button><button class="or-btn or-btn--ghost" style="height:36px;font-size:16px" data-cancel>Cancel</button></div>`;
        else ctl = `<button class="or-binding__slot ${cap ? 'is-listening' : v ? '' : 'is-empty'}" tabindex="-1">${cap ? 'Press a key · Esc cancels · Backspace clears' : `<span class="or-keycap${v && v.length > 4 ? ' or-keycap--wide' : ''}">${esc(v || 'Unbound')}</span>`}</button>`;
      }
      return `<div class="srow" role="listitem" tabindex="-1" data-i="${i}"><div class="srow__label">${esc(r.label)}</div><div class="srow__ctl">${ctl}</div></div>`;
    },
    wireRow(el, r, i) {
      el.addEventListener('mouseenter', () => { if (!this.capture && !this.dragging) this.setRow(i); });
      el.addEventListener('click', () => this.setRow(i));
      if (r.type === 'slider') {
        const tr = $('.or-slider__track', el);
        // Update the slider in place while dragging: re-rendering the row would detach the
        // captured track and end the drag after the first move.
        const set = e => {
          const b = tr.getBoundingClientRect();
          setV(r.id, r.min + Math.max(0, Math.min(1, (e.clientX - b.left) / b.width)) * (r.max - r.min));
          this.paintSlider(el, r);
        };
        tr.addEventListener('pointerdown', e => {
          e.preventDefault();
          if (this.row !== i) this.setRow(i);
          this.dragging = true;
          set(e);
          tr.setPointerCapture(e.pointerId);
          tr.onpointermove = set;
          tr.onpointerup = tr.onpointercancel = () => { tr.onpointermove = null; this.dragging = false; };
        });
      } else if (r.type === 'switch') $('.or-switch', el).onclick = e => { e.stopPropagation(); this.setRow(i); this.activate(); };
      else if (r.type === 'seg') $$('[data-opt]', el).forEach(b => (b.onclick = e => { e.stopPropagation(); this.setRow(i); setV(r.id, b.dataset.opt); this.refreshRow(i); }));
      else if (r.type === 'step') $$('[data-d]', el).forEach(b => (b.onclick = e => { e.stopPropagation(); this.setRow(i); this.adjust(+b.dataset.d); }));
      else if (r.type === 'bind') {
        const slot = $('.or-binding__slot', el); if (slot) slot.onclick = e => { e.stopPropagation(); this.setRow(i); this.activate(); };
        const sw2 = $('[data-swap]', el); if (sw2) sw2.onclick = e => { e.stopPropagation(); this.resolveConflict(true); };
        const cn = $('[data-cancel]', el); if (cn) cn.onclick = e => { e.stopPropagation(); this.resolveConflict(false); };
      }
    },
    paintSlider(el, r) {
      const v = V[r.id], p = (v - r.min) / (r.max - r.min) * 100;
      $('.or-slider__fill', el).style.width = p + '%';
      $('.or-slider__thumb', el).style.left = p + '%';
      $('.or-slider__value', el).textContent = fmt(r, v);
      const tr = $('.or-slider__track', el);
      tr.setAttribute('aria-valuenow', v); tr.setAttribute('aria-valuetext', fmt(r, v));
      this.renderDetail();
      const saved = $('.saved'); if (saved) saved.classList.toggle('is-warn', !state.saveOk);
    },
    refreshRow(i) {
      const rows = this.SEC.rows, el = $(`.srow[data-i="${i}"]`);
      const tmp = document.createElement('div'); tmp.innerHTML = this.rowHtml(rows[i], i);
      const n = tmp.firstElementChild; el.replaceWith(n); this.wireRow(n, rows[i], i);
      if (rows[i].group === 'gfx' || rows[i].id === 'preset') rows.forEach((r, j) => { if (j !== i && (r.group === 'gfx' || r.id === 'preset')) { const o = $(`.srow[data-i="${j}"]`); const t2 = document.createElement('div'); t2.innerHTML = this.rowHtml(r, j); const n2 = t2.firstElementChild; o.replaceWith(n2); this.wireRow(n2, r, j); } });
      this.setRow(this.row, true);
      const saved = $('.saved'); if (saved) { saved.classList.toggle('is-warn', !state.saveOk); }
    },
    setRow(i, keepFocus) {
      this.row = i;
      $$('.srow').forEach((e, j) => e.classList.toggle('is-current', j === i));
      const el = $(`.srow[data-i="${i}"]`);
      if (el) { el.scrollIntoView({ block: 'nearest' }); if (!keepFocus || document.activeElement === document.body || document.activeElement.classList.contains('srow')) el.focus({ preventScroll: true }); }
      this.renderDetail();
    },
    renderDetail() {
      const r = this.SEC.rows[this.row], d = $('#detail'); if (!d) return;
      d.innerHTML = `<div class="or-eyebrow">${esc(this.SEC.name)}</div><h2>${esc(r.label)}</h2><p>${esc(r.help || '')}</p>${r.more ? `<p>${esc(r.more)}</p>` : ''}${r.type === 'bind' ? `<p>Select the slot, then press a key or mouse button. Esc cancels. Backspace clears. If the key is in use you choose whether to swap.</p>` : ''}<div class="viz">${this.viz(r)}</div>`;
    },
    viz(r) {
      const v = V[r.id];
      if (r.viz === 'mouse') { const a = Math.min(1, v / (r.max)) * 120; return `<svg width="260" height="200" viewBox="0 0 260 200"><path d="M${130 - Math.sin(a * Math.PI / 180) * 90} ${150 - Math.cos(a * Math.PI / 180) * 90} A90 90 0 0 1 ${130 + Math.sin(a * Math.PI / 180) * 90} ${150 - Math.cos(a * Math.PI / 180) * 90}" fill="none" stroke="var(--accent)" stroke-width="3" stroke-dasharray="4 6"/><rect x="104" y="80" width="52" height="84" rx="26" fill="none" stroke="var(--text-primary)" stroke-width="3"/><line x1="130" y1="80" x2="130" y2="112" stroke="var(--text-primary)" stroke-width="3"/><rect x="126" y="92" width="8" height="14" rx="4" fill="var(--text-primary)"/></svg><div class="viz-caption">${fmt(r, v)} · ${v < 0.5 ? 'Precise' : v > 1.4 ? 'Fast' : 'Standard'}</div>`; }
      if (r.viz === 'stick') { const dz = (r.id === 'dzRight' ? V.dzRight : V.dzLeft) / 100; return `<svg width="220" height="220" viewBox="0 0 220 220"><circle cx="110" cy="110" r="100" fill="none" stroke="var(--text-primary)" stroke-width="2"/><circle cx="110" cy="110" r="${Math.max(4, dz * 100)}" fill="rgb(197 242 119 / .18)" stroke="var(--accent)" stroke-dasharray="4 4"/><line x1="110" y1="10" x2="110" y2="210" stroke="var(--border)"/><line x1="10" y1="110" x2="210" y2="110" stroke="var(--border)"/><circle cx="110" cy="110" r="7" fill="var(--text-primary)"/></svg><div class="viz-caption">${state.device === 'pad' ? 'Move the stick to test drift' : 'Connect a controller to test drift'} · shaded area is ignored</div>`; }
      if (r.viz === 'volume') { const n = Math.ceil(v / 25); return `<svg width="240" height="140" viewBox="0 0 240 140"><path d="M30 50h30l40-34v108L60 90H30z" fill="none" stroke="var(--text-primary)" stroke-width="3"/>${[0, 1, 2, 3].map(k => `<path d="M${120 + k * 22} ${40 - k * 10} q${16 + k * 4} ${30 + k * 10} 0 ${60 + k * 20}" fill="none" stroke="${k < n ? 'var(--accent)' : 'var(--surface-raised)'}" stroke-width="3"/>`).join('')}</svg><div class="viz-caption">${esc(r.label)} ${Math.round(v)}%</div>`; }
      if (r.viz === 'fov') { const a = v / 2 * Math.PI / 180; return `<svg width="260" height="180" viewBox="0 0 260 180"><path d="M130 170 L${130 - Math.sin(a) * 150} ${170 - Math.cos(a) * 150} A150 150 0 0 1 ${130 + Math.sin(a) * 150} ${170 - Math.cos(a) * 150} Z" fill="rgb(197 242 119 / .12)" stroke="var(--accent)" stroke-width="2"/><circle cx="130" cy="170" r="5" fill="var(--text-primary)"/></svg><div class="viz-caption">${v}° horizontal</div>`; }
      if (r.viz === 'preset') { const lv = x => Q4.indexOf(V[x]) + 1; return `<div class="preset-bars">${['shadows', 'textures', 'foliage', 'effects', 'viewDist'].map(k => `<span>${esc(ROWS[k].label)}</span><span class="bars">${[1, 2, 3, 4].map(n => `<i class="${n <= lv(k) ? 'on' : ''}"></i>`).join('')}</span>`).join('')}</div><div class="viz-caption">Preset: ${esc(V.preset)}</div>`; }
      if (r.viz === 'hud') return `<div class="mini-hud" style="--hud-scale:${V.hudScale / 100};zoom:${V.textScale / 100}"><div class="or-hud" style="align-self:flex-start;transform:scale(${V.hudScale / 100});transform-origin:left top"><div class="or-meter or-meter--shield">${icon('shield', 'or-meter__icon')}<div class="or-meter__track">${Orbit.meterSegments(40)}</div><span class="or-meter__value">40</span></div><div class="or-meter or-meter--health">${icon('health', 'or-meter__icon')}<div class="or-meter__track">${Orbit.meterSegments(100)}</div><span class="or-meter__value">100</span></div></div><div class="msg or-hud" style="align-self:flex-start">Storm closes in 0:30. Move to the safe zone.</div></div><div class="viz-caption">Preview · HUD ${V.hudScale}% · text ${V.textScale}%</div>`;
      if (r.viz === 'damage' || r.viz === 'heal') {
        const heal = r.viz === 'heal', on = heal ? V.healGlow : V.dmgDir;
        return `<div class="mini-hud" style="min-height:200px;position:relative">${heal ? `<div class="heal-glow ${on ? 'on' : ''}" style="position:absolute;inset:0"></div>` : `<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 100% 40%, rgb(255 121 127 / ${0.6 * V.dmgIntensity / 100}), transparent 55%)"></div>${V.dmgDir ? `<svg viewBox="0 0 200 200" style="position:absolute;left:50%;top:50%;width:150px;margin:-75px 0 0 -75px;transform:rotate(80deg)"><path d="M70 22 A80 80 0 0 1 130 22" fill="none" stroke="var(--danger)" stroke-width="7" stroke-linecap="round"/></svg>` : ''}`}<div class="crosshair" style="position:absolute"><i></i><i></i><i></i><i></i></div></div><div class="viz-caption">${heal ? (on ? 'Shown while using Shield Pack' : 'Off · the heal timer still shows') : `Hit from the right · ${V.dmgIntensity}%${V.dmgDir ? '' : ' · arc off'}`}</div>`;
      }
      if (r.viz === 'pad') { const ps = padStyle() === 'ps'; const g = ps ? PAD.ps : PAD.xbox; return `<svg width="300" height="170" viewBox="0 0 300 170"><path d="M60 30 h180 q40 0 50 50 l10 60 q4 26 -20 26 q-16 0 -30 -26 l-14 -24 h-172 l-14 24 q-14 26 -30 26 q-24 0 -20 -26 l10 -60 q10 -50 50 -50z" fill="none" stroke="var(--text-primary)" stroke-width="2.5"/><circle cx="95" cy="80" r="18" fill="none" stroke="var(--text-primary)" stroke-width="2"/><circle cx="180" cy="112" r="18" fill="none" stroke="var(--text-primary)" stroke-width="2"/>${[[230, 60, g.alt2], [210, 80, g.alt], [250, 80, g.back], [230, 100, g.confirm]].map(([x, y, t], k) => `<circle cx="${x}" cy="${y}" r="11" fill="${k === 3 ? 'var(--accent)' : 'none'}" stroke="${k === 3 ? 'var(--accent)' : 'var(--text-primary)'}" stroke-width="2"/><text x="${x}" y="${y + 5}" text-anchor="middle" font-size="13" font-weight="700" fill="${k === 3 ? 'var(--text-on-accent)' : 'var(--text-primary)'}" font-family="IBM Plex Sans">${t}</text>`).join('')}</svg><div class="viz-caption">${state.device === 'pad' ? 'Controller connected' : 'No controller connected'} · showing ${ps ? 'PlayStation' : 'Xbox'}</div>`; }
      if (r.viz === 'key') return `<div style="display:flex;align-items:center;gap:16px"><span class="or-keycap or-keycap--wide" style="height:56px;min-width:72px;font-size:22px">${esc(V[r.id] || '—')}</span><span class="note">Enter or click to rebind</span></div>`;
      return '';
    },
    adjust(d) {
      const r = this.SEC.rows[this.row], v = V[r.id];
      if (r.type === 'slider') setV(r.id, v + d * r.step * (r.unit === 'x' ? 1 : (r.max - r.min > 50 ? 5 : 1)));
      else if (r.type === 'switch') setV(r.id, d > 0);
      else if (r.type === 'seg' || r.type === 'step') { const o = r.options, i = o.indexOf(v); const n = r.type === 'seg' ? Math.max(0, Math.min(o.length - 1, i + d)) : (i + d + o.length) % o.length; setV(r.id, o[n]); }
      else return;
      this.refreshRow(this.row);
    },
    activate() {
      const r = this.SEC.rows[this.row];
      if (r.type === 'switch') { setV(r.id, !V[r.id]); this.refreshRow(this.row); }
      else if (r.type === 'seg' || r.type === 'step') { const o = r.options; setV(r.id, o[(o.indexOf(V[r.id]) + 1) % o.length]); this.refreshRow(this.row); }
      else if (r.type === 'bind') { this.capture = { id: r.id }; this.refreshRow(this.row); }
    },
    captureKey(name) {
      const c = this.capture; if (!c || c.conflict) return;
      if (name === 'Escape') { this.capture = null; this.refreshRow(this.row); return; }
      if (name === 'Backspace') { setV(c.id, ''); this.capture = null; this.refreshRow(this.row); return; }
      const other = Object.keys(V).find(k => k.startsWith('bind.') && k !== c.id && V[k] === name);
      if (other) { c.conflict = other; c.key = name; this.refreshRow(this.row); return; }
      setV(c.id, name); this.capture = null; this.refreshRow(this.row);
    },
    resolveConflict(swap) {
      const c = this.capture;
      if (swap) { const old = V[c.id]; setV(c.conflict, old); setV(c.id, c.key); toast('success', `${c.key} is now ${ROWS[c.id].label}. ${ROWS[c.conflict].label} moved to ${old || 'Unbound'}.`); }
      this.capture = null;
      this.render();
    },
    async key(a, e) {
      if (dialogState) return;
      if (this.capture) { if (a === 'back' && this.capture.conflict) this.resolveConflict(false); return; }
      const rows = this.SEC.rows, c = this.C;
      if (a === 'up') this.setRow((this.row - 1 + rows.length) % rows.length);
      else if (a === 'down') this.setRow((this.row + 1) % rows.length);
      else if (a === 'left') this.adjust(-1);
      else if (a === 'right') this.adjust(1);
      else if (a === 'confirm') this.activate();
      else if (a === 'prevCat' || a === 'nextCat') { const i = CATS.indexOf(c); this.cat = CATS[(i + (a === 'prevCat' ? -1 : 1) + CATS.length) % CATS.length].id; this.sec = null; this.row = 0; this.render(); }
      else if (a === 'alt2') { const i = c.sections.indexOf(this.SEC); this.sec = c.sections[(i + (e && e.shiftKey ? -1 : 1) + c.sections.length) % c.sections.length].id; this.row = 0; this.render(); }
      else if (a === 'alt') {
        const n = c.sections.reduce((s, x) => s + x.rows.length, 0);
        if (await confirmDialog({ title: `Restore ${c.name}?`, body: `Resets all ${n} ${c.name.toLowerCase()} settings to their defaults. Other categories keep their values.`, ok: `Restore ${c.name}` })) {
          c.sections.forEach(s => s.rows.forEach(r => (V[r.id] = r.def))); setV(c.sections[0].rows[0].id, V[c.sections[0].rows[0].id]);
          this.render(); toast('success', `${c.name} restored to defaults`);
        }
      } else if (a === 'back') back();
    },
    onDevice() { if (state.screen === 'settings') this.renderDetail(); }
  };

  // ---------------------------------------------------------------- keyboard, mouse, gamepad
  function keyName(e) {
    if (e.code === 'Space') return 'Space';
    if (e.key === 'Shift' || e.key === 'Control' || e.key === 'Alt') return e.key === 'Control' ? 'Ctrl' : e.key;
    if (e.key.length === 1) return e.key.toUpperCase();
    return e.key;
  }
  const NAV_KEYS = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right', Enter: 'confirm', Escape: 'back' };
  window.addEventListener('keydown', e => {
    setDevice('kb');
    if (e.target.tagName === 'INPUT') return;
    const scr = SCREENS[state.screen];
    if (state.screen === 'settings' && scr.capture && !scr.capture.conflict) { e.preventDefault(); scr.captureKey(e.key === 'Escape' || e.key === 'Backspace' ? e.key : keyName(e)); return; }
    if (dialogState) {
      if (e.key === 'Escape') { e.preventDefault(); dialogState.close(false); }
      else if (/Arrow(Left|Right|Up|Down)/.test(e.key)) { e.preventDefault(); const b = dialogState.buttons, i = b.indexOf(document.activeElement); b[(i + 1) % b.length].focus(); }
      return;
    }
    if (e.key === '`') { toggleProto(); return; }
    if (state.screen === 'game') { Match.keydown(e, keyName(e)); return; }
    let a = NAV_KEYS[e.key];
    const k = keyName(e);
    if (!a && state.screen === 'settings') a = { Q: 'prevCat', E: 'nextCat', Tab: 'alt2', R: 'alt' }[k];
    if (!a && state.screen === 'loading') a = 'any';
    if (a) { if (a !== 'confirm' || state.screen === 'settings' || state.screen === 'loading') e.preventDefault(); if (scr.key) scr.key(a, e); }
  });
  window.addEventListener('keyup', e => { if (state.screen === 'game') Match.keyup(e, keyName(e)); });
  window.addEventListener('pointerdown', e => {
    if (e.pointerType === 'mouse' || e.pointerType === 'touch') setDevice('kb');
    if (state.screen === 'loading' && !e.target.closest('.proto, .proto-btn, .tip, #retry')) SCREENS.loading.pointer();
  });
  window.addEventListener('mousedown', e => {
    const scr = SCREENS.settings;
    if (state.screen === 'settings' && scr.capture && !scr.capture.conflict && e.target.closest('.or-binding__slot') === null) { e.preventDefault(); scr.captureKey('M' + (e.button + 1)); }
  });

  // Gamepad: polled; menu actions with key-repeat, match controls handed to Match.
  const PADMAP = { 0: 'confirm', 1: 'back', 2: 'alt', 3: 'alt2', 4: 'prevCat', 5: 'nextCat', 12: 'up', 13: 'down', 14: 'left', 15: 'right', 9: 'back' };
  const prevBtn = {}; let stickHeld = null, stickAt = 0;
  function pollPads() {
    const pads = navigator.getGamepads ? Array.from(navigator.getGamepads()).filter(Boolean) : [];
    const p = pads[0];
    if (p) {
      const pressed = p.buttons.map(b => b.pressed);
      const active = pressed.some(Boolean) || p.axes.some(a => Math.abs(a) > 0.5);
      if (active) setDevice('pad', p.id);
      if (state.screen === 'game') Match.pad(p, pressed, prevBtn);
      else {
        pressed.forEach((d, i) => {
          if (d && !prevBtn[i] && PADMAP[i] != null) dispatchPad(PADMAP[i]);
        });
        const ax = p.axes[0] || 0, ay = p.axes[1] || 0;
        const dir = ay < -0.6 ? 'up' : ay > 0.6 ? 'down' : ax < -0.6 ? 'left' : ax > 0.6 ? 'right' : null;
        const now = performance.now();
        if (dir && (dir !== stickHeld || now - stickAt > 180)) { dispatchPad(dir); stickAt = now + (dir !== stickHeld ? 220 : 0); }
        stickHeld = dir;
      }
      pressed.forEach((d, i) => (prevBtn[i] = d));
    }
    requestAnimationFrame(pollPads);
  }
  function dispatchPad(a) {
    if (dialogState) { if (a === 'back') dialogState.close(false); else if (a === 'confirm') document.activeElement.click(); else { const b = dialogState.buttons, i = b.indexOf(document.activeElement); b[(i + 1) % b.length].focus(); } return; }
    const scr = SCREENS[state.screen];
    if (state.screen === 'loading') { scr.key(a); return; }
    if (scr.key) scr.key(a, {});
  }
  window.addEventListener('gamepadconnected', e => { setDevice('pad', e.gamepad.id); toast('success', 'Controller connected'); });
  window.addEventListener('gamepaddisconnected', () => { setDevice('kb'); toast('warning', 'Controller disconnected'); });

  // ---------------------------------------------------------------- prototype drawer
  const protoEl = $('#proto');
  function toggleProto() { protoEl.classList.toggle('is-open'); }
  $('#proto-btn').onclick = toggleProto;
  protoEl.addEventListener('click', e => {
    const b = e.target.closest('[data-go],[data-ev]'); if (!b) return;
    if (b.dataset.go) {
      const g = b.dataset.go;
      if (['inventory', 'map', 'pause'].includes(g)) { if (state.screen !== 'game') go('game', { spawn: 'glass' }); Match.open(g); }
      else if (g === 'results') go('results', { reason: 'eliminated', by: 'Bot Rhea', weapon: 'SR-8 Longview', placement: 12, elims: 3, dmg: 486, time: 522 });
      else if (g === 'game') go('game', { spawn: 'glass' });
      else go(g);
    } else if (window.Match && state.screen === 'game') Match.event(b.dataset.ev);
    else toast('warning', 'Start a match first: Lobby › Start match');
  });
  $('#p-fail').onchange = e => (state.proto.failDownload = e.target.checked);
  $('#p-bots').onchange = e => (state.proto.botsShoot = e.target.checked);
  $('#p-freeze').onchange = e => (state.proto.pauseFreezes = e.target.checked);

  window.OR = { state, V, ROWS, SCREENS, go, back, toast, confirmDialog, glyph, glyphText, prompt, refreshGlyphs, bindActs, moveFocus, focusFirst, W, drawWorld, esc, setV, store };
  window.addEventListener('DOMContentLoaded', () => {
    applySettings();
    requestAnimationFrame(pollPads);
    go('loading');
  });
})();
