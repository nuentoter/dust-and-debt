"""Pure geometry for auditing actual route paths through bridge footprints."""
import math
from frontier_routes import Route


def clip_deck_segment(deck,a,b):
    """Closed finite segment versus the deck's rotated rectangle, in [0,1]."""
    ax=(a[0]-deck.x)*deck.dx+(a[1]-deck.y)*deck.dy
    ay=-(a[0]-deck.x)*deck.dy+(a[1]-deck.y)*deck.dx
    dx=(b[0]-a[0])*deck.dx+(b[1]-a[1])*deck.dy
    dy=-(b[0]-a[0])*deck.dy+(b[1]-a[1])*deck.dx
    lo,hi=0.,1.
    for origin,delta,extent in ((ax,dx,deck.half_length),(ay,dy,deck.half_width)):
        if abs(delta)<1e-10:
            if abs(origin)>extent:return None
        else:
            t0,t1=sorted(((-extent-origin)/delta,(extent-origin)/delta))
            lo=max(lo,t0);hi=min(hi,t1)
            if lo>hi:return None
    return (lo,hi) if hi-lo>1e-9 else None


def route_lengths(route):
    result=[0.]
    for a,b in zip(route.vertices,route.vertices[1:]):result.append(result[-1]+math.dist(a,b))
    return result


def point_at(route,lengths,distance):
    """Position on the original polyline, retaining its segment and local t."""
    distance=max(0.,min(lengths[-1],distance))
    for i,(a,b) in enumerate(zip(route.vertices,route.vertices[1:])):
        size=lengths[i+1]-lengths[i]
        if size>0 and distance<=lengths[i+1]+1e-9:
            t=max(0.,min(1.,(distance-lengths[i])/size))
            return {'segment':i,'t':t,'xy':(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)}
    raise ValueError('Approach route has no nonzero segments')


def deck_intervals(deck,route,lengths):
    """Merge consecutive deck intersections across bends; retain repeat visits."""
    intervals=[]
    for i,(a,b) in enumerate(zip(route.vertices,route.vertices[1:])):
        hit=clip_deck_segment(deck,a,b)
        if hit is None:continue
        size=lengths[i+1]-lengths[i]
        if size<=1e-9:continue
        start,end=(lengths[i]+t*size for t in hit)
        if intervals and start<=intervals[-1][1]+1e-6:
            intervals[-1]=(intervals[-1][0],max(intervals[-1][1],end))
        else:intervals.append((start,end))
    return intervals


def approach_anchor(route,lengths,edge,direction,surface,guard=150.,step=10.):
    """Follow the route at least guard units, then seek land or its terminal.

    A wet route terminal remains a failed anchor; it is never projected onto
    a different route or replaced by an invented straight-line bank position.
    """
    if step<=0 or not math.isfinite(step):raise ValueError('step must be positive and finite')
    if direction not in (-1,1):raise ValueError('direction must be -1 or 1')
    if guard<0 or not math.isfinite(guard):raise ValueError('guard must be nonnegative and finite')
    total=lengths[-1]
    distance=max(0.,min(total,edge+direction*guard))
    while True:
        anchor=point_at(route,lengths,distance)
        anchor.update(distance=distance,surface=surface(*anchor['xy']),route_terminal=distance in (0.,total))
        if anchor['surface'] in ('land','settlement') or distance in (0.,total):return anchor
        distance=max(0.,min(total,distance+direction*step))


def crop_route(route,lengths,start,end):
    """Keep all authored bends between two arclength positions."""
    points=[point_at(route,lengths,start)['xy']]
    points.extend(p for p,s in zip(route.vertices,lengths) if start<s<end)
    points.append(point_at(route,lengths,end)['xy'])
    unique=[points[0]]
    for point in points[1:]:
        if point!=unique[-1]:unique.append(point)
    return Route(route.id,route.kind,tuple(unique),route.source)
