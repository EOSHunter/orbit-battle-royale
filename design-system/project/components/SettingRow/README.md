# SettingRow

One setting: a label and optional help on the left, its control in an aligned right column. Rows stack into a continuous list with hairline `border` rules.

**Consumer provides:** label, optional help text (one sentence, `supporting` style), one control (Switch, Slider, Select, stepper, BindingCapture), and `is-modified` when the value differs from the default.

- Minimum height `row-min-height` (72px); padding `space-3` / `space-6`.
- The whole row highlights `surface-raised` on hover and when its control has focus; the row is the controller navigation target.
- Disabled rows say why in the help text ("Not supported by this browser").
- Under 720px wide the control drops below the label.
- Never wrap a single row in its own card.
