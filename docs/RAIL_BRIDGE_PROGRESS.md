# v2.9-map rail clearance and bridge footprints

November 9, 2026. Continues the [road clearance pass](ROAD_CLEARANCE_PROGRESS.md)
from `0ad5c00`; current measurements are in [road_audit.json](road_audit.json).

## Changes

- Moved river-hugging stretches of the Blackwater, Dustwell and Riversend rail
  corridors onto dry banks. Added local detours around boarding houses and
  trading/clinic buildings at Galloway, Larkfield, Dustwell and Riversend.
  Mapped rail station locations remain accessible; no buildings, missions,
  wagon roads, campsites or fishing destinations were moved.
- Added immutable `BridgeDeck` frames derived from existing bridge records.
  Unit headings, length, width and corner coordinates now drive both the
  light timber polygon and river passability. The old deck painting was 15
  units shorter per end and narrower than the collision exemption. That
  mismatch and the default hidden collision margin are removed.
- Rail decks are 76 units wide; wagon decks are 164 units wide, preserving
  existing road collision clearance. Rail crossing lengths account for the
  river crossing angle when its sine is at least 0.15. Near-parallel riverbed
  tracks require authored detours rather than enormous bridge exemptions.
  The longest resulting half-span is approximately 876.42 units.
- Bridge culling uses the complete rotated footprint, so an approach remains
  drawn even when the bridge center is offscreen. Rendering and collision use
  the same precomputed frame; neither builds route graphs per frame.
- `--include-rail` makes rail clearance an explicit required physical gate.
  Linux CI now requires road, trail **and rail** clearance and retains its
  JSON artifact on failure. Graph mode restrictions still keep wagons off rail.

## Measured result

All center/margin probes use at most 10-unit spacing and the current game's
foot (11) and mounted (16) collision radii.

| Rail corridor | Previous blocked probes | Current probes | Current blocked |
|---|---:|---:|---:|
| `rail_00` | 5 | 10,876 | 0 |
| `rail_01` | 979 | 15,708 | 0 |
| `rail_02` | 1,911 | 13,688 | 0 |
| `rail_03` | 215 | 7,172 | 0 |

The previous and current paths have different lengths, so these are measured
collision counts, not percentages over identical samples. The new combined
report contains **240,974 probes with zero collisions**: **193,530** wagon,
trail and starter probes plus **47,444** rail probes. Geometry digest:
`8fdd554657b7193e4d25702239416bf0259ec859bfc17f09185ded396e420f03`.

There are 50 derived/authored crossing records after the rail realignment.
The audit now records actual deck dimensions and corners and includes those
frames in its geometry digest.

## Verification and limitations

All 31 regression scripts passed with the silent Xvfb runner. Eight new bridge
unit tests cover normalized geometry, inside/outside boundaries for every
live deck, exact painted corners, culling long decks, finite angled rail spans,
station access, lake/Gulf blocking and explicit rail acceptance. The actual
world renderer also checks road/long rail decks in Normal and Low graphics.
The game self-test and whitespace review passed. No audible playback was used.

This passes sampled static route clearance, not a continuous swept envelope,
train movement simulation, hardware performance target or user long ride.
The water test still follows the game's point-based water collision behavior.
Lakes and Gulf water remain blocked even when a synthetic test deck overlaps.

Seven bridge records still report water at one straight-line point 25 units
beyond a deck end. These are retained as **unresolved approach-review probes**,
not removed from the report. The route itself may bend away before that point;
its actual route probes pass. Review those records individually against real
route approaches, deck ends and representative captures before asserting full
bridge acceptance. `physically_validated` remains false for that broader check.

## Reproduce and continue

```sh
DUST_AND_DEBT_SILENT=1 python3 tests/bridge_deck_test.py
DUST_AND_DEBT_SILENT=1 python3 tools/audit_routes.py --physical --include-rail --check --json /tmp/road_audit.json
xvfb-run -a python3 tools/run_tests.py
```

Next: inspect the seven approach-review probes, retire the phantom legacy-grid
terrain protection deliberately, collect six representative view captures and
baseline performance measurements, and prepare the Cinder Creek → Galloway →
Roan Creek → Northstar fishing bank → Everwood camp ride. Traveler AI and
milestone closure still wait for the remaining acceptance gates.
