#!/usr/bin/env python3
"""Gunfight regression: xvfb-run -a python3 tests/combat_test.py"""
import os,sys,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,"save.json")
  root=tk.Tk();root.withdraw();g=game.Game(root);g.new_game();g.dialog=None
  assert hasattr(g,"line_of_fire") and hasattr(g,"combat_damage")
  assert g.line_of_fire(700,610,720,610)
  assert not g.line_of_fire(700,600,920,380)  # store building intervenes
  target=game.Actor(g.x+45,g.y,"bandit","Test Rider",100,100,75)
  assert g.combat_damage(target)==52
  g.deadeye_active=True
  assert g.combat_damage(target)>52
  g.deadeye_active=False
  g.hit_marker=.15;g.render()
  g.safe_timer=0.;g.x,g.y=1450,500
  foe=game.Actor(g.x+220,g.y,"bandit","Drifter",70,70,75)
  g.actors.append(foe)
  g.update_ai(.05)
  assert foe.x<g.x+220 or foe.y!=g.y
  assert g.save(manual=True)
  root.destroy()
 print("OK: v1.6 cover sightlines, strafing, damage and save")
if __name__=="__main__":main()
