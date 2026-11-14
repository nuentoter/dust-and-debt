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
    """Convert a D01 board crop to a silhouette, retaining dark doors/walls.

    Board artwork contains black between roof and storefront and thin gold
    review-frame lines. A background flood fill alone leaks through those
    windows, deleting lower halves of buildings. Instead:
      1. trim thin detached review-border scanlines,
      2. identify the dominant building component with a forgiving matte,
      3. fill enclosed rows between the structure's left and right outline,
         never expanding outside the row's actual building silhouette.
    """
    from collections import deque
    image=crop.convert("RGB")
    w,h=image.size
    rgb=image.load()

    def foreground(x,y):
        r,g,b=rgb[x,y]
        # Neutral near-black belongs to the board background. Warm dark wood
        # and roofs (even low-saturation stone) should remain.
        return max(r,g,b)>35 and (r+g+b)>85

    active=bytearray(w*h)
    visited=bytearray(w*h)
    for y in range(h):
        for x in range(w):
            if foreground(x,y):active[y*w+x]=1
    # A separated gold outline along the upper panel edge is only 1-3 px.
    # Remove narrow rows near the crop's uppermost edge before components.
    for y in range(min(12,h)):
        count=sum(active[y*w:(y+1)*w])
        if count>int(w*0.65) and (
                y==0 or sum(active[(y-1)*w:y*w])<int(w*0.2)):
            active[y*w:(y+1)*w]=bytes(w)
    largest=[]
    for y in range(h):
        for x in range(w):
            origin=y*w+x
            if visited[origin] or not active[origin]:continue
            visited[origin]=1
            queue=deque([origin])
            group=[]
            while queue:
                current=queue.popleft()
                group.append(current)
                xx,yy=current%w,current//w
                for nx,ny in ((xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)):
                    if 0<=nx<w and 0<=ny<h:
                        neighbour=ny*w+nx
                        if not visited[neighbour] and active[neighbour]:
                            visited[neighbour]=1
                            queue.append(neighbour)
            if len(group)>len(largest):largest=group
    if len(largest)<500:raise ValueError("D01 crop missing building silhouette")
    keep=bytearray(w*h)
    for pos in largest:keep[pos]=1
    # Recover the dark windows and lower façade even when disconnected from
    # roof by a near-black porch. Only bridge horizontal gaps within rows
    # supported by the building's actual roof/body envelope.
    alpha=Image.new("L",(w,h),0)
    output=alpha.load()
    rows=[[] for _ in range(h)]
    for pos in largest:
        rows[pos//w].append(pos%w)
    supported=[y for y,row in enumerate(rows) if len(row)>=10]
    if not supported:raise ValueError("D01 crop contains only detached markings")
    first,last=min(supported),max(supported)
    for y in range(first,last+1):
        xs=rows[y]
        if not xs:
            # A one-row dark gap is inside the facade, not empty sky.
            nearest_above=next((rows[i] for i in range(y-1,first-1,-1)
                                if rows[i]),[])
            nearest_below=next((rows[i] for i in range(y+1,last+1)
                                if rows[i]),[])
            if not nearest_above or not nearest_below:continue
            lo=max(min(nearest_above),min(nearest_below))
            hi=min(max(nearest_above),max(nearest_below))
        else:
            lo,hi=min(xs),max(xs)
        for x in range(lo,hi+1):output[x,y]=255
    bounds=alpha.getbbox()
    sprite=crop.convert("RGBA")
    sprite.putalpha(alpha)
    return sprite.crop(bounds)



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
    """Erase the legacy building and its shadow with a feathered local repair.

    A rectangular repeated-tile fill caused the previous screenshots'
    conspicuous patches. This reconstruction uses the natural ground around
    the old roof, interpolates that ground across the building, and blends the
    repair outward over 28px. Authored roads outside the original footprint
    are untouched where the route protection mask is black.
    """
    x,y,w,h=rect
    outer=28
    left=max(0,x-outer)
    top=max(0,y-outer)
    right=min(image.width,x+w+outer)
    bottom=min(image.height,y+h+outer)
    original=image.copy().load()
    dest=image.load()
    protected=protected_mask.load() if protected_mask is not None else None

    def earth(px,py):
        px=min(image.width-1,max(0,px))
        py=min(image.height-1,max(0,py))
        r,g,b=original[px,py]
        if 118<=r<=239 and 78<=g<=214 and 50<=b<=189 and r>=g+7 and g>=b-6:
            return (r,g,b)
        return None

    # Each repair column uses local colours ABOVE and BELOW the source roof,
    # and every row also samples ground to the left and right.
    perimeter=[]
    for xx in range(left,right,7):
        for yy in (max(0,y-outer-9),min(image.height-1,y+h+outer+9)):
            sample=earth(xx,yy)
            if sample is not None:perimeter.append(sample)
    for yy in range(top,bottom,7):
        for xx in (max(0,x-outer-9),min(image.width-1,x+w+outer+9)):
            sample=earth(xx,yy)
            if sample is not None:perimeter.append(sample)
    if perimeter:
        fallback=tuple(sorted(sample[c] for sample in perimeter)[len(perimeter)//2]
                       for c in range(3))
    else:
        fallback=(189,151,109)

    def sample(px,py):
        return earth(px,py) or fallback

    for py in range(top,bottom):
        vy=(py-top+1)/max(1,bottom-top+1)
        for px in range(left,right):
            inside=x<=px<x+w and y<=py<y+h
            if not inside and protected is not None and protected[px,py]==0:
                continue
            if inside:
                alpha=1.0
            else:
                dx=max(x-px,px-(x+w-1),0)
                dy=max(y-py,py-(y+h-1),0)
                d=max(dx,dy)
                if d>=outer:continue
                t=1.0-d/outer
                alpha=t*t*(3-2*t)
            # Sample 38px beyond the artifact itself, not from its old shadow.
            lx=sample(x-outer-20,py)
            rx=sample(x+w+outer+20,py)
            ty=sample(px,y-outer-20)
            by=sample(px,y+h+outer+20)
            u=(px-left+1)/max(1,right-left+1)
            candidate=tuple(round(
                0.5*(lx[c]*(1-u)+rx[c]*u)+
                0.5*(ty[c]*(1-vy)+by[c]*vy))
                for c in range(3))
            # Keep existing natural microtexture rather than painting a flat
            # monotone rectangle, without retaining old roof/outline pixels.
            grain=((px*37+py*23)%9)-4
            candidate=tuple(max(0,min(255,v+grain)) for v in candidate)
            old=original[px,py]
            dest[px,py]=tuple(round(old[c]*(1-alpha)+candidate[c]*alpha)
                              for c in range(3))



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
