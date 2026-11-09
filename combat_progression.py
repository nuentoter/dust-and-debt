"""Lightweight v2.8 combat choices. Pure helpers keep rules independently testable."""
import math

WEAPONS={
    "peacemaker":{"label":"COLT PEACEMAKER","capacity":6,"damage":52,"cooldown":.25,"reload":1.15,"velocity":710},
    "marshal":{"label":"MARSHAL'S IRON","capacity":5,"damage":68,"cooldown":.39,"reload":1.65,"velocity":760},
}
DIFFICULTIES={"trail":.65,"standard":1.0,"hard":1.4}

def available_weapons(arrests=0,work=0,kills=0):
    """Earn the second revolver without requiring purchases or outlaw conduct."""
    earned=(arrests>=2 or work>=4 or kills>=10)
    return ("peacemaker","marshal") if earned else ("peacemaker",)

def normal_weapon(value,arrests=0,work=0,kills=0):
    return value if value in available_weapons(arrests,work,kills) else "peacemaker"

def normal_difficulty(value):
    return value if value in DIFFICULTIES else "standard"

def incoming_damage(value,base):
    return max(1,round(base*DIFFICULTIES[normal_difficulty(value)]))

def aim_vector(dx,dy,actors,x,y,assist=False,range_limit=430):
    """Mild aim correction, hostile standing actors only; does not shoot through walls."""
    magnitude=math.hypot(dx,dy)
    if magnitude<.001:return (0.,-1.)
    ux,uy=dx/magnitude,dy/magnitude
    if not assist:return ux,uy
    best=None
    for a in actors:
        if a.dead or not (a.kind in ("bandit","bounty_target","deputy") or a.kind.startswith("mission_")):continue
        vx,vy=a.x-x,a.y-y
        dist=math.hypot(vx,vy)
        if not 25<dist<range_limit:continue
        dot=(vx*ux+vy*uy)/dist
        if dot<.986:continue # only about 9.6 degrees from deliberate aim
        score=(1-dot)*3+dist/2500
        if best is None or score<best[0]:best=(score,vx/dist,vy/dist)
    return (best[1],best[2]) if best else (ux,uy)

def earned_perks(arrests=0,work=0,kills=0):
    """Automatic, permanent-by-achievement perks; counters already persist."""
    perks=[]
    if arrests>=3:perks.append("steady_nerve")
    if work>=6:perks.append("trail_grit")
    if kills>=12:perks.append("quick_hands")
    return tuple(perks)

def perk_reload_multiplier(perks):
    return .90 if "quick_hands" in perks else 1.0

def perk_incoming_multiplier(perks):
    return .90 if "steady_nerve" in perks else 1.0

def perk_deadeye_regen(perks):
    return 14. if "trail_grit" in perks else 11.
