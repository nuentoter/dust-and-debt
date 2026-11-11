"""GFX-02 Cinder Creek art: optional baked world replacement.

This module has no Pillow runtime dependency. Existing world-space coordinates,
actor drawing, collisions, doors and mission triggers remain authoritative.
"""
import os

ZONE_BOUNDS = (0, 0, 2400, 1600)
ART_RELATIVE_PATH = os.path.join("gfx02", "cinder_creek", "world_gfx02.png")
BASE_RELATIVE_PATH = "world.png"

# Mirrored only for asset-building protection; gameplay continues to use
# game.BUILDINGS and its unchanged interaction rectangles.
STARTER_BUILDINGS = (
    ("Sheriff", 320, 300, 196, 130),
    ("Saloon", 565, 315, 238, 160),
    ("General Store", 854, 318, 204, 144),
    ("Doctor", 320, 694, 169, 120),
    ("Stable", 835, 728, 210, 144),
    ("Hotel", 540, 735, 215, 168),
    ("Station", 1150, 1321, 240, 115),
    ("Cabin", 1670, 320, 140, 110),
    ("Outpost", 1960, 1150, 140, 100),
    ("Ranch", 1470, 850, 160, 125),
)

def select_world_image(assets_root, enabled=False):
    """Return an existing PNG, falling back to the legacy art."""
    legacy = os.path.join(assets_root, BASE_RELATIVE_PATH)
    upgraded = os.path.join(assets_root, ART_RELATIVE_PATH)
    return upgraded if enabled and os.path.isfile(upgraded) else legacy

def validate_starter_geometry(buildings):
    """Prevent accidental drift between art protection and game coordinates."""
    lookup = {name: (x, y, w, h) for name, x, y, w, h in buildings}
    return all(lookup.get(name) == (x, y, w, h)
               for name, x, y, w, h in STARTER_BUILDINGS)

def inside_art(x, y):
    left, top, width, height = ZONE_BOUNDS
    return left <= x < left + width and top <= y < top + height
