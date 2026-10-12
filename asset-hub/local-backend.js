// Local backend for the Asset Hub when it runs as its own web page
// (asset-hub/server.js). Provides the same window.claude.use() calls the hub
// uses as a claude.ai artifact (db, assets, user), backed by the repo through
// the server's /api routes. Inside the artifact, the platform's own runtime is
// used instead and this file does nothing.
(function () {
  if (location.hostname.endsWith('claudeusercontent.com') || location.hostname.endsWith('claude.ai')) return;

  const api = async (p, opts) => {
    const r = await fetch('/api/' + p, opts);
    if (!r.ok) throw Object.assign(new Error(r.statusText), { code: r.status === 413 ? 'too_large' : 'failed' });
    return r.json();
  };
  const json = (method, body) => ({ method, headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });

  let docs = [];
  const listeners = new Set();
  const notify = () => listeners.forEach(cb => cb({ docs: docs.map(d => ({ id: d.id, data: () => d })) }));
  const refresh = async () => { docs = await api('assets'); notify(); };
  let last = '';
  // Pick up edits made elsewhere (another tab, a git pull) every few seconds.
  setInterval(async () => {
    try { const next = await api('assets'); const sig = JSON.stringify(next); if (sig !== last) { last = sig; docs = next; notify(); } } catch (e) { /* server stopped */ }
  }, 4000);

  const doc = id => ({
    update: async patch => { await api('assets/' + encodeURIComponent(id), json('PATCH', patch)); await refresh(); },
    set: async data => { await api('assets/' + encodeURIComponent(id), json('PUT', data)); await refresh(); },
    delete: async () => { await api('assets/' + encodeURIComponent(id), { method: 'DELETE' }); await refresh(); },
  });
  const db = {
    collection: () => ({
      doc,
      onSnapshot(cb, onError) {
        listeners.add(cb);
        refresh().catch(e => onError && onError(e));
        return () => listeners.delete(cb);
      },
    }),
  };
  const assets = {
    upload: (blob, opts) => api('blob', { method: 'POST', headers: { 'content-type': (opts && opts.type) || blob.type || 'application/octet-stream' }, body: blob }),
    delete: id => (String(id).startsWith('repo/') ? Promise.resolve() : api('blob/' + encodeURIComponent(id), { method: 'DELETE' })),
  };
  const user = {
    id: async () => 'local',
    me: async () => ({ id: 'local', name: 'You' }),
    can: async () => true,
    isOwner: () => true,
    canEdit: () => true,
    profiles: async ids => Object.fromEntries((ids || []).map(i => [i, { name: i === 'local' ? 'You' : '' }])),
  };

  let online = null;
  const ping = () => (online ??= fetch('/api/ping').then(r => r.ok, () => false));
  window.claude = { use: async name => ((await ping()) ? { db, assets, user }[name] || null : null) };
})();
