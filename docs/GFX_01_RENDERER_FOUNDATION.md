# GFX-01 — Renderer Foundation (experimental)

Status: **prototype on feature branch; not production-approved**.

## What changed

- Added an opt-in `RetainedCanvas` Tk backend. It reuses Canvas item identities between complete frames where a drawing primitive and option-name set match. Unchanged coordinates and options are not reissued to Tk.
- The original legacy renderer remains the default. The game's visual calls, projection, world geography, collision, and save data are unchanged.
- Early-return screens (title, death, ending, interiors) now finish their retained frames through a `try/finally` wrapper.
- Added object-order, stale-option, and whole-game rendering smoke tests.
- Added a side-by-side timing harness with reproducible scene coordinates.

## Commands

```sh
# Default: unchanged legacy renderer
./Play_Dust_and_Debt.sh

# Test experimental renderer manually
DUST_AND_DEBT_RETAINED_CANVAS=1 ./Play_Dust_and_Debt.sh

# Headless regression
DUST_AND_DEBT_SILENT=1 xvfb-run -a python3 tests/render_cache_test.py

# Capture both modes with the same frame sequence
xvfb-run -a -s '-screen 0 1280x1024x24' python3 tools/benchmark_renderer.py --frames 24

# Existing full game tests
xvfb-run -a python3 tools/run_tests.py
```

## Implementation boundaries

Each frame is still described by the existing Canvas drawing methods. At a
given sequence index, an old item of the same kind with identical option
**names** may be reused; changed coordinates/options are applied only when
necessary. If type or option names change, a fresh item is created. Unused
items are deleted. The exact painter stacking sequence is restored when item
identity order changes.

This is **not** tile batching, GPU acceleration, or a finished sprite
renderer. Fast camera motion can still update most geometry and may erase any
benefit. In crowded scenes, retagging when the item list changes can cost
more than recreating. These costs must be measured, not presumed.

## Acceptance gates before default enablement

1. All existing regression scripts pass, plus the new retained-render test.
2. Title, map, interiors, normal/low detail, dialogue, weather, and combat are
   visually identical to the old renderer in representative Xvfb captures.
3. A long live ride confirms no trails, stale panels, ghost items, incorrect
   draw order, or lingering interface elements.
4. Benchmark repeated scenes and camera movement on Archcraft/X11 / older
   Intel hardware. Retention must outperform legacy **without** significant
   regressions or memory growth.
5. If it fails performance acceptance, disable and retain the benchmark data;
   evaluate cached tile/raster layers or SDL rather than shipping a slower
   default.

Do not treat Xvfb timings as real hardware FPS. No saves or world geometry
need migration. Subsequent terrain and sprite milestones should wait for
this foundation's performance decision.
