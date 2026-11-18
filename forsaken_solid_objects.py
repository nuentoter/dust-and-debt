"""GFX-09: cached solid-landform art, retaining original rock collision."""
import json
from pathlib import Path
import tkinter as tk

NAMES=("pine","dead_tree")
EXPECTED={"pine":"tree","dead_tree":"dead_tree"}

def choose_rock_art(solid,biome,index):
    """One-to-one authored ROCKS placements; collision flags unchanged."""
    if solid and biome=="forest":return "pine"
    if solid and biome in ("scrub","canyon","mesa") and index%3==0:
        return "dead_tree"
    return "rock"

def load_solid_art(assets_root):
    directory=Path(assets_root)/"forsaken_v1"/"gfx09"
    try:
        manifest=json.loads((directory/"manifest.json").read_text())
        if (manifest.get("schema_version")!=1
            or manifest.get("source")!="GFX-B01 approved magenta source board"
            or manifest.get("source_verified") is not True
            or manifest.get("geometry_modified") is not False):
            return {}
        sprites={}
        for name in NAMES:
            record=manifest["items"][name]
            if (record["collision_class"]!=EXPECTED[name]
                or record["physical_collision_activated"] is not False
                or record.get("mask_rows",0)<=0):
                return {}
            image=tk.PhotoImage(file=str(directory/(name+".png")))
            if ((image.width(),image.height())!=tuple(record["size"])
                or not image.transparency_get(0,0)):
                return {}
            sprites[name]=image
        # Use the independently extracted GFX08 rock: B01 rock panel
        # motifs overlap and cannot be cropped without broken silhouettes.
        from forsaken_wilderness import load_wilderness
        previous=load_wilderness(assets_root)
        if "rock" in previous:
            sprites["rock"]=previous["rock"]
        return sprites
    except (OSError,ValueError,TypeError,KeyError,tk.TclError):
        return {}

def draw_rock_sprite(canvas,images,x,y,radius,solid,biome,index):
    kind=choose_rock_art(solid,biome,index)
    image=images.get(kind)
    if image is None:return False
    canvas.create_image(round(x),round(y+radius*.5),
                        image=image,anchor="s",
                        tags=("gfx09_solid_landform",))
    return True
