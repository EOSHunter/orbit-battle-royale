# Asset pipeline

How an asset gets from concept to the game. Every asset has an id in the [asset list](asset-list.md) and the Asset Hub (for example `ar-7-wayfarer`); use that id for file names everywhere.

```text
concept art          codex/concepts/…            reference only
editable source      art/<category>/<id>.blend   Blender, Krita, audio sessions
game-ready export    game/assets/<kind>/<category>/<id>.glb   what Godot imports (res://assets/…)
preview + tracking   Asset Hub                   attach the export, tick deliverables
```

The exact paths for each asset are listed in the asset list and on its Asset Hub page.

## Folders

| Folder | What goes there | Imported by Godot |
|---|---|---|
| `art/` | Blender files, texture sources (`.psd`, `.kra`, `.spp`), audio masters | No (outside the project) |
| `game/assets/models/` | Exported `.glb` models: characters, weapons, items, vehicles, environment | Yes |
| `game/assets/animations/` | Animation libraries as `.glb` | Yes |
| `game/assets/vfx/` | Effect meshes and textures | Yes |
| `game/assets/audio/` | Game-ready sounds, one folder per audio asset | Yes |
| `game/assets/ui/`, `game/assets/art/` | Icons, logo masters, map illustration, key art | Yes |
| `codex/` | Concept art and exploration | No |

## Git LFS

Binary files go through Git LFS automatically: `.blend`, `.glb`, `.fbx`, `.bin`, audio, fonts, `.psd`/`.kra`/`.exr`, and textures inside `art/` and `game/assets/`. The rules are in [.gitattributes](../.gitattributes). Run `git lfs install` once per machine before committing art.

- Text formats stay in normal Git: `.gltf`, `.svg`, `.tscn`, `.tres`, `.import`.
- Blender backups (`.blend1`, `.blend2`) are ignored.
- GitHub's free LFS storage and bandwidth are limited. Check usage under your GitHub billing settings once real assets arrive, and avoid committing many revisions of large textures.
- CI does not fetch LFS files yet. When the game starts using real assets, the workflow will need `lfs: true` on checkout, which counts against LFS bandwidth.

## Modeling in Blender

- **Scale:** 1 Blender unit = 1 meter. Apply scale and rotation (Ctrl+A) before export. The player is 1.8 m tall.
- **Facing:** models face −Y in Blender (toward the Front view). The glTF exporter converts this to +Z, which is Godot's model front.
- **Origins:** props and characters at the base center on the ground; weapons at the grip; vehicles at the center of the wheelbase on the ground.
- **Budgets:** follow the triangle and texture budgets in the asset list. Godot generates distance LODs automatically on import, so author one full-detail mesh unless a hand-made LOD is noted.
- **Collision** uses Godot's import name hints on objects:

| Suffix | Result in Godot |
|---|---|
| `-col` | Mesh plus a static collision copy of it |
| `-colonly` | Collision only, mesh hidden (use simple boxes for walls and floors) |
| `-convcolonly` | Convex collision only (good for props) |
| `-noimp` | Not imported (helpers, reference meshes) |

- **Hookable surfaces:** the Tethercaster hooks the `grappable` physics layer. Mark hookable collision in Blender with the custom property `grapple = 1` on the collision object; the import script will put it on that layer when the first production level is set up.
- **Materials:** one material per surface type; PBR metal/roughness. Use the palette from the concept art: graphite and navy armor, ivory panels, pale lime markings, amber lights.

## Exporting glTF from Blender

File → Export → glTF 2.0, with:

- Format: **glTF Binary (.glb)**
- Include: selected objects or the collection for this asset
- Transform: **+Y Up** on
- Mesh: Apply Modifiers on; UVs, normals and tangents on
- Materials: Export; Images: Automatic
- Compression: **off** (Godot doesn't support Draco)
- Animation: export actions as separate clips; name clips plainly (`idle`, `walk`, `fire`, `reload`). Add `-loop` to clip names that should loop.

Save the export to the asset's `game/assets/…` path, open Godot so it imports, then attach the same `.glb` to the asset in the Asset Hub for review.

## Textures

- Power-of-two sizes, 2048² maximum unless the asset list says otherwise.
- Godot compresses textures for the GPU on import. The web export currently targets desktop browsers (S3TC/BPTC). Supporting phone browsers would need ETC2 as well, which is a decision for later.

## Audio

- Record and edit at 48 kHz, 24-bit WAV. Keep masters in `art/<category>/<id>/`.
- **Short sound effects** (weapons, impacts, UI, footsteps): export WAV 48 kHz, mono for anything positioned in the world. Godot compresses them with QOA on import.
- **Loops and music** (engines, ambience, storm, music): export Ogg Vorbis 48 kHz. Loops must be seamless; set the loop flag in Godot's import settings.
- Peak at about −1 dBFS. Mix levels relative to each other in-engine, not by baking volume into files.
- Name variations with a numeric suffix: `fire-close-01.wav`, `fire-close-02.wav`.

## Checklist for a finished asset

- [ ] Named with its asset id, exported to its `game/assets/…` path, source saved in `art/`
- [ ] Within budget (the Asset Hub viewer shows triangles and size in meters)
- [ ] Correct scale, facing and origin
- [ ] Collision set up where needed
- [ ] Imports in Godot without warnings
- [ ] Attached in the Asset Hub, deliverables ticked, stage moved to *In engine*
