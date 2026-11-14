# GFX-ART-001 — High-contrast editing and manual sprite transparency

Effective 2026-11-14. This replaces accepting dark-background review sheet crops as production assets.

## Nine-sheet review

| Group | Production mode | Corrective action |
|---|---|---|
| D01 Gothic buildings | RGBA objects | Hand clean building silhouettes; preserve black windows and dark roof pixels; separate entrance anchors |
| A01 Terrain | Opaque 16px tiles | Seamless true tiles and transitions; never key away dirt |
| A02 Roads, trails and rails | Opaque connections plus transparent overlays | Hand-author straight/turn/T/cross junctions; validate routes |
| A03 Cliffs and elevation | Opaque ground with RGBA objects | Preserve cave darkness and actual collision independently |
| A04 Water and shores | Opaque animated water + RGBA objects | Separate docks, reeds and floating decorations |
| B01 Woodland | RGBA trunk/canopy/foliage | Keep dark foliage; split canopies from trunks |
| B02 Grayscale dryland | RGBA plants | Grayscale vegetation is art, not matte |
| B03 Marsh vegetation | RGBA growth/moss/roots | Preserve black branches and shaded roots |
| B04 Fungi, wildflowers and understory | RGBA small objects | Erase only actual background, retain tiny dark pixels |

## Mandatory rules

- Existing approved black Gothic sheets are reference boards, not sprite atlases.
- #FF00FF is a reserved, high-contrast EDITING BACKGROUND, not a runtime colour. Export RGBA sprites with alpha 0 outside the silhouette.
- Never globally delete dark/black pixels: roof, door, window and vegetation colors overlap the dark presentation-board backdrop.
- Keep layers separate: original unmodified crop, manually edited sprite/mask, and removable magenta background.
- Do not embed ambient night lighting, ground shadows, dirt lots, board borders, headings or labels in object sprites.
- Full opaque ground and water tiles must not be artificially made transparent.
- Do not tile a 64px review crop as a seamless world texture until properly authored/checked 16px terrain transitions.
- Preserve physical geometry and entrance anchors as independent gameplay metadata.
- Nearest-neighbour sampling for game scaling. Check sprites on both magenta and checkerboard backgrounds.
- Every production sprite must pass alpha integrity, no visible magenta, silhouette integrity, placement, and human visual review.
- The automatic silhouette generator is experimental, never a substitute for a cleaned manual RGBA sprite.

## Pack and integration workflow

The separate Dust_and_Debt_Forsaken_HighContrast_Workbench_v2.zip includes all nine original approved boards, individual manual D01 cutouts, magenta previews, editable ORA layers, alpha masks, and a PNG validator. This is an EDITING PACK, not a drop-in runtime ZIP.

After the user supplies the hand-cleaned PNGs, import them to assets/forsaken_v1/game_ready/buildings/ only after visual approval. Do not render incomplete automatic crops or square ground patches when clean art is absent.

Related implementation branch: graphics/gfx-03-forsaken-pack-foundation, draft PR #24.