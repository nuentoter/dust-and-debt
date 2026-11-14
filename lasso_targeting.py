"""Mouse-targeted lasso geometry for Dust & Debt.

The rope never reaches past the pointer. A cursor directly over an outlaw
has priority over a merely intersecting target, provided the target is in
range and unobstructed. No Tk or game dependencies.
"""
import math

LASSO_RANGE=300.0
LASSO_RADIUS=27.0
CURSOR_TOLERANCE=32.0


def throw_segment(player, pointer, facing=(1.0, 0.0), max_range=LASSO_RANGE):
    """Return (start, tip, unit_direction, length, pointer_distance).

    The tip is exactly at the world-space cursor when in range; otherwise it
    stops at maximum rope length. The origin is the player (not an extension
    beyond the cursor). The center-point distance governs valid capture range.
    """
    px,py=player
    mx,my=pointer
    dx,dy=mx-px,my-py
    pointer_distance=math.hypot(dx,dy)
    if pointer_distance<1e-5:
        dx,dy=facing
        magnitude=math.hypot(dx,dy)
        if magnitude<1e-5:dx,dy,magnitude=1.0,0.0,1.0
        ux,uy=dx/magnitude,dy/magnitude
        length=0.0
    else:
        ux,uy=dx/pointer_distance,dy/pointer_distance
        length=min(pointer_distance,max_range)
    return ((px,py),(px+ux*length,py+uy*length),
            (ux,uy),length,pointer_distance)


def choose_target(origin, tip, direction, length, pointer, candidates,
                  visible, radius=LASSO_RADIUS, cursor_tolerance=CURSOR_TOLERANCE):
    """Choose a live candidate under the cursor, then nearest along the rope.

    A valid target must lie within the paid-out rope (with slight center/
    sprite tolerance) and in the rope's narrow path; unobstructed candidates
    only. This deliberately refuses out-of-range or behind-the-player actors.
    """
    ox,oy=origin
    mx,my=pointer
    ux,uy=direction
    pointed=[]
    along=[]
    for target in candidates:
        dx,dy=target.x-ox,target.y-oy
        projection=dx*ux+dy*uy
        lateral=abs(dx*uy-dy*ux)
        distance=math.hypot(dx,dy)
        if distance>LASSO_RANGE or projection<0 or projection>length+radius:
            continue
        if lateral>radius or not visible(ox,oy,target.x,target.y):
            continue
        cursor_distance=math.hypot(target.x-mx,target.y-my)
        if cursor_distance<=cursor_tolerance:
            pointed.append((cursor_distance,distance,target))
        if projection<=length+radius:
            along.append((projection,lateral,target))
    if pointed:
        return min(pointed,key=lambda entry:(entry[0],entry[1]))[2]
    if along:
        return min(along,key=lambda entry:(entry[0],entry[1]))[2]
    return None
