# ScreenShell

The full-screen frame for loading, main menu, lobby, results and pause: a title row, a content region and a footer of input prompts.

**Consumer provides:** eyebrow (mode or context), title, one dominant action per region, footer prompts built from the player's current bindings.

- Inset content by `space-12` (48px at 1920x1080); keep the same inset across screens so titles never jump.
- Title in `page-title` (Archivo expanded). The main menu replaces it with the logo lockup once logo masters exist.
- One `Button--primary` per screen region. Secondary actions are ghost buttons.
- Footer prompts show the binding for the device in use: keyboard keycaps, or controller face buttons once a pad sends input.
- Back closes one layer and restores focus to the control that opened it.
- Reflow, don't shrink: under 1280px wide, stack the content region and keep body text at 18px.
