#!/usr/bin/env python3
"""Print/write a reproducible baseline audit of New Austellia travel routes.

Usage:
  python tools/audit_routes.py
  python tools/audit_routes.py --json docs/road_audit.json
  python tools/audit_routes.py --check

This stage deliberately reports failures rather than fabricating connecting
routes or marking disconnected towns as reachable. --check exits nonzero if
mainland wagon components remain disconnected.
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from frontier_routes import ROUTE_GRAPH, WAGON, RAIL, projection
from new_austellia import BRIDGES, TOWNS, MAJOR_TOWNS, ROADS, RAILS, is_water
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
    for i,(x,y,dx,dy,name,kind,width) in enumerate(BRIDGES):
        center=(x,y)
        bank0=(x-dx*(width+135),y-dy*(width+135))
        bank1=(x+dx*(width+135),y+dy*(width+135))
        bridges.append({"id":"crossing_%03d"%i,"water":name,"kind":kind,
                        "xy":[round(x,1),round(y,1)],
                        "center_passable":not is_water(*center),
                        "entry_passable":not is_water(*bank0),
                        "exit_passable":not is_water(*bank1),
                        "physically_validated":False})
    # Critical initial-town network: 12 mainland towns + one original area.
    core=[a for a in sites if a["id"] in MAJOR_TOWNS]
    root_components=sorted(set(a["component"] for a in core if a["component"] is not None))
    disconnected=[a["id"] for a in core if a["component"] is None
                  or a["needs_road_approach"] or a["component"]!=root_components[0]]
    return {
        "schema":1,"milestone":"v2.9-map","phase":"baseline_audit",
        "world":[60000,40960],
        "source":{"wagon_polylines":len(ROADS),"rail_polylines":len(RAILS),
                  "site_count":len(TOWNS),"waystations":len(WAYSTATIONS),
                  "starter_spur":[list(p) for p in START_SPUR]},
        "graph":{"wagon_components":len(groups),"rail_components":len(graph.components("rail")),
                 "wagon_routes":road_groups,"mainland_core_components":root_components,
                 "disconnected_or_missing_road_core_ids":disconnected},
        "sites":sites,"waystations":stations,"crossings":bridges,
        "known_exemptions":["calhoun_island","herons_key","drake_isles"],
        "notes":[
            "No connector geometry has been authored yet; disconnected components are expected.",
            "A visually drawn connection does not prove passage through terrain/building collision.",
            "The original map's START_SPUR is tracked as separate geometry.",
            "Rail track proximity does not count toward wagon connectivity.",
            "This report makes no claims about existing game runtime frame rate."]
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",help="Write the deterministic baseline report to a file")
    parser.add_argument("--check",action="store_true",help="Fail if the required mainland road network is disconnected")
    args=parser.parse_args()
    result=audit()
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.json:
        dest=Path(args.json)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(output,encoding="utf8")
        print("Wrote",dest)
    else:print(output)
    if args.check and (result["graph"]["wagon_components"]!=1 or
                       result["graph"]["disconnected_or_missing_road_core_ids"]):
        print("Road network not ready for autonomous travelers",file=sys.stderr)
        return 1
    return 0

if __name__=="__main__":raise SystemExit(main())
