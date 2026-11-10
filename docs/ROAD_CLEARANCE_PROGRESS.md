# v2.9-map physical clearance progress

Measured November 9, 2026, continuing the milestone's Group 2 physical gate.
The historical [Phase 0 findings](ROAD_CLEARANCE_FINDINGS.md) remain a baseline.
Current machine-readable results are in [road_audit.json](road_audit.json).

## Implemented in this continuation

The diagnostic used to check one radius at route centers every 90 units.
It now defaults to at most **10 units** and tests the game's actual movement
radii: foot **11**, mounted **16**. It probes the center and both usable margins
of each segment, including exact endpoints. Margins use painted surface widths
(100 primary, 60 secondary, 33 worn trail, 38 starter); decorative road
shoulders do not count as usable road. The trail probe includes its scuffed edge. Rail probes remain a separate diagnostic.

Failures carry route ID (report key), original segment index, longitudinal `t`,
world position, actor radius, lane, lateral offset and collision reason. The
report also groups contiguous failures into ranges for targeted repairs.
Classification matches `Game.solid` for static water, terrain, buildings and
world bounds, verified without constructing a game window. Water follows the
current game's point-based test; this does not certify a radius-buffered bank.

`--check` still supports a fast graph-only check. Combined with `--physical`,
it rejects blocked wagon/trail probes, missing town/waystation approaches,
coarser-than-10-unit spacing and center-only diagnostics. CI requires the full nonrail physical gate and archives the report even on
failure. Rail failures remain a diagnostic; they cannot satisfy wagon access.

## Crossing repair

The bridge builder previously discarded every crossing within 180 units of a
previous crossing. At river junctions this lost distinct approach headings and
road decks beside rail decks. It now deduplicates only coincident, parallel
crossings of the same waterway and transport type. Opposite directions on the
same line still count as one deck. Road/wagon graph and rail eligibility stay
separate; no routes or town positions were moved.

The deduplication repair alone raised the crossing-record count from 19 to 47.
After integrating four explicit GitHub-authored town decks, the current count
is **51 crossing records**. These are not necessarily
47 separate physical structures: overlapping river channels and approaches
can share a location. Existing rendering and collision consume the same bridge
records. Exact rendered deck width/length versus the passable footprint, acute
crossing lengths and bank approaches still need their separate acceptance pass.

## Measured effect

The controlled before/after runs, before integrating concurrent road repairs,
used identical 10-unit spacing, two actor radii, margin probes and
52 route records, totaling **232,166 probes**. These are sampled positions,
not unique obstacles or a continuous sweep of a road surface.

| Blocked probes | Before crossing repair | After |
|---|---:|---:|
| Wagon and secondary roads | 2,057 | 1,630 |
| Foot/horse destination trails | 0 | 0 |
| Rail corridors (diagnostic) | 3,239 | 3,110 |
| Total | 5,296 | 4,740 |

`wagon_08` and `wagon_12` now have zero blocked probes. All 24 destination
trails and the starter spur/approach also have zero blocked probes in this
run. This does not certify camp pad area, turn envelopes or an actual long ride.

## Integrated result after latest GitHub repairs

Concurrent GitHub changes supplied additional dry road approaches and explicit
bridges, plus named-camp rest support. Those changes were retained. The finer
sampler then found residual building conflicts on five approaches: `wagon_03`
and `wagon_04` near Roan Creek Boarding House, `blackwater_larkfield` near the
Larkfield Trading Post, `larkfield_harpers` near Larkfield Clinic, and
`riversend_saint_brigids` near Riversend Clinic. Small authored bends now pass
around those buildings with horse/edge clearance. The later GitHub-authored
Roan Creek north exit was retained and rechecked rather than replaced. Buildings, town centers,
mission coordinates and destination endpoints were preserved.

**The integrated nonrail physical gate passes.** The current report contains
**238,790 probes**, including **193,530 wagon/trail/starter probes with zero
collisions** and **45,260 rail probes with 3,110 failures**. All 24 destination
trails pass both actor radii and margins; this does not certify the entire camp
pad, a continuous swept surface, turn dynamics or a real long ride.

Rail water spans and business-building conflicts remain the next physical
repair task. Do not mark all bridges or the complete milestone delivered.
Exact painted-versus-passable deck dimensions and approaches, legacy route-grid
protection, six reference captures, performance baselines and user ride
acceptance also remain open. No autonomous traveler simulation was added.

## Reproduce silently

```sh
DUST_AND_DEBT_SILENT=1 python3 tests/route_clearance_test.py
DUST_AND_DEBT_SILENT=1 python3 tools/audit_routes.py --check
DUST_AND_DEBT_SILENT=1 python3 tools/audit_routes.py --physical --check --json /tmp/road_audit.json
xvfb-run -a python3 tools/run_tests.py
```

Use `--step 90 --centerline-only` only for quick diagnostics, never physical
signoff. The report includes a geometry SHA-256 so a saved measurement can be
compared to current route/bridge data. The full report intentionally keeps
rail failures even though rails are excluded from the wagon acceptance gate.

## Verification

All 30 regression scripts passed under the silent Xvfb runner on the integrated
route changes. The game self-test and whitespace review passed. No audible
playback or interactive windows were used. The physical CI command now checks
10-unit centers and margins for both actor radii; rail diagnostics are retained
in its artifact. Local regression success is separate from a verified GitHub
Actions run and from real-hardware playtesting.
