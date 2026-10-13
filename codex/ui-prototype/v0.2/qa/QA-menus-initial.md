# Independent menu fidelity audit — initial prototype

Reference: selected images 15–24 in `outputs/ui-concepts-v0.2/manifest.json`. Evaluated by direct visual inspection of every reference and live prototype through a separate background CUA tab at approximately 1265 × 712. Scores concern fidelity, not feature count. None passes the requested 9/10 threshold.

| Screen | Score / 10 | Required corrections |
| --- | --- | --- |
| 15 Main menu | 5 | Fit complete menu/footer in viewport. Restore wide extended typography, left perimeter rail, nested action geometry, index compartment, engineered underlines, chamfered arrow button. Current button border right side is missing/clipped. |
| 16 Lobby | 4 | Start match and callsign hidden below viewport. Reduce logo/spacing/box padding. Restore lime side bracket on SOLO, open mission framing, integrated map population block and wide start action. Current symmetric polygon map differs substantially. |
| 17 Assets | 4 | Single-line headline, reference order headline then download stage, wide lime bracket progress frame, compact numbered check rows, tip and cancel visible. Remove demo advance button from composition or place in explorer. Current screen wastes right half while scrolling on left. |
| 18 Match loading | 3 | Replace crude polygon ship with detailed authored blueprint illustration. One coherent checklist panel under heading, thinner integrated progress line, larger right illustration frame. Tip/footer visible. Keep demo transition in explorer. |
| 19 Match menu | 4 | Compact logo and controls so Leave match/footer visible. Restore detailed chamfer action frames, lime engineering underline, framed arrow, danger side bracket. Current thin broken outline is unlike reference. |
| 20 Report | 5 | Reference back at top-left and close at top-right, no large logo header. Wide headline, distinct lime numbered section markers. Issue controls need chamfers, icons and radio selectors. Complete text field, counter and save/cancel visible. Right attachment frame should follow reference proportions. |
| 21 Learn controls | 2 | Replace stick figure with authored armored operator, cable, gantry and basalt illustration. Preserve compact copy region and wide hero. Left indexed action geometry/arrow controls, progress dash indicator and footer visible. Move/Aim lessons currently show tiny generic icon surrounded by blank space. |
| 22 Map | 3 | Terrain must be actual authored map with island, lakes, roads, terrain/settlement detail. Current radial procedural polygon/rectangles are placeholder. Restore violet ion-storm shading outside circle, consistent seven POI labels, wide map frame. Footer/timer should fit. |
| 23 Victory | 2 | Replace polygon mannequin with detailed operator artwork; match hero crop, large extended headline, wide stats frame, lime bracket CTA. Return-to-lobby action visible. |
| 24 Elimination | 3 | Restore logo-bearing composition, title case headline, dense topographic map illustration with centered elimination X. Match statistic/CTA scales and column proportions. Return-to-lobby/footer visible. |

## Shared blockers

- The prototype uses fixed minimum heights, padding and oversized headers. Ordinary viewport screenshot clips critical buttons; this is a functional failure as well as fidelity failure. Scale the game canvas within available viewport, or size layout proportionally to a documented design canvas. Check 1920×1080, 1366×768 and 1280×720.
- Selected reference typography is broad and geometric; current Oxanium heavy face is narrow and square with different character proportions. Adjust width, spacing, weight and size per role rather than simply applying bold uppercase everywhere.
- Reference panels use sparse fine-line surfaces, variable/asymmetric notches, nested frame sections and lime selection accents. Generic identical eight-corner boxes with double borders flatten this hierarchy.
- Noninteractive authored illustration assets are appropriate in a coded UI. Crop/extract or faithfully recreate hero drawings and terrain, leaving all labels, controls and state as live DOM. Do not upscale a generic 26px glyph into hero artwork.
- Explorer UI should stay separate from screen controls and not consume essential game composition. Sample-state controls belong there.

Re-audit required after revision. These initial scores are not a pass certificate.
