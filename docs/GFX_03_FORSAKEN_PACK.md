# GFX-03 — Forsaken art library / integration foundation

This milestone begins integration of the approved **Forsaken Gothic Frontier**
art direction without repeating the earlier Cinder Creek problem of pasting
presentation panels, dark backdrops or rectangular lots into the world.

## Scope delivered

1. **Nine versioned visual-reference boards** D01, A01-A04, B01-B04,
   distributed separately as `Dust_and_Debt_Forsaken_ArtPack_v1.zip`. The
   generated review images are not committed to the repository and must be
   provided by the user. The pack contains `manifest.json` with SHA-256
   checksums, dimensions and explicit production status for each board.
2. **`tools/forsaken_pack.py`** validates the manifest and the full nine-board
   file list, checks content hashes, flags accidental production-ready labels,
   and creates a contact preview. With `--extract-candidates` it cuts
   12 label-free 64x64 terrain candidate crops from the A01 board and
   records edge discontinuity metrics. These are not seamless, not a complete
   16x16 atlas, and are NOT used by the game yet.
3. **Optional runtime selection:** when `DUST_AND_DEBT_FORSAKEN_V1=1`, the
   game will prefer a *separately prepared* image at
   `assets/forsaken_v1/runtime/world_forsaken.png` **only** if its PNG header
   declares the legacy world size `4800x3200`. Otherwise the existing
   GFX02/legacy artwork remains active. No new runtime libraries, colliders,
   building coordinates or gameplay geometry.
4. Regression tests with synthetic PNG fixtures. CI exercises the import,
   preview, candidate manifest, hash checks, and world-image selection.

## Installing the art package

On Linux, after obtaining the separate archive:

```sh
cd ~/dust-and-debt-github
git fetch origin
git switch graphics/gfx-03-forsaken-pack-foundation
mkdir -p assets/forsaken_v1
unzip -o ~/Downloads/Dust_and_Debt_Forsaken_ArtPack_v1.zip -d assets/forsaken_v1
python3 tools/forsaken_pack.py --validate --preview --extract-candidates
```

The zip must extract its `manifest.json` and `source_boards/` directory
directly beneath `assets/forsaken_v1`. Read the manifest for how the
reference art is tracked.

**Do not copy a source board to `world_forsaken.png`.** A 1448x1086
presentation board is not a 4800x3200 gameplay scene and should never be
stretched onto the map. The runtime selector is intentionally staged until
individual sprite extraction, alpha isolation, tile seams, route masks,
player/building visual anchors and collision review are complete.

## Acceptance before real gameplay art

- [x] Freeze approved visual references and checksums
- [x] Separate source boards from runtime artwork
- [x] Extract 12 clean terrain samples for technical evaluation
- [x] Wire dimension-guarded, opt-in runtime fallback into the game
- [x] Add GitHub integration tests
- [ ] Turn A01 samples into **seam-checked** terrain tiles and true autotiles
- [ ] Derive route-safe world masks from authored roads/trails/rails
- [ ] Separate D01 building sprites into valid alpha masks with south anchors
- [ ] Complete sprite atlas metadata and layer sorting for B01-B04 vegetation
- [ ] Bake and *visually inspect* a route- and collision-safe 4800x3200 pilot
- [ ] Compare gameplay screenshots and benchmarks on old Intel laptop
- [ ] Verify third-party source-art rights before publishing binaries

The source art is conceptually approved, not automatically pixel-perfect.
Texture samples have measurable edge discontinuities. Treat technical
validation and release approval separately from artistic approval.

## Milestone 2 — Seam-checked terrain and protected Cinder Creek pilot

This phase deliberately makes a **playable terrain pilot**, rather than
claiming the presentation-board road tiles are production-ready.

After installing the graphics ZIP and updating this branch:

```sh
python3 tools/forsaken_pack.py --validate --extract-candidates
python3 tools/build_forsaken_pilot.py --seam-tiles --road-candidates
python3 tests/forsaken_pilot_test.py
python3 tools/build_forsaken_pilot.py --pilot
DUST_AND_DEBT_FORSAKEN_V1=1 DUST_AND_DEBT_RETAINED_CANVAS=1 ./Play_Dust_and_Debt.sh
```

Output:
- `assets/forsaken_v1/prepared/A01/`: 12 processed 64×64
  seam-matched terrain textures and machine-readable pixel-boundary reports
- `assets/forsaken_v1/runtime/world_forsaken.png`: opt-in 4800×3200
  **terrain-only** game-map pilot, selected by the environment variable
- `assets/forsaken_v1/runtime/route_protection_mask.png`: white editable,
  black excluded areas; generated from canonical roads, trails, rails, starter
  town road corridors and existing building footprints
- `assets/forsaken_v1/runtime/pilot_manifest.json`: traceable changes and
  explicit pending checks

**Scope constraints:**
- The nine approved boards remain local source/reference images.
- The pilot **does not draw new road sprites**. Roads, rails, trails, water
  and building geometry are protected, because the illustrated A02 road
  board does not yet contain validated transparent tiles.
- Texture samples are converted to equal-edge 64×64 repeating textures,
  but **not full 16×16 directional/autotile terrain**. They remain under
  visual acceptance; seam-equality alone does not imply beautiful repetition.
- The pilot applies subtle texture variation only to pixels that look like
  existing dusty soil, within three conservative trial regions. It changes
  *no* gameplay coordinates, pathing or collision.
- The authoritative original map and `DUST_AND_DEBT_GFX02` fallback remain
  usable. If the pilot isn't built, the game falls back safely.
- Do not merge as a final whole-world texture overhaul until we have local
  gameplay screenshots, full 16px autotiles, the A02 road/rail atlas, and
  legacy starter town/route masking review.

### Checking the pilot

Capture before/after at the starter town edge, the road northeast of the
stable, and the three trial areas. Report any obvious rectangle, road seam,
washed-out ground, texture repetition, or frame-time regression. Before
merging, run `xvfb-run -a python3 tools/benchmark_renderer.py --frames 24`
on the target laptop and compare with the previous renderer settings.

### A02 road/rail candidate handoff

The same CLI with `--road-candidates` extracts eight small RGB crops
from the approved A02 concept board under
`assets/forsaken_v1/candidates/A02/`. The output
`road_candidates.png` makes it easy to compare wagons, trail forks and
railroad ballast. Its manifest explicitly marks every item
`connection_validated=false` and `alpha_validated=false`.
**Do not paste these presentation snippets into the runtime world.**
They require alpha cleanup, directional matching, junction tiling, and a
road connectivity QA pass first. The initial playable terrain pilot
preserves the existing roads exactly.
