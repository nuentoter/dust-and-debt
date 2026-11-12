#!/usr/bin/env python3
"""GFX sprite import: alpha, alignment, shadow, lot blending, deterministic bake."""
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PIL import Image, ImageDraw
from cinder_creek_gfx import STARTER_BUILDINGS
from tools.extract_western_sheet import remove_sheet_background
from tools.cinder_creek_sheet_art import (
    REQUIRED_SPRITES, SPRITE_BY_BUILDING, _fit_sprite, _ground_patch,
    _composite_shadow_and_sprite, paint_sheet_buildings,
    sprites_available, validate_sprite_pack,
)

with tempfile.TemporaryDirectory() as temp:
    art=Path(temp)
    base=Image.new("RGB",(2400,1600),(196,155,110))
    assert not sprites_available(art)
    assert paint_sheet_buildings(base,art)==[]
    assert validate_sprite_pack(art)
    for index,name in enumerate(REQUIRED_SPRITES):
        tile=Image.new("RGBA",(32,32),(0,0,0,0))
        d=ImageDraw.Draw(tile)
        d.rectangle((3,3,28,29),fill=(100+index,60,30,255))
        tile.save(art/(name+".png"))
    assert sprites_available(art)
    assert not validate_sprite_pack(art)
    # A partially missing pack produces no changes, and no silent half-bake.
    (art/"store.png").unlink()
    assert not sprites_available(art)
    assert paint_sheet_buildings(base,art)==[]
    invalid=Image.new("RGBA",(32,32),(170,70,50,255))
    invalid.save(art/"store.png")
    assert any("no transparent background" in message
               for message in validate_sprite_pack(art))
    try:
        paint_sheet_buildings(base,art)
        raise AssertionError("Opaque sprites must not pass production validation")
    except ValueError:
        pass
    valid=Image.new("RGBA",(32,32),(0,0,0,0))
    ImageDraw.Draw(valid).rectangle((2,2,30,29),fill=(170,70,50,255))
    valid.save(art/"store.png")
    assert not validate_sprite_pack(art)

    # New art remains inside the existing logical footprints and the world
    # coordinate map does not change.
    before=base.copy()
    painted=paint_sheet_buildings(base,art)
    assert painted==[row[0] for row in STARTER_BUILDINGS]
    assert base.size==before.size
    assert base.getpixel((10,10))==before.getpixel((10,10))
    assert base.getpixel((400,380))!=before.getpixel((400,380))
    assert set(SPRITE_BY_BUILDING.values())==set(REQUIRED_SPRITES)

# No stretched/doubly anchored sprites. Transparent margins are trimmed.
sprite=Image.new("RGBA",(24,48),(0,0,0,0))
ImageDraw.Draw(sprite).rectangle((4,5,19,44),fill=(140,80,30,255))
fitted,left,top=_fit_sprite(sprite,50,50,100,100)
assert fitted.width <= 90 and fitted.height <= 92
assert left >= 50 and top >= 50
assert top+fitted.height==146
assert abs(fitted.width / fitted.height - 16/40) < .04

# Old rectangle AND its shadow halo are fully erased, without a new box seam.
land=Image.new("RGB",(320,260),(196,155,110))
ld=ImageDraw.Draw(land)
ld.rectangle((60,40,230,190),fill=(65,46,33))
_ground_patch(land,(60,40,160,140),seed=1337)
assert land.getpixel((240,100))==(196,155,110)  # outside blended region
assert min(land.getpixel((225,110)))>110  # old dark border is gone
assert min(land.getpixel((100,70)))>110  # old building is gone
# No hard jump across the fill/feather boundary.
a=land.getpixel((245,100))
b=land.getpixel((246,100))
assert max(abs(a[i]-b[i]) for i in range(3))<32

# Shadow opacity follows actual sprite silhouette, not its entire canvas box.
ground=Image.new("RGB",(90,90),(196,155,110))
shape=Image.new("RGBA",(20,20),(0,0,0,0))
ImageDraw.Draw(shape).rectangle((4,4,10,10),fill=(120,70,45,255))
_composite_shadow_and_sprite(ground,shape,40,40)
assert ground.getpixel((54,56))!=(196,155,110)  # shadow offset
assert ground.getpixel((59,60))==(196,155,110)  # transparent sprite corner
assert ground.getpixel((45,45))==(120,70,45)    # opaque building itself

# Extraction must remove outer matte without destroying enclosed dark windows.
fixture=Image.new("RGBA",(16,16),(8,18,23,255))
drawer=ImageDraw.Draw(fixture)
drawer.rectangle((3,3,12,12),fill=(145,75,42,255))
drawer.rectangle((6,6,9,9),fill=(10,20,25,255))
cut=remove_sheet_background(fixture)
assert cut.size==(10,10)
assert cut.getpixel((0,0))[3]==255
assert cut.getpixel((4,4))[3]==255
print("Cinder Creek sprite integration, shadow and terrain tests OK")
