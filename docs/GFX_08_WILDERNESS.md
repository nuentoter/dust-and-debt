# GFX-08 — Wilderness sprite pilot (B01)

## Scope

The approved GFX-B01 sheet is the first environmental board with a genuinely
high-contrast magenta matte. This milestone cuts **four verified** B01 motifs
(bush, fern, stump, rock) from the approved source, keys their magenta to true
RGBA alpha, resizes using nearest-neighbor and draws them at the existing
deterministic outdoor-scattered-prop positions. It replaces only the old
decorative canvas ovals/lines when the optional flag is enabled.

**This is NOT a full foliage/rock collision replacement.** The original
`solid()` collision and `natural_terrain.ROCKS` positions remain unchanged.
A physical blocker cannot be inferred from the entire alpha silhouette of
overhanging vegetation. The shared GFX05 foot-mask builder remains the future
source for solid trunks and boulders at authored positions. Adding hard
collision to these previously decorative props would be a gameplay change.

Other boards, including the black-backed B02 presentation sheet, must not
have black pixels auto-keyed to transparency: the original sprite details
also contain black. They need new magenta-background extraction-safe source
art before any reliable production export.

## Install from GitHub

```sh
cd ~/dust-and-debt-github
git fetch origin
git switch graphics/gfx-08-wilderness-objects
git pull --ff-only origin graphics/gfx-08-wilderness-objects

python3 tools/gfx08_wilderness.py \
  --archive ~/Downloads/Dust_and_Debt_Forsaken_Master_Art_Source_v1.zip

xdg-open assets/forsaken_v1/gfx08/review.png

DUST_AND_DEBT_GFX08=1 DUST_AND_DEBT_GFX07=1 \
  DUST_AND_DEBT_GFX06=1 DUST_AND_DEBT_RETAINED_CANVAS=1 \
  ./Play_Dust_and_Debt.sh
```

The GFX-08 effect is visible outdoors **outside the safe town**, where
`Game.draw_scattered_props` draws its seeded decorative objects. In town,
the old starter-world PNG remains in place, so this pilot intentionally does
not redraw baked-in starter-map cacti or trees. The GFX-07/06 setup is only
necessary if you want the previous road improvements at the same time.

If the image pack isn't present or the manifest/alpha checks fail, the
original vector clutter is drawn. Omit `DUST_AND_DEBT_GFX08=1` to
disable the new sprites without rebuilding the game.

## Data and validation

- Source: original, SHA-verified, user-approved 17-board art ZIP
- Input: `boards/GFX-B01.png`, exact 1536×1024 magenta layout
- Output: four RGBA PNGs and `manifest.json` under
  `assets/forsaken_v1/gfx08/`
- All exported sprites require a transparent outer margin and complete
  bounding boxes; output alpha is checked
- Cached Tk PhotoImage references, no per-frame rasterization/Pillow
- Existing deterministic prop hash and outdoor-road/building/water exclusions
  stay identical
- No shadow generation and no added collision boxes
- GitHub CI includes a synthetic test for magenta keying, crop rejection,
  lower-foot collision candidates and fallback drawing

## QA gate / remaining work

Review `review.png` and an outdoor gameplay screenshot first. The source
art may show matting artifacts at complex leaves or fine twigs. On the
user's older Intel GPU, test a forest edge and a desert region and compare
render time with and without GFX08. Do not merge as default before review.

Next submilestones: clean individual B01 trees and foliage canopy/trunk
layers, integrate visually compatible GFX-B02/B03/B04 from separately
redrawn magenta art, author true collision footprints for solid objects,
and redraw starter-map vegetation independently of the baked ground image.
