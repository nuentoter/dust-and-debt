#!/usr/bin/env python3
"""GFX-03: asset pack integrity, preview and opt-in world fallback smoke tests."""
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PIL import Image
from tools.forsaken_pack import EXPECTED, validate_pack, preview, extract_terrain_candidates
from cinder_creek_gfx import select_world_image, ZONE_BOUNDS

with tempfile.TemporaryDirectory() as temp:
    base=Path(temp)
    pack=base/"assets"/"forsaken_v1"
    source=pack/"source_boards"
    source.mkdir(parents=True)
    Image.new("RGB",(4800,3200),"#b7a181").save(base/"assets"/"world.png")
    # Genuine PNG contents so Pillow previews test the same path as production.
    records=[]
    for index,ident in enumerate(EXPECTED):
        image=Image.new("RGB",(1448,1086),(70+index*9,60,50))
        filename=ident+".png"
        path=source/filename
        image.save(path)
        records.append({"id":ident,"name":ident,"file":"source_boards/"+filename,
                        "size":[1448,1086],
                        "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                        "production_status":"reference_board_not_sprite_atlas"})
    manifest={"schema_version":1,"base_tile_px":16,"baked_lighting":False,
              "render_perspective":"true_top_down",
              "integration_state":"staged_review_only","sheets":records}
    (pack/"manifest.json").write_text(json.dumps(manifest))
    assert validate_pack(pack)==[]
    out=preview(pack)
    assert Image.open(out).size==(1200,930)
    candidates=extract_terrain_candidates(pack)
    atlas=Image.open(candidates/"candidate_atlas.png")
    assert atlas.size==(256,192)
    manifest_candidates=json.loads((candidates/"candidate_manifest.json").read_text())
    assert len(manifest_candidates["tiles"])==12
    assert manifest_candidates["world_ready"] is False
    assert all(tile["seamless"] is False for tile in manifest_candidates["tiles"])
    # SHA mismatch must be rejected.
    (source/"GFX-A01.png").write_bytes(b"corrupted")
    assert any("SHA" in issue or "PNG" in issue for issue in validate_pack(pack))
    Image.new("RGB",(1448,1086),"#b7a181").save(source/"GFX-A01.png")
    records[1]["sha256"]=hashlib.sha256((source/"GFX-A01.png").read_bytes()).hexdigest()
    (pack/"manifest.json").write_text(json.dumps(manifest))
    assert not validate_pack(pack)
    # Explicitly enabled runtime art must be a source-independent 4800x3200
    # prepared PNG, never a review sheet. Invalid dims must fall back.
    assets=base/"assets"
    legacy=str(assets/"world.png")
    assert select_world_image(str(assets),forsaken_enabled=True)==legacy
    dest=pack/"runtime"/"world_forsaken.png"
    dest.parent.mkdir(parents=True)
    Image.new("RGB",(800,600)).save(dest)
    assert select_world_image(str(assets),forsaken_enabled=True)==legacy
    Image.new("RGB",ZONE_BOUNDS[2:],"#796856").save(dest)
    assert select_world_image(str(assets),forsaken_enabled=True)==str(dest)
    assert select_world_image(str(assets))==legacy
print("GFX-03 Forsaken pack staging, candidate and fallback tests OK")
