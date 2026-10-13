# Gameplay and dialogs independent QA

Reference: selected screens 25–28 in the sci-fi UI v0.2 manifest. Baseline reviewed against actual concept images, supplied screenshots, saved prototype previews, live browser screenshots, and measured DOM bounds.

| Screen | Baseline score / 10 | Required correction |
| --- | ---: | --- |
| 25 Reset category | 5 | Chamfered dialog and buttons, engineering divider, centered copy, contextual backdrop |
| 26 Leave match | 4 | Full-sized exit emblem, authored frame accents, proportional heading/action layout |
| 27 Gameplay HUD | 3 at 140%; 6 at 100% | Eliminate overlap, center hotbar, reproduce actual equipment/map artwork and slim frame detail |
| 28 Inventory | 6 | Detailed equipment silhouettes and weapon schematic, larger title, vitals meters and frame hierarchy |

## Measured baseline defect

At a 1280 × 720 browser viewport with the persisted 140% HUD scale, vitals span x32–494; hotbar spans x188–891; ammo spans x842–1248. Vitals overlap the hotbar by 306px and ammo overlaps it by 49px. The hotbar center is approximately x540 rather than x640. Help hints intersect its top edge. The old code reads `safeInset` but does not apply it.

## Reconstruction acceptance criteria

- The reference canvas is 1672 × 941, proportionately fitted into the viewport.
- HUD 75%, 100%, 140% and 150% maintain distinct left / center / right zones; larger internal content may grow upward, with no collision.
- Exactly five interactive quick slots and exactly five inventory modules.
- Four segments per vital; 75 shields = three filled; 100 health = four filled.
- Equipment and map crops contain visual artwork only; labels, values, selection, interactions and frame geometry remain authored UI.
- Reset uses a 754 × 255 nominal dialog; Leave uses 885 × 490.
- Cancel / Stay has initial focus, Escape exits, and reset scope remains limited to the named category.
- All four must be independently reviewed again after integration. Baseline scores are not completion scores.
