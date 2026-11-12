#!/usr/bin/env python3
"""Regression tests for the long-term GFX handoff contract and CLI checks."""
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PIL import Image, ImageDraw
from tools.validate_graphics_assets import (
    RULES,validate_rules,validate_pack,validate_manifest,
)
from tools.cinder_creek_sheet_art import REQUIRED_SPRITES

assert not validate_rules(),validate_rules()

with tempfile.TemporaryDirectory() as folder:
    root=Path(folder)
    rules=json.loads(RULES.read_text())
    bogus=root/"bad_rules.json"
    rules["world"]["starter_dimensions"]=[2400,1600]
    bogus.write_text(json.dumps(rules))
    assert any("dimensions" in item for item in validate_rules(bogus))
    rules["world"]["starter_dimensions"]=[4800,3200]
    rules["pixel_sampling"]="bilinear"
    bogus.write_text(json.dumps(rules))
    assert any("nearest" in item for item in validate_rules(bogus))
    assert validate_pack(root,require=True)
    assert not validate_pack(root)
    for name in REQUIRED_SPRITES:
        art=Image.new("RGBA",(24,32),(0,0,0,0))
        ImageDraw.Draw(art).rectangle((4,3,19,30),fill=(160,90,50,255))
        art.save(root/(name+".png"))
    assert not validate_pack(root,require=True)
    (root/"store.png").unlink()
    assert validate_pack(root)
    damaged_manifest=root/"bad_manifest.json"
    damaged_manifest.write_text(json.dumps({
        "size":[2400,1600],
        "geometry_changes":True,
        "redrawn_buildings":0,
        "art_source":"procedural_fallback",
        "output":"assets/gfx02/missing.png"
    }))
    issues=validate_manifest(damaged_manifest)
    assert len(issues)>=3,issues

print("Graphics standards and quality gate tests OK")
