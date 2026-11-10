## Phase 2–4 verification update — successful strict 20-unit wagon check

**Verified green CI:** [Run 42744389118](https://github.com/nuentoter/dust-and-debt/actions/runs/42744389118) / commit `1eb9ac45`.

After adding the mainland connector network, rerouting water-hugging wagon tracks and painting explicit local bridge decks, the **strict `--physical --check` route audit passed**. It sampled the centerlines of the 13 primary wagon roads, 10 secondary road connectors, 24 foot/horse trails and 4 rail corridors at **20-world-unit intervals**.

- **Wagon centerline collisions: 0 reported** in the latest 20-unit sample; all 12 core towns and 13 waystations share one wagon-route graph component.
- **Fishing/camp trails:** 24 named destinations, dry approach pads and trail centerline tests are green.
- **Old rail lines:** **406 blocked rail samples** remain out of 21,918 samples across all modes: `rail_00` (1 building), `rail_01` (131 water/building), `rail_02` (242 water), `rail_03` (32 water). Rail routes remain **not approved** for rail traffic or wagon shortcuts; these require a separate rail regrading and bridge project.
- **Important limits:** Sampling centerlines cannot certify full-width horse/wagon shoulder clearance or prove that every position is safe at arbitrary resolution. User ride and low-end laptop performance checks are pending.

The original figures below are preserved as a **historical pre-repair baseline**, not a description of the current wagon network.

---

# New Austellia — Phase 0 physical route clearance findings

**CI execution:** https://github.com/nuentoter/dust-and-debt/actions/runs/42739838298  
**Measured from:** `python3 tools/audit_routes.py --physical --json /tmp/dust_debt_road_audit.json` on GitHub Actions Linux  
**Source:** Current 13 wagon road polylines, 4 rail corridors and `START_SPUR`; every source segment sampled in 90-world-unit increments.  
**Status:** Diagnostic, not a finished road or bridge fix.

## Results

- **2,975** total route-centerline samples; **147** collided (4.94%).
- **54** blocked samples along wagon routes; **93** along rail corridors.
- Failures: **141 water**, **6 buildings**, **0 ridge/rock** in this baseline sample.
- **5** wagon routes with water failures, **2** wagon routes with building conflicts (one route could have both).
- This is point sampling, not continuous collision validation of full wagon or horse width. Some missed narrow obstacles or alternate safe lanes are possible; player/horse clearance must be tested separately.

### Per-route failures

| Route | Total blocked | Water | Rock/ridge | Buildings | Next repair action |
|---|---:|---:|---:|---:|---|
| `wagon_00` | 2 | 0 | 0 | 2 | Inspect approach near Cinder Ridge / Galloway against building footprint |
| `wagon_01` | 12 | 12 | 0 | 0 | Reconcile Silvervein–Blackwater water crossing(s) |
| `wagon_05` | 4 | 4 | 0 | 0 | Check Hollow Bend–Harper bank/bridge deck |
| `wagon_06` | 1 | 1 | 0 | 0 | Inspect Galloway–Stonewall water interface |
| `wagon_07` | 3 | 3 | 0 | 0 | Inspect Stonewall–Dustwell river/wash crossing |
| `wagon_09` | 30 | 30 | 0 | 0 | **Highest priority wagon water obstruction:** Harper–Bayou route |
| `wagon_11` | 2 | 0 | 0 | 2 | Inspect Riversend–Lone Pine / Black Rock buildings |
| `rail_01` | 30 | 28 | 0 | 2 | Validate mainline coastal/river deck continuity; rail-specific deck |
| `rail_02` | 56 | 56 | 0 | 0 | **Highest priority rail water obstruction:** Dustwell–Riversend–Saint Brigid corridor |
| `rail_03` | 7 | 7 | 0 | 0 | Check Larkfield–Valleyford–Riversend rail water crossing |

Other atlas routes reported zero centerline collisions at this step size; they are **not certified** as traversable until edge-width sampling and a movement test pass.

## Connectivity findings (static atlas graph)

From `docs/road_audit_baseline.json`:
- The 13 canonical wagon routes have **five disconnected exact-intersection components**.
- The old starter spur is a **sixth isolated component**.
- Last-mile distance from mapped site to nearest wagon geometry: Brimstone Point ~9,381 world units; Larkfield ~6,597; Iron Mesa Fort ~5,817; Saint Brigid's Port ~5,363.
- Those distances are to a painted polyline, **not** to a collision-safe path or approved wagon junction.
- Rails do not count as wagon connections, even when the atlas depicts settlements along the rail line.

## Phase 2 prioritized implementation backlog

- [ ] **First fix physical water breaks already on drawn roads**, especially `wagon_09` and `wagon_01`, with real visually matching bridge/ford solutions or deliberate detours.
- [ ] Resolve rail water breaks using rail-specific deck art/collision, not a universal wagon bridge.
- [ ] Identify why six building-collision samples intersect road/rail centerlines; reroute local approaches or reposition **new** props; preserve original mission buildings.
- [ ] Bridge existing five wagon components using explicit authored roads grounded in the atlas and physical terrain, not teleport/snap graph edges.
- [ ] Connect the separate starter spur without a hidden legacy grid shortcut.
- [ ] Create direct last-mile branches to Larkfield, Saint Brigid's Port, Brimstone and Iron Mesa.
- [ ] Add the 12+ fishing and 12+ campsite destinations only after these trunk access issues are resolved.
- [ ] Run 10-unit and offset-lane clearance samples and horse/rider collision tests; this 90-unit diagnostic is only a first screen.
- [ ] Replace map/minimap imagery based on the **verified** corrected network; do not paint disconnected roads as open thoroughfares.

**No terrain geometry, roads, bridge collision, minimap or routes were changed in Phase 0/first Phase 1 slice.** Existing route problems remain until subsequent implementation groups are committed.
