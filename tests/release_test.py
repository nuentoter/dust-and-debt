#!/usr/bin/env python3
"""Complete Frontier release regression: xvfb-run -a python3 tests/release_test.py"""
import json
import os
import sys
import tempfile
import tkinter as tk

sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game

def main():
 with tempfile.TemporaryDirectory() as temp:
  game.SAVE=os.path.join(temp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  assert game.VERSION.startswith('2.0')
  assert g.save(manual=True)
  g.x,g.y=1235.,742.
  g.money=235
  assert g.save(manual=True)
  assert os.path.exists(game.SAVE+'.bak')
  with open(game.SAVE+'.bak',encoding='utf8') as f:
   previous=json.load(f)
  assert previous['x']!=1235.
  # Primary file damaged: existing backup loads and is not overwritten.
  with open(game.SAVE,'w',encoding='utf8') as f:f.write('{broken')
  restored=game.Game(root);restored.continue_game()
  assert restored.screen=='playing' and restored.loaded_backup
  assert (restored.x,restored.y)==(previous['x'],previous['y'])
  assert restored.save(manual=True)
  with open(game.SAVE,encoding='utf8') as f:
   repaired=json.load(f)
  assert repaired['stage']==previous['stage']
  # If both copies are corrupt, stay at title and DO NOT wipe either.
  with open(game.SAVE,'w') as f:f.write('{bad')
  with open(game.SAVE+'.bak','w') as f:f.write('not json')
  fail=game.Game(root);fail.continue_game()
  assert fail.screen=='title'
  with open(game.SAVE) as f:assert f.read()=='{bad'
  # Existing quests can still be staged and mission enemies defeated.
  game.SAVE=os.path.join(temp,'story.json')
  story=game.Game(root);story.new_game();story.dialog=None
  sheriff=next(a for a in story.actors if a.kind=='sheriff')
  story.x,story.y=sheriff.x,sheriff.y
  story.interact()
  assert story.stage==1 and story.enemies_remaining('hollow')==5
  story.dialog=None
  for a in story.actors:
   if a.kind=='mission_hollow':a.dead=True
  story.update(.03)
  assert story.stage==2
  story.dialog=None;story.x,story.y=sheriff.x,sheriff.y
  story.interact()
  assert story.stage==3 and story.money>=115
  story.dialog=None
  story.autosave_timer=.01
  story.update(.03)
  assert story.autosave_timer>80 and story.last_save_ok
  # Rendering with distant actors, old map and new terrain.
  story.x,story.y=11900.,8400.
  story.camx,story.camy=11400,8100
  story.render()
  root.destroy()
 print('OK: v2.0 save backup recovery, safe corrupt-save behavior, missions, autosave, rendering')

if __name__=='__main__':
 main()
