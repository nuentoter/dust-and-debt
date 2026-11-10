# Dust & Debt — Roads, Trails & Landmarks Pass

**Milestone:** v2.9-map / v3.0 prerequisite  
**Status:** SPECIFICATION APPROVED FOR IMPLEMENTATION; NO ROUTE/GRAPHICS CHANGES IN THIS COMMIT  
**Last revised:** November 9, 2026  
**Dependencies:** Existing New Austellia atlas, 60,000×40,960 world, Rivers/Ridges/Stone first pass, original Cinder Creek parcel  
**Sequence:** Finish and test **before** implementing autonomous traveler pathfinding  
**Repository:** `nuentoter/dust-and-debt` / `main`

**Implementation architecture and staged commits:** [ROADS_TRAILS_TECHNICAL_PLAN.md](ROADS_TRAILS_TECHNICAL_PLAN.md)

## 1. Goal and player experience

Create a **legible, continuous travel network** across all populated mainland New Austellia. Towns should be reachable by believable wagon roads; smaller settlements and businesses should connect by lesser roads; camps, fishing holes and scenic sites should be reachable by well-authored foot/horse trails branching from that network. The visual language must explain where to travel without requiring HUD waypoints.

**Player-level acceptance:** A player starting near Cinder Creek can follow recognizable routes to settlements, find signposted forks to camps and fishing banks, and arrive at their destinations without unexplained water, rock, cliff or invisible-grid obstruction. The same routes must support later NPC travelers.

### Non-goals in this milestone

- No traveling NPC simulation, roaming crowds, procedural traffic or fishing minigame yet.
- No 3-D graphics, new GPU libraries or wholesale world art replacement.
- No arbitrary bridges across the Auburn Gulf; the Calhoun/Heron/Drake offshore islands require a separately planned ferry/boat solution, not fictional land roads.
- No rewrite of the original 4,800×3,200 Cinder Creek buildings, storyline, mission triggers or save progression.
- No assumption that the existing route network is already complete merely because polylines are drawn.

## 2. Baseline inventory: facts from current source

| Existing source | Current reality | Required action |
|---|---|---|
| `new_austellia.py` | 60,000×40,960 world; **35 authored sites** in `TOWNS_SRC` (includes water/landmarks/islands); **13** `ROADS_SRC` wagon paths; **4** `RAILS_SRC` corridors; **5** named waterways and **2** lakes | Use original atlas as the geographic authority. Analyze line endpoint and midsegment connections before modifying them |
| `new_austellia.py` | `BRIDGES` derives rail/road intersections with water; `is_water` blocks other water except valid bridges and protected settlement parcels | Test all river/route intersections, visible bridge decks, passability and lack of invisible crossings |
| `frontier_world.py` | **13** named `WAYSTATIONS`, associated with atlas transport hubs; `START_SPUR` joins early authored parcel toward outside world; `ROAD_X/ROAD_Y` is still present for some old nearby road behavior | Retire/bridge over visible-vs-logical legacy grid discrepancy in a controlled change; never strand the first town or break jobs |
| `natural_terrain.py` | Ridges, dry washes, deterministic rocky clusters; `near_protected` excludes current road/rail/town corridors | Extend protected travel corridors to new roads/trails before enabling collision; avoid rock/cliff obstructions |
| `game.py` | Geographical drawing + old authored starter parcel + landmarks, waystations and collision | Integrate new renderer between ground and markers; add HUD/map trail indicators judiciously |
| `frontier_world.py` | `LANDMARKS` infers categories from existing atlas sites, including camp-like ranches | Keep that classification separate from **new physical campsite destinations**; don't assume every camp label is a camp clearing |

**Critical observation:** A series of rendered strokes is not a connected, walkable route graph. Railway tracks, wagon roads and foot trails must be separately classified for traveler eligibility and player wayfinding; drawing a route across the map does not prove that both endpoints are reachable.

## 3. Settlement access audit

Keep this register current as each destination is audited. Record nearest route anchor, actual segment/junction, reachable approach position, water crossing, obstruction result, visual result and regression ID. Use the real position from `TOWN_BY_ID` rather than retyping coordinates.

### Core mainland town network (must have usable road access)

- [ ] Galloway (`galloway`)
- [ ] Saint's Hollow (`saints_hollow`)
- [ ] Roan Creek (`roan_creek`)
- [ ] Blackwater Crossing (`blackwater_crossing`)
- [ ] Larkfield (`larkfield`)
- [ ] Harper's Landing (`harpers_landing`)
- [ ] Valleyford (`valleyford`)
- [ ] Dustwell (`dustwell`)
- [ ] Riversend (`riversend`)
- [ ] Saint Brigid's Port (`saint_brigids`)
- [ ] Bayou Haven (`bayou_haven`)
- [ ] Elmshade (`elmshade`)

### Secondary mainland settlements, worksites and transport hubs (must have an approach appropriate to type)

- [ ] Hollow Bend Post — road/ferry-bank access review
- [ ] Pineheart Trading Post — road from Roan Creek as mapped
- [ ] Cinder Ridge Camp — road to Galloway corridor
- [ ] Silvervein Mine — road to Blackwater route
- [ ] Iron Mesa Fort — **check** for missing last-mile connection
- [ ] Stonewall Fort — Galloway spur
- [ ] Brimstone Point — **audit explicitly; no direct endpoint in baseline `ROADS_SRC`**
- [ ] Bearclaw Lookout — ridge/bayou approach
- [ ] Mercy Flats Ranch — **check** for connector from nearby trunk
- [ ] Prairie View Ranch — Blackwater–Valleyford spur
- [ ] Black Rock Ranch — **check** last-mile connection
- [ ] Rattler's Rest — off-road ruin: signed rough trail, not necessarily wagon road
- [ ] Old Kestrel Mill — remote ruin trail from Harper's corridor
- [ ] Widow's Pass — pass approach from Saint's Hollow
- [ ] Lone Pine Mine — Riversend road spur
- [ ] Driftwood Springs — last-mile access from Stonewall corridor
- [ ] Original Cinder Creek playable parcel — verify `START_SPUR` joins a *visible, traversable* trunk route without legacy grid teleports

### Non-road natural sites: access should make sense without false land bridges

- [ ] Frostvein Lake — shoreline approach; trail stops **on dry land**, not lake center
- [ ] Northstar Lake — fishing trails to more than one shore-access point
- [ ] Highfalls — lookout/viewpoint trail to dry side of falls
- [ ] Calhoun Island — classify as **water-only access**, defer boats/ferries
- [ ] Heron's Key — water-only access
- [ ] Drake Isles — water-only access

**Audit rules:** Every mainland `city/town/settlement/port` gets a route to the shared wagon component. Sites of type `post/fort/ranch/mine/camp/tower` get a clear side road or named trail with explicit reason for any exception. Ruins, passes, lakes, falls and springs should have purposeful last-mile trails. Islands are explicitly exempt from the mainland road graph but **must not appear reachable over invisible dry land**.

## 4. Route taxonomy and graph contract

- [ ] Add a single authoritative data module, e.g. `frontier_routes.py`, with immutable IDs, `kind` (`wagon`, `secondary`, `trail`, `rail`), world-space polyline vertices, optional destination/region IDs, travel eligibility, bridge references and `source` (`atlas`/`authored`).
- [ ] Preserve `ROADS_SRC` and `RAILS_SRC` geometry as baseline; adapt via explicit documented connectors/realigned points, not randomized generation.
- [ ] Convert crossings and endpoint-to-midsegment joins into *shared graph nodes* through a bounded snap tolerance; never assume two crossing strokes are connected without geometric/junction validation.
- [ ] Build a cached adjacency graph once; provide `nearest_route_anchor`, `route_neighbors`, `route_path(start,end,mode)`, and `route_accessible` without calculating all-pairs routes per frame.
- [ ] Assign wagon eligibility only to actual wagon roads and approved crossings. Rails stay separate unless an explicitly shared pedestrian corridor is authored. Foot/horse trails may be narrower and non-wagon.
- [ ] Ensure every required mainland settlement and 13 waystations belongs to the same reachable wagon component **or** list an explicit documented special-case transfer that is actually implemented.
- [ ] Measure endpoint-to-route offset, longest disconnected tail, road gap length, graph component sizes, and unreachable site IDs. Print a deterministic machine-readable report.
- [ ] Require at least one meaningful alternative trunk connection where geography permits; don't force loop roads through protected mountains or water.
- [ ] Ensure no isolated microsegments are left on the map unless they end at a documented trailhead, dead-end camp, overlook or mine.

### Passability checks

- [ ] Sample all road centerlines and edges at intervals no larger than the player's collision radius/route width tolerance; use `Game.solid` or lower-level shared collision APIs.
- [ ] Sample all trail centerlines for on-foot and mounted movement widths, including bends and approach pads.
- [ ] Check against `is_water`, `bridge_at`, `landform_solid`, buildings and existing handmade-world obstacles.
- [ ] A route over a waterway must have a bridge/ford/ferry surface visibly matching the **collision passable footprint**; no unpainted cross-water gaps.
- [ ] No new trail should cross a rock core, ridge wall or large water body merely because it draws on top of them.
- [ ] First and last route nodes must stop near a usable entry point rather than entering an interior, building wall, lake center or other impassable coordinate.
- [ ] Connectivity report distinguishes *graph connection* from *physical movement passability*; both are required for acceptance.

## 5. Trails, fishing access and camp destinations

Author **real coordinate destinations** in a dedicated `frontier_destinations.py` (stable ID, name, type, anchor point, approach point, region, linked trail ID, visual props). These are new reachable locations—not just automatic markers over random rivers.

### Fishing access (minimum 12, with geographic diversity)

- [ ] Two distinct **Frostvein Lake** dry-bank fishing approaches, each with a trailhead
- [ ] Two **Northstar Lake** shore approaches on accessible banks
- [ ] One **Sable River** eddy/pool away from bridge conflict
- [ ] One **Blackwater River** bank near a sensible road spur
- [ ] One **Roan Creek** pool with visible branch trail
- [ ] One **Riversend Channel** bank platform/pull-off
- [ ] One **Dustwell Wash** seasonal-bank access (mark as seasonal where appropriate)
- [ ] One **Cypress Bayou** shore/fishing clearing, avoiding deep wetlands
- [ ] One **Harper's Landing** public river landing / fishing access
- [ ] One **Saint Brigid's Port** pier/shore access, only if current port collision allows it

All 12 are placement **targets**, not assertions that usable coordinates already exist. Select and validate precise world positions during implementation using hydrology geometry and the atlas; avoid the centers of rivers/lakes.

**Fishing destination acceptance**
- [ ] Approach coordinate is dry, collision-clear and connected to the route graph.
- [ ] The fishing bank is visually readable (worn approach, reeds/logs/river stones, optional small deck) without obstructing bridges.
- [ ] Destination is discoverable by an unobtrusive trailhead/signpost and map legend; no fishing mechanic required yet.
- [ ] At least one bank per major named inland water region where physically reasonable; don't allow fishing from offshore islands without a boat.

### Known camping spots and trailheads (minimum 12)

- [ ] Dustwell roadside camp / waystation integration
- [ ] Cinder Ridge high-desert camp
- [ ] Graystone Range mountain shelter
- [ ] Everwood Forest hunter's camp
- [ ] Cedarheart Woods shaded camp
- [ ] Heartland Plains wagon camp
- [ ] Sable River bank camp **above ordinary flood edge**
- [ ] Roan Creek riverside camp on dry ground
- [ ] Red Thorn Canyon sheltered camp / side trail
- [ ] Sundown Plateau overlook camp
- [ ] Red Mesa Buttes camp
- [ ] Cypress Bayou raised-ground camp (not floating in water)

**Camping destination acceptance**
- [ ] Camps have a distinguishable approach trail, dry open pad, tent/fire ring/bedroll-style readable prop arrangement, and safe dismount/pick-up area.
- [ ] Existing gameplay camps (`camps_used`, `rest_at_frontier_camp`) remain functional; extending rest interaction is optional only after conflict checks.
- [ ] Camps avoid cliff edges, deep water, mission spawn pads, town business entrances and protected no-spawn areas.
- [ ] Trailheads originate from a road or a connected intermediate trail; intentionally remote camps can be a signed dead-end spur.
- [ ] Every new named camp and fishing destination appears in the route/destination audit and has a repeatable test.

## 6. Rendering and map graphic quality pass

### Road surface language

- [ ] **Primary wagon roads:** 90–110 world-unit packed-earth footprint, feathered colored shoulder, a dirt-center variation, paired faint wheel ruts and occasional compacted gravel. Consistent apparent width even on angled segments and joints.
- [ ] **Secondary roads:** 55–80 units, slightly darker/rougher surfaces, narrower shoulder and less continuous wheel rut marks.
- [ ] **Foot/horse trails:** 18–36 units, irregular/scuffed edges and small interrupted segments. Distinct from wagon roads but readable in forests, mesa and scrub.
- [ ] **Railroad:** visually separate rail-bed and ties, not mistaken for public wagon road; keep water crossings aligned.
- [ ] Color within local biome palette; not identical beige strokes across grass, forest, desert, rock and swamp.
- [ ] Smooth bends via restrained subdivision/interpolation that **does not alter collision or travel graph**; preserve canonical junctions and bridge endpoints.
- [ ] Route edges cannot abruptly stop at town overlays, waystations, bridges, atlas cut lines or the starter parcel.
- [ ] Trail forks and signed turnoffs readable from top-down gameplay without relying on world-map annotations.

### Route-side art and destinations

- [ ] Compact posts/signs at meaningful forks, e.g. "ROAN CREEK / NORTHSTAR LAKE"; use authoritative destinations and only actual path junctions.
- [ ] Periodic hitching posts, tire/hoof wear, native scrub and sparse stones near roads; none block the route centerline.
- [ ] Fishing markers: slight trodden ramp, bank vegetation, rocks, reeds, optional short dock **only** on suitable banks.
- [ ] Camps: flat clearing, muted tent/fire pit/packed ground, weathered equipment; silhouettes must remain legible at normal gameplay zoom.
- [ ] Distinct river crossings (road bridge vs rail), wet edges and banks, no duplicate bridges or fake fords.
- [ ] Avoid square tile seams and regular repeated prop spacing; vary via deterministic seeded microdetail **after route clearance**.

### World map and readability

- [ ] Update parchment/illustrated atlas overlay: strong but not overpowering wagon routes; thin dotted trails; rail as separate line style; fork/bridge icons; destination legend.
- [ ] Show camp and fishing icons with a consistent vocabulary, ideally revealed when discovered; optional "show all trails" map filter later.
- [ ] Place map pins at reachable bank/clearing approaches, *not* the center of a lake or waterfall.
- [ ] Ensure map scaling `MAP_RECT` and the drawn gameplay route share identical world coordinates; no visually promising but unwalkable shortcuts.
- [ ] Review the 4800×3200 original art seam and `START_SPUR` transition at the edge of the starting world.
- [ ] At least six representative reference screenshots/review captures: grassy town junction, desert wagon road, forest foot trail, river bridge, fishing approach, camp clearing (record only after actual screenshots exist).

### Tkinter/X11 performance constraints

- [ ] Keep camera-local culling for lines, dots, signs, banks, and props.
- [ ] Precompute route geometry, adjacency, deterministic decoration and collision exclusions; no expensive pathfinding or random point generation every frame.
- [ ] Audit `canvas.find_all()` item count and panning responsiveness in both normal and Low detail (F8 → 1).
- [ ] Low detail removes microdetail first; **never remove critical routes, trails, bridges or destination readability**.
- [ ] Avoid Pillow at runtime, OpenGL requirements, large mandatory image textures or heavyweight new dependencies.
- [ ] Benchmark a modest Archcraft/X11 laptop when available; capture local frame pacing, memory, route draw object counts and any hitch around transitions.

## 7. Data ownership / implementation architecture

| Module | Proposed ownership | Constraints |
|---|---|---|
| `new_austellia.py` | Canonical traced atlas town/rail/road/water geometry and bridges | Minimal deliberate edits; track each change in audit |
| `frontier_routes.py` **new** | Normalized route polylines, intersections/snap points, graph, path querying, clearance corridor masks | Deterministic, Python standard library only; no Tk dependencies |
| `frontier_destinations.py` **new** | Authored dry-bank fishing sites, campsite pads and trailhead metadata | No invented placement until atlas/collision validation |
| `frontier_route_art.py` **new** | Camera-culled wagon/secondary/trail strokes, signs, site props and optional terrain texture | Respect Low detail, avoid heavy draw calls |
| `frontier_world.py` | Adapter for existing waystations, landscape route queries and legacy starter corridors | No invisible road-grid shortcuts |
| `natural_terrain.py` | Route-exclusion masks for new paths, gentle terrain clearance and rock placement | Route corridors override rock conflicts only where explicitly authored |
| `game.py` | Integrates drawing, collision, route hints, map markers, optional discovery and later NPC compatibility | Preserve missions, bounty capture, music, settings, save |
| `tests/road_network_test.py` **new** | Graph connectivity, crossings, destinations, collision, route rendering, save/smoke checks | Add to Linux Actions; no real audio device needed |

**Suggested pipeline:** canonical routes → derive snapped junction graph → select validated dry destination pads → author side trails from nearest safe trunk → register clearance bands → render canonical route tiers → overlay signs/markers → unit and integrated playtests.

## 8. Work phases: implementation checklist

### Phase A — Inventory and road-network audit (blocking)
- [ ] Dump all 13 road and 4 rail paths with endpoints, vertex counts and connected components.
- [ ] Identify true junctions including rail/wagon crossing semantics and roads meeting midsegments.
- [ ] Calculate nearest usable road attachment for all 35 atlas sites and 13 waystations; label mainland vs water-only.
- [ ] Audit every existing `BRIDGES` intersection and test whether collision and deck art match.
- [ ] Generate and commit `docs/road_audit.json` or Markdown report with dated measurements, disconnected IDs and proposed fixes.
- [ ] Write **failing first** graph tests for missing town/road connectivity; don't hide failures by marking sites optional.

### Phase B — Fix primary and secondary network
- [ ] Repair missing endpoint-to-trunk connections and visible road discontinuities.
- [ ] Verify all 12 major mainland towns are in shared wagon component, including the Cinder Creek connection.
- [ ] Add appropriate last-mile connectors for posts, ranches, forts and mines; account explicitly for Brimstone Point and Mercy Flats.
- [ ] Preserve genuine bridge/rail grade separations and passable decks.
- [ ] Resolve / document legacy `ROAD_X/ROAD_Y` and `START_SPUR` transition instead of leaving an invisible functional grid.
- [ ] Validate AI-compatible road graph for later travelers; no autonomous travelers yet.

### Phase C — Fishing and camping access
- [ ] Author **12+** dry-bank fishing destinations with named routes and pads.
- [ ] Author **12+** distinct, collision-clear camp destinations with trailheads.
- [ ] Add connected side trails from existing roads/trails; fit paths around hydrology/ridges without arbitrary cutting.
- [ ] Add minimal campsite/fishing-bank environmental props.
- [ ] Validate on-foot/horse approach and no dead-end softlocks around rocky terrain.

### Phase D — Route presentation
- [ ] Render primary, secondary, rail and foot trail tiers with intentionally distinct visual language.
- [ ] Add junction shaping, wheel ruts, shoulders, trail erosion and biome color variation.
- [ ] Improve crossings, bank transitions, campsite/fishing identity and signposts.
- [ ] Update parchment map legend and discovered destination markers; no false map routes.
- [ ] Run Normal + Low graphics sweeps to confirm functional visibility and acceptable draw load.

### Phase E — Verification, release candidate
- [ ] Run graph reachability tests for all mainland settlements and 13 waystations.
- [ ] Validate every camp/fishing pad + first/last 150 units of every approach trail with player collision.
- [ ] Validate each road/rail water crossing and every known protected bridge.
- [ ] Run starting-area mission, bounties alive/dead, field arrest, escort, courier, waystation, regional-story and save/reload regressions.
- [ ] Run map zoom/pan and scene drawing tests at multiple biome corners; measure item count.
- [ ] Run Linux/Xvfb CI suite to green; record exact CI run link (do not infer from empty commit-status responses).
- [ ] Have user make one practical long ride: Cinder Creek → Galloway → Roan Creek, then branch to one lake fishing site and one forest camp; record snags.
- [ ] After green CI and user approval, close this milestone and **only then** begin traveler traffic/AI pathing.

## 9. Measurable exit criteria

| Gate | Threshold |
|---|---|
| Mainland core towns | **12/12** physically accessible from the principal road component, or a consciously designed verified transfer |
| Named waystations | **13/13** traversable approaches |
| Major bridges/crossings | **100%** audited with graphics and collision aligned |
| Fishing sites | **≥12** named dry-bank destinations with connected traversable trails |
| Camps | **≥12** traversable, visually distinctive clearings with trail access |
| Main route connectivity | **0** unexplained disjoint wagon components or visually joined but collision-disconnected intersections |
| Early-map join | Cinder Creek `START_SPUR` → visible outer road, collision-safe |
| Graphics | Wagon / secondary / trail / rail visibly distinct at gameplay scale and on map |
| Low-detail graphics | All traversable routes and critical destination cues remain visible |
| Performance | Camera-local route drawing; no significant regression on user's actual laptop |
| CI | Full regression suite green with linked workflow run |
| Gameplay | User-confirmed long ride and at least one fishing + one camping approach |

**Do not call this milestone finished if only the graph passes but the player cannot walk or ride the route.**

## 10. Risks, priorities and safeguards

1. **The current 13 polylines may not join at intended town hubs.** Graph audit first, not cosmetic painting.
2. **Atlas drawing and river collision are slightly different geometries.** Keep bridge deck and passability sampled together.
3. **Legacy nearby road grid may still influence obstacles even where it is not painted.** Correct deliberately with regressions.
4. **New tracks could be erased or blocked by rocky terrain and dry washes.** Extend protection corridors before adding props.
5. **Fisheries near coastline and lakes can put a marker over impassable water.** Derive reachable shore coordinates, validate with `is_water`.
6. **Widened roads can swallow scenic texture or town squares.** Use a narrower tier near interiors and predictable joins.
7. **Visual optimization can hide critical trails in Low graphics mode.** Route strokes and signs always rendered.
8. **Old X11 performance is a priority.** Avoid per-frame global route searches and excess Canvas objects.
9. **Later travelers need stable nodes.** Do not bake fragile screen-space route positions into AI or saves.
10. **Scope creep:** No fishing gameplay/boats/AI crowds until navigation is verified.

## 11. Definition of done and handoff

Deliver: (a) road and bridge audit report, (b) normalized route graph, (c) fixed town/waystation network, (d) authored fishing/camp trails and destinations, (e) improved gameplay + parchment graphics, (f) screenshots and low-detail review, (g) CI/tests, (h) plain-language user playtest instructions, (i) exact main-branch commit.

**No code implementing paths, trails, locations or new graphics was created by writing this specification.** This milestone is intentionally a prerequisite to the next autonomous-travelers development pass.
