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
    """Largest contiguous non-matte silhouette; no presentation-board lines.

    Retain dark windows and door details as opaque pixels within each row of
    the extracted silhouette. Largest component rejects disconnected labels.
    """
    rgb=crop.convert("RGB")
    width,height=rgb.size
    raw=rgb.load()
    binary=Image.new("L",rgb.size,0)
    pix=binary.load()
    for y in range(height):
        for x in range(width):
            red,green,blue=raw[x,y]
            pix[x,y]=255 if red+green+blue>88 and max(red,green,blue)>36 else 0
    binary=binary.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    pix=binary.load()
    seen=bytearray(width*height)
    largest=[]
    for y in range(height):
        for x in range(width):
            i=y*width+x
            if seen[i] or pix[x,y]<128:continue
            seen[i]=1
            group=[i]
            for k in group:
                cx,cy=k%width,k//width
                for xx,yy in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)):
                    if 0<=xx<width and 0<=yy<height:
                        j=yy*width+xx
                        if not seen[j] and pix[xx,yy]>=128:
                            seen[j]=1
                            group.append(j)
            if len(group)>len(largest):
                largest=group
    if len(largest)<500:
        raise ValueError("No substantial building found in art crop")
    result=Image.new("L",rgb.size,0)
    out=result.load()
    for k in largest:out[k%width,k//width]=255
    # Include enclosed dark windows/doors and roof holes in the silhouette
    # rather than leaving transparent holes showing unrelated ground below.
    for y in range(height):
        xs=[x for x in range(width) if out[x,y]]
        if xs:
            for x in range(xs[0],xs[-1]+1):
                out[x,y]=255
    bbox=result.getbbox()
    sprite=crop.convert("RGBA")
    sprite.putalpha(result)
    return sprite.crop(bbox)


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
    """Replace historical rooftop within its footprint, feather outside it.

    No large opaque squares: a textured sample is feathered over just a
    12-pixel perimeter. Roads more than 12px from the old building cannot
    be changed by this erasure. The painted structure covers the centre.
    """
    x,y,w,h=rect
    spread=12
    left=max(0,x-spread)
    top=max(0,y-spread)
    right=min(image.width,x+w+spread)
    bottom=min(image.height,y+h+spread)
    src=image.load()
    earth=ground.load()
    protect=protected_mask.load() if protected_mask is not None else None
    for py in range(top,bottom):
        for px in range(left,right):
            if protect is not None and protect[px,py]==0 and not (x<=px<x+w and y<=py<y+h):
                continue
            dx=max(x-px,px-(x+w-1),0)
            dy=max(y-py,py-(y+h-1),0)
            distance=max(dx,dy)
            alpha=1 if distance==0 else max(0.0,1.0-distance/spread)
            if alpha<=0:continue
            original=src[px,py]
            texture=earth[px%ground.width,py%ground.height]
            # Use native approved ground texture; no rectangular drop shadow.
            src[px,py]=tuple(round(a*(1-alpha)+b*alpha)
                             for a,b in zip(original,texture))


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
