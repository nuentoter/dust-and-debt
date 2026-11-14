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

## Milestone 3 — Visible starter-town art correction

The first GFX-03 pilot only changed distant, lightly tinted soil pixels; it
could look **identical to the legacy map** from the starting camera. That was
not acceptable as a graphics integration. The bake now:

- Paints approved terrain texture strongly over existing earth-coloured ground
  in the starter camera and approach areas, with an 80px feather. The road,
  rail, water, and old building exclusion logic remains in place.
- Extracts **ten** actual Gothic building sprites from the *approved* D01
  source sheet. A largest-component matte removes the dark presentation
  background and decorative frame lines; original building footprints are
  replaced with texture before overlay. The visible building is anchored
  south-centre, while gameplay collision and NPC positions stay untouched.
- Refuses to save a world if fewer than 2,500 starter-camera pixels differ
  by 18 RGB levels or the maximum channel difference is below 25.
- Writes `assets/forsaken_v1/runtime/before_after_starter.png` as a
  **1920×600** before/after crop. The left half shows the legacy starter
  camera; the right half shows the actual new baked scene.
- Writes extracted transparent building sprites to
  `assets/forsaken_v1/prepared/D01` and records placement bounds in the
  pilot manifest.

Install/rebuild (after updating the graphics branch):

```sh
python3 tools/forsaken_pack.py --validate --extract-candidates
python3 tools/build_forsaken_pilot.py --pilot
xdg-open assets/forsaken_v1/runtime/before_after_starter.png
DUST_AND_DEBT_FORSAKEN_V1=1 DUST_AND_DEBT_RETAINED_CANVAS=1 ./Play_Dust_and_Debt.sh
```

**Visual review still required:** extraction uses approximate D01 pixel
silhouettes rather than individually hand-authored transparent source art.
At some storefronts the preserved collision rectangle may extend beyond the
new visual wall. Check approaches, signs, road margins, building fronts and
old-shadow removal before accepting the composition or merging this PR.
The wider map still has the old artwork outside the pilot regions.

## GFX-03 matte and ground correction — screenshot review (Nov 13)

The first visible live pilot had obvious **gray rectangular soil patches** and
Gothic buildings with square ground mats. These were actual defects, not
acceptable art direction:

- `make_pilot` used to mix the full RGB color of a gray A01 soil tile at up
  to 78% strength into a sharply classified dirt region. That made pasted
  gray blocks. It now applies **mean-centered per-channel texture detail**
  while preserving each original terrain pixel's native color. Region edges
  remain feathered and authored route exclusion remains active.
- `silhouette` used to fill all pixels between first and last retained
  points on each row. That implicitly resurrected rectangular backgrounds
  and could keep labels. It now flood-fills only near-black exterior matte,
  preserves enclosed building details, and retains the dominant foreground
  connected component.
- The previous building eraser tiled approved gray soil directly into the
  gameplay building rectangle, reproducing the most noticeable squares.
  It now **samples surrounding original soil and inpaints inside the old
  footprint only**; nothing outside the gameplay rectangle is rewritten by
  this eraser, including nearby roads. Gameplay collision is still identical.
- Sample the exterior ground even when the route-protection halo marks it as
  protected: the mask deliberately extends 55px beyond buildings, and
  rejecting those samples would leave only a constant tan fallback.

Validation: run the graphics test suite and inspect
`assets/forsaken_v1/runtime/before_after_starter.png`. Do not claim this is
visually accepted until it has been rebuilt and reviewed on the user machine.

## GFX-03 visual correction 2 — review of November 13, 10:19 PM captures

The comparison showed remaining severe artifacts:

- Pale repeating 64px terrain texture **checkerboard patches** along north/west
  parts of Cinder Creek and next to the railway/roads.
- Lower parts of several storefront and stable sprites removed by the
  **near-black-background flood fill**. Only their rooftop remained.
- Thin L-shaped black outlines and hard-edged tan building footprints.

This change addresses the actual rendering causes:

1. A01 now samples its original 64px swatches at **smoothly warped world
   coordinates**, so the same motif is not repeated at fixed 64px intervals.
   The original earth's colour is kept, tint strength is reduced, and the
   protected route/building mask is blurred *only on editable pixels* to soften
   the surrounding boundary. No original route pixels are altered.
2. D01 export recovers facade rows disconnected from the largest roof
   component by shadowed porches. This fixes the roof-only extraction that
   created empty lower halves of buildings.
3. Building cleanup uses a **28px feathered ground reconstruction**, sampling
   actual surrounding original soil beyond the old shadow rather than drawing
   a tan rectangle within the collider.
4. Regression tests explicitly cover detached facade recovery and preservation
   of the outside of protected building/road areas.

These are procedural, best-effort fixes to imperfect board artwork, not a
substitute for truly authored transparent sprite assets. Do not merge until
the 960×600 in-game capture and before/after composite have been reviewed.

Rebuild after pulling:

```sh
python3 tools/forsaken_pack.py --validate --extract-candidates
python3 tools/build_forsaken_pilot.py --pilot
xdg-open assets/forsaken_v1/runtime/before_after_starter.png
DUST_AND_DEBT_FORSAKEN_V1=1 DUST_AND_DEBT_RETAINED_CANVAS=1 ./Play_Dust_and_Debt.sh
```
