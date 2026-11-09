"""Procedural original (not sampled or copyrighted) sounds for optional game audio.

Creates small PCM WAV files lazily in the local cache, never in the repository.
No MIDI, ffmpeg-python, NumPy, or pip packages. These are *background texture*
and utility effects, not a substitute for the game's supplied title theme.
"""
import math,os,random,wave,struct

RATE=11025
SFX_LENGTH={"gunshot":.34,"reload":.20,"lasso":.38,"hogtie":.24,
            "bounty_complete":.65,"arrest":.55,"job_accept":.52,
            "job_complete":.65,"purchase":.25,"horse":.55,
            "door":.32,"weather_rain":1.4,"weather_dust":1.2,"menu":.13}
AMBIENCE_STATES=("wilderness","night","town","combat","interior")

def destination(cache_root,kind,name):
 if kind=='sfx':
  if name not in SFX_LENGTH:return None
  return os.path.join(cache_root,"sfx",name+".wav")
 if kind=='music':
  if name not in AMBIENCE_STATES:return None
  return os.path.join(cache_root,"music",name+".wav")
 return None

def _sfx(name):
 duration=SFX_LENGTH[name]
 rng=random.Random(sum(ord(c)*37 for c in name))
 samples=[]
 for i in range(int(RATE*duration)):
  t=i/RATE;u=t/duration
  noise=rng.uniform(-1,1)
  if name=="gunshot":
   signal=(.86*noise+.14*math.sin(2*math.pi*(98-55*u)*t))*math.exp(-17*u)
  elif name=="reload":
   signal=(.55*math.sin(2*math.pi*1370*t)+.3*noise)*max(0.,1-abs((u-.24)/.19)) + (.28*noise)*max(0.,1-abs((u-.79)/.12))
  elif name=="lasso":
   signal=.4*math.sin(2*math.pi*(440+780*u)*t)*math.sin(math.pi*u)+.13*noise*(1-u)
  elif name=="hogtie":
   signal=(.21*noise+.26*math.sin(2*math.pi*190*t))*(1-u)
  elif name in ("purchase","menu","job_accept","job_complete","bounty_complete","arrest"):
   notes={"purchase":(720,1030),"menu":(570,),
          "job_accept":(420,560),"job_complete":(440,660,880),
          "bounty_complete":(330,495,660),"arrest":(375,560)}[name]
   note=min(len(notes)-1,int(u*len(notes)))
   env=(1-math.exp(-30*t))*math.exp(-4*(u*len(notes)%1))
   signal=.26*math.sin(2*math.pi*notes[note]*t)*env
  elif name=="horse":
   signal=.46*noise*max(0,math.sin(2*math.pi*4.2*t))**7*(1-u)
  elif name=="door":
   signal=(.26*math.sin(2*math.pi*(115-40*u)*t)+.25*noise)*math.exp(-5*u)
  else:
   signal=(.12 if name=="weather_rain" else .2)*noise*(.3+.7*math.sin(math.pi*u))
  samples.append(max(-1.,min(1.,signal)))
 return samples

def _ambient(state):
 duration=9.0
 root={"wilderness":110,"night":82.4,"town":146.8,"combat":73.4,"interior":130.8}[state]
 amplitude={"combat":.16,"town":.13,"interior":.09,"night":.12,"wilderness":.12}[state]
 rng=random.Random(len(state)*984)
 samples=[]
 # Low rumbling, near-stationary drones and sparse pulses; not a MIDI score.
 for i in range(int(RATE*duration)):
  t=i/RATE
  u=t/duration
  slow=.65+.35*math.sin(2*math.pi*t/duration)
  chord=(.46*math.sin(2*math.pi*root*t)+
         .24*math.sin(2*math.pi*root*1.5*t)+
         .17*math.sin(2*math.pi*root*.5*t))
  earth=.1*math.sin(2*math.pi*36.7*t)
  wind=.08*rng.uniform(-1,1)*(math.sin(2*math.pi*t/3)**2)
  pulse=0.
  if state=="combat":
   beat=t%1.5
   pulse=.21*rng.uniform(-1,1)*math.exp(-20*beat)
  signal=amplitude*(chord*slow+earth+wind+pulse)
  envelope=min(1.,t/.24,(duration-t)/.24)
  samples.append(max(-1.,min(1.,signal))*max(0.,envelope))
 return samples

def ensure_wav(cache_root,kind,name):
 path=destination(cache_root,kind,name)
 if not path:return None
 if os.path.isfile(path) and os.path.getsize(path)>44:return path
 os.makedirs(os.path.dirname(path),exist_ok=True)
 # Avoid partially written caches (e.g., power loss during startup).
 temp=path+".tmp"
 samples=_sfx(name) if kind=="sfx" else _ambient(name)
 with wave.open(temp,'wb') as stream:
  stream.setnchannels(1);stream.setsampwidth(2);stream.setframerate(RATE)
  stream.writeframes(b''.join(struct.pack('<h',int(max(-1.,min(1.,v))*32760)) for v in samples))
 os.replace(temp,path)
 return path
