#!/usr/bin/env python3
"""GFX-03 Gothic buildings: border removal, alpha, ground and route safety."""
import sys
from pathlib import Path
from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.forsaken_buildings import silhouette, _erase_old_art, CROPS
from cinder_creek_gfx import STARTER_BUILDINGS

# An isolated label/frame line must never become part of the sprite.
source=Image.new("RGB",(140,110),(14,18,19))
d=ImageDraw.Draw(source)
d.rectangle((15,4,125,6),fill=(154,113,83))  # disconnected border
d.rectangle((26,21,113,104),fill=(124,82,55))
d.rectangle((43,69,56,92),fill=(23,20,18))   # dark window should be opaque
cut=silhouette(source)
alpha=cut.getchannel("A")
assert 70<=cut.width<=115 and 65<=cut.height<=100,cut.size
assert alpha.getextrema()==(255,255) or alpha.getextrema()==(0,255)
assert cut.getchannel("A").getbbox() is not None
assert cut.height<100  # disconnected framing removed

# Clear the original building picture without touching surrounding road
# pixels, and never move/resize the gameplay footprint.
world=Image.new("RGB",(190,150),(170,132,99))
ImageDraw.Draw(world).rectangle((49,49,110,110),fill=(50,42,34))
ground=Image.new("RGB",(64,64),(118,98,85))
protect=Image.new("L",world.size,0)  # all outside is a protected road
before=world.copy()
_erase_old_art(world,(50,50,60,60),ground,protect)
assert world.getpixel((30,70))==before.getpixel((30,70))
assert world.getpixel((48,70))==before.getpixel((48,70))
assert world.getpixel((55,70))!=(50,42,34)
assert world.getpixel((75,70))!=(50,42,34)
assert world.getpixel((55,70))!=(118,98,85)  # not a tiled gray square

assert len(STARTER_BUILDINGS)==10
assert set(name for name,*_ in STARTER_BUILDINGS)==set(CROPS)
print("GFX-03 D01 matte, alpha and road-safe building replacement tests OK")
