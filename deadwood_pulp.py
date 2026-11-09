"""Deadwood Pulp rendering: lightweight, inked Tk Canvas illustrations.

Presentation only; collisions, missions and world geometry remain unchanged.
"""
INK='#231b1b'
GOLD='#e4af64'

def panel(c,x,y,w,h,fill='#241d1a',edge='#b88754'):
    c.create_rectangle(x+4,y+5,x+w+4,y+h+5,fill='#100d0c',outline='')
    c.create_rectangle(x,y,x+w,y+h,fill=fill,outline=INK,width=3)
    c.create_rectangle(x+3,y+3,x+w-3,y+h-3,outline=edge,width=1)
    for cx in (x+9,x+w-9):
        for cy in (y+9,y+h-9):
            c.create_oval(cx-2,cy-2,cx+2,cy+2,fill=GOLD,outline=INK)

def horse(c,x,y):
    """Outlined overhead horse with visible tack, mane and hooves."""
    c.create_oval(x-24,y+12,x+27,y+36,fill='#392722',outline='')
    for dx in (-15,12):
        c.create_polygon(x+dx-5,y+6,x+dx+3,y+6,x+dx+7,y+32,
                         x+dx-6,y+31,fill='#442c24',outline=INK,width=2)
    c.create_oval(x-20,y-19,x+21,y+23,fill='#74462e',outline=INK,width=3)
    c.create_polygon(x-12,y-11,x-13,y-31,x-2,y-23,x+6,y-33,
                     x+15,y-13,fill='#865537',outline=INK,width=2)
    for dx in (-12,12):
        c.create_polygon(x+dx-5,y-26,x+dx,y-38,x+dx+6,y-23,
                         fill='#523427',outline=INK)
    c.create_oval(x-10,y-18,x+10,y+13,fill='#352924',
                  outline='#c29860',width=3)
    c.create_line(x-9,y-8,x+10,y+4,fill='#c29860',width=2)
    c.create_line(x,y+19,x-9,y+36,fill=INK,width=4)

def person(c,x,y,coat='#425457',hat='#503728',facing=(0,-1),
           mounted=False,sheriff=False):
    """Compact ink-outlined overhead western character."""
    dy=-7 if mounted else 0
    c.create_oval(x-15,y+10,x+16,y+18,fill='#584033',outline='')
    for dx in (-7,5):
        c.create_rectangle(x+dx-4,y+3+dy,x+dx+4,y+15+dy,
                           fill='#312725',outline=INK)
    c.create_polygon(x-12,y-10+dy,x+12,y-10+dy,x+14,y+10+dy,
                     x-14,y+10+dy,fill=coat,outline=INK,width=3)
    c.create_polygon(x-10,y-9+dy,x+2,y-3+dy,x+9,y+7+dy,
                     x-11,y+4+dy,fill='#9c4533',outline=INK)
    c.create_line(x-10,y+4+dy,x+12,y+4+dy,fill='#c39556',width=3)
    c.create_oval(x-7,y-23+dy,x+8,y-8+dy,
                  fill='#c18a63',outline=INK,width=2)
    c.create_oval(x-17,y-21+dy,x+18,y-14+dy,
                  fill=hat,outline=INK,width=2)
    c.create_rectangle(x-10,y-29+dy,x+10,y-19+dy,
                       fill=hat,outline=INK,width=2)
    c.create_line(x-9,y-22+dy,x+9,y-22+dy,fill='#a6774a',width=2)
    if sheriff:
        c.create_polygon(x,y-3+dy,x+4,y+1+dy,x+2,y+5+dy,
                         x-2,y+5+dy,x-4,y+1+dy,fill=GOLD,outline=INK)
    if facing!=(0,-1):
        fx,fy=facing
        c.create_line(x+fx*8,y+fy*6+dy,x+fx*22,y+fy*19+dy,
                      fill=INK,width=5)
        c.create_line(x+fx*12,y+fy*10+dy,x+fx*22,y+fy*19+dy,
                      fill='#c8b9a1',width=2)
