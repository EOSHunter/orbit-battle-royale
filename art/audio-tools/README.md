# Procedural audio tools

Every sound in `game/assets/audio/` (except the announcer voice, which needs recording) is synthesised
here in Python with numpy. No samples or recordings are used. The scripts use fixed seeds, so running
them again produces the same files.

## Requirements

Use Blender's bundled Python, which ships numpy. Scipy isn't needed. Run the bundled interpreter
directly (fastest):

```sh
PY="/c/Program Files/Blender Foundation/Blender 5.1/5.1/python/bin/python.exe"
"$PY" art/audio-tools/gen_weapons.py
```

or through Blender:

```sh
"/c/Program Files/Blender Foundation/Blender 5.1/blender.exe" -b --factory-startup --python-exit-code 1 \
  --python art/audio-tools/gen_weapons.py -- [args]
```

Any Python 3.10+ with numpy works too. Don't pipe scripts through stdin; always run the script files.

## Regenerating everything

Run from the repo root. Each script writes straight into `game/assets/audio/` and prints one line per file.

| Script | Writes | Optional args (after `--`) |
|---|---|---|
| `gen_weapons.py` | `weapon-audio/<weapon>-audio/` fire-close-01..03, fire-distant, reload, equip, dry-fire | weapon ids, e.g. `sr-8-longview` |
| `gen_items.py` | `item-audio/healing-item-audio/`, `grenade-audio/`, `tethercaster-audio/` | — |
| `gen_vehicles.py` | `vehicle-audio/<vehicle>-audio/`, `drop-transport/drop-transport-audio/` | `vehicles`, `drop` |
| `gen_ambience.py` | `ambience/ringfall-ambience/`, `ambience/ion-storm-audio/` | `ringfall`, `storm` |
| `gen_ui_foley.py` | `ui-audio/interface-sounds/`, `ui-audio/match-feedback-sounds/`, `foley/footsteps/` | `ui`, `feedback`, `foley` |
| `gen_music.py` | `music/main-menu-theme/`, `music/match-stingers/` | `theme`, `stingers` |
| `analyze.py` | nothing (prints a report) | a path filter, e.g. `weapon-audio` |

```sh
for s in gen_weapons gen_items gen_vehicles gen_ambience gen_ui_foley gen_music analyze; do
  "$PY" art/audio-tools/$s.py
done
```

A full run takes a few minutes on an idle machine. The music theme and ambience are the slowest.

## Modules

- `synth.py` holds the DSP core: oscillators (PolyBLEP saw and square, FM, modal banks, Karplus-Strong),
  noise (white, sloped, crackle), envelopes, RBJ biquad cascades (applied as causal IR plus FFT convolution,
  so there's no pre-ringing on transients), zero-phase spectral filters, a time-varying state-variable
  filter, synthetic reverb IRs with frequency-dependent decay, a look-ahead limiter, mastering, WAV I/O and
  analysis.
- `sfx.py` holds the sound-design building blocks: clicks, metal and glass hits, thuds, scrapes, rustles,
  whooshes, rattles, explosions, outdoor tails, and helpers for circular loops.

## Conventions

- 48 kHz, 16-bit PCM WAV. World sounds are mono. Only the music (theme and stingers) is stereo. UI is
  mono too, because stereo added nothing.
- `master()` in `synth.py` removes DC (18 Hz high-pass), fades one-shot edges, trims silent tails, then
  matches loudness within a category (maximum short-term RMS for one-shots, full RMS for loops) behind a
  -1 dBFS look-ahead limiter.
- **Loops are seamless by construction.** Loop noise is filtered circularly in the frequency domain.
  Every oscillator frequency is quantised to a whole number of cycles per loop (`qfreq`). Modulators are
  periodic, discrete events wrap around the loop end, and the reverb is a circular convolution. The
  last sample flows into the first exactly as any two neighbouring samples do. `analyze.py` checks this
  as the "seam" ratio (jump at the seam divided by the RMS sample-to-sample step; about 1 is ideal, and
  anything over 4 is flagged).
- Files that repeat often (gunshots, impacts, bounces, footsteps, hit markers, thunder) get numbered
  variations (`-01`, `-02`, ...) built from different seeds and small pitch offsets.

## Tuning

Each sound is a short recipe near the top of its script. Weapon voices live in the `WEAPONS` table in
`gen_weapons.py`, and engine states in the `VEH` table in `gen_vehicles.py`. Change a value, re-run that
script, then run `analyze.py` and listen in Godot.
