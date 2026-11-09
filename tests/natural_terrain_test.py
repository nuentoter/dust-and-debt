#!/usr/bin/env python3
"""v2.8-map: natural terrain geometry, safe passages and camera-local rendering."""
import os,sys,tempfile,tkinter as tk,math
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from natural_terrain import (RIDGES,BOULDER_FIELDS,ROCKS,WASHES,
                            hash32,noise,ground_color,landform_solid)
from new_austellia import TOWNS,BRIDGES,ROADS,RAILS
from frontier_world import WAYSTATIONS

def main():
 assert len(RIDGES)>=8 and len(BOULDER_FIELDS)>=20 and len(WASHES)>=5
 assert len(ROCKS)>20
 assert len(set((round(x),round(y)) for x,y,r,solid in ROCKS))==len(ROCKS)
 assert noise(13043,5719)==noise(13043,5719)
 assert ground_color(13043,5719)==ground_color(13043,5719)
 assert hash32(1,2)!=hash32(2,1)
 assert ground_color(15000,6000).startswith('#')
 for key,name,x,y,kind in TOWNS:
  if kind in ('lake','island','spring','waterfall'):continue
  assert not landform_solid(x,y),('landform in town',name)
 for key,name,x,y in WAYSTATIONS:
  assert not landform_solid(x,y),('blocked waystation',name)
 for bx,by,dx,dy,river,kind,width in BRIDGES:
  assert not landform_solid(bx,by),('blocked bridge',river)
 for route in ROADS+RAILS:
  for a,b in zip(route,route[1:]):
   for i in range(11):
    x=a[0]+(b[0]-a[0])*i/10.;y=a[1]+(b[1]-a[1])*i/10.
    assert not landform_solid(x,y),('blocked wagon/rail',x,y)
 solid_rocks=[(x,y) for x,y,r,solid in ROCKS if solid]
 assert solid_rocks and all(landform_solid(x,y) for x,y in solid_rocks)
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  assert g.can_move(6000,4300)
  for x,y in solid_rocks[:10]:assert g.solid(x,y)
  # Camera-panning does not change the static coordinates of natural cover.
  x,y=solid_rocks[0]
  g.x,g.y=x+120,y+120
  for camx,camy in ((x-470,y-320),(10000,10000),(45000,26000)):
   g.camx,g.camy=camx,camy;g.render()
   assert len(g.canvas.find_all())<6000
   assert landform_solid(x,y)
  assert g.save(manual=True)
  reloaded=game.Game(root);reloaded.continue_game()
  assert landform_solid(x,y)
  reloaded.audio.stop();g.audio.stop();root.destroy()
 print('OK: ridges, organic color, washes, rocks, protected towns/bridges/roads and render')

if __name__=='__main__':main()
