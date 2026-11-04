#!/usr/bin/env python3
"""Build the expanded original Western territory. Pillow needed only to regenerate art."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import random, math
ROOT=Path(__file__).parent/'assets'
R=random.Random(462189)
W,H=4800,3200
old=Image.open(ROOT/'world_original.png') if (ROOT/'world_original.png').exists() else Image.open(ROOT/'world.png')
if old.size!=(2400,1600):
 raise SystemExit('The original 2400x1600 artwork must be kept as assets/world_original.png')
canvas=Image.new('RGB',(W,H),'#c7a06d');d=ImageDraw.Draw(canvas)
# Broad region textures and earthy gradients, generated deterministically.
for y in range(0,H,8):
 for x in range(0,W,8):
  if x<2400 and y<1600: continue
  n=R.randrange(-9,10); dry=(x>3000 and y<2000); green=(y>2000 and x<2200)
  base=(190,151,101) if dry else ((150,157,111) if green else (188,157,109))
  d.rectangle((x,y,x+8,y+8),fill=tuple(max(0,min(255,a+n)) for a in base))
for _ in range(18500):
 x=R.randrange(W); y=R.randrange(H)
 if x<2400 and y<1600:continue
 s=R.randrange(3,24)
 d.line((x,y,x+s,y+R.randrange(-4,5)),fill=R.choice(['#d0b17d','#b18c62','#ac905e','#bca272','#bd9965']),width=R.randrange(1,4))
# World geographic identity: northwest snow-brushed highlands, northeast mesa, southern greener basin.
for x,y,rx,ry in [(3620,600,540,380),(4100,950,690,570),(3180,350,360,270),(2400,2700,490,300),(3850,2650,510,350)]:
 for n in range(8,0,-1):
  scale=n/8
  color=['#735e4d','#846b55','#94775b','#9c805f','#ad8d63','#bc9a6e','#c4a679','#c8a779'][8-n]
  d.ellipse((x-rx*scale,y-ry*scale,x+rx*scale,y+ry*scale),outline=color,width=18)
# River runs from northern central edge into southwest basin, and Silverwater lake.
river=[(2790,-50),(2690,240),(2770,610),(2620,960),(2710,1350),(2580,1660),(2470,1910),(2270,2200),(1990,2480),(1730,2750),(1530,3300)]
d.line(river,fill='#a6a77d',width=164,joint='curve')
d.line(river,fill='#648e91',width=112,joint='curve')
d.line(river,fill='#8aadb0',width=80,joint='curve')
# banks around lake
lake=(1450,2330,2110,2830)
d.ellipse((lake[0]-40,lake[1]-40,lake[2]+40,lake[3]+40),fill='#a8a07b')
d.ellipse(lake,fill='#658a8d',outline='#9ab2aa',width=22)
for i in range(75):
 x=R.randrange(1400,2100);y=R.randrange(2350,2780)
 if ((x-1780)/330)**2+((y-2580)/250)**2 <1:
  d.arc((x,y,x+R.randrange(9,28),y+R.randrange(4,12)),180,340,fill='#b2cbba',width=2)
# trails throughout new territory, with tracks and junctions.
trails=[[(2150,570),(2530,600),(3120,770),(3480,1330),(4100,1500),(4610,1770)],
 [(2050,1390),(2480,1720),(3160,1850),(3530,2230),(4060,2510)],
 [(640,1400),(870,1810),(1190,2140),(1370,2470),(1150,2840)],
 [(1270,1480),(1620,1870),(2200,2180),(3100,1830)],
 [(3160,1850),(3230,2460),(3020,3000)],
 [(4050,1490),(4220,2100),(4480,2900)]]
for trail in trails:
 d.line(trail,fill='#a78358',width=72,joint='curve')
 d.line(trail,fill='#bc9665',width=56,joint='curve')
 d.line(trail,fill='#c5a273',width=24,joint='curve')
# bridge across river at north central and southern central
for cx,cy in [(2700,690),(2350,2110)]:
 d.rectangle((cx-145,cy-43,cx+145,cy+43),fill='#5f4939',outline='#302f2a',width=8)
 for xx in range(cx-130,cx+132,18):d.line((xx,cy-34,xx,cy+34),fill='#a27f58',width=11)
 for yy in (cy-40,cy+40):d.line((cx-150,yy,cx+150,yy),fill='#4b3e33',width=9)
# Railway extends through the territory and toward distant mining operation.
for off in [-8,8]:d.line([(0,1418+off),(2250,1418+off),(2850,1830+off),(3600,2370+off),(4650,2370+off)],fill='#52483d',width=5)
for i in range(0,4650,20):
 if i<2250: x,y=i,1418
 elif i<2850:x=i;y=1418+(i-2250)*412/600
 elif i<3600:x=i;y=1830+(i-2850)*540/750
 else:x=i;y=2370
 d.line((x-3,y-12,x+7,y+12),fill='#66513b',width=8)
# Grasslands, pines, brush, cacti. Keep town centers and roads uncluttered.
settlements=[(3370,1770,350),(1070,2490,310),(4110,2500,310),(3810,1250,260)]
for i in range(1950):
 x=R.randrange(35,W-35);y=R.randrange(35,H-35)
 if x<2400 and y<1600:continue
 if any(math.hypot(x-cx,y-cy)<rad for cx,cy,rad in settlements):continue
 if any(math.hypot(x-a,y-b)<80 for path in trails for a,b in path):continue
 k=R.random()
 if y>2000 and x<2500 and k<.26:
  d.ellipse((x-13,y+4,x+15,y+15),fill='#8a865f')
  d.rectangle((x-4,y-22,x+5,y+7),fill='#514d3d')
  for layer in range(3):
   rad=20-layer*4
   d.ellipse((x-rad,y-42+layer*12,x+rad,y-12+layer*10),fill=['#485f46','#526d4c','#657b54'][layer])
 elif k<.25:
  d.line((x,y,x,y-22),fill='#50744d',width=5)
  d.line((x,y-10,x-10,y-11,x-10,y-24),fill='#50744d',width=4)
  d.line((x,y-16,x+8,y-17,x+8,y-27),fill='#50744d',width=4)
 elif k<.74:
  for j in range(3):d.line((x-11+j*6,y+4,x-2+j*6,y-R.randrange(4,13)),fill=R.choice(['#778052','#8c8954','#777d4d']),width=2)
 else:
  sz=R.randrange(7,21)
  d.ellipse((x-sz,y-sz//3,x+sz,y+sz//2),fill='#a58963',outline='#90704e',width=2)
# New towns and points of interest.
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',17)
except:font=ImageFont.load_default()
NEW=[
 ('TRADING POST',3250,1650,200,145,'#65594c'),('SAGEBRUSH SALOON',3530,1650,220,150,'#865d43'),
 ('SHERIFF ANNEX',3250,1910,185,120,'#646554'),('LIVERY',3510,1905,205,140,'#776144'),
 ('FISHING SHACK',910,2445,140,105,'#6f6855'),('LAKE CABIN',1150,2440,150,110,'#8a6e4f'),
 ('WATCHTOWER',3770,1060,128,120,'#6b594b'),('MESA CAMP',4050,1320,125,110,'#6f5748'),
 ('COPPER MINE',4090,2450,225,155,'#67564c'),('ASSAY OFFICE',4420,2440,165,120,'#777052'),
 ('BUNKHOUSE',4060,2700,200,120,'#735544'),('GHOST CHAPEL',2900,2690,170,145,'#777668'),
 ('SOUTH RANCH',710,2040,190,140,'#7b624a'),('WINDMILL',940,2140,90,90,'#746148'),
 ('RIVERSIDE CAMP',2320,2550,140,100,'#6a5c46'),('OLD MISSION',4550,1870,185,150,'#867461'),
 ('SMUGGLER SHED',3500,2900,160,110,'#645447')]
for name,x,y,w,h,color in NEW:
 d.rectangle((x+11,y+13,x+w+11,y+h+13),fill='#907451')
 d.rectangle((x,y,x+w,y+h),fill='#3d332e',outline='#282825',width=5)
 d.rectangle((x+7,y+7,x+w-7,y+h-7),fill=color)
 for yy in range(y+47,y+h-8,23):d.line((x+9,yy,x+w-9,yy),fill='#584c40',width=2)
 d.rectangle((x+8,y+7,x+w-8,y+38),fill='#493e36')
 label=name.replace('SAGEBRUSH ','').replace('SHERIFF ','')
 bbox=d.textbbox((0,0),label,font=font);tw=bbox[2]-bbox[0]
 if tw>w-14:label=label[:max(4,int(len(label)*(w-18)/tw))]
 bbox=d.textbbox((0,0),label,font=font)
 d.text((x+(w-(bbox[2]-bbox[0]))/2,y+14),label,font=font,fill='#f1d6a5',stroke_fill='#342d27',stroke_width=1)
 d.rectangle((x+w//2-14,y+h-22,x+w//2+14,y+h),fill='#372b27')
 for xx in (x+17,x+w-42):d.rectangle((xx,y+55,xx+23,y+79),fill='#d3b883',outline='#42372c',width=3)
# dots of activity in the settlement streets
for cx,cy in [(3370,1820),(1120,2280),(4150,2570)]:
 for i in range(10):
  a=R.random()*math.tau;rad=R.randrange(120,220)
  x=cx+math.cos(a)*rad;y=cy+math.sin(a)*rad
  d.ellipse((x-4,y-4,x+4,y+4),fill='#775c46')
# Borders and labels
labels=[('SAGEBRUSH CROSSING',3270,1575),('SILVERWATER LAKE',1440,2890),('COPPER RIDGE',4060,2375),
 ('THE HIGH MESA',3820,690),('GHOST MISSION',2880,2620),('SOUTH RANCHLAND',700,1920),
 ('RED ROCK WILDS',3270,370),('SOUTHERN BADLANDS',3160,3050)]
for name,x,y in labels:d.text((x,y),name,fill='#6d5747',font=font,stroke_width=2,stroke_fill='#d3b586')
# Restore original handcrafted story territory untouched above new features.
canvas.paste(old,(0,0))
canvas.save(ROOT/'world.png',optimize=True)
# Antique-style scaled cartographic map, displayed 658x394 inside world map screen.
thumb=canvas.resize((658,394),Image.Resampling.BILINEAR).convert('RGB')
from PIL import ImageEnhance
thumb=ImageEnhance.Color(thumb).enhance(.48)
thumb=ImageEnhance.Contrast(thumb).enhance(.84)
thumb.save(ROOT/'map.png',optimize=True)
print('Expanded playable world:',W,H,'and cartographic overview generated.')
