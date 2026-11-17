#!/usr/bin/env python3
"""GFX-08: anti-crop magenta extraction and decorative render safety."""
import sys
import tempfile
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.gfx08_wilderness import extract_one,is_matte,CROPS,SIZES
from forsaken_wilderness import draw_wilderness,NAMES
from tools.gfx05_collision import collision_rows

assert is_matte(255,0,255)
assert is_matte(244,21,233)
assert not is_matte(38,28,25)
assert not is_matte(179,55,72)
assert len(CROPS)==4 and set(CROPS)==set(NAMES)
with tempfile.TemporaryDirectory() as directory:
    root=Path(directory)
    image=Image.new("RGB",(110,105),(255,0,255))
    painter=ImageDraw.Draw(image)
    painter.polygon(((22,81),(31,33),(47,14),(62,31),(80,82)),
                    fill=(76,63,52))
    painter.rectangle((37,53,59,81),fill=(35,25,24))
    result=extract_one(image,(0,0,110,105),root/"sprite.png",(38,34))
    assert result["alpha_corners_transparent"]
    with Image.open(root/"sprite.png") as f:
        assert f.mode=="RGBA" and f.size==(46,42)
        assert f.getpixel((0,0))[3]==0
        assert f.getpixel((23,22))[3]==255
        # Only the physical lower band is a blocker candidate. However
        # decorative wilderness objects are intentionally NOT made solid.
        assert collision_rows(f,"shrub")==()
        assert collision_rows(f,"boulder")
    # A crop that slices the object's silhouette must fail rather than
    # silently repeat the historical chopped-building problem.
    try:
        extract_one(image,(35,20,77,85),root/"bad.png",(30,30))
    except ValueError:pass
    else:raise AssertionError("Cropped object was accepted")

class FakeCanvas:
    def __init__(self):self.calls=[]
    def create_image(self,*args,**kwargs):self.calls.append((args,kwargs))
canvas=FakeCanvas()
sprites={n:object() for n in NAMES}
for i in range(4):
    assert draw_wilderness(canvas,sprites,100,200,i)
    xy,opts=canvas.calls[-1]
    assert xy==(100,207) and opts["anchor"]=="s"
    assert opts["tags"]==("gfx08_wilderness",)
assert not draw_wilderness(canvas,{},100,200,5)
print("PASS: B01 magenta alpha, complete silhouettes, foot masks, cached sprite draw and legacy fallback")
