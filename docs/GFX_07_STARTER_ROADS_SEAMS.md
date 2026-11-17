# GFX-07 — Cinder Creek roads and starter-map seams

This draft milestone turns the verified source A02 road color palette into an
**opt-in replacement of the actual starter-image roads**, not just the distant
Great Territory vector routes from GFX-06.

## Install (GitHub first)

```sh
cd ~/dust-and-debt-github
git fetch origin
git switch graphics/gfx-07-starter-roads-seams
git pull --ff-only origin graphics/gfx-07-starter-roads-seams
```

If you have not yet created the approved GFX-06 palette, generate it from
the 17-sheet master source archive (same ZIP as previous milestones):

```sh
python3 tools/gfx06_road_palette.py \
  --archive ~/Downloads/Dust_and_Debt_Forsaken_Master_Art_Source_v1.zip
```

If you want the approved Gothic buildings, make sure the earlier GFX-04
bake exists:

```sh
python3 tools/build_redrawn_buildings.py
```

(This needs the previously extracted **redrawn** magenta-background GFX-D01
art file at `assets/forsaken_v1/redrawn/GFX-D01-redrawn.png`.)

To also include A01 soil styling, stage GFX-05 first if you have not already:

```sh
python3 tools/gfx05_pipeline.py \
  --archive ~/Downloads/Dust_and_Debt_Forsaken_Master_Art_Source_v1.zip --stage
```

Create the starter-road replacement and its 1920×600 before/after image:

```sh
python3 tools/gfx07_starter_roads.py
xdg-open assets/forsaken_v1/gfx07/gfx07_starter_before_after.png
```

Play:

```sh
DUST_AND_DEBT_GFX07=1 DUST_AND_DEBT_GFX06=1 \
DUST_AND_DEBT_RETAINED_CANVAS=1 ./Play_Dust_and_Debt.sh
```

Turn GFX-07 off simply by omitting that environment variable. You can
continue playing earlier graphics using the older environment flags.

## Scope and guarantees

- Offline Pillow bake builds `assets/forsaken_v1/gfx07/world_gfx07.png`
  in RGBA mode, exactly 4800×3200 pixels. The running game has **no**
  Pillow dependency.
- The source is the previously generated **GFX-04 buildings world** when
  available, otherwise existing GFX-05 terrain world, otherwise original
  `assets/world.png`. All source files remain unchanged.
- When the GFX-05 seam-checked A01 soil swatch is already staged, an
  additional soil-only patch is applied to the source **outside preserved
  building/road features**. This is optional.
- Authored source-image road centres are copied from `build_assets.py`:
  east/west town street, north/south wagon road, two diagonal branches and
  the southern railway. No new geometry, bridges or collisions.
- Existing road/rail colors are removed ONLY within known road corridors,
  and the new A02-derived paint is clipped around all ten original building
  footprints (18px protective margin).
- The old square starter-image edge is replaced with an RGBA feather along
  the eastern and southern borders. The previous checker/stippled transition
  is automatically skipped **only if the new image actually loaded**.
- Actual A02 source illustrations are **reference colors**, not connected
  PNG tile atlases. The new starter streets are explicitly painted connected
  bands, wheel ruts and twin-rail sleepers.
- The new roadmap and collision rules are separate; no gameplay data is
  modified by this milestone.

## Tests

```sh
python3 tests/gfx07_starter_roads_test.py
DUST_AND_DEBT_SILENT=1 xvfb-run -a python3 tools/run_tests.py
```

The synthetic GFX-07 regression covers old painted road removal,
connected road/rail replacement, protected buildings, unchanged source
pixels, eastern/southern alpha, bad-palette rejection and fallback.
Existing CI additionally tests road clearance, bridges and gameplay.

## Visual acceptance gate

Check the opening Cinder Creek junction, the saloon and sheriff entrances,
diagonal branches, the railway and the far-world seam, particularly at
night and on the old Intel iGPU. **Do not merge the draft PR until the
user-supplied gameplay screenshots confirm no road ghosts, halos or
shadow rectangles.**

**Remaining task:** real per-family 16px terrain autotiling, topology-tested
road tile atlas, all-world material integration, and the additional object
and actor sprite families. This pilot does not falsely claim they are done.
