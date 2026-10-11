# SettingsShell

One full-screen shell for every settings category: page title, top category tabs, local section tabs, then continuous SettingRows.

**Consumer provides:** the six categories in this order — Mouse & keyboard, Controller, Audio, Video, Accessibility, Gameplay — the local sections of the active category, and its rows.

- Category tabs switch with the bumpers / Q and E; show those keycaps at the ends of the tab bar.
- Settings apply immediately and persist on this device. There is no Save button; confirm with a `Toast--success` only when persistence fails or succeeds after a delay.
- "Reset <category>" is a `Button--danger` in the title row and opens a Dialog naming exactly what resets.
- Constrain the content to 1120px wide; rows run edge to edge inside it. No card around each setting.
- Help text collapses below the label on narrow displays (SettingRow handles this).
