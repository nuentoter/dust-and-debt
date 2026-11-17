# GFX-04 — Redrawn Gothic buildings in working Cinder Creek

This milestone uses the newly redrawn **high-contrast magenta** 1448x1086,
12-building sheet. It does **not** use the cropped black-background D01
concept sheet, and it does not use v1-v10 automatic masks.

## Install and run on Archcraft

1. Update the new development branch:
   
   ```bash
   cd ~/dust-and-debt-github
   git fetch origin
   git switch graphics/gfx-04-redrawn-buildings
   git pull --ff-only origin graphics/gfx-04-redrawn-buildings
   ```

2. Download `Dust_and_Debt_GFX04_Redrawn_Assets.zip` from this conversation.
   Unzip directly in the repository root:

   ```bash
   unzip -o ~/Downloads/Dust_and_Debt_GFX04_Redrawn_Assets.zip
   ```

   It supplies `assets/forsaken_v1/redrawn/GFX-D01-redrawn.png`,
   already clean independent RGBA building exports and a reference preview.
   They remain outside Git because the existing art-pack ignore rule
   excludes `assets/forsaken_v1/`.

3. Bake the real gameplay starter-town illustration:

   ```bash
   python3 tools/build_redrawn_buildings.py
   xdg-open assets/forsaken_v1/runtime/redrawn_before_after_cinder_creek.png
   ```

4. Play the optional new version:

   ```bash
   DUST_AND_DEBT_FORSAKEN_V1=1 DUST_AND_DEBT_RETAINED_CANVAS=1 ./Play_Dust_and_Debt.sh
   ```

To return to the existing graphics, start the game without
`DUST_AND_DEBT_FORSAKEN_V1=1`. The bake starts from the unchanged
`assets/world.png` and does not stack on old experimental baked worlds.
The existing startup image selector verifies a 4800x3200 PNG. No runtime
Pillow/Numpy requirement is added.

## Technical policy

- Magenta is an **editing matte**. The generator creates RGBA exports,
  with alpha zero for background pixels, from all 12 full-redrawn buildings.
- Only 10 authored original Cinder Creek buildings are replaced for now,
  using existing positions; Outpost reuses the cabin.
- Existing building collision rectangles, missions, NPC anchors and roads
  remain authoritative.
- A source-soil-colour reconstruction fills old painted rooftop pixels
  inside the old footprint before the alpha compositing step. Nothing
  outside the original rectangle is erased.
- No baked cast shadows. The nearest-neighbour resizer preserves shape,
  aspect ratio and south-centre visual anchor.
- The user reviews the 1920x600 before/after image and new on-machine game
  screenshot before merging the branch. A pixel test cannot guarantee no
  leftover painted shadow or perfect doorway alignment in the real map.

## Pending after visual acceptance

- Ensure source-world old shadow halos (outside the original collision rect)
  do not show on the user's map.
- Review signs, entrances, roads immediately outside the hotel, saloon,
  sheriff, and stable.
- Extend the graphic standard to other towns.
- Integrate the new inn, bank and undertaker graphics into authored locations
  after gameplay and world-layout review.
