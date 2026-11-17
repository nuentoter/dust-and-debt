#!/usr/bin/env python3
"""Synthetic GFX-05 import, provenance, terrain/road staging and alpha QA."""
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
from tools.gfx05_pipeline import (
    EXPECTED_GROUPS,PILOT_PICK,ROAD_SAMPLES,TILE_IDS,stage,verify_source,
)
from tools.build_forsaken_pilot import seam_error
from tools.gfx05_collision import collide_at,collision_rows
from cinder_creek_gfx import select_world_image

with tempfile.TemporaryDirectory() as folder:
    tmp=Path(folder)
    archive=tmp/"source.zip"
    out=tmp/"staged"
    board=Image.new("RGB",(1448,1086),(54,41,39))
    d=ImageDraw.Draw(board)
    # Synthetic A01 sources have different terrain colors by row, not
    # arbitrary board matte colours.
    from tools.gfx05_pipeline import TERRAIN_X,TERRAIN_ROWS
    for ri,(_,y) in enumerate(TERRAIN_ROWS):
        for j,x in enumerate(TERRAIN_X):
            d.rectangle((x-26,y-26,x+26,y+26),
                        fill=(95+ri*8,75+ri*6,65+j*5))
    data=io.BytesIO()
    board.save(data,format="PNG")
    board_bytes=data.getvalue()
    other=Image.new("RGB",(1536,1024),(31,37,41))
    b=io.BytesIO();other.save(b,format="PNG")
    large_bytes=b.getvalue()
    rows=[]
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
        for name in EXPECTED_GROUPS:
            image_data=large_bytes if name=="GFX-B01" else board_bytes
            size=[1536,1024] if name=="GFX-B01" else [1448,1086]
            path="boards/"+name+".png"
            z.writestr(path,image_data)
            rows.append(dict(id=name,relative_path=path,dimensions=size,
                             sha256=hashlib.sha256(image_data).hexdigest()))
        z.writestr("manifest.json",json.dumps({
            "pack_version":"source-v1","asset_count":17,"files":rows}))
    assert verify_source(archive)["asset_count"]==17
    info=stage(archive,out)
    assert info["runtime_status"]=="staged_no_game_mutation"
    assert not info["a02"]["route_replacement_enabled"]
    assert len(info["a02"]["candidates"])==len(ROAD_SAMPLES)==12
    assert set(info["a01"]["pilot_tiles"])==set(TILE_IDS)==set(PILOT_PICK)
    assert (out/"roads_review.png").is_file()
    for name in TILE_IDS:
        tile=Image.open(out/"candidates"/"A01"/(name+".png"))
        assert tile.mode=="RGB" and tile.size==(64,64)
        assert seam_error(tile)==(0,0)
    # Missing/invalid source cannot be silently used as artwork.
    bad=tmp/"bad.zip"
    with zipfile.ZipFile(archive) as origin, zipfile.ZipFile(bad,"w") as dest:
        for name in origin.namelist():
            raw=origin.read(name)
            if name=="boards/GFX-A02.png":raw=b"bad"
            dest.writestr(name,raw)
    try:verify_source(bad)
    except ValueError:pass
    else:raise AssertionError("Tampered road art was accepted")

    # A sprite can have empty corners and opaque body but only physical
    # lower-foot intervals collide, not the rectangular PNG bbox.
    image=Image.new("RGBA",(16,20),(255,0,255,0))
    pen=ImageDraw.Draw(image)
    pen.rectangle((2,1,13,19),fill=(30,26,22,255))
    mask=collision_rows(image,"tree")
    assert mask and collide_at(mask,5,17)
    assert not collide_at(mask,5,1)
    assert not collide_at(mask,0,17)
    assert collision_rows(image,"grass")==()
    assert collision_rows(image,"canopy")==()
    try:collision_rows(image.convert("RGB"),"tree")
    except ValueError:pass
    else:raise AssertionError("RGB board was accepted as RGBA sprite")
    # A missing opt-in world image must preserve the legacy fallback.
    assert select_world_image(str(tmp),gfx05_enabled=True).endswith("world.png")
    root=tmp/"forsaken_v1"/"gfx05"
    root.mkdir(parents=True)
    Image.new("RGB",(100,100)).save(root/"world_gfx05.png")
    assert select_world_image(str(tmp),gfx05_enabled=True).endswith("world.png")

print("PASS: 17 source groups + SHA/zip checks, 12 seam pilots, 12 road samples, collision classes and fallback")
