"""Bake cut-out building sprites from the user-provided Western style sheet.

The sprites are PNGs with transparent backgrounds, stored at
assets/gfx02/cinder_creek/sprites/. They are optional; the historical
procedural art is retained as a no-sprites fallback.

This module is offline Pillow tooling, not imported by the game runtime.
"""
from pathlib import Path
import random
from PIL import Image, ImageDraw
from cinder_creek_gfx import STARTER_BUILDINGS
from tools.cinder_creek_buildings import _font

SPRITE_BY_BUILDING = {
    "Sheriff": "sheriff",
    "Saloon": "saloon",
    "General Store": "store",
    "Doctor": "church",
    "Stable": "stable",
    "Hotel": "inn",
    "Station": "smithy",
    "Cabin": "house",
    "Outpost": "house",
    "Ranch": "stable",
}
REQUIRED_SPRITES = tuple(sorted(set(SPRITE_BY_BUILDING.values())))
DEFAULT_SPRITES = Path(__file__).resolve().parents[1] / "assets" / "gfx02" / "cinder_creek" / "sprites"


def sprites_available(sprite_dir=DEFAULT_SPRITES):
    root=Path(sprite_dir)
    return all((root / (name+".png")).is_file() for name in REQUIRED_SPRITES)


def _ground_patch(image, box, seed):
    """Cover the old rectangle before introducing the new alpha-edged sprite.

    All edits stay inside the prior building's collision rectangle.
    Nearby terrain provides the colour, with slight dirt stippling so the
    former rectangular roof does not peek through transparent sprite edges.
    """
    x,y,w,h=box
    sample_x=min(image.width-1, max(0, x-12))
    sample_y=min(image.height-1, max(0, y+h+12))
    r,g,b=image.getpixel((sample_x,sample_y))[:3]
    # Avoid patching old roof with another roof-coloured sample.
    if max(r,g,b)<95 or r<g:
        r,g,b=(194,155,108)
    rng=random.Random(seed)
    d=ImageDraw.Draw(image)
    d.rectangle((x,y,x+w-1,y+h-1), fill=(r,g,b))
    for _ in range((w*h)//42):
        px=rng.randrange(x,x+w); py=rng.randrange(y,y+h)
        delta=rng.choice((-17,-9,7,13))
        col=tuple(max(0,min(255,c+delta)) for c in (r,g,b))
        d.line((px,py,min(x+w-1,px+rng.randrange(1,5)),py),fill=col,width=1)


def _station_sign(image, x,y,w,h):
    # The original sheet has a smithy sprite, not a depot. Mark its adapted
    # function explicitly without inventing a train-station sprite.
    d=ImageDraw.Draw(image)
    label="STATION"
    font=_font(12)
    bb=d.textbbox((0,0),label,font=font)
    tw=bb[2]-bb[0]
    top=y+int(h*.68)
    cx=x+w//2
    d.rectangle((cx-tw//2-8,top-4,cx+tw//2+8,top+17),
                fill="#553b2d",outline="#c8a16d",width=2)
    d.text((cx-tw//2,top-2),label,font=font,fill="#f1d5a2")


def paint_sheet_buildings(image, sprite_dir=DEFAULT_SPRITES,
                          buildings=STARTER_BUILDINGS):
    """Replace original building visuals with real sheet sprites.

    Returns a list of updated building names. If the pack is incomplete,
    return an empty list and leave the image untouched.
    """
    root=Path(sprite_dir)
    if not sprites_available(root):
        return []
    if image.mode!="RGB":
        raise ValueError("Expected RGB baked map")
    sprites={}
    for stem in REQUIRED_SPRITES:
        with Image.open(root/(stem+".png")) as file:
            sprites[stem]=file.convert("RGBA")
    updated=[]
    for index,(name,x,y,w,h) in enumerate(buildings):
        if name not in SPRITE_BY_BUILDING:
            raise ValueError("Unknown building: "+name)
        if x<0 or y<0 or x+w>image.width or y+h>image.height:
            raise ValueError("Building outside map: "+name)
        art=sprites[SPRITE_BY_BUILDING[name]]
        if art.getbbox() is None:
            raise ValueError("Blank reference sprite for "+name)
        # Anchor the porch/front entrance near the historical southern edge.
        # Use essentially the whole collision footprint, but preserve a
        # small internal margin so the new art never misrepresents collision.
        target_w=max(1,w-10); target_h=max(1,h-10)
        scaled=art.resize((target_w,target_h),Image.Resampling.NEAREST)
        left=x+(w-target_w)//2
        top=y+4
        _ground_patch(image,(x,y,w,h),1889+index*53)
        image.paste(scaled,(left,top),scaled)
        if name=="Station":
            _station_sign(image,x,y,w,h)
        updated.append(name)
    return updated
