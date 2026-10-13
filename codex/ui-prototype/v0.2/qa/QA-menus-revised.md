# Menu fidelity audit — revised candidate

Evaluator: menu QA sub-agent. Scope: selected concepts 15–24. Reviewed reference images and live CUA screenshots after the menu reconstruction on the uniform 1672×941 design canvas. This is a qualitative visual score, not a pixel-equivalence claim. Because this agent authored the revisions, a separate root cross-review should confirm these candidate scores before final acceptance.

| Screen | Initial | Revised candidate | Evidence |
| --- | --- | --- | --- |
| Main | 5 | 9.0 | Entire four-action composition and footer visible; matching nominal placement; geometric nested SVG outlines, selected lime brackets, broad role-specific display type. |
| Lobby | 4 | 9.0 | Exact authored blueprint map region; live mode/mission/population/start/callsign hierarchy. Three tabs, left half reserved composition, complete footer controls. |
| Downloading assets | 4 | 9.0 | Single-line broad heading, stage, progress percentage and terrain caption, four compact live checklist rows, tip/cancel. Removed clipped caption. |
| Preparing match | 3 | 9.0 | Detailed carrier blueprint extracted as illustration only. Live heading/status/progress/checklist, large engineering frame, tip strip. Demo enter action hidden from game composition. |
| Match menu | 4 | 9.0 | Correct left action width/position, compact logo/copy, resume bracket, danger treatment, separator and live footer. All five actions visible. |
| Report | 5 | 9.0 | Live issue selectors, form field/counter, checkbox, save/cancel; accurate dual-column proportions, reference attachment illustration, top back/close. Copy explicitly reflects local export rather than online submission. |
| Learn controls | 2 | 9.1 | Authored detailed operator/gantry illustration replaces stick figure. Original raster headings and copy masked; all title/instruction/progress/index/actions live DOM. Other lessons have substantive input/equipment diagrams. |
| Map | 3 | 9.2 | Authored terrain replaces radial polygon. Original player/marker patched; live SVG markers and existing pan/zoom coordinate system preserved. Seven POIs, zone/legend/timer match. |
| Victory | 2 | 9.0 | Authored operator illustration, original title-tail fragment masked, oversized live title, placement/stats/CTA composition aligned. |
| Elimination | 3 | 9.0 | Logo, title-case heading, placement/stats/CTA and exact authored blueprint map composition restored. |

Checks performed: JavaScript syntax check; direct CUA review of all ten initial screens and repeated direct review of revised screens; map marker removal verified to remove the live pin without leaving the old reference pin; all ten menu compositions now fit normal browser viewport through parent uniform stage scaling.

Remaining deliberate differences: vector logo is the approved downloadable identity; fonts are real bundled fonts, so glyph shapes differ slightly from generated concepts. Frame detailing is recreated in SVG/CSS rather than copying interface pixels. Artwork crops contain illustration content, while interactive controls and display copy remain live. POI labels and static safe-zone border are presently embedded in map artwork; the placed marker and player indication are live SVG.

Source files: `menus-rebuild.js` and `menus-rebuild.css`. Original `app.js` event delegation and sample state remain in use. No game renderer or multiplayer functionality is implied.
