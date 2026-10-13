# Codex workspace

Work produced in the Orbit Royale Codex conversation lives here so Claude and other collaborators can find the concept art, prompts, and original planning material together.

## Start here

- [Matching sci-fi UI v0.2](concepts/ui-v0.2/index.html): 28 screens spanning settings, menus, dialogs, HUD and inventory. [Claude handoff notes](concepts/ui-v0.2/README.md).
- [Main menu v0.2 — sci-fi UI exploration](concepts/main-menu-v0.2/README.md): alternate typography, panels and selected states on a plain background.
- [Menu and settings concept gallery](concepts/menus-v0.1/index.html): 26 screens based on the Kong prototype's Hybrid structure, in Orbit Royale's own style. [Review notes](concepts/menus-v0.1/README.md).
- [Gameplay and inventory concepts](concepts/gameplay-v0.1/README.md): first-person POV with HUD and held rifle, plus the five-slot inventory overlay.
- [Latest concept gallery — v0.2](concepts/v0.2/index.html): 48 selected concepts covering characters, equipment, vehicles, transport, Ringfall, effects, branding, and UI.
- [Concept inventory](concepts/v0.2/manifest.json): selected image paths plus retained first drafts.
- [Original supplied concept list](concepts/v0.2/source-list.txt) and [generation prompts](concepts/v0.2/prompts.md).
- [Art review notes](concepts/v0.2/README.md): scope, refinements, and production limitations.
- [Earlier v0.1 sheets](concepts/v0.1/README.md): four category sheets retained for comparison.

## Original planning snapshots

The documents below preserve the initial Codex-authored planning from commit `f281158`. They are historical snapshots, not copies of the latest implementation decisions. In particular, the original handoff predates the Godot trial and Claude's prototype work.

- [Game concept](documents/game-concept.md).
- [Design system v0.1](documents/design-system.md).
- [Initial Claude handoff](documents/claude-handoff.md).
- [Kong reference context](documents/references/README.md).

For current shared project guidance, read [docs/game-concept.md](../docs/game-concept.md), [docs/design-system.md](../docs/design-system.md), and [docs/claude-handoff.md](../docs/claude-handoff.md). Claude's implementation work is also available in [design-system/project](../design-system/project/README.md), [prototype](../prototype/README.md), and [asset-hub](../asset-hub/index.html).

## Organization

```text
codex/
  README.md           Entry point for collaborators
  documents/          Original planning snapshots and reference material
  concepts/
    v0.1/             Four early equipment sheets
    v0.2/             Full 48-concept gallery, images, manifest, and prompts
    gameplay-v0.1/    First-person gameplay and inventory visual targets
    menus-v0.1/       Settings, menus, match flow, and confirmations
```

Keep future Codex-produced concepts, drafts, and review artifacts in clearly named folders here. Use new versions for art revisions and maintain this index. Update shared implementation files in their existing locations when the task calls for it; this folder does not replace the application structure.

Images are exploratory raster references, not final 3D models, approved vector logos, or production glyphs. Generated details do not silently approve new mechanics. No compiled builds, ZIP duplicates, credentials, or temporary scratch files are stored here.

## Viewing the gallery

GitHub displays the individual PNG files but does not render the gallery HTML as an application. After cloning/pulling the repository, open `codex/concepts/v0.2/index.html` in a browser. It uses local relative image paths and requires no build or dependencies.

The full set includes 48 selected images plus two retained first drafts. The first-generation four category sheets are separate in v0.1. All generation used the built-in image_gen tool.
