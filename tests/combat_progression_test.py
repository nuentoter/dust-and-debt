#!/usr/bin/env python3
"""v2.8 combat progression smoke checks under Xvfb."""
import os,sys,tempfile,json,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from combat_progression import WEAPONS,available_weapons,normal_weapon,incoming_damage,aim_vector

def main():
 assert available_weapons()==('peacemaker',)
 assert 'marshal' in available_weapons(arrests=2)
 assert 'marshal' in available_weapons(work=4)
 assert 'marshal' in available_weapons(kills=10)
 assert normal_weapon('marshal')=='peacemaker'
 assert incoming_damage('trail',10)==6
 assert incoming_damage('standard',10)==10
 assert incoming_damage('hard',10)==14
 enemy=game.Actor(100,5,'bandit')
 assert aim_vector(100,0,[enemy],0,0,True)[1]>0
 assert aim_vector(100,0,[enemy],0,0,False)==(1.,0.)
 civilian=game.Actor(100,0,'civilian')
 assert aim_vector(100,0,[civilian],0,0,True)==(1.,0.)
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None;g.safe_timer=100
  assert g.weapon=='peacemaker' and g.difficulty=='standard' and not g.aim_assist
  g.switch_weapon();assert g.weapon=='peacemaker'
  g.field_arrests=2;g.switch_weapon();assert g.weapon=='marshal'
  g.ammo=0;g.reserve=30;g.reload();assert g.reload_timer==WEAPONS['marshal']['reload']
  g.keys.clear();g.update(2.)
  assert g.ammo==5 and g.reserve==25
  g.reload_timer=0;g.switch_weapon();assert g.weapon=='peacemaker'
  g.key_down(type('Key',(),{'keysym':'F6','state':0})());assert g.difficulty=='hard'
  g.key_down(type('Key',(),{'keysym':'F7','state':0})());assert g.aim_assist
  assert g.save(manual=True)
  with open(game.SAVE,encoding='utf8') as f:s=json.load(f)
  assert s['weapon']=='peacemaker' and s['difficulty']=='hard' and s['aim_assist']
  loaded=game.Game(root);loaded.continue_game()
  assert loaded.difficulty=='hard' and loaded.aim_assist
  assert loaded.field_arrests==2
  assert loaded.weapon=='peacemaker'
  loaded.weapon='marshal';assert loaded.save()
  reloaded=game.Game(root);reloaded.continue_game();assert reloaded.weapon=='marshal'
  reloaded.audio.stop();loaded.audio.stop();g.audio.stop();root.destroy()
 print('OK: weapon unlocks, alternate reload, difficulty, aim assist and save/load')

if __name__=='__main__':main()
