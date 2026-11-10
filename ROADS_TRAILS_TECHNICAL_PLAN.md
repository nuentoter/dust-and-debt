# Dust & Debt — Technical Implementation Plan: Roads, Trails & Landmarks

**Companion specification:** [ROADS_TRAILS_LANDMARKS_MILESTONE.md](ROADS_TRAILS_LANDMARKS_MILESTONE.md)  
**Milestone:** v2.9-map, GitHub issue #20 — prerequisite to autonomous travelers  
**Plan status:** IMPLEMENTATION PLAN ONLY. This commit does **not** alter world geometry, gameplay, or graphics.  
**Date:** November 9, 2026  
**Target:** Python 3 + Tkinter on low-end Archcraft/X11 hardware; no additional runtime dependencies  
**Source of truth:** New Austellia world dimensions **60,000×40,960**, atlas source dimensions **1448×1086**, existing town/river/road/rail/bridge definitions

## 0. Engineering decisions

1. **One world-space route database** for navigation, route-aware terrain protection, gameplay strokes, minimap, and parchment map. The atlas's historical traced geometry seeds that database; other modules must not independently invent transport routes.
2. **Graph reachability and physical traversability are separate gates.** Joining points in a graph is insufficient if water/buildings/ridge collisions prevent movement.
3. **Never merge rail and wagon traffic implicitly.** Railroad crossings over/near roads require explicit junction semantics. Rail bridges are not automatically wagon bridges.
4. **Author destination pads and last-mile paths**, not points at the middle of lakes or on cliff edges.
5. **Keep Cinder Creek's original 4,800×3,200 painting**, its quest scripts, and building collisions intact; solve the visible exit seam using a controlled starter-spur connector.
6. **Fix the actual render pipeline, not just the atlas.** `draw_local_geography`, `draw_atlas`, `draw_minimap`, `road_at`, `is_frontier_road`, and route-related procedural clutter must agree.
7. **Make graph indexing and art deterministic, immutable, and precomputed** at import/init time; camera draw and movement collision must not run graph construction.
8. **Stage behind verified commits and tests.** Each phase leaves `main` bootable, with feature-specific tests, and can be rolled back independently.

## 1. Actual integration audit (confirmed from current code)

| Present function/data | File | Engineering implication |
|---|---|---|
| `TOWNS_SRC`, `P()`, `ROADS_SRC` / `ROADS`, `RAILS_SRC` / `RAILS` | `new_austellia.py` | 13 wagon road polylines, 4 rail polylines, 34 site records. Preserve source coordinates; register persistent IDs for routes |
| `WATERWAYS`, `LAKES`, `COAST_POLYGON`, `BRIDGES`, `bridge_at`, `is_water` | `new_austellia.py` | Water collision is geometric and bridge-limited. A road visually painted across water is **not** guaranteed passable |
| `draw_local_geography()` | `new_austellia.py` | Currently renders rivers/lakes, 100-world-unit wagon roads, rails and bridge decks in a fixed order; route strokes must migrate without double-drawing |
| `draw_atlas()` | `new_austellia.py` | World-map vector map draws its own road/rail strokes; when an illustrated PNG is available, full-map display currently bypasses this vector route layer |
| `ROAD_X`, `ROAD_Y`, `START_SPUR`, `road_at()`, `WAYSTATIONS` | `frontier_world.py` | Old-grid road predicates still exist near the starter area. `START_SPUR` art is drawn separately and should converge with route data |
| `near_protected()`, `ROCKS`, `landform_solid()` | `natural_terrain.py` | Rocks are generated and filtered once at module import. New protected route corridors must be defined **before** rock filtering or via a compatible override |
| `Game.solid()` (line ~236), `can_move()`, `move_actor()` | `game.py` | Water, rock/cliff, then building checks. Test the precise player-radius/horse steps used in the game |
| `draw_far_terrain()` and `draw_world()` (~1993, ~2063) | `game.py` | Scene order is terrain → atlas geography → old parcel overlay → towns/landmarks/waystations → decoration → actors. Route art must respect this |
| `draw_scattered_props()` | `game.py` | Existing decor excludes `is_frontier_road()` only. Add new route corridor awareness before rendering shrubs/rocks across trails |
| `draw_minimap()` (~2262) | `game.py` | **Still renders straight ROAD_X / ROAD_Y grid strokes**, even while the full world uses traced atlas routes. Replace with the same route polylines |
| `draw_map()` (~2328) | `game.py` | Whole map may display `austellia_image` PNG, whereas zoomed map uses vector `draw_atlas`. Overlay added paths on **both** views |
| `draw_starting_transition()` | `new_austellia.py` | Keep the hand-painted map boundary visually soft; do not route inside existing impassable houses |
| `draw_waystations()`, `LANDMARKS` | `frontier_world.py` | 13 waystations should be real graph destinations; old "camp" landmark category is not proof of a new physical campsite |
| `Game.rest_at_frontier_camp()`, `camps_used`, `landmarks_found` | `game.py` | Optional future interaction integrations must not erase existing camp progression or discovery state |

**Known structural risk:** `new_austellia.travel_road()` currently includes both `ROADS` and `RAILS`; `frontier_world.road_at()` includes a legacy grid in one region. Neither is an adequate authoritative *wagon* graph. The milestone explicitly separates them.

## 2. System layout and dependency direction

```text
new_austellia.py (source atlas records; unchanged primitives)
          │
          ▼
frontier_routes.py  ◄── frontier_route_additions.py (audited authored connectors)
  normalize segments / snap / split / graph / spatial bins
          │                    └── route centerline predicate
          ├──► frontier_destinations.py (dry pads + designated trails)
          ├──► frontier_route_art.py (draw world + parchment + minimap)
          ├──► frontier_world.py (road_at / waystation adapter)
          ├──► natural_terrain.py (route exclusion for rocks and cliff collision)
          └──► game.py (collision + render + map UI + optional discovery)
```

**Avoid circular imports:** `frontier_routes` may import `new_austellia` and pure geometry helpers, but **must not import** `frontier_world`, `natural_terrain`, or `game`. `frontier_destinations` may depend on route geometry and atlas hydrology only; it must never invoke `Game.solid` during import. `frontier_route_art` depends on route/destination models but is called by game; it never calls game methods. Terrain can import a prebuilt route corridor function safely once the graph's import DAG has been validated.

**If shared route data must be used by both route validation and terrain collision:** extract a pure `frontier_route_geometry.py` layer (route polygons, segment AABBs, distance, bands) with no game/terrain imports. Keep `frontier_routes.py` for graph operations. Do not create a graph ↔ terrain cycle.

### Proposed source files and boundaries

| File | Contents / responsibilities | Public API |
|---|---|---|
| `frontier_route_geometry.py` (new) | Immutable source and authored route records, distance / projection / segment intersection, spatial hash, clear-width corridor checks | `ROUTE_SEGMENTS`, `route_surface_at(x,y,mode)`, `near_route(x,y,pad=0)`, `nearest_segment(x,y,kinds)` |
| `frontier_routes.py` (new) | Intersection splitting, shared node registry, adjacency, components, anchors and A*/Dijkstra | `ROUTE_GRAPH`, `nearest_route_anchor(point,mode)`, `route_path(a,b,mode)`, `connected_components(mode)` |
| `frontier_route_additions.py` (new) | Reviewed patch list: explicit endpoints, last-mile connectors, updated road spurs and dry trails (source atlas or world points indicated) | `ADDITIONAL_ROUTES`, `CONNECTOR_AUDIT` |
| `frontier_destinations.py` (new) | 12+ fishing-bank pads and 12+ camp pads, trailhead coordinates and IDs | `DESTINATIONS`, `destination_by_id(id)`, `destinations_in_view(bounds)` |
| `frontier_route_art.py` (new) | Layered camera-culling routes, shoulders/ruts, trails, signposts, bank/camp props, map/minimap overlays | `draw_routes(canvas,view,detail)`, `draw_destinations(...)`, `draw_route_map(canvas,view,rect,...)`, `draw_route_minimap(...)` |
| `docs/road_audit.json` (generated) | Deterministic baseline + post-fix graph diagnostics; sample failing positions and exemptions | JSON audit schema below |
| `tests/route_geometry_test.py` | Pure graph geometry, clipping, snapped intersections, mode eligibility | Run without Tk/Xvfb where possible |
| `tests/road_network_test.py` | All settlement, destination, bridge and actor-collision guarantees | Linux/Xvfb |
| `tests/route_render_test.py` | Graphics tiers, map/minimap alignment, culling and Low graphics | Linux/Xvfb |

`new_austellia.py` remains the **atlas data authority**, but a single route adapter must own rendered/usable roads after migration. Avoid copy/pasting a second unrelated `ROADS_SRC` coordinate list.

## 3. Precise data model

World coordinates are float or int in `[0,60000] × [0,40960]`; source atlas coordinates use `P(source_x,source_y)`. Declare coordinate system in every authored record and convert exactly once.

```python
from dataclasses import dataclass
from typing import Literal

Point = tuple[float, float]
RouteKind = Literal["wagon", "secondary", "trail", "rail"]

@dataclass(frozen=True)
class Route:
    id: str                    # stable: "atlas_road_00", "spur_mercy_flats"
    kind: RouteKind
    vertices: tuple[Point, ...] # WORLD coordinates only at runtime
    width: float                # rendered footprint (world units)
    source: str                 # "atlas" / "authored" / "starter"
    allowed: frozenset[str]     # "foot", "horse", "wagon", "rail"
    destination_ids: tuple[str, ...] = ()
    crossing_ids: tuple[str, ...] = ()

@dataclass(frozen=True)
class GraphNode:
    id: str
    point: Point
    route_ids: tuple[str, ...]

@dataclass(frozen=True)
class GraphEdge:
    id: str
    start_id: str
    end_id: str
    route_id: str
    length: float
    allowed: frozenset[str]

@dataclass(frozen=True)
class Destination:
    id: str                  # e.g. "fish_northstar_west"
    name: str
    kind: str                # "fishing", "camp", "trailhead", "overlook"
    point: Point             # safe dry pad or bank standing point
    trailhead: Point         # joins connected route
    route_id: str
    region: str
    artwork: str
    access: str              # "foot", "horse", etc.
```

Data values above are **proposed API contracts**, not existing committed game objects.

Suggested widths: **wagon 100**, **secondary 65**, **trail 28** world units, **rail 25**. Rendering shoulder extends beyond the visual core but collision clearance does not create a fake flat ford. Waypoint/destination connection tolerance should begin at **90** world units for road nodes, **35** for foot-trail joins; these are *initial tunables* to be measured against current atlas geometry. Do not silently join any route farther than the tolerance—emit an audit warning and author a real connector.

### Explicit route eligibility

| Route kind | Foot | Horse | Wagon | Rail | Comments |
|---|---|---|---|---|---|
| Wagon road | yes | yes | yes | no | Normal shared route |
| Secondary road | yes | yes | yes if width/grade pass | no | Some steep spurs foot/horse only |
| Trail | yes | yes if clearance permits | no | no | Camps and fishing paths |
| Rail | no by default | no by default | no | yes | Explicit foot/horse crossing only if safe and marked |

**Do not use rail as free wagon connectivity.** If a major town is only connected by rail, add a genuine road or mark a designed transfer that exists in gameplay.

## 4. Route graph construction algorithm

Implement in **pure Python**; no external graph/GIS dependency.

1. Import existing `ROADS` and `RAILS` once. Give each route a stable ID from its atlas index. Add audited `START_SPUR` and authored route patches by ID; preserve per-record source.
2. Expand each polyline into line segments, build axis-aligned bounding boxes (AABB), register segment metadata and indexing tiles (starting cell size ~512 world units). World/atlas geometry is fixed, so build once.
3. Detect endpoints near existing **same-mode** segment interiors using nearest projection. Record proposed joins and their distances; only auto-snap if within the bounded tolerance and a meaningful physical junction is intended.
4. Detect actual same-mode segment crossings with robust orientation/intersection tests. Reject or separately mark grade-separated crossings, especially rail/road.
5. Split every crossed segment at shared intersection or projected T-node positions. Sort split positions by parametric `t` along segment and collapse duplicates below a small epsilon.
6. Quantize/merge nodes using a bounded spatial key, not raw floating equality; deterministic ordering = original route IDs + vertex index + split index.
7. Add undirected graph edges weighted by Euclidean length. Attach allowed mode set from route record and any crossing restrictions.
8. Compute connected components per mode with DFS/union-find. Anchor every required town and waystation to a **nearby physically usable** graph point; avoid snapping to arbitrary rail stations if no shared pedestrian/wagon corridor exists.
9. Implement A* (Euclidean admissible heuristic) or Dijkstra as an offline/on-demand query. Return path nodes and route IDs; cache only bounded, frequently requested results if needed. Never recompute topology during frame updates.
10. Save graph snapshots/digest deterministically, and compare canonical route components before/after each connector change.

```python
def build_graph(routes) -> "RouteGraph": ...
def nearest_route_anchor(x, y, mode="horse", max_distance=450) -> "Anchor | None": ...
def route_path(start, end, mode="horse") -> "tuple[Point,...] | None": ...
def connected_components(mode="wagon") -> "tuple[frozenset[str],...]": ...
def point_in_route_corridor(x, y, radius=11, kinds=None) -> bool: ...
```

**Important edge case:** A segment intersection is not a safe junction when `is_water` blocks its node, when a cliff cuts the road, or when one crossing is rail-only. Graph topological joins must carry a **physical-validation status**. A deliberate unbuilt river crossing should fail validation rather than become a navigable edge.

## 5. Physics / obstacle / bridge integration

### Pure validation versus game collision

Avoid a circular dependency between `Game.solid` and the route clearance test:

```text
route core (pure geometry) ─────► corridor checks
             │                         │
             ▼                         ▼
natural terrain rock filtering   Game.solid() asks existing
(no Game import)                 is_water/landform/buildings
             │                         │
             └──────────► offline route sampler ◄─────────┘
```

**Route clearance isn't a blanket "ignore all collision" switch.** For a proposed trail crossing a mountain, change the trail geometry to use a gap/valley or author a passage after verifying terrain. When excluding preexisting rocks from new routes, filter or clip rocks deterministically, then re-run collision sampling. Never mark a new overwater trail safe solely because a corridor predicate returns true.

### Sample-based acceptance

- Sample centerline every **≤10 world units** on each segment for foot radius 11 and horse approximate step envelope (measure real mounted collision code before final threshold). For width-sensitive roads, sample offsets at both edges (center ± (half usable width − radius)).
- Compute clearance separately from `is_water`, `landform_solid`, building footprints, and any legacy/start-zone obstacle. Include exact failing route, segment index, longitudinal t, world x/y, reason and actor radius.
- At river crossings, compare `BRIDGES` centerline orientation and deck half-width to actual `bridge_at()`; verify entry/midspan/exit and non-crossing bank water remains solid.
- Check `coastal_water` and `lake_at` separately; river bridge exemptions must never create a pass through ocean/lake.
- Validate spurs end with at least one reachable, collision-free approach point. If the historic town center is protected but a street approach is not, anchor to the street.
- Keep mission hardcoded positions, `safe_enemy_spawn`, bounty targets, waystation and escort stops explicitly protected. Run existing tests after every route change.

**Audit sample schema:**

```json
{
  "schema": 1,
  "world": [60000, 40960],
  "baseline": {"wagon_polylines": 13, "rail_polylines": 4, "waystations": 13},
  "graph": {"wagon_components": null, "unreachable_town_ids": [], "unreachable_waystation_ids": []},
  "crossings": [{"route_id": "atlas_road_00", "river": "Sable River", "status": "unchecked"}],
  "blockages": [{"route_id": "pending", "segment": 0, "xy": [0, 0], "reason": "example only"}],
  "exemptions": ["calhoun_island", "herons_key", "drake_isles"]
}
```

Values above are **schema examples**, not measured audit results. The implemented audit command must populate real measurements rather than copying these placeholders.

## 6. Authoring fishing banks and campsite destinations

Start with the 12 fishing-site targets and 12 camp targets in the companion spec. Site coordinates are **not yet selected**. Store their final coordinates as stable world points with descriptive region/site metadata.

### Fishing bank algorithm

1. Choose a named water body from the atlas (`WATERWAYS`, `LAKES`, coastline as appropriate).
2. Sample candidate shore locations by projecting a point outward from river tangent or lake ellipse normal; choose dry land at least `player radius + margin` clear of water and buildings.
3. Test approach radius around that point and avoid beaches on steep/cliffside terrain.
4. Find a physically accessible nearest trailhead on an existing wagon/secondary route.
5. Author 2–8 waypoints forming a trail around obstacle/river geometries; do **not** rely on straight-line interpolation across water.
6. Name and register the destination; add its trail to route graph and render database.
7. Add visual bank wear/reeds/rocks/signpost with no player-blocking prop at the standing pad.
8. Produce a deterministic route-to-bank reachability and dry-bank assertion.

### Camp pad algorithm

1. Pick region/setting, find a 100–180-unit open patch by collision sampling around center (actual footprint configurable).
2. Reject pads too close to town interior doors, job objective markers, cliff edges, rivers or rock cores.
3. Connect pad to road network via a narrow branch trail; preserve intended remoteness, but not accidental isolation.
4. Add a restrained clearing plus tent/fire ring/bedroll. Props should be decorative unless explicitly designed as colliders.
5. Tag an official trailhead/fork sign where a rider would notice the path.
6. Persist discovery IDs only if a discovery feature is implemented. **Do not repurpose** `camps_used` without tested migration.

### Fishing and camping minimums

- **Fishing ≥12**: two each at Frostvein/Northstar lakes, Sable River, Blackwater River, Roan Creek, Riversend Channel, Dustwell Wash, Cypress Bayou, Harper's Landing, Saint Brigid's Port (per source spec).
- **Camps ≥12**: Dustwell, Cinder Ridge, Graystone Range, Everwood, Cedarheart, Heartland Plains, Sable River, Roan Creek, Red Thorn Canyon, Sundown Plateau, Red Mesa Buttes, Cypress Bayou.
- All pads on land, all approaches traversable, all camp/fishing icons tied to real trail endpoints. Offshore islands excluded pending boats/ferries.

## 7. Rendering pipeline refactor

### Target world draw order

```text
ground + biome swaths
    ↓
nonblocking ridge silhouettes, washes, background rocks
    ↓
rivers / lakes / coastline (from atlas)
    ↓
wagon + secondary road surfaces, shoulders, ruts
    ↓
foot/horse trail surfaces, erosion marks
    ↓
rail bed + ties
    ↓
explicit bridges, decks and bank transitions
    ↓
original 4,800×3,200 artwork and boundary feathering (where present)
    ↓
towns, landmarks, waystations
    ↓
fishing/camp clearings, signposts, route props
    ↓
safe, route-excluded scatter props
    ↓
actors, player, projectiles, HUD
```

**Migration strategy:** Keep `new_austellia.draw_local_geography()` responsible for water and coast. Extract road/rail/bridge drawing to the route-art layer only after tests prove output parity, or add explicit `draw_routes=False` flag defaulting to historical behavior and switch `game.py` to new rendering atomically. Never render both roads in the same viewport. Bridges must be on top of rivers and routes. Any starting-map art overlap needs a targeted transition renderer rather than double-opaque bands.

### Tier-specific art rules

- Wagon: dirt shoulder, dual faint ruts, 100-unit center, rounded/smoothed joins; color derived from region/biome.
- Secondary: 65-unit uneven packed path, subdued shoulder, partial wheel marks.
- Trail: ~28 units, soft worn-earth center, sparse dashed scuffs, non-periodic deterministic edge spots.
- Rail: separate bed and tie cadence; only real rail bridge decks.
- Bridge: road deck width, rail width and crossing orientation must correspond to the route that generated it; no one-size-fits-all painted deck.
- Destination: restrained physical props and route signs; never conceal quest/NPC interaction prompts.

**Camera-local art algorithm:** query segment bins overlapping viewport expanded by maximum stroke/prop width; draw each visible continuous polyline once where possible; trim to view bounds; use deterministic hash of route ID/segment index for ruts and occasional gravel. No full-map scan of every tiny dot during each frame. Low detail may drop shoulder noise/vegetation but must keep every navigable route, bridge, junction sign and destination pad.

### Minimap and parchment

1. Replace `Game.draw_minimap` loops over `ROAD_X` and `ROAD_Y` with clipped actual roads/secondary/trails in same world-space projection as players and markers. The old grid should not remain visible as imaginary roads.
2. On `draw_map()`, overlay map routes over both background modes: full-map illustrated `austellia_image` and zoomed vector `draw_map_background`. Avoid repainting canonical atlas roads twice by using incremental/overlay render flags.
3. For atlas route projection use `point_on_map`/`MAP_RECT`; ensure clipping uses **screen rectangle** after world→map transform. The current `draw_atlas()` helper clips after projection; build tests for left/top/right/bottom bounds and map zoom to avoid misinterpreting world-space origin.
4. Use distinct marks: thick brown wagon, lighter brown secondary, thin dotted foot/horse trail, red/dark rail; consistent camp/fishing glyph legend.
5. Add destinations only when physically implemented and appropriately discovered. Map controls Tab, Enter, Z and click must continue to work.
6. Verify no diverging coordinates among game-world strokes, minimap strokes, and full atlas route overlay.

## 8. Deterministic build and test tools

Create a CLI command `python tools/audit_routes.py --json docs/road_audit.json` (write from current committed route data, no network). Support `--check` to fail when implementation gates regress.

### Unit tests (pure and fast)

- Segment intersection: crossing, parallel, collinear overlap, T junction, near miss, endpoint-on-segment.
- Snap threshold boundary and deterministic node IDs.
- Segment-splitting invariants: total edge length near source length; no zero-length edges.
- Rail/wagon separation.
- A* optimality versus Dijkstra on small known fixtures.
- World→atlas→world point round-trip within tolerance.
- Stable graph checksum across repeated initialization.

### Integration tests (Tk/Xvfb)

- 12/12 core towns connect on wagon-eligible graph and have collision-safe access pads.
- 13/13 waystations match actual graph anchors; starting Cinder Creek join verified.
- ≥12 fishing sites and ≥12 camp sites, with dry pads and branch trails.
- All 5 named rivers, lake shores and coast crossings physically checked; every auto-derived bridge has matching deck/passability.
- No solid rocks/buildings/water on sampled required traversable corridors.
- Existing Sheriff Bell mission steps, two regional investigations, lasso/hogtie/surrender, road escort and courier tasks still work.
- Save/load (including corrupt-primary backup recovery) preserves progress, waypoint and discovery if implemented.
- Render snapshots/object counts for ≥6 reference views: old parcel seam, grass junction, forest trail, mesa/desert road, river bridge, fishing bank, campsite.
- Screen and map overlays never exceed viewport/UI bounds; F8 Low detail keeps roads/trails visible.
- Tests must keep current audio tracks optional; mocked or silent backend acceptable.

### Performance methodology

Measure with `time.perf_counter()` and `canvas.find_all()` in a local test harness. Compare before/after at fixed camera positions and identical world seeds: (a) Cinder Creek seam, (b) dense town, (c) river crossing, (d) rocky valley, (e) forest with trails, (f) camp cluster. Record p50 and p95 frame-render time, max Tk Canvas object count, import/init time, graph build time, and peak process RSS where available. **Baseline must be recorded first; no invented FPS threshold.**

Optimization order: cull → index/bucket → batch nearby strokes → cache style/segment projections → reduce decorative density. Never reduce route legibility to inflate a benchmark.

## 9. Execution sequence / commit groups

Every phase is a separate **mergeable** group. GitHub-first: push to `main`, run Linux CI, address regressions, then continue. The user does not need to test each group, only the integrated milestone unless issues arise.

### Group 0 — Baseline and failing audits

**Files:** `tools/audit_routes.py`, `tests/route_geometry_test.py`, `docs/road_audit.json`  
**Tasks**
- [ ] Extract baseline world/atlas quantities, every route polyline, 34 site IDs and 13 waystation records.
- [ ] Check existing bridge count, endpoints and nearest route; emit disconnected/missing locations.
- [ ] Record six camera baseline draw metrics.
- [ ] Add graph fixture tests and report missing links as expected, without treating baseline failures as final release failures.

**Gate:** Reproducible report checked into repo; no gameplay changes.

### Group 1 — Pure route core

**Files:** `frontier_route_geometry.py`, `frontier_routes.py`, `tests/route_geometry_test.py`  
**Tasks**
- [ ] Define immutable route model from `ROADS`, `RAILS`, `START_SPUR`.
- [ ] Implement segment spatial hashing, snapped intersections and strict mode isolation.
- [ ] Build deterministic adjacency/components/path search and audit interface.
- [ ] Test exact canonical route graph and performance.

**Gate:** Unit tests pass; `game.py` unchanged.

### Group 2 — Real road fixes

**Files:** `frontier_route_additions.py`, atlas adapter, `frontier_world.py`, `natural_terrain.py`, `tests/road_network_test.py`  
**Tasks**
- [ ] Connect missing mainland towns and 13 waystations; fix Brimstone/remote approach register.
- [ ] Join `START_SPUR` to painted traversable trunk, not old invisible grid.
- [ ] Align wagon water crossings to actual bridges; forbid wagon travel on rail-only spans.
- [ ] Extend rock/prop protection consistently without water bypass.
- [ ] Re-run route centerline and margin collision sampler.

**Gate:** 12 core towns + 13 waystations reachable on **both graph and physical map**; no known broken crossings.

### Group 3 — Fishing/camp routes

**Files:** `frontier_destinations.py`, additions module, art module tests  
**Tasks**
- [ ] Author 12+ validated fishing access banks and 12+ camps with route-attached pads.
- [ ] Draw narrow, curved side trails around ridge/water hazards.
- [ ] Add small environmental props and signed forks.
- [ ] Validate approaches and gameplay camp compatibility.

**Gate:** Every new destination connected, dry and visually reachable; no false water paths.

### Group 4 — Rendering and atlas consistency

**Files:** `frontier_route_art.py`, `game.py`, `new_austellia.py`, `tests/route_render_test.py`  
**Tasks**
- [ ] Migrate the in-world routes and bridges to a unified, layered renderer.
- [ ] Replace minimap legacy grid with authored routes.
- [ ] Overlay new trail/route graphics on both illustrated and vector maps.
- [ ] Add biome-specific shoulders/ruts and restrained route/landmark details.
- [ ] Verify F8 Normal/Low, screens, interior overlays and path readability.

**Gate:** In-world/minimap/atlas same source coordinates; visual and Canvas count checks pass.

### Group 5 — Integrated acceptance and handoff

**Files:** Linux Actions workflow, `docs/road_audit.json`, README, milestone issue/roadmap  
**Tasks**
- [ ] Verify old mission, bounty, regional stories, road jobs, captures and saves.
- [ ] Run all project CI checks and record actual green run URL.
- [ ] Document on-hardware Archcraft FPS/memory observations.
- [ ] Provide one user ride itinerary: Cinder Creek → Galloway → Roan Creek → Northstar fishing trail → Everwood camp.
- [ ] List any deliberate isolation or transport exceptions, known art tradeoffs and future traveler API details.
- [ ] Mark issue #20 complete only after all gates and user sign-off.

**Gate:** Functioning navigation, real graph reachability, full CI and user-approved ride.

## 10. Precise rollback / data compatibility policy

- Retain historical atlas polylines until adapters and tests prove equality at bridge/town anchors.
- Preserve existing save schema, story and waypoint fields. Add `discovered_destinations` only if needed, with default `[]` migration and version-guarded tests; no wholesale save reset.
- When changes threaten quest and bounty pathing, prioritize relocation of new scenery/rock collision, not relocation of hardcoded mission NPCs.
- Ship route art and route graph behind a single engine adapter; no duplicate collision vs painting implementations.
- Revert failed group to its preceding stable GitHub commit rather than stacking fixes on broken gameplay.

## 11. Implementation completion / release gate

This technical plan is executable once each group is translated into commits. Actual milestone completion requires **12/12 mainland towns, 13/13 waystations, 12+ fishing banks, 12+ camps, 100% checked road/river bridges, no unexplained disconnected road graph, normal + low-detail route visibility, passing regression CI, and user long-ride acceptance**.

**Not done yet:** baseline graph measurements, route repairs, new bank/camp coordinates, actual route graphics, tests, benchmarks and hardware validation. Do not describe those as implemented before their corresponding commits and checks.
