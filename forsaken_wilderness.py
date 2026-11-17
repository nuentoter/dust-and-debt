"""GFX-08: cached Tk PhotoImages for opt-in wilderness decoration.

Only independently extracted RGBA PNGs are loaded; no source board photos,
no additional runtime libraries, and no new collision rules for this pass.
"""
import json
from pathlib import Path
import tkinter as tk

NAMES=("bush","fern","stump","rock")
EXPECTED_CLASSES={"bush":"shrub","fern":"grass","stump":"stump","rock":"boulder"}

def load_wilderness(root):
    directory=Path(root)/"forsaken_v1"/"gfx08"
    try:
        manifest=json.loads((directory/"manifest.json").read_text())
        if (manifest.get("schema_version")!=1
            or manifest.get("source")!="GFX-B01 approved magenta source board"
            or manifest.get("source_verified") is not True
            or manifest.get("mattes_keyed_to_alpha") is not True
            or manifest.get("geometry_modified") is not False):
            return {}
        items=manifest["items"]
        images={}
        for name in NAMES:
            info=items[name]
            if (info.get("collision_class")!=EXPECTED_CLASSES[name]
                or info.get("physical_collision_activated") is not False):
                return {}
            img=tk.PhotoImage(file=str(directory/(name+".png")))
            if ((img.width(),img.height())!=tuple(info["pixels"])
                or img.width()>100 or img.height()>100):
                return {}
            if not img.transparency_get(0,0):
                return {}
            images[name]=img
        return images
    except (OSError,ValueError,KeyError,TypeError,tk.TclError):
        return {}

def draw_wilderness(canvas,images,sx,sy,hash_value):
    """Bottom-center at the existing deterministic prop location."""
    name=NAMES[hash_value%len(NAMES)]
    image=images.get(name)
    if image is None:return False
    canvas.create_image(round(sx),round(sy+7),image=image,anchor="s",
                        tags=("gfx08_wilderness",))
    return True
