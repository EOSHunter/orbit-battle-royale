// Ringfall, drawn procedurally. Stand-in art for the prototype until production
// loading/menu art exists. Illustration colors live here, not in the UI tokens.
(function () {
  const ART = {
    skyTop: '#05070f', skyMid: '#141a35', skyLow: '#3a2d56', haze: '#6b5a8e',
    ringLit: [236, 226, 255], ringShade: [150, 140, 200],
    planet: '#2a2350', planetLit: '#9c8bd6',
    ridgeFar: '#2b3150', ridgeMid: '#1a1f36', ridgeNear: '#0d1120',
    lake: '#3fb8c4', grass: '#5d7a74', grassFar: '#40566a',
    amber: '#ffb45c', lume: '#7ef0e0', lumeViolet: '#b49cff'
  };

  // Periodic 1D noise: integer-frequency sines, so it wraps every 360 degrees.
  function ridgeFn(seed, freqs) {
    const parts = freqs.map((f, i) => ({ f, a: 1 / (i + 1.2), p: Math.sin(seed * 97.3 + i * 13.1) * 10 }));
    const norm = parts.reduce((s, p) => s + p.a, 0);
    return deg => {
      const r = deg * Math.PI / 180;
      let v = 0;
      for (const p of parts) v += p.a * Math.sin(p.f * r + p.p);
      return v / norm; // -1..1
    };
  }
  const R = {
    far: ridgeFn(1, [2, 3, 7, 13, 29]),
    mid: ridgeFn(2, [3, 5, 11, 23, 41]),
    near: ridgeFn(3, [4, 9, 17, 37, 61])
  };

  function rng(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; }

  function fitCanvas(c) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = c.clientWidth, h = c.clientHeight;
    if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) {
      c.width = Math.round(w * dpr); c.height = Math.round(h * dpr);
    }
    const ctx = c.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx, w, h };
  }

  function sky(ctx, w, h, horizon) {
    const g = ctx.createLinearGradient(0, 0, 0, horizon);
    g.addColorStop(0, ART.skyTop); g.addColorStop(0.55, ART.skyMid); g.addColorStop(1, ART.skyLow);
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, horizon + 2);
    const r = rng(7);
    for (let i = 0; i < 260; i++) {
      const x = r() * w, y = r() * horizon * 0.9, s = r();
      ctx.fillStyle = `rgba(230,236,255,${0.15 + s * 0.6 * (1 - y / horizon)})`;
      ctx.fillRect(x, y, s > 0.95 ? 2 : 1, s > 0.95 ? 2 : 1);
    }
  }

  // The planet's rings: a tilted, very wide band of ringlets with a gap and a shadowed span.
  function rings(ctx, cx, cy, rx, tilt, alpha) {
    ctx.save();
    ctx.translate(cx, cy); ctx.rotate(tilt);
    const bands = [[1.0, 0.012, 0.55], [0.975, 0.02, 0.85], [0.94, 0.006, 0.4], [0.915, 0.03, 0.95], [0.87, 0.012, 0.6], [0.84, 0.004, 0.3], [0.8, 0.025, 0.7]];
    for (const [k, thick, a] of bands) {
      const r1 = rx * k;
      const grad = ctx.createLinearGradient(-r1, 0, r1, 0);
      const L = ART.ringLit, S = ART.ringShade;
      grad.addColorStop(0, `rgba(${S},${a * 0.15 * alpha})`);
      grad.addColorStop(0.35, `rgba(${L},${a * 0.55 * alpha})`);
      grad.addColorStop(0.6, `rgba(${L},${a * 0.8 * alpha})`);
      grad.addColorStop(1, `rgba(${S},${a * 0.25 * alpha})`);
      ctx.strokeStyle = grad;
      ctx.lineWidth = Math.max(1.5, rx * thick * 0.5);
      ctx.beginPath(); ctx.ellipse(0, 0, r1, r1 * 0.09, 0, Math.PI, Math.PI * 2); ctx.stroke();
    }
    ctx.restore();
  }

  function ridgeLayer(ctx, w, base, amp, fn, offsetDeg, degPerPx, color, glow) {
    ctx.beginPath(); ctx.moveTo(0, base + 400);
    for (let x = 0; x <= w + 8; x += 6) {
      const v = fn(offsetDeg + x * degPerPx);
      ctx.lineTo(x, base - (v * 0.5 + 0.5) * amp);
    }
    ctx.lineTo(w, base + 400); ctx.closePath();
    ctx.fillStyle = color; ctx.fill();
    if (glow) { ctx.strokeStyle = glow; ctx.lineWidth = 1; ctx.stroke(); }
  }

  function haze(ctx, w, y, hgt, color, a) {
    const g = ctx.createLinearGradient(0, y - hgt, 0, y + hgt * 0.3);
    g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, color.replace('A', a));
    ctx.fillStyle = g; ctx.fillRect(0, y - hgt, w, hgt * 1.3);
  }

  function colonyLights(ctx, pts) {
    for (const [x, y, s] of pts) {
      const g = ctx.createRadialGradient(x, y, 0, x, y, s * 6);
      g.addColorStop(0, 'rgba(255,180,92,0.9)'); g.addColorStop(1, 'rgba(255,180,92,0)');
      ctx.fillStyle = g; ctx.fillRect(x - s * 6, y - s * 6, s * 12, s * 12);
      ctx.fillStyle = ART.amber; ctx.fillRect(x - s / 2, y - s / 2, s, s);
    }
  }

  // Wide establishing view: loading, menu, lobby, settings backgrounds.
  function vista(c, opts) {
    opts = opts || {};
    const { ctx, w, h } = fitCanvas(c);
    const horizon = h * (opts.horizon || 0.62);
    sky(ctx, w, h, horizon);
    // Veyra's moon-sized neighbour, half-set behind the ridge
    const pr = Math.max(w, h) * 0.16, px = w * (opts.planetX || 0.78), py = horizon - h * 0.2;
    const pg = ctx.createRadialGradient(px - pr * 0.4, py - pr * 0.5, pr * 0.1, px, py, pr);
    pg.addColorStop(0, ART.planetLit); pg.addColorStop(0.55, ART.planet); pg.addColorStop(1, '#120f26');
    ctx.fillStyle = pg; ctx.beginPath(); ctx.arc(px, py, pr, 0, Math.PI * 2); ctx.fill();
    rings(ctx, w * 0.5, horizon + h * 0.05, Math.max(w, h) * 1.05, -0.32, 1);
    haze(ctx, w, horizon, h * 0.35, 'rgba(107,90,142,A)', 0.55);
    const span = 140, dpp = span / w, off = opts.offset || 30;
    ridgeLayer(ctx, w, horizon + h * 0.02, h * 0.2, R.far, off, dpp, ART.ridgeFar);
    // comms dish on Crown Observatory
    const dx = w * 0.62, dy = horizon + h * 0.02 - (R.far(off + dx * dpp) * 0.5 + 0.5) * h * 0.2;
    ctx.strokeStyle = '#3a4266'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(dx, dy); ctx.lineTo(dx, dy - h * 0.05); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(dx, dy - h * 0.06, h * 0.025, h * 0.012, -0.5, 0, Math.PI * 2); ctx.stroke();
    // crater lake
    const lg = ctx.createLinearGradient(0, horizon + h * 0.03, 0, horizon + h * 0.12);
    lg.addColorStop(0, 'rgba(63,184,196,0.55)'); lg.addColorStop(1, 'rgba(30,80,110,0.2)');
    ctx.fillStyle = lg; ctx.beginPath(); ctx.ellipse(w * 0.55, horizon + h * 0.07, w * 0.32, h * 0.045, 0, 0, Math.PI * 2); ctx.fill();
    ridgeLayer(ctx, w, horizon + h * 0.14, h * 0.22, R.mid, off + 40, dpp * 1.2, ART.ridgeMid);
    colonyLights(ctx, [[w * 0.3, horizon + h * 0.06, 2], [w * 0.32, horizon + h * 0.065, 2], [w * 0.335, horizon + h * 0.058, 3], [w * 0.71, horizon + h * 0.09, 2], [w * 0.735, horizon + h * 0.088, 2]]);
    ridgeLayer(ctx, w, h * 1.02, h * 0.3, R.near, off + 90, dpp * 1.6, ART.ridgeNear);
    // luminous vegetation in the foreground
    const r = rng(11);
    for (let i = 0; i < 70; i++) {
      const x = r() * w, y = h * (0.86 + r() * 0.14), s = 1 + r() * 2.5;
      ctx.fillStyle = r() > 0.6 ? 'rgba(180,156,255,0.7)' : 'rgba(126,240,224,0.75)';
      ctx.beginPath(); ctx.arc(x, y, s, 0, Math.PI * 2); ctx.fill();
    }
  }

  // First-person match view. heading in degrees; fov in degrees.
  function firstPerson(c, s) {
    const { ctx, w, h } = fitCanvas(c);
    const horizon = h * 0.52, dpp = s.fov / w;
    const left = s.heading - s.fov / 2;
    const proj = b => { let d = ((b - s.heading + 540) % 360) - 180; return { x: w / 2 + d / dpp, d }; };
    sky(ctx, w, h, horizon);
    // the ring plane crosses the whole sky: draw its arc from both sides of the planet
    for (const b of [205, 25]) { const ring = proj(b); if (Math.abs(ring.d) < 150) rings(ctx, ring.x, horizon + h * 0.12, w * 1.6, b === 25 ? 0.16 : -0.16, 1); }
    const moon = proj(120);
    if (Math.abs(moon.d) < s.fov) { ctx.fillStyle = '#b8a8ee'; ctx.beginPath(); ctx.arc(moon.x, horizon - h * 0.3, h * 0.03, 0, Math.PI * 2); ctx.fill(); }
    haze(ctx, w, horizon, h * 0.3, 'rgba(107,90,142,A)', 0.5);
    ridgeLayer(ctx, w, horizon + 2, h * 0.16, R.far, left, dpp, ART.ridgeFar);
    ridgeLayer(ctx, w, horizon + h * 0.03, h * 0.08, R.mid, left * 1.5, dpp * 1.5, '#273a4e');
    // grassland
    const gg = ctx.createLinearGradient(0, horizon, 0, h);
    gg.addColorStop(0, ART.grassFar); gg.addColorStop(0.25, '#4f6a6c'); gg.addColorStop(1, ART.grass);
    ctx.fillStyle = gg; ctx.fillRect(0, horizon + h * 0.03, w, h);
    // colony structure at bearing 30
    const col = proj(30);
    if (Math.abs(col.d) < s.fov) {
      const bx = col.x, by = horizon + h * 0.035;
      ctx.fillStyle = '#1c2436'; ctx.fillRect(bx - 60, by - 46, 120, 46); ctx.fillRect(bx + 30, by - 90, 16, 90);
      ctx.fillStyle = '#2b3550'; ctx.fillRect(bx - 66, by - 50, 132, 6);
      colonyLights(ctx, [[bx - 40, by - 30, 3], [bx, by - 30, 3], [bx + 38, by - 86, 3]]);
    }
    // ground rows for depth
    ctx.strokeStyle = 'rgba(20,30,40,0.25)'; ctx.lineWidth = 1;
    for (let i = 1; i < 14; i++) { const y = horizon + h * 0.03 + Math.pow(i / 14, 2.2) * h * 0.5; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
    // bots: dark silhouettes with amber visors, nearest last
    const bots = s.bots.filter(b => b.alive).map(b => ({ ...b, p: proj(b.bearing) })).sort((a, b) => b.dist - a.dist);
    for (const b of bots) {
      if (Math.abs(b.p.d) > s.fov / 2 + 5) continue;
      const by = horizon + h * 0.03 + (h * 0.5) * (6 / b.dist), bh = h * 4.5 / b.dist;
      const bw = bh * 0.36;
      ctx.fillStyle = b.flash > 0 ? '#ffffff' : '#141a2a';
      ctx.beginPath(); ctx.roundRect(b.p.x - bw / 2, by - bh, bw, bh * 0.62, bw * 0.3); ctx.fill();
      ctx.beginPath(); ctx.arc(b.p.x, by - bh - bw * 0.25, bw * 0.38, 0, Math.PI * 2); ctx.fill();
      ctx.fillRect(b.p.x - bw * 0.35, by - bh * 0.4, bw * 0.25, bh * 0.4); ctx.fillRect(b.p.x + bw * 0.1, by - bh * 0.4, bw * 0.25, bh * 0.4);
      ctx.fillStyle = ART.amber; ctx.fillRect(b.p.x - bw * 0.28, by - bh - bw * 0.32, bw * 0.56, Math.max(2, bw * 0.12));
      b.screen = { x: b.p.x, y: by - bh * 0.6, r: bw };
      const src = s.bots.find(o => o.id === b.id); src.screen = b.screen;
    }
    // luminous plants near the camera, parallaxing fastest
    const r = rng(5);
    for (let i = 0; i < 40; i++) {
      const bearing = r() * 360, dist = 0.2 + r() * 0.8, p = proj(bearing);
      if (Math.abs(p.d) > s.fov / 2) continue;
      const y = h * (0.72 + dist * 0.28), sz = 2 + dist * 5;
      ctx.fillStyle = r() > 0.5 ? 'rgba(126,240,224,0.8)' : 'rgba(180,156,255,0.75)';
      ctx.beginPath(); ctx.arc(p.x, y, sz, 0, Math.PI * 2); ctx.fill();
    }
    // vignette
    const v = ctx.createRadialGradient(w / 2, h / 2, h * 0.4, w / 2, h / 2, Math.max(w, h) * 0.75);
    v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(5,7,15,0.55)');
    ctx.fillStyle = v; ctx.fillRect(0, 0, w, h);
  }

  // Ringfall map. view: {cx, cy, zoom} in map units (0..1); state: storm, safe, player, marker
  const LOCATIONS = [
    { id: 'crown', name: 'Crown Observatory', x: 0.30, y: 0.20 },
    { id: 'anchor', name: 'Anchorport', x: 0.78, y: 0.30 },
    { id: 'glass', name: 'Glass Basin', x: 0.52, y: 0.50 },
    { id: 'bloom', name: 'Bloomwild', x: 0.22, y: 0.62 },
    { id: 'relay', name: 'Relay Nine', x: 0.74, y: 0.70 },
    { id: 'spine', name: 'The Spine', x: 0.50, y: 0.18 },
    { id: 'hollow', name: 'Hollow Array', x: 0.42, y: 0.84 }
  ];
  function drawMap(c, view, st, opts) {
    opts = opts || {};
    const { ctx, w, h } = fitCanvas(c);
    const size = Math.min(w, h) * view.zoom;
    const ox = w / 2 - view.cx * size, oy = h / 2 - view.cy * size;
    const M = (x, y) => [ox + x * size, oy + y * size];
    ctx.fillStyle = '#0a1426'; ctx.fillRect(0, 0, w, h);
    // ocean texture
    const r = rng(3);
    ctx.fillStyle = 'rgba(112,214,255,0.04)';
    for (let i = 0; i < 300; i++) { const [x, y] = M(r() * 1.4 - 0.2, r() * 1.4 - 0.2); ctx.fillRect(x, y, 2, 2); }
    // landmass: noisy blob
    const land = ridgeFn(9, [3, 5, 8, 13]);
    ctx.beginPath();
    for (let a = 0; a <= 360; a += 3) {
      const rr = 0.43 + land(a) * 0.05;
      const [x, y] = M(0.5 + Math.cos(a * Math.PI / 180) * rr, 0.5 + Math.sin(a * Math.PI / 180) * rr);
      a === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.closePath();
    const lgr = ctx.createRadialGradient(...M(0.5, 0.5), 0, ...M(0.5, 0.5), size * 0.48);
    lgr.addColorStop(0, '#47615e'); lgr.addColorStop(0.7, '#36504f'); lgr.addColorStop(1, '#2a3f44');
    ctx.fillStyle = lgr; ctx.fill();
    ctx.strokeStyle = 'rgba(126,240,224,0.35)'; ctx.lineWidth = 2; ctx.stroke();
    // basalt highlands
    const hills = [[0.3, 0.22, 0.12], [0.52, 0.17, 0.08], [0.8, 0.62, 0.08], [0.2, 0.45, 0.07]];
    for (const [x, y, rr] of hills) { const g = ctx.createRadialGradient(...M(x, y), 0, ...M(x, y), rr * size); g.addColorStop(0, 'rgba(20,24,40,0.85)'); g.addColorStop(1, 'rgba(20,24,40,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(...M(x, y), rr * size, 0, Math.PI * 2); ctx.fill(); }
    // Bloomwild glow
    const bg = ctx.createRadialGradient(...M(0.22, 0.64), 0, ...M(0.22, 0.64), 0.1 * size); bg.addColorStop(0, 'rgba(180,156,255,0.35)'); bg.addColorStop(1, 'rgba(180,156,255,0)');
    ctx.fillStyle = bg; ctx.beginPath(); ctx.arc(...M(0.22, 0.64), 0.1 * size, 0, Math.PI * 2); ctx.fill();
    // crater lake + islands
    const lake = ridgeFn(4, [3, 4, 7]);
    ctx.beginPath();
    for (let a = 0; a <= 360; a += 4) { const rr = 0.13 + lake(a) * 0.02; const [x, y] = M(0.52 + Math.cos(a * Math.PI / 180) * rr, 0.5 + Math.sin(a * Math.PI / 180) * rr * 0.85); a === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
    ctx.closePath(); ctx.fillStyle = '#2a9cb0'; ctx.fill(); ctx.strokeStyle = 'rgba(200,250,255,0.5)'; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.fillStyle = '#1c2236';
    for (const [x, y, rr] of [[0.5, 0.48, 0.018], [0.56, 0.53, 0.012], [0.47, 0.54, 0.009]]) { ctx.beginPath(); ctx.arc(...M(x, y), rr * size, 0, Math.PI * 2); ctx.fill(); }
    // roads
    ctx.strokeStyle = 'rgba(232,220,190,0.35)'; ctx.lineWidth = 2; ctx.setLineDash([]);
    const road = [[0.3, 0.2], [0.36, 0.34], [0.33, 0.5], [0.22, 0.62], [0.32, 0.76], [0.42, 0.84], [0.6, 0.8], [0.74, 0.7], [0.8, 0.5], [0.78, 0.3], [0.62, 0.22], [0.5, 0.18], [0.3, 0.2]];
    ctx.beginPath(); road.forEach(([x, y], i) => i ? ctx.lineTo(...M(x, y)) : ctx.moveTo(...M(x, y))); ctx.stroke();
    // anchorport pads
    ctx.fillStyle = 'rgba(255,180,92,0.6)';
    for (let i = 0; i < 6; i++) { const [x, y] = M(0.75 + (i % 3) * 0.025, 0.28 + Math.floor(i / 3) * 0.03); ctx.fillRect(x, y, size * 0.016, size * 0.02); }
    // storm: violet outside the current circle
    if (st.storm) {
      ctx.save();
      ctx.beginPath(); ctx.rect(0, 0, w, h);
      ctx.arc(...M(st.storm.x, st.storm.y), st.storm.r * size, 0, Math.PI * 2, true);
      ctx.fillStyle = 'rgba(169,139,255,0.32)'; ctx.fill('evenodd');
      ctx.strokeStyle = '#a98bff'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(...M(st.storm.x, st.storm.y), st.storm.r * size, 0, Math.PI * 2); ctx.stroke();
      ctx.restore();
    }
    if (st.safe) {
      ctx.strokeStyle = '#f3f5fa'; ctx.lineWidth = 2; ctx.setLineDash([]);
      ctx.beginPath(); ctx.arc(...M(st.safe.x, st.safe.y), st.safe.r * size, 0, Math.PI * 2); ctx.stroke();
    }
    // labels
    if (!opts.noLabels) {
      ctx.font = `600 ${Math.max(12, Math.min(16, size * 0.022))}px "IBM Plex Sans", system-ui, sans-serif`;
      for (const l of LOCATIONS) {
        const [x, y] = M(l.x, l.y);
        const hot = opts.hover === l.id || opts.selected === l.id;
        ctx.fillStyle = hot ? '#c5f277' : '#f3f5fa';
        ctx.beginPath(); ctx.arc(x, y, hot ? 6 : 4, 0, Math.PI * 2); ctx.fill();
        const tw = ctx.measureText(l.name).width;
        ctx.fillStyle = 'rgba(11,16,27,0.78)'; ctx.fillRect(x + 10, y - 12, tw + 12, 24);
        ctx.fillStyle = hot ? '#c5f277' : '#f3f5fa'; ctx.fillText(l.name, x + 16, y + 5);
      }
    }
    // marker
    if (st.marker) {
      const [x, y] = M(st.marker.x, st.marker.y);
      ctx.fillStyle = '#c5f277';
      ctx.beginPath(); ctx.moveTo(x, y); ctx.arc(x, y - 16, 8, Math.PI * 0.8, Math.PI * 0.2); ctx.closePath(); ctx.fill();
      ctx.fillStyle = '#0b101b'; ctx.beginPath(); ctx.arc(x, y - 16, 3, 0, Math.PI * 2); ctx.fill();
    }
    // player arrow
    if (st.player) {
      const [x, y] = M(st.player.x, st.player.y);
      ctx.save(); ctx.translate(x, y); ctx.rotate(st.player.heading * Math.PI / 180);
      ctx.fillStyle = '#f3f5fa'; ctx.strokeStyle = '#0b101b'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(0, -10); ctx.lineTo(7, 8); ctx.lineTo(0, 4); ctx.lineTo(-7, 8); ctx.closePath(); ctx.stroke(); ctx.fill();
      ctx.restore();
    }
    return { size, ox, oy };
  }

  window.Ringfall = { vista, firstPerson, drawMap, LOCATIONS, fitCanvas };
})();
