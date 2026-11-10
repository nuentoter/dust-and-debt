#!/usr/bin/env python3
"""v2.9-map rendering/regression smoke on Xvfb for roads, trails and 24 sites."""
import os,sys,tempfile,time,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from frontier_destinations import DESTINATIONS,fishing_spots,campsites
from frontier_route_art import clip_segment,draw_scaled_routes
from frontier_routes import ROUTE_GRAPH

def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,"save.json")
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  results=[]
  for detail in ("normal","low"):
   g.graphics_quality=detail
   for site in (fishing_spots()[0],campsites()[0],fishing_spots()[-1],campsites()[-1]):
    g.x,g.y=site.x,site.y
    g.camx=max(0,g.x-game.VW/2);g.camy=max(0,g.y-game.VH/2)
    t=time.perf_counter();g.render()
    elapsed=time.perf_counter()-t
    count=len(g.canvas.find_all())
    assert count>20 and count<3000,(detail,site.id,count)
    results.append((detail,site.id,round(elapsed*1000,1),count))
   g.map_open=True
   g.map_zoom=False;g.render()
   g.map_zoom=True;g.map_center=[g.x,g.y];g.render()
   g.map_open=False;g.render()
  assert len(DESTINATIONS)==24
  assert g.save(manual=True)
  g.audio.stop();root.destroy()
  print("OK: world, atlas and minimap render at 4 destination sites in Normal/Low detail")
  print("Samples (mode,site,ms,canvas objects):",results)

if __name__=="__main__":main()
