# GFX-02 — Cinder Creek terrain and artwork prototype

**Status:** opt-in first pass; visual approval and real-hardware benchmarking pending.

This is the first step toward the uploaded **A Western Tale** 16×16 Western
pixel-art style guide. The generated village mockup is *visual reference only*,
not game-coordinate-aligned artwork. Inserting it directly would move doors,
roads, collision silhouettes and mission locations. The production renderer
therefore stays anchored to the existing 4800×3200 original-world source image.

## What this changes

- `cinder_creek_gfx.py`: authoritative baked-art selection and fixed gameplay
  alignment safeguards.
- `tools/build_cinder_creek_scene.py`: deterministic offline Pillow bake
  adding Western-pixel-style ground detail, scrub, rocks, cacti and flowers to
  the existing source art, avoiding the authored building footprints and major
  road corridors. Outputs a PNG and a JSON build manifest.
- `game.py`: opt-in image replacement, **without** extra draw calls or
  gameplay geometry modifications.
- `tests/cinder_creek_gfx_test.py`: bounds, preserved building rectangles,
  image fallback, optional output dimensions and live game render smoke test.

This is deliberately a **terrain/decor prototype**, NOT a complete reconstruction
of the reference's saloon, sheriff, house and railway pixel art. Building sprite
replacement needs independently cut-out transparent artwork positioned to the
existing gameplay door footprints; that is a subsequent GFX-02 pass.

## Build once, then launch

```sh
cd ~/dust-and-debt-github
python3 -m pip install --user Pillow  # if not installed; use an Arch package or venv if needed
python3 tools/build_cinder_creek_scene.py
DUST_AND_DEBT_RETAINED_CANVAS=1 DUST_AND_DEBT_GFX02=1 ./Play_Dust_and_Debt.sh
```

Without a generated `world_gfx02.png`, or without the GFX02 environment
variable, the game automatically keeps `assets/world.png` as before.
Pillow is only needed by the build script, **not** by game runtime.

Generated files are:
- `assets/gfx02/cinder_creek/world_gfx02.png`
- `assets/gfx02/cinder_creek/build_manifest.json`

A comparative run is simply:

```sh
DUST_AND_DEBT_RETAINED_CANVAS=1 ./Play_Dust_and_Debt.sh
```

## Acceptance gates

- [ ] Compare standard and GFX02 renders at the sheriff, saloon, general
      store, stable, hotel and station.
- [ ] Confirm doors, NPCs, prompts, horse travel and shooting remain usable.
- [ ] Confirm no scenery floats over buildings or blocks road visibility.
- [ ] Compare performance using the retained backend, normal and low detail.
- [ ] Review the border at x=2400 / y=1600 and continue the world terrain
      transition work before making the new art default.
- [ ] Produce properly aligned, transparent multi-layer building assets for
      the reference-style architecture, plus a camera review capture.

The new art replaces only the starter image already used by game.py; all
other map terrain and existing v2.9 road, trail and collision layers remain
unchanged. We do not change save compatibility or player progression.
