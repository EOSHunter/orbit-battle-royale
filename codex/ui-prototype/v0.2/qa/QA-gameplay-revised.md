# Independent gameplay and dialog visual QA

Review 1: inspected the actual saved evidence PNGs for screens 26–29 and compared them with selected concepts 25–28. These scores evaluate the rendered evidence, not the intent of the new code.

| Screen | Score / 10 | Pass ≥ 9? |
| --- | ---: | --- |
| Reset category confirmation | 6 | No |
| Leave match confirmation | 5 | No |
| Gameplay HUD | 2 | No |
| Inventory | 4 | No |

## First capture failure (superseded)

All four evidence PNGs are 1204 × 677 and show a clipped portion of the reference canvas. The HUD bottom widgets are entirely absent and the right counters are clipped. Inventory clips the detail pane, right health indicator, ammo reserves and footer. Leave dialog clips its right and bottom edges. Reset dialog is horizontally displaced rather than centered in the captured viewport.

Root investigation identified a screenshot clipping / coordinate mismatch rather than actual application stage failure. Complete 1586 × 923 viewport evidence superseded those first captures.

## Review 2: complete viewport evidence

| Screen | Score / 10 | Pass ≥ 9? |
| --- | ---: | --- |
| Reset category confirmation | 7.8 | No |
| Leave match confirmation | 7.8 | No |
| Gameplay HUD | 8.6 | No |
| Inventory | 5.5 | No |

HUD artwork is present and the complete default layout fits without overlap. Inventory's complete snapshot lacks every equipment crop and its detailed schematic; the leave-dialog background also lacks map / equipment imagery. This appears to be capture timing before the SVG image elements have painted, because the next HUD capture does show the same artwork. Stable evidence must show all assets before scoring is final.

The next corrective iteration widens display typography toward the reference, gives safe dialog actions a visible white frame and lime corners, thickens the exit symbol, and matches the HUD counter group width. These changes are not yet scored until fresh, fully loaded screenshots are reviewed.

HUD 140% and 150% visual QA remains pending separate complete evidence. Source inspection and syntax checking do not substitute for rendered verification.

## Review 3: artwork ready and latest typography

The third capture set was taken after decoding reference artwork and waiting for fonts. All four full screens are now visible and every equipment / schematic crop is present.

| Screen | Score / 10 | Pass ≥ 9? |
| --- | ---: | --- |
| Reset category confirmation | 9.0 | Yes |
| Leave match confirmation | 8.8 | No |
| Gameplay HUD at 100% | 9.0 | Yes |
| Inventory | 8.5 | No |

Reset now matches the compact dialog scale, centered copy, safe white action frame and named-category context. HUD matches equipment artwork, five-slot hierarchy, slim four-segment vitals, separate lower zones and readable centered aiming area. Minor differences in procedural frame detailing remain within the threshold.

Leave title was approximately 11% too narrow, and its emblem remained slightly small. Inventory's right detail frame stretched below the intended row and overlapped the ammunition reserve frame; item artwork and text were approximately 35 nominal pixels too far left. Corrections for these failures are saved and require final recapture before approval. HUD 140% and 150% verification is still pending.

## Final review: current complete evidence

Reviewed updated full-viewport reset, leave and inventory evidence, plus `hud-140.png` and `hud-150.png`, against the selected concept images. All artwork is present. The detail panel now ends above the ammunition reserves; title proportions and equipment alignment have been corrected.

| Screen | Final visual score / 10 | Pass ≥ 9? |
| --- | ---: | --- |
| Reset category confirmation | 9.0 | Yes |
| Leave match confirmation | 9.1 | Yes |
| Gameplay HUD at 100% | 9.0 | Yes |
| Inventory | 9.0 | Yes |
| HUD at 140% and 150% | 9.0 | Yes |

HUD stress evidence keeps five slots, distinct left / center / right lower zones, visible quantities, full bottom bounds and a clear aiming area. Increasing scale enlarges content and vertical extent inside reserved widths rather than independently scaling whole groups into each other. Root measured positive gaps of approximately 72 and 128 physical pixels across 75–150%.

Two tiny source-art crop remnants visible at enlarged scale were removed by tightening the grapple and medical-pouch crops; these edits do not change widget layout. Safe-area inset now updates actual corner and bottom positions using a bounded delta: clamp(-24px, 48px, (setting - 5) × 9.6px). The default 5 setting preserves reviewed reference positions; extreme values retain positive reserved-zone gaps. Root should retain the final refreshed HUD and inset bounds checks alongside this report.

These scores certify fidelity of the reviewed prototype evidence, not a production game or pixel-identical replication. Remaining small differences are procedural frame ornament and some type metrics. There are no blocking visual failures in the final reviewed four screens.

### Final crop containment correction

The 150% follow-up exposed a narrow source-selection strip in the first equipment sprite. Physical SVG viewport overflow clipping did not constrain source pixels within letterbox padding produced by `preserveAspectRatio`. Each artwork crop now has a unique `userSpaceOnUse` clip path that clips the source image explicitly to its x/y/width/height rectangle. This prevents any surrounding concept UI from leaking into the authored equipment controls. Syntax check passes; root is retaining a refreshed 150% screenshot to verify containment.

Final refreshed 140%, 150% and inventory evidence was visually inspected after explicit clipping. Surrounding source UI strips and duplicated index / quantity remnants are gone; all 9.0 passing scores remain unchanged. The grapple clip includes a small top-left exclusion for the source slot number, allowing the full tether loop to remain visible without bringing that number into the sprite. This final art-only refinement does not change any UI bounds.
