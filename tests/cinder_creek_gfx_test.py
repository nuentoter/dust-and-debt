#!/usr/bin/env python3
"""GFX-02 art select, coordinate safety, and optional runtime load tests."""
import os
from pathlib import Path
import sys
import tempfile
import tkinter as tk

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cinder_creek_gfx import (ZONE_BOUNDS, STARTER_BUILDINGS, inside_art,
                             select_world_image,validate_starter_geometry)
from game import BUILDINGS,Game

assert ZONE_BOUNDS==(0,0,2400,1600)
assert inside_art(0,0) and inside_art(2399,1599)
assert not inside_art(2400,0) and not inside_art(-1,100)
assert validate_starter_geometry(BUILDINGS)
assert not validate_starter_geometry([("Sheriff",321,300,196,130)])

with tempfile.TemporaryDirectory() as folder:
    base=Path(folder)/"world.png"
    base.write_bytes(b"legacy")
    assert select_world_image(folder,True)==str(base)
    art=Path(folder)/"gfx02"/"cinder_creek"/"world_gfx02.png"
    art.parent.mkdir(parents=True)
    art.write_bytes(b"gfx02")
    assert select_world_image(folder,True)==str(art)
    assert select_world_image(folder,False)==str(base)

# Optional generated asset must match the legacy world dimensions.
asset=ROOT/"assets"/"gfx02"/"cinder_creek"/"world_gfx02.png"
if asset.is_file():
    root=tk.Tk();root.withdraw()
    try:
        photo=tk.PhotoImage(file=str(asset))
        assert (photo.width(),photo.height())==ZONE_BOUNDS[2:]
    finally:root.destroy()

os.environ["DUST_AND_DEBT_SILENT"]="1"
root=tk.Tk();root.withdraw()
game=None
try:
    game=Game(root)
    game.screen="playing"
    game.render()
    assert len(game.canvas.find_all())>0
finally:
    if game:game.audio.stop()
    root.destroy()
print("GFX-02 Cinder Creek art integration OK")
