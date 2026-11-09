#!/usr/bin/env python3
"""Outer-terrain collision and rendering regression."""
import os,sys,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from natural_terrain import ROCKS,landform_solid
def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw();g=game.Game(root);g.new_game();g.dialog=None
  assert game.WW==60000 and game.WH==40960
  assert not g.is_frontier_road(700,610)
  assert g.is_frontier_road(6000,4300)
  assert g.terrain_obstacle(700,610) is None
  # New v2.8-map cover is authored along ridges, not old 112-pixel tiles.
  assert len(ROCKS)>=20
  found=next(((x,y,r) for x,y,r,solid in ROCKS if solid),None)
  assert found is not None
  x,y,r=found
  assert landform_solid(x,y)
  assert g.solid(x,y)
  assert g.can_move(6000,4300)
  assert not g.line_of_fire(x-60,y,x+60,y)
  g.x,g.y=7500.,6500.;g.camx=7000;g.camy=6200
  g.render()
  assert g.save(manual=True)
  root.destroy()
 print('OK: v2.8-map natural cover collision, roads and terrain rendering')
if __name__=='__main__':main()
