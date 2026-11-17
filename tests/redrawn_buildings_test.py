#!/usr/bin/env python3
"""GFX-04: extraction/alpha plus opt-in bake never changes gameplay geometry."""
import sys
import tempfile
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.build_redrawn_buildings import extract,bake_world,BUILDINGS,magenta

from cinder_creek_gfx import STARTER_BUILDINGS
assert len(BUILDINGS)==len(STARTER_BUILDINGS)==10
for name,x,y,w,h,stem in BUILDINGS:
    assert (name,x,y,w,h) in STARTER_BUILDINGS

assert magenta((240,10,242))
assert not magenta((40,25,23))
assert not magenta((124,74,61))

with tempfile.TemporaryDirectory() as folder:
    temp=Path(folder)
    sheet=Image.new("RGB",(1448,1086),(240,12,242))
    d=ImageDraw.Draw(sheet)
    for col in range(4):
        for row in range(3):
            x=col*362+40;y=row*362+85
            d.rectangle((x,y,x+265,y+254),fill=(91,64,47))
            d.rectangle((x+74,y+100,x+119,y+180),fill=(19,17,16))
    assets=temp/"buildings"
    records=extract(sheet,assets)
    assert len(records)==12
    for record in records:
        sprite=Image.open(assets/(record["id"]+".png"))
        assert sprite.mode=="RGBA"
        assert sprite.getpixel((0,0))[3]==0
        assert sprite.getpixel((sprite.width//2,sprite.height//2))[3]==255
        assert sprite.getpixel((sprite.width//2,sprite.height//2))[:3]!=(240,12,242)
    world=Image.new("RGB",(500,400),(185,147,105))
    d=ImageDraw.Draw(world)
    d.rectangle((40,40,178,136),fill=(50,38,30))
    before=world.copy()
    result,placed=bake_world(world,assets,locations=(("Mock",40,40,138,96,"sheriff"),))
    assert len(placed)==1
    assert placed[0]["south_anchor"]==[109,136]
    assert world.tobytes()==before.tobytes()
    assert result.getpixel((10,10))==before.getpixel((10,10))
    assert result.getpixel((495,395))==before.getpixel((495,395))
    assert result.getpixel((109,90))!=before.getpixel((109,90))
print("GFX-04 magenta extraction, alpha, sprite bake and immutable geometry OK")
