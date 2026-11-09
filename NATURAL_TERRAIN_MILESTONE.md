# Rivers, Ridges & Stone — v2.8-map implementation design

**Status: initial implementation in progress; validation and additional polish pending.** Tracker: [#19](https://github.com/nuentoter/dust-and-debt/issues/19).

## Implementation snapshot (first pass)\n\nThe initial `natural_terrain.py` now contains 12 authored upland spines, 8 dry washes connected geographically to mapped river corridors, fixed rock fields, continuous coarse-value noise, biome blending, camera-local broad terrain swaths and conservative rock collision. `game.py` now renders this geometry instead of the rectangular 112-unit tile floor and delegates outer cover collision to the new module. The legacy rectangular crossroads painting was removed from the outer terrain renderer. Natural-terrain tests and Linux Actions coverage have been introduced; full green verification and remaining art polish are still required.\n\n## Design intent

New Austellia's existing 60,000 × 40,960 world, 15 regions and traced town/river/railway geography remain fixed. The problem to solve is that much of the terrain currently feels like empty space, and inherited sector-based repetition reads as a rectangular grid. Create broad coherent landscapes, not evenly distributed props.

Start from the source illustrated map. In particular, use Graystone Range, Cinder Ridge Badlands, Iron Mesa, Red Mesa Buttes, Red Thorn Canyon and Sundown Plateau to anchor continuous upland systems. Link minor waterways into the existing Sable, Blackwater, Roan Creek, Riversend Channel, Dustwell Wash and Cypress Bayou geography; never generate a river crossing a rail bridge at a different location than its visible deck.

## World shaping rules

- **Regional gradients:** Blend nearby named biome influence points through low-frequency deterministic noise at multiple scales (e.g. ~1200–5000 units), keeping large coherent patches and avoiding rectangular sector seams. Preserve current geographic labels.
- **Landform skeleton:** Author 8–12 ridges/mesas as polylines or layered closed polygons, with long sightlines, plateau shelves, cliff edges and narrow but navigable passes. Multiple stacked contour bands provide height cues in top-down view.
- **Water drainage:** Use existing five traced named channels, then create a handful of smaller tributaries with endpoint junctions, flow direction toward rivers/lakes/coast and gentle interpolated bends. Dry washes may be passable while wet channels retain existing collision rules.
- **Rock distributions:** Place at least 20 clusters; anchor to ridge foot/canyon wash/mines. A cluster has 1–3 larger rocks, 3–8 medium rocks, and smaller decorative scree. Only anchor rocks are solid; decorative stone should not snag the horse.
- **Vegetation:** Forest groves near water, scrub in transitional prairie, occasional trees in open grass, reeds on calm banks. Keep plausible sparse desert corridors and clear gameplay sightlines.
- **Road flow:** Honor existing atlas roads/rail and crossing decks, then soften local track rendering with erosion/wheel ruts, not arbitrary disconnected routes. If a road must bend around new rock, move the rock rather than silently breaking the canonical road.

## Python interface sketch

```python
# natural_terrain.py — data/functions proposed, not yet implemented
TERRAIN_SEED = 1889
RIDGES = (...)           # authored plateau and cliff spine points
PASS_CORRIDORS = (...)   # authored traversable paths through ridges
BOULDER_FIELDS = (...)  # authored cluster footprints and deterministic seeds
TRIBUTARIES = (...)     # connected to mapped source river polylines

def sample_terrain(x: float, y: float) -> dict:
    # biome weights, altitude band, moisture, erosion, feature flags
    ...

def landform_solid(x: float, y: float, radius: float = 11) -> bool:
    # fast candidate queries, respecting bridges/roads/towns and passes
    ...

def draw_visible(canvas, camx, camy, width, height) -> None:
    # spatially cull precomputed geometry and draw at most screen-local items
    ...
```

Use polygon-to-circle / polyline capsule distance for the collision profile, not the pixel outlines of shading. Deterministic hashes and authored points guarantee a saved journey looks the same after restart. Use coarse bins / feature bounding boxes so collision is not linear in all boulders and all rivers. Draw shaded layers with simple Tk canvas shapes, no runtime Pillow requirement.

## Integration points (existing files)

| Existing owner | Current responsibility | Change |
|---|---|---|
| `new_austellia.py` | Traced source map, rivers, bridges, towns, road network, coast | Keep authoritative, reuse source polylines; integrate any mapped tributaries without changing bridge safety |
| `frontier_world.py` | Biomes, sector constants, palettes, map helpers, camera-local landmarks | Replace visible sector-derived terrain with smooth influence fields while preserving APIs that old tests reference |
| `game.py` | `solid`, `can_move`, render order, props, horse collision, actor spawns | Add safe landform collision check and draw between ground and actors; preserve original 4800×3200 area |
| `tests/natural_terrain_test.py` | New tests | Determinism, visibility, crossing exclusions, route access, spawn safety, regression/performance sampling |

## Build order

1. Record important protected points: towns, quest nodes, waystations, original buildings, roads, river bridges, old-world handcrafted map. Add exclusion radii and route corridors.
2. Implement deterministic organic biome patches and simple contour shading (no solids yet); inspect the first camera views.
3. Add ridge polygons/cliff collision and authored passes. Verify graph reachability across regions.
4. Add connected tributary visuals, dry gullies, boulder clusters and biome-sensitive foliage.
5. Integrate terrain collision and spawn filtering, tune horse/escort clearance.
6. Compare representative screenshots and run Xvfb + full CI. Tune draw-call count for old Intel GPUs.

## Regression gates

- All 30+ mapped destinations, 13 waystations, original storyline mission points and both regional chapter sequences remain accessible.
- All road/rail bridge approaches stay traversable and water outside approved crossings stays blocked.
- Save/reload changes neither terrain geometry nor discovery/quest positions.
- Repeated queries at fixed coordinates are identical regardless of frame, camera position or restart.
- Sparse world views remain sparse and terrain features do not constantly cover enemy telegraphs or interactables.
- Measure draw-call budgets and frame times rather than claiming hardware frame rate from CI.

Documentation goal: the player should experience **landscape flow**—an open valley leading to a rocky pass, a creek following the low ground and a settlement logically sited beside the crossing—without noticing any underlying sector-grid boundaries.
