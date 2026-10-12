// Orbit Royale Asset Hub: production tracker + model/audio/image inspection.
// Records live in the artifact's db (collection "assets"); preview files live in its asset store.
import { createViewer } from './viewer.js';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const STAGES = ['Not started', 'Concept', 'Draft', 'Production', 'Review', 'In engine', 'Done'];
const STAGE_CLASS = s => 'st-' + STAGES.indexOf(s);
const MILESTONES = ['Foundations', 'Traversal', 'Combat and inventory', 'Visual slice', 'Match loop', 'Equipment and rotation', 'Full local match'];
const SECTIONS = [
  { id: 'all', name: 'All' },
  { id: 'characters', name: 'Characters', cats: ['Characters'] },
  { id: 'weapons', name: 'Weapons', cats: ['Weapons'] },
  { id: 'items', name: 'Items', cats: ['Healing items', 'Grenades', 'Utility', 'Pickups'] },
  { id: 'vehicles', name: 'Vehicles', cats: ['Vehicles'] },
  { id: 'transport', name: 'Drop transport', cats: ['Drop transport'] },
  { id: 'world', name: 'World', cats: ['Environment', 'Locations'] },
  { id: 'vfx', name: 'VFX', cats: ['VFX'] },
  { id: 'ui', name: 'Brand & UI', cats: ['Brand and UI'] },
  { id: 'audio', name: 'Audio', kind: 'audio' }
];
const KIND_LABEL = { model: '3D model', animation: 'Animation', audio: 'Audio', vfx: 'Visual effect', ui: 'UI / brand', art: 'Artwork' };
const VIEW_KIND = k => (k === 'audio' ? 'audio' : k === 'ui' || k === 'art' ? 'image' : 'model');
const MAX_BYTES = 20 * 1024 * 1024;
const fmtBytes = b => (b > 1048576 ? (b / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(b / 1024)) + ' KB');
const fmtDate = iso => { try { return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }); } catch (e) { return ''; } };

const S = {
  assets: [], sel: null, section: 'all', q: '', stage: '', milestone: '', decisions: false,
  db: null, user: null, store: null, me: null, canWrite: false, status: 'loading',
  loadedFor: undefined, local: null, names: {}
};
try { const r = JSON.parse(localStorage.getItem('orbit.hub') || '{}'); Object.assign(S, { section: r.section || 'all', sel: r.sel || null }); } catch (e) { /* storage unavailable */ }
const remember = () => { try { localStorage.setItem('orbit.hub', JSON.stringify({ section: S.section, sel: S.sel })); } catch (e) { /* ignore */ } };

// ---------------------------------------------------------------- data access
const inSection = (a, sec) => sec.id === 'all' || (sec.kind ? a.kind === sec.kind : sec.cats.includes(a.category));
const progress = a => { const p = a.parts || []; return p.length ? p.filter(x => x.done).length / p.length : a.stage === 'Done' ? 1 : 0; };
function filtered() {
  const sec = SECTIONS.find(s => s.id === S.section) || SECTIONS[0], q = S.q.trim().toLowerCase();
  return S.assets.filter(a => inSection(a, sec)
    && (!q || [a.name, a.category, a.group, a.path, a.notes].join(' ').toLowerCase().includes(q))
    && (!S.stage || a.stage === S.stage) && (!S.milestone || a.milestone === S.milestone) && (!S.decisions || a.decision));
}
const current = () => S.assets.find(a => a.id === S.sel);
async function save(id, patch) {
  if (!S.db || !S.canWrite) return false;
  try {
    await S.db.collection('assets').doc(id).update(Object.assign({}, patch, { updatedAt: new Date().toISOString(), updatedBy: S.me || null }));
    return true;
  } catch (e) {
    if (e && e.code === 'invalid_argument') { S.canWrite = false; render(); toast('warning', 'You can view this hub but not change it. Ask the owner for Contributor access.'); }
    else toast('danger', 'Could not save. Check your connection and try again.');
    return false;
  }
}

// ---------------------------------------------------------------- shell
const app = $('#hub');
app.innerHTML = `
  <header class="top">
    <div class="brand"><span class="wordmark"><b>ORBIT</b><span>ROYALE</span></span><h1>Asset Hub</h1></div>
    <div class="summary" id="summary"></div>
    <div class="top-actions"><button class="or-btn" id="add-btn" hidden>Add asset</button></div>
  </header>
  <nav class="or-tabs sections" role="tablist" id="sections" aria-label="Asset sections"></nav>
  <div class="toolbar">
    <label class="search"><span class="sr-only">Search assets</span><input id="q" type="search" placeholder="Search names, paths, notes" autocomplete="off"></label>
    <select class="or-select" id="f-stage" aria-label="Filter by stage"><option value="">Every stage</option>${STAGES.map(s => `<option>${s}</option>`).join('')}</select>
    <select class="or-select" id="f-ms" aria-label="Filter by milestone"><option value="">Every milestone</option>${MILESTONES.map(s => `<option>${s}</option>`).join('')}</select>
    <label class="check"><input type="checkbox" id="f-dec"> Needs a decision</label>
  </div>
  <main class="body">
    <section class="list" id="list" aria-label="Assets"></section>
    <section class="detail" aria-label="Asset detail">
      <div class="stage-area" id="stage-area">
        <div class="vhost" id="vhost"></div>
        <div class="audio-panel" id="audio-panel" hidden></div>
        <div class="image-panel" id="image-panel" hidden></div>
        <div class="drop-empty" id="empty"></div>
        <div class="drop-hint" id="drop-hint" hidden>Drop to preview</div>
      </div>
      <div class="vtools" id="vtools"></div>
      <div class="info" id="info"></div>
    </section>
  </main>
  <input type="file" id="file" hidden>
  <div class="dock" id="toasts" aria-live="polite"></div>
  <div class="layer" id="layer"></div>`;

$('#q').oninput = e => { S.q = e.target.value; renderList(); };
$('#f-stage').onchange = e => { S.stage = e.target.value; renderList(); };
$('#f-ms').onchange = e => { S.milestone = e.target.value; renderList(); };
$('#f-dec').onchange = e => { S.decisions = e.target.checked; renderList(); };
$('#add-btn').onclick = openAddDialog;

function toast(tone, text) {
  const ic = { success: 'check', warning: 'warning', danger: 'error' }[tone];
  $('#toasts').innerHTML = `<div class="or-toast or-toast--${tone}" role="status">${Orbit.icon(ic, 'or-toast__icon')}<span>${esc(text)}</span></div>`;
  clearTimeout(toast.t); toast.t = setTimeout(() => ($('#toasts').innerHTML = ''), 4500);
}

// ---------------------------------------------------------------- render
function render() { renderSummary(); renderSections(); renderList(); renderDetail(); $('#add-btn').hidden = !S.canWrite; }

function renderSummary() {
  const el = $('#summary');
  if (S.status !== 'ready') { el.innerHTML = ''; return; }
  const n = S.assets.length;
  const parts = S.assets.reduce((s, a) => s + (a.parts || []).length, 0);
  const done = S.assets.reduce((s, a) => s + (a.parts || []).filter(p => p.done).length, 0);
  const counts = STAGES.map(st => S.assets.filter(a => a.stage === st).length);
  const dec = S.assets.filter(a => a.decision).length;
  const files = S.assets.reduce((s, a) => s + (a.files || []).length, 0);
  el.innerHTML = `
    <div class="sum-main"><span class="big">${parts ? Math.round(done / parts * 100) : 0}%</span><span class="sum-label">of ${parts} deliverables done<br>${n} assets · ${files} files attached</span></div>
    <div class="sum-bar-wrap"><div class="sum-bar" role="img" aria-label="${STAGES.map((s, i) => `${counts[i]} ${s}`).join(', ')}">${counts.map((c, i) => c ? `<i class="${'st-' + i}" style="flex:${c}" title="${STAGES[i]}: ${c}"></i>` : '').join('')}</div>
    <div class="sum-legend">${STAGES.map((s, i) => counts[i] ? `<span><i class="dot ${'st-' + i}"></i>${s} ${counts[i]}</span>` : '').join('')}${dec ? `<button class="sum-dec" id="sum-dec">${Orbit.icon('warning', '')}${dec} need a decision</button>` : ''}</div></div>`;
  const d = $('#sum-dec'); if (d) d.onclick = () => { S.decisions = true; $('#f-dec').checked = true; renderList(); };
}

function renderSections() {
  $('#sections').innerHTML = SECTIONS.map(s => {
    const items = S.assets.filter(a => inSection(a, s));
    const done = items.filter(a => a.stage === 'Done').length;
    return `<button class="or-tab" role="tab" aria-selected="${S.section === s.id}" data-sec="${s.id}">${esc(s.name)} <small>${S.status === 'ready' ? (done ? `${done}/` : '') + items.length : ''}</small></button>`;
  }).join('');
  $$('[data-sec]').forEach(b => (b.onclick = () => { S.section = b.dataset.sec; remember(); renderSections(); renderList(); }));
}

function kindIcon(k) {
  return {
    audio: '<svg viewBox="0 0 24 24"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/><path d="M16 8c1.5 1.2 1.5 6.8 0 8M19 5.5c3 2.6 3 10.4 0 13" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    animation: '<svg viewBox="0 0 24 24"><circle cx="12" cy="5" r="2.5" fill="currentColor"/><path d="M12 8v6l-4 7M12 14l4 7M6 11l6-2 6 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    vfx: '<svg viewBox="0 0 24 24"><path d="M12 2l2 7 7 3-7 3-2 7-2-7-7-3 7-3z" fill="currentColor"/></svg>',
    ui: '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M7 15l3-4 3 3 2-2 3 3" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    art: '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="9" cy="10" r="2" fill="currentColor"/><path d="M4 18l6-5 4 3 6-5" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    model: '<svg viewBox="0 0 24 24"><path d="M12 2l9 5v10l-9 5-9-5V7z M12 12l9-5 M12 12v10 M12 12L3 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'
  }[k] || '';
}

function renderList() {
  const el = $('#list');
  if (S.status === 'loading') { el.innerHTML = `<div class="list-empty"><p>Loading the asset list…</p></div>`; return; }
  if (S.status === 'offline') { el.innerHTML = `<div class="list-empty"><h3>The tracker isn't available here</h3><p>Open this page on claude.ai, signed in, to see and update the asset list. The viewer on the right still previews files from your computer.</p></div>`; return; }
  if (!S.assets.length) { el.innerHTML = `<div class="list-empty"><h3>No assets yet</h3><p>The production list appears here once it is added. ${S.canWrite ? 'Use Add asset to start one.' : ''}</p></div>`; return; }
  const rows = filtered();
  const groups = [];
  rows.forEach(a => { let g = groups.find(x => x.cat === a.category); if (!g) groups.push(g = { cat: a.category, items: [] }); g.items.push(a); });
  el.innerHTML = rows.length ? groups.map(g => `<div class="grp"><div class="grp-h">${esc(g.cat)} <span>${g.items.length}</span></div>${g.items.map(a => {
    const p = progress(a), np = (a.parts || []).length, nd = (a.parts || []).filter(x => x.done).length;
    return `<button class="row ${a.id === S.sel ? 'is-sel' : ''}" data-id="${a.id}" aria-current="${a.id === S.sel}">
      <span class="thumb">${thumbOf(a) ? `<img src="/_blob/${esc(thumbOf(a))}" alt="" loading="lazy">` : kindIcon(a.kind)}</span>
      <span class="row-main"><span class="row-name">${esc(a.name)}${a.decision ? `<span class="dec-flag" title="Needs a decision">${Orbit.icon('warning', '')}</span>` : ''}</span><span class="row-sub">${esc(KIND_LABEL[a.kind])}${a.group ? ' · ' + esc(a.group) : ''}</span></span>
      <span class="row-meta"><span class="pill ${STAGE_CLASS(a.stage)}">${esc(a.stage)}</span><span class="mini"><i style="width:${p * 100}%"></i></span><span class="row-count">${nd}/${np}${(a.files || []).length ? ` · ${a.files.length} file${a.files.length > 1 ? 's' : ''}` : ''}</span></span>
    </button>`;
  }).join('')}</div>`).join('') : `<div class="list-empty"><p>No assets match these filters.</p><button class="or-btn or-btn--ghost" id="clear-f">Clear filters</button></div>`;
  $$('.row', el).forEach(b => (b.onclick = () => select(b.dataset.id)));
  const cf = $('#clear-f'); if (cf) cf.onclick = () => { S.q = ''; S.stage = ''; S.milestone = ''; S.decisions = false; $('#q').value = ''; $('#f-stage').value = ''; $('#f-ms').value = ''; $('#f-dec').checked = false; renderList(); };
}

const thumbOf = a => a.thumb || (a.concepts && a.concepts[0] && a.concepts[0].id) || null;

function select(id) {
  if (S.sel === id) return;
  S.sel = id; S.local = null; remember();
  $$('.row').forEach(r => { r.classList.toggle('is-sel', r.dataset.id === id); r.setAttribute('aria-current', r.dataset.id === id); });
  renderDetail();
}

// ---------------------------------------------------------------- detail: stage area (viewer / audio / image)
let viewer = null;
function getViewer() { if (!viewer) viewer = createViewer($('#vhost')); return viewer; }
const audio = { el: new Audio(), url: null, buf: null };
audio.el.loop = false;

function stageMode(a) { return a ? VIEW_KIND(a.kind) : 'model'; }
function renderStage() {
  const a = current(), mode = stageMode(a);
  $('#vhost').hidden = mode !== 'model';
  $('#audio-panel').hidden = mode !== 'audio';
  $('#image-panel').hidden = mode !== 'image';
  const files = (a && a.files) || [];
  const latest = files.filter(f => f.kind === mode).slice(-1)[0] || files.slice(-1)[0];
  const key = a ? a.id + ':' + (latest ? latest.id : '') + ':' + (a.concepts && a.concepts[0] ? a.concepts[0].id : '') : null;
  if (S.local && S.local.for === (a && a.id)) { renderTools(); return; }
  if (S.loadedFor === key) { renderTools(); return; }
  S.loadedFor = key; S.loaded = null;
  if (viewer) viewer.clear();
  stopAudio(); $('#image-panel').innerHTML = '';
  if (latest) loadStored(latest, latest.kind); else showEmpty(a, mode);
  renderTools();
}

function showEmpty(a, mode) {
  const e = $('#empty');
  if (!a && S.status === 'ready') { e.hidden = false; e.innerHTML = `<p class="em-t">Pick an asset to inspect it</p>`; return; }
  e.hidden = false;
  const what = { model: 'a .glb or .gltf model', audio: 'an .ogg, .wav or .mp3 file', image: 'a .png, .jpg, .webp or .svg image' }[mode];
  const c = a && a.concepts && a.concepts[0];
  if (c && mode !== 'audio') {
    e.innerHTML = `<img class="em-concept" src="/_blob/${esc(c.id)}" alt="Concept art for ${esc(a.name)}"><div class="em-bar"><span><b>Concept art</b> · no ${mode === 'model' ? 'model' : 'final file'} yet. Drop ${what} here to inspect it.</span><button class="or-btn" id="choose">Choose a file</button></div>`;
    $('#choose').onclick = () => pickFile(mode);
    return;
  }
  e.innerHTML = `<div class="em-ico">${kindIcon(a ? a.kind : 'model')}</div><p class="em-t">${a ? `No ${mode === 'model' ? 'model' : mode === 'audio' ? 'audio' : 'image'} for ${esc(a.name)} yet` : 'Model viewer'}</p><p class="em-s">Drop ${what} here to inspect it${mode === 'model' ? ': rotate, check scale in meters, triangle count and animations' : ''}. It stays on your screen until you attach it.</p><button class="or-btn" id="choose">Choose a file</button>`;
  $('#choose').onclick = () => pickFile(mode);
}

async function loadStored(f, mode) {
  // A record can hold files of several kinds (a location has models and screenshots).
  $('#vhost').hidden = mode !== 'model';
  $('#audio-panel').hidden = mode !== 'audio';
  $('#image-panel').hidden = mode !== 'image';
  if (mode !== 'audio') stopAudio();
  const e = $('#empty'); e.hidden = false; e.innerHTML = `<p class="em-t">Loading ${esc(f.name)}…</p>`;
  try {
    const res = await fetch('/_blob/' + f.id);
    if (!res.ok) throw new Error('missing');
    if (mode === 'model') {
      // .glb files from the repo are binary; copies stored in the artifact are glTF JSON.
      const buf = await res.arrayBuffer();
      const glb = buf.byteLength > 4 && new TextDecoder().decode(new Uint8Array(buf, 0, 4)) === 'glTF';
      const { info } = await getViewer().load(glb ? buf : new TextDecoder().decode(buf));
      S.loaded = { info, file: f };
    } else if (mode === 'audio') {
      if ((res.headers.get('content-type') || '').startsWith('audio/')) await showAudio(await res.blob(), f.name);
      else { const w = await res.json(); const bytes = Uint8Array.from(atob(w.data), c => c.charCodeAt(0)); await showAudio(new Blob([bytes], { type: w.mime }), f.name); }
      S.loaded = { file: f };
    }
    else { showImage('/_blob/' + f.id, f.name); S.loaded = { file: f }; }
    e.hidden = true;
  } catch (err) {
    e.innerHTML = `<p class="em-t">${esc(f.name)} couldn't be loaded</p><p class="em-s">The stored copy is missing or unreadable. Attach the file again from your computer.</p>`;
  }
  renderTools(); renderInfo();
}

function pickFile(mode) {
  const inp = $('#file');
  inp.accept = { model: '.glb,.gltf', audio: '.ogg,.wav,.mp3,.opus,.m4a,.flac', image: '.png,.jpg,.jpeg,.webp,.svg,.gif' }[mode];
  inp.value = ''; inp.onchange = () => inp.files[0] && openLocal(inp.files[0]);
  inp.click();
}

async function openLocal(file) {
  const a = current(), mode = stageMode(a), ext = file.name.split('.').pop().toLowerCase();
  const wanted = { model: ['glb', 'gltf'], audio: ['ogg', 'wav', 'mp3', 'opus', 'm4a', 'flac'], image: ['png', 'jpg', 'jpeg', 'webp', 'svg', 'gif'] }[mode];
  if (!wanted.includes(ext)) { toast('warning', `${a ? a.name + ' takes' : 'The viewer takes'} ${wanted.map(x => '.' + x).join(', ')} files.`); return; }
  const e = $('#empty'); e.hidden = false; e.innerHTML = `<p class="em-t">Opening ${esc(file.name)}…</p>`;
  try {
    if (mode === 'model') {
      const data = ext === 'glb' ? await file.arrayBuffer() : await file.text();
      const { gltf, info } = await getViewer().load(data);
      S.local = { for: a && a.id, file, gltf, info, mode };
    } else if (mode === 'audio') {
      await showAudio(file, file.name); S.local = { for: a && a.id, file, mode };
    } else { showImage(URL.createObjectURL(file), file.name); S.local = { for: a && a.id, file, mode }; }
    e.hidden = true;
  } catch (err) {
    e.innerHTML = `<p class="em-t">${esc(file.name)} couldn't be opened</p><p class="em-s">${mode === 'model' ? 'Export a .glb, or a .gltf with embedded buffers and textures. Draco-compressed files aren\'t supported in the hub yet.' : 'The file may be damaged or in a format this browser can\'t decode.'}</p><button class="or-btn" id="choose">Choose another file</button>`;
    $('#choose').onclick = () => pickFile(mode);
  }
  renderTools(); renderInfo();
}

// drag and drop anywhere on the stage
const stageEl = $('#stage-area');
['dragenter', 'dragover'].forEach(t => stageEl.addEventListener(t, ev => { ev.preventDefault(); $('#drop-hint').hidden = false; }));
['dragleave', 'drop'].forEach(t => stageEl.addEventListener(t, ev => { ev.preventDefault(); if (t === 'dragleave' && stageEl.contains(ev.relatedTarget)) return; $('#drop-hint').hidden = true; }));
stageEl.addEventListener('drop', ev => { const f = ev.dataTransfer.files[0]; if (f) openLocal(f); });

async function showAudio(blob, name) {
  stopAudio();
  audio.url = URL.createObjectURL(blob); audio.el.src = audio.url;
  const panel = $('#audio-panel');
  panel.innerHTML = `<canvas id="wave" aria-label="Waveform of ${esc(name)}"></canvas><div class="aud-row"><button class="or-btn or-btn--primary" id="aplay">Play</button><label class="check"><input type="checkbox" id="aloop"> Loop</label><span class="aud-time" id="atime">0:00</span><span class="aud-meta" id="ameta"></span></div>`;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const buf = await ctx.decodeAudioData(await blob.arrayBuffer());
    audio.buf = buf; ctx.close();
    let peak = 0; for (let c = 0; c < buf.numberOfChannels; c++) { const d = buf.getChannelData(c); for (let i = 0; i < d.length; i += 64) peak = Math.max(peak, Math.abs(d[i])); }
    $('#ameta').textContent = `${buf.duration.toFixed(2)} s · ${buf.numberOfChannels === 1 ? 'mono' : buf.numberOfChannels === 2 ? 'stereo' : buf.numberOfChannels + ' ch'} · ${(buf.sampleRate / 1000).toFixed(1)} kHz · peak ${(20 * Math.log10(peak || 1e-6)).toFixed(1)} dBFS`;
    drawWave();
  } catch (e) { $('#ameta').textContent = 'Waveform unavailable for this format'; }
  $('#aplay').onclick = () => (audio.el.paused ? audio.el.play() : audio.el.pause());
  $('#aloop').onchange = e => (audio.el.loop = e.target.checked);
  audio.el.onplay = () => { $('#aplay').textContent = 'Pause'; tick(); };
  audio.el.onpause = audio.el.onended = () => { const b = $('#aplay'); if (b) b.textContent = 'Play'; };
}
function drawWave() {
  const c = $('#wave'); if (!c || !audio.buf) return;
  const w = c.clientWidth, h = c.clientHeight, dpr = devicePixelRatio || 1; c.width = w * dpr; c.height = h * dpr;
  const g = c.getContext('2d'); g.scale(dpr, dpr);
  const d = audio.buf.getChannelData(0), step = Math.ceil(d.length / w), css = getComputedStyle(document.documentElement);
  g.fillStyle = css.getPropertyValue('--shield').trim();
  for (let x = 0; x < w; x++) { let mn = 1, mx = -1; for (let i = 0; i < step; i++) { const v = d[x * step + i] || 0; if (v < mn) mn = v; if (v > mx) mx = v; } g.fillRect(x, (1 + mn) * h / 2, 1, Math.max(1, (mx - mn) * h / 2)); }
  const p = audio.el.duration ? audio.el.currentTime / audio.el.duration : 0;
  g.fillStyle = css.getPropertyValue('--accent').trim(); g.fillRect(p * w, 0, 2, h);
}
function tick() { if (audio.el.paused) return; drawWave(); const t = $('#atime'); if (t) t.textContent = `${Math.floor(audio.el.currentTime / 60)}:${String(Math.floor(audio.el.currentTime % 60)).padStart(2, '0')}`; requestAnimationFrame(tick); }
function stopAudio() { audio.el.pause(); if (audio.url) URL.revokeObjectURL(audio.url); audio.url = null; audio.buf = null; }
function showImage(src, name) { $('#image-panel').innerHTML = `<img src="${esc(src)}" alt="${esc(name)}">`; }

function renderTools() {
  const t = $('#vtools'), a = current(), mode = stageMode(a);
  const has = mode === 'model' ? viewer && viewer.hasModel() : !!(S.local || S.loaded);
  const info = S.local ? S.local.info : S.loaded && S.loaded.info;
  let html = '';
  if (mode === 'model' && has) {
    html += `<div class="seg" role="group" aria-label="Lighting"><button data-light="studio" aria-pressed="${(S.light || 'studio') === 'studio'}">Studio</button><button data-light="sky" aria-pressed="${S.light === 'sky'}">Ringfall dusk</button><button data-light="flat" aria-pressed="${S.light === 'flat'}">Flat</button></div>
      <label class="check"><input type="checkbox" id="t-wire" ${S.wire ? 'checked' : ''}> Wireframe</label>
      <label class="check"><input type="checkbox" id="t-grid" ${S.grid === false ? '' : 'checked'}> Grid (1 m)</label>
      <label class="check"><input type="checkbox" id="t-rot" ${S.rot ? 'checked' : ''}> Turntable</label>
      ${info && info.animations.length ? `<select class="or-select" id="t-anim" aria-label="Animation"><option value="-1">Bind pose</option>${info.animations.map((x, i) => `<option value="${i}">${esc(x.name)} · ${x.duration}s</option>`).join('')}</select>` : ''}
      <button class="or-btn or-btn--ghost" id="t-reset">Reset view</button>`;
  }
  if (has || S.local) html += `<span class="spacer"></span><button class="or-btn or-btn--ghost" id="t-open">Open another file</button>`;
  if (S.local && a && S.store && S.canWrite) html += `<button class="or-btn or-btn--primary" id="t-attach">Attach to ${esc(a.name)}</button>`;
  else if (S.local && a) html += `<span class="note">${S.store ? 'Viewing only: you can\'t attach files here' : 'Preview only on this screen'}</span>`;
  t.innerHTML = html;
  $$('[data-light]', t).forEach(b => (b.onclick = () => { S.light = b.dataset.light; getViewer().setLighting(S.light); renderTools(); }));
  const on = (id, f) => { const el = $(id, t); if (el) el.onchange = el.onclick = f; };
  on('#t-wire', e => { S.wire = e.target.checked; getViewer().setWire(S.wire); });
  on('#t-grid', e => { S.grid = e.target.checked; getViewer().setGrid(S.grid); });
  on('#t-rot', e => { S.rot = e.target.checked; getViewer().setAutoRotate(S.rot); });
  const an = $('#t-anim', t); if (an) an.onchange = e => (+e.target.value < 0 ? viewer.stop() : viewer.play(+e.target.value));
  const rs = $('#t-reset', t); if (rs) rs.onclick = () => viewer.reset();
  const op = $('#t-open', t); if (op) op.onclick = () => pickFile(mode);
  const at = $('#t-attach', t); if (at) at.onclick = attachLocal;
}

// ---------------------------------------------------------------- attach / remove files
async function attachLocal() {
  const a = current(), L = S.local; if (!a || !L || !S.store) return;
  const btn = $('#t-attach'); btn.classList.add('is-pending'); btn.disabled = true;
  try {
    let blob, type, extra = {}, thumb = null;
    if (L.mode === 'model') {
      const json = await viewer.toGltfJson(L.gltf);
      blob = new Blob([json], { type: 'application/json' }); type = 'application/json';
      extra = { tris: L.info.tris, size: L.info.size, animations: L.info.animations.length };
      const shot = await (await fetch(viewer.snapshot())).blob();
      try { thumb = (await S.store.upload(shot, { type: 'image/webp' })).id; } catch (e) { thumb = null; }
    } else if (L.mode === 'audio') {
      const b64 = await new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(String(r.result).split(',')[1]); r.onerror = rej; r.readAsDataURL(L.file); });
      blob = new Blob([JSON.stringify({ format: 'orbit-audio/1', mime: L.file.type || 'audio/ogg', name: L.file.name, data: b64 })], { type: 'application/json' }); type = 'application/json';
      extra = { duration: audio.buf ? +audio.buf.duration.toFixed(2) : null };
    } else {
      blob = L.file; type = { svg: 'image/svg+xml', jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', webp: 'image/webp', gif: 'image/gif' }[L.file.name.split('.').pop().toLowerCase()];
    }
    if (blob.size > MAX_BYTES) { toast('warning', `The hub copy would be ${fmtBytes(blob.size)}; the limit is 20 MB. Use 2048² textures or smaller, or keep this file in the repo only.`); return; }
    const up = await S.store.upload(blob, { type });
    const rec = Object.assign({ id: up.id, kind: L.mode, name: L.file.name, bytes: L.file.size, at: new Date().toISOString(), by: S.me || null }, extra);
    const patch = { files: (a.files || []).concat(rec) };
    if (thumb) patch.thumb = thumb; else if (L.mode === 'image') patch.thumb = up.id;
    if (await save(a.id, patch)) { toast('success', `${L.file.name} attached to ${a.name}`); S.local = null; S.loadedFor = a.id + ':' + up.id; S.loaded = { info: L.info, file: rec }; }
  } catch (e) {
    const msg = { too_large: 'That file is over the hub\'s size limit.', unsupported_type: 'The hub can\'t store that file type.', quota_or_state: 'The hub\'s storage is full. Remove old files first.', rate_limited: 'Too many uploads at once. Wait a moment and try again.' }[e && e.code] || 'The upload didn\'t finish. Try again.';
    toast('danger', msg);
  } finally { const b = $('#t-attach'); if (b) { b.classList.remove('is-pending'); b.disabled = false; } }
}

async function removeFile(fid) {
  const a = current(); if (!a) return;
  const files = (a.files || []).filter(f => f.id !== fid);
  const patch = { files };
  if (a.thumb && (a.files || []).find(f => f.id === fid && (f.kind === 'model' || f.id === a.thumb))) patch.thumb = files.filter(f => f.kind !== 'audio').slice(-1)[0]?.id || null;
  if (await save(a.id, patch)) {
    try { await S.store.delete(fid); } catch (e) { /* row already updated; an orphaned blob is harmless */ }
    toast('success', 'File removed');
  }
}

// ---------------------------------------------------------------- detail: info
function renderDetail() { renderStage(); renderInfo(); }
function renderInfo() {
  const el = $('#info'), a = current();
  const typing = document.activeElement && el.contains(document.activeElement) && /^(TEXTAREA|INPUT)$/.test(document.activeElement.tagName) && document.activeElement.type !== 'checkbox';
  if (typing && a && el.dataset.for === a.id) return;
  el.dataset.for = a ? a.id : '';
  if (!a) { el.innerHTML = S.status === 'ready' ? `<p class="note">Select an asset from the list to see its deliverables, budget and files.</p>` : ''; return; }
  const w = S.canWrite, info = S.local ? S.local.info : S.loaded && S.loaded.info;
  const np = (a.parts || []).length, nd = (a.parts || []).filter(p => p.done).length;
  const ids = (a.files || []).map(f => f.by).filter(Boolean);
  el.innerHTML = `
    <div class="info-head">
      <div><div class="or-eyebrow">${esc(a.category)} · ${esc(KIND_LABEL[a.kind])}</div><h2>${esc(a.name)}</h2>${a.group ? `<div class="note">${esc(a.group)}</div>` : ''}</div>
      <div class="stage-ctl"><label for="i-stage" class="lbl">Stage</label>${w ? `<select class="or-select" id="i-stage">${STAGES.map(s => `<option ${s === a.stage ? 'selected' : ''}>${s}</option>`).join('')}</select>` : `<span class="pill ${STAGE_CLASS(a.stage)}">${esc(a.stage)}</span>`}</div>
    </div>
    ${a.decision ? `<div class="decision">${Orbit.icon('warning', '')}<div><strong>Needs a decision</strong><span>${esc(a.decision)}</span></div>${w ? `<button class="or-btn or-btn--ghost" id="i-resolve">Mark resolved</button>` : ''}</div>` : ''}
    ${info ? statsHtml(a, info) : ''}
    <div class="concepts">
      <div class="col-h"><span class="lbl">Concept art</span><span class="note">${(a.concepts || []).length ? `${a.concepts.length} image${a.concepts.length === 1 ? '' : 's'} · select one to view full size` : 'None yet'}</span></div>
      <div class="cgrid">${(a.concepts || []).map((c, i) => `<button class="cthumb" data-ci="${i}" aria-label="View concept ${i + 1} of ${a.concepts.length}"><img src="/_blob/${esc(c.id)}" alt="" loading="lazy"></button>`).join('')}${w && S.store ? `<button class="cthumb cadd" id="c-add" aria-label="Add concept art">+ Add image</button>` : ''}</div>
    </div>
    <div class="cols">
      <div class="col">
        <div class="col-h"><span class="lbl">Deliverables</span><span class="note">${nd} of ${np} done</span></div>
        <ul class="parts">${(a.parts || []).map((p, i) => `<li><label class="check"><input type="checkbox" data-part="${i}" ${p.done ? 'checked' : ''} ${w ? '' : 'disabled'}> <span>${esc(p.n)}</span></label></li>`).join('')}</ul>
        ${w ? `<form class="add-part" id="add-part"><input id="i-newpart" placeholder="Add a deliverable" aria-label="New deliverable"><button class="or-btn or-btn--ghost">Add</button></form>` : ''}
      </div>
      <div class="col">
        <dl class="facts">
          <dt>Milestone</dt><dd>${w ? `<select class="or-select" id="i-ms">${MILESTONES.map(m => `<option ${m === a.milestone ? 'selected' : ''}>${m}</option>`).join('')}</select>` : esc(a.milestone)}</dd>
          <dt>Budget</dt><dd>${esc(a.budget || 'Not set')}${a.budget ? ' <span class="note">(proposed)</span>' : ''}</dd>
          <dt>Game file</dt><dd><code>${esc(a.path)}</code> <button class="copy" data-copy="${esc(a.path)}">Copy</button></dd>
          ${a.source ? `<dt>Blender source</dt><dd><code>${esc(a.source)}</code> <button class="copy" data-copy="${esc(a.source)}">Copy</button></dd>` : ''}
        </dl>
        <label class="lbl" for="i-notes">Notes</label>
        <textarea id="i-notes" rows="4" ${w ? '' : 'readonly'} placeholder="${w ? 'References, art direction, feedback' : ''}">${esc(a.notes || '')}</textarea>
        <span class="note" id="notes-state"></span>
      </div>
    </div>
    <div class="files">
      <div class="col-h"><span class="lbl">Attached files</span><span class="note">Hub preview copies. Source files live in the repo.</span></div>
      ${(a.files || []).length ? `<ul>${a.files.slice().reverse().map(f => `<li><button class="file-open" data-fid="${f.id}">${kindIcon(f.kind === 'image' ? 'art' : f.kind)}<span><b>${esc(f.name)}</b><small>${fmtBytes(f.bytes || 0)}${f.tris ? ' · ' + f.tris.toLocaleString() + ' tris' : ''}${f.duration ? ' · ' + f.duration + ' s' : ''} · ${fmtDate(f.at)} · <span data-uid="${esc(f.by || '')}"></span></small></span></button>${w && S.store ? `<button class="or-btn or-btn--ghost rm" data-rm="${f.id}">Remove</button>` : ''}</li>`).join('')}</ul>` : `<p class="note">Nothing attached yet. Drop a file on the viewer above.</p>`}
    </div>
    <div class="updated note">${a.updatedAt ? `Last change ${fmtDate(a.updatedAt)} · <span data-uid="${esc(a.updatedBy || '')}"></span>` : 'Not changed since the list was created'}</div>
    ${w ? `<div class="danger-zone"><button class="or-btn or-btn--danger" id="i-del">Delete asset</button></div>` : ''}`;
  resolveNames([...ids, a.updatedBy].filter(Boolean));
  $$('[data-ci]', el).forEach(b => (b.onclick = () => openConcept(a.id, +b.dataset.ci)));
  const cadd = $('#c-add', el); if (cadd) cadd.onclick = () => addConcept(a);
  if (!w) { wireCopy(el); wireFiles(el); return; }
  $('#i-stage').onchange = e => save(a.id, { stage: e.target.value });
  $('#i-ms').onchange = e => save(a.id, { milestone: e.target.value });
  $$('[data-part]', el).forEach(c => (c.onchange = () => { const parts = a.parts.map((p, i) => (i === +c.dataset.part ? { n: p.n, done: c.checked } : { n: p.n, done: p.done })); save(a.id, { parts }); }));
  $('#add-part').onsubmit = ev => { ev.preventDefault(); const v = $('#i-newpart').value.trim(); if (v) save(a.id, { parts: (a.parts || []).map(p => ({ n: p.n, done: p.done })).concat({ n: v, done: false }) }); };
  const notes = $('#i-notes');
  notes.onblur = async () => { if (notes.value !== (a.notes || '')) { $('#notes-state').textContent = 'Saving…'; $('#notes-state').textContent = (await save(a.id, { notes: notes.value })) ? 'Saved' : ''; } };
  const rv = $('#i-resolve'); if (rv) rv.onclick = () => save(a.id, { decision: null, notes: ((a.notes || '') + `\nDecision resolved ${fmtDate(new Date().toISOString())}: ${a.decision}`).trim() });
  $('#i-del').onclick = () => confirmDelete(a);
  wireCopy(el); wireFiles(el);
}
function wireCopy(el) { $$('[data-copy]', el).forEach(b => (b.onclick = async () => { try { await navigator.clipboard.writeText(b.dataset.copy); b.textContent = 'Copied'; } catch (e) { const r = document.createRange(); r.selectNodeContents(b.previousElementSibling); getSelection().removeAllRanges(); getSelection().addRange(r); b.textContent = 'Selected'; } setTimeout(() => (b.textContent = 'Copy'), 1500); })); }
function wireFiles(el) {
  $$('[data-fid]', el).forEach(b => (b.onclick = () => { const a = current(), f = a.files.find(x => x.id === b.dataset.fid); S.local = null; S.loadedFor = a.id + ':' + f.id; if (viewer) viewer.clear(); loadStored(f, f.kind); }));
  $$('[data-rm]', el).forEach(b => (b.onclick = () => {
    if (b.dataset.armed) return removeFile(b.dataset.rm);
    b.dataset.armed = '1'; b.textContent = 'Remove for everyone'; b.classList.add('or-btn--danger');
    setTimeout(() => { if (b.isConnected) { delete b.dataset.armed; b.textContent = 'Remove'; b.classList.remove('or-btn--danger'); } }, 4000);
  }));
}
function statsHtml(a, info) {
  const m = /([\d.]+)k tris/.exec(a.budget || ''), budget = m ? +m[1] * 1000 : null;
  const over = budget && info.tris > budget;
  return `<div class="stats">
    <div><small>Triangles</small><strong class="${over ? 'is-over' : ''}">${info.tris.toLocaleString()}</strong>${budget ? `<span>${over ? 'over' : 'within'} ${budget.toLocaleString()} budget</span>` : ''}</div>
    <div><small>Size (m)</small><strong>${info.size.join(' × ')}</strong><span>W × H × D</span></div>
    <div><small>Materials</small><strong>${info.materials}</strong><span>${info.textures} textures${info.maxTex ? ', max ' + info.maxTex + 'px' : ''}</span></div>
    <div><small>Rig</small><strong>${info.skinned ? 'Skinned' : 'Static'}</strong><span>${info.animations.length} animation${info.animations.length === 1 ? '' : 's'}</span></div>
    ${S.local ? '<p class="note local-note">Previewing a file from your computer. Not saved to the hub.</p>' : ''}</div>`;
}
async function resolveNames(ids) {
  if (!S.user || !ids.length) return;
  try {
    const ps = await S.user.profiles([...new Set(ids)]);
    $$('[data-uid]').forEach(s => { const id = s.dataset.uid; s.textContent = id ? (id === S.me ? 'you' : (ps[id] && ps[id].name) || 'Someone') : 'unknown'; });
  } catch (e) { /* names are optional */ }
}

// ---------------------------------------------------------------- concept art
function openConcept(assetId, i) {
  const a = S.assets.find(x => x.id === assetId); if (!a || !a.concepts || !a.concepts[i]) return;
  const c = a.concepts[i], n = a.concepts.length, w = S.canWrite && S.store;
  const l = openLayer(`<div class="lightbox" role="dialog" aria-modal="true" aria-label="Concept art for ${esc(a.name)}">
    <div class="lb-head"><div><div class="or-eyebrow">${esc(a.name)} · concept ${i + 1} of ${n}</div><div class="note">${esc(c.source || c.name || '')}</div></div>
      <div class="lb-actions">${w ? `<button class="or-btn or-btn--ghost" id="lb-rm">Remove</button>` : ''}<button class="or-btn" id="lb-x">Close</button></div></div>
    <div class="lb-img">${n > 1 ? `<button class="lb-nav prev" id="lb-prev" aria-label="Previous concept">‹</button>` : ''}<img src="/_blob/${esc(c.id)}" alt="Concept art for ${esc(a.name)}">${n > 1 ? `<button class="lb-nav next" id="lb-next" aria-label="Next concept">›</button>` : ''}</div></div>`);
  const go = d => openConcept(assetId, (i + d + n) % n);
  $('#lb-x', l).onclick = closeLayer; $('#lb-x', l).focus();
  const p = $('#lb-prev', l), nx = $('#lb-next', l); if (p) p.onclick = () => go(-1); if (nx) nx.onclick = () => go(1);
  l.onkeydown = e => { if (e.key === 'Escape') closeLayer(); if (n > 1 && e.key === 'ArrowLeft') go(-1); if (n > 1 && e.key === 'ArrowRight') go(1); };
  const rm = $('#lb-rm', l);
  if (rm) rm.onclick = async () => {
    if (!rm.dataset.armed) { rm.dataset.armed = '1'; rm.textContent = 'Remove for everyone'; rm.classList.add('or-btn--danger'); return; }
    const patch = { concepts: a.concepts.filter((_, k) => k !== i) };
    if (await save(a.id, patch)) { try { await S.store.delete(c.id); } catch (e) { /* orphan is harmless */ } closeLayer(); toast('success', 'Concept image removed'); }
  };
}
function addConcept(a) {
  const inp = $('#file');
  inp.accept = '.png,.jpg,.jpeg,.webp'; inp.value = '';
  inp.onchange = async () => {
    const f = inp.files[0]; if (!f) return;
    const type = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp' }[f.name.split('.').pop().toLowerCase()];
    if (!type) { toast('warning', 'Concept art takes .png, .jpg or .webp images.'); return; }
    if (f.size > MAX_BYTES) { toast('warning', `That image is ${fmtBytes(f.size)}; the limit is 20 MB. Export it as .webp or .jpg first.`); return; }
    try {
      const up = await S.store.upload(f, { type });
      if (await save(a.id, { concepts: (a.concepts || []).concat({ id: up.id, name: f.name, source: f.name, at: new Date().toISOString(), by: S.me || null }) })) toast('success', `Concept added to ${a.name}`);
    } catch (e) { toast('danger', e && e.code === 'quota_or_state' ? 'The hub\'s storage is full. Remove old files first.' : 'The upload didn\'t finish. Try again.'); }
  };
  inp.click();
}

// ---------------------------------------------------------------- dialogs
function openLayer(html) { const l = $('#layer'); l.innerHTML = `<div class="or-backdrop">${html}</div>`; l.classList.add('is-open'); l.onkeydown = e => { if (e.key === 'Escape') closeLayer(); }; return l; }
function closeLayer() { const l = $('#layer'); l.classList.remove('is-open'); l.innerHTML = ''; }
function confirmDelete(a) {
  const l = openLayer(`<div class="or-dialog" role="dialog" aria-modal="true" aria-labelledby="d-t"><h2 id="d-t">Delete ${esc(a.name)}?</h2><p>Removes it from the tracker for everyone, with its deliverables, notes and ${(a.files || []).length} attached file${(a.files || []).length === 1 ? '' : 's'}. Files in the repo are not touched.</p><div class="or-dialog__actions"><button class="or-btn or-btn--ghost" id="d-no">Keep it</button><button class="or-btn or-btn--danger" id="d-yes">Delete asset</button></div></div>`);
  $('#d-no', l).onclick = closeLayer; $('#d-no', l).focus();
  $('#d-yes', l).onclick = async () => {
    try {
      await S.db.collection('assets').doc(a.id).delete();
      for (const f of a.files || []) { try { await S.store.delete(f.id); } catch (e) { /* orphan is harmless */ } }
      if (a.thumb) { try { await S.store.delete(a.thumb); } catch (e) { /* ignore */ } }
      closeLayer(); S.sel = null; toast('success', `${a.name} deleted`);
    } catch (e) { toast('danger', 'Could not delete. Try again.'); }
  };
}
function openAddDialog() {
  const cats = [...new Set(S.assets.map(a => a.category))];
  const l = openLayer(`<form class="or-dialog add-form" role="dialog" aria-modal="true" aria-labelledby="a-t" id="a-form"><h2 id="a-t">Add asset</h2>
    <label class="lbl" for="a-name">Name</label><input id="a-name" required placeholder="e.g. Colony fuel tank">
    <div class="two"><div><label class="lbl" for="a-cat">Category</label><select class="or-select" id="a-cat">${cats.map(c => `<option>${esc(c)}</option>`).join('')}</select></div>
    <div><label class="lbl" for="a-kind">Type</label><select class="or-select" id="a-kind">${Object.entries(KIND_LABEL).map(([k, v]) => `<option value="${k}">${v}</option>`).join('')}</select></div></div>
    <label class="lbl" for="a-ms">Milestone</label><select class="or-select" id="a-ms">${MILESTONES.map(m => `<option>${m}</option>`).join('')}</select>
    <label class="lbl" for="a-parts">Deliverables, one per line</label><textarea id="a-parts" rows="4" placeholder="Mesh&#10;Materials&#10;Icon"></textarea>
    <p class="note" id="a-err" role="alert"></p>
    <div class="or-dialog__actions"><button type="button" class="or-btn or-btn--ghost" id="a-no">Cancel</button><button class="or-btn or-btn--primary">Add asset</button></div></form>`);
  $('#a-name', l).focus(); $('#a-no', l).onclick = closeLayer;
  $('#a-form', l).onsubmit = async ev => {
    ev.preventDefault();
    const name = $('#a-name', l).value.trim(), id = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    if (!id) return;
    if (S.assets.some(a => a.id === id)) { $('#a-err', l).textContent = `An asset called ${name} already exists.`; return; }
    const cat = $('#a-cat', l).value, kind = $('#a-kind', l).value, cslug = cat.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    const folder = { model: 'models', animation: 'animations', audio: 'audio', vfx: 'vfx', ui: 'ui', art: 'art' }[kind], ext = { model: 'glb', animation: 'glb', vfx: 'glb', audio: 'ogg', ui: 'svg', art: 'png' }[kind];
    try {
      await S.db.collection('assets').doc(id).set({ name, category: cat, kind, group: null, milestone: $('#a-ms', l).value, stage: 'Not started',
        parts: $('#a-parts', l).value.split('\n').map(s => s.trim()).filter(Boolean).map(n => ({ n, done: false })),
        budget: null,
        path: kind === 'audio' || kind === 'ui' ? `game/assets/${folder}/${cslug}/${id}/` : `game/assets/${folder}/${cslug}/${id}.${ext}`,
        source: ['model', 'animation', 'vfx'].includes(kind) ? `art/${cslug}/${id}.blend` : kind === 'audio' ? `art/${cslug}/${id}/` : null,
        decision: null, notes: '', order: Math.max(0, ...S.assets.map(a => a.order || 0)) + 1, files: [], createdAt: new Date().toISOString(), updatedBy: S.me || null });
      closeLayer(); S.sel = id; toast('success', `${name} added`);
    } catch (e) { $('#a-err', l).textContent = e && e.code === 'quota_exceeded' ? 'The tracker is full. Delete unused assets first.' : 'Could not add the asset. Try again.'; }
  };
}

// ---------------------------------------------------------------- boot
render();
(async () => {
  const use = n => (window.claude && window.claude.use ? window.claude.use(n) : Promise.resolve(null));
  const [db, user, store] = await Promise.all([use('db'), use('user'), use('assets')]);
  S.db = db; S.user = user; S.store = store;
  if (!db) { S.status = 'offline'; render(); return; }
  if (user) { try { S.me = await user.id(); } catch (e) { S.me = null; } const c = await user.can('data.write'); S.canWrite = c !== false; }
  db.collection('assets').onSnapshot(snap => {
    S.assets = snap.docs.map(d => Object.assign({ id: d.id }, d.data())).sort((a, b) => (a.order ?? 1e9) - (b.order ?? 1e9));
    S.status = 'ready';
    if (S.sel && !S.assets.some(a => a.id === S.sel)) S.sel = null;
    if (!S.sel && S.assets.length) S.sel = S.assets[0].id;
    render();
  }, () => { S.status = 'offline'; render(); });
})();
window.addEventListener('resize', () => drawWave());
