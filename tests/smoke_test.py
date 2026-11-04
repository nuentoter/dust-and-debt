#!/usr/bin/env python3
"""Headless/virtual-display smoke test: xvfb-run -a python3 tests/smoke_test.py."""
import os,sys,tempfile
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
import tkinter as tk

def main():
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  assert g.honor==50 and g.deadeye==100
  g.change_honor(-8,'test');g.report_crime(2,'test')
  assert g.honor==42 and g.law_status=='WANTED'
  g.deadeye_active=True;g.update(.05)
  assert 0<g.deadeye<100
  g.save()
  r=game.Game(root);r.continue_game();r.dialog=None
  assert r.honor==42 and r.crimes==1 and 0<r.deadeye<100
  for overlay in ('map_open','journal_open','show_help'):
   setattr(r,overlay,True);r.render();setattr(r,overlay,False)
  r.render();r.interior='General Store';r.render();r.interior=None
  r.mouse=(650,320);r.fire();r.update(.04);r.render()
  r.screen='title';r.render()
  root.destroy()
  print('OK: v1.3 mechanics, persistence and graphical scenes')
if __name__=='__main__':main()
