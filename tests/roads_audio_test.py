#!/usr/bin/env python3
"""v2.6 regional road events, escort rescue and audio playback regression."""
import os,sys,tempfile,tkinter as tk,math,wave
from unittest.mock import patch
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import game
from frontier_world import WAYSTATIONS
from road_events import EVENT_TYPES,mission_offer,offer_for_day,dispatch_rumor,safe_event_position
from audio_system import AudioDirector
from audio_assets import ensure_wav

class DummyProcess:
 def __init__(self):self.stopped=False
 def poll(self):return 0 if self.stopped else None
 def terminate(self):self.stopped=True
 def wait(self,timeout=None):self.stopped=True;return 0
 def kill(self):self.stopped=True

def main():
 assert len(WAYSTATIONS)>=13 and len(EVENT_TYPES)==4
 assert all(mission_offer(WAYSTATIONS[0][0],kind) for kind in EVENT_TYPES)
 assert len({offer_for_day(WAYSTATIONS[0][0],day)['type'] for day in range(4)})==4
 assert isinstance(dispatch_rumor(52000,34000,3),str)
 assert safe_event_position(200,200,lambda x,y,r:True)==(200,200)
 with tempfile.TemporaryDirectory() as tmp:
  # Synthesized original PCM audio is real audio, not music files in the repository.
  for sound in ('gunshot','lasso','horse'):
   path=ensure_wav(tmp,'sfx',sound)
   with wave.open(path,'rb') as wav:
    assert wav.getnchannels()==1 and wav.getnframes()>1000
  ambient=ensure_wav(tmp,'music','night')
  with wave.open(ambient,'rb') as wav:assert wav.getnframes()>60000
  assert ensure_wav(tmp,'music','night')==ambient
  assert ensure_wav(tmp,'music','title') is None
  # v2.9 recorded music is required; provide test-only valid WAV overrides
  # for music state switching, rather than relying on generated score.
  os.makedirs(os.path.join(tmp,'music'),exist_ok=True)
  import shutil
  for scene in ('wilderness','town'):
   shutil.copy2(ambient,os.path.join(tmp,'music',scene+'.wav'))
  with patch('audio_system.shutil.which',side_effect=lambda name: '/usr/bin/ffplay' if name=='ffplay' else None):
   with patch.dict(os.environ,{'DUST_AND_DEBT_SILENT':'0'}), patch('audio_system.subprocess.Popen',side_effect=lambda *a,**k:DummyProcess()) as pop:
    ad=AudioDirector(assets_path=tmp,cache_path=tmp)
    assert ad.backend=='ffplay'
    ad.enabled=True
    assert ad.cue('gunshot')
    ad.set_music_enabled(True)
    assert ad.set_music_state('wilderness')
    assert ad.music_process is not None
    assert ad.set_music_state('town')
    assert pop.call_count>=3
    ad.stop()
    assert ad.music_process is None
  # No audio backend must not stop the game.
  quiet=AudioDirector()
  quiet.enabled=True
  assert not quiet.cue('gunshot')
  game.SAVE=os.path.join(tmp,'save.json')
  root=tk.Tk();root.withdraw()
  g=game.Game(root);g.new_game();g.dialog=None
  agents=[a for a in g.actors if a.kind=='station_agent']
  outer_bandits=[a for a in g.actors if a.kind=='bandit' and a.x>20000]
  assert len(agents)==len(WAYSTATIONS) and len(outer_bandits)>=20
  assert hasattr(g,'road_contract') and hasattr(g,'road_contracts_done')
  # An ambush can appear on open roads, never in protected waystations.
  g.x,g.y=21800,18800;g.safe_timer=0
  with patch('game.random.choice',return_value='ambush'):
   assert g.spawn_road_encounter()
  assert any(a.name=='Road Ambusher' and not a.dead for a in g.actors)
  # Four contracts from four adjacent waystations, each completed only once.
  for idx,kind in enumerate(EVENT_TYPES):
   station=WAYSTATIONS[idx]
   g.x,g.y=station[2],station[3]
   assert g.offer_road_contract()
   job=g.road_contract
   assert job and job['type']==kind and job['status']=='outbound'
   amount=g.money
   if kind=='escort':
    follower=g.road_escort()
    assert follower is not None
    original=(follower.x,follower.y)
    g.x,g.y=follower.x+150,follower.y
    g.update_road_escort(.45)
    assert (follower.x,follower.y)!=original
    # Save mid-escort and verify the passenger returns.
    assert g.save(manual=True)
    recovered=game.Game(root);recovered.continue_game();recovered.dialog=None
    assert recovered.road_contract['type']=='escort'
    assert recovered.road_escort()
    g=recovered
    follower=g.road_escort()
    # Simulate completing a long journey, without testing user walking speed.
    tx,ty=job['target_pos']
    g.x,g.y=tx,ty
    follower.x,follower.y=tx-25,ty+20
   else:
    g.x,g.y=job['target_pos']
   assert g.progress_road_contract()
   if kind in ('salvage','survey'):
    assert g.road_contract and g.road_contract['status']=='return'
    g.x,g.y=station[2],station[3]
    assert g.offer_road_contract()
   assert g.road_contract is None
   assert g.money>=amount+job['reward']
   assert not g.progress_road_contract(), 'No duplicate road job payout'
  assert g.road_contracts_done==4
  assert g.road_income>=sum(mission_offer(WAYSTATIONS[i][0],kind)['reward'] for i,kind in enumerate(EVENT_TYPES))
  assert g.regional_standing
  # Same-day dispatch not repeated at a station.
  g.x,g.y=WAYSTATIONS[0][2],WAYSTATIONS[0][3]
  assert not g.offer_road_contract()
  g.advance_clock(24)
  assert g.offer_road_contract()
  assert g.road_contract['type']=='courier'
  g.road_contract=None;g.waypoint=None
  g.x,g.y=WAYSTATIONS[3][2],WAYSTATIONS[3][3]
  previous=dict(g.regional_standing)
  g.report_crime(1,'Theft')
  region=game.region_at(g.x,g.y)
  assert g.regional_standing.get(region,0)<previous.get(region,0)
  g.map_open=True;g.render();g.map_open=False
  g.x,g.y=58000,34000;g.render()
  assert g.save(manual=True)
  reloaded=game.Game(root);reloaded.continue_game()
  assert reloaded.road_contracts_done==4
  assert reloaded.regional_standing==g.regional_standing
  assert reloaded.road_offer_day==g.road_offer_day
  reloaded.audio.stop();g.audio.stop()
  root.destroy()
 print('OK: 4 road job types, escort following, staged deliveries, region reputation, persistent dispatches and real optional WAV/audio backend')

if __name__=='__main__':main()
