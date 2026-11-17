#!/usr/bin/env python3
"""GFX-06: connected road painting respects authored geometry and A02 source."""
import hashlib
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from forsaken_route_renderer import (
    draw_forsaken_routes,validated_palette,DEFAULT_PALETTE,_visible_segments,
)
from tools.gfx06_road_palette import build_palette
from tools.gfx05_pipeline import EXPECTED_GROUPS,ROAD_SAMPLES
from new_austellia import ROADS,RAILS,TRAILS,SECONDARY_ROADS
from frontier_route_art import clip_segment

class FakeCanvas:
    def __init__(self):self.lines=[]
    def create_line(self,*coords,**kwargs):
        self.lines.append((coords,kwargs))
        return len(self.lines)

pal=validated_palette({"road":"#556677","ruts":"not-a-color"})
assert pal["road"]=="#556677"
assert pal["ruts"]==DEFAULT_PALETTE["ruts"]
assert validated_palette(None)==DEFAULT_PALETTE
for line in _visible_segments(((10,100),(600,100)),(100,50,200,150)):
    a,b=line
    assert a[0]<=100 and b[0]>=300
assert list(_visible_segments(((900,900),(950,900)),(100,50,200,150)))==[]
assert clip_segment((0,0),(300,0),(100,-30,100,80))==((100.0,0.0),(200.0,0.0))
before=(repr(ROADS),repr(SECONDARY_ROADS),repr(TRAILS),repr(RAILS))
fake=FakeCanvas()
# Camera in real Great Territory; render at least one full authored route
a,b=ROADS[0][:2]
x=(a[0]+b[0])/2;y=(a[1]+b[1])/2
draw_forsaken_routes(fake,x-350,y-220,700,440,pal)
assert fake.lines,"No visible actual source routes drawn"
assert all("gfx06_route" in opt["tags"] for _,opt in fake.lines)
assert any(opt["width"]==126 for _,opt in fake.lines),"Primary road missing"
assert any(opt.get("dash")== (13,16) for _,opt in fake.lines),"Wagon ruts missing"
assert before==(repr(ROADS),repr(SECONDARY_ROADS),repr(TRAILS),repr(RAILS))

with tempfile.TemporaryDirectory() as d:
    tmp=Path(d)
    archive=tmp/"art.zip"
    sheet=Image.new("RGB",(1448,1086),(255,0,255))
    painter=ImageDraw.Draw(sheet)
    for i,(_,x,y) in enumerate(ROAD_SAMPLES):
        painter.rectangle((x-17,y-17,x+17,y+17),
                          fill=(112+i*4,88+i*3,60+i*2))
    stream=io.BytesIO();sheet.save(stream,format="PNG")
    raw=stream.getvalue()
    entries=[]
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
        for name in EXPECTED_GROUPS:
            path="boards/"+name+".png"
            z.writestr(path,raw)
            entries.append({"id":name,"relative_path":path,
                            "dimensions":[1448,1086],
                            "sha256":hashlib.sha256(raw).hexdigest()})
        z.writestr("manifest.json",json.dumps({
            "asset_count":17,"pack_version":"source-v1","files":entries}))
    output=tmp/"route_palette.json"
    palette=build_palette(archive,output)
    assert len(palette)==len(DEFAULT_PALETTE)
    manifest=json.loads(output.read_text())
    assert manifest["route_positions_modified"] is False
    assert manifest["connected_autotiles_claimed"] is False
    assert all(v.startswith("#") and len(v)==7 for v in palette.values())
    assert manifest["source_samples"]["road_junction"].startswith("#")
    # No changes to collision rules or routable coordinate definitions.
    assert before==(repr(ROADS),repr(SECONDARY_ROADS),repr(TRAILS),repr(RAILS))

print("PASS: A02 source verification, 9 extracted materials, clipped connected roads, ruts and preserved route topology")
