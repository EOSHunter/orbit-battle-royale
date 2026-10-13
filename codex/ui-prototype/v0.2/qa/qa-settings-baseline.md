# Independent settings reference audit

Baseline inspected 2026-10-13 by the settings QA subagent using the selected concept PNGs and a separate browser tab. Browser viewport: 1265 × 712. The score measures visual fidelity, not whether a control responds.

Rubric: composition and scale 2 points; typography 2; panel and state treatment 2; control geometry and alignment 2; illustration and contextual help 2. Pass requires at least 9/10 and no clipping, overlap, missing key component, or wrong active state in the comparison fixture. Saved user preferences are not penalized, but the comparison fixture must initialize to reference values.

| Reference | Score | Screen-specific repair |
|---|---:|---|
| 01 Mouse | 5.0 | Put increment before value; restore angled selected bracket; detailed mouse diagram, lime rotation arrows and corner brackets; toggle uses reference left/right selector. |
| 02 Behavior | 4.5 | Full-width joined Hold/Toggle controls, lime filled selection; label rows Aim/Crouch/Sprint; two labeled mouse panels with highlighted left button and explanation. |
| 03 Keyboard bindings | 4.5 | Ten visible rows in stage; selected first row; primary/secondary columns match reference widths; WASD keycaps and Capture/Clear/Cancel hints in help pane. |
| 04 Controller layout | 4.8 | Wide joined prompt choices, flanking arrows; toggle controls aligned with selector column; detailed controller with labeled colored face buttons and connection status. |
| 05 Controller look | 4.8 | Response choice geometry and arrows; large gridded lime curve with Fast/Slow and Low/High input labels, rather than small generic diagonal. |
| 06 Deadzones | 4.8 | Detailed paired circles with axes, dashed annuli, gray ignored area, lime corner brackets and bottom status. |
| 07 Controller bindings | 4.3 | Remove empty secondary column; align button column at right; colored A/B/X/Y circles and trigger glyphs; full controller diagram. |
| 08 Audio volume | 5.0 | Default comparison focus Combat & world; show all six rows; bracketed speaker with alternating lime/white sound arcs; joined dynamic-range selector. |
| 09 Audio voice | 5.0 | Align disabled selector columns and boxed Unavailable badges; disabled sliders muted, rather than lime; detailed mic with echo arcs and brackets. |
| 10 Video display | 4.5 | Default comparison focus Render scale; detailed world wireframe inside render-scale diagram plus separate sharp UI overlay; correct selector widths. |
| 11 Video graphics | 5.0 | Five boxed help rows with label/description columns instead of loose prose; show six settings without clipping. |
| 12 Readability | 3.5 | Repair oversized full-width shield; help must contain small health/shield meters and five slots inside a compact bounded sample; no help content may overflow. |
| 13 Comfort | 4.5 | Two labeled Motion enabled/Reduced motion diagram panels with motion trails and baseline arrows; proper selected row and control arrows. |
| 14 Gameplay HUD settings | 4.5 | Default comparison focus Safe-area inset; visual crosshair choices; complete inset diagram with crosshair, five mini slots, edge arrows and dashed safe boundary. |

Shared blockers: header/category/subtab area consumes roughly 55% of the viewport before content, compared with 35.5% in the concepts. Body/footer overflow below the viewport. Category and panel frames have heavy double octagonal edges; reference uses thin engineered chamfer rules with lime bracket selection. Reference help headings have a separator rule; body copy has technical spacing. Settings labels and control dimensions should share a stable stage grid. Full-screen 16:9 composition should be preserved through uniform stage scaling, then mobile treatment can be separately specified.

No screen passes the requested 9/10 bar in this baseline.
