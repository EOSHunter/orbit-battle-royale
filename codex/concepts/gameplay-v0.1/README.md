# Gameplay and inventory concepts v0.1

Generated using the built-in image_gen tool with the existing AR-7, first-person arms, Glass Basin, Tethercaster, and refined Field Patch images as design references.

## Selected images

- [First-person gameplay POV](first-person-pov.png): held AR-7, armored arms, Glass Basin, rings belonging to Veyra overhead, minimap, compass, match counters, health/shields, five-slot quick inventory, and ammo.
- [Inventory screen](inventory-screen.png): the same gameplay backdrop beneath a dark overlay, two weapon slots plus three item slots, selected weapon details, consumable caps, ammo reserves, and Equip/Move/Drop/Close actions.
- [Prompts and refinement instructions](prompts.md).

These are generated visual targets, not screenshots of the Godot build or proof of browser performance. Names, bindings, ammo counts, match values, and stack values are illustrative. The actual shared component contracts and game data remain authoritative.

## Example state

23 combatants remain; 4 eliminations; shield 75/100; health 100/100; assault rifle has 24 rounds in the magazine and 150 in reserve. Loadout: AR-7 Wayfarer, SG-4 Breaker, Tethercaster, three Shield Packs, six Field Patches. Inventory reserve row illustrates Light 0, Medium 150, Heavy 12, Shells 16.

The selected inventory screen uses a grapple launcher and a flexible Field Patch pouch after refinement. Small quick-HUD glyphs in the POV are illustrative and still need replacement with the final consistent icon family. The held weapon perspective was corrected to face away from the camera into the scene. Health and shield meters illustrate four 25-point segments.

## Implementation review

Preserve the five-slot rule and color-independent labels/icons. Ammo is a separate bounded reserve, not extra carried-item slots. Inventory has explicit non-drag actions. Do not hard-code concept values, invent new bindings, or infer weapon tuning from the artwork. Implement actual state, responsive scaling, contrast, keyboard/controller focus, and input ownership through shared components.

The depicted world detail, ring geometry, distant landmarks, weapon geometry, and camera proportions still need an art/level consistency pass. Keep the aiming region clear and measure browser performance with actual assets.
