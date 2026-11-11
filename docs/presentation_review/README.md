# v2.9 map consistency and presentation pass

November 10, 2026. This advances the rendering/atlas work in Group 4 of the
[technical plan](../../ROADS_TRAILS_TECHNICAL_PLAN.md) and the profiling scope of
Presentation & Reliability. v2.9-map remains open for visual/hardware/user-ride
acceptance; this is not a v3.0 release or traveler-AI signoff.

## Starter route: one definition, all views

`new_austellia.START_SPUR` now owns the preserved world-coordinate tuple
`((4650, 2980), (6000, 4300))`. The compatibility export in `frontier_world`,
graph source, Cinder Creek connector, clearance mask, world painter and scaled
map painter all consume that definition. No route or collision geometry moved.

World drawing retains its previous widths, colors, dash phase and old-parcel
overlay order. The minimap, vector overview/zoom and illustrated-background
overlay now draw the spur through the shared clipped route layer. The vector
atlas also uses that layer for its other route types, keeping styles consistent
with the minimap. An offscreen segment is culled or clipped by each view.

Six new starter-route tests verify shared ownership, endpoint continuity,
world stroke parity, clipping with both endpoints outside the view, culling,
and exactly one spur in the real minimap/atlas paths. Illustrated-background
tests use a native Tk bitmap fixture; the captures below show the actual
vector atlas, not a claimed copy of the missing illustrated source artwork.

## Text resources and HUD bounds

`Game.text_font` retains named Tk fonts by family, size and weight across
`canvas.delete('all')`. Dynamic labels reuse those resources; label contents
still update on every draw. The profile workload used nine named-font
constructions across 870 `draw_text` calls. Canvas text/item creation itself
remains a major render cost and needs further profiling.

The clock/region heading measures its available 292-pixel width, uses 11 to
9 point text as needed, then an ellipsis for longer fallback strings. It stays
on one line inside the top-right panel. Short headings keep their original
size. Five new text tests cover font lifetime/reuse, geometry parity against
the previous tuple fonts, all named locations, fallback fitting, and the actual
HUD foreground/shadow bounds. No new runtime dependency or save field is added.

## Native captures

| View | Normal | Low |
|---|---|---|
| Starter seam and now-connected local radar | [Open](starter_seam_normal.png) | [Open](starter_seam_low.png) |
| Long region heading inside HUD panel | [Open](legacy_grid_ridge_normal.png) | [Open](legacy_grid_ridge_low.png) |
| Actual vector atlas overview | [Open](starter_atlas_overview.png) | Covered by route tests |
| Actual vector atlas regional zoom | [Open](starter_atlas_zoom.png) | Covered by route tests |

Compare the previous [starter view](../map_review/starter_seam_normal.png) and
[clipped long-region heading](../map_review/legacy_grid_ridge_normal.png).
These are native 960 x 600 screenshots from a correctly sized Xvfb display;
no generated art, scaling or compositing was used. The world camera follows
the displayed player in the atlas captures.

## Measured profile, not a hardware FPS claim

Both instrumented workloads render nine fixed cameras in Normal/Low: one
warmup plus two measured frames per view, totaling **54 render calls**.
They use the same seed, clock and geometry. Before is clean source `2cafd90`;
after is its tested working tree with this pass applied.

| Function / cumulative seconds | Before | After |
|---|---:|---:|
| Game.render | 8.497 | 7.174 |
| Game.draw_hud | 5.077 | 4.290 |
| Game.draw_world | 3.271 | 2.758 |
| Game.draw_text | 4.470 | 3.805 |
| Tkinter create_text | 4.956 | 4.192 |

These timings include cProfile overhead and shared-host scheduling. Unchanged
work such as image initialization also varied, so the observed differences
do not establish a causal speedup from font reuse. Resource reuse and text
geometry are tested directly. Two measured frames per view are
diagnostic samples, not a reliable p95 or hardware-performance acceptance.
The previous [10-sample baseline](../map_review/README.md) remains available.

Raw frame metrics: [before](before_metrics.json), [after](after_metrics.json).
Portable profile summaries: [before](before_profile.json), [after](after_profile.json).
The source/dirty flags and Python version are retained. Binary Python-version-
specific `.prof` files remain local under `/tmp`.

## Verification and next work

All **35 regression scripts** passed locally with the silent runner; the new
starter/text cases are included in Linux CI. The game self-test and whitespace
review passed. The complete stored physical/bridge audit remains identical:
**240,974 clear route probes**, **50 bridge records**, **101 approach paths**.
The starter view adds one expected radar route stroke; the other fixed-camera
Canvas object counts are unchanged in the profiled runs.

Next: visual clarity for ridge contours, forest character and the starter seam;
settlement label/sign/prompt crowding; profile repeated Canvas item creation;
then actual Archcraft/X11 measurements and the user long ride. These remain
acceptance requirements before closing the map milestone or enabling travelers.

```sh
DUST_AND_DEBT_SILENT=1 xvfb-run -a python3 tests/starter_route_test.py
DUST_AND_DEBT_SILENT=1 xvfb-run -a python3 tests/text_rendering_test.py
xvfb-run -a -s '-screen 0 1280x1024x24' python3 -m cProfile -o /tmp/map-render.prof tools/capture_map_review.py --output /tmp/map-profile --samples 2 --metrics-only
xvfb-run -a python3 tools/run_tests.py
```

All capture/profile runs were silent, used temporary saves and closed their
virtual windows/audio directors on exit.
