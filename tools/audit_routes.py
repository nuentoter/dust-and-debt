#!/usr/bin/env python3
"""Print/write deterministic graph and physical clearance audits.

Usage:
  python tools/audit_routes.py
  python tools/audit_routes.py --json docs/road_audit.json
  python tools/audit_routes.py --physical --check

Graph-only --check verifies mainland connections. With --physical it also
requires foot/horse center and edge probes at <=10 units and rejects blocked
wagon/trail samples. Rail clearance is reported separately unless --include-rail is selected.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from frontier_routes import ROUTE_GRAPH, WAGON, RAIL, projection
from new_austellia import BRIDGES, TOWNS, MAJOR_TOWNS, ROADS, RAILS, is_water, BRIDGE_DECKS
from frontier_world import WAYSTATIONS, START_SPUR

def audit():
    graph=ROUTE_GRAPH
    groups=graph.components("wagon")
    group_lookup={}
    for i,group in enumerate(groups):
        for node in group:group_lookup[node]=i
    def site(key,name,x,y,kind):
        anchor=graph.nearest_anchor((x,y),mode="wagon")
        component=group_lookup.get(anchor["node"]) if anchor else None
        return {"id":key,"name":name,"kind":kind,
                "xy":[x,y],"nearest_wagon_route":anchor["route_id"] if anchor else None,
                "distance_to_wagon":round(anchor["distance"],1) if anchor else None,
                "component":component,
                "needs_road_approach":kind in ("city","town","port","settlement") and
                     (not anchor or anchor["distance"]>180)}
    sites=[site(key,name,x,y,kind) for key,name,x,y,kind in TOWNS]
    stations=[site(key,name,x,y,"waystation") for key,name,x,y in WAYSTATIONS]
    wagon_route_groups=graph.route_component_ids("wagon")
    # This summarizes purely *geometrical* components. Physical clearance
    # comes in later route test milestones; it is never inferred from graph.
    road_groups=[]
    for index,group in enumerate(groups):
        ids=sorted(rid for rid,components in wagon_route_groups.items() if index in components)
        road_groups.append({"component":index,"routes":ids,
                            "nodes":len(group),"edges":sum(
                                edge.node_a in group and edge.node_b in group and edge.kind==WAGON
                                for edge in graph.edges)})
    # Don't treat a bridge as evidence of wagon connectivity if it belongs
    # to rail or its centerline can't be crossed by the player.
    bridges=[]
    for i,(record,deck) in enumerate(zip(BRIDGES,BRIDGE_DECKS)):
        x,y,dx,dy,name,kind,width=record
        center=(x,y)
        bank0=(x-deck.dx*(deck.half_length+25),y-deck.dy*(deck.half_length+25))
        bank1=(x+deck.dx*(deck.half_length+25),y+deck.dy*(deck.half_length+25))
        bridges.append({"id":"crossing_%03d"%i,"water":name,"kind":kind,
                        "xy":[round(x,1),round(y,1)],
                        "deck_half_length":deck.half_length,"deck_half_width":deck.half_width,
                        "deck_corners":deck.corners,
                        "center_passable":not is_water(*center),
                        "entry_passable":not is_water(*bank0),
                        "exit_passable":not is_water(*bank1),
                        "physically_validated":False})
    # Critical initial-town network: 12 mainland towns + one original area.
    core=[a for a in sites if a["id"] in MAJOR_TOWNS]
    root_components=sorted(set(a["component"] for a in core if a["component"] is not None))
    disconnected=[a["id"] for a in core if a["component"] is None
                  or a["needs_road_approach"] or a["component"]!=root_components[0]]
    geometry={"routes":[(r.id,r.kind,r.source,r.vertices) for r in graph.routes],
              "bridges":BRIDGES,"deck_frames":[vars(deck) for deck in BRIDGE_DECKS]}
    digest=hashlib.sha256(json.dumps(geometry,sort_keys=True).encode()).hexdigest()
    return {
        "schema":1,"milestone":"v2.9-map","phase":"clearance_validation",
        "world":[60000,40960],
        "source":{"wagon_polylines":len(ROADS),"rail_polylines":len(RAILS),
                  "site_count":len(TOWNS),"waystations":len(WAYSTATIONS),
                  "route_records":len(graph.routes),
                  "trail_polylines":sum(r.kind=="trail" for r in graph.routes),
                  "bridge_records":len(BRIDGES),"geometry_sha256":digest,
                  "starter_spur":[list(p) for p in START_SPUR]},
        "graph":{"wagon_components":len(groups),"rail_components":len(graph.components("rail")),
                 "wagon_routes":road_groups,"mainland_core_components":root_components,
                 "disconnected_or_missing_road_core_ids":disconnected},
        "sites":sites,"waystations":stations,"crossings":bridges,
        "known_exemptions":["calhoun_island","herons_key","drake_isles"],
        "notes":[
            "Includes authored secondary roads and 24 foot/horse destination trails.",
            "A visually drawn connection does not prove passage through terrain/building collision.",
            "The original map's START_SPUR is tracked explicitly alongside its authored approach.",
            "Rail track proximity does not count toward wagon connectivity.",
            "This report makes no claims about existing game runtime frame rate."]
    }

# Match the actual movement envelopes in Game.update: foot=11, horse=16.
ACTOR_RADII=(11,16)


def route_half_width(route):
    """Travel footprint: packed roads, the 33-unit worn trail, and rail bed."""
    if route.kind=="trail":return 16.5
    if route.kind==RAIL:return 12.5
    if route.source=="legacy":return 19.
    return 50. if route.source=="atlas" else 30.

def route_samples(route,step=10,radius=11,edges=True):
    """Yield exact endpoints and evenly spaced center/usable-edge positions.

    Offsets leave room for the actor radius inside the painted surface. These
    are independent lane probes, not proof of a continuous collision-free area.
    """
    if not math.isfinite(step) or step<=0:raise ValueError("step must be positive and finite")
    if not math.isfinite(radius) or radius<=0:raise ValueError("radius must be positive and finite")
    offset=max(0.,route_half_width(route)-radius)
    lanes=(("center",0.),("left",offset),("right",-offset)) if edges and offset else (("center",0.),)
    for index,(a,b) in enumerate(zip(route.vertices,route.vertices[1:])):
        distance=math.dist(a,b)
        if not distance:continue
        nx,ny=-(b[1]-a[1])/distance,(b[0]-a[0])/distance
        count=max(1,math.ceil(distance/step))
        for lane,shift in lanes:
            for i in range(count+1):
                t=i/count
                yield {"segment":index,"t":t,"lane":lane,"offset":shift,
                       "radius":radius,"xy":(a[0]+(b[0]-a[0])*t+nx*shift,
                                                a[1]+(b[1]-a[1])*t+ny*shift)}

def collision_reason(x,y,radius):
    """Classify the same static obstacles as Game.solid, without creating Tk.

    Game.terrain_obstacle currently returns None; parity is regression-tested.
    Water follows current gameplay's point test, not an invented radius buffer.
    """
    from natural_terrain import landform_solid
    from game import BUILDINGS,WW,WH
    if x<23 or y<23 or x>WW-23 or y>WH-23:return "world_bounds"
    if is_water(x,y):return "water"
    if landform_solid(x,y,radius):return "ridge_or_rock"
    if any(bx-radius<x<bx+bw+radius and by-radius<y<by+bh+radius
           for _,bx,by,bw,bh in BUILDINGS):return "building"
    return None

def physical_audit(step=10,edges=True,routes=None,classify=None):
    """Probe foot/horse centerlines and margins, reporting exact failure context.

    Rail collision is reported separately; rails cannot satisfy wagon access.
    Injected route/classifier fixtures support precise sampler regressions.
    """
    classify=classify or collision_reason
    detail={}
    for route in ROUTE_GRAPH.routes if routes is None else routes:
        total=blocked=0
        reasons={"water":0,"ridge_or_rock":0,"building":0,"world_bounds":0}
        examples=[];profiles={};ranges=[]
        for radius in ACTOR_RADII:
            profile={"samples":0,"blocked":0,"lanes":{}}
            profiles[str(radius)]=profile
            active=None
            for sample in route_samples(route,step,radius,edges):
                x,y=sample["xy"]
                total+=1;profile["samples"]+=1
                lane=profile["lanes"].setdefault(sample["lane"],{"samples":0,"blocked":0})
                lane["samples"]+=1
                reason=classify(x,y,radius)
                if reason:
                    blocked+=1;profile["blocked"]+=1;lane["blocked"]+=1
                    reasons[reason]=reasons.get(reason,0)+1
                    failure=dict(sample,xy=[round(x,3),round(y,3)],reason=reason)
                    if len(examples)<8:examples.append(failure)
                    key=(radius,sample["segment"],sample["lane"],reason)
                    if active is None or active[0]!=key:
                        interval={"radius":radius,"segment":sample["segment"],
                                  "lane":sample["lane"],"offset":sample["offset"],
                                  "reason":reason,"start_t":sample["t"],
                                  "end_t":sample["t"],"start_xy":failure["xy"],
                                  "end_xy":failure["xy"],"samples":0}
                        ranges.append(interval);active=(key,interval)
                    active[1]["end_t"]=sample["t"]
                    active[1]["end_xy"]=failure["xy"]
                    active[1]["samples"]+=1
                else:active=None
        detail[route.id]={"kind":route.kind,"sample_step":step,"edges_sampled":edges,
                          "half_width":route_half_width(route),
                          "samples":total,"blocked":blocked,"reasons":reasons,
                          "actor_profiles":profiles,"first_failures":examples,
                          "blocked_ranges":ranges}
    return detail

def bridge_surface(x,y):
    """Distinguish real ground/settlement anchors from a supported wet deck."""
    from new_austellia import near_atlas_town,river_at,lake_at,coastal_water
    if near_atlas_town(x,y,230) is not None:return 'settlement'
    if not (river_at(x,y) or lake_at(x,y) or coastal_water(x,y)):return 'land'
    return 'water' if is_water(x,y) else 'deck'


def bridge_approach_audit(routes=None,decks=None,classify=None,surface=None,step=10):
    """Validate every same-mode path through each deck, following actual bends.

    Raw tangent probes remain diagnostic. A wet tangent within a painted route
    footprint is a failure; an off-route tangent is retained with its distance.
    """
    from tools.bridge_approaches import route_lengths,deck_intervals,approach_anchor,crop_route,point_at
    routes=ROUTE_GRAPH.routes if routes is None else tuple(routes)
    decks=BRIDGE_DECKS if decks is None else tuple(decks)
    surface=surface or bridge_surface
    classify=classify or collision_reason
    lengths={route.id:route_lengths(route) for route in routes}
    results=[]
    for deck in decks:
        paths=[];related=[]
        eligible=RAIL if deck.kind=='rail' else WAGON
        for route in routes:
            if route.kind!=eligible:continue
            distances=lengths[route.id]
            intervals=deck_intervals(deck,route,distances)
            if not intervals:continue
            related.append(route)
            for start,end in intervals:
                entry=approach_anchor(route,distances,start,-1,surface,step=step)
                exit=approach_anchor(route,distances,end,1,surface,step=step)
                cropped=crop_route(route,distances,entry['distance'],exit['distance'])
                probes=physical_audit(step,True,(cropped,),classify)[route.id]
                for failure in probes['first_failures']:
                    index,hit=min(enumerate(zip(route.vertices,route.vertices[1:])),
                                  key=lambda item:projection(failure['xy'],*item[1])[0])
                    _,t,_=projection(failure['xy'],*hit)
                    failure['crop_segment']=failure['segment']
                    failure['segment']=index;failure['t']=t
                supported=all(anchor['surface'] in ('land','settlement') for anchor in (entry,exit))
                paths.append({'route_id':route.id,'kind':route.kind,'entry':entry,'exit':exit,
                              'deck_entry':point_at(route,distances,start),
                              'deck_exit':point_at(route,distances,end),
                              'guard_distance':150,'entry_guard':start-entry['distance'],
                              'exit_guard':exit['distance']-end,'sample_step':step,
                              'samples':probes['samples'],'blocked':probes['blocked'],
                              'actor_profiles':probes['actor_profiles'],
                              'first_failures':probes['first_failures'],
                              'passed':supported and probes['blocked']==0 and step<=10})
        reviews=[]
        for sign,label in ((-1,'entry'),(1,'exit')):
            point=(deck.x+sign*deck.dx*(deck.half_length+25),
                   deck.y+sign*deck.dy*(deck.half_length+25))
            candidates=[(projection(point,a,b)[0],route.id,index,projection(point,a,b)[2],
                         route_half_width(route))
                        for route in related for index,(a,b) in enumerate(zip(route.vertices,route.vertices[1:]))]
            nearest=min(candidates) if candidates else None
            wet=surface(*point) in ('water','deck') and bool(classify(*point,11))
            # The production classifier reports a water failure at a wet raw
            # tangent. Fixtures can exercise a wet point without a real map.
            status='clear'
            if wet:status='off_route_tangent' if nearest and nearest[0]>nearest[4] else 'unsafe_route_tangent'
            reviews.append({'end':label,'xy':point,'status':status,
                            'nearest_route':nearest[1] if nearest else None,
                            'distance_to_route':nearest[0] if nearest else None,
                            'route_half_width':nearest[4] if nearest else None,
                            'route_segment':nearest[2] if nearest else None,
                            'projected_xy':nearest[3] if nearest else None})
        passed=bool(paths) and all(path['passed'] for path in paths)
        passed=passed and not any(item['status']=='unsafe_route_tangent' for item in reviews)
        results.append({'passed':passed,'scope':'sampled_same_mode_route_approaches',
                        'paths':paths,'tangent_reviews':reviews})
    return results


def acceptance_failures(result,include_rail=False):
    """Keep graph acceptance separate from optional physical clearance gates."""
    failures=[]
    if result["graph"]["wagon_components"]!=1:failures.append("disconnected wagon graph")
    if result["graph"]["disconnected_or_missing_road_core_ids"]:failures.append("missing mainland town approaches")
    for station in result["waystations"]:
        if station["distance_to_wagon"] is None or station["distance_to_wagon"]>180:
            failures.append("missing waystation approach: "+station["id"])
    for rid,entry in result.get("physical_collision",{}).items():
        if entry["kind"]==RAIL and not include_rail:continue
        if entry["sample_step"]>10 or not entry["edges_sampled"]:
            failures.append("incomplete physical sampling: "+rid)
        if entry["blocked"]:failures.append("blocked route: "+rid)
    for crossing in result['crossings'] if 'crossings' in result else ():
        review=crossing.get('approach_validation')
        if review is None and 'physical_collision' in result:
            failures.append('missing bridge approach validation: '+crossing['id'])
        elif review is not None and not review['passed']:
            failures.append('unvalidated bridge approach: '+crossing['id'])
    return failures

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",help="Write the deterministic route report to a file")
    parser.add_argument("--check",action="store_true",help="Fail graph gates and, with --physical, foot/horse clearance gates")
    parser.add_argument("--physical",action="store_true",help="Sample foot/horse collision at route centers and usable edges")
    parser.add_argument("--step",type=float,default=10,help="Maximum physical sample spacing (default 10 world units)")
    parser.add_argument("--centerline-only",action="store_true",help="Diagnostic only: omit edge probes")
    parser.add_argument("--bridges",action="store_true",help="Validate route-aware bridge approaches without the full route scan")
    parser.add_argument("--include-rail",action="store_true",help="Also require rail clearance in physical acceptance")
    args=parser.parse_args()
    if args.include_rail and not args.physical:parser.error("--include-rail requires --physical")
    result=audit()
    if args.physical or args.bridges:
        if not math.isfinite(args.step) or args.step<=0:parser.error("--step must be positive and finite")
    if args.physical:
        result['physical_collision']=physical_audit(args.step,not args.centerline_only)
        detail=result['physical_collision']
        total=sum(entry['samples'] for entry in detail.values())
        blocked=sum(entry['blocked'] for entry in detail.values())
        print('Route collision sample summary: %d blocked of %d samples' % (blocked,total))
        nonrail=sum(entry['blocked'] for entry in detail.values() if entry['kind']!=RAIL)
        print('Wagon/trail blocked probes: %d; rail diagnostic blocked probes: %d' %
              (nonrail,blocked-nonrail))
        for name,item in detail.items():
            if item['blocked']:
                print('  %s: %d blocked (water=%d, rock=%d, buildings=%d)' %
                      (name,item['blocked'],item['reasons']['water'],
                       item['reasons']['ridge_or_rock'],item['reasons']['building']))
                print('    first failures:',item['first_failures'][:3])
    if args.physical or args.bridges:
        reviews=bridge_approach_audit(step=args.step)
        for crossing,review in zip(result['crossings'],reviews):
            crossing['approach_validation']=review
            crossing['physically_validated']=review['passed']
            crossing['physical_validation_scope']=review['scope']
        paths=[path for review in reviews for path in review['paths']]
        print('Bridge approaches: %d/%d records passed, %d route paths, %d blocked probes' %
              (sum(review['passed'] for review in reviews),len(reviews),len(paths),
               sum(path['blocked'] for path in paths)))
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.json:
        dest=Path(args.json)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(output,encoding="utf8")
        print("Wrote",dest)
    else:print(output)
    failures=acceptance_failures(result,args.include_rail)
    if args.check and failures:
        print("Road network acceptance failed: "+"; ".join(failures),file=sys.stderr)
        return 1

    return 0

if __name__=="__main__":raise SystemExit(main())
