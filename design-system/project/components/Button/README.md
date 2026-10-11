# Button

Triggers one action. Labels are verbs that say exactly what happens: "Play", "Start match", "Leave match", "Retry download".

**Consumer provides:** label, variant (`or-btn--primary`, default, `or-btn--ghost`, `or-btn--danger`), and an `is-pending` class while an async action runs.

- One `--primary` per task region, at `primary-height` (56px), `accent` fill with `text-on-accent`.
- Default buttons are `surface` with a `border-control` outline at `control-height` (48px).
- `--danger` for destructive or match-ending actions; always separated from Resume / Cancel by space or position.
- Focus is a 2px `focus` (white) ring offset 2px, so focus and the accent-filled selection never look alike.
- Pending keeps the button's width and swaps in a spinner; success and failure report through Toast, and failure offers Retry.
- Do not put icons alone in a button without a visible label, except the close button in a Dialog title row.
