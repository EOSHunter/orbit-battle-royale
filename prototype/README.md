# Orbit Royale UI prototype

A clickable prototype of the screen flow: loading → main menu → lobby → deployment → match HUD (inventory, map, pause) → results, plus settings and credits. It is built on the design system in `design-system/` and uses procedural placeholder art.

## Run it

```bash
node prototype/serve.js
```

Then open http://localhost:5173. Press <kbd>`</kbd> (or the Prototype button) to jump between screens and trigger match events such as hits from a direction, low health, storm warnings, elimination or a win.

After you change `design-system/project/tokens.json` or `components/bundle.css`, rebuild the prototype's copy:

```bash
node design-system/scripts/build-prototype-css.js
```

## What is placeholder

Magazine sizes, damage, loot, storm timings and bot behavior are stand-ins, not balance decisions. Art is drawn in the browser until production assets exist. There is no audio. Pause behavior in solo bot mode is undecided: the prototype defaults to "match continues", with a toggle in the prototype controls.
