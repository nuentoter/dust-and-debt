#!/usr/bin/env python3
"""Working Frontier economy and audio preparation regression (Xvfb)."""
import os,sys,tempfile,tkinter as tk
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from working_frontier import work_offer,shop_prices,daily_stock
from audio_system import AudioDirector,CUES,MUSIC_STATES

def main():
 bells=[]
 fake_clock=[10.]
 director=AudioDirector(bell=lambda:bells.append('bell'),clock=lambda:fake_clock[0])
 assert not director.cue('gunshot') and not bells
 director.enabled=True
 assert director.cue('gunshot') and len(bells)==1
 assert not director.cue('reload') and len(bells)==1
 fake_clock[0]+=1.
 assert director.cue('reload') and len(bells)==2
 assert not director.cue('unknown')
 assert director.set_music_state('wilderness')
 assert not director.set_music_state('wilderness')
 assert not director.set_music_state('invalid')
 director.configure({'music_enabled':True,'master_volume':8,'effects_volume':-.1})
 assert director.master_volume==1 and director.effects_volume==0
 assert 'gunshot' in CUES and 'combat' in MUSIC_STATES
 with tempfile.TemporaryDirectory() as tmp:
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  assert hasattr(g,'work_active') and hasattr(g,'shop_inventory')
  assert g.work_finished==0 and g.work_active is None
  assert g.audio.music_state=='silence' and not g.audio.enabled
  assert len(g.audio.settings())==5
  # A store has finite daily inventory, consistent pricing and saved stock.
  g.money=500
  g.interior='General Store'
  stock=g.shop_inventory()
  assert stock==daily_stock('store',game.SHOP_GOODS['store'])
  cost=g.shop_cost(0)
  assert cost==shop_prices('store',game.SHOP_GOODS['store'],g.honor)[0]
  reserve=g.reserve
  starting=stock[0]
  for i in range(starting):g.buy_item(0)
  assert stock[0]==0 and g.reserve==reserve+30*starting
  amount=g.money
  g.buy_item(0)
  assert g.money==amount, 'Sold out inventory cannot be purchased again'
  assert g.save(manual=True)
  restored=game.Game(root);restored.continue_game();restored.dialog=None
  restored.interior='General Store'
  assert restored.shop_inventory()[0]==0
  restored.advance_clock(24)
  assert restored.economy_day==1 and restored.shop_inventory()[0]==starting
  assert restored.work_expenses==cost*starting
  # Stationmaster work: take task, visit destination, return for payment.
  restored.interior=None;restored.shop_open=False;restored.money=35
  nell=next(a for a in restored.actors if a.name=='Nell the stationmaster')
  restored.x,restored.y=nell.x,nell.y
  assert restored.offer_work()
  active=restored.work_active
  assert active and active['giver']==nell.name and active['reward']==22
  assert restored.waypoint==active['destination']
  assert restored.save(manual=True)
  r=game.Game(root);r.continue_game();r.dialog=None
  assert r.work_active['title']==active['title']
  tx,ty=r.work_active['destination']
  r.x,r.y=tx,ty
  assert r.complete_work_step() and r.work_active['status']=='return'
  assert not r.complete_work_step(), 'No multiple task completion'
  r.x,r.y=nell.x,nell.y
  earned_before=r.money
  assert r.offer_work()
  assert r.work_active is None and r.money==earned_before+22
  assert r.work_finished==1 and r.work_income==22
  assert not r.offer_work(), 'No same-day repeat of completed job'
  r.advance_clock(24)
  assert r.offer_work(), 'Job renews next day'
  # A second type of employment is available from non-station staff.
  r.work_active=None
  amos=next(a for a in r.actors if a.name=='Rancher Amos')
  r.x,r.y=amos.x,amos.y
  assert r.offer_work() and r.work_active['kind']=='ranch'
  r.work_ledger_open=True
  r.render()
  r.work_ledger_open=False
  r.map_open=True;r.render();r.map_open=False
  r.x,r.y=amos.x,amos.y;r.render()
  assert r.save(manual=True)
  again=game.Game(root);again.continue_game();again.dialog=None
  assert again.work_active and again.work_active['giver']=='Rancher Amos'
  assert again.work_income==22 and again.work_finished==1
  # Time, horse care and current-version settings work without external audio files.
  again.mounted=True;again.horse_hp=25
  again.update(.04)
  assert again.horse_hp<25
  again.audio.set_music_state('town')
  again.audio.music_enabled=True
  assert again.save(manual=True)
  settings=game.Game(root);settings.continue_game()
  assert settings.audio.music_enabled
  root.destroy()
 print('OK: v2.5 daily stock, pricing, jobs, payment, income, horse care, audio routing, settings, save/load')

if __name__=='__main__':main()
