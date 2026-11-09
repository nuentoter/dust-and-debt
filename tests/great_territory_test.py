#!/usr/bin/env python3
"""10x Great Territory geometry, cartography and distant rendering regression."""
import os,sys,math,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from new_austellia import TOWNS,REGIONS,TOWN_BY_ID,travel_road,is_water
from frontier_world import (
 WORLD_WIDTH,WORLD_HEIGHT,SECTOR_NAMES,BIOME_GRID,BIOME_PALETTES,
 LANDMARKS,WAYSTATIONS,ROAD_X,ROAD_Y,START_SPUR,sector_at,region_at,
 biome_at,near_landmark,near_waystation,road_at,map_view,point_on_map,
 world_from_map,draw_map_background
)

def main():
 assert (game.WW,game.WH)==(WORLD_WIDTH,WORLD_HEIGHT)==(60000,40960)
 assert game.WW*game.WH==10*19200*12800
 assert game.WW*game.WH==160*game.OLD_WW*game.OLD_WH
 assert len(SECTOR_NAMES)==len(BIOME_GRID)==4
 assert all(len(row)==6 for row in SECTOR_NAMES)
 assert all(kind in BIOME_PALETTES for row in BIOME_GRID for kind in row)
 assert len({name for row in SECTOR_NAMES for name in row})==24
 assert len(LANDMARKS)>=20 and len(WAYSTATIONS)>=12
 assert all(23<x<WORLD_WIDTH-23 and 23<y<WORLD_HEIGHT-23 for _,_,x,y,*_ in LANDMARKS)
 assert all(23<x<WORLD_WIDTH-23 and 23<y<WORLD_HEIGHT-23 for _,_,x,y in WAYSTATIONS)
 assert len({key for key,*_ in LANDMARKS})==len(LANDMARKS)
 assert len({key for key,*_ in WAYSTATIONS})==len(WAYSTATIONS)
 assert sector_at(30,30)==(0,0) and sector_at(WORLD_WIDTH-30,WORLD_HEIGHT-30)==(3,5)
 assert region_at(57000,36000) in {r[0] for r in REGIONS}
 assert biome_at(30000,21000) in BIOME_PALETTES
 assert not road_at(700,610), 'Preserve handmade original region'
 assert road_at(6000,4300), 'Old frontier approach remains open'
 assert road_at(*TOWN_BY_ID['galloway'][2:4]) and road_at(*TOWN_BY_ID['blackwater_crossing'][2:4]), 'Illustrated railway stations are connected'
 assert not road_at(56400,40300), 'Fictional cross-map straight road grid was removed'
 assert not road_at(*START_SPUR[0]), 'The original hand-painted terrain retains its own paths'
 assert road_at(4900,3250) and road_at(*START_SPUR[1])
 first_landmark=LANDMARKS[0]
 assert near_landmark(first_landmark[2],first_landmark[3])==first_landmark[0]
 assert near_waystation(WAYSTATIONS[0][2],WAYSTATIONS[0][3])==WAYSTATIONS[0][0]
 # Both map modes preserve coordinates when converting screen/world.
 for center in ((680,630),(28600,19100),(58300,39900)):
  for zoom in (False,True):
   view=map_view(zoom,*center)
   if zoom:
    px=view[0]+view[2]*.5;py=view[1]+view[3]*.5
   else:px,py=center
   screen=point_on_map(px,py,view)
   assert screen is not None
   x,y=world_from_map(*screen,view)
   assert abs(x-px)<.1 and abs(y-py)<.1,(zoom,center,x,y)
   assert world_from_map(0,0,view) is None
 with tempfile.TemporaryDirectory() as temp:
  game.SAVE=os.path.join(temp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  old_building=next(b for b in game.BUILDINGS if b[0]=='Sheriff')
  assert old_building[1:]==(320,300,196,130)
  assert len(TOWNS)>=25 and len(REGIONS)>=12
  assert 'blackwater_crossing' in TOWN_BY_ID
  assert g.in_safe_settlement(WAYSTATIONS[0][2],WAYSTATIONS[0][3])
  assert g.in_safe_settlement(WAYSTATIONS[-1][2],WAYSTATIONS[-1][3])
  assert g.can_move(WAYSTATIONS[0][2],WAYSTATIONS[0][3])
  assert not g.in_safe_settlement(58600,38600)
  # Check each far edge with no huge image allocation or out-of-bounds camera.
  for x,y in ((700,650),(18000,3500),(35200,16000),(54000,30000),
              (59900,40850),(35000,40920),(59300,650)):
   g.x,g.y=x,y
   g.camx=max(0,min(game.WW-game.VW,int(x-game.VW/2)))
   g.camy=max(0,min(game.WH-game.VH,int(y-game.VH/2)))
   g.map_open=False
   g.render()
   assert 0<=g.camx<=game.WW-game.VW
   assert 0<=g.camy<=game.WH-game.VH
   assert len(g.canvas.find_all())<5000,'Excessive Tk terrain objects'
  # Landmarks discover and persist; explore a deep-region waypoint.
  g.x,g.y=first_landmark[2],first_landmark[3]
  assert g.discover_landmark()
  assert not g.discover_landmark()
  assert g.landmarks_found==[first_landmark[0]]
  g.x,g.y=WAYSTATIONS[0][2],WAYSTATIONS[0][3];g.hp=48;g.mounted=False;g.interior=None
  assert g.rest_at_frontier_camp() and g.hp==78
  assert not g.rest_at_frontier_camp()
  assert WAYSTATIONS[0][0] in g.camps_used
  g.map_open=True;g.map_zoom=False
  g.render()
  # Zoom around far-off territory and set a waypoint via map click.
  g.map_zoom=True;g.map_center=[57100,36800]
  view=g.current_map_view()
  p=point_on_map(57000,36000,view)
  assert p and g.set_waypoint_from_map(*p)
  assert math.hypot(g.waypoint[0]-57000,g.waypoint[1]-36000)<3
  g.render()
  # Panning and wide overview use the same coordinate basis.
  g.map_zoom=False;g.render()
  assert g.save(manual=True)
  restored=game.Game(root);restored.continue_game()
  assert restored.landmarks_found==[first_landmark[0]]
  assert WAYSTATIONS[0][0] in restored.camps_used
  assert restored.waypoint==g.waypoint
  root.destroy()
 print('OK: 10x New Austellia, named regions, atlas landmarks, waystations, mapped railways, camera, navigation and saves')

if __name__=='__main__':main()
