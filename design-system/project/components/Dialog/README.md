# Dialog

A modal decision on top of a screen or the match: confirm leave, confirm reset, failed download.

**Consumer provides:** title as a question or statement, one sentence of consequence, and two actions.

- Opens on `scrim`; panel is `surface` with `radius-panel` and `space-8` padding.
- Focus moves to the safe action first (Stay / Cancel). Back or Esc closes it and returns focus to the opener.
- The destructive action names the outcome ("Leave match", "Reset Audio"), never "OK".
- One overlay at a time; gameplay input never passes through.
