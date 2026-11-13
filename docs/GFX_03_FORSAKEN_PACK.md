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
