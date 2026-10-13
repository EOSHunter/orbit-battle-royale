# Independent cross-review: dialogs, HUD and inventory

Reviewer: settings QA agent, who did not author gameplay-rebuild.js or gameplay-rebuild.css. Inspected selected references 25–28, the latest full screenshots 26–29, and HUD screenshots at 140% and 150%. This review is separate from the gameplay author's scores.

Rubric: composition/containment 2; typography 2; frames/states 2; controls/alignment 2; art/content 2. Unresolved overlaps, clipped principal content, or missing components fail regardless of numeric score.

| Concept | Evidence | Composition | Type | Frames | Controls | Art/content | Final |
|---|---|---:|---:|---:|---:|---:|---:|
| 25 Reset confirmation | 26-reset-settings-confirmation.png | 2.0 | 1.8 | 1.8 | 1.5 | 2.0 | **9.1/10** |
| 26 Leave match | 27-leave-match-confirmation.png | 2.0 | 1.7 | 1.6 | 1.8 | 1.9 | **9.0/10** |
| 27 Gameplay HUD | 28-gameplay-hud.png | 2.0 | 1.7 | 1.7 | 1.8 | 2.0 | **9.2/10** |
| 28 Inventory | 29-inventory.png | 2.0 | 1.7 | 1.7 | 1.8 | 2.0 | **9.2/10** |

Reset: centered compact panel, correct category title and explanatory text, Cancel as the safe focused action, distinct coral Reset. Background remains recognizable. The reset glyph differs from the reference circular arrow, and frame details/lettering are approximate; these are deductions rather than missing controls.

Leave: corrected title now matches the reference scale and occupies one line; large exit symbol, separator, explanatory text and paired Stay/Leave actions fit. The background uses the current canonical five-slot HUD instead of the older illustrative HUD in this particular generated dialog reference, preserving the player's actual prototype UI.

HUD: detailed minimap and storm card, centered directional strip and crosshair, counters, separated health/shield meters, exactly five item slots with matching equipment art, and a right ammunition card are all present. The clear central aiming area matches the reference. The three lower groups do not collide. Minor frame-detail and font differences remain.

Inventory: title and two vitals fit; five rows and item art have sufficient room; the detail panel begins in its own column and contains the large rifle illustration, magazine and reserve stats without overlap. All four ammo reserve groups and footer controls fit. The original cut/overlap concern is resolved. Typography and frames retain small differences from generated concept lettering and details.

HUD accessibility evidence: independently viewed hud-140.png and hud-150.png; both maintain clear space between meters/hotbar and hotbar/ammunition, and every lower group remains fully visible. The supplied DOM measurements for scales 75/100/140/150 record left gap 72.56 px, right gap 128.74 px, and bottomVisible true for every case. Those measurements support the visible containment check; they are not used as a substitute for visual comparison.

All four pass the requested 9/10 visual threshold in this independent review. Scores are reviewer judgments, not pixel-identity assertions.
