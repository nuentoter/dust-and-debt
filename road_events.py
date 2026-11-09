"""Deterministic content for the 60,000x40,960 Great Territory.

Cross-country contracts use named waystations and landmark coordinates.
No large terrain assets, network requests, or extra runtime dependencies.
"""
import math
from frontier_world import WAYSTATIONS, LANDMARKS, region_at, road_at

EVENT_TYPES=("escort","courier","salvage","survey")
EVENT_PAY={"escort":75,"courier":48,"salvage":38,"survey":42}
EVENT_TITLES={"escort":"Safe Passage","courier":"The Sealed Letter",
              "salvage":"The Missing Freight","survey":"Trail Survey"}
REGIONAL_RUMORS=(
 "Railway hands say the eastbound freight has gone missing.",
 "The old crossing has been watched by men with no badges.",
 "The night wind carries bell sounds from the abandoned mine.",
 "An injured traveler was spotted beyond the last water stop.",
 "A deputy was asking about wagon tracks near the ridge.",
 "A sealed message was due here three days ago.",
)

def distance(a,b):
 return math.hypot(a[0]-b[0],a[1]-b[1])

def nearby_station(x,y,radius=220):
 return next((s for s in WAYSTATIONS if math.hypot(s[2]-x,s[3]-y)<=radius),None)

def nearest_landmark(x,y):
 return min(LANDMARKS,key=lambda lm:math.hypot(lm[2]-x,lm[3]-y))

def next_station(key):
 idx=next((i for i,s in enumerate(WAYSTATIONS) if s[0]==key),None)
 if idx is None:return None
 return WAYSTATIONS[(idx+1)%len(WAYSTATIONS)]

def mission_offer(key,kind,day=0):
 source=next((s for s in WAYSTATIONS if s[0]==key),None)
 if not source or kind not in EVENT_TYPES:return None
 _,name,sx,sy=source
 if kind in ("escort","courier"):
  target=next_station(key)
  tx,ty=target[2],target[3]
  location_name=target[1]
 else:
  lm=nearest_landmark(sx,sy)
  tx,ty=lm[2],lm[3]
  location_name=lm[1]
 reward=EVENT_PAY[kind]
 # Long escorts pay more; never charge more than players can earn.
 if kind=="escort":reward+=min(55,int(distance((sx,sy),(tx,ty))//2000)*5)
 return {"type":kind,"title":EVENT_TITLES[kind],"origin":key,
         "origin_name":name,"origin_pos":[sx,sy],
         "target_pos":[tx,ty],"destination":location_name,
         "reward":reward,"status":"outbound","day":int(day)}

def offer_for_day(key,day):
 idx=next((i for i,s in enumerate(WAYSTATIONS) if s[0]==key),None)
 if idx is None:return None
 # Rotate contracts so a station has something different on subsequent days.
 kind=EVENT_TYPES[(idx+int(day))%len(EVENT_TYPES)]
 return mission_offer(key,kind,day)

def dispatch_rumor(x,y,day):
 row,col=(int(y//10240),int(x//10000))
 idx=(row*7+col*3+int(day))%len(REGIONAL_RUMORS)
 return REGIONAL_RUMORS[idx]

def safe_event_position(x,y,can_move):
 # Keep the core position of the landmark/station for visual map fidelity.
 if can_move(x,y,20):return (x,y)
 for radius in (50,100,150,225,300):
  for dx,dy in ((radius,0),(-radius,0),(0,radius),(0,-radius),
                (radius,radius),(-radius,radius),(radius,-radius),(-radius,-radius)):
   px,py=x+dx,y+dy
   if can_move(px,py,20):return (px,py)
 return None
