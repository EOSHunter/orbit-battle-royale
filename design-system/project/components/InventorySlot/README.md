# InventorySlot

One of five numbered slots in a single horizontal strip, bottom-center of the HUD. Slots 1-2 hold weapons; slots 3-5 hold healing, grenades and the Tethercaster.

**Consumer provides:** slot number and its current binding, item icon, quantity, optional charge (Tethercaster cooldown, heal progress), and state.

- Slots 1-2 carry a small diamond weapon-eligibility mark; a gap separates them from 3-5.
- Selected: 2px `accent` border and the item name under the strip. Empty: dashed `border`, no icon.
- Quantity bottom-right in `tabular-nums`. Healing icons take `health` or `shield` tint; everything else stays `text-primary`.
- `is-full` (`warning` border) appears with a message when a pickup cannot be carried: "Shield Pack 3/3 · full".
- Every move, drop, split and swap works without dragging: select a slot, then press the action's binding.
- Distinct silhouettes per item; never rely on tint to tell items apart.
