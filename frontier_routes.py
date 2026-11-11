"""Immutable New Austellia transport graph (v2.9-map, phases 0-1).

This is the audited SOURCE graph, not a claim that a drawn stroke is physically
walkable. It does not alter terrain, atlas rendering, or existing NPC movement.
Wagon and rail topology are kept strictly separate.
"""
from dataclasses import dataclass
from collections import defaultdict
import heapq
import math

from new_austellia import ROADS, RAILS, SECONDARY_ROADS, TRAILS, START_SPUR

Point=tuple[float,float]
WAGON="wagon"
RAIL="rail"
TRAIL="trail"

def allowed_kinds(mode):
    if mode=="rail":return frozenset((RAIL,))
    if mode=="wagon":return frozenset((WAGON,))
    if mode in ("foot","horse"):return frozenset((WAGON,TRAIL))
    raise ValueError("Unknown travel mode: "+str(mode))

@dataclass(frozen=True)
class Route:
    id:str
    kind:str
    vertices:tuple
    source:str="atlas"

@dataclass(frozen=True)
class Edge:
    node_a:str
    node_b:str
    route_id:str
    length:float
    kind:str

ROUTE_SOURCES=(
    tuple(Route("wagon_%02d"%i,WAGON,tuple(points)) for i,points in enumerate(ROADS))+
    tuple(Route("rail_%02d"%i,RAIL,tuple(points)) for i,points in enumerate(RAILS))+
    tuple(Route(key,WAGON,tuple(points),"authored") for key,points in SECONDARY_ROADS)+
    tuple(Route(key,TRAIL,tuple(points),"authored") for key,kind,name,points in TRAILS)+
    # The protected starter exit joins the authored Cinder Creek approach.
    (Route("starter_spur",WAGON,START_SPUR,"legacy"),)
)
EPSILON=1e-8

def interpolate(a,b,t):
    return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)

def segment_intersection(a,b,c,d):
    """Return (t,u,world_point) for finite non-collinear intersections."""
    ux,uy=b[0]-a[0],b[1]-a[1]
    vx,vy=d[0]-c[0],d[1]-c[1]
    det=ux*vy-uy*vx
    if abs(det)<EPSILON:return None
    wx,wy=c[0]-a[0],c[1]-a[1]
    t=(wx*vy-wy*vx)/det
    u=(wx*uy-wy*ux)/det
    if -EPSILON<=t<=1+EPSILON and -EPSILON<=u<=1+EPSILON:
        t=max(0.,min(1.,t));u=max(0.,min(1.,u))
        return (t,u,interpolate(a,b,t))
    return None

def projection(point,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1]
    length2=dx*dx+dy*dy
    t=max(0.,min(1.,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/length2)) if length2 else 0.
    x,y=interpolate(a,b,t)
    return (math.hypot(point[0]-x,point[1]-y),t,(x,y))

def node_id(point):
    # Subunit rounding makes exact geometric crossings shared by both routes
    # while preserving natural mismatches rather than inventing connectors.
    return "%.3f,%.3f"%(point[0],point[1])

class RouteGraph:
    def __init__(self,routes=ROUTE_SOURCES):
        self.routes=tuple(routes)
        self.segments=[]
        self.nodes={}
        self.edges=[]
        self.neighbors=defaultdict(list)
        self.route_nodes=defaultdict(set)
        self.segment_nodes=defaultdict(set)
        self._build()

    def _build(self):
        segments=[]
        for route in self.routes:
            for i,(a,b) in enumerate(zip(route.vertices,route.vertices[1:])):
                if a==b:continue
                segments.append((route.id,route.kind,i,a,b))
        self.segments=tuple(segments)
        splits=[{0.,1.} for _ in segments]
        # One-time O(n²) build: approximately 100 atlas line segments;
        # no graph work per frame.
        for i,(rid,kind,idx,a,b) in enumerate(segments):
            for j in range(i+1,len(segments)):
                rid2,kind2,idx2,c,d=segments[j]
                # Only same transport surfaces, or an intentional foot-trail
                # meeting a road, are allowed to share a junction.
                if (kind==RAIL)!=(kind2==RAIL):continue
                # Pre-filter non-overlapping segment bounds.
                if max(a[0],b[0])<min(c[0],d[0]) or max(c[0],d[0])<min(a[0],b[0]):continue
                if max(a[1],b[1])<min(c[1],d[1]) or max(c[1],d[1])<min(a[1],b[1]):continue
                hit=segment_intersection(a,b,c,d)
                if hit:
                    t,u,_=hit
                    splits[i].add(round(t,10));splits[j].add(round(u,10))
                # Collinear overlaps are not forcibly merged. They must be
                # resolved explicitly during route correction audit.
        unique_edges=set()
        for (rid,kind,index,a,b),ts in zip(segments,splits):
            positions=sorted(ts)
            for t1,t2 in zip(positions,positions[1:]):
                if t2-t1<=EPSILON:continue
                pa=interpolate(a,b,t1);pb=interpolate(a,b,t2)
                n1=node_id(pa);n2=node_id(pb)
                if n1==n2:continue
                self.nodes[n1]=pa;self.nodes[n2]=pb
                self.route_nodes[rid].update((n1,n2))
                self.segment_nodes[(rid,index)].update((n1,n2))
                key=(n1,n2,rid)
                if key in unique_edges:continue
                unique_edges.add(key)
                length=math.dist(pa,pb)
                edge=Edge(n1,n2,rid,length,kind)
                self.edges.append(edge)
                self.neighbors[n1].append((n2,length,kind,rid))
                self.neighbors[n2].append((n1,length,kind,rid))

    def components(self,mode=WAGON):
        eligible=allowed_kinds(mode)
        visited=set()
        groups=[]
        for n in sorted(self.nodes):
            if n in visited or not any(e[2] in eligible for e in self.neighbors[n]):continue
            stack=[n];visited.add(n);group=set()
            while stack:
                current=stack.pop();group.add(current)
                for other,_,kind,_ in self.neighbors[current]:
                    if kind in eligible and other not in visited:
                        visited.add(other);stack.append(other)
            groups.append(frozenset(group))
        return tuple(sorted(groups,key=lambda group:(-len(group),min(group))))

    def nearest_anchor(self,point,mode=WAGON,max_distance=None):
        kinds=allowed_kinds(mode)
        best=None
        for rid,kind,idx,a,b in self.segments:
            if kind not in kinds:continue
            dist,t,closest=projection(point,a,b)
            if best is None or dist<best[0]:
                best=(dist,rid,idx,closest)
        if best is None or (max_distance is not None and best[0]>max_distance):return None
        # Anchor on nearest end node for graph query; projected position is
        # retained for later edge-splitting in phase 2.
        distance,rid,idx,projected=best
        nodes=self.segment_nodes[(rid,idx)]
        endpoint=min(nodes,key=lambda key:math.dist(self.nodes[key],projected))
        return {"distance":distance,"route_id":rid,"segment_index":idx,
                "projected":projected,"node":endpoint}

    def path(self,a,b,mode=WAGON):
        allowed=allowed_kinds(mode)
        start=a if isinstance(a,str) and a in self.nodes else self.nearest_anchor(a,mode)
        end=b if isinstance(b,str) and b in self.nodes else self.nearest_anchor(b,mode)
        if isinstance(start,dict):start=start["node"]
        if isinstance(end,dict):end=end["node"]
        if start is None or end is None:return None
        dist={start:0.};prev={};heap=[(0.,start)]
        while heap:
            cost,node=heapq.heappop(heap)
            if cost>dist.get(node,float("inf")):continue
            if node==end:
                result=[node]
                while node in prev:
                    node=prev[node];result.append(node)
                return tuple(self.nodes[n] for n in reversed(result))
            for other,length,kind,_ in self.neighbors[node]:
                if kind not in allowed:continue
                new=cost+length
                if new<dist.get(other,float("inf")):
                    dist[other]=new;prev[other]=node
                    heapq.heappush(heap,(new,other))
        return None

    def route_component_ids(self,mode=WAGON):
        node_to_group={}
        groups=self.components(mode)
        for i,group in enumerate(groups):
            for n in group:node_to_group[n]=i
        eligible=allowed_kinds(mode)
        return {route.id:sorted({node_to_group[n] for n in self.route_nodes[route.id]
                                 if n in node_to_group})
                for route in self.routes if route.kind in eligible}

ROUTE_GRAPH=RouteGraph()

def nearest_route_anchor(x,y,mode="wagon",max_distance=None):
    return ROUTE_GRAPH.nearest_anchor((x,y),mode,max_distance)

def route_path(start,end,mode="wagon"):
    return ROUTE_GRAPH.path(start,end,mode)

def connected_components(mode="wagon"):
    return ROUTE_GRAPH.components(mode)
