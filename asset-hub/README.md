# Asset Hub

Production tracker and viewer for every Orbit Royale asset: progress by deliverable, a 3D viewer (rotate, wireframe, scale grid, triangle counts, animation clips), an audio player and an image viewer.

## Run it

```bash
node asset-hub/server.js
```

Then open http://localhost:5180. It needs Node only; nothing is installed. It listens on this computer only.

## Where things live

| What | Where |
|---|---|
| Records (stages, deliverables, notes) | `data/assets.json`, saved as you edit. Commit it to share progress. |
| Models, sounds, icons | Served straight from `game/assets/`, so the hub always shows the current exports. |
| Concept art | Served from `codex/concepts/`. |
| Thumbnails and screenshots | `data/thumbs/`, `data/shots/` |
| Files dropped onto the viewer and attached by hand | `data/blobs/` (Git LFS) |

## After adding assets

```bash
node asset-hub/sync.js
```

Re-attaches the repo's current files to every record (models with triangle and animation counts, sounds, icons, screenshots) and keeps files attached by hand. Which files belong to which record is listed at the top of `sync.js`; records not listed there use their `path` (a file or a folder).

New model thumbnails: `blender -b --factory-startup --python art/tools/render_thumbs.py` renders any that are missing into `data/thumbs/` (then run `sync.js`).

## The claude.ai artifact version

The same page also runs as a claude.ai artifact (`local-backend.js` steps aside there), but the artifact sandbox blocks the `data:` and `blob:` URLs that three.js uses to load embedded model data, so stored models can't be opened there. This standalone page is the working version.
