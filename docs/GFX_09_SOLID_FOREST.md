# GFX-09 — Solid landscape objects and forests (first pass)

**Status:** opt-in review milestone; leave draft until visual QA on target Linux.

GFX-09 extracts two large, complete motifs from the high-contrast approved
GFX-B01 sheet: a pine and a skeletal dead tree. The **overlapping** rock motifs
on that same board cannot be safely cropped individually, so game art reuses
the independently extracted, complete GFX-08 rock instead.

The game now draws cached RGBA sprites at a subset of the **existing**
`natural_terrain.ROCKS` positions, including its existing collision flags.
The choice of sprite is made from the existing biome and rock solid flag:
pine at solid forest rock sites; dead tree at selected solid dryland sites;
rock everywhere else. Every rock remains at its original coordinates and
size in the gameplay collision system. This initial art pass **does not**
plant new collision obstacles in previously clear ground.

## Install on Archcraft

```sh
cd ~/dust-and-debt-github
git fetch origin
git switch graphics/gfx-09-solid-forest-art
git pull --ff-only origin graphics/gfx-09-solid-forest-art

# These source boards were delivered as the master ZIP in chat.
python3 tools/gfx08_wilderness.py \
  --archive ~/Downloads/Dust_and_Debt_Forsaken_Master_Art_Source_v1.zip

python3 tools/gfx09_solid_art.py \
  --archive ~/Downloads/Dust_and_Debt_Forsaken_Master_Art_Source_v1.zip

xdg-open assets/forsaken_v1/gfx09/review.png

DUST_AND_DEBT_GFX09=1 DUST_AND_DEBT_GFX08=1 \
DUST_AND_DEBT_GFX07=1 DUST_AND_DEBT_GFX06=1 \
DUST_AND_DEBT_RETAINED_CANVAS=1 ./Play_Dust_and_Debt.sh
```

The updated trees and rocks occur in **Great Territory uplands** where the
existing ROCKS are seeded. Cinder Creek's background image still contains
older painted vegetation, so it is intentionally unaffected by this stage.
Some environments may show only boulders; tree choices are biome-aware.

## Technical contract

- Source: SHA-checked 17-board ZIP / B01 1536x1024 magenta sheet.
- Source crop QA: detect substantial non-matte pixels along image crop edge,
  reject likely clipped trees, preserve bottom-right extent.
- Output: two genuinely transparent RGBA PNGs and `manifest.json`, plus
  `review.png`. Separate physical foot-mask candidates are calculated
  from exported alpha and summarized in the manifest.
- Runtime: pure Tk, cached `PhotoImage` objects. No Pillow in game runtime.
- Source magenta becomes **alpha zero**; no sprite rectangle is a new
  collider. Collision candidates exclude transparent parts and upper tree
  canopy but are **not automatically authoritative** in this iteration.
- Existing `ROCKS`, `landform_solid()`, roads, water, bridges and quests
  remain untouched, so old NPC/horse/player pathing stays stable.
- Missing/invalid sprite files: fall back to the existing procedural rocks.
- Switch the new rendering off by omitting `DUST_AND_DEBT_GFX09=1`.

## Important outstanding work

1. Review the actual exported large trees for magenta fringes and full
   silhouettes. Only two clean B01 trees are in this first stage.
2. Author collision footprints in world units, check player and horse
   movement around each trunk and rock, and enable alpha-derived blockers
   **only after** they pass route-clearance and stability tests. For now the
   old obstacle circles still decide collision.
3. Separate the overlapping rocky B01 tiles and redraw dark-backed B02/B03
   artwork on a dedicated high-contrast matte. Never erase dark colors.
4. Expand tree variety and position forest vegetation independently of
   rock anchor sites, with ground/overhead layering and benchmark the number
   of visible Tk image objects on the user's older Intel iGPU.

## Tests

```sh
python3 tests/gfx09_solid_art_test.py
DUST_AND_DEBT_SILENT=1 xvfb-run -a python3 tools/run_tests.py
```
