#!/usr/bin/env python3
"""Virtual display regression test: xvfb-run -a python3 tests/dialogue_test.py."""
import os,sys,tempfile
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
import tkinter as tk

def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  civilian=next(a for a in g.actors if a.kind=='civilian')
  g.offer_civilian_dialogue(civilian)
  assert len(g.choice_dialog['options'])==3
  assert 'Afternoon' in g.choice_dialog['prompt']
  g.render()
  g.select_dialogue_option(0)
  assert g.choice_dialog is None and g.dialog
  g.dialog=None;g.honor=20;g.offer_civilian_dialogue(civilian)
  assert 'not a good one' in g.choice_dialog['prompt']
  g.choice_dialog=None;g.honor=80;g.offer_civilian_dialogue(civilian)
  assert 'helping folks' in g.choice_dialog['prompt']
  g.choice_dialog=None;g.law_status='WANTED';g.offer_civilian_dialogue(civilian)
  assert 'hands' in g.choice_dialog['prompt']
  g.select_dialogue_option(1)
  assert 'price on your head' in g.dialog[1][0]
  g.dialog=None;g.stage=0
  sheriff=next(a for a in g.actors if a.name=='Sheriff Bell')
  g.x,g.y=sheriff.x,sheriff.y
  g.interact()
  assert g.stage==1 and g.choice_dialog is None and g.dialog
  root.destroy()
  print('OK: v1.4 dialogue choices, honor, wanted status, sheriff missions')
if __name__=='__main__':main()
