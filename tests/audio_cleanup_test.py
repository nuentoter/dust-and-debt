#!/usr/bin/env python3
"""Silent playback, root destruction and interpreter-exit audio cleanup."""
import os
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from audio_system import AudioDirector
import game


def main():
    with patch.dict(os.environ,{'DUST_AND_DEBT_SILENT':'1'}):
        bell=Mock()
        audio=AudioDirector(bell=bell)
        audio.player='/never/launch';audio.backend='ffplay';audio.enabled=True
        with patch('audio_system.subprocess.Popen') as launch:
            assert audio._run('song.m4a',.5) is None
            assert not audio.cue('menu')
            launch.assert_not_called();bell.assert_not_called()
    # Direct Tk destruction must stop every game attached to the root.
    root=tk.Tk();root.withdraw()
    first=game.Game(root);second=game.Game(root)
    players=[]
    for instance in (first,second):
        player=Mock();player.poll.return_value=None
        instance.audio.music_process=player;players.append(player)
    root.destroy()
    for player in players:
        player.terminate.assert_called_once();player.wait.assert_called_once()
    # Stubborn players are killed and reaped, including effects.
    audio=AudioDirector()
    player=Mock();player.poll.return_value=None
    player.wait.side_effect=[subprocess.TimeoutExpired('player',.2),0]
    audio.effects=[player];audio.stop()
    player.kill.assert_called_once();assert player.wait.call_count==2
    assert not audio.effects
    # A forgotten stop still reaps an actual child on normal Python exit.
    # The child only sleeps: no audio device is opened.
    code='''import subprocess,sys
from audio_system import AudioDirector
audio=AudioDirector()
audio.music_process=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print(audio.music_process.pid,flush=True)
'''
    pid=int(subprocess.check_output([sys.executable,'-c',code],text=True,
                                    cwd=Path(__file__).resolve().parent.parent))
    try:os.kill(pid,0)
    except ProcessLookupError:pass
    else:raise AssertionError('Player survived parent exit')
    print('OK: silent tests, Tk destruction, kill/reap fallback and exit cleanup')


if __name__=='__main__':main()
