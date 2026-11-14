#!/usr/bin/env python3
"""Main menu, volume, rebinding, and preference persistence integration."""
import os,sys,tempfile,json,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from menu_preferences import DEFAULT_KEYS,translate,rebind,load_preferences

class Key:
 def __init__(self,value):self.keysym=value;self.state=0
def tap(g,value):
 e=Key(value);g.key_down(e);g.key_up(e)

def main():
 assert translate('w',DEFAULT_KEYS)=='w'
 replacement,error=rebind(DEFAULT_KEYS,'move_up','z')
 assert error is None
 assert translate('z',replacement)=='w'
 assert translate('w',replacement)=='__unbound__'
 _,error=rebind(replacement,'move_up','escape')
 assert error and 'reserved' in error.lower()
 _,error=rebind(replacement,'move_up','s')
 assert error and 'assigned' in error.lower()
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root)
  assert g.screen=='title' and g.menu_index==0
  g.render()
  tap(g,'Down');tap(g,'Down')
  assert g.menu_index==2
  tap(g,'Return')
  assert g.screen=='options'
  assert g.options_tab=='audio'
  before=g.audio.master_volume
  tap(g,'Right')
  assert g.audio.master_volume>before
  tap(g,'Down')
  music_before=g.audio.music_volume
  tap(g,'Left')
  assert g.audio.music_volume<music_before
  tap(g,'Down')
  effects_before=g.audio.effects_volume
  tap(g,'Left')
  assert g.audio.effects_volume<effects_before
  tap(g,'Tab')
  assert g.options_tab=='controls'
  tap(g,'Return')
  assert g.rebinding=='move_up'
  tap(g,'Escape')
  assert g.rebinding is None and g.screen=='options'
  tap(g,'Return');tap(g,'s')
  assert g.bindings['move_up']=='w' and g.rebinding=='move_up'
  tap(g,'z')
  assert g.bindings['move_up']=='z' and g.rebinding is None
  g.render()
  tap(g,'Escape')
  assert g.screen=='title'
  prefs=load_preferences(g.preferences_path)
  assert prefs['keys']['move_up']=='z'
  assert prefs['audio']['master_volume']==g.audio.master_volume
  assert prefs['audio']['music_volume']==g.audio.music_volume
  assert prefs['audio']['effects_volume']==g.audio.effects_volume
  # New Game preserves preferences and the remapped movement controls.
  tap(g,'Up');tap(g,'Up')
  assert g.menu_index==0
  tap(g,'Return')
  assert g.screen=='playing' and g.bindings['move_up']=='z'
  g.dialog=None
  tap(g,'w')
  assert 'w' not in g.keys
  g.key_down(Key('z'))
  assert 'w' in g.keys
  g.key_up(Key('z'))
  assert 'w' not in g.keys
  assert g.save(manual=True)
  # A completed save must not be wiped by an accidental New Game click.
  fresh=game.Game(root)
  tap(fresh,'Return')
  assert fresh.menu_confirm_new and fresh.screen=='title'
  tap(fresh,'n')
  assert fresh.screen=='title' and not fresh.menu_confirm_new
  tap(fresh,'Return')
  assert fresh.menu_confirm_new
  tap(fresh,'y')
  assert fresh.screen=='playing'
  fresh.audio.stop()
  # A second instance simulates the next game launch.
  h=game.Game(root)
  assert h.bindings['move_up']=='z'
  assert h.audio.master_volume==g.audio.master_volume
  assert h.audio.music_volume==g.audio.music_volume
  assert h.audio.effects_volume==g.audio.effects_volume
  tap(h,'Down');tap(h,'Return')
  assert h.screen=='playing' and h.bindings['move_up']=='z'
  # Existing game save and standalone preferences coexist.
  with open(game.SAVE,encoding='utf8') as fh:save=json.load(fh)
  assert save['stage']==g.stage
  assert os.path.isfile(g.preferences_path)
  h.audio.stop();g.audio.stop();root.destroy()
 print('OK: New Game/Continue/Options menu, audio volumes, remap conflicts, persistence and old key unbinding')

if __name__=='__main__':main()
