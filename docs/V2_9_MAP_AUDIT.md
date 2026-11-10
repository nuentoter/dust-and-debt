# v2.9 map handoff reconciliation

Updated November 9, 2026 after fetching GitHub `main` at `3514e26`.

The initial local review used `96e5a97`, which was behind GitHub. That checkout
had the legacy minimap grid, 13 wagon polylines and no dedicated fishing/camp
registry. Those findings are historical, not the current implementation status.

GitHub already supplied the six-phase map specifications, deterministic route
graph and audit tools, nine wagon connectors, twelve fishing destinations,
twelve campsite destinations, trail geometry, shared clipped route rendering,
and separate foot/horse graph traversal. The local branch was fast-forwarded
to preserve this work. The initial local minimap implementation was superseded
by GitHub's `frontier_route_art.py`, avoiding duplicate renderers.

Continue from these authoritative development documents:

- [Milestone scope](../ROADS_TRAILS_LANDMARKS_MILESTONE.md)
- [Technical implementation plan](../ROADS_TRAILS_TECHNICAL_PLAN.md)
- [Physical clearance findings](ROAD_CLEARANCE_FINDINGS.md)
- [Current roadmap](../ROADMAP_v3.md)

Destination presence alone does not prove fishing/rest gameplay integration or
physical route clearance. Keep the remaining acceptance gates in those plans;
do not mark the complete milestone delivered from this reconciliation.

## Audio cleanup correction

Earlier regression runs launched real soundtrack players, and some tests
exited without stopping them. Six orphaned players were identified; remaining
live players were terminated and a process check confirmed none remained.

Audio now stops on direct Tk root destruction and normal Python exit, and both
music and effects are terminated and reaped, with a kill fallback. Run future
regressions silently with:

```sh
xvfb-run -a python3 tools/run_tests.py
```

The runner sets `DUST_AND_DEBT_SILENT=1`, suppressing players and Tk bell.
Mocked audio tests explicitly opt back in only around fake player launches.
Linux CI uses the same silent environment. Cleanup regression coverage uses
mock players and a real sleeping child process; no speaker output is needed.

## Validation and additional route correction

All 27 regression scripts passed in silent mode (the economy test's fake bell
assertions needed an explicit mocked-only opt-in, then passed on rerun).
The game self-test and `git diff --check` also passed. A final host process
check found no remaining players, Python test processes or Xvfb sessions.

The fetched route regression exposed a Galloway endpoint mismatch and an
outdated trail inventory assertion. Concurrent GitHub commits subsequently
fixed both; their route geometry was retained during reconciliation. An added
local regression confirms foot/horse access and wagon exclusion on campsite
trails. Newer GitHub updates also add dry-bank trail repairs, road styling,
signposts, map legends and destination regression coverage. These changes are
preserved. Full-world physical clearance remains subject to the milestone's
separate audit gates.
