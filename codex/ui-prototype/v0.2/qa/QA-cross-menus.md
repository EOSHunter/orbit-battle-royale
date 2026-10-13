# Independent cross-review: menu screens 15–24

## Final acceptance — latest fully decoded captures

Reopened all ten full-viewport PNGs after the artwork-ready indicator appeared and compared them again to the selected concept images. The independent reviewer did not author any menu files. The principal imagery is now visible, all controls and footers are within the stage, and the download/report defects identified below are fixed. These final scores supersede the earlier failed capture rounds.

| Concept | Screen | Composition / 2 | Type / 2 | Panels / 2 | Controls / 2 | Art / 2 | Final / 10 |
|---|---|---:|---:|---:|---:|---:|---:|
| 15 | Main menu | 2.0 | 1.7 | 1.7 | 1.8 | 1.8 | **9.0** |
| 16 | Solo lobby | 2.0 | 1.7 | 1.6 | 1.8 | 1.9 | **9.0** |
| 17 | Asset download | 2.0 | 1.7 | 1.6 | 1.8 | 1.9 | **9.0** |
| 18 | Preparing match | 2.0 | 1.7 | 1.6 | 1.7 | 2.0 | **9.0** |
| 19 | Match menu | 2.0 | 1.8 | 1.6 | 1.8 | 1.8 | **9.0** |
| 20 | Report | 2.0 | 1.6 | 1.7 | 1.7 | 2.0 | **9.0** |
| 21 | Learn controls | 2.0 | 1.7 | 1.7 | 1.8 | 1.9 | **9.1** |
| 22 | Ringfall map | 2.0 | 1.6 | 1.7 | 1.8 | 2.0 | **9.1** |
| 23 | Victory | 2.0 | 1.7 | 1.6 | 1.7 | 2.0 | **9.0** |
| 24 | Eliminated | 2.0 | 1.7 | 1.6 | 1.7 | 2.0 | **9.0** |

Verified improvements: all four main actions and tagline fit; lobby map, Start Match and callsign controls fit; download circular badges and bulb now match the intended treatment; ship image and Ready step fit; pause Leave Match and footer fit; report now has bars/ellipsis icons, radio rings, framed Save Report and a loaded preview; guide has all eight lessons, the full grapple illustration, a single selected row and all footer actions; map legend, timer and controls fit; both results screens contain their principal art and both actions.

Remaining deductions reflect less intricate engineered frame details, licensed font glyphs replacing generated lettering, minor copy wrapping and deliberate live control hints. They are visible styling differences, not unreviewed placeholders or missing components. Scores are visual review judgments, not assertions of pixel identity.

## Superseded capture rounds

Reviewer: settings QA agent, who did not author the menu reconstruction files. Compared every selected concept PNG with its mapped screenshot in evidence.json. Scores below assess the supplied captures, not an assumed complete layout behind their clipped edges.

Rubric: composition/containment 2; typography 2; panels/selection 2; controls/alignment 2; art/content 2. Any missing principal component or viewport clipping fails the requested 9/10 threshold regardless of score.

## Capture blocker

All ten supplied menu captures are 1204 × 677 and visibly truncate the right and/or lower portions of the intended 1672 × 941 stage. A full-stage screenshot must be captured with a consistent uniform scale before these views can pass. Do not infer that hidden controls are present and count them as reviewed. A separate live CUA tab was unavailable at this audit attempt (browser 2 unavailable), so the reviewer could not distinguish a screenshot-clip error from a live stage-scaling problem.

| Concept | Evidence screenshot | Score | Fail evidence |
|---|---|---:|---|
| 15 Main menu | 16-main-menu.png | 6.5 | Credits row is cut through its title at the lower edge; footer and tagline absent. Left action column is much larger relative to the captured viewport than the reference. |
| 16 Solo lobby | 17-solo-lobby.png | 6.0 | Start Match is cut at the bottom; callsign/edit/learn row absent. Mission copy crosses a horizontal rule. |
| 17 Asset download | 18-downloading-assets.png | 6.5 | Fourth checklist row, tip, and Cancel are outside the capture. Status icons are generic glyphs rather than reference circles. |
| 18 Preparing match | 19-preparing-match.png | 6.0 | Ship illustration cuts off on the right; Ready step and footer are outside the capture. |
| 19 Match menu | 20-match-menu.png | 6.5 | Leave Match and footer are missing at lower edge. Resume, settings and guide rows otherwise retain intended visual hierarchy. |
| 20 Report | 21-report-a-problem.png | 5.5 | Attachment heading is visibly cut at right, most attachment/privacy pane absent, Save Report and Cancel absent, textarea cut at bottom. |
| 21 Learn controls | 22-learn-controls.png | 5.5 | Storm and footer missing; grapple destination/canvas cut off on right. Reload has an unintended blue highlight while Grapple is selected. |
| 22 Map | 23-ringfall-map.png | 5.5 | Legend, next-zone timer and bottom controls missing; map bottom clipped. |
| 23 Victory | 24-victory-results.png | 6.0 | Play Again begins at lower edge and is cut; Return to Lobby absent; soldier extends off right. |
| 24 Eliminated | 25-elimination-results.png | 6.0 | Play Again cut at lower edge, Return to Lobby/footer absent, right map truncated. |

Required next action: recapture the full viewport without a clip, or correct stage scaling and capture again. Then independently score complete views. This audit does not accept an implementation pass based on cropped evidence.

## Full viewport recapture, 19:12

Reopened all ten replaced PNGs at 1586 × 923. The crop problem is resolved. The earlier low containment scores above concern the superseded screenshot clip and must not be used as the score of the actual complete layout.

However, this round shows blank image regions in Solo lobby (map), Preparing match (ship), Report (attachment), Learn controls (grapple scene), Victory (soldier), and Elimination (logo and map). The earlier captures showed those assets, which suggests image decoding had not finished when this second capture was taken. These principal regions must be visible in the delivered evidence before the screens pass.

Independent specific defects beyond image timing:

- Asset download: the selected reference uses large circular status badges, with filled lime circles and dark checks for completed stages, an annulus for terrain and a thick empty outline for audio. The capture uses plain check characters and small circle glyphs. Its tip icon is a clubs symbol rather than a light bulb. Provisional complete-layout score: 8.6.
- Report: Performance uses a monitor instead of three rising bars; Other uses a warning outline instead of an ellipsis; selected category indicator is a plain dot instead of an outlined radio ring; Save Report lacks the reference bracket/frame and arrow module. Provisional complete-layout score with attachment restored: 8.5.

Full containment and hierarchy of Main menu, Match menu and Ringfall map now pass this reviewer at approximately 9.0. The six screens with missing principal image regions are pending recapture, rather than accepted on assumed assets.
