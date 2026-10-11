# Performance baseline

First measurements of the Godot web build, taken 2026-10-11 on the movement playground (greybox only: no production art, audio, combat or bots). Later phases are held against these numbers and against the target hardware once it is chosen.

## How to measure

- **Benchmark:** visits four fixed views of the playground for 3 seconds each (spawn lane, tower field, the course from the 50 m tower, and a tethered swing across the gap) and records frame time, main-thread time, draw calls and triangles.
  - Desktop: `godot --path game --resolution 1920x1080 -- --bench` (vsync off; prints a `BENCH {...}` line and quits).
  - Browser: open the web build with `#bench` at the end of the URL; results land in `window.orbitPerf.bench` (and the page-load time in `window.orbitPerf.firstFrame`).
- **Live readout:** press F3 in the game for frame rate, frame time, main-thread time, draw calls and triangles.
- **Download size:** export the web build and compress the files with gzip and Brotli (CI reports the gzip size in each run's summary).

## Machine used

Not the target hardware: a fast desktop, so these numbers are a floor, not a promise.

| | |
|---|---|
| CPU | Intel Core i5-14600KF, 14 cores / 20 threads |
| GPU | NVIDIA GeForce RTX 4070 (the browser renders through ANGLE on Direct3D 11) |
| Memory | 32 GB |
| Display | 240 Hz |
| Browser | Chromium-based (the Claude desktop app's browser pane), 1600×900 |

## Download size (web build, Godot 4.7.2, single-threaded)

| File | Raw | gzip -9 | Brotli 11 |
|---|---:|---:|---:|
| `index.wasm` (engine) | 37.68 MB | 9.68 MB | 6.77 MB |
| `index.pck` (game data) | 0.10 MB | 0.07 MB | 0.06 MB |
| `index.js` | 0.27 MB | 0.07 MB | 0.06 MB |
| **Total** | **38.1 MB** | **9.8 MB** | **6.9 MB** |

The engine dominates. Serving with Brotli makes the first download about 6.9 MB: roughly 0.6 s at 100 Mbps, 2.2 s at 25 Mbps, 5.5 s at 10 Mbps, before any game content. Production art will grow `index.pck` and should stream in after the menu, not block it.

## Load time

| Measure | Result |
|---|---:|
| Page load to first rendered frame (local server, no network delay) | 1.86 s |
| Engine start to first frame (web) | 0.59 s |
| Engine start to first frame (desktop) | 0.83 s |

Over a real connection, add the download time above.

## Frame time

| View | Desktop, vsync off | Browser |
|---|---|---|
| Spawn lane | 0.55 ms avg (1,818 fps), 0.77 ms p95 | 4.17 ms, locked to 240 Hz, no dropped frames |
| Tower field | 0.63 ms (1,599 fps), 0.87 ms p95 | 4.17 ms, locked, none dropped |
| Course from the 50 m tower | 0.54 ms (1,860 fps), 0.74 ms p95 | 4.17 ms, locked, none dropped |
| Swing gap, tethered | 0.62 ms (1,622 fps), 0.82 ms p95 | 4.17 ms, locked, none dropped |

| View | Browser main-thread time | Draw calls | Triangles |
|---|---:|---:|---:|
| Spawn lane | 4.35 ms | 150 | 10.2k |
| Tower field | 3.76 ms | 104 | 9.6k |
| Course from the 50 m tower | 3.99 ms | 127 | 5.7k |
| Swing gap, tethered | 3.62 ms | 84 | 9.5k |

Browsers cap the frame rate at the display refresh, so browser frame time only shows that no frames were missed. The browser's main-thread time (about 3.6–4.4 ms) is the useful number: about a quarter of a 60 fps budget (16.7 ms) is already in use on a fast machine with an empty greybox level. WebAssembly runs single-threaded here, and that main-thread cost is what will grow with bots, physics and effects.

## What this tells us

- The greybox is cheap: about 100–150 draw calls and 10k triangles per view.
- The download is acceptable today (6.9 MB) if the host serves Brotli; without compression it is 38 MB.
- Main-thread time in the browser is already noticeable on fast hardware, so 59 bots will need careful budgeting (simple bot logic at a lower tick rate, pooled effects, few physics bodies).
- GPU time isn't measured: the Compatibility renderer doesn't report it in the browser.

## Still to measure

- The same benchmark on the target hardware, once it is chosen (Phase 0 decision).
- Firefox and Safari, and a 60 Hz display, where a missed frame is easier to see.
- Load time over a throttled connection.
- Memory use in the browser (the engine doesn't report it on the web; use the browser's task manager).
