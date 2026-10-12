// Attach the repo's current files to Asset Hub records.
//
//   node asset-hub/sync.js                 refresh files on every record
//   node asset-hub/sync.js --from <dir>    first run: import records exported from
//                                          the claude.ai artifact (<dir>/<id>.json)
//
// Each record gets the files that belong to it (models, sounds, icons,
// screenshots) as "repo/<path>" ids, which asset-hub/server.js serves straight
// from the repo, plus a thumbnail from asset-hub/data/thumbs. Files attached by
// hand through the hub (stored in data/blobs) are kept. Run it after adding
// assets, then commit asset-hub/data.

const fs = require('fs');
const path = require('path');

const HUB = __dirname;
const REPO = path.resolve(HUB, '..');
const DB = path.join(HUB, 'data', 'assets.json');
const M = 'game/assets/models/';
const SHOTS = 'asset-hub/data/shots/';

// Records whose files aren't simply their `path` (a file or a folder). Entries are
// repo paths; a trailing * matches by prefix within that folder.
const FILES = {
  'operator-third-person': [M + 'characters/operator.glb'],
  'bot-operator': [M + 'characters/bot-operator-*'],
  'first-person-arms': [M + 'characters/first-person-arms.glb'],
  'ammunition-boxes': [M + 'pickups/ammo-*'],
  // Every animation clip lives on the rigged operator.
  ...Object.fromEntries(['locomotion-set', 'tethercaster-traversal-set', 'weapon-handling-set', 'healing-use-set', 'freefall-and-landing', 'vehicle-set', 'elimination'].map(id => [id, [M + 'characters/operator.glb']])),
  'colony-supply-crate': [M + 'pickups/colony-supply-crate.glb'],
  'colony-structure-kit': [M + 'colony-kit/*'],
  'prop-kit': [M + 'props/*'],
  'ancient-ruins-kit': [M + 'ruins-kit/*'],
  'luminous-vegetation-kit': [M + 'vegetation/*'],
  'ringfall-terrain': [SHOTS + 'ringfall-overview.jpg', SHOTS + 'ringfall-height-map.jpg', M + 'terrain-kit/rock-*', M + 'terrain-kit/ring-fragment.glb'],
  'ringfall-map-illustration': [SHOTS + 'ringfall-height-map.jpg'],
  'ringed-sky-dome': [SHOTS + 'ringfall-overview.jpg'],
  'glass-basin': [SHOTS + 'glass-basin.jpg', M + 'terrain-kit/glass-*', M + 'terrain-kit/ring-fragment.glb'],
  'crown-observatory': [SHOTS + 'crown-observatory.jpg', M + 'locations/observatory-dome.glb', M + 'locations/comms-dish.glb'],
  'relay-nine': [SHOTS + 'relay-nine.jpg', M + 'locations/relay-power-core.glb'],
  'anchorport': [SHOTS + 'anchorport.jpg'],
  'bloomwild': [SHOTS + 'bloomwild.jpg'],
  'the-spine': [SHOTS + 'the-spine.jpg'],
  'hollow-array': [SHOTS + 'hollow-array.jpg'],
};
const KIND = { '.glb': 'model', '.gltf': 'model', '.wav': 'audio', '.ogg': 'audio', '.mp3': 'audio', '.png': 'image', '.jpg': 'image', '.jpeg': 'image', '.webp': 'image', '.svg': 'image' };

function expand(entry) {
  const abs = path.join(REPO, entry.replace(/\*$/, ''));
  if (entry.endsWith('/*')) return expand(entry.slice(0, -1));
  if (entry.endsWith('*')) {
    const dir = path.dirname(abs);
    const prefix = path.basename(abs);
    if (!fs.existsSync(dir)) return [];
    return fs.readdirSync(dir).filter(f => f.startsWith(prefix)).sort().map(f => path.relative(REPO, path.join(dir, f)));
  }
  if (!fs.existsSync(abs)) return [];
  if (fs.statSync(abs).isDirectory()) return fs.readdirSync(abs).sort().map(f => path.relative(REPO, path.join(abs, f)));
  return [path.relative(REPO, abs)];
}

// Triangle and animation counts from a .glb's JSON chunk.
function glbInfo(file) {
  try {
    const buf = fs.readFileSync(file);
    const len = buf.readUInt32LE(12);
    const doc = JSON.parse(buf.slice(20, 20 + len).toString('utf8'));
    let tris = 0;
    for (const m of doc.meshes || []) for (const p of m.primitives || []) {
      if ((p.mode ?? 4) !== 4) continue;
      tris += Math.floor(doc.accessors[p.indices ?? p.attributes.POSITION].count / 3);
    }
    return { tris, animations: (doc.animations || []).length };
  } catch (e) {
    return {};
  }
}

function filesFor(rec) {
  const entries = FILES[rec.id] || (rec.path ? [rec.path] : []);
  const out = [];
  for (const e of entries) {
    for (const rel of expand(e)) {
      const posix = rel.replace(/\\/g, '/');
      const kind = KIND[path.extname(posix).toLowerCase()];
      if (!kind || out.some(f => f.id === 'repo/' + posix)) continue;
      // Textures Godot extracted from a model belong to that model, not the record.
      if (kind === 'image' && posix.startsWith(M)) continue;
      const st = fs.statSync(path.join(REPO, rel));
      const f = { id: 'repo/' + posix, kind, name: path.basename(posix), bytes: st.size, at: st.mtime.toISOString(), by: null };
      if (kind === 'model') Object.assign(f, glbInfo(path.join(REPO, rel)));
      out.push(f);
    }
  }
  return out;
}

function thumbFor(files) {
  for (const f of files) {
    const base = path.basename(f.name, path.extname(f.name));
    if (f.kind === 'model' && fs.existsSync(path.join(HUB, 'data', 'thumbs', base + '.jpg'))) return 'repo/asset-hub/data/thumbs/' + base + '.jpg';
    if (f.kind === 'image') return f.id;
  }
  return null;
}

let records = fs.existsSync(DB) ? JSON.parse(fs.readFileSync(DB, 'utf8')) : [];
const from = process.argv.indexOf('--from');
if (from > 0) {
  const dir = process.argv[from + 1];
  records = fs.readdirSync(dir).filter(f => f.endsWith('.json')).map(f => Object.assign({ id: path.basename(f, '.json') }, JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'))));
  // Uploads to the artifact store don't exist here; repo files replace them.
  for (const r of records) { r.files = []; r.thumb = null; }
}

let attached = 0;
for (const r of records) {
  const kept = (r.files || []).filter(f => !String(f.id).startsWith('repo/') && /^[0-9a-f]{32}$/.test(f.id) && fs.existsSync(path.join(HUB, 'data', 'blobs', f.id)));
  const repo = filesFor(r);
  r.files = kept.concat(repo);
  attached += repo.length;
  const t = thumbFor(repo);
  if (t) r.thumb = t;
  else if (r.thumb && String(r.thumb).startsWith('repo/') && !fs.existsSync(path.join(REPO, r.thumb.slice(5)))) r.thumb = null;
}
fs.mkdirSync(path.dirname(DB), { recursive: true });
fs.writeFileSync(DB, JSON.stringify(records.sort((a, b) => (a.order ?? 1e9) - (b.order ?? 1e9)), null, 1) + '\n');
console.log(`${records.length} records, ${attached} repo files attached -> ${path.relative(REPO, DB)}`);
