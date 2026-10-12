// Orbit Royale Asset Hub as its own web page, served from the repo.
//
//   node asset-hub/server.js [port]      then open http://localhost:5180
//
// The hub talks to this server through the same calls it uses as a claude.ai
// artifact (see local-backend.js): records are kept in asset-hub/data/assets.json
// (commit it to share progress), files dropped on the viewer are stored in
// asset-hub/data/blobs/, and attached game files are served straight from the
// repo (ids starting with "repo/"), so models, textures, sounds and concept art
// are always the current versions with nothing to upload.
// Listens on localhost only.

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const HUB = __dirname;
const REPO = path.resolve(HUB, '..');
const DATA = path.join(HUB, 'data');
const BLOBS = path.join(DATA, 'blobs');
const DB = path.join(DATA, 'assets.json');
const PORT = +process.argv[2] || 5180;
// Repo folders the hub may read files from.
const REPO_ALLOW = ['game/assets/', 'codex/concepts/', 'asset-hub/data/', 'art/'];

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml',
  '.gif': 'image/gif', '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json', '.wav': 'audio/wav', '.ogg': 'audio/ogg',
  '.mp3': 'audio/mpeg', '.woff2': 'font/woff2'
};

fs.mkdirSync(BLOBS, { recursive: true });
let assets = [];
let loadedAt = 0;
// Re-read the file when it changes on disk (git pull, sync.js), so edits made
// outside the hub aren't overwritten by the next save.
function loadDb() {
  if (!fs.existsSync(DB)) return;
  const m = fs.statSync(DB).mtimeMs;
  if (m !== loadedAt) { assets = JSON.parse(fs.readFileSync(DB, 'utf8')); loadedAt = m; }
}
function saveDb() {
  fs.writeFileSync(DB, JSON.stringify(assets.slice().sort((a, b) => (a.order ?? 1e9) - (b.order ?? 1e9)), null, 1) + '\n');
  loadedAt = fs.statSync(DB).mtimeMs;
}
loadDb();

function send(res, code, body, type = 'application/json') {
  res.writeHead(code, { 'content-type': type, 'cache-control': 'no-store' });
  res.end(typeof body === 'string' || Buffer.isBuffer(body) ? body : JSON.stringify(body));
}

function sendFile(res, file) {
  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) return send(res, 404, { error: 'not found' });
    res.writeHead(200, { 'content-type': TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream', 'content-length': st.size, 'cache-control': 'no-cache' });
    fs.createReadStream(file).pipe(res);
  });
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    req.on('data', c => { size += c.length; if (size > 64 * 1024 * 1024) { reject(Object.assign(new Error('too large'), { code: 413 })); req.destroy(); } else chunks.push(c); });
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

// "repo/<path>" -> absolute path inside an allowed repo folder, or null.
function repoPath(id) {
  const rel = decodeURIComponent(id.slice(5)).replace(/\\/g, '/');
  if (rel.includes('..') || !REPO_ALLOW.some(p => rel.startsWith(p))) return null;
  return path.join(REPO, rel);
}

function blobFile(id) {
  if (id.startsWith('repo/')) return repoPath(id);
  if (!/^[0-9a-f]{32}$/.test(id)) return null;
  const f = path.join(BLOBS, id);
  if (fs.existsSync(f)) return f;
  // Concept art uploaded to the old artifact: fall back to its source in codex/.
  for (const a of assets) for (const c of a.concepts || []) if (c.id === id && c.source) return path.join(REPO, c.source);
  return null;
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  const p = decodeURIComponent(url.pathname);
  try {
    if (p.startsWith('/api/') || p.startsWith('/_blob/')) loadDb();
    if (p === '/api/ping') return send(res, 200, { ok: true });
    if (p === '/api/assets' && req.method === 'GET') return send(res, 200, assets);
    if (p.startsWith('/api/assets/')) {
      const id = p.slice(12);
      const i = assets.findIndex(a => a.id === id);
      if (req.method === 'DELETE') { if (i >= 0) assets.splice(i, 1); saveDb(); return send(res, 200, { ok: true }); }
      const body = JSON.parse((await readBody(req)).toString('utf8') || '{}');
      if (req.method === 'PUT') { const doc = Object.assign({ id }, body); if (i >= 0) assets[i] = doc; else assets.push(doc); }
      else if (req.method === 'PATCH') { if (i < 0) return send(res, 404, { error: 'not found' }); Object.assign(assets[i], body); }
      else return send(res, 405, { error: 'method' });
      saveDb();
      return send(res, 200, { ok: true });
    }
    if (p === '/api/blob' && req.method === 'POST') {
      const buf = await readBody(req);
      const id = crypto.createHash('sha256').update(buf).digest('hex').slice(0, 32);
      fs.writeFileSync(path.join(BLOBS, id), buf);
      const type = req.headers['content-type'] || 'application/octet-stream';
      return send(res, 200, { id, url: '/_blob/' + id, sizeBytes: buf.length, contentType: type });
    }
    if (p.startsWith('/api/blob/') && req.method === 'DELETE') {
      const id = p.slice(10);
      if (/^[0-9a-f]{32}$/.test(id)) fs.rmSync(path.join(BLOBS, id), { force: true });
      return send(res, 200, { ok: true });
    }
    if (p.startsWith('/_blob/')) {
      const f = blobFile(p.slice(7));
      if (!f) return send(res, 404, { error: 'not found' });
      return sendFile(res, f);
    }
    // The hub page and its scripts.
    const rel = p === '/' ? 'index.html' : p.slice(1);
    if (rel.includes('..')) return send(res, 400, { error: 'bad path' });
    if (rel === 'index.html') {
      // The page is written as an artifact body; give it a full document here.
      const body = fs.readFileSync(path.join(HUB, 'index.html'), 'utf8');
      return send(res, 200, `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body>${body}</body></html>`, 'text/html; charset=utf-8');
    }
    return sendFile(res, path.join(HUB, rel));
  } catch (e) {
    return send(res, e.code === 413 ? 413 : 500, { error: String(e.message || e) });
  }
});

server.listen(PORT, '127.0.0.1', () => console.log(`Asset Hub: http://localhost:${PORT}  (${assets.length} assets, data in ${path.relative(REPO, DB)})`));
