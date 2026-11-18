#!/usr/bin/env python3
"""GFX-09 B01 full silhouette, alpha/footprint and immutable rock geometry QA."""
import sys
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.gfx09_solid_art import convert_sprite,SPECS
from forsaken_solid_objects import choose_rock_art,draw_rock_sprite
from tools.gfx05_collision import collision_rows,collide_at
from natural_terrain import ROCKS,landform_solid
from cinder_creek_gfx import STARTER_BUILDINGS

assert len(SPECS)==2 and set(SPECS)=={"pine","dead_tree"}
assert choose_rock_art(True,"forest",0)=="pine"
assert choose_rock_art(True,"scrub",3)=="dead_tree"
assert choose_rock_art(True,"desert",3)=="rock"
assert choose_rock_art(False,"forest",3)=="rock"

source=Image.new("RGB",(120,130),(255,0,255))
paint=ImageDraw.Draw(source)
paint.polygon(((57,14),(31,69),(40,98),(74,98),(86,70)),fill=(40,35,32))
paint.rectangle((52,72,65,112),fill=(75,46,32))
result,record=convert_sprite(source,(0,0,120,130),(42,67))
assert result.mode=="RGBA" and result.size==(54,79)
assert result.getpixel((0,0))[3]==0
assert result.getpixel((27,45))[3]==255
rows=collision_rows(result,"tree")
assert rows and any(collide_at(rows,x,y) for y,x,b in rows)
assert not collide_at(rows,0,0)
assert record["physical_collision_activated"] is False
# Deliberately trim tree from the right; should NEVER silently export it.
try:
    convert_sprite(source,(35,0,75,130),(42,67))
except ValueError:pass
else:raise AssertionError("Truncated tree passed source crop QA")

class Fake:
    def __init__(self):self.images=[]
    def create_image(self,*args,**kwargs):self.images.append((args,kwargs))
fake=Fake()
sprites={"pine":object(),"dead_tree":object(),"rock":object()}
assert draw_rock_sprite(fake,sprites,18,22,25,True,"forest",0)
assert fake.images[-1][1]["tags"]==("gfx09_solid_landform",)
assert fake.images[-1][1]["anchor"]=="s"
assert not draw_rock_sprite(fake,{},18,22,25,True,"forest",0)
# Solid position/collision coordinates remain exactly as originally authored.
before=tuple(ROCKS)
assert any(solid for _,_,_,solid in ROCKS)
for x,y,rad,solid in ROCKS[:12]:
    assert isinstance(landform_solid(x,y,0),bool)
assert before==ROCKS
assert len(STARTER_BUILDINGS)==10
print("PASS: original ROCKS positions/collision, full magenta silhouettes, physical-footprint QA, solid-art fallback")
