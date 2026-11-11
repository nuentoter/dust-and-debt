# v2.9-map terrain-mask cleanup and visual baseline

Review updated November 10, 2026. The phantom grid no longer clears terrain or suppresses
scenery. Authored roads, rails, trails, towns and the starter parcel retain
their clearance. This page records actual screenshots and measurements;
it does not mark the art or hardware-performance acceptance gates complete.

## Functional result

- `road_at` now uses the authored atlas network and preserved `START_SPUR`.
  `ROAD_X`/`ROAD_Y` remain deprecated importable constants with no runtime mask.
- A Graystone West ridge crossing at x=10,200 is solid again for foot and horse.
- Deterministic rocks increase from 332 (94 solid) to 334 (95 solid). Restored
  rocks are at (11755.37, 7917.90), radius 32, solid; and (11717.19, 7867.71),
  radius 19, decorative. They were previously removed by the invisible y=7,900 strip.
- Four new regression tests failed against the old grid behavior, then passed.
  They cover phantom corridor rejection, the restored ridge, clearance along
  all authored routes, and starter-parcel/spur policy.
- All 33 regression scripts passed silently. Full physical validation remains
  clear: 240,974 route probes and 50 bridge records / 101 approach paths.
- Route/deck geometry, original mission locations and save fields are unchanged.

## Reference captures

Native 960 x 600 game-canvas screenshots captured in Xvfb. Normal and Low
use the same authored world coordinates, seed 1889, clock 08:00 and frozen
game simulation. The player stands off the ridge collision focus in that view.
The virtual screen is explicitly 1280 x 1024 so the complete viewport is captured.
No image generation, compositing or rescaling was used.

| View | Normal | Low | Before (Normal) |
|---|---|---|---|
| Cinder Creek eastern/southern seam | [Open](starter_seam_normal.png) | [Open](starter_seam_low.png) | [Before](baseline/starter_seam_normal.png) |
| Larkfield grassland junction | [Open](grass_junction_normal.png) | [Open](grass_junction_low.png) | [Before](baseline/grass_junction_normal.png) |
| Dustwell desert wagon approach | [Open](desert_road_normal.png) | [Open](desert_road_low.png) | [Before](baseline/desert_road_normal.png) |
| Copper Sands wagon road | [Open](desert_outskirts_normal.png) | [Open](desert_outskirts_low.png) | Not captured |
| Everwood branch trail | [Open](forest_trail_normal.png) | [Open](forest_trail_low.png) | [Before](baseline/forest_trail_normal.png) |
| Blackwater town bridge | [Open](river_bridge_normal.png) | [Open](river_bridge_low.png) | [Before](baseline/river_bridge_normal.png) |
| Northstar east fishing bank | [Open](fishing_bank_normal.png) | [Open](fishing_bank_low.png) | [Before](baseline/fishing_bank_normal.png) |
| Everwood named camp | [Open](camp_clearing_normal.png) | [Open](camp_clearing_low.png) | [Before](baseline/camp_clearing_normal.png) |
| Graystone ridge at former grid line | [Open](legacy_grid_ridge_normal.png) | [Open](legacy_grid_ridge_low.png) | [Before](baseline/legacy_grid_ridge_normal.png) |

The Copper Sands outskirts camera was added after the initial baseline to
show a desert road outside the Dustwell plaza; it has no before timing.
All 16 original baseline captures and their exact metrics are retained under
[baseline/](baseline/metrics.json). The post-cleanup gallery has 18 captures.

## Render measurements

One warmup render, then 10 samples per camera/detail mode. The measured scope
is `Game.render + Tk.update_idletasks`; PNG encoding is excluded. p50 is the
median; p95 is the nearest-rank sample. Rendering runs in a silent virtual
display with scheduled gameplay callbacks cancelled. The final after run had
no concurrent local regression/audit process. Shared-host load and warmup
effects are not controlled well enough to infer a causal timing change.

| View / mode | Before p50 / p95 ms | After p50 / p95 ms | Canvas before / after |
|---|---:|---:|---:|
| starter_seam / normal | 167.12 / 441.65 | 125.96 / 146.01 | 284 / 284 |
| grass_junction / normal | 143.40 / 202.22 | 224.61 / 318.05 | 364 / 364 |
| desert_road / normal | 133.78 / 165.78 | 210.45 / 264.22 | 494 / 494 |
| desert_outskirts / normal | Not measured | 163.84 / 299.57 | — / 200 |
| forest_trail / normal | 152.21 / 255.84 | 113.98 / 135.24 | 171 / 171 |
| river_bridge / normal | 184.43 / 217.97 | 197.08 / 342.73 | 634 / 634 |
| fishing_bank / normal | 121.30 / 250.14 | 182.55 / 235.87 | 220 / 220 |
| camp_clearing / normal | 111.17 / 139.03 | 179.23 / 206.06 | 220 / 220 |
| legacy_grid_ridge / normal | 93.53 / 116.98 | 148.51 / 339.83 | 214 / 220 |
| starter_seam / low | 98.12 / 155.97 | 114.12 / 136.51 | 229 / 229 |
| grass_junction / low | 176.62 / 402.22 | 198.10 / 537.02 | 349 / 349 |
| desert_road / low | 143.66 / 196.33 | 217.15 / 323.95 | 440 / 440 |
| desert_outskirts / low | Not measured | 147.97 / 241.93 | — / 147 |
| forest_trail / low | 97.18 / 122.52 | 108.64 / 129.65 | 148 / 148 |
| river_bridge / low | 138.97 / 233.72 | 167.10 / 182.83 | 594 / 594 |
| fishing_bank / low | 85.90 / 91.85 | 179.52 / 314.06 | 165 / 165 |
| camp_clearing / low | 87.91 / 104.48 | 133.76 / 167.54 | 155 / 155 |
| legacy_grid_ridge / low | 84.68 / 90.97 | 129.73 / 176.42 | 160 / 160 |

Canvas counts are unchanged at seven matched cameras in both modes. At the
former grid/ridge camera, Normal adds six scenery items (214 -> 220); Low
remains 160. These are object-count observations, not a frame-rate guarantee.
Timing increased at several unchanged scenes and varied widely. **No timing
improvement or performance acceptance is claimed.** Profile the rendering work
and validate on the owner's Archcraft/X11 hardware before signing off.

| Process measurement | Before | After |
|---|---:|---:|
| Game + review imports (seconds) | 0.198096 | 0.229068 |
| Game construction/new game (seconds) | 1.420493 | 1.438091 |
| Peak process RSS (KiB) | 172008 | 172100 |

RSS includes Tk, game assets, review imports and Pillow screenshot tooling.
The after run includes two extra outskirts views, so this is not a controlled
game-only working-set comparison. `source_commit` identifies the base commit;
`game_sources_dirty` is false before and true for the tested cleanup working
tree before its commit. These historical flags are preserved honestly.

Raw data: [before](baseline/metrics.json), [after](metrics.json),
[pure graph build baseline](graph_metrics.json).

## Visual review findings / next work

The reviewed screenshots preserve navigable road/trail silhouettes, bridge
timber, fishing pads and camp silhouettes in Low. They also expose remaining
presentation work:

- The starter artwork still has a visible rectangular edge despite feathering.
- Follow-up: [starter-route unification](../presentation_review/README.md) now
  includes that spur in the scaled atlas/minimap layers without moving it.
- Larkfield and Dustwell have crowded NPC labels, signs and interaction prompts.
- Everwood views remain visually sparse for a forest; biome art needs attention.
- Ridge contour bands can resemble an oversized road, while the minimap correctly
  shows no route through the restored solid ridge. Add clearer landform cues.
- Follow-up: [bounded HUD headings](../presentation_review/README.md) fix the
  long-region overflow shown in these historical captures.
- Rendering needs profiling and real-hardware verification before adding detail.

These are findings for the next polish pass, not visual approval. User long-ride
acceptance and milestone closure remain open; traveler AI is deferred.

## Reproduce

Pillow is optional development tooling for native PNG capture; the game runtime
and `--metrics-only` mode retain their existing dependency baseline.

```sh
xvfb-run -a -s '-screen 0 1280x1024x24' python3 tools/capture_map_review.py --output /tmp/map-review --samples 10
xvfb-run -a -s '-screen 0 1280x1024x24' python3 tools/capture_map_review.py --output /tmp/map-metrics --samples 10 --metrics-only
DUST_AND_DEBT_SILENT=1 python3 tests/route_mask_test.py
DUST_AND_DEBT_SILENT=1 python3 tools/audit_routes.py --physical --include-rail --check --json /tmp/road-audit.json
xvfb-run -a python3 tools/run_tests.py
```

The capture tool always silences playback, uses a temporary save, freezes its
simulation, and stops audio/destroys the virtual window in a `finally` block.
