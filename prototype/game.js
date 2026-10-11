// Orbit Royale prototype: deployment, match HUD, inventory, map, pause, results.
// Balance numbers (magazines, damage, timers) are placeholders, not tuned values.
(function () {
  const { state, V, SCREENS, go, back, toast, confirmDialog, glyph, glyphText, prompt, bindActs, W, esc } = OR;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const LOC = Ringfall.LOCATIONS;
  const fmtTime = s => `${Math.floor(Math.max(0, s) / 60)}:${String(Math.floor(Math.max(0, s) % 60)).padStart(2, '0')}`;

  // ---------------------------------------------------------------- items (proposed launch set)
  const ITEMS = {
    ar7: { name: 'AR-7 Wayfarer', kind: 'weapon', icon: 'rifle', role: 'Assault rifle · dependable midrange automatic', ammo: 'medium', mag: 30, dmg: 24, auto: true, vm: 'rifle' },
    sg4: { name: 'SG-4 Breaker', kind: 'weapon', icon: 'shotgun', role: 'Shotgun · strong close bursts, costly misses', ammo: 'shells', mag: 6, dmg: 70, vm: 'shotgun' },
    sr8: { name: 'SR-8 Longview', kind: 'weapon', icon: 'sniper', role: 'Sniper · precision at range, slow follow-up', ammo: 'heavy', mag: 5, dmg: 95, vm: 'rifle' },
    fieldPatch: { name: 'Field Patch', kind: 'heal', pool: 'health', amount: 25, stack: 6, cap: 6, time: 2, icon: 'patch', tint: 'health', effect: '+25 health' },
    shieldCell: { name: 'Shield Cell', kind: 'heal', pool: 'shield', amount: 25, stack: 6, cap: 6, time: 2, icon: 'cell', tint: 'shield', effect: '+25 shields' },
    shieldPack: { name: 'Shield Pack', kind: 'heal', pool: 'shield', amount: 50, stack: 3, cap: 3, time: 3.5, icon: 'shield', tint: 'shield', effect: '+50 shields' },
    phoenix: { name: 'Phoenix Capsule', kind: 'heal', pool: 'both', amount: 200, stack: 1, cap: 1, time: 9, icon: 'phoenix', tint: 'shield', effect: 'Full health and shields' },
    frag: { name: 'Fragmentation grenade', kind: 'grenade', stack: 3, cap: 3, icon: 'grenade', effect: 'Timed explosive that bounces' },
    tether: { name: 'Tethercaster', kind: 'utility', stack: 1, cap: 1, icon: 'grapple', effect: 'Hook terrain or structures and swing toward them', cooldown: 8 }
  };
  const AMMO = { medium: { name: 'Medium', cap: 300 }, shells: { name: 'Shells', cap: 36 }, heavy: { name: 'Heavy', cap: 30 }, light: { name: 'Light', cap: 240 } };
  const EXTRA = {
    patch: '<rect x="3" y="6" width="18" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M10.5 8.5h3v2h2v3h-2v2h-3v-2h-2v-3h2z" fill="currentColor"/>',
    cell: '<path d="M12 4l6.5 3.75v7.5L12 19l-6.5-3.75v-7.5z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 8l3 1.7v3.6L12 15l-3-1.7V9.7z" fill="currentColor"/>',
    phoenix: '<path d="M12 2l8.5 4.9v10.2L12 22l-8.5-4.9V6.9z" fill="none" stroke="var(--shield)" stroke-width="2"/><path d="M10 7h4v4h4v4h-4v4h-4v-4H6v-4h4z" fill="var(--health)"/>'
  };
  const ico = (name, cls) => EXTRA[name] ? `<svg class="${cls || ''}" viewBox="0 0 24 24" aria-hidden="true">${EXTRA[name]}</svg>` : Orbit.icon(name, cls);

  // ---------------------------------------------------------------- match state
  let G = null;
  const BOT_NAMES = ['Rhea', 'Ivo', 'Kade', 'Sol', 'Varn', 'Mira', 'Ilse', 'Tamsin', 'Oren', 'Juno', 'Brask', 'Lio', 'Pell', 'Astra', 'Corvin', 'Nadi', 'Wren', 'Esk'];
  function newMatch(spawnId) {
    const sp = LOC.find(l => l.id === spawnId) || LOC[2];
    const bots = [];
    for (let i = 0; i < 7; i++) bots.push({ id: i, name: 'Bot ' + BOT_NAMES[i], bearing: (i - 3) * 14 + (Math.random() * 8 - 4), dist: 28 + Math.random() * 50, hp: 100, alive: true, flash: 0 });
    return {
      heading: 0, hp: 100, sh: 70, sel: 0, alive: 60, elims: 0, dmgDealt: 0, t: 0, spawn: sp,
      pos: { x: sp.x, y: sp.y }, marker: null,
      slots: [{ id: 'ar7', qty: 1, mag: 24 }, { id: 'sg4', qty: 1, mag: 5 }, { id: 'tether', qty: 1, readyAt: 0 }, { id: 'shieldPack', qty: 2 }, { id: 'fieldPatch', qty: 4 }],
      ammo: { medium: 150, shells: 18, heavy: 10, light: 0 },
      ground: [{ id: 'shieldPack', qty: 2 }, { id: 'shieldCell', qty: 4 }, { id: 'frag', qty: 3 }, { id: 'sr8', qty: 1, mag: 5 }, { id: 'phoenix', qty: 1 }],
      bots, arcs: [], feed: [], keys: {},
      storm: { x: 0.5, y: 0.5, r: 0.62 }, safe: { x: 0.5 + (Math.random() - 0.5) * 0.12, y: 0.48, r: 0.24 }, phase: 1, stormT: 95, closing: 0,
      nextElim: 4, nextShot: 6, using: null, reload: null, fireHeld: false, lastShot: 0, stormTick: 0, overlay: null, dead: false, lastHeading: null
    };
  }
  const selItem = () => G.slots[G.sel] && ITEMS[G.slots[G.sel].id];
  const carried = id => G.slots.reduce((s, x) => s + (x && x.id === id ? x.qty : 0), 0);
  const eligible = (id, i) => (ITEMS[id].kind === 'weapon' ? i < 2 : i >= 2);
  function addFeed(html) { G.feed.unshift({ html, t: G.t }); G.feed = G.feed.slice(0, 4); paintFeed(); }

  // ---------------------------------------------------------------- DEPLOY
  const ROLES = { crown: 'Long sightlines', anchor: 'Dense fights, vehicles', glass: 'Risky crossings', bloom: 'Cover, quiet looting', relay: 'Vertical combat', spine: 'Contested high ground', hollow: 'Close combat' };
  SCREENS.deploy = {
    enter(el) {
      W.mode = 'vista';
      this.sel = null; this.hover = null; this.t = 20;
      el.innerHTML = `<div class="deploy"><div class="map" style="position:relative"><canvas id="dmap" aria-label="Ringfall map. Choose a landing zone."></canvas><div class="zoom-label">Ringfall · Veyra</div></div>
        <aside class="side"><div><div class="or-eyebrow">Deployment</div><h2>Choose where to land</h2></div>
          <p class="note">Transport and drop rules are still undecided. This prototype only picks your landing zone.</p>
          <div><div class="or-eyebrow">Drop window closes in</div><div class="big-num" id="dt">0:20</div></div>
          <div class="loc-list">${LOC.map(l => `<button data-nav data-loc="${l.id}" aria-pressed="false"><span>${esc(l.name)}</span><small>${ROLES[l.id]}</small></button>`).join('')}</div>
          <button class="or-btn or-btn--primary" data-nav id="deploy-go">Deploy to a random zone</button>
          <div class="prompts">${prompt('confirm', 'Select')}${prompt('back', 'Back to lobby')}</div></aside></div>`;
      const c = $('#dmap');
      this.paint = () => { this.geo = Ringfall.drawMap(c, { cx: 0.5, cy: 0.5, zoom: 0.92 }, {}, { hover: this.hover, selected: this.sel }); };
      this.paint();
      const pick = (e) => { const b = c.getBoundingClientRect(), g = this.geo; const mx = (e.clientX - b.left - g.ox) / g.size, my = (e.clientY - b.top - g.oy) / g.size; let best = null, bd = 0.07; LOC.forEach(l => { const d = Math.hypot(l.x - mx, l.y - my); if (d < bd) { bd = d; best = l.id; } }); return best; };
      c.onmousemove = e => { const h = pick(e); if (h !== this.hover) { this.hover = h; this.paint(); } c.style.cursor = h ? 'pointer' : 'default'; };
      c.onclick = e => { const p = pick(e); if (p) this.select(p); };
      $$('[data-loc]', el).forEach(b => (b.onclick = () => this.select(b.dataset.loc)));
      $('#deploy-go').onclick = () => this.deploy();
      bindActs(el, { confirm: () => this.deploy(), back: () => back() });
      $('[data-loc]', el).focus();
      this.timer = setInterval(() => { this.t -= 1; const d = $('#dt'); if (d) d.textContent = fmtTime(this.t); if (this.t <= 0) this.deploy(); }, 1000);
    },
    exit() { clearInterval(this.timer); },
    resize() { this.paint && this.paint(); },
    select(id) {
      this.sel = id; this.paint();
      $$('[data-loc]').forEach(b => b.setAttribute('aria-pressed', b.dataset.loc === id));
      $('#deploy-go').textContent = 'Deploy to ' + LOC.find(l => l.id === id).name;
    },
    deploy() { clearInterval(this.timer); go('game', { spawn: this.sel || LOC[Math.floor(Math.random() * LOC.length)].id }); },
    key(a) {
      const el = $('#s-deploy');
      if (a === 'up' || a === 'left') OR.moveFocus(el, -1);
      else if (a === 'down' || a === 'right') OR.moveFocus(el, 1);
      else if (a === 'back') back();
      else if (a === 'confirm' && state.device === 'pad') document.activeElement.click();
    }
  };

  // ---------------------------------------------------------------- viewmodels (placeholder art)
  const VM = {
    rifle: `<svg viewBox="0 0 600 400" class="weapon-vm" id="vm"><defs><linearGradient id="gm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a4668"/><stop offset="1" stop-color="#141a2a"/></linearGradient></defs><path d="M120 260 L420 150 L470 150 L560 210 L560 260 L440 300 L300 340 L250 400 L140 400 L160 330 Z" fill="url(#gm)"/><path d="M60 300 L140 270 L150 290 L70 330Z" fill="#232c44"/><rect x="250" y="170" width="120" height="26" rx="6" transform="rotate(-20 250 170)" fill="#46566d"/><rect x="300" y="196" width="40" height="8" rx="3" transform="rotate(-20 300 196)" fill="#ffb45c"/><path d="M330 300 L420 270 L440 330 L360 400 L300 400Z" fill="#2a2f3f"/><circle cx="510" cy="215" r="6" fill="#70d6ff"/></svg>`,
    shotgun: `<svg viewBox="0 0 600 400" class="weapon-vm" id="vm"><defs><linearGradient id="gm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a3f3a"/><stop offset="1" stop-color="#1a1416"/></linearGradient></defs><path d="M80 280 L430 170 L520 180 L560 240 L470 290 L320 340 L270 400 L150 400 L170 330Z" fill="url(#gm)"/><rect x="120" y="250" width="320" height="22" rx="10" transform="rotate(-18 120 250)" fill="#2b3550"/><rect x="200" y="252" width="120" height="30" rx="8" transform="rotate(-18 200 252)" fill="#5b4a3a"/><path d="M340 300 L430 270 L450 330 L370 400 L310 400Z" fill="#2a2f3f"/><rect x="430" y="196" width="30" height="8" rx="3" fill="#ffb45c"/></svg>`,
    heal: c => `<svg viewBox="0 0 600 400" class="weapon-vm" id="vm"><rect x="330" y="170" width="120" height="190" rx="24" fill="#1d2438" stroke="#46566d" stroke-width="4" transform="rotate(14 390 265)"/><rect x="356" y="200" width="68" height="110" rx="12" fill="${c}" opacity=".8" transform="rotate(14 390 265)"/><path d="M290 400 L340 300 L420 290 L470 400Z" fill="#2a2f3f"/></svg>`,
    tether: `<svg viewBox="0 0 600 400" class="weapon-vm" id="vm"><path d="M200 300 L430 200 L500 210 L520 250 L440 290 L330 340 L290 400 L190 400Z" fill="#232c44"/><path d="M500 210 l30 -30 m-30 30 l40 0 m-40 0 l20 34" stroke="#c5f277" stroke-width="8" stroke-linecap="round" fill="none"/><circle cx="360" cy="270" r="22" fill="none" stroke="#46566d" stroke-width="6"/><path d="M330 310 L420 280 L440 340 L360 400 L300 400Z" fill="#2a2f3f"/></svg>`,
    grenade: `<svg viewBox="0 0 600 400" class="weapon-vm" id="vm"><circle cx="400" cy="250" r="56" fill="#2b3550"/><rect x="380" y="180" width="40" height="22" rx="4" fill="#46566d"/><path d="M420 190 l40 -20" stroke="#ffb45c" stroke-width="6"/><path d="M300 400 L350 290 L440 300 L480 400Z" fill="#2a2f3f"/></svg>`,
    none: `<svg viewBox="0 0 600 400" class="weapon-vm" id="vm"></svg>`
  };
  function vmFor() {
    const it = selItem(); if (!it) return VM.none;
    if (it.kind === 'weapon') return VM[it.vm];
    if (it.kind === 'heal') return VM.heal(it.tint === 'health' ? '#ff8d7f' : '#70d6ff');
    if (it.kind === 'utility') return VM.tether;
    return VM.grenade;
  }

  // ---------------------------------------------------------------- slot rendering
  function slotHtml(i, o) {
    o = o || {};
    const s = G.slots[i], it = s && ITEMS[s.id];
    const cls = ['or-slot'];
    if (!s) cls.push('is-empty');
    if (o.selected) cls.push('is-selected');
    if (it && it.tint) cls.push('or-slot--' + it.tint);
    if (o.extra) cls.push(o.extra);
    let charge = '';
    if (s && s.id === 'tether' && s.readyAt > G.t) charge = `<span class="or-slot__charge"><i style="width:${(1 - (s.readyAt - G.t) / ITEMS.tether.cooldown) * 100}%"></i></span>`;
    const qty = s && (it.kind !== 'weapon' && it.kind !== 'utility') ? `<span class="or-slot__qty">${s.qty}</span>` : s && it.kind === 'weapon' ? `<span class="or-slot__qty" style="font-size:14px;color:var(--text-secondary)">${s.mag}</span>` : '';
    const label = s ? `${it.name}${it.kind === 'heal' || it.kind === 'grenade' ? ', ' + s.qty : ''}` : `Empty slot ${i + 1}`;
    return `<button class="${cls.join(' ')}" data-slot="${i}" aria-label="${esc(label)}" tabindex="-1">${glyph('slot' + (i + 1), 'or-keycap--sm or-slot__key')}${i < 2 ? '<span class="or-slot__weapon-mark"></span>' : ''}${s ? ico(it.icon, 'or-slot__icon') : ''}${qty}${charge}</button>`;
  }

  // ---------------------------------------------------------------- GAME SCREEN
  let raf = 0, lastT = 0, locked = false, wantPause = true;
  SCREENS.game = {
    enter(el, p) {
      if (!(p.returning && G)) G = newMatch(p.spawn);
      W.mode = 'game';
      el.innerHTML = `<div class="game ${locked ? '' : 'no-lock'}" id="groot" style="position:absolute;inset:0">
        <div id="vmwrap"></div>
        <div class="dmg-glow" id="dglow"></div><div class="low-health" id="lowhp"></div><div class="heal-glow" id="hglow"></div><div class="storm-edge" id="sedge"></div>
        <div class="hud" id="hud">
          <div class="hud-tl"><div class="minimap"><canvas id="mini"></canvas></div><div class="storm-line" id="stormline"></div></div>
          <div class="compass" aria-hidden="true"><div class="compass-strip" id="cstrip"></div></div><div class="compass-bearing" id="cbear"></div>
          <div class="hud-tr"><div class="stats"><div class="or-hud"><span class="or-stat">${Orbit.icon('survivors')}<span id="surv"></span></span><small>Alive</small></div><div class="or-hud"><span class="or-stat">${Orbit.icon('eliminations')}<span id="elims"></span></span><small>Elims</small></div></div><div class="feed" id="feed"></div></div>
          <div class="crosshair ${V.crosshair === 'Dot' ? 'is-dot' : ''}" id="xh"><i></i><i></i><i></i><i></i></div><div class="hitmarker" id="hm"></div><div class="dmg-arcs" id="arcs"></div><div id="dnum" style="position:absolute;left:calc(50% + 28px);top:calc(50% - 40px);font:700 22px/1 var(--font-ui);color:var(--text-primary);text-shadow:0 1px 3px #000"></div>
          <div class="use-ring" id="uring" hidden><svg viewBox="0 0 88 88"><circle class="track" cx="44" cy="44" r="40"/><circle class="fill" cx="44" cy="44" r="40" stroke-dasharray="251.3" stroke-dashoffset="251.3"/></svg></div><div class="use-label" id="ulabel" hidden></div>
          <div class="hud-prompts" id="hprompts"></div>
          <div class="hud-bl"><div class="or-hud"><div class="or-meter or-meter--shield">${Orbit.icon('shield', 'or-meter__icon')}<div class="or-meter__track" id="mtsh"></div><span class="or-meter__value" id="vsh"></span></div><div class="or-meter or-meter--health">${Orbit.icon('health', 'or-meter__icon')}<div class="or-meter__track" id="mthp"></div><span class="or-meter__value" id="vhp"></span></div></div><div class="heal-status" id="hstat"></div></div>
          <div class="hud-bc"><div class="slot-caption" id="scap"></div><div class="or-inventory" id="slots"></div></div>
          <div class="hud-br" id="ammo"></div>
        </div>
        <div class="lock-hint" id="lockhint"></div>
        <div class="overlay" id="ov-inventory"></div><div class="overlay" id="ov-map"></div><div class="overlay" id="ov-pause"></div>
      </div>`;
      const root = $('#groot');
      root.addEventListener('mousedown', onMouseDown);
      root.addEventListener('contextmenu', e => { if (!G.overlay || G.overlay !== 'map') e.preventDefault(); });
      root.addEventListener('wheel', e => { if (!G.overlay) { selectSlot((G.sel + (e.deltaY > 0 ? 1 : -1) + 5) % 5); } }, { passive: true });
      paintAll();
      if (p.returning) Match.open('pause');
      else { addFeed(`Landed at <b>${esc(G.spawn.name)}</b>`); paintLockHint(); }
      lastT = performance.now();
      cancelAnimationFrame(raf); raf = requestAnimationFrame(loop);
    },
    exit(next) {
      if (next !== 'settings') { cancelAnimationFrame(raf); G = null; }
      wantPause = false; if (document.pointerLockElement) document.exitPointerLock();
    },
    resize() { if (G) paintMini(); }
  };

  function paintLockHint() {
    const h = $('#lockhint'); if (!h) return;
    if (locked || G.overlay) { h.innerHTML = ''; return; }
    h.innerHTML = `<button class="or-btn or-btn--primary" id="lockbtn">Click to aim with the mouse</button><p>Mouse turns, ${glyphText('fire')} fires or uses the selected item, ${glyphText('forward')} moves, ${glyphText('slot1')}–${glyphText('slot5')} select slots, ${glyphText('inventory')} inventory, ${glyphText('map')} map, Esc menu. Arrow keys also turn. Press <b>\`</b> for prototype controls.</p>`;
    $('#lockbtn').onclick = e => { e.stopPropagation(); requestLock(); };
  }
  function requestLock() {
    const root = $('#groot'); if (!root || !root.requestPointerLock) return;
    try { const r = root.requestPointerLock(); if (r && r.catch) r.catch(() => {}); } catch (e) { /* unsupported: arrow keys still turn */ }
  }
  document.addEventListener('pointerlockchange', () => {
    locked = !!document.pointerLockElement;
    const root = $('#groot'); if (root) root.classList.toggle('no-lock', !locked);
    if (!G || state.screen !== 'game') return;
    if (!locked && wantPause && !G.overlay) Match.open('pause');
    wantPause = true;
    paintLockHint();
  });
  document.addEventListener('mousemove', e => {
    if (!G || state.screen !== 'game' || G.overlay) return;
    if (locked) turn(e.movementX * 0.12 * V.sens);
    else if (e.buttons & 2) turn(e.movementX * 0.25 * V.sens);
  });
  function turn(d) { G.heading = (G.heading + d + 360) % 360; }
  function onMouseDown(e) {
    if (!G || G.overlay || G.dead) return;
    if (e.target.closest('.lock-hint, .or-slot')) { const s = e.target.closest('.or-slot'); if (s) selectSlot(+s.dataset.slot); return; }
    if (e.button === 0) { G.fireHeld = true; primary(); }
  }
  document.addEventListener('mouseup', e => {
    if (!G || e.button !== 0) return;
    G.fireHeld = false;
    if (G.using && V.healMode === 'Hold') interruptUse('Released before finishing');
  });

  // ---------------------------------------------------------------- actions
  function selectSlot(i) {
    if (!G || i === G.sel) return;
    if (G.using) interruptUse('Switched slot');
    if (G.reload) G.reload = null;
    G.sel = i; paintSlots(); paintAmmo(); paintVM();
  }
  function primary() {
    const s = G.slots[G.sel], it = selItem();
    if (!s) { flashCaption('Empty slot'); return; }
    if (it.kind === 'weapon') fire();
    else if (it.kind === 'heal') { if (G.using) return; startUse(); }
    else if (it.kind === 'utility') grapple();
    else if (it.kind === 'grenade') throwGrenade();
  }
  function fire() {
    const s = G.slots[G.sel], it = selItem();
    if (G.reload) return;
    if (G.t - G.lastShot < (it.auto ? 0.11 : 0.45)) return;
    if (s.mag <= 0) { flashCaption(G.ammo[it.ammo] ? `Empty · press ${glyphText('reload')} to reload` : 'No ammunition left'); G.fireHeld = false; return; }
    G.lastShot = G.t; s.mag--;
    const vm = $('#vm'); if (vm) { vm.classList.add('recoil'); setTimeout(() => vm.classList.remove('recoil'), 60); }
    const xh = $('#xh'); xh.classList.add('kick'); setTimeout(() => xh.classList.remove('kick'), 90);
    const cw = innerWidth / 2;
    const target = G.bots.find(b => b.alive && b.screen && Math.abs(b.screen.x - cw) < Math.max(10, b.screen.r * 0.7) && Math.abs(b.p_d || 999) < V.fov / 2);
    if (target) {
      const dmg = Math.round(it.dmg * (0.85 + Math.random() * 0.3) * (s.id === 'sg4' && target.dist > 45 ? 0.35 : 1));
      target.hp -= dmg; target.flash = 0.08; G.dmgDealt += dmg;
      const hm = $('#hm'); hm.className = 'hitmarker'; void hm.offsetWidth; hm.className = 'hitmarker show' + (target.hp <= 0 ? ' is-elim' : '');
      if (V.dmgNumbers) { const n = $('#dnum'); n.textContent = dmg; clearTimeout(fire.t); fire.t = setTimeout(() => (n.textContent = ''), 500); }
      if (target.hp <= 0) {
        target.alive = false; G.elims++; G.alive--;
        addFeed(`<b>You</b> eliminated ${esc(target.name)} · ${esc(it.name)}`);
        paintStats();
        setTimeout(() => { if (G) G.bots.push({ id: G.bots.length + 100, name: 'Bot ' + BOT_NAMES[(G.bots.length + 7) % BOT_NAMES.length], bearing: G.heading + 60 + Math.random() * 240, dist: 30 + Math.random() * 45, hp: 100, alive: true, flash: 0 }); }, 6000);
        if (G.alive <= 1) setTimeout(() => endMatch('victory'), 900);
      }
    }
    if (s.mag === 0 && G.ammo[it.ammo] > 0) setTimeout(() => G && startReload(), 250);
    paintSlots(); paintAmmo();
  }
  function startReload() {
    const s = G.slots[G.sel], it = selItem();
    if (!it || it.kind !== 'weapon' || G.reload || s.mag >= it.mag) return;
    if (!G.ammo[it.ammo]) { flashCaption(`No ${AMMO[it.ammo].name.toLowerCase()} ammunition`); return; }
    if (G.using) interruptUse('Reloading');
    G.reload = { t0: G.t, dur: it.id === 'sg4' ? 2.2 : 1.6, slot: G.sel };
    paintAmmo();
  }
  function startUse() {
    const s = G.slots[G.sel], it = selItem();
    if (it.pool === 'health' && G.hp >= 100) { toast('warning', 'Health is full'); return; }
    if (it.pool === 'shield' && G.sh >= 100) { toast('warning', 'Shields are full'); return; }
    if (it.pool === 'both' && G.hp >= 100 && G.sh >= 100) { toast('warning', 'Health and shields are full'); return; }
    G.using = { slot: G.sel, id: s.id, t0: G.t, dur: it.time };
    const ring = $('#uring'); ring.hidden = false; ring.classList.toggle('is-health', it.pool === 'health');
    $('#ulabel').hidden = false;
    const glow = $('#hglow'); glow.className = 'heal-glow' + (V.healGlow ? ' on' : '') + (it.pool === 'health' ? ' is-health' : '');
    $('#hstat').textContent = `Using ${it.name}…`;
    $('#hstat').style.color = it.pool === 'health' ? 'var(--success)' : 'var(--shield)';
    const vm = $('#vm'); if (vm) vm.classList.remove('lowered');
  }
  function finishUse() {
    const u = G.using, it = ITEMS[u.id], s = G.slots[u.slot];
    if (it.pool === 'health') G.hp = Math.min(100, G.hp + it.amount);
    else if (it.pool === 'shield') G.sh = Math.min(100, G.sh + it.amount);
    else { G.hp = 100; G.sh = 100; }
    s.qty--; if (s.qty <= 0) G.slots[u.slot] = null;
    G.using = null; endUseUi(true);
    $('#hstat').textContent = `${it.effect} · ${it.name} used`;
    setTimeout(() => { const h = $('#hstat'); if (h && !G?.using) h.textContent = ''; }, 2200);
    paintMeters(); paintSlots(); paintVM();
  }
  function interruptUse(reason) {
    if (!G.using) return;
    const it = ITEMS[G.using.id];
    G.using = null; endUseUi(false);
    const h = $('#hstat'); if (h) { h.textContent = `Interrupted · ${reason}. ${it.name} kept.`; h.style.color = 'var(--warning)'; }
    setTimeout(() => { const h2 = $('#hstat'); if (h2 && G && !G.using) h2.textContent = ''; }, 2400);
  }
  function endUseUi(done) {
    const ring = $('#uring'); if (ring) ring.hidden = true;
    const l = $('#ulabel'); if (l) l.hidden = true;
    const g = $('#hglow'); if (g) { g.className = g.className.replace(' on', '') + (done && V.healGlow ? ' done' : ''); requestAnimationFrame(() => requestAnimationFrame(() => g.classList.remove('done'))); }
  }
  function grapple() {
    const s = G.slots[G.sel];
    if (s.readyAt > G.t) { flashCaption(`Tethercaster recharging · ${Math.ceil(s.readyAt - G.t)}s`); return; }
    if (G.using) interruptUse('Grappled');
    s.readyAt = G.t + ITEMS.tether.cooldown;
    const loc = nearestLoc(G.pos);
    addFeed(`Tethercaster anchored · ${esc(loc.name)} ridge`);
    G.pos.x += Math.sin(G.heading * Math.PI / 180) * 0.03; G.pos.y -= Math.cos(G.heading * Math.PI / 180) * 0.03;
  }
  function throwGrenade() {
    const s = G.slots[G.sel];
    if (G.using) interruptUse('Threw a grenade');
    s.qty--; if (s.qty <= 0) G.slots[G.sel] = null;
    addFeed(`${esc(ITEMS[s.id].name)} thrown`);
    paintSlots(); paintVM();
  }
  function nearestLoc(p) { return LOC.reduce((a, l) => (Math.hypot(l.x - p.x, l.y - p.y) < Math.hypot(a.x - p.x, a.y - p.y) ? l : a)); }
  function flashCaption(msg) { const c = $('#scap'); if (!c) return; c.innerHTML = `<span style="color:var(--warning)">${esc(msg)}</span>`; clearTimeout(flashCaption.t); flashCaption.t = setTimeout(paintSlots, 1600); }

  // ---------------------------------------------------------------- damage
  function takeDamage(bearing, amount, source) {
    if (!G || G.dead) return;
    if (G.using) interruptUse('Took damage');
    const hadShield = G.sh > 0;
    const toShield = Math.min(G.sh, amount); G.sh -= toShield; G.hp = Math.max(0, G.hp - (amount - toShield));
    if (hadShield && G.sh === 0) addFeed('<span style="color:var(--shield)">Shields broken</span>');
    if (state.screen === 'game') {
      showDamageDir(bearing);
      paintMeters();
    }
    if (G.hp <= 0) { G.dead = true; G.killer = source; setTimeout(() => endMatch(source && source.storm ? 'storm' : 'eliminated'), 1100); }
  }
  function showDamageDir(bearing) {
    const rel = ((bearing - G.heading + 540) % 360) - 180;
    if (V.dmgDir) {
      const host = $('#arcs');
      const el = document.createElement('div'); el.className = 'dmg-arc on';
      el.innerHTML = '<svg viewBox="0 0 260 260"><path d="M86 18 A118 118 0 0 1 174 18"/></svg>';
      el.style.transform = `rotate(${rel}deg)`;
      host.appendChild(el);
      const arc = { bearing, el, t: G.t }; G.arcs.push(arc);
      requestAnimationFrame(() => requestAnimationFrame(() => el.classList.remove('on')));
      setTimeout(() => { el.remove(); G && (G.arcs = G.arcs.filter(a => a !== arc)); }, 1400);
    }
    const r = rel * Math.PI / 180, x = 50 + Math.sin(r) * 60, y = 50 - Math.cos(r) * 60;
    const g = $('#dglow');
    g.style.background = `radial-gradient(ellipse 70% 70% at ${x}% ${y}%, rgb(255 121 127 / 0.55), rgb(255 121 127 / 0.15) 40%, transparent 70%)`;
    g.classList.add('on'); requestAnimationFrame(() => requestAnimationFrame(() => g.classList.remove('on')));
  }

  // ---------------------------------------------------------------- loop
  function loop(now) {
    raf = requestAnimationFrame(loop);
    if (!G) return;
    const dt = Math.min(0.05, (now - lastT) / 1000); lastT = now;
    const frozen = G.overlay === 'pause' && state.proto.pauseFreezes || state.screen === 'settings' && state.proto.pauseFreezes;
    if (!frozen && !G.dead) sim(dt);
    if (state.screen === 'game') frame();
  }
  function sim(dt) {
    G.t += dt;
    if (state.screen === 'game' && !G.overlay) {
      const k = G.keys, turnKeys = (k.ArrowRight ? 1 : 0) - (k.ArrowLeft ? 1 : 0);
      if (turnKeys) turn(turnKeys * 110 * dt * Math.max(0.4, V.sens));
      const fwd = (k[V['bind.forward']] ? 1 : 0) - (k[V['bind.backward']] ? 1 : 0), side = (k[V['bind.right']] ? 1 : 0) - (k[V['bind.left']] ? 1 : 0);
      if (fwd || side || G.padMove) {
        const sp = (k[V['bind.sprint']] ? 0.016 : 0.01) * dt, h = G.heading * Math.PI / 180;
        const f = fwd + (G.padMove ? G.padMove.y : 0), s2 = side + (G.padMove ? G.padMove.x : 0);
        G.pos.x = Math.min(0.95, Math.max(0.05, G.pos.x + (Math.sin(h) * f + Math.cos(h) * s2) * sp));
        G.pos.y = Math.min(0.95, Math.max(0.05, G.pos.y + (-Math.cos(h) * f + Math.sin(h) * s2) * sp));
      }
      if (G.fireHeld && selItem() && selItem().auto) fire();
    }
    G.bots.forEach(b => { if (b.flash > 0) b.flash -= dt; });
    if (G.using && G.t - G.using.t0 >= G.using.dur) finishUse();
    if (G.reload && G.t - G.reload.t0 >= G.reload.dur) {
      const s = G.slots[G.reload.slot], it = s && ITEMS[s.id];
      if (it) { const need = it.mag - s.mag, take = Math.min(need, G.ammo[it.ammo]); s.mag += take; G.ammo[it.ammo] -= take; }
      G.reload = null; paintAmmo(); paintSlots();
    }
    // storm phases
    G.stormT -= dt;
    if (G.closing > 0) {
      G.closing -= dt;
      const k = Math.max(0, G.closing / 20);
      G.storm.r = G.safe.r + (G.storm.r0 - G.safe.r) * k;
      G.storm.x = G.safe.x + (G.storm.x0 - G.safe.x) * k; G.storm.y = G.safe.y + (G.storm.y0 - G.safe.y) * k;
      if (G.closing <= 0) { G.phase++; G.stormT = 75; G.safe = { x: G.safe.x + (Math.random() - 0.5) * G.safe.r * 0.6, y: G.safe.y + (Math.random() - 0.5) * G.safe.r * 0.6, r: G.safe.r * 0.55 }; }
    } else if (G.stormT <= 0) {
      G.closing = 20; G.storm.r0 = G.storm.r; G.storm.x0 = G.storm.x; G.storm.y0 = G.storm.y;
      if (state.screen === 'game') toast('warning', 'The ion storm is closing. Move inside the white circle.');
    } else if (G.stormT < 30 && !G.warned30) { G.warned30 = G.phase; if (state.screen === 'game') toast('warning', 'Storm closes in 0:30. Move to the safe zone.'); }
    if (G.warned30 && G.warned30 !== G.phase) G.warned30 = 0;
    const outside = Math.hypot(G.pos.x - G.storm.x, G.pos.y - G.storm.y) > G.storm.r;
    G.inStorm = outside;
    if (outside) { G.stormTick -= dt; if (G.stormTick <= 0) { G.stormTick = 1; G.hp = Math.max(0, G.hp - 2); if (G.using) interruptUse('Storm damage'); paintMeters(); if (G.hp <= 0) { G.dead = true; setTimeout(() => endMatch('storm'), 1100); } } }
    // background eliminations
    G.nextElim -= dt;
    if (G.nextElim <= 0 && G.alive > 2) {
      G.nextElim = 4 + Math.random() * 7; G.alive--;
      const a = BOT_NAMES[Math.floor(Math.random() * BOT_NAMES.length)], b = BOT_NAMES[Math.floor(Math.random() * BOT_NAMES.length)];
      if (a !== b) addFeed(`Bot ${a} eliminated Bot ${b}`); paintStats();
    }
    // bots shoot back
    if (state.proto.botsShoot) {
      G.nextShot -= dt;
      if (G.nextShot <= 0) {
        G.nextShot = 6 + Math.random() * 7;
        const shooters = G.bots.filter(b => b.alive);
        const sh = Math.random() < 0.35 || !shooters.length ? { name: 'Bot ' + BOT_NAMES[Math.floor(Math.random() * 18)], bearing: G.heading + 90 + Math.random() * 180 } : shooters[Math.floor(Math.random() * shooters.length)];
        const burst = 1 + Math.floor(Math.random() * 3);
        for (let i = 0; i < burst; i++) setTimeout(() => G && takeDamage(sh.bearing, 6 + Math.floor(Math.random() * 9), sh), i * 160);
      }
    }
  }
  function frame() {
    if (!G.overlay || G.overlay === 'inventory') Match.draw();
    G.bots.forEach(b => { if (b.screen) b.p_d = ((b.bearing - G.heading + 540) % 360) - 180; });
    G.arcs.forEach(a => (a.el.style.transform = `rotate(${((a.bearing - G.heading + 540) % 360) - 180}deg)`));
    if (G.lastHeading === null || Math.abs(G.lastHeading - G.heading) > 0.3) { G.lastHeading = G.heading; paintCompass(); }
    if (G.using) {
      const it = ITEMS[G.using.id], k = (G.t - G.using.t0) / G.using.dur;
      $('#uring .fill').setAttribute('stroke-dashoffset', 251.3 * (1 - k));
      $('#ulabel').textContent = `${it.name} · ${Math.max(0, G.using.dur - (G.t - G.using.t0)).toFixed(1)}s`;
    }
    if (G.reload) $('#scap').innerHTML = `Reloading… <small>${Math.max(0, G.reload.dur - (G.t - G.reload.t0)).toFixed(1)}s</small>`;
    const now = Math.floor(G.t * 4);
    if (now !== G.lastQ) { G.lastQ = now; paintMini(); paintStorm(); const s = G.slots[2]; if (G.slots.some(x => x && x.id === 'tether' && x.readyAt > G.t - 0.3)) paintSlots(); }
    $('#lowhp').classList.toggle('on', V.lowHealth && G.hp > 0 && G.hp <= 25);
    $('#sedge').classList.toggle('on', !!G.inStorm);
    $('#hud').style.visibility = G.overlay ? 'hidden' : '';
    $('#vmwrap').style.visibility = G.overlay ? 'hidden' : '';
  }

  // ---------------------------------------------------------------- paint
  function paintAll() { paintCompass(); paintStats(); paintMeters(); paintSlots(); paintAmmo(); paintVM(); paintFeed(); paintMini(); paintStorm(); paintHudPrompts(); }
  function paintMeters() {
    if (!$('#mtsh')) return;
    $('#mtsh').innerHTML = Orbit.meterSegments(G.sh); $('#mthp').innerHTML = Orbit.meterSegments(G.hp);
    $('#vsh').textContent = Math.round(G.sh); $('#vhp').textContent = Math.round(G.hp);
    $('#vhp').classList.toggle('is-low', G.hp <= 25);
  }
  function paintStats() { if (!$('#surv')) return; $('#surv').textContent = G.alive; $('#elims').textContent = G.elims; }
  function paintFeed() { const f = $('#feed'); if (!f) return; f.style.display = V.feed ? '' : 'none'; f.innerHTML = G.feed.filter(x => G.t - x.t < 8).map(x => `<div>${x.html}</div>`).join(''); }
  setInterval(() => G && state.screen === 'game' && paintFeed(), 1000);
  function paintSlots() {
    const el = $('#slots'); if (!el) return;
    el.innerHTML = [0, 1, 2, 3, 4].map(i => slotHtml(i, { selected: i === G.sel }) + (i === 1 ? '<span class="or-inventory__sep"></span>' : '')).join('');
    const s = G.slots[G.sel], it = s && ITEMS[s.id];
    $('#scap').innerHTML = s ? `${esc(it.name)}<small>${it.kind === 'heal' ? `${s.qty} · ${esc(it.effect)} · ${it.time}s` : it.kind === 'grenade' ? `${s.qty}/${it.cap}` : it.kind === 'utility' ? (s.readyAt > G.t ? `Recharging ${Math.ceil(s.readyAt - G.t)}s` : 'Ready') : ''}</small>` : `<small style="margin:0">Empty slot ${G.sel + 1}</small>`;
  }
  function paintAmmo() {
    const el = $('#ammo'); if (!el) return;
    const s = G.slots[G.sel], it = s && ITEMS[s.id];
    if (it && it.kind === 'weapon') {
      el.innerHTML = `<div class="or-hud"><div class="or-ammo ${s.mag <= it.mag * 0.25 ? 'is-low' : ''}"><span class="or-ammo__mag">${s.mag}</span><span class="or-ammo__reserve">/ ${G.ammo[it.ammo]}</span></div><span class="or-eyebrow">${esc(it.name)}</span>${s.mag <= it.mag * 0.25 && !G.reload ? `<span class="or-prompt" style="color:var(--warning)">${glyph('reload', 'or-keycap--sm')}Reload</span>` : ''}</div>`;
    } else if (it) el.innerHTML = `<div class="or-hud"><span class="or-eyebrow">${esc(it.name)}</span><span class="or-prompt">${glyph('fire', 'or-keycap--sm')}${it.kind === 'heal' ? (V.healMode === 'Hold' ? 'Hold to use' : 'Use') : it.kind === 'utility' ? 'Fire tether' : 'Throw'}</span></div>`;
    else el.innerHTML = '';
  }
  function paintVM() { const w = $('#vmwrap'); if (w) w.innerHTML = vmFor(); }
  function paintHudPrompts() { const p = $('#hprompts'); if (p) p.innerHTML = `<span class="or-prompt">${glyph('inventory', 'or-keycap--sm')}Inventory</span><span class="or-prompt">${glyph('map', 'or-keycap--sm')}Map</span>`; }
  function paintCompass() {
    const strip = $('#cstrip'); if (!strip) return;
    const w = strip.parentElement.clientWidth, ppd = w / 150, h = G.heading;
    const card = { 0: 'N', 45: 'NE', 90: 'E', 135: 'SE', 180: 'S', 225: 'SW', 270: 'W', 315: 'NW' };
    let html = '';
    for (let d = Math.ceil((h - 80) / 15) * 15; d <= h + 80; d += 15) {
      const n = (d + 360) % 360, x = w / 2 + (d - h) * ppd;
      html += `<span class="${card[n] ? 'card' : ''}" style="left:${x}px">${card[n] || n}</span>`;
    }
    if (G.marker) { const b = Math.atan2(G.marker.x - G.pos.x, -(G.marker.y - G.pos.y)) * 180 / Math.PI; const rel = ((b - h + 540) % 360) - 180; if (Math.abs(rel) < 75) html += `<span class="mk" style="left:${w / 2 + rel * ppd}px">▼</span>`; }
    strip.innerHTML = html;
    $('#cbear').textContent = V.bearing ? `${Math.round(h) % 360}°` : '';
  }
  function paintMini() {
    const c = $('#mini'); if (!c || !G) return;
    Ringfall.drawMap(c, { cx: G.pos.x, cy: G.pos.y, zoom: 3.2 }, { storm: G.storm, safe: G.safe, player: { x: G.pos.x, y: G.pos.y, heading: G.heading }, marker: G.marker }, { noLabels: true });
  }
  function paintStorm() {
    const el = $('#stormline'); if (!el) return;
    const txt = G.closing > 0 ? `Storm closing · ${fmtTime(G.closing)}` : `Storm closes in ${fmtTime(G.stormT)}`;
    el.className = 'storm-line' + (G.closing > 0 || G.stormT < 30 ? ' is-urgent' : '');
    el.innerHTML = `${Orbit.icon('storm')}${txt}${G.inStorm ? ' · <span style="color:var(--danger)">In storm</span>' : ''}`;
  }

  // ---------------------------------------------------------------- INVENTORY overlay
  const INV = { focus: 'slots', i: 0, gi: 0, mode: null };
  function previewPickup(g) {
    const it = ITEMS[g.id];
    if (it.kind === 'weapon') { const e = [0, 1].find(i => !G.slots[i]); return e != null ? { text: `Goes to slot ${e + 1}` } : { text: 'Both weapon slots full · choose one to replace', warn: true }; }
    const space = it.cap - carried(g.id);
    if (space <= 0) return { text: `Carrying ${it.cap}/${it.cap} · full`, warn: true, full: true };
    const stack = G.slots.findIndex((s, i) => i >= 2 && s && s.id === g.id && s.qty < it.stack);
    const empty = [2, 3, 4].find(i => !G.slots[i]);
    const take = Math.min(g.qty, space);
    const left = g.qty - take ? ` · ${g.qty - take} stays on the ground (carry limit ${it.cap})` : '';
    if (stack >= 0) return { text: `Adds to slot ${stack + 1} (${G.slots[stack].qty} → ${Math.min(it.stack, G.slots[stack].qty + take)})${left}` };
    if (empty != null) return { text: `Goes to slot ${empty + 1}${left}` };
    return { text: 'No free item slot · choose one to replace', warn: true };
  }
  function pickup(gi) {
    const g = G.ground[gi], it = ITEMS[g.id];
    if (it.kind === 'weapon') {
      const e = [0, 1].find(i => !G.slots[i]);
      if (e == null) { INV.mode = 'replace'; INV.replaceGi = gi; INV.focus = 'slots'; INV.i = 0; return renderInv(); }
      G.slots[e] = { id: g.id, qty: 1, mag: g.mag || 0 }; G.ground.splice(gi, 1); toast('success', `Picked up ${it.name} · slot ${e + 1}`);
      return renderInv();
    }
    let space = it.cap - carried(g.id);
    if (space <= 0) { toast('warning', `${it.name} ${it.cap}/${it.cap} · full. You can't carry more.`); INV.flash = g.id; return renderInv(); }
    let take = Math.min(g.qty, space), placed = 0;
    for (let i = 2; i < 5 && take > 0; i++) { const s = G.slots[i]; if (s && s.id === g.id) { const add = Math.min(take, it.stack - s.qty); s.qty += add; take -= add; placed += add; } }
    for (let i = 2; i < 5 && take > 0; i++) if (!G.slots[i]) { const add = Math.min(take, it.stack); G.slots[i] = { id: g.id, qty: add, readyAt: 0 }; take -= add; placed += add; }
    if (!placed) { INV.mode = 'replace'; INV.replaceGi = gi; INV.focus = 'slots'; INV.i = 2; return renderInv(); }
    g.qty -= placed; if (g.qty <= 0) G.ground.splice(gi, 1);
    toast('success', `Picked up ${placed} ${it.name}${g.qty > 0 ? ` · ${g.qty} left on the ground (carry limit ${it.cap})` : ''}`);
    renderInv();
  }
  function replaceSlot(i) {
    const g = G.ground[INV.replaceGi], it = ITEMS[g.id];
    if (!eligible(g.id, i)) { toast('warning', it.kind === 'weapon' ? 'Weapons go in slot 1 or 2' : 'Items go in slots 3 to 5'); return; }
    const old = G.slots[i];
    G.slots[i] = null;
    if (old) G.ground.push(Object.assign({}, old));
    const space = it.cap - carried(g.id), take = it.kind === 'weapon' ? 1 : Math.min(g.qty, space, it.stack);
    G.slots[i] = { id: g.id, qty: take, mag: g.mag, readyAt: 0 };
    g.qty -= take; if (g.qty <= 0) G.ground.splice(G.ground.indexOf(g), 1);
    toast('success', `${it.name} in slot ${i + 1}${old ? ` · dropped ${ITEMS[old.id].name}` : ''}`);
    INV.mode = null; renderInv(); paintAll();
  }
  async function dropSlot(i) {
    const s = G.slots[i]; if (!s) return;
    if (V.confirmDrop && !(await confirmDialog({ title: `Drop ${ITEMS[s.id].name}?`, body: 'It stays on the ground nearby, where anyone can pick it up.', ok: 'Drop' }))) return;
    if (G.using && G.using.slot === i) interruptUse('Dropped the item');
    G.ground.unshift(Object.assign({}, s)); G.slots[i] = null;
    toast('success', `Dropped ${ITEMS[s.id].name}`); renderInv(); paintAll();
  }
  function splitSlot(i) {
    const s = G.slots[i]; if (!s || s.qty < 2) { toast('warning', 'Only stacks of 2 or more can be split'); return; }
    const e = [2, 3, 4].find(j => !G.slots[j]);
    if (e == null) { toast('warning', 'Splitting needs an empty item slot'); return; }
    const n = Math.floor(s.qty / 2); s.qty -= n; G.slots[e] = { id: s.id, qty: n };
    toast('success', `Split ${ITEMS[s.id].name}: ${s.qty} in slot ${i + 1}, ${n} in slot ${e + 1}`); renderInv(); paintAll();
  }
  function moveTo(j) {
    const i = INV.moveFrom, a = G.slots[i], b = G.slots[j];
    if ((a && !eligible(a.id, j)) || (b && !eligible(b.id, i))) { toast('warning', 'Weapons stay in slots 1–2 and items in 3–5'); return; }
    G.slots[i] = b; G.slots[j] = a; if (G.sel === i) G.sel = j; else if (G.sel === j) G.sel = i;
    INV.mode = null; INV.i = j; renderInv(); paintAll();
  }
  function invPrimary() {
    if (INV.focus === 'ground') { if (G.ground[INV.gi]) pickup(INV.gi); return; }
    const i = INV.i;
    if (INV.mode === 'replace') return replaceSlot(i);
    if (INV.mode === 'move') return moveTo(i);
    const s = G.slots[i]; if (!s) return;
    const it = ITEMS[s.id];
    selectSlot(i); Match.close();
    if (it.kind === 'heal') startUse();
  }
  function renderInv() {
    const ov = $('#ov-inventory'); if (!ov || G.overlay !== 'inventory') return;
    const i = INV.i, s = G.slots[i], it = s && ITEMS[s.id];
    const rep = INV.mode === 'replace' && G.ground[INV.replaceGi];
    const slotCols = [0, 1, 2, 3, 4].map(k => {
      const sk = G.slots[k];
      const extra = [];
      if (INV.focus === 'slots' && k === i) extra.push('');
      if (rep) extra.push(eligible(rep.id, k) ? 'is-target' : 'is-ineligible');
      if (INV.mode === 'move' && k === INV.moveFrom) extra.push('is-target');
      if (INV.flash && sk && sk.id === INV.flash) extra.push('is-full');
      return `<div style="display:flex;flex-direction:column;align-items:center;gap:8px">${slotHtml(k, { selected: INV.focus === 'slots' && k === i, extra: extra.filter(Boolean).join(' ') })}<span class="slot-name ${k === i ? 'is-sel' : ''}">${sk ? esc(ITEMS[sk.id].name.split(' ')[0] === 'Fragmentation' ? 'Frag grenade' : ITEMS[sk.id].name) : k < 2 ? 'Weapon' : 'Item'}</span></div>${k === 1 ? '<span class="or-inventory__sep"></span>' : ''}`;
    }).join('');
    INV.flash = null;
    let card;
    if (!s) card = `<div class="art">${k2(i)}</div><div><h3>Empty slot ${i + 1}</h3><p class="note">${i < 2 ? 'Slots 1 and 2 hold weapons only.' : 'Slots 3 to 5 hold healing, grenades and the Tethercaster.'}</p></div>`;
    else {
      const rows = [['Type', it.kind === 'heal' ? 'Healing' : it.kind === 'weapon' ? 'Weapon' : it.kind === 'grenade' ? 'Grenade' : 'Utility']];
      if (it.kind === 'weapon') rows.push(['Magazine', `${s.mag} / ${it.mag}`], ['Reserve', `${G.ammo[it.ammo]} ${AMMO[it.ammo].name.toLowerCase()}`]);
      else { rows.push(['Effect', it.effect]); if (it.stack > 1 || it.kind === 'heal') rows.push(['In this slot', `${s.qty} / ${it.stack} per stack`], ['Carrying', `${carried(s.id)} / ${it.cap} total`]); if (it.time) rows.push(['Use time', `${it.time} s · walk slowly while using`]); if (it.cooldown) rows.push(['Recharge', `${it.cooldown} s`]); }
      card = `<div class="art ${it.tint ? 'ico-' + it.tint : ''}">${ico(it.icon, '')}</div><div><h3>${esc(it.name)}</h3><div class="note">${esc(it.role || (it.kind === 'heal' ? 'Interrupted by damage, firing or grappling; the item is kept.' : ''))}</div><dl>${rows.map(([a, b]) => `<dt>${a}</dt><dd>${esc(b)}</dd>`).join('')}</dl></div>
        <div class="actions"><button class="or-btn or-btn--primary" data-ia="use">${glyph('confirm', 'or-keycap--sm')}${it.kind === 'heal' ? 'Use' : 'Equip'}</button><button class="or-btn" data-ia="move">${glyph('move', 'or-keycap--sm')}Move</button>${s.qty > 1 ? `<button class="or-btn" data-ia="split">${glyph('split', 'or-keycap--sm')}Split stack</button>` : ''}<button class="or-btn or-btn--danger" data-ia="drop">${glyph('drop', 'or-keycap--sm')}Drop</button></div>`;
    }
    const modeBar = rep ? `<div class="replace-bar" role="status"><strong style="color:var(--warning)">Replace with ${esc(ITEMS[rep.id].name)}</strong><span class="note">Choose ${ITEMS[rep.id].kind === 'weapon' ? 'slot 1 or 2' : 'a slot from 3 to 5'}. ${G.slots[i] && eligible(rep.id, i) ? `Drops ${esc(ITEMS[G.slots[i].id].name)}.` : ''}</span><button class="or-btn or-btn--ghost" style="height:36px;font-size:16px" data-ia="cancel">${glyph('back', 'or-keycap--sm')}Cancel</button></div>`
      : INV.mode === 'move' ? `<div class="replace-bar" role="status"><strong style="color:var(--warning)">Moving ${esc(ITEMS[G.slots[INV.moveFrom].id].name)}</strong><span class="note">Choose a slot to swap with, then ${esc(glyphText('confirm'))}.</span><button class="or-btn or-btn--ghost" style="height:36px;font-size:16px" data-ia="cancel">${glyph('back', 'or-keycap--sm')}Cancel</button></div>` : '';
    ov.innerHTML = `<div class="inv"><div class="pad scale-root">
      <div class="settings-head"><div><div class="or-eyebrow">${G.alive} alive · storm ${G.closing > 0 ? 'closing' : 'in ' + fmtTime(G.stormT)} · match continues</div><h1 class="settings-title" style="margin-bottom:0">Inventory</h1></div>${prompt('back', 'Close')}</div>
      <div class="inv-grid">
        <div class="inv-left">
          <div><div class="or-inventory" style="gap:8px">${slotCols}</div></div>
          ${modeBar}
          <div class="item-card">${card}</div>
          <div><div class="or-eyebrow" style="margin-bottom:8px">Ammunition · carried separately, not in slots</div><div class="ammo-row">${Object.entries(AMMO).map(([k, a]) => `<div><small>${a.name}</small><strong>${G.ammo[k]}<span> / ${a.cap}</span></strong></div>`).join('')}</div></div>
        </div>
        <div class="nearby"><div class="or-eyebrow" style="margin-bottom:8px">On the ground · within reach</div>
          <div class="nearby-list">${G.ground.length ? G.ground.map((g, k) => { const gi = ITEMS[g.id], pv = previewPickup(g); return `<button class="nearby-item ${INV.focus === 'ground' && k === INV.gi ? 'is-current' : ''}" data-g="${k}"><span class="${gi.tint ? 'ico-' + gi.tint : ''}">${ico(gi.icon, '')}</span><span><span class="nm">${esc(gi.name)}</span><span class="pv ${pv.warn ? 'is-warn' : ''}">${esc(pv.text)}</span></span><span class="qty">${gi.kind === 'weapon' ? '' : '×' + g.qty}</span></button>`; }).join('') : '<p class="note" style="padding:16px">Nothing nearby.</p>'}</div>
        </div>
      </div>
      <div class="prompts" style="margin-top:24px">${prompt('adjust', 'Select slot')}${prompt('nav', 'Slots / ground')}${prompt('confirm', INV.focus === 'ground' ? 'Pick up' : INV.mode ? 'Place here' : 'Use or equip')}${prompt('back', INV.mode ? 'Cancel' : 'Close')}</div>
    </div></div>`;
    $$('[data-slot]', ov).forEach(b => (b.onclick = () => { INV.focus = 'slots'; if (INV.i === +b.dataset.slot && !INV.mode) return renderInv(); INV.i = +b.dataset.slot; if (INV.mode === 'replace') replaceSlot(INV.i); else if (INV.mode === 'move') moveTo(INV.i); else renderInv(); }));
    $$('[data-g]', ov).forEach(b => (b.onclick = () => { INV.focus = 'ground'; INV.gi = +b.dataset.g; pickup(INV.gi); }));
    $$('[data-ia]', ov).forEach(b => (b.onclick = () => ({ use: invPrimary, move: () => { INV.mode = 'move'; INV.moveFrom = INV.i; renderInv(); }, split: () => splitSlot(INV.i), drop: () => dropSlot(INV.i), cancel: () => { INV.mode = null; renderInv(); } })[b.dataset.ia]()));
    bindActs(ov, { back: () => invKey('back'), confirm: invPrimary });
  }
  const k2 = i => `<span class="note" style="font-size:28px">${i + 1}</span>`;
  function invKey(a) {
    if (a === 'back') { if (INV.mode) { INV.mode = null; renderInv(); } else Match.close(); return; }
    if (INV.focus === 'slots') {
      if (a === 'left') INV.i = (INV.i + 4) % 5;
      else if (a === 'right') INV.i = (INV.i + 1) % 5;
      else if (a === 'down' && G.ground.length && !INV.mode) { INV.focus = 'ground'; INV.gi = Math.min(INV.gi, G.ground.length - 1); }
      else if (a === 'confirm') return invPrimary();
      else if (a === 'drop' && !INV.mode) return dropSlot(INV.i);
      else if (a === 'split' && !INV.mode) return splitSlot(INV.i);
      else if (a === 'move' && G.slots[INV.i] && !INV.mode) { INV.mode = 'move'; INV.moveFrom = INV.i; }
    } else {
      if (a === 'up') { if (INV.gi === 0) INV.focus = 'slots'; else INV.gi--; }
      else if (a === 'down') INV.gi = Math.min(G.ground.length - 1, INV.gi + 1);
      else if (a === 'left' || a === 'right') INV.focus = 'slots';
      else if (a === 'confirm') return pickup(INV.gi);
    }
    renderInv();
  }

  // ---------------------------------------------------------------- MAP overlay
  const MAPV = { cx: 0.5, cy: 0.5, zoom: 0.95 };
  function renderMap() {
    const ov = $('#ov-map');
    ov.innerHTML = `<div class="map-wrap"><div class="map"><canvas id="bigmap" aria-label="Ringfall map"></canvas><div class="zoom-label" id="zl"></div><div class="map-prompts prompts"><span class="prompt">Click · Place marker</span><span class="prompt">Right-click · Remove marker</span><span class="prompt">Wheel · Zoom</span><span class="prompt">Drag · Pan</span></div></div>
      <aside class="side"><div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px"><div><div class="or-eyebrow">Alive</div><div class="big-num" id="m-alive"></div></div><div class="prompts" style="flex-direction:column;align-items:flex-end;gap:8px">${prompt('map', 'Close map')}${prompt('back', 'Back to match')}</div></div>
      <div><div class="or-eyebrow" id="m-phase"></div><div class="big-num" id="m-storm" style="display:flex;align-items:center;gap:12px"></div></div>
      <div class="legend"><div><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="var(--text-primary)" stroke-width="2"/></svg><span>Next safe zone</span><em></em></div>
        <div><svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" fill="rgb(169 139 255 / .4)" stroke="var(--storm)" stroke-width="2"/></svg><span>Ion storm</span><em></em></div>
        <div><svg viewBox="0 0 24 24"><path d="M12 3l7 17-7-4-7 4z" fill="var(--text-primary)"/></svg><span>You</span><em id="m-you"></em></div>
        <div><svg viewBox="0 0 24 24"><path d="M12 22s-7-7-7-12a7 7 0 0 1 14 0c0 5-7 12-7 12z" fill="var(--accent)"/></svg><span>Your marker</span><em id="m-mk"></em></div></div>
      <p class="note">${glyphText('confirm')} places a marker at the center · ${glyphText('alt')} removes it · ${glyphText('prevCat')}/${glyphText('nextCat')} zoom · arrows pan.</p></aside></div>`;
    const c = $('#bigmap');
    let drag = null;
    const toMap = e => { const b = c.getBoundingClientRect(), g = MAPV.geo; return { x: (e.clientX - b.left - g.ox) / g.size, y: (e.clientY - b.top - g.oy) / g.size }; };
    c.onwheel = e => { e.preventDefault(); MAPV.zoom = Math.max(0.9, Math.min(3, MAPV.zoom * (e.deltaY > 0 ? 0.88 : 1.14))); paintMap(); };
    c.onmousedown = e => { drag = { x: e.clientX, y: e.clientY, cx: MAPV.cx, cy: MAPV.cy, moved: false, b: e.button }; };
    c.onmousemove = e => { if (!drag) return; const dx = e.clientX - drag.x, dy = e.clientY - drag.y; if (Math.hypot(dx, dy) > 4) drag.moved = true; if (drag.moved) { MAPV.cx = drag.cx - dx / MAPV.geo.size; MAPV.cy = drag.cy - dy / MAPV.geo.size; paintMap(); } };
    c.onmouseup = e => { if (drag && !drag.moved) { if (e.button === 2) G.marker = null; else G.marker = toMap(e); paintMap(); } drag = null; };
    c.oncontextmenu = e => e.preventDefault();
    bindActs(ov, { map: () => Match.close(), back: () => Match.close() });
    paintMap();
  }
  function paintMap() {
    const c = $('#bigmap'); if (!c) return;
    MAPV.geo = Ringfall.drawMap(c, MAPV, { storm: G.storm, safe: G.safe, player: { x: G.pos.x, y: G.pos.y, heading: G.heading }, marker: G.marker });
    $('#zl').textContent = `Zoom ${MAPV.zoom.toFixed(1)}x`;
    $('#m-alive').textContent = G.alive;
    $('#m-phase').textContent = `Storm phase ${G.phase} · ${G.closing > 0 ? 'closing' : 'closes in'}`;
    $('#m-storm').innerHTML = `${Orbit.icon('storm')}${fmtTime(G.closing > 0 ? G.closing : G.stormT)}`;
    $('#m-storm svg').style.cssText = 'width:36px;height:36px;color:var(--storm)';
    $('#m-you').textContent = `Near ${nearestLoc(G.pos).name}`;
    $('#m-mk').textContent = G.marker ? `Near ${nearestLoc(G.marker).name}` : 'None';
  }
  function mapKey(a) {
    const step = 0.06 / MAPV.zoom;
    if (a === 'back' || a === 'map') return Match.close();
    if (a === 'left') MAPV.cx -= step; else if (a === 'right') MAPV.cx += step; else if (a === 'up') MAPV.cy -= step; else if (a === 'down') MAPV.cy += step;
    else if (a === 'confirm') G.marker = { x: MAPV.cx, y: MAPV.cy };
    else if (a === 'alt') G.marker = null;
    else if (a === 'prevCat') MAPV.zoom = Math.max(0.9, MAPV.zoom / 1.2); else if (a === 'nextCat') MAPV.zoom = Math.min(3, MAPV.zoom * 1.2);
    paintMap();
  }
  setInterval(() => { if (G && G.overlay === 'map') paintMap(); if (G && G.overlay === 'inventory') { const e = $('.inv .or-eyebrow'); if (e) e.textContent = `${G.alive} alive · storm ${G.closing > 0 ? 'closing' : 'in ' + fmtTime(G.stormT)} · match continues`; } }, 500);

  // ---------------------------------------------------------------- PAUSE overlay
  const PAUSE = { i: 0 };
  function renderPause() {
    const ov = $('#ov-pause');
    const freeze = state.proto.pauseFreezes;
    ov.innerHTML = `<div class="pause left-fade"><div class="pad scale-root" style="position:relative">
      <div class="or-eyebrow eyebrow-rule">Solo · Ringfall</div>
      <h1 class="settings-title" style="margin-bottom:8px">Menu</h1>
      <div class="chip ${freeze ? '' : 'chip--warning'}"><span class="status-dot" style="background:${freeze ? 'var(--success)' : 'var(--warning)'}"></span>${freeze ? 'Match paused · solo mode only' : 'Match continues · bots keep playing'}</div>
      <div class="pause-menu" role="menu">
        <button class="menu-item" role="menuitem" data-pi="0">Resume</button>
        <button class="menu-item" role="menuitem" data-pi="1">Settings</button>
        <div class="menu-sep"></div>
        <button class="menu-item menu-item--danger" role="menuitem" data-pi="2">Leave match</button>
      </div>
      <div class="prompts" style="margin-top:auto">${prompt('back', 'Resume')}${prompt('nav', 'Select')}${prompt('confirm', 'Open')}</div></div></div>`;
    $$('[data-pi]', ov).forEach(b => { b.onclick = () => pauseAct(+b.dataset.pi); b.onmouseenter = () => { PAUSE.i = +b.dataset.pi; markPause(); }; });
    bindActs(ov, { back: () => Match.close(), confirm: () => pauseAct(PAUSE.i) });
    markPause();
  }
  function markPause() { $$('[data-pi]').forEach(b => b.classList.toggle('is-current', +b.dataset.pi === PAUSE.i)); const b = $(`[data-pi="${PAUSE.i}"]`); if (b) b.focus({ preventScroll: true }); }
  async function pauseAct(i) {
    if (i === 0) Match.close();
    else if (i === 1) go('settings', { cat: 'mk' });
    else if (await confirmDialog({ title: 'Leave match?', body: `You'll be out of this match and placed ${G.alive}th of 60. Bots keep playing without you.`, ok: 'Leave match', cancel: 'Stay' })) endMatch('left');
  }

  // ---------------------------------------------------------------- results
  function endMatch(reason) {
    if (!G) return;
    const r = { reason, placement: reason === 'victory' ? 1 : G.alive, elims: G.elims, dmg: G.dmgDealt, time: G.t, by: G.killer && G.killer.name, weapon: G.killer && !G.killer.storm ? 'AR-7 Wayfarer' : null };
    G.overlay = null;
    go('results', r, { replace: true });
  }
  SCREENS.results = {
    enter(el, r) {
      W.mode = 'vista'; W.offset = 200; W.planetX = 0.6;
      const ord = n => n + (n % 100 >= 11 && n % 100 <= 13 ? 'th' : ['th', 'st', 'nd', 'rd'][n % 10] || 'th');
      const line = { victory: 'Last one standing on Ringfall.', eliminated: `Eliminated by ${r.by || 'a bot'}${r.weapon ? ' · ' + r.weapon : ''}.`, storm: 'The ion storm caught you.', left: 'You left the match.' }[r.reason];
      el.innerHTML = `<div class="scale-root"><div class="pad left-fade">
        <div style="position:relative"><span class="wordmark wordmark--sm"><b>ORBIT</b><span>ROYALE</span></span></div>
        <div class="results-body" style="position:relative">
          <div><div class="or-eyebrow eyebrow-rule" style="${r.reason === 'victory' ? 'color:var(--accent)' : ''}">${r.reason === 'victory' ? 'Victory' : 'Match over'} · Solo · Ringfall</div>
            <div class="placement">${ord(r.placement)}<small>of 60</small></div>
            <p class="body" style="margin:16px 0 0;color:var(--text-secondary)">${esc(line)}</p></div>
          <div><div class="results-stats"><div><small>Placement</small><strong>${ord(r.placement)}</strong></div><div><small>Eliminations</small><strong>${r.elims}</strong></div><div><small>Damage dealt</small><strong>${r.dmg}</strong></div><div><small>Survival time</small><strong>${fmtTime(r.time)}</strong></div></div>
            <div class="results-actions"><button class="or-btn or-btn--primary" data-nav data-act="again">${glyph('confirm', 'or-keycap--sm')} Play again</button><button class="or-btn" data-nav data-act="lobby">Return to lobby</button></div></div>
        </div>
        <div class="prompts" style="position:relative">${prompt('confirm', 'Play again')}${prompt('back', 'Return to lobby')}</div></div></div>`;
      bindActs(el, { again: () => go('deploy'), lobby: () => go('lobby'), confirm: () => go('deploy'), back: () => go('lobby') });
      $('[data-act="again"]', el).focus();
    },
    key(a) {
      const el = $('#s-results');
      if (a === 'left' || a === 'up') OR.moveFocus(el, -1); else if (a === 'right' || a === 'down') OR.moveFocus(el, 1);
      else if (a === 'back') go('lobby'); else if (a === 'confirm' && state.device === 'pad') document.activeElement.click();
    }
  };

  // ---------------------------------------------------------------- public Match API
  const KEYACT = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right', Enter: 'confirm', Escape: 'back' };
  window.Match = {
    draw() {
      if (!G) return;
      Ringfall.firstPerson($('#world'), { heading: G.heading, fov: V.fov, bots: G.bots });
    },
    open(name) {
      if (!G) return;
      if (G.overlay) $('#ov-' + G.overlay).classList.remove('is-open');
      G.overlay = name; G.fireHeld = false; G.openedAt = performance.now();
      wantPause = false; if (document.pointerLockElement) document.exitPointerLock();
      const ov = $('#ov-' + name); ov.classList.add('is-open');
      if (name === 'inventory') { INV.focus = 'slots'; INV.i = G.sel; INV.mode = null; renderInv(); }
      if (name === 'map') { MAPV.cx = G.pos.x; MAPV.cy = G.pos.y; MAPV.zoom = 1.2; renderMap(); }
      if (name === 'pause') { PAUSE.i = 0; renderPause(); }
      paintLockHint();
    },
    close() {
      if (!G || !G.overlay) return;
      $('#ov-' + G.overlay).classList.remove('is-open'); $('#ov-' + G.overlay).innerHTML = '';
      G.overlay = null; paintAll(); requestLock(); setTimeout(paintLockHint, 50);
    },
    keydown(e, k) {
      if (!G) return;
      const a = KEYACT[e.key];
      if (G.overlay) {
        e.preventDefault();
        if (G.overlay === 'inventory') {
          if (k === V['bind.inventory'] && !INV.mode) return Match.close();
          return invKey(a || { X: 'drop', S: 'split', Space: 'move' }[k]);
        }
        if (G.overlay === 'map') return mapKey(k === V['bind.map'] ? 'map' : a || { R: 'alt', Q: 'prevCat', E: 'nextCat', '-': 'prevCat', '=': 'nextCat', '+': 'nextCat' }[k]);
        if (G.overlay === 'pause') {
          if (a === 'back') { if (performance.now() - G.openedAt > 200) Match.close(); return; }
          if (a === 'up' || a === 'down') { const order = [0, 1, 2], j = order.indexOf(PAUSE.i); PAUSE.i = order[(j + (a === 'up' ? 2 : 1)) % 3]; markPause(); }
          if (a === 'confirm') pauseAct(PAUSE.i);
        }
        return;
      }
      if (['Tab', ' ', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) e.preventDefault();
      G.keys[k] = true; G.keys[e.key] = true;
      if (e.key === 'Escape') return Match.open('pause');
      if (G.dead) return;
      for (let i = 1; i <= 5; i++) if (k === V['bind.slot' + i]) return selectSlot(i - 1);
      if (k === V['bind.reload']) return startReload();
      if (k === V['bind.inventory']) return Match.open('inventory');
      if (k === V['bind.map']) return Match.open('map');
      if (k === 'T') return Match.event('random');
    },
    keyup(e, k) { if (G) { G.keys[k] = false; G.keys[e.key] = false; } },
    pad(p, pressed, prev) {
      if (!G) return;
      const edge = i => pressed[i] && !prev[i];
      if (G.overlay) {
        const map = { 0: 'confirm', 1: 'back', 2: G.overlay === 'inventory' ? 'drop' : 'alt', 3: 'split', 4: 'prevCat', 5: G.overlay === 'inventory' ? 'move' : 'nextCat', 12: 'up', 13: 'down', 14: 'left', 15: 'right', 9: 'back', 8: 'back' };
        for (const i in map) if (edge(+i)) { const a = map[i]; if (G.overlay === 'inventory') invKey(a); else if (G.overlay === 'map') mapKey(a); else Match.keydown({ key: { up: 'ArrowUp', down: 'ArrowDown', confirm: 'Enter', back: 'Escape' }[a] || '', preventDefault() {} }, ''); }
        return;
      }
      const dz = v => (Math.abs(v) < V.dzRight / 100 ? 0 : v);
      const rx = dz(p.axes[V.swapSticks ? 0 : 2] || 0);
      if (rx) turn(rx * Math.abs(rx) * 3.2 * V.padLook);
      const lx = p.axes[V.swapSticks ? 2 : 0] || 0, ly = p.axes[V.swapSticks ? 3 : 1] || 0;
      G.padMove = Math.hypot(lx, ly) > V.dzLeft / 100 ? { x: lx, y: -ly } : null;
      const rt = p.buttons[7] && p.buttons[7].value > 0.4;
      if (rt && !G.fireHeld) { G.fireHeld = true; primary(); } else if (!rt && G.fireHeld) { G.fireHeld = false; if (G.using && V.healMode === 'Hold') interruptUse('Released before finishing'); }
      if (edge(4)) selectSlot((G.sel + 4) % 5); if (edge(5)) selectSlot((G.sel + 1) % 5);
      if (edge(2)) startReload();
      if (edge(8)) Match.open('inventory'); if (edge(12)) Match.open('map'); if (edge(9)) Match.open('pause');
    },
    event(ev) {
      if (!G) return;
      const rel = { front: 0, left: -90, right: 90, behind: 180 }[ev];
      if (rel !== undefined) takeDamage(G.heading + rel, 22, { name: 'Bot Rhea' });
      else if (ev === 'random') takeDamage(Math.random() * 360, 15 + Math.floor(Math.random() * 15), { name: 'Bot ' + BOT_NAMES[Math.floor(Math.random() * 18)] });
      else if (ev === 'storm') { G.stormT = 31; G.warned30 = 0; }
      else if (ev === 'shrink') { G.stormT = 0.1; }
      else if (ev === 'lowhp') { G.sh = 0; G.hp = 18; paintMeters(); }
      else if (ev === 'heal') { G.hp = 100; G.sh = 100; paintMeters(); }
      else if (ev === 'die') takeDamage(G.heading + 150, 400, { name: 'Bot Rhea' });
      else if (ev === 'win') { G.alive = 1; endMatch('victory'); }
      else if (ev === 'refill') { G.ground.push({ id: 'shieldPack', qty: 2 }, { id: 'frag', qty: 3 }, { id: 'fieldPatch', qty: 6 }); toast('success', 'Loot added nearby'); renderInv(); }
    }
  };
})();
