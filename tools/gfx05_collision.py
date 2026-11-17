#!/usr/bin/env python3
"""GFX-05: object alpha/collision policy, independent of gameplay geometry.

The magenta editor matte means *transparent*, not "every opaque pixel
blocks the player". Walls/trees use an authored physical foot-zone; grasses,
effects, water, overlays and UI are non-blocking. The existing world solid()
remains authoritative until explicit object positions are authored/approved.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class CollisionRule:
    physical:bool
    foot_start:float=0.65
    foot_end:float=1.0
    alpha_threshold:int=128

COLLISION_RULES={
    "tree":CollisionRule(True,.72,1.0),
    "dead_tree":CollisionRule(True,.70,1.0),
    "cactus":CollisionRule(True,.65,1.0),
    "boulder":CollisionRule(True,.40,1.0),
    "building":CollisionRule(True,.30,1.0),
    "barrier":CollisionRule(True,0.0,1.0),
    "grass":CollisionRule(False),
    "shrub":CollisionRule(False),
    "canopy":CollisionRule(False),
    "flower":CollisionRule(False),
    "trail_overlay":CollisionRule(False),
    "water_surface":CollisionRule(False),
    "ui_icon":CollisionRule(False),
}

def collision_rows(image,kind):
    """Return actual per-row opaque x intervals inside the physical foot band.

    This produces a conservative pixel collision *candidate*, not new world
    coordinates. Only an authored placement may activate it in game.
    """
    if kind not in COLLISION_RULES:
        raise ValueError("Unknown sprite collision class "+str(kind))
    rule=COLLISION_RULES[kind]
    if image.mode!="RGBA":
        raise ValueError("Collision images must be RGBA, not magenta RGB")
    if not rule.physical:
        return ()
    alpha=image.getchannel("A")
    w,h=image.size
    pixels=alpha.load()
    rows=[]
    lo=max(0,min(h-1,int(h*rule.foot_start)))
    hi=max(lo+1,min(h,int(h*rule.foot_end)))
    for y in range(lo,hi):
        run=None
        for x in range(w+1):
            solid=x<w and pixels[x,y]>=rule.alpha_threshold
            if solid and run is None:run=x
            if not solid and run is not None:
                rows.append((y,run,x))
                run=None
    return tuple(rows)

def collide_at(mask_rows,px,py):
    return any(y==py and left<=px<right
               for y,left,right in mask_rows)
