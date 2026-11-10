"""Original, procedural instrumental Western score for Dust & Debt.

Generates small cached PCM WAV loops using only the Python standard library.
These are original composed melodic cues, not recordings or third-party songs.
The user's future recorded title track can override title.wav/m4a/ogg/mp3.
"""
import math
import os
import random
import struct
import wave

RATE=11025
SCORE_VERSION="score_v1"
# Semitones relative to A3 (220 Hz); None is a rest.
# Four bar phrases, composed specifically for six in-game scenes.
SCORES={
 "title":{
  "tempo":88, "root":-2, "mode":"minor",
  "melody":(0,None,3,5,7,5,3,None,0,None,-2,0,3,0,-2,None,
            0,3,5,7,10,7,5,3,0,None,-2,0,-2,None,None,None),
  "chords":((0,3,7),(-2,2,5),(-5,0,3),(-2,2,5)),
  "bright":.76},
 "wilderness":{
  "tempo":92,"root":0,"mode":"major",
  "melody":(0,2,4,None,7,None,4,2,0,None,4,7,9,7,4,None,
            5,4,2,0,-3,None,0,2,4,None,2,0,None,None,None,None),
  "chords":((0,4,7),(-3,0,4),(5,9,12),(0,4,7)),
  "bright":.90},
 "town":{
  "tempo":106,"root":-3,"mode":"major",
  "melody":(0,4,7,4,0,None,-3,None,2,5,9,5,2,0,None,None,
            4,7,9,7,4,2,0,None,0,2,4,0,-3,None,None,None),
  "chords":((0,4,7),(5,9,12),(-3,0,4),(0,4,7)),
  "bright":1.},
 "night":{
  "tempo":72,"root":-5,"mode":"minor",
  "melody":(0,None,3,None,7,5,3,None,0,None,-2,None,0,None,None,None,
            3,None,5,7,5,None,0,None,-2,None,0,None,None,None,None,None),
  "chords":((0,3,7),(-5,0,3),(-2,2,5),(0,3,7)),
  "bright":.58},
 "interior":{
  "tempo":96,"root":-1,"mode":"major",
  "melody":(0,4,None,7,4,None,2,None,0,2,4,None,0,None,None,None,
            -3,0,4,None,2,0,-3,None,0,None,4,2,0,None,None,None),
  "chords":((0,4,7),(-3,0,4),(5,9,12),(0,4,7)),
  "bright":.66},
 "combat":{
  "tempo":132,"root":-7,"mode":"minor",
  "melody":(0,0,None,3,5,None,3,0,0,None,-2,0,3,None,5,7,
            7,5,3,0,None,0,-2,0,3,5,7,5,3,None,0,None),
  "chords":((0,3,7),(-2,2,5),(-5,0,3),(-2,2,5)),
  "bright":.93},
}

def _pitch(semitones):
 return 220.0*2**(semitones/12.0)

def _pluck(t,frequency,decay=3.4):
 if t<0:return 0.
 # A picked-string sound: decaying fundamental + upper harmonics.
 env=(1.-math.exp(-36*t))*math.exp(-decay*t)
 phase=2*math.pi*frequency*t
 return env*(.58*math.sin(phase)+.27*math.sin(2*phase)+.15*math.sin(3*phase))

def _reed(t,frequency):
 if t<0:return 0.
 env=min(1.,t*13)
 phase=2*math.pi*frequency*t
 vibrato=.022*math.sin(t*2*math.pi*4.7)
 return env*(.72*math.sin(phase+vibrato)+.19*math.sin(2*phase)+.09*math.sin(3*phase))

def _score_pcm(state):
 cfg=SCORES[state]
 beat=60.0/cfg["tempo"]
 eighth=beat/2
 steps=cfg["melody"]
 duration=len(steps)*eighth
 root=cfg["root"]
 # Precompute sparse instruments rather than building a giant mixing buffer.
 notes=[]
 for i,step in enumerate(steps):
  if step is not None:
   notes.append((i*eighth,_pitch(root+step+12),.23 if i%8==0 else .19))
 # Chords on each two-beat grouping; arpeggiate for a frontier-guitar feel.
 for chord_i,chord in enumerate(cfg["chords"]*2):
  start=chord_i*4*eighth
  for j,semitone in enumerate(chord):
   notes.append((start+j*eighth*.72,_pitch(root+semitone),.082))
 low=[(i*beat*2,_pitch(root+chord[0]-12)) for i,chord in enumerate(cfg["chords"]*2)]
 rng=random.Random(1898+sum(ord(c) for c in state))
 pcm=bytearray()
 for index in range(int(duration*RATE)):
  t=index/RATE
  step_i=min(len(steps)-1,int(t/eighth))
  signal=0.
  # Only events near the current time contribute; cap polyphony cheaply.
  for start,frequency,level in notes:
   elapsed=t-start
   if 0<=elapsed<.92:
    signal+=level*_pluck(elapsed,frequency)
  for start,frequency in low:
   dt=t-start
   if 0<=dt<1.2:signal+=.16*_pluck(dt,frequency,1.5)
  # Whistled/harmonica-like long line at select phrase starts.
  if state in ("title","night","wilderness","interior"):
   phrase_start=(step_i//8)*8*eighth
   phrase_note=steps[(step_i//8)*8]
   if phrase_note is not None:
    dt=t-phrase_start
    if 0<=dt<3.5*eighth:
     tail=min(1.,(3.5*eighth-dt)*3)
     signal+=.07*cfg["bright"]*tail*_reed(dt,_pitch(root+phrase_note+24))
  # Muted brush / hoof pulse with sparse deterministic transient noise.
  beat_phase=t%beat
  if beat_phase<.065:
   strength=.045 if state in ("title","wilderness","town") else (.080 if state=="combat" else .020)
   signal+=strength*rng.uniform(-1.,1.)*math.exp(-45*beat_phase)
  # Low stable air/wind texture.
  signal+=.009*math.sin(2*math.pi*36.7*t)
  fade=min(1.,t/.22,(duration-t)/.30)
  signal*=max(0.,fade)*.85
  pcm+=struct.pack('<h',int(max(-.95,min(.95,signal))*32767))
 return pcm

def ensure_score(cache_root,state):
 if state not in SCORES:return None
 folder=os.path.join(cache_root,SCORE_VERSION)
 path=os.path.join(folder,state+".wav")
 if os.path.isfile(path) and os.path.getsize(path)>RATE*8:return path
 os.makedirs(folder,exist_ok=True)
 tmp=path+".tmp"
 try:
  with wave.open(tmp,"wb") as out:
   out.setnchannels(1);out.setsampwidth(2);out.setframerate(RATE)
   out.writeframes(_score_pcm(state))
  os.replace(tmp,path)
 except Exception:
  try:os.unlink(tmp)
  except OSError:pass
  raise
 return path
