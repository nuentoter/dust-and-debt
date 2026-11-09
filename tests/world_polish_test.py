#!/usr/bin/env python3
"""World Polish checks: xvfb-run -a python3 tests/world_polish_test.py"""
import os,sys,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game

def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,"save.json")
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  assert hasattr(g,'set_waypoint_from_map') and hasattr(g,'weather_kind')
  assert g.waypoint is None and g.sound_on is False
  assert not g.set_waypoint_from_map(20,20)
  assert g.set_waypoint_from_map(game.MAP_RECT[0]+game.MAP_RECT[2]-1,game.MAP_RECT[1]+game.MAP_RECT[3]-1)
  assert g.waypoint and 0<g.waypoint[0]<game.WW and 0<g.waypoint[1]<game.WH
  g.map_open=True;g.render()
  g.map_open=False;g.render()
  assert g.save(manual=True)
  r=game.Game(root);r.continue_game();r.dialog=None
  assert r.waypoint==g.waypoint
  assert r.sound_on is False
  conditions=set()
  for h in range(24):
   r.clock=h;conditions.add(r.weather_kind())
   r.render()
  assert conditions.issubset({'rain','clear','dust'}) and len(conditions)>1
  for name in ('Saloon','Doctor','General Store','Hotel','Stable','Sheriff','Ghost Chapel'):
   r.interior=name;r.shop_open=False;r.render()
  r.interior=None
  # Mocking a system bell isn't necessary: disabled cues must be safe.
  r.sound_on=False;r.sound_cue()
  root.destroy()
 print('OK: waypoint persistence, map markers, weather, interiors and optional sound')
if __name__=='__main__':main()
