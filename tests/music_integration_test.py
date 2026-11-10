#!/usr/bin/env python3
"""Creator's real M4A soundtrack mapping and Linux playback integration."""
import os,sys,tempfile,tkinter as tk
from unittest.mock import patch
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from soundtrack_manifest import SOUNDTRACK_PLAYLISTS,SOURCE_FILES,tracks_for,installed_count
from audio_system import AudioDirector
from tools.install_soundtrack import install
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
 assert len(SOURCE_FILES)==12
 assert SOUNDTRACK_PLAYLISTS["title"]==("Forsaken to This Land.m4a",)
 assert "Blood Money Spends.m4a" in SOUNDTRACK_PLAYLISTS["combat"]
 with tempfile.TemporaryDirectory() as tmp:
  source=os.path.join(tmp,"source")
  music=os.path.join(tmp,"music")
  os.makedirs(source)
  # A stand-in only for the test; actual recordings must be supplied by owner.
  for name in SOURCE_FILES:
   with open(os.path.join(source,name),"wb") as f:f.write(b"mock-media")
  installed,skipped,missing=install(source,music)
  assert len(installed)==12 and not missing
  assert installed_count(music)==12
  assert len(tracks_for("wilderness",music))==3
  assert not tracks_for("silence",music)
  assert install(source,music)[1]==list(SOURCE_FILES)
  assert os.path.basename(tracks_for("title",music)[0])=="Forsaken to This Land.m4a"
  with patch("audio_system.shutil.which",side_effect=lambda name:"/usr/bin/ffplay" if name=="ffplay" else None):
   with patch("audio_system.subprocess.Popen",return_value=FakePlayer()) as pop:
    audio=AudioDirector(assets_path=tmp,cache_path=tmp)
    assert audio.backend=="ffplay"
    # Use installed assets under expected audio/music layout.
    asset_dir=os.path.join(tmp,"assets")
    os.makedirs(os.path.join(asset_dir,"music"))
    for name in SOURCE_FILES:
     with open(os.path.join(asset_dir,"music",name),"wb") as f:f.write(b"mock-media")
    audio.assets_path=asset_dir
    assert audio._music_file("title").endswith("Forsaken to This Land.m4a")
    audio.set_music_enabled(True)
    assert audio.set_music_state("title")
    assert audio.music_process is not None
    assert audio.set_music_state("wilderness")
    assert audio._music_file("wilderness").endswith("Whistling the Frontier.m4a")
    audio.music_process.stopped=True
    audio.service()
    assert audio._music_file("wilderness").endswith("Dust on Our Sleeves.m4a")
    assert pop.call_count>=3
    audio.stop()
  with patch("audio_system.shutil.which",return_value=None):
   audio=AudioDirector(assets_path=tmp)
   assert audio.backend=="none"
   assert audio._music_file("title").endswith("Forsaken to This Land.m4a")
   audio.set_music_enabled(True);audio.set_music_state("title")
   assert audio.music_process is None  # No player; never fabricate audio.
  game.SAVE=os.path.join(tmp,"save.json")
  root=tk.Tk();root.withdraw()
  g=game.Game(root)
  assert g.audio.music_enabled
  g.render()
  assert g.audio.music_state=="title"
  g.new_game();g.dialog=None
  assert g.save(manual=True)
  saved=game.Game(root);saved.continue_game();saved.dialog=None
  assert saved.audio.music_enabled
  key(saved,"o")
  assert not saved.audio.music_enabled
  assert saved.save(manual=True)
  loaded=game.Game(root);loaded.continue_game()
  assert not loaded.audio.music_enabled
  loaded.audio.stop();saved.audio.stop();g.audio.stop();root.destroy()
 print("OK: 12 named M4As, original song playlists, installer, player and saved toggle")

if __name__=="__main__":main()
