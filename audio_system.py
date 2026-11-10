"""Linux audio playback for the creator's original Dust & Debt M4A tracks.

Only the sound effects are synthesized. Music is drawn exclusively from the
creator's actual recordings in assets/audio/music, never generated substitutes.
FFplay or mpv supports M4A/MP3/OGG; pw-play/aplay can play original WAVs.
The selected scene playlist rotates as songs finish without blocking Tkinter.
"""
import atexit,os,shutil,subprocess,time
from audio_assets import ensure_wav
from soundtrack_manifest import tracks_for,installed_count

CUES = frozenset((
    "gunshot", "reload", "lasso", "hogtie", "bounty_complete",
    "arrest", "job_accept", "job_complete", "purchase", "horse",
    "door", "weather_rain", "weather_dust", "menu",
))
MUSIC_STATES = frozenset(("title", "town", "wilderness", "combat", "interior", "night", "silence"))

class AudioDirector:
    def __init__(self, bell=None, clock=None, assets_path=None, cache_path=None):
        self.bell=bell
        self.clock=clock or time.monotonic
        self.assets_path=assets_path
        self.cache_path=cache_path or os.path.join(os.path.expanduser("~"),".cache","dust-and-debt","audio")
        self.player=None
        self.backend="bell" if bell else "none"
        if assets_path:
            for candidate in ("ffplay","mpv","pw-play","aplay"):
                result=shutil.which(candidate)
                if result:
                    self.player=result
                    self.backend=candidate
                    break
        self.enabled=False
        self.music_enabled=False
        self.master_volume=.7
        self.music_volume=.55
        self.effects_volume=.8
        self.music_state="silence"
        self.last_event=None
        self.last_bell=-1e9
        self.music_process=None
        self.effects=[]
        self.playlist_index={state:0 for state in MUSIC_STATES}
        self._music_retry_at=0.
        atexit.register(self.stop)

    def _run(self,file,volume,loop=False):
        if os.environ.get("DUST_AND_DEBT_SILENT")=="1":return None
        if not self.player or not file:return None
        value=int(100*max(0.,min(1.,volume)))
        if value<=0:return None
        if self.backend=="ffplay":
            args=[self.player,"-nodisp","-loglevel","quiet","-nostats",
                  "-volume",str(value)]
            if loop:args+=["-stream_loop","-1"]
            args+=["-autoexit",file]
        elif self.backend=="mpv":
            args=[self.player,"--no-config","--no-video","--really-quiet",
                  "--volume="+str(value)]
            if loop:args+=["--loop-file=inf"]
            args.append(file)
        elif self.backend=="pw-play":
            if os.path.splitext(file)[1].lower()!=".wav":return None
            args=[self.player,"--volume",str(round(value/100,3)),file]
        else:  # aplay: WAV-only, ALSA handles output routing
            if os.path.splitext(file)[1].lower()!=".wav":return None
            args=[self.player,"-q",file]
        try:
            return subprocess.Popen(args,stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                                    start_new_session=True)
        except (OSError,ValueError):
            return None

    def cue(self,event):
        if event not in CUES:return False
        self.last_event=event
        if not self.enabled or os.environ.get("DUST_AND_DEBT_SILENT")=="1":return False
        now=self.clock()
        if now-self.last_bell<.14:return False
        self.last_bell=now
        if self.player:
            self.effects=[p for p in self.effects if p.poll() is None]
            if len(self.effects)<4:
                try:
                    file=self._effect_file(event)
                    proc=self._run(file,self.master_volume*self.effects_volume)
                    if proc:
                        self.effects.append(proc)
                        return True
                except (OSError,ValueError):pass
        if not self.bell:return False
        if now-getattr(self,"last_fallback_bell",-1e9)<.35:return False
        self.last_fallback_bell=now
        try:self.bell()
        except Exception:return False
        return True

    def _effect_file(self,event):
        if not self.assets_path:return None
        folder=os.path.join(self.assets_path,"sfx")
        for ext in (".wav",".ogg",".mp3"):
            path=os.path.join(folder,event+ext)
            if os.path.isfile(path):return path
        return ensure_wav(self.cache_path,"sfx",event)

    def _music_file(self,state):
        if not self.assets_path or state=="silence":return None
        folder=os.path.join(self.assets_path,"music")
        extensions=(".wav",) if self.backend in ("pw-play","aplay") else (".m4a",".mp3",".ogg",".wav")
        # Explicit state-name overrides still work for renamed custom tracks.
        for ext in extensions:
            path=os.path.join(folder,state+ext)
            if os.path.isfile(path):return path
        recordings=tracks_for(state,folder)
        if self.backend in ("pw-play","aplay"):
            recordings=tuple(p for p in recordings if p.lower().endswith(".wav"))
        if not recordings:return None
        return recordings[self.playlist_index[state]%len(recordings)]

    def set_music_state(self,state):
        if state not in MUSIC_STATES:return False
        if self.music_state==state:return False
        self.music_state=state
        self._music_retry_at=0.
        self.refresh_music()
        return True

    def set_music_enabled(self,enabled):
        self.music_enabled=bool(enabled)
        self.refresh_music()

    def refresh_music(self):
        self._stop_music()
        self._music_retry_at=0.
        self._start_music()

    def _start_music(self):
        if not self.music_enabled or not self.player or self.music_state=="silence":return
        try:file=self._music_file(self.music_state)
        except (OSError,ValueError):file=None
        if not file:return
        # Do not infinite-loop a single song: advance after it finishes.
        self.music_process=self._run(file,self.master_volume*self.music_volume,False)
        if self.music_process is None:self._music_retry_at=self.clock()+5.

    def service(self):
        """Advance original soundtrack on track completion without blocking Tk."""
        if not self.music_enabled or not self.player or self.music_state=="silence":return
        if self.music_process and self.music_process.poll() is None:return
        if self.clock()<self._music_retry_at:return
        if self.music_process:
            self.music_process=None
            self.playlist_index[self.music_state]+=1
        self._start_music()

    def soundtrack_count(self):
        """Number of known original recordings currently installed."""
        if not self.assets_path:return 0
        return installed_count(os.path.join(self.assets_path,"music"))

    @staticmethod
    def _stop_process(proc):
        if proc is None:return
        try:
            if proc.poll() is None:proc.terminate()
            proc.wait(timeout=.2)
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
                proc.wait(timeout=.2)
            except (OSError,subprocess.TimeoutExpired):pass
        except OSError:pass

    def _stop_music(self):
        proc=self.music_process
        self.music_process=None
        self._stop_process(proc)

    def stop(self):
        self._stop_music()
        for proc in self.effects:self._stop_process(proc)
        self.effects=[]

    def settings(self):
        return {"enabled":self.enabled,"music_enabled":self.music_enabled,
                "master_volume":self.master_volume,"music_volume":self.music_volume,
                "effects_volume":self.effects_volume}

    def configure(self,data):
        if not isinstance(data,dict):return
        self.enabled=bool(data.get("enabled",self.enabled))
        enabled=bool(data.get("music_enabled",self.music_enabled))
        for name in ("master_volume","music_volume","effects_volume"):
            try:value=float(data.get(name,getattr(self,name)))
            except (TypeError,ValueError):continue
            setattr(self,name,max(0.,min(1.,value)))
        self.set_music_enabled(enabled)
