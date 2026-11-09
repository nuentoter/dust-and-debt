"""Horse riding model for low-spec top-down Dust & Debt.

Time-based movement, acceleration and stamina require no extra dependencies.
Horse condition (care) remains separate from momentary gallop stamina.
"""
import math

TROT_SPEED=308.0         # 1.5x previous 205 mounted walk
GALLOP_SPEED=650.0       # 2.5x previous 260 mounted sprint
ACCELERATION=4.8
TURN_RATE=7.5
STAMINA_DRAIN=23.0
STAMINA_RECOVERY=14.0
EXHAUSTED_RECOVERY=20.0

def step_motion(state,dx,dy,dt,wants_gallop,condition):
    """Advance a horse-motion dict; return (vx,vy,actual_galloping)."""
    dt=max(0.,min(float(dt),.15))
    stamina=max(0.,min(100.,float(state.get('stamina',100.))))
    speed=max(0.,float(state.get('speed',0.)))
    heading_x=float(state.get('heading_x',0.))
    heading_y=float(state.get('heading_y',-1.))
    length=math.hypot(dx,dy)
    moving=length>.001
    exhausted=bool(state.get('exhausted',False))
    if exhausted and stamina>=28:exhausted=False
    if stamina<=.01:exhausted=True
    gallop=bool(wants_gallop and moving and not exhausted and stamina>0.)
    if gallop:
        stamina=max(0.,stamina-STAMINA_DRAIN*dt)
        if stamina<=0:exhausted=True
    else:
        stamina=min(100.,stamina+(EXHAUSTED_RECOVERY if not moving else STAMINA_RECOVERY)*dt)
    health=max(0.,min(100.,float(condition)))
    modifier=.7 if health<20 else .86 if health<50 else 1.
    target=(GALLOP_SPEED if gallop else TROT_SPEED)*modifier if moving else 0.
    blend=1-math.exp(-ACCELERATION*dt)
    speed+=(target-speed)*blend
    if moving:
        dx/=length;dy/=length
        turn=1-math.exp(-TURN_RATE*dt)
        heading_x+=(dx-heading_x)*turn
        heading_y+=(dy-heading_y)*turn
        mag=math.hypot(heading_x,heading_y)
        if mag>.0001:heading_x/=mag;heading_y/=mag
    else:
        # No ghost movement after releasing controls; the speed meter eases to zero.
        speed=0.
    state.update(stamina=stamina,speed=speed,heading_x=heading_x,
                 heading_y=heading_y,exhausted=exhausted)
    return (heading_x*speed if moving else 0.,
            heading_y*speed if moving else 0.,gallop)
