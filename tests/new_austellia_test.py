#!/usr/bin/env python3
"""The illustrated New Austellia map: geography, waterways, towns and interaction."""
import os,sys,math,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from new_austellia import (
 P,TOWNS,TOWN_BY_ID,REGIONS,MAJOR_TOWNS,RAILS,ROADS,WATERWAYS,LAKES,
 region_at,biome_at,travel_road,river_at,is_water,coastal_water,
 near_atlas_town,draw_atlas
)
from frontier_world import WAYSTATIONS,LANDMARKS,MAP_RECT,world_from_map,point_on_map

def main():
 assert len(TOWNS)>=30 and len(REGIONS)>=12
 assert len(RAILS)>=4 and len(ROADS)>=10 and len(WATERWAYS)>=4
 assert len(MAJOR_TOWNS)>=10
 for name in ("Galloway","Blackwater Crossing","Saint Brigid's Port",
              "Roan Creek","Dustwell","Bayou Haven","Saint's Hollow"):
  assert any(t[1]==name for t in TOWNS),name
 assert TOWN_BY_ID["blackwater_crossing"][2:4]==P(648,515)
 assert TOWN_BY_ID["saint_brigids"][2:4]==P(819,891)
 assert TOWN_BY_ID["pineheart"][2:4]==P(1157,142)
 assert region_at(*P(1084,213)) in [v[0] for v in REGIONS]
 assert region_at(*P(260,820))=="Copper Sands Desert"
 assert biome_at(*P(1200,495))=="forest"
 assert river_at(*P(320,440))=="Sable River"
 assert travel_road(*P(648,515)),'Blackwater railroad crossing must be navigable'
 assert not is_water(*P(648,515)), 'Rail bridge must permit passage'
 assert is_water(*P(505,146)),'Frostvein Lake is an obstacle'
 assert coastal_water(*P(900,1020)),'Auburn Gulf must exist'
 assert not coastal_water(*P(700,600)),'Heartland should be dry land'
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,"save.json")
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  assert g.region_name(700,610)=="Cinder Creek"
  # All mapped towns and road dispatch stations need safe ground access.
  for key,name,x,y,kind in TOWNS:
   assert 0<x<game.WW and 0<y<game.WH
   assert not is_water(x,y),name
  for key,name,x,y in WAYSTATIONS:
   assert g.in_safe_settlement(x,y),name
   assert g.can_move(x,y,8),name
  assert g.solid(*P(505,146),r=8)
  assert g.can_move(*P(648,515),8)
  # Relocated inherited frontier towns correspond to actual atlas locations.
  expected={"drybone":"galloway","ironwell":"iron_mesa","painted":"dustwell",
            "saltwater":"roan_creek","ember":"larkfield","sundown":"riversend"}
  for key,target in expected.items():
   town=next(t for t in game.SETTLEMENTS if t[0]==key)
   assert town[1:4]==TOWN_BY_ID[target][1:4],(town,target)
   assert g.can_move(town[2],town[3]),town[1]
  # Full and zoomed atlas share a world-space projection and draw without a giant image.
  g.map_open=True
  for zoom,center in ((False,(40000,20000)),(True,P(648,515))):
   g.map_zoom=zoom;g.map_center=list(center)
   view=g.current_map_view()
   target=center if not zoom else (view[0]+view[2]/2,view[1]+view[3]/2)
   pt=point_on_map(*target,view)
   assert pt
   world=world_from_map(*pt,view)
   assert math.hypot(world[0]-target[0],world[1]-target[1])<1
   g.render()
   assert len(g.canvas.find_all())<7000
  # Landmarks and mapped towns remain visible at distant local coordinates.
  g.map_open=False
  for key in ("galloway","blackwater_crossing","roan_creek","bayou_haven"):
   tx,ty=TOWN_BY_ID[key][2:4]
   g.x,g.y=tx,ty
   g.camx=max(0,min(game.WW-game.VW,int(tx-game.VW/2)))
   g.camy=max(0,min(game.WH-game.VH,int(ty-game.VH/2)))
   g.render()
   assert len(g.canvas.find_all())<6000
  assert g.save(manual=True)
  reloaded=game.Game(root);reloaded.continue_game()
  assert reloaded.screen=="playing"
  reloaded.audio.stop();g.audio.stop()
  root.destroy()
 print("OK: New Austellia 1898 atlas, named towns, winding railway, bridges, rivers, lakes, Gulf, 6 relocated towns and local renderer")

if __name__=="__main__":main()
