#!/usr/bin/env python3
"""Optional asset regeneration; game itself uses no third-party Python libraries."""
from PIL import Image, ImageDraw, ImageFont
import random, math, os
ROOT=os.path.join(os.path.dirname(__file__),'assets')
os.makedirs(ROOT,exist_ok=True)
r=random.Random(1889)
W,H=2400,1600
im=Image.new('RGB',(W,H),'#c8a06d');d=ImageDraw.Draw(im)
# Broad terrains, scrubland bands and tracks
for i in range(4800):
 x=r.randrange(W);y=r.randrange(H)
 co=r.choice(['#cca775','#d0a979','#c29a67','#b99464','#c6a171','#c9a374'])
 s=r.randrange(2,15)
 d.rectangle((x,y,x+s,y+r.randrange(1,5)), fill=co)
for j in range(130):
 x=r.randrange(W);y=r.randrange(H);s=r.randrange(18,110)
 d.ellipse((x-s,y-s//2,x+s,y+s//2),fill=r.choice(['#c59b6a','#c9a06c','#bfa06c','#c5a174']))
# Roads, railway, town plaza
for offset in range(-44,45,7):
 d.line([(0,570+offset),(2350,570+offset)],fill='#a67d52',width=6)
 d.line([(640+offset,-20),(680+offset,1620)],fill='#a67d52',width=6)
for offset in range(-18,19,9):
 d.line([(640,570+offset),(1830,430+offset)],fill='#b48a59',width=8)
 d.line([(650,580+offset),(2020,1240+offset)],fill='#b48a59',width=7)
# Railway at south
for y in (1414,1427): d.line((0,y,W,y),fill='#554a3c',width=4)
for x in range(0,W,22):d.line((x,1407,x+4,1434),fill='#786045',width=7)
# Geological motifs
for i in range(65):
 x=r.randrange(W);y=r.randrange(H)
 if 290<x<1110 and 285<y<920:continue
 w=r.randrange(18,60);h=r.randrange(10,35)
 d.ellipse((x,y,x+w,y+h),fill='#af855c',outline='#a07750',width=3)
 d.arc((x+6,y+2,x+w-6,y+h-4),0,170,fill='#d1ab78',width=2)
# Cactus, scrub, flowers
for i in range(660):
 x=r.randrange(15,W-15);y=r.randrange(15,H-15)
 if (300<x<1090 and 240<y<960) or abs(y-570)<72 or abs(x-670)<70:continue
 k=r.random()
 if k<.18:
  d.ellipse((x-12,y-2,x+13,y+8),fill='#a98758')
  d.line((x,y+2,x,y-24),fill='#54754b',width=5)
  d.line((x,y-10,x-9,y-14,x-9,y-23),fill='#54754b',width=4)
  d.line((x,y-15,x+8,y-17,x+8,y-29),fill='#54754b',width=4)
  d.line((x,y-24,x,y-27),fill='#95a574',width=2)
 elif k<.55:
  d.line((x-11,y+3,x-2,y-4,x+9,y+3),fill='#8c8552',width=2)
  d.line((x-7,y+5,x-4,y-7,x+4,y+5),fill='#868b53',width=2)
 else:
  d.ellipse((x-4,y-2,x+5,y+2),fill=r.choice(['#b58e5c','#d8ac78','#a68555']))
# Buildings with southwest shadows and evocative roofs
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
try:font=ImageFont.truetype(fontpath,14);small=ImageFont.truetype(fontpath,11)
except:font=ImageFont.load_default();small=font
BUILDINGS=[
 ('SHERIFF',320,300,196,130,'#6d6556'),('SALOON',565,315,238,160,'#8a5141'),
 ('GENERAL STORE',854,318,204,144,'#84724e'),('DOCTOR',320,694,169,120,'#a08266'),
 ('STABLE',835,728,210,144,'#66583f'),('HOTEL',540,735,215,168,'#7d6656'),
 ('STATION',1150,1321,240,115,'#765e4a'),('CABIN',1670,320,140,110,'#74644c'),
 ('OUTPOST',1960,1150,140,100,'#795443'),('RANCH',1470,850,160,125,'#745f45')]
for name,x,y,w,h,color in BUILDINGS:
 d.rounded_rectangle((x+11,y+14,x+w+11,y+h+14),radius=4,fill='#9e7e54')
 d.rectangle((x,y,x+w,y+h),fill='#483b31',outline='#302d29',width=4)
 d.rectangle((x+7,y+7,x+w-7,y+h-7),fill=color)
 for yy in range(y+20,y+h-6,26):d.line((x+10,yy,x+w-10,yy),fill='#4f493d',width=2)
 d.rectangle((x+9,y+9,x+w-9,y+37),fill='#52443b')
 bb=d.textbbox((0,0),name,font=font);tw=bb[2]-bb[0]
 d.text((x+(w-tw)//2,y+15),name,font=font,fill='#f7dfab',stroke_width=1,stroke_fill='#362b21')
 d.rectangle((x+w//2-15,y+h-26,x+w//2+15,y+h),fill='#3a3029')
 for xx in [x+25,x+w-45]:
  d.rectangle((xx,y+54,xx+22,y+78),fill='#c9b77a',outline='#3f3027',width=3)
# Camp boundary, signs, fire and burned out wagon
for cx,cy in [(1840,480),(2040,1280)]:
 d.ellipse((cx-115,cy-82,cx+115,cy+80),outline='#8a744c',width=5)
 for xx,yy in [(-70,-30),(60,-34),(-40,55)]:
  x=cx+xx;y=cy+yy
  d.polygon((x-29,y+18,x,y-24,x+30,y+18),fill='#706850',outline='#453c33')
  d.line((x-29,y+18,x+30,y+18),fill='#403c31',width=3)
 d.ellipse((cx-12,cy-3,cx+16,cy+17),fill='#5b4839')
 d.polygon((cx-6,cy+10,cx,cy-17,cx+10,cy+9),fill='#df8b40')
 d.polygon((cx-1,cy+8,cx+3,cy-9,cx+6,cy+9),fill='#f6d16e')
# Forest oasis in north-west
for i in range(40):
 x=r.randrange(90,270);y=r.randrange(75,410)
 d.ellipse((x-15,y-4,x+19,y+13),fill='#a08355')
 d.rectangle((x-3,y-30,x+4,y+2),fill='#66533e')
 for k in range(3):
  rad=23-k*4
  d.ellipse((x-rad,y-47+k*12,x+rad,y-10+k*10),fill=['#536347','#617047','#72804e'][k],outline='#46563e',width=2)
# Written place and location details
labels=[('CINDER CREEK',505,240),('THE RED MESA',1820,210),('DUST HOLLOW',1745,600),('THE DRY FLATS',1320,1175),('BLACKSPUR OUTPOST',1880,1380),('IRON HORSE RAILROAD',90,1450)]
for t,x,y in labels:
 d.text((x,y),t,fill='#785d42',font=font,stroke_width=1,stroke_fill='#d3ae7b')
im.save(os.path.join(ROOT,'world.png'),optimize=True)
# Title background, poster and UI texture
p=Image.new('RGB',(960,600),'#261d18');pd=ImageDraw.Draw(p)
for y in range(600):
 rr=int(30+45*y/600);gg=int(24+22*y/600);bb=int(24+10*y/600)
 pd.line((0,y,960,y),fill=(rr,gg,bb))
pd.ellipse((645,72,870,297),fill='#e7a364')
for i in range(17):
 x=i*76-40
 pd.polygon((x,380,x+110,220+r.randrange(80),x+210,382),fill='#49352e')
pd.rectangle((0,385,960,600),fill='#271f1b')
for x in range(40,960,190):
 pd.line((x,355,x,500),fill='#171612',width=8)
 pd.line((x-20,395,x+18,395),fill='#171612',width=7)
for i in range(110):
 x=r.randrange(960);y=r.randrange(425,600)
 pd.line((x,y,x+13,y-7),fill='#58402e',width=2)
p.save(os.path.join(ROOT,'title.png'),optimize=True)
print('Generated original western pixel-art assets.')
