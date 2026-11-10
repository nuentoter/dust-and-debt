# v2.9-map bridge approach review

November 9, 2026. Continues the seven review probes recorded in
[rail/bridge progress](RAIL_BRIDGE_PROGRESS.md). The current machine-readable
result is [road_audit.json](road_audit.json).

## Finding

All seven water failures came from extending a bridge's straight heading
25 units beyond a deck end. At bends and confluences that point is off the
actual route. Each bridge already connects to clear, authored approach paths.
Route, deck, water, building and mission geometry were preserved.

| Crossing | Surface | Waterway | Probe end | Distance to actual route | Route half-width |
|---|---|---|---|---:|---:|
| `crossing_000` | Rail | Sable River | Exit | 425.92 | 12.5 |
| `crossing_008` | Rail | Blackwater River | Exit | 417.60 | 12.5 |
| `crossing_014` | Road | Blackwater River | Entry | 106.06 | 30 |
| `crossing_020` | Rail | Roan Creek | Exit | 598.14 | 12.5 |
| `crossing_026` | Rail | Riversend Channel | Exit | 423.43 | 12.5 |
| `crossing_027` | Rail | Riversend Channel | Entry | 78.18 | 12.5 |
| `crossing_046` | Road | Blackwater Town Crossing | Entry | 166.72 | 50 |

Distances and widths are world units. The JSON retains the original
`entry_passable`/`exit_passable` water-only tangent results. New
`tangent_reviews` classify these seven as `off_route_tangent`, preserving
coordinates, nearest route, segment, projection, width and exact distance.
They are explained diagnostic results, not silently deleted failures.

## Route-aware validation

`tools/bridge_approaches.py` clips each same-mode route segment to the rotated
deck rectangle, merges contiguous intersections through authored bends, and
keeps repeated visits separate. The validator then follows the original
polyline in both directions: at least 150 units where route length permits,
continuing farther if needed to reach real land or an existing raised
settlement parcel. A route terminal inside unsupported water fails.

The cropped approach retains all authored vertices; no straight shortcut,
nearest-town teleport or rail-to-wagon attachment is introduced. It is sampled
at <=10-unit spacing for foot radius 11 and horse radius 16, at centers and
usable lane margins. Failure examples retain original route segment indices.

A water tangent that lies **inside** an attached route's painted footprint
is an acceptance failure, even if other coarse probes happened to pass.
A missing same-mode route, collision, unsupported terminal, missing review or
coarser-than-10-unit approach sampling also prevents acceptance.

## Measured result

- **50/50** bridge records pass scoped route-approach validation.
- **101** actual route paths checked; **31,118** approach probes, zero blocked.
- **202** supported anchors: 108 on land, 94 in existing settlement parcels.
- 70 anchor guards terminate before 150 units at authored route endpoints.
  Those endpoints are explicitly marked `route_terminal` and physically
  sampled; no extension beyond the source route is assumed.
- The full road/trail/starter/rail scan still passes **240,974 probes**.
  Approach probes overlap that scan and other bridge approaches; they are
  not additional unique world positions.
- Route and deck geometry digest remains
  `8fdd554657b7193e4d25702239416bf0259ec859bfc17f09185ded396e420f03`.

`physically_validated` now refers explicitly to
`physical_validation_scope = sampled_same_mode_route_approaches`. It does
not certify a continuous swept surface, train turning dynamics, a full
bridge-perimeter walk, visual approval or real-hardware performance.

## Reproduce

```sh
DUST_AND_DEBT_SILENT=1 python3 tests/bridge_approach_test.py
DUST_AND_DEBT_SILENT=1 python3 tools/audit_routes.py --bridges --check --json /tmp/bridge_review.json
DUST_AND_DEBT_SILENT=1 python3 tools/audit_routes.py --physical --include-rail --check --json /tmp/road_audit.json
```

The full physical command and Linux CI now require the bridge-approach
reviews, in addition to route clearance. Twelve fixture tests exercise rotated
clipping, bends, repeat visits, land-anchor search, retained off-route probes,
real wet approaches, unsupported terminals, horse-only building collisions,
mode isolation, coarse sampling and missing/failed review gates.

Next milestone work: remove phantom legacy-grid terrain protection while
preserving authored routes and the starter parcel, then collect representative
captures/performance baselines and prepare the user long-ride acceptance.
Traveler AI and milestone closure remain deferred.
