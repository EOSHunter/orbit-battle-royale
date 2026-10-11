# Tabs

Switches between sibling views without leaving the screen. Used for settings categories (top) and sections within a category (local).

**Consumer provides:** tab labels in a fixed order and the selected index.

- Selected tab: `text-primary` label and a 3px `accent` underline. Unselected: `text-secondary`.
- Hover lifts to `surface-raised`; focus adds the white ring. Selection and focus stay distinguishable.
- Local tabs (`or-tabs--local`) are 40px tall at 18px so the hierarchy reads at a glance.
- On narrow screens the strip scrolls horizontally; never wrap tabs onto two lines.
