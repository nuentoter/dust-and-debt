# Dust & Debt Graphics Integration Standard (GFX-STD-01)

**Applies to:** every new Western pixel-art tile, prop, building, creature,
character, animation and static scene in Dust & Debt. This is an engineering
contract, not just an art-style mood board.

**Visual target:** the supplied `A Western Tale` Western village sheet:
hand-authored wood and stone textures, nuanced roof and porch silhouettes,
muted desert earth, warm highlights, clear shape at 960×600, and crisp pixels.
Do not replace this look with flat procedural rectangles.

## 1. One source of truth for gameplay geometry

- `game.BUILDINGS`, authored routes, doors, NPC positions and collision code
  remain **gameplay truth**. Sprite placements and painting may not alter them.
- World coordinates are game pixels: original starter image is **4800×3200**,
  origin `(0, 0)`, and native game view is **960×600**.
- Building art is anchored `south_center`: horizontally centred and the
  south/front edge sits near the previous building rectangle's south edge.
- **Never stretch to a collision rectangle independently on both axes.**
  Trim transparent edges and resize with a single aspect-preserving scale.
- If art and collision cannot be aligned without visible mismatch, adjust
  **the art**, add an explicit entrance/porch art anchor, or log an exception
  for later geometry review. Never secretly move a door or collision box.
- Rails, roads, bridges and water edges use existing authored route data.

## 2. Asset handoff and file format

- Source sprite: **PNG RGBA**, with genuine transparent background and no
  dark presentation-sheet matte, rectangular drop shadow, or caption.
- Native pixel-art reference grid: **16×16**. Bigger sprites may be built from
  multiple tiles; do not force an entire building into 16×16.
- Export at native pixel scale wherever possible; baked scene compositing
  uses Pillow offline and **nearest-neighbour** resizing, no bilinear blur.
- Lowercase snake-case names, e.g. `saloon.png`, `campfire_idle.png`.
- Keep authored master files separately from runtime derivatives. The
  `world_gfx02.png` bake is generated, not an editable source asset.
- Sprite directions have canonical order `s,sw,w,nw,n,ne,e,se`. Animation
  frames have consistent canvas dimensions, identical feet-pivot and alpha
  padding across directions. Suggested initial hero frame is **32×48**, horse
  **48×64**; animation counts are targets, not fake placeholder frames.
- Future individual sprite metadata must contain at least:
  `id`, `kind`, `source`, `rights`, `anchor`,
  `native_dimensions`. Example:

```json
{
  "id": "cinder_creek_saloon",
  "kind": "building",
  "source": "A Western Tale user-supplied reference sheet",
  "rights": "verify before redistribution",
  "anchor": "south_center",
  "native_dimensions": [180, 130],
  "gameplay_binding": "BUILDINGS:Saloon",
  "scale_policy": "preserve_aspect",
  "layers": ["static_building"],
  "qa": {"visual_review": false, "collision_review": false}
}
```

Note that a user-provided reference sheet is not automatically licensed for
redistribution. Verify original ownership and reuse permissions **before**
including its artwork in a public release.

## 3. Compositing and ground-shadow rules

**Mandatory, prompted by the Cinder Creek artifact report:**

1. Source sprites must be cropped to nonempty alpha bounds. Reject completely
   opaque presentation crops and missing/blank PNGs.
2. Remove the *old* rectangle and its baked shadow halo before importing a
   replacement. Sample surrounding terrain **outside the entire footprint**,
   fill the former roof zone, and blend its outer region with a feathered edge.
3. The dirt fill must be seeded/deterministic, softly textured, and must not
   leave an observable axis-aligned box. Never add a rectangle of uniform
   darkness as a shadow.
4. Derive shadows from the **sprite alpha mask**, tint dark brown with partial
   opacity, and offset consistently (currently **+5,+6** world pixels at
   **max alpha 76/255**). Transparent gaps must remain unshadowed.
5. Preserve aspect ratio and align visual entrance/foot-of-building to the
   existing south/front edge. Never resize a building to arbitrary width
   **and** height simultaneously.
6. Compose static terrain, buildings, and static props **offline** into
   baked PNG layers when useful. Retain a separate foreground layer only if
   actors need to pass behind roof awnings, branches or arches.
7. Don't introduce collision via decorative props until their gameplay
   semantics and accessibility are explicitly reviewed.

## 4. Layers and renderer budget

Use the order in `assets/gfx02/asset_rules.json`: terrain, ground decals,
building ground shadow, static structure, ground props, actors, foreground
occluders, weather/lighting, HUD.

- The Tk Canvas retained renderer remains opt-in until established by
  gameplay benchmarks. Don't replace a few baked sprites with hundreds of
  per-frame `create_*` primitives.
- Load/cache sprites once, not each frame; clip to viewport; use nearest
  sampling. Avoid a new PNG dependency at runtime.
- Protect the old Intel HD Graphics/X11 path. Compare normal and low detail
  with `tools/benchmark_renderer.py` and live gameplay; Xvfb is not hardware
  FPS evidence.
- Dynamic art may use directional sprite strips or sheets, with static data
  for frame positions/pivots rather than hard-coded offsets per animation.

## 5. Repeatable change workflow

1. **Reference / permissions:** identify visual reference and provenance,
   confirm distribution rights. Keep the source PNG unchanged.
2. **Cut / matte:** extract sprites from the sheet using
   `tools/extract_western_sheet.py` or a reviewed transparent source file.
3. **Preflight:** run `python3 tools/validate_graphics_assets.py --require-sheet`
   *after baking* when shipping sheet art; it checks sizes, transparency,
   source claim, art count and geometry guards.
4. **Fit / anchor:** use the per-asset metadata and existing game coordinates.
   Draw shadow from alpha, never from a rectangle.
5. **Bake:** `python3 tools/build_cinder_creek_scene.py --require-sheet`.
   Check `art_source=user_supplied_sheet` in the manifest. Builds must be
   deterministic with stable seeds, and repeat builds must not degrade art.
6. **Automated tests:** run `tests/cinder_creek_sheet_art_test.py`,
   `tests/cinder_creek_buildings_test.py`,
   `tests/cinder_creek_gfx_test.py`, and the complete regression suite.
   CI includes the asset quality gate.
7. **Visual acceptance:** capture day/dusk, entrances, sidewalks, riding and
   combat at several zoom/camera positions; explicitly inspect shadow halos,
   background seams, pixel blur, door overlap, z-order, labels and NPC occlusion.
8. **Performance acceptance:** compare retained-render A/B measurements on
   the target Archcraft laptop and document any regression.
9. **GitHub-first release:** stage on a feature branch and draft PR; preserve
   the legacy art fallback. Merge only after CI, screenshot review, live
   movement checks and authorization for shipped source artwork.

## 6. Reject conditions

A graphics PR must not be merged if it has any of these:
- rectangular lot outline/shadow, cutout matte, unwanted halo or transparent
  fringe, disproportionate stretching or blurry filtering;
- door/quest marker visually disconnected from the relevant building;
- resized/cropped world image that alters the 4800×3200 starter coordinates;
- missing required sprite or incorrectly reported procedural fallback;
- art with unresolved redistribution permissions packaged for release;
- low-detail or old hardware performance regression without mitigation;
- missing screenshot comparisons, required tests or validation record.

**Source of truth for automated checks:**
`assets/gfx02/asset_rules.json`, enforced by
`tools/validate_graphics_assets.py`. Update this standard, its JSON contract,
its tests, and its project implementation together whenever conventions
intentionally change.
