#!/usr/bin/env python3
"""GFX-03: cut approved Gothic buildings from D01 and stamp in starter town.

Offline Pillow processing only. Artwork stays separate from collision/doors.
No square drop shadows, source-board borders, label headers or baked lighting.
The previous building illustration is removed in its *original* rect first;
road texture outside the rect is not removed. This is a visual pilot.
"""
import json
from pathlib import Path
from PIL import Image, ImageFilter
from cinder_creek_gfx import STARTER_BUILDINGS
from tools.forsaken_pack import PACK, validate_pack

# Carefully measured crop boxes on the 1448x1086 approved board. The labels
# and presentation borders live OUTSIDE the crop. Do not scale full panels.
CROPS = {
    "Sheriff": ("sheriff",(90,209,318,403)),
    "Saloon": ("saloon",(422,205,650,403)),
    "General Store": ("general_store",(756,209,992,396)),
    "Hotel": ("hotel",(1107,202,1345,404)),
    "Stable": ("stable",(90,461,323,666)),
    "Doctor": ("doctor",(493,466,636,669)),
    "Cabin": ("cabin",(830,466,990,670)),
    "Station": ("station",(1076,468,1344,672)),
    "Ranch": ("ranch",(72,736,322,929)),
    "Outpost": ("cabin",(830,466,990,670)),
}


def silhouette(crop):
    """Cut an actual building silhouette from the dark review background.

    A flood fill travels through near-neutral, near-black pixels connected to
    the *outside* of the crop. Dark windows enclosed within the illustration
    are preserved. Selecting the largest foreground island removes the thin
    leftover review-frame lines that were visible below the extracted sprites.
    Never fill an entire scanline: it would reintroduce rectangular mattes.
    """
    from collections import deque
    rgb=crop.convert("RGB")
    w,h=rgb.size
    pixels=rgb.load()
    background=bytearray(w*h)
    pending=deque()

    def dark_matte(c):
        r,g,b=c
        return max(c)<39 and abs(r-g)<9 and abs(g-b)<10 and abs(r-b)<10

    def flood_seed(x,y):
        pos=y*w+x
        if not background[pos] and dark_matte(pixels[x,y]):
            background[pos]=1
            pending.append(pos)

    for x in range(w):
        flood_seed(x,0)
        flood_seed(x,h-1)
    for y in range(h):
        flood_seed(0,y)
        flood_seed(w-1,y)
    while pending:
        pos=pending.popleft()
        x,y=pos%w,pos//w
        for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=xx<w and 0<=yy<h:
                flood_seed(xx,yy)

    # Pick the dominant structure, excluding detached presentation-board lines.
    seen=bytearray(w*h)
    largest=[]
    for y in range(h):
        for x in range(w):
            pos=y*w+x
            if background[pos] or seen[pos]:
                continue
            seen[pos]=1
            component=[pos]
            for current in component:
                cx,cy=current%w,current//w
                for xx,yy in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)):
                    if 0<=xx<w and 0<=yy<h:
                        ni=yy*w+xx
                        if not background[ni] and not seen[ni]:
                            seen[ni]=1
                            component.append(ni)
            if len(component)>len(largest):
                largest=component
    if len(largest)<500:
        raise ValueError("Building art has no isolated non-matte component")
    alpha=Image.new("L",(w,h),0)
    a=alpha.load()
    for pos in largest:
        a[pos%w,pos//w]=255
    bounds=alpha.getbbox()
    result=crop.convert("RGBA")
    result.putalpha(alpha)
    return result.crop(bounds)



def extract_building_sprites(pack=PACK):
    pack=Path(pack)
    errors=validate_pack(pack)
    if errors:raise ValueError("Invalid D01 source: "+"; ".join(errors))
    with Image.open(pack/"source_boards"/"GFX-D01.png") as sheet:
        if sheet.size!=(1448,1086):
            raise ValueError("D01 board size changed: crop metadata invalid")
        board=sheet.convert("RGB")
    dest=pack/"prepared"/"D01"
    dest.mkdir(parents=True,exist_ok=True)
    records=[]
    cache={}
    for name,(stem,rect) in CROPS.items():
        if stem not in cache:
            art=silhouette(board.crop(rect))
            if art.getchannel("A").getextrema()!=(0,255):
                # If crop boundary exactly follows silhouette it may be
                # 255 at edges; that's fine if image contains transparent
                # corners, otherwise reject a boxed matte.
                if art.getchannel("A").getextrema()[0]==255:
                    raise ValueError("D01 matte not removed for "+stem)
            art.save(dest/(stem+".png"))
            cache[stem]=art
        records.append({"building":name,"sprite":stem+".png",
                        "dimensions":list(cache[stem].size),
                        "anchor":"south_center","production":"pilot_art",
                        "lighting":"unlit","collision_changed":False})
    (dest/"building_manifest.json").write_text(json.dumps({
        "source_sheet":"GFX-D01","buildings":records,"gameplay_geometry_changed":False,
        "status":"visual_pilot_requires_playtest"},indent=2)+"\n")
    return dest


def _erase_old_art(image,rect,ground,protected_mask=None):
    """Inpaint the old structure from neighbouring soil, not a 64px tile box.

    The prior implementation tiled an ash-gray texture across the entire
    gameplay rectangle and up to 12px outside it. This produced the huge
    square/rectangular mats in screenshots. Here we sample neighbouring
    ground along four exterior sides, interpolate *inside* the old footprint,
    and never touch any exterior pixels (or authored roads).
    """
    x,y,w,h=rect
    original=image.copy().load()
    out=image.load()
    width,height=image.size
    protection=protected_mask.load() if protected_mask is not None else None

    def soil_color(px,py):
        px=min(width-1,max(0,px))
        py=min(height-1,max(0,py))
        # Route mask includes a 55px exclusion HALO around every building.
        # Sampling inside that halo would reject *all* neighbouring soil and
        # force one constant fallback colour, recreating a square lot.
        # Use actual original earth pixels outside the footprint instead.
        r,g,b=original[px,py]
        if 115<r<243 and 75<g<215 and 52<b<190 and r>=g+8 and g>=b-5:
            return (r,g,b)
        return None

    # Weighted median of actual ground around the historical sprite. This
    # fallback avoids copying road/roof/water pixels into the reconstruction.
    perimeter=[]
    for dy in range(0,h+1,5):
        for xx in (x-18,x+w+18):
            sample=soil_color(xx,y+dy)
            if sample:perimeter.append(sample)
    for dx in range(0,w+1,5):
        for yy in (y-18,y+h+18):
            sample=soil_color(x+dx,yy)
            if sample:perimeter.append(sample)
    if perimeter:
        fallback=tuple(sorted(sample[c] for sample in perimeter)[len(perimeter)//2]
                       for c in range(3))
    else:
        fallback=(186,147,108)

    def color_or_fallback(px,py):
        return soil_color(px,py) or fallback

    # Rebuild old roof pixels with the local terrain's colors rather than
    # pasting a repeated grayscale tile or a rectangular shadow.
    for yy in range(max(0,y),min(height,y+h)):
        t=(yy-y+1)/(h+1)
        for xx in range(max(0,x),min(width,x+w)):
            u=(xx-x+1)/(w+1)
            left=color_or_fallback(x-18,yy)
            right=color_or_fallback(x+w+18,yy)
            top=color_or_fallback(xx,y-18)
            bottom=color_or_fallback(xx,y+h+18)
            horizontal=tuple(left[c]*(1-u)+right[c]*u for c in range(3))
            vertical=tuple(top[c]*(1-t)+bottom[c]*t for c in range(3))
            # Subtle deterministic grain, no material hue change.
            grain=((xx*31+yy*17)%7)-3
            out[xx,yy]=tuple(max(0,min(255,round(
                (horizontal[c]+vertical[c])*0.5+grain))) for c in range(3))



def paint_forsaken_buildings(image,pack=PACK,buildings=STARTER_BUILDINGS,protected_mask=None):
    """Replace old Cinder Creek structures without changing gameplay rects."""
    pack=Path(pack)
    directory=extract_building_sprites(pack)
    from PIL import Image as PILImage
    ground=PILImage.open(pack/"prepared"/"A01"/"bleached_dirt.png").convert("RGB")
    if ground.size!=(64,64):
        raise ValueError("Prepare A01 64px seamless ground before buildings")
    painted=[]
    for name,x,y,w,h in buildings:
        if name not in CROPS:continue
        filename=CROPS[name][0]+".png"
        with PILImage.open(directory/filename) as raw:
            sprite=raw.convert("RGBA")
        # Preserve perspective and aspect ratio; south-centre visual anchor.
        max_w,max_h=w-4,h+12
        factor=min(max_w/sprite.width,max_h/sprite.height)
        sw,sh=max(1,round(sprite.width*factor)),max(1,round(sprite.height*factor))
        sprite=sprite.resize((sw,sh),PILImage.Resampling.NEAREST)
        left=x+(w-sw)//2
        top=y+h-sh
        _erase_old_art(image,(x,y,w,h),ground,protected_mask)
        image.paste(sprite,(left,top),sprite)
        painted.append({"name":name,"world_anchor":[x+w//2,y+h],
                        "sprite_bounds":[left,top,sw,sh]})
    return painted
