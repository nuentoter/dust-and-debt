#!/usr/bin/env python3
"""Optional Pillow-only architectural bake tests; no game runtime dependency."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

try:
    from PIL import Image
except ImportError:
    print("SKIP GFX-02 building-art tests (Pillow is offline build tooling)")
    raise SystemExit(0)

from cinder_creek_gfx import STARTER_BUILDINGS,validate_starter_geometry
from tools.cinder_creek_buildings import SCHEMES,paint_buildings

assert all(name in SCHEMES for name,*_ in STARTER_BUILDINGS)
assert len(STARTER_BUILDINGS)==10
source=Image.new("RGB",(2400,1600),"#c8a06d")
outside=source.getpixel((12,12))
count=paint_buildings(source)
assert count==len(STARTER_BUILDINGS)
assert source.getpixel((12,12))==outside
for name,x,y,w,h in STARTER_BUILDINGS:
    assert source.getpixel((x+w//2,y+h//2))!=outside,name
    # Test lower entrance and the sign area rather than assuming an exact
    # style-specific pixel: both must differ from an unpainted background.
    assert source.getpixel((x+w//2,y+h-28))!=outside,name
assert validate_starter_geometry(STARTER_BUILDINGS)

# A source-sized baked file is created by the preceding CI build step.
manifest=ROOT/"assets/gfx02/cinder_creek/build_manifest.json"
if manifest.is_file():
    data=json.loads(manifest.read_text())
    assert data["size"]==[4800,3200]
    assert data["redrawn_buildings"]==len(STARTER_BUILDINGS)
    assert data["building_names"]==[b[0] for b in STARTER_BUILDINGS]
    baked=Image.open(ROOT/data["output"])
    assert baked.size==(4800,3200)
print("GFX-02 architectural art tests OK")
