#!/usr/bin/env python3
"""v2.9-map rendering/regression smoke on Xvfb for roads, trails and 24 sites."""
import os,sys,tempfile,time,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from frontier_destinations import DESTINATIONS,fishing_spots,campsites
from frontier_route_art import clip_segment,draw_scaled_routes
from frontier_routes import ROUTE_GRAPH
from new_austellia import BRIDGE_DECKS

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
   # The real world pipeline must draw shared-footprint bridge polygons.
   rail=max((d for d in BRIDGE_DECKS if d.kind=='rail'),key=lambda d:d.half_length)
   road=next(d for d in BRIDGE_DECKS if d.kind=='road')
   for deck in (road,rail):
    g.x,g.y=deck.x,deck.y
    g.camx=max(0,g.x-game.VW/2);g.camy=max(0,g.y-game.VH/2)
    g.render()
    assert g.canvas.find_withtag('bridge_deck'),(detail,deck.water)
    assert len(g.canvas.find_all())<3000,(detail,deck.water)
   g.map_open=True
   g.map_zoom=False;g.render()
   g.map_zoom=True;g.map_center=[g.x,g.y];g.render()
   g.map_open=False;g.render()
  assert len(DESTINATIONS)==24
  rest_site=campsites()[0]
  g.x,g.y=rest_site.x,rest_site.y
  g.mounted=False;g.interior=None;g.hp=30
  assert g.rest_at_frontier_camp()
  assert rest_site.id in g.camps_used and g.hp>=60
  assert not g.rest_at_frontier_camp(), 'One free rest per named camp'
  assert g.save(manual=True)
  loaded=game.Game(root);loaded.continue_game()
  assert rest_site.id in loaded.camps_used
  loaded.audio.stop()
  g.audio.stop();root.destroy()
  print("OK: world, atlas and minimap render at 4 destination sites in Normal/Low detail")
  print("Samples (mode,site,ms,canvas objects):",results)

if __name__=="__main__":main()
