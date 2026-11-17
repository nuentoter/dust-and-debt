"""Compose Western building sprites over the existing Cinder Creek world.

Offline Pillow-only pipeline. Source image/world coordinates and game collision
rectangles are never modified. Art is bottom-anchored, alpha-shaded and the old
rectangular building art is replaced with softly blended terrain.
"""
from pathlib import Path
import math
import random
from PIL import Image, ImageDraw
from cinder_creek_gfx import STARTER_BUILDINGS
from tools.cinder_creek_buildings import _font

SPRITE_BY_BUILDING = {
    "Sheriff": "sheriff", "Saloon": "saloon",
    "General Store": "store", "Doctor": "church",
    "Stable": "stable", "Hotel": "inn",
    "Station": "smithy", "Cabin": "house",
    "Outpost": "house", "Ranch": "stable",
}
REQUIRED_SPRITES = tuple(sorted(set(SPRITE_BY_BUILDING.values())))
DEFAULT_SPRITES = Path(__file__).resolve().parents[1] / "assets" / "gfx02" / "cinder_creek" / "sprites"
GROUND_MARGIN = 18
SHADOW_OFFSET = (5, 6)
SHADOW_OPACITY = 76


def sprites_available(sprite_dir=DEFAULT_SPRITES):
    root = Path(sprite_dir)
    return all((root / (stem + ".png")).is_file() for stem in REQUIRED_SPRITES)


def _median(values):
    values = sorted(values)
    return values[len(values) // 2]


def _terrain_color(image, x, y, w, h, margin):
    """Find surrounding ground colours without sampling the old roof.

    Sample several points on each side, outside the legacy rectangular
    building AND its baked outline/shadow. Median per-channel filtering
    avoids a single cactus or wooden prop dominating the fill colour.
    """
    points = []
    for i in range(1, 8):
        t = i / 8.0
        xx = x + int(t * max(w - 1, 1))
        yy = y + int(t * max(h - 1, 1))
        points.extend(((xx, y - margin), (xx, y + h + margin),
                       (x - margin, yy), (x + w + margin, yy)))
    pixels = []
    for xx, yy in points:
        xx = max(0, min(image.width - 1, xx))
        yy = max(0, min(image.height - 1, yy))
        pixels.append(image.getpixel((xx, yy))[:3])
    return tuple(_median(p[channel] for p in pixels) for channel in range(3))


def _ground_patch(image, box, seed, feather=GROUND_MARGIN):
    """Erase old box and its drop shadow with a feathered, textured ground fill.

    Centre of the original rectangular plot is fully covered. Outside its
    edges the terrain is alpha-blended over 'feather' pixels, so there can be
    no hard rectangular colour seam. The same seed yields identical results.
    """
    x, y, w, h = box
    if w <= 0 or h <= 0:
        raise ValueError("Invalid building footprint")
    # Legacy art left a dark rectangular outline up to ~10 px beyond the
    # building. Fully repaint that halo before the feather starts.
    halo = 12
    margin = halo + feather + 12
    colour = _terrain_color(image, x, y, w, h, margin)
    extent = halo + feather
    left, top = max(0, x - extent), max(0, y - extent)
    right, bottom = min(image.width, x + w + extent), min(image.height, y + h + extent)
    if left >= right or top >= bottom:
        return
    rng = random.Random(seed)
    original = image.crop((left, top, right, bottom)).convert("RGB")
    pixels = original.load()
    for j in range(bottom - top):
        py = top + j
        for i in range(right - left):
            px = left + i
            # Inside the footprint coverage is complete. Outside it,
            # interpolate smoothly toward the existing untouched terrain.
            dx = max(x - px, px - (x + w - 1), 0)
            dy = max(y - py, py - (y + h - 1), 0)
            dist = max(dx, dy)
            t = max(0.0, min(1.0, 1.0 - max(0, dist - halo) / feather))
            blend = t * t * (3.0 - 2.0 * t)
            if blend <= 0:
                continue
            noise = rng.choice((-12, -6, -3, 0, 2, 6, 11))
            fill = tuple(max(0, min(255, v + noise)) for v in colour)
            if blend >= 1:
                pixels[i, j] = fill
            else:
                old = pixels[i, j]
                pixels[i, j] = tuple(int(round(old[k] * (1.0 - blend) + fill[k] * blend))
                                     for k in range(3))
    image.paste(original, (left, top))


def _fit_sprite(sprite, x, y, w, h):
    """Crop transparent margins and preserve aspect ratio and bottom anchor."""
    if sprite.mode != "RGBA":
        sprite = sprite.convert("RGBA")
    box = sprite.getchannel("A").getbbox()
    if not box:
        raise ValueError("Sprite is entirely transparent")
    sprite = sprite.crop(box)
    max_w, max_h = max(1, w - 10), max(1, h - 8)
    scale = min(max_w / sprite.width, max_h / sprite.height)
    tw, th = max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))
    resized = sprite.resize((tw, th), Image.Resampling.NEAREST)
    left = x + (w - tw) // 2
    top = y + h - th - 4
    return resized, left, top


def _composite_shadow_and_sprite(image, sprite, left, top, opacity=SHADOW_OPACITY):
    """Shade only the alpha silhouette, not the entire rectangular lot."""
    alpha = sprite.getchannel("A")
    # Alpha scaled, not thresholded: soft/antialiased source edge remains soft.
    shadow_alpha = alpha.point(lambda value: round(value * opacity / 255))
    shadow = Image.new("RGB", sprite.size, (64, 46, 31))
    sx, sy = left + SHADOW_OFFSET[0], top + SHADOW_OFFSET[1]
    # Clipped paste for sprites near the overall world boundary.
    right = min(image.width, sx + sprite.width)
    bottom = min(image.height, sy + sprite.height)
    if sx < right and sy < bottom and sx >= 0 and sy >= 0:
        image.paste(shadow.crop((0, 0, right - sx, bottom - sy)),
                    (sx, sy), shadow_alpha.crop((0, 0, right - sx, bottom - sy)))
    image.paste(sprite.convert("RGB"), (left, top), alpha)


def _station_sign(image, x, y, w, h):
    d = ImageDraw.Draw(image)
    label = "STATION"
    font = _font(12)
    box = d.textbbox((0, 0), label, font=font)
    text_w = box[2] - box[0]
    cx = x + w // 2
    top = y + int(h * .70)
    d.rectangle((cx - text_w // 2 - 8, top - 4, cx + text_w // 2 + 8, top + 17),
                fill="#553b2d", outline="#c8a16d", width=2)
    d.text((cx - text_w // 2, top - 2), label, font=font, fill="#f1d5a2")


def validate_sprite_pack(sprite_dir=DEFAULT_SPRITES):
    """Fail early on missing, invalid, or fully opaque building PNGs."""
    root = Path(sprite_dir)
    problems = []
    for stem in REQUIRED_SPRITES:
        path = root / (stem + ".png")
        if not path.is_file():
            problems.append("missing " + path.name)
            continue
        try:
            with Image.open(path) as opened:
                if opened.format != "PNG":
                    problems.append(stem + ": expected PNG")
                if min(opened.size) < 8:
                    problems.append(stem + ": fewer than 8 pixels on an axis")
                rgba = opened.convert("RGBA")
                extrema = rgba.getchannel("A").getextrema()
                if extrema[1] == 0:
                    problems.append(stem + ": completely transparent")
                if extrema[0] == 255:
                    problems.append(stem + ": no transparent background")
        except (OSError, ValueError) as exc:
            problems.append(stem + ": " + str(exc))
    return problems


def paint_sheet_buildings(image, sprite_dir=DEFAULT_SPRITES,
                          buildings=STARTER_BUILDINGS):
    """Use the sheet's cut-out art at the exact existing game footprints.

    No file means no changes (procedural fallback). An *incomplete/invalid*
    pack is rejected rather than accidentally baking flawed or blank art.
    """
    root = Path(sprite_dir)
    if not sprites_available(root):
        return []
    problems = validate_sprite_pack(root)
    if problems:
        raise ValueError("Invalid reference sprite pack: " + "; ".join(problems))
    if image.mode != "RGB":
        raise ValueError("Expected RGB baked map")
    sprites = {}
    for stem in REQUIRED_SPRITES:
        with Image.open(root / (stem + ".png")) as opened:
            sprites[stem] = opened.convert("RGBA")
    updated = []
    for index, (name, x, y, w, h) in enumerate(buildings):
        if name not in SPRITE_BY_BUILDING:
            raise ValueError("Unknown building: " + name)
        if min(x, y) < 0 or x + w > image.width or y + h > image.height:
            raise ValueError("Building outside map: " + name)
        sprite, left, top = _fit_sprite(sprites[SPRITE_BY_BUILDING[name]], x, y, w, h)
        # Erase the historical rectangle and its drawn drop shadow first.
        _ground_patch(image, (x, y, w, h), seed=1889 + index * 53)
        _composite_shadow_and_sprite(image, sprite, left, top)
        if name == "Station":
            _station_sign(image, x, y, w, h)
        updated.append(name)
    return updated
