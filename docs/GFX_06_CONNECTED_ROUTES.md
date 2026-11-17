# GFX-06 — Connected Forsaken Roads, Trails & Railbeds (opt-in)

This milestone replaces the **visual strokes** of the canonical New
Austellia routes, **not their geometry**, using colors extracted from the
user-approved GFX-A02 source sheet. Existing authored primary roads,
secondary roads, trails, rails, and bridge-deck drawing remain the source
of truth. This is a real playable, camera-local vector styling pass—not
an unverified attempt to use concept-board image patches as autotiles.

## GitHub-first update

```bash
cd ~/dust-and-debt-github
git fetch origin
git switch graphics/gfx-06-connected-routes
git pull --ff-only origin graphics/gfx-06-connected-routes
```

Use the unchanged, previously downloaded 17-board art ZIP:

```bash
python3 tools/gfx06_road_palette.py \
  --archive ~/Downloads/Dust_and_Debt_Forsaken_Master_Art_Source_v1.zip

DUST_AND_DEBT_GFX06=1 DUST_AND_DEBT_RETAINED_CANVAS=1 \
  ./Play_Dust_and_Debt.sh
```

If you also want the GFX-05 soil material pilot, generate it as documented
in `docs/GFX_05_INTEGRATION_FOUNDATION.md` first. GFX-06 will select that
prepared world when present, otherwise the original map.

To return to the original road presentation, run the game without
`DUST_AND_DEBT_GFX06=1`. Missing/malformed color JSON leaves the
legacy road renderer active. Runtime requires only Tk/Python standard library.

## What is actually implemented

- A02 source archive validation: 17 files / SHA256 / board dimensions.
- Nine palette entries sampled from A02 road, trail and rail illustrations.
  The original illustration is a **style guide**; palette source materials
  aren't represented as production-ready 16px autotiles.
- All roads use existing polyline vertices in `new_austellia.py`.
  The new renderer uses camera clip margins and round joins to eliminate
  cosmetic gaps at corners and intersections. Existing road widths and
  walkability are not changed.
- Primary/secondary roads: layered shoulders, core and dual wheel ruts.
- Trails: narrow dark verge, lighter interior and broken wear track.
- Rails: stone ballast, repeated wooden sleeper pattern and twin steel rails.
- Bridge decks, waterfronts, towns, actors and all gameplay overlays draw
  in their original order. No new collision rectangles or route connectors.
- No main-menu setting added: opting in is via an environment variable.
- **Important:** The inherited Cinder Creek `world.png` overlays the
  map-space routes in its original 4800×3200 area. Therefore the new
  vector style is easiest to see *outside the starter-world image bounds*
  (Great Territory). The Cinder Creek starter roads remain inherited image
  artwork. Replacing them in a road-safe bake is a later milestone.

## Tests and limitations

```bash
python3 tests/gfx06_routes_test.py
DUST_AND_DEBT_SILENT=1 xvfb-run -a python3 tools/run_tests.py
```

Test verifies source checksum, nine extractable material colors, failure
on missing route geometry, clipped drawing, wagon ruts, and preservation of
the canonical route data. CI additionally runs pre-existing road/bridge
clearance regressions.

The source board has no validated curve/junction atlas. Until new
connection-tested tiles exist, this renderer uses connected vectors instead
of claiming falsely that arbitrary magenta-key crops form seamless roads.
Review actual screenshots in Larkfield, desert crossroads, bridge crossings
and the starter-to-Great-Territory seam before merging into main. Test FPS
on the target old Intel iGPU hardware, particularly at rail/road junctions.
