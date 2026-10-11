# Announcer callouts

No audio here yet. These lines need a recorded (or licensed) voice performance. They were not
synthesised because a procedural placeholder voice would not be good enough to ship. Whether the game
has an announcer at all is still an open decision (see `docs/asset-list.md`). Subtitles are planned
either way.

## Lines to record

| File | Line | Notes |
|---|---|---|
| `storm-closing.wav` | "Storm closing." | Calm and urgent. Plays with the storm-closing stinger. |
| `survivors-remaining-<n>.wav` | "N survivors remaining." | Record the counts the game announces, e.g. 50, 25, 10, 5, 3, 2. Alternatively record the numbers and "survivors remaining" separately and join them at runtime. |
| `victory.wav` | "Victory." | Warm and triumphant. Plays over the victory stinger. |

## Delivery spec

- WAV, 48 kHz, 16-bit, mono, dry (no reverb). Godot adds space per bus.
- Peaks around -1 dBFS, consistent loudness across lines, about 50 ms of silence at the head and 200 ms at the tail.
- Record 2–3 takes per line so a director can pick one.
