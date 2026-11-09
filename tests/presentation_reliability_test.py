#!/usr/bin/env python3
"""v2.9: settings UI, schema migration, corruption and backup recovery."""
import json,os,sys,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from save_schema import SAVE_SCHEMA,migrate_save,validate_save

def key(g,name):
 event=type('Event',(),{'keysym':name,'state':0})()
 g.key_down(event);g.key_up(event)

def main():
 old={'x':700,'y':610,'stage':0,'work_finished':5,'contract':{'status':'hunting'}}
 migrated=migrate_save(old)
 assert migrated['schema']==SAVE_SCHEMA
 assert migrated['work_finished']==5 and migrated['contract']==old['contract']
 assert migrated['settings']=={'graphics':'normal','weather':True,'hints':True}
 for bad in ({'x':float('nan'),'y':610,'stage':0},
             {'x':700,'y':610,'stage':True},
             {'x':700,'y':610,'stage':0,'contract':'broken'},
             {'x':700,'y':610,'stage':0,'schema':SAVE_SCHEMA+1}):
  try:validate_save(bad)
  except ValueError:pass
  else:raise AssertionError('Accepted corrupt save '+str(bad))
 with tempfile.TemporaryDirectory() as temp:
  game.SAVE=os.path.join(temp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  assert game.VERSION.startswith('2.9')
  key(g,'F8')
  assert g.settings_open
  key(g,'1');assert g.graphics_quality=='low'
  key(g,'2');assert not g.weather_enabled
  key(g,'3');assert not g.context_hints
  key(g,'F8');assert not g.settings_open
  g.render()
  assert g.save(manual=True)
  key(g,'F8');key(g,'1');key(g,'2');key(g,'3');key(g,'F8')
  assert g.save(manual=True)
  with open(game.SAVE,encoding='utf8') as f:latest=json.load(f)
  assert latest['schema']==SAVE_SCHEMA and latest['settings']['graphics']=='normal'
  assert os.path.isfile(game.SAVE+'.bak')
  with open(game.SAVE,'w',encoding='utf8') as f:f.write('{"x": NaN, "y": 610, "stage": 0}')
  restored=game.Game(root);restored.continue_game()
  assert restored.loaded_backup and restored.screen=='playing'
  assert restored.graphics_quality=='low'
  assert restored.weather_enabled is False and restored.context_hints is False
  assert restored.save(manual=True)
  with open(game.SAVE,encoding='utf8') as f:repaired=json.load(f)
  validate_save(repaired)
  restored.audio.stop();g.audio.stop();root.destroy()
 print('OK: v2.9 settings, legacy migration, corrupt-save validation and backup recovery')

if __name__=='__main__':main()
