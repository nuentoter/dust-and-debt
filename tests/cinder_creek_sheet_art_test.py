#!/usr/bin/env python3
"""Verify real-sheet override, geometry and missing-asset fallback in Pillow."""
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PIL import Image, ImageDraw
from cinder_creek_gfx import STARTER_BUILDINGS
from tools.extract_western_sheet import remove_sheet_background
from tools.cinder_creek_sheet_art import (REQUIRED_SPRITES,SPRITE_BY_BUILDING,
    paint_sheet_buildings,sprites_available)

with tempfile.TemporaryDirectory() as temp:
    art=Path(temp)
    base=Image.new("RGB",(2400,1600),(196,155,110))
    assert not sprites_available(art)
    assert paint_sheet_buildings(base,art)==[]
    for index,name in enumerate(REQUIRED_SPRITES):
        tile=Image.new("RGBA",(32,32),(0,0,0,0))
        draw=ImageDraw.Draw(tile)
        draw.rectangle((3,3,28,29),fill=(100+index,60,30,255))
        tile.save(art/(name+".png"))
    assert sprites_available(art)
    # One missing source asset means the entire pass cleanly falls back.
    (art/"store.png").unlink()
    assert not sprites_available(art)
    assert paint_sheet_buildings(base,art)==[]
    Image.new("RGBA",(32,32),(170,70,50,255)).save(art/"store.png")
    assert sprites_available(art)
    before=base.copy()
    painted=paint_sheet_buildings(base,art)
    assert painted==[row[0] for row in STARTER_BUILDINGS]
    assert base.getpixel((10,10))==before.getpixel((10,10))
    assert base.getpixel((400,380)) != before.getpixel((400,380))
    assert base.getpixel((1210,1380)) != before.getpixel((1210,1380))
    assert set(SPRITE_BY_BUILDING.values())==set(REQUIRED_SPRITES)
# A background-connected dark matte becomes transparent, while an enclosed
# dark window survives inside a roof.
fixture=Image.new("RGBA",(16,16),(8,18,23,255))
drawer=ImageDraw.Draw(fixture)
drawer.rectangle((3,3,12,12),fill=(145,75,42,255))
drawer.rectangle((6,6,9,9),fill=(10,20,25,255))
cut=remove_sheet_background(fixture)
assert cut.size==(10,10)
assert cut.getpixel((0,0))[3]==255
assert cut.getpixel((4,4))[3]==255
print("Cinder Creek real-sheet art tests OK")
