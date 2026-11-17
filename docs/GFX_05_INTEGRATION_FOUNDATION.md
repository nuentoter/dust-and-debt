# GFX-05 — Forsaken asset integration foundation

**Branch:** `graphics/gfx-05-asset-integration` (draft; do not merge until on-device visual approval)

This is a first executable graphics pipeline, not a claim that the 17
illustrated concept boards contain ready-made sprites or seamless connected
road tiles. It works with the EXACT SHA-verified master source ZIP and keeps
the original game geography, missions, collision and NPC coordinates intact.

## Install / run on Archcraft (GitHub-first)

```sh
cd ~/dust-and-debt-github
git fetch origin
git switch graphics/gfx-05-asset-integration
git pull --ff-only origin graphics/gfx-05-asset-integration

# Use the previously downloaded 17-board ZIP unchanged:
python3 tools/gfx05_pipeline.py \
  --archive ~/Downloads/Dust_and_Debt_Forsaken_Master_Art_Source_v1.zip \
  --verify --stage
xdg-open assets/forsaken_v1/gfx05/terrain_review.png
xdg-open assets/forsaken_v1/gfx05/roads_review.png
```

The source archive is **not** silently replaced by the old nine-board
Forsaken pack; if the ZIP is absent or a sheet is altered, the command fails.

To generate the **opt-in A01 Cinder Creek soil pilot**:

```sh
python3 tools/gfx05_pipeline.py \
  --archive ~/Downloads/Dust_and_Debt_Forsaken_Master_Art_Source_v1.zip \
  --pilot
xdg-open assets/forsaken_v1/gfx05/gfx05_before_after.png
DUST_AND_DEBT_GFX05=1 DUST_AND_DEBT_RETAINED_CANVAS=1 ./Play_Dust_and_Debt.sh
```

Run without `DUST_AND_DEBT_GFX05=1` to see the normal game (or use the
older `DUST_AND_DEBT_FORSAKEN_V1=1` path for the earlier building pilot).
The stage/preview/export tooling requires Pillow; runtime stays pure Tk.

## What this actually changes

- **A01:** Crops 56 labelled terrain references, makes 12 deterministic
  **64×64 pilot** swatches with mathematically matched opposite tile edges.
  These are **not** validated 16×16 production autotiles. The pilot changes
  earth-like pixels only in a restricted Cinder Creek region, using existing
  `make_pilot` route/building exclusion. No ground changes outside the
  region and no water or authored road pixels are overwritten.
- **A02:** Crops 12 road, trail and railway reference snippets. Each is
  explicitly marked **candidate only** and cannot replace authored road
  routes. No junction adjacency/curve/bridge validation is claimed.
- **Other 15 sheets:** SHA-verified against the master source manifest and
  held as original concept art, not used in-game.
- **Transparency/collision:** `tools/gfx05_collision.py` establishes
  class-aware alpha-footprint candidates. Magenta is editor-only background,
  alpha-zero pixels cannot collide; canopy, grass, small shrubs, water overlays,
  decorative and UI art default to no solid collision. Solid trees, cactus,
  boulders, buildings and barriers use a constrained physical foot band
  rather than a full PNG rectangle. These collision proposals are NOT yet
  wired to new in-world instances; existing solid() logic remains in charge.
- **Select/render:** `DUST_AND_DEBT_GFX05=1` chooses the stage-generated
  world ONLY when its PNG header has exactly the original 4800×3200
  dimensions. Otherwise it returns to existing game art. The earlier
  `DUST_AND_DEBT_FORSAKEN_V1` selector still works.

## Rules to be applied to every remaining sprite family

1. Preserve original approved master RGB boards verbatim, with SHA checks.
2. Presentation art is separate from the final extraction-ready RGBA PNG.
3. A magenta working background is not alpha; exported sprites must have
   actual alpha zero and no opaque magenta fringes.
4. No baked cast shadows. New game lighting/shadows will be separate.
5. No crops touching any source edge. Review bottom/right extensions.
6. Ground is opaque and walkability authored by the game; standalone objects
   use their lower physical footprint after separately validated alpha.
7. Test world-scale draw order, entrances, screen bounds, roads/trails,
   bridge clearance and on-device speed before enabling in main.
8. Do not claim that seam-matching two edges makes curve/intersection
   tiles topologically compatible. Route graph and layout review required.
9. Stage every new family under its own immutable asset ID with a manifest
   and explicit `artist_verified` gate.

## Tests

```sh
python3 tests/gfx05_pipeline_test.py
xvfb-run -a python3 tools/run_tests.py
```

GitHub Actions runs the new isolated test alongside existing gameplay,
road geometry and graphics suites.

## Remaining to ship as full graphics overhaul

This milestone is a **foundation + playable A01 soil pilot**. It is NOT a
full-world A01 replacement or an A02 road replacement. We must first produce
proper joined 16px transition tiles and correct rail/junction topology, then
review actual screenshot + performance and extend to the other 15 groups.
