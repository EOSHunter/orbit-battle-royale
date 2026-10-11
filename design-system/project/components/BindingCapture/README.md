# BindingCapture

Rebinds one action. Each action has a primary and an alternate slot.

**Consumer provides:** action name (in the SettingRow label), current bindings, and the conflicting action when a new binding is already used.

- Activating a slot enters listening (`is-listening`): accent outline and the instruction "Press a key · Esc cancels · Del clears". Mouse buttons count.
- A conflict never silently steals: show the warning-outlined slot plus an `or-conflict` row naming the other action, with Swap and Cancel.
- Controller bindings use pad glyphs (`or-keycap--pad`).
