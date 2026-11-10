#!/usr/bin/env python3
"""Original Western score, optional Linux players and game integration."""
import os
import sys
import tempfile
import wave
from unittest.mock import patch
import tkinter as tk

sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from music_score import SCORES,ensure_score
from audio_system import AudioDirector
import game

class FakePlayer:
 def __init__(self):self.stopped=False
 def poll(self):return 0 if self.stopped else None
 def terminate(self):self.stopped=True
 def wait(self,timeout=None):self.stopped=True;return 0
 def kill(self):self.stopped=True

def key(g,name):
 e=type("Event",(),{"keysym":name,"state":0})()
 g.key_down(e);g.key_up(e)

def main():
 assert set(SCORES)=={"title","town","wilderness","combat","interior","night"}
 with tempfile.TemporaryDirectory() as tmp:
  generated={}
  for state in SCORES:
   path=ensure_score(tmp,state)
   assert os.path.isfile(path)
   assert ensure_score(tmp,state)==path
   with wave.open(path,'rb') as wav:
    assert wav.getframerate()==11025 and wav.getnchannels()==1
    assert wav.getnframes()>40000
    generated[state]=wav.readframes(2048)
   assert os.path.getsize(path)>20000
  assert generated['title']!=generated['combat']
  assert generated['night']!=generated['town']
  music_dir=os.path.join(tmp,"music")
  os.makedirs(music_dir,exist_ok=True)
  with open(os.path.join(music_dir,"title.wav"),'wb') as custom:
   custom.write(b"custom recording placeholder")
  # Custom music always takes priority over synthesized score.
  with patch("audio_system.shutil.which",side_effect=lambda name:"/usr/bin/ffplay" if name=="ffplay" else None):
   with patch("audio_system.subprocess.Popen",return_value=FakePlayer()) as pop:
    audio=AudioDirector(assets_path=tmp,cache_path=tmp)
    assert audio.backend=="ffplay"
    assert audio._music_file("title")==os.path.join(music_dir,"title.wav")
    audio.set_music_enabled(True)
    assert audio.set_music_state("title")
    assert audio.music_process is not None
    assert audio.set_music_state("combat")
    assert pop.call_count>=2
    audio.stop()
  # Common PipeWire and ALSA CLI fallback players can play generated WAVs.
  for fallback in ("pw-play","aplay"):
   with patch("audio_system.shutil.which",side_effect=lambda name:f"/usr/bin/{fallback}" if name==fallback else None):
    with patch("audio_system.subprocess.Popen",return_value=FakePlayer()) as pop:
     audio=AudioDirector(assets_path=tmp,cache_path=tmp)
     assert audio.backend==fallback
     audio.set_music_enabled(True)
     audio.set_music_state("night")
     assert audio.music_process is not None
     # Simulate an ended loop; service() restarts it without blocking Tk.
     audio.music_process.stopped=True
     audio.service()
     assert pop.call_count>=2
     audio.stop()
  game.SAVE=os.path.join(tmp,"save.json")
  root=tk.Tk();root.withdraw()
  g=game.Game(root)
  assert g.audio.music_enabled
  g.render()
  assert g.audio.music_state=="title"
  g.new_game();g.dialog=None
  g.update(.03)
  assert g.audio.music_state in ("town","wilderness","night","combat","interior")
  assert g.save(manual=True)
  saved=game.Game(root);saved.continue_game();saved.dialog=None
  assert saved.audio.music_enabled
  key(saved,"o")
  assert not saved.audio.music_enabled
  assert saved.save(manual=True)
  loaded=game.Game(root);loaded.continue_game()
  assert not loaded.audio.music_enabled
  loaded.audio.stop();saved.audio.stop();g.audio.stop();root.destroy()
 print("OK: six original cached WAV scores, playback routing, custom override, saved music toggle")

if __name__=="__main__":main()
