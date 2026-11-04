#!/usr/bin/env python3
"""Regression test for Living Towns: xvfb-run -a python3 tests/living_towns_test.py"""
import os,sys,tempfile
import tkinter as tk
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import game

def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  assert hasattr(g,'npc_schedule') and hasattr(g,'daily_period')
  assert len([a for a in g.actors if a.kind=='civilian'])>=16
  martha=next(a for a in g.actors if a.name=='Martha')
  sheriff=next(a for a in g.actors if a.name=='Sheriff Bell')
  fixed=(sheriff.x,sheriff.y)
  g.clock=8;g.update_npc_schedules()
  morning=martha.destination
  assert g.daily_period()=='morning' and g.can_move(*morning)
  assert morning==(750,550)
  g.clock=14;g.update_npc_schedules()
  assert g.daily_period()=='working' and martha.destination!=(750,550)
  assert g.npc_activity(martha)=='selling produce'
  g.offer_civilian_dialogue(martha)
  assert 'selling produce' in g.choice_dialog['options'][0][1]
  g.choice_dialog=None
  x,y=martha.x,martha.y
  for i in range(30):g.update_ai(.05)
  assert (martha.x,martha.y)!=(x,y)
  g.clock=19;g.update_npc_schedules()
  assert g.daily_period()=='evening'
  assert martha.destination==(655,570)
  g.clock=1;g.update_npc_schedules()
  assert g.daily_period()=='night'
  assert martha.destination==g.npc_home['Martha']
  assert (sheriff.x,sheriff.y)==fixed
  g.x,g.y=fixed
  g.stage=0;g.interact()
  assert g.stage==1 and g.dialog and g.choice_dialog is None
  g.dialog=None;g.render()
  assert g.save(manual=True)
  r=game.Game(root);r.continue_game()
  assert r.stage==1
  root.destroy()
 print('OK: NPC routines, dialogue, movement, story and save compatibility')
if __name__=='__main__':main()
