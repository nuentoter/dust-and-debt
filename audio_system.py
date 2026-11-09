"""Audio event router for future Dust & Debt music and sound effects.

The core game publishes semantic cues here without depending on any playback
library. Currently a gated Tk system-bell fallback is available. This module
does NOT decode or play audio samples and does not promise a soundtrack.
"""
import time

CUES = frozenset((
    "gunshot", "reload", "lasso", "hogtie", "bounty_complete",
    "arrest", "job_accept", "job_complete", "purchase", "horse",
    "door", "weather_rain", "weather_dust", "menu",
))
MUSIC_STATES = frozenset(("title", "town", "wilderness", "combat", "interior", "night", "silence"))

class AudioDirector:
    def __init__(self, bell=None, clock=None):
        self.bell = bell
        self.clock = clock or time.monotonic
        self.enabled = False
        self.music_enabled = False
        self.master_volume = 0.7
        self.music_volume = 0.55
        self.effects_volume = 0.8
        self.music_state = "silence"
        self.last_event = None
        self.last_bell = -1e9
        self.backend = "bell" if bell else "none"

    def cue(self, event):
        if event not in CUES:return False
        self.last_event=event
        if not self.enabled or not self.bell:return False
        now=self.clock()
        if now-self.last_bell<.35:return False
        self.last_bell=now
        try:self.bell()
        except Exception:return False
        return True

    def set_music_state(self, state):
        if state not in MUSIC_STATES:return False
        if self.music_state==state:return False
        self.music_state=state
        # Future sample/streaming backends will implement transitions here.
        return True

    def settings(self):
        return {"enabled":self.enabled,"music_enabled":self.music_enabled,
                "master_volume":self.master_volume,"music_volume":self.music_volume,
                "effects_volume":self.effects_volume}

    def configure(self, data):
        if not isinstance(data,dict):return
        self.enabled=bool(data.get("enabled",self.enabled))
        self.music_enabled=bool(data.get("music_enabled",self.music_enabled))
        for name in ("master_volume","music_volume","effects_volume"):
            try:value=float(data.get(name,getattr(self,name)))
            except (TypeError,ValueError):continue
            setattr(self,name,max(0.,min(1.,value)))
