#!/usr/bin/env python3
"""v2.1 handcrafted cyber-noir city panoramas for Posledniy Signal.

Draws deliberately composed pixel-art architecture at a 1400x120 logical canvas,
then enlarges with nearest-neighbour to the project's 4200x360 panorama contract.
No external artwork, vector rendering, or random pixel-noise fills are used.
"""
from __future__ import annotations

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "backgrounds"
OUT.mkdir(parents=True, exist_ok=True)
W, H, SCALE = 1400, 120, 3

# Each chapter has its own coherent lighting temperature and skyline language.
THEMES = [
    {"sky":(7,10,27),"haze":(42,29,59),"street":(6,10,22),"far":(22,28,53),"mid":(15,22,43),"near":(9,14,29),"pink":(244,75,151),"cyan":(67,211,237),"warm":(255,185,125),"moon":(203,184,204)},
    {"sky":(14,10,22),"haze":(58,35,43),"street":(9,10,20),"far":(38,29,43),"mid":(25,21,35),"near":(13,14,25),"pink":(255,105,94),"cyan":(94,202,211),"warm":(255,191,119),"moon":(221,184,157)},
    {"sky":(5,18,30),"haze":(24,59,72),"street":(5,13,24),"far":(20,48,63),"mid":(14,37,52),"near":(7,23,37),"pink":(77,202,220),"cyan":(116,228,239),"warm":(238,190,135),"moon":(170,211,216)},
    {"sky":(11,9,29),"haze":(54,32,67),"street":(7,8,22),"far":(33,27,60),"mid":(22,20,45),"near":(12,13,31),"pink":(224,91,187),"cyan":(112,151,242),"warm":(248,174,151),"moon":(194,177,222)},
    {"sky":(9,15,31),"haze":(39,51,68),"street":(6,12,23),"far":(28,43,63),"mid":(19,32,50),"near":(10,19,34),"pink":(180,130,221),"cyan":(91,209,199),"warm":(247,194,132),"moon":(184,202,213)},
    {"sky":(16,9,28),"haze":(59,29,57),"street":(8,8,21),"far":(39,25,53),"mid":(27,18,42),"near":(14,12,30),"pink":(246,76,137),"cyan":(74,202,231),"warm":(255,178,114),"moon":(217,171,190)},
]

def lerp(a,b,t):
    return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))

def rect(d, box, fill, outline=None):
    d.rectangle(tuple(int(v) for v in box), fill=fill, outline=outline)

def line(d, pts, fill, width=1):
    d.line([(int(x),int(y)) for x,y in pts], fill=fill, width=width, joint="curve")

def polygon(d, pts, fill, outline=None):
    d.polygon([(int(x),int(y)) for x,y in pts], fill=fill, outline=outline)

def glow(im, x, y, color, radius=10, strength=48):
    # Low-opacity, small-radius bloom is kept behind hard pixel edges.
    layer=Image.new("RGBA", im.size, (0,0,0,0))
    ld=ImageDraw.Draw(layer)
    ld.ellipse((x-radius,y-radius,x+radius,y+radius), fill=(*color,strength))
    layer=layer.filter(ImageFilter.GaussianBlur(max(1,radius//3)))
    im.alpha_composite(layer)

def draw_sky(im, t, rng, chapter):
    d=ImageDraw.Draw(im)
    for y in range(120):
        if y<54:
            c=lerp(t["sky"],t["haze"],(y/54)**1.6)
        elif y<88:
            c=lerp(t["haze"],t["mid"],(y-54)/34*.42)
        else:
            c=lerp(t["mid"],t["street"],(y-88)/32)
        rect(d,(0,y,1399,y),c)
    # Large, sparse bands of cloud, built from stepped pixel clusters.
    cloud=t["far"]
    for i in range(12):
        x=(i*127+chapter*43)%1450-25
        y=13+(i*17+chapter*5)%31
        width=22+(i*19)%58
        shade=lerp(t["haze"],t["sky"],.42)
        rect(d,(x,y,x+width,y+1),shade)
        rect(d,(x+7,y+2,x+width-8,y+2),shade)
    # Stars and distant aircraft lights are sparse and intentional.
    for i in range(65):
        x=(i*97+chapter*53)%1390+4
        y=(i*29+chapter*11)%43+4
        if i%7==0:
            rect(d,(x,y,x+1,y+1),t["cyan"])
        elif i%3==0:
            rect(d,(x,y,x+2,y),lerp(t["haze"],t["moon"],.42))
    # A chapter-specific moon / distant orbital halo.
    if chapter in (0,3,5):
        mx,my,rad=108+chapter*11,27,10 if chapter!=5 else 8
        for ox,oy,rr,alpha in ((0,0,rad+8,16),(0,0,rad+4,26),(0,0,rad,255)):
            if rr>rad:
                glow(im,mx,my,t["pink"],rr,alpha)
            else:
                d.ellipse((mx-rr,my-rr,mx+rr,my+rr),fill=t["moon"])
        rect(d,(mx-12,my-2,mx+12,my+2),t["sky"])
        rect(d,(mx-10,my-5,mx+12,my-3),t["moon"])
    elif chapter in (1,4):
        mx,my=181,25
        d.ellipse((mx-8,my-8,mx+8,my+8),outline=t["cyan"],width=1)
        d.ellipse((mx-5,my-5,mx+5,my+5),outline=lerp(t["cyan"],t["sky"],.5),width=1)
    else:
        line(d,[(180,17),(205,17),(215,19),(232,19)],t["cyan"],1)

def building(d, x, base, width, height, fill, edge, window, seed, style=0):
    rng=random.Random(seed)
    top=base-height
    rect(d,(x,top,x+width,base),fill)
    # Roof profile and a second, offset silhouette make the block feel constructed.
    rect(d,(x-2,top+2,x+width+2,top+4),edge)
    if style%4==0:
        rect(d,(x+width//3,top-7,x+width*2//3,top+1),fill)
        line(d,[(x+width//2,top-7),(x+width//2,top-13)],edge)
        rect(d,(x+width//2-1,top-15,x+width//2+1,top-13),window)
    elif style%4==1:
        polygon(d,[(x,top+5),(x+width//2,top-5),(x+width,top+5)],fill,edge)
    elif style%4==2:
        rect(d,(x+4,top-5,x+width-4,top),edge)
        rect(d,(x+width//2-2,top-10,x+width//2+2,top-4),fill)
    else:
        rect(d,(x+width-5,top-12,x+width-3,top),edge)
        rect(d,(x+width-7,top-14,x+width-1,top-12),window)
    # Deep window recesses, with a few lit rooms rather than uniform checkerboard.
    cols=max(1,(width-8)//6)
    rows=max(1,(height-12)//7)
    for ry in range(rows):
        for cx in range(cols):
            if rng.random()<.48:
                wx=x+4+cx*6; wy=top+7+ry*7
                if wy+3<base:
                    rect(d,(wx,wy,wx+2,wy+3),window if rng.random()<.45 else lerp(fill,window,.35))
                    if rng.random()<.12:
                        rect(d,(wx,wy,wx+2,wy),edge)
    # Structural seams, rain streaks and exposed service conduits.
    if width>19:
        line(d,[(x+width//2,top+5),(x+width//2,base-2)],edge)
    if style%3==0:
        line(d,[(x+width-3,top+8),(x+width-3,base-4)],edge)
        rect(d,(x+3,base-9,x+width-4,base-7),lerp(fill,edge,.4))

def signboard(im, x, y, width, height, accent, secondary, label_seed):
    d=ImageDraw.Draw(im)
    # Layered casing, inset panel, pixel tubes and tiny glyph-like bars.
    rect(d,(x-2,y-2,x+width+2,y+height+2),(4,7,17))
    rect(d,(x,y,x+width,y+height),(9,13,29),accent)
    rect(d,(x+2,y+2,x+width-2,y+height-2),(13,17,34))
    line(d,[(x+3,y+3),(x+width-3,y+3)],lerp(accent,(255,255,255),.32))
    rng=random.Random(label_seed)
    bar_y=y+5
    while bar_y<y+height-3:
        bar_w=rng.randint(max(3,width//5),max(4,width-6))
        rect(d,(x+4,bar_y,x+min(width-4,bar_w),bar_y+1),accent if rng.random()<.65 else secondary)
        bar_y+=rng.randint(3,5)
    glow(im,x+width//2,y+height//2,accent,12,36)

def street(im, t, chapter, rng):
    d=ImageDraw.Draw(im)
    # Layered street wall and curb, with hard-edged puddle reflections.
    rect(d,(0,91,1399,119),t["street"])
    rect(d,(0,91,1399,93),lerp(t["near"],t["cyan"],.18))
    rect(d,(0,95,1399,96),lerp(t["street"],t["pink"],.13))
    # Perspective lane markings, wet road seams, drain grates.
    for x in range(-40,1450,118):
        polygon(d,[(x,120),(x+2,120),(x+16,94),(x+13,94)],lerp(t["street"],t["cyan"],.28))
    for x in range(22,1400,47):
        rect(d,(x,112,x+2,113),lerp(t["street"],t["cyan"],.5))
    for x in (78,347,590,833,1104,1322):
        rect(d,(x,98,x+17,100),lerp(t["near"],t["cyan"],.38))
        for k in range(4):
            rect(d,(x+2+k*4,98,x+3+k*4,100),lerp(t["street"],t["cyan"],.58))
    # Reflections broken into horizontal pixel strips, each tied to a real sign/window.
    for i in range(33):
        x=(i*43+chapter*17)%1380
        y=97+(i*7)%20
        c=t["pink"] if i%3==0 else t["cyan"] if i%3==1 else t["warm"]
        length=4+(i*13)%28
        alpha_color=lerp(t["street"],c,.22 if i%2 else .38)
        rect(d,(x,y,x+length,y+1+(i%2)),alpha_color)
    # Water glints and broken rain streaks.
    for i in range(72):
        x=(i*71+chapter*19)%1397
        y=94+(i*11)%25
        if i%4==0:
            rect(d,(x,y,x+2,y),t["cyan"])
        elif i%5==0:
            rect(d,(x,y,x+1,y+1),t["pink"])
    # Underpass darkness at the base adds strong foreground framing.
    rect(d,(0,117,1399,119),(3,5,13))


def draw_panorama_landmarks(im, chapter, t):
    """Seven individually composed, non-repeating set pieces across the 4200px world."""
    d = ImageDraw.Draw(im)
    def panel(x, y, w, h, edge, inner=(7, 12, 25)):
        rect(d, (x, y, x+w, y+h), inner, edge)
        rect(d, (x+2, y+2, x+w-2, y+4), lerp(inner, edge, .35))
    def window_grid(x, y, cols, rows, color, seed):
        rr = random.Random(seed)
        for row in range(rows):
            for col in range(cols):
                wx=x+col*5; wy=y+row*6
                if rr.random() < .62:
                    rect(d,(wx,wy,wx+2,wy+3),color if rr.random()<.42 else lerp(color,(8,13,26),.48))
    def cable(x1,y1,x2,y2,color):
        line(d,[(x1,y1),((x1+x2)//2,y1+3),(x2,y2)],(4,7,16),2)
        line(d,[(x1,y1-1),((x1+x2)//2,y1+2),(x2,y2-1)],color,1)
    # Each module occupies its own camera-sized chapter of the panorama.
    for seg, x in enumerate((0, 205, 410, 615, 820, 1025, 1230)):
        accent = t["pink"] if (seg+chapter)%2==0 else t["cyan"]
        warm = t["warm"]
        base = 93
        if chapter == 0:
            if seg == 0:  # cramped noodle-house frontage
                polygon(d,[(x+5,74),(x+18,56),(x+62,56),(x+77,74)],(17,19,39),accent)
                panel(x+16,73,49,18,accent); window_grid(x+21,78,8,2,warm,seg+1)
                signboard(im,x+25,48,38,10,t["pink"],t["cyan"],101)
                for xx in (x+9,x+70): rect(d,(xx,65,xx+3,94),(5,8,18),t["cyan"])
            elif seg == 1:  # vending-machine alcove
                rect(d,(x+18,61,x+73,94),(11,16,31),(57,76,103))
                for k in range(3):
                    panel(x+22+k*16,67,12,24,t["cyan"] if k==1 else t["pink"])
                    for yy in range(71,88,5): rect(d,(x+25+k*16,yy,x+30+k*16,yy+2),warm)
                cable(x+7,43,x+88,49,t["pink"])
            elif seg == 2:  # elevated train station and carriage
                rect(d,(x,63,x+180,67),(5,9,21),t["cyan"])
                rect(d,(x+25,49,x+112,63),(8,14,28),(73,91,118))
                for k in range(5): rect(d,(x+31+k*15,53,x+41+k*15,60),t["cyan"])
                rect(d,(x+20,66,x+122,68),t["pink"])
                for xx in (x+12,x+132): line(d,[(xx,34),(xx,94)],(5,8,19),2)
            elif seg == 3:  # stacked holographic billboards
                for k,(yy,ww) in enumerate(((37,55),(55,43),(72,66))):
                    signboard(im,x+28+(k%2)*22,yy,ww,11,accent if k%2==0 else warm,t["cyan"],110+seg*4+k)
                line(d,[(x+18,32),(x+18,93)],(5,8,18),3)
                for yy in (42,60,78): rect(d,(x+14,yy,x+22,yy+2),t["pink"])
            elif seg == 4:  # narrow arcade with awning and shutter
                polygon(d,[(x+8,65),(x+20,51),(x+83,51),(x+95,65)],(14,17,34),t["pink"])
                for k in range(7):
                    polygon(d,[(x+20+k*9,54),(x+28+k*9,54),(x+32+k*9,65),(x+24+k*9,65)],t["pink"] if k%2==0 else t["cyan"])
                rect(d,(x+20,68,x+83,94),(8,12,25),(62,61,91))
                for yy in range(75,91,4): line(d,[(x+26,yy),(x+77,yy)],(36,49,72))
            elif seg == 5:  # overhead footbridge
                rect(d,(x+2,53,x+190,57),(7,11,24),t["cyan"])
                line(d,[(x+2,49),(x+190,49)],t["pink"],1)
                for xx in range(x+10,x+190,12): line(d,[(xx,50),(xx,57)],(53,79,103))
                for xx in (x+25,x+164): line(d,[(xx,57),(xx,94)],(5,8,18),3)
            else:  # glowing street shrine
                polygon(d,[(x+28,73),(x+42,55),(x+82,55),(x+96,73)],(13,17,34),warm)
                polygon(d,[(x+20,56),(x+62,43),(x+104,56),(x+98,60),(x+62,49),(x+26,60)],(8,12,26),t["pink"])
                panel(x+47,74,30,19,t["cyan"]); rect(d,(x+57,80,x+67,90),warm)
        elif chapter == 1:
            if seg == 0:  # blast furnace
                polygon(d,[(x+14,94),(x+20,49),(x+34,39),(x+69,39),(x+83,49),(x+89,94)],(19,17,29),(100,61,53))
                rect(d,(x+31,48,x+71,87),(9,12,22),(123,68,48))
                for yy in (57,69,81): rect(d,(x+37,yy,x+65,yy+3),warm)
                for xx in (x+26,x+77): line(d,[(xx,34),(xx,94)],(8,11,19),3)
            elif seg == 1:  # pressure pipes and valves
                for yy in (47,61,77):
                    line(d,[(x+4,yy),(x+185,yy)],(7,11,20),5)
                    line(d,[(x+4,yy-1),(x+185,yy-1)],accent,1)
                for xx in (x+27,x+75,x+124,x+164):
                    rect(d,(xx,yy-7,xx+8,yy+7),(14,17,27),warm)
                    line(d,[(xx+4,yy-12),(xx+4,yy+12)],(8,11,18),2)
            elif seg == 2:  # refinery distillation towers
                for xx,top,w in ((x+18,35,27),(x+58,24,34),(x+111,43,29),(x+153,31,24)):
                    rect(d,(xx,top,xx+w,94),(15,17,28),(84,66,67))
                    rect(d,(xx-3,top+8,xx+w+3,top+12),(24,22,31),accent)
                    for yy in range(top+20,88,13): rect(d,(xx+5,yy,xx+w-5,yy+2),warm)
                    line(d,[(xx+w//2,top-8),(xx+w//2,top)],(7,10,17),2)
            elif seg == 3:  # conveyor and robotic gantry
                rect(d,(x+2,81,x+185,87),(5,8,17),(72,65,65))
                for xx in range(x+8,x+180,12): d.ellipse((xx,83,xx+5,88),fill=(34,42,51))
                for xx in (x+38,x+111,x+166):
                    line(d,[(xx,28),(xx,75)],(8,11,18),4)
                    line(d,[(xx,29),(xx+25,29)],accent,2)
                    line(d,[(xx+25,29),(xx+25,49)],(8,11,18),2)
            elif seg == 4:  # cooling towers
                for xx in (x+20,x+88,x+147):
                    polygon(d,[(xx,94),(xx+7,48),(xx+14,39),(xx+40,39),(xx+47,48),(xx+54,94)],(17,20,30),(76,75,80))
                    rect(d,(xx+12,58,xx+42,60),accent)
            elif seg == 5:  # freight loading crane
                line(d,[(x+25,25),(x+25,94)],(7,10,18),4)
                line(d,[(x+25,27),(x+173,27)],(7,10,18),4)
                line(d,[(x+25,29),(x+173,29)],warm,1)
                for xx in (x+51,x+103,x+153): line(d,[(xx,29),(xx,57)],accent,1)
                for xx in (x+39,x+91,x+141):
                    rect(d,(xx,58,xx+44,89),(17,23,32),accent)
                    for k in range(4): line(d,[(xx+7+k*9,62),(xx+7+k*9,85)],(55,67,76))
            else:  # smokestack bank
                for xx,hh in ((x+22,56),(x+62,72),(x+111,49),(x+151,66)):
                    rect(d,(xx,94-hh,xx+18,94),(14,16,26),(75,57,59))
                    rect(d,(xx-2,92-hh,xx+20,95-hh),warm)
                    for yy in range(94-hh+9,91,12): rect(d,(xx+4,yy,xx+14,yy+2),accent)
        elif chapter == 2:
            if seg == 0:  # container ship bow
                polygon(d,[(x+4,70),(x+161,70),(x+188,86),(x+169,94),(x+22,94)],(8,24,37),t["cyan"])
                for k in range(5):
                    rect(d,(x+17+k*28,52,x+43+k*28,69),(13,43,57),t["cyan"])
                    line(d,[(x+21+k*28,55),(x+21+k*28,66)],(46,101,115))
                for xx in (x+40,x+91,x+142): rect(d,(xx,79,xx+4,82),warm)
            elif seg == 1:  # gantry crane
                line(d,[(x+28,18),(x+28,94)],(7,18,29),4)
                line(d,[(x+28,20),(x+175,20)],(7,18,29),4)
                line(d,[(x+28,22),(x+175,22)],t["cyan"],1)
                line(d,[(x+155,22),(x+155,56)],(7,18,29),3)
                rect(d,(x+130,57,x+180,86),(12,40,55),t["cyan"])
                for xx in range(x+136,x+178,8): line(d,[(xx,61),(xx,82)],(46,98,111))
            elif seg == 2:  # lighthouse and beacon
                polygon(d,[(x+57,94),(x+68,35),(x+103,35),(x+114,94)],(15,35,47),t["cyan"])
                rect(d,(x+64,27,x+108,39),(8,18,30),warm)
                rect(d,(x+71,18,x+101,27),(9,20,31),t["cyan"])
                line(d,[(x+86,18),(x+86,7)],warm,2)
                for xx in (x+9,x+157): line(d,[(xx,83),(xx+9,83)],t["cyan"],1)
            elif seg == 3:  # warehouse loading bays
                polygon(d,[(x+3,58),(x+22,43),(x+176,43),(x+193,58),(x+193,94),(x+3,94)],(12,29,42),(54,91,105))
                for k in range(4):
                    panel(x+16+k*43,65,31,28,t["cyan"])
                    rect(d,(x+21+k*43,70,x+42+k*43,90),(7,20,31))
                    for yy in (74,82): line(d,[(x+22+k*43,yy),(x+41+k*43,yy)],(41,79,92))
            elif seg == 4:  # moored tugboat
                polygon(d,[(x+11,77),(x+178,77),(x+157,94),(x+35,94)],(8,23,34),t["cyan"])
                rect(d,(x+62,51,x+115,77),(14,32,44),t["cyan"])
                rect(d,(x+74,42,x+106,51),(12,26,38),warm)
                for xx in (x+80,x+96): rect(d,(xx,45,xx+7,49),t["cyan"])
                line(d,[(x+33,73),(x+15,55)],warm,1)
            elif seg == 5:  # stacked cargo containers
                for row in range(3):
                    for col in range(4):
                        xx=x+9+col*44+(row%2)*8; yy=49+row*15
                        rect(d,(xx,yy,xx+39,yy+13),(12+row*2,35+col*2,48+row*2),t["cyan"] if (row+col)%2 else (70,110,118))
                        for k in range(4): line(d,[(xx+5+k*9,yy+2),(xx+5+k*9,yy+11)],(38,77,91))
            else:  # harbor signal mast
                line(d,[(x+91,18),(x+91,94)],(7,19,31),3)
                for yy,ww in ((29,48),(48,34),(67,20)):
                    line(d,[(x+91-ww//2,yy),(x+91+ww//2,yy)],t["cyan"],1)
                    rect(d,(x+87,yy-3,x+95,yy+3),warm)
                cable(x+6,38,x+74,50,t["cyan"])
        elif chapter == 3:
            if seg == 0:  # corporate supertower
                polygon(d,[(x+48,94),(x+58,22),(x+79,9),(x+120,9),(x+142,22),(x+152,94)],(15,17,42),(99,76,147))
                for yy in range(30,88,8): rect(d,(x+77,yy,x+123,yy+3),t["cyan"] if yy%3 else t["pink"])
                line(d,[(x+100,8),(x+100,0)],t["pink"],2)
            elif seg == 1:  # skybridge between towers
                for xx,top in ((x+14,28),(x+148,38)):
                    rect(d,(xx,top,xx+34,94),(14,17,40),(72,76,131))
                    window_grid(xx+6,top+9,5,8,t["cyan"],xx)
                rect(d,(x+42,49,x+148,58),(18,20,49),t["pink"])
                for xx in range(x+48,x+145,12): rect(d,(xx,52,xx+6,55),t["cyan"])
            elif seg == 2:  # rooftop heliport
                rect(d,(x+18,47,x+180,52),(12,14,36),(91,78,145))
                line(d,[(x+98,46),(x+98,14)],(7,9,23),2)
                d.ellipse((x+63,25,x+132,42),outline=t["cyan"],width=1)
                line(d,[(x+57,33),(x+139,33)],t["pink"],1)
                line(d,[(x+98,33),(x+98,21)],warm,1)
            elif seg == 3:  # security checkpoint
                for xx in (x+17,x+148):
                    rect(d,(xx,48,xx+29,94),(12,14,34),(88,77,137))
                    rect(d,(xx+6,55,xx+23,69),t["pink"])
                    rect(d,(xx+9,58,xx+20,66),(8,12,28))
                rect(d,(x+46,79,x+145,84),(8,10,25),t["cyan"])
                for xx in range(x+55,x+140,16): line(d,[(xx,80),(xx,93)],(53,67,102))
            elif seg == 4:  # holographic corporate crest
                signboard(im,x+46,32,90,32,t["pink"],t["cyan"],303)
                for k in range(4):
                    line(d,[(x+25+k*42,72),(x+25+k*42,94)],(7,9,23),3)
                line(d,[(x+24,73),(x+180,73)],t["cyan"],1)
            elif seg == 5:  # office atrium with lit ribs
                polygon(d,[(x+20,94),(x+43,31),(x+151,31),(x+176,94)],(12,14,35),(83,75,130))
                for xx in range(x+50,x+160,13):
                    line(d,[(xx,36),(x+31+(xx-x)//1,92)],(38,45,78),1)
                rect(d,(x+80,54,x+117,92),(8,11,28),t["cyan"])
            else:  # orbital antenna
                line(d,[(x+98,21),(x+98,94)],(7,9,24),3)
                d.arc((x+48,17,x+148,91),190,350,fill=t["cyan"],width=2)
                line(d,[(x+50,43),(x+146,43)],t["pink"],1)
                rect(d,(x+92,13,x+104,23),warm)
        elif chapter == 4:
            if seg == 0:  # water tanks and vents
                for xx,yy,ww in ((x+18,44,39),(x+77,32,49),(x+145,51,31)):
                    rect(d,(xx,yy,xx+ww,yy+31),(12,27,43),(76,96,112))
                    rect(d,(xx+4,yy+4,xx+ww-4,yy+8),(32,61,76))
                    line(d,[(xx+ww//2,yy-8),(xx+ww//2,yy)],(5,12,23),2)
            elif seg == 1:  # greenhouse rooftop
                polygon(d,[(x+12,91),(x+28,49),(x+164,49),(x+184,91)],(9,27,37),t["cyan"])
                for xx in range(x+36,x+164,18):
                    line(d,[(xx,51),(xx-7,90)],(47,91,91),1)
                for xx,yy in ((x+53,69),(x+88,60),(x+124,73),(x+145,63)):
                    line(d,[(xx,87),(xx,yy)],(8,19,26),2)
                    for dx in (-4,3): rect(d,(xx+dx,yy+5,xx+dx+5,yy+9),t["cyan"])
            elif seg == 2:  # satellite dish and aerials
                d.arc((x+38,36,x+116,91),185,345,fill=(9,16,29),width=4)
                d.arc((x+41,39,x+113,88),185,345,fill=t["cyan"],width=1)
                line(d,[(x+78,67),(x+78,94)],(7,12,22),3)
                line(d,[(x+78,67),(x+110,42)],t["pink"],1)
                for xx in (x+135,x+157,x+177):
                    line(d,[(xx,44),(xx,94)],(7,12,22),2)
                    line(d,[(xx-7,56),(xx+7,56)],t["cyan"],1)
            elif seg == 3:  # collapsed apartment facade
                polygon(d,[(x+8,94),(x+15,38),(x+53,28),(x+83,43),(x+104,34),(x+128,55),(x+177,49),(x+190,94)],(13,24,39),(64,82,97))
                for xx,yy in ((x+28,53),(x+66,65),(x+116,57),(x+151,71)):
                    rect(d,(xx,yy,xx+14,yy+9),(5,11,21),t["pink"])
                    line(d,[(xx+7,yy),(xx+7,yy+9)],(38,50,67),1)
            elif seg == 4:  # fire escape and ladder
                for yy in (48,65,82):
                    line(d,[(x+17,yy),(x+112,yy)],(7,13,24),2)
                    line(d,[(x+17,yy-2),(x+112,yy-2)],(70,91,104),1)
                for xx in (x+22,x+106): line(d,[(xx,43),(xx,94)],(7,13,24),2)
                for yy in range(49,94,7): line(d,[(x+129,yy),(x+148,yy)],t["cyan"],1)
                line(d,[(x+129,43),(x+129,94)],(7,13,24),2)
            elif seg == 5:  # rooftop garden and old tree
                for xx in range(x+18,x+178,22):
                    rect(d,(xx,82,xx+16,94),(9,26,29),(42,83,66))
                    for k in range(3): rect(d,(xx+3+k*4,76-(k%2)*4,xx+5+k*4,82),t["cyan"])
                line(d,[(x+102,82),(x+102,40)],(8,16,22),3)
                for dx,yy in ((-17,43),(13,37),(-7,29),(20,51)):
                    line(d,[(x+102,yy+10),(x+102+dx,yy)],(8,16,22),2)
                    rect(d,(x+102+dx-3,yy-2,x+102+dx+3,yy+3),t["cyan"])
            else:  # rooftop water tower
                rect(d,(x+47,37,x+137,77),(13,27,41),(74,92,106))
                d.arc((x+47,29,x+137,49),180,360,fill=(91,109,119),width=2)
                for xx in (x+56,x+127): line(d,[(xx,77),(xx,94)],(7,13,22),3)
                line(d,[(x+92,27),(x+92,12)],t["pink"],1)
        else:
            if seg == 0:  # broken transit arch
                for xx in (x+18,x+145):
                    polygon(d,[(xx,94),(xx+7,38),(xx+17,27),(xx+28,38),(xx+35,94)],(10,15,34),(66,79,108))
                line(d,[(x+31,29),(x+153,29)],t["cyan"],2)
                for xx in range(x+42,x+148,17): line(d,[(xx,31),(xx,51)],(7,10,23),2)
            elif seg == 1:  # signal relay tower
                line(d,[(x+96,13),(x+96,94)],(6,10,25),4)
                for yy,ww in ((28,66),(48,48),(68,30)):
                    line(d,[(x+96-ww//2,yy),(x+96+ww//2,yy)],t["cyan"],2)
                    rect(d,(x+91,yy-4,x+101,yy+4),t["pink"])
                cable(x+8,42,x+88,53,t["cyan"])
            elif seg == 2:  # server monolith
                polygon(d,[(x+35,94),(x+45,18),(x+144,18),(x+156,94)],(10,13,34),(89,70,133))
                for yy in range(27,87,8):
                    rect(d,(x+61,yy,x+139,yy+3),t["cyan"] if yy%3 else t["pink"])
                    rect(d,(x+51,yy,x+56,yy+3),warm)
                line(d,[(x+94,10),(x+94,18)],t["pink"],2)
            elif seg == 3:  # reactor cooling pipes
                for xx,top in ((x+21,37),(x+69,22),(x+128,43),(x+166,31)):
                    rect(d,(xx,top,xx+21,94),(11,16,32),(72,79,112))
                    for yy in range(top+8,90,12):
                        rect(d,(xx+4,yy,xx+17,yy+3),t["cyan"] if yy%2 else t["pink"])
                line(d,[(x+3,62),(x+194,62)],warm,1)
            elif seg == 4:  # shattered signal dish
                d.arc((x+38,20,x+161,112),190,350,fill=t["cyan"],width=2)
                d.arc((x+49,31,x+150,103),190,350,fill=t["pink"],width=1)
                line(d,[(x+99,66),(x+99,94)],(7,10,24),3)
                for xx,yy in ((x+50,45),(x+68,32),(x+131,37),(x+150,55)):
                    line(d,[(x+99,66),(xx,yy)],(7,11,25),2)
                    rect(d,(xx-2,yy-2,xx+2,yy+2),warm)
            elif seg == 5:  # abandoned platform with signal lamps
                rect(d,(x+3,79,x+191,84),(7,10,24),t["cyan"])
                for xx in (x+22,x+67,x+113,x+159):
                    line(d,[(xx,34),(xx,79)],(6,10,23),3)
                    rect(d,(xx-6,36,xx+6,47),(9,13,28),t["pink"])
                    rect(d,(xx-2,39,xx+2,44),warm)
                line(d,[(x+8,54),(x+185,54)],(7,11,24),2)
            else:  # final antenna crown
                line(d,[(x+97,10),(x+97,94)],(6,9,22),3)
                for yy,ww in ((23,88),(42,65),(61,43)):
                    line(d,[(x+97-ww//2,yy),(x+97+ww//2,yy)],t["pink"] if yy==23 else t["cyan"],1)
                for xx in (x+53,x+141): rect(d,(xx,20,xx+5,25),warm)
        # Small authored foreground props make each segment readable at gameplay zoom.
        for k in range(3):
            px=x+12+k*61
            rect(d,(px,88,px+9,94),(5,8,17))
            rect(d,(px+2,84,px+7,88),accent if k==1 else lerp(accent,t["warm"],.3))
    # Fine pixel grain is clustered by architectural edge, never random full-frame noise.
    for seg, x in enumerate((0,205,410,615,820,1025,1230)):
        for k in range(13):
            px=x+((k*37+seg*19)%190)
            py=27+((k*17+chapter*7)%60)
            c=lerp(t["far"],t["cyan"],.24 if k%3 else .42)
            rect(d,(px,py,px+1,py+1),c)

def chapter_scene(chapter):
    t=THEMES[chapter]
    rng=random.Random(32000+chapter*911)
    im=Image.new("RGBA",(W,H),(0,0,0,255))
    draw_sky(im,t,rng,chapter)
    d=ImageDraw.Draw(im)
    # Distant silhouette: dense but low-contrast, leaving breathing room in the sky.
    x=-12
    while x<W:
        width=rng.randint(14,32); height=rng.randint(22,48)
        shade=lerp(t["far"],t["haze"],rng.uniform(.08,.28))
        building(d,x,88,width,height,shade,lerp(shade,t["cyan"],.17),lerp(shade,t["cyan"],.42),rng.randrange(1_000_000),rng.randrange(4))
        x+=width+rng.randint(2,7)
    # Middle layer uses recognizable industrial / residential blocks.
    x=-16
    while x<W:
        width=rng.randint(22,48); height=rng.randint(28,65)
        shade=lerp(t["mid"],t["far"],rng.uniform(.05,.28))
        building(d,x,94,width,height,shade,lerp(shade,t["pink"],.12),lerp(shade,t["warm"],.30),rng.randrange(1_000_000),rng.randrange(4))
        x+=width+rng.randint(3,9)
    # Distinct chapter landmarks, composed by hand rather than generic repeated props.
    landmark_base = im.copy()
    if chapter==0:  # neon shopping alley
        signboard(im,58,48,38,15,t["pink"],t["cyan"],11)
        signboard(im,188,58,28,11,t["cyan"],t["pink"],12)
        # Vertical lanterns and hanging cables.
        for x in (42,155,225):
            line(d,[(x,30),(x,54)],(5,7,17),2)
            rect(d,(x-3,52,x+3,62),(10,14,29),t["pink"])
            rect(d,(x-1,54,x+1,60),t["pink"])
        # Elevated rail and a distant train car.
        rect(d,(0,66,466,68),(7,11,24))
        line(d,[(0,65),(466,65)],t["cyan"],1)
        rect(d,(105,55,155,64),(9,15,30),lerp(t["cyan"],t["pink"],.5))
        for wx in (111,124,137):
            rect(d,(wx,57,wx+7,61),t["cyan"])
        rect(d,(111,63,151,64),t["pink"])
    elif chapter==1:  # industrial floodlit district
        # Factory sawtooth roof, chimney stacks, steam and warning lamps.
        for x in (28,103,176):
            rect(d,(x,45,x+13,93),(16,17,29),(68,42,48))
            rect(d,(x+3,34,x+10,46),(22,19,31))
            rect(d,(x+1,31,x+12,34),t["warm"])
            for yy in (49,58,67,76):
                rect(d,(x+3,yy,x+9,yy+2),t["pink"])
        polygon(d,[(0,84),(0,68),(24,55),(49,68),(73,55),(97,68),(120,55),(144,68),(168,55),(192,68),(216,55),(239,68),(239,94)],(15,16,28),(68,43,50))
        for x in (17,87,160,220):
            rect(d,(x,74,x+7,83),t["warm"])
        signboard(im,146,43,50,13,t["warm"],t["pink"],13)
    elif chapter==2:  # rain-swept waterfront / container port
        # Crane gantry, stacked shipping containers and beacon.
        rect(d,(0,79,235,95),(9,24,37))
        for x in (13,66,119,172):
            rect(d,(x,69,x+45,91),(13,37,52),t["cyan"])
            for xx in range(x+5,x+43,8):
                line(d,[(xx,72),(xx,89)],(33,82,98))
        line(d,[(181,24),(181,89)],(10,26,42),3)
        line(d,[(143,26),(218,26)],(10,26,42),3)
        line(d,[(143,26),(143,33)],t["cyan"])
        line(d,[(218,26),(218,33)],t["cyan"])
        rect(d,(177,20,185,25),t["warm"])
        # Water horizon and ship lights.
        line(d,[(0,88),(235,88)],t["cyan"],1)
        for x in (25,48,86,132,204):
            rect(d,(x,85,x+2,86),t["warm"])
    elif chapter==3:  # corporate tower / vertical city
        # Tall monolithic tower with stepped crown, illuminated spine and skybridge.
        polygon(d,[(62,93),(62,40),(82,28),(111,28),(130,40),(130,93)],(15,15,39),(91,65,120))
        rect(d,(84,34,108,92),(23,24,57))
        for yy in range(40,88,7):
            rect(d,(87,yy,105,yy+2),t["cyan"] if yy%2 else t["pink"])
        line(d,[(96,24),(96,7)],t["pink"],1)
        rect(d,(92,19,100,22),t["pink"])
        polygon(d,[(0,75),(239,75),(239,79),(0,79)],(9,11,29),(69,49,98))
        for x in (17,52,155,193,221):
            rect(d,(x,79,x+8,84),t["cyan"])
        signboard(im,154,49,43,15,t["pink"],t["cyan"],14)
    elif chapter==4:  # abandoned residential rooftops / overgrown city
        # Rooftop water tanks, antennas, broken windows and a small tree silhouette.
        for x,y in ((29,55),(88,49),(161,60),(210,52)):
            rect(d,(x,y,x+18,y+15),(15,25,43),(79,91,109))
            rect(d,(x+3,y+3,x+15,y+5),(29,43,60))
            line(d,[(x+9,y-7),(x+9,y)],(8,13,25),1)
            line(d,[(x+3,y-4),(x+15,y-4)],(8,13,25),1)
        # Tree branch silhouette with sparse cyan leaves.
        line(d,[(207,94),(208,64),(198,52)],(8,15,26),2)
        line(d,[(208,72),(221,57)],(8,15,26),2)
        for x,y in ((197,50),(202,45),(218,53),(224,56),(212,47)):
            rect(d,(x,y,x+3,y+2),t["cyan"] if x%2 else t["pink"])
        signboard(im,105,64,31,10,t["cyan"],t["pink"],15)
    else:  # endgame: signal array and ruined transit station
        # Giant signal ring / transmitter, framed by broken station girders.
        d.ellipse((66,24,151,109),outline=(13,18,39),width=5)
        d.ellipse((72,30,145,103),outline=t["cyan"],width=1)
        d.ellipse((82,40,135,93),outline=lerp(t["cyan"],t["pink"],.5),width=1)
        rect(d,(104,34,113,97),(9,12,30),t["pink"])
        line(d,[(108,15),(108,29)],t["pink"],2)
        rect(d,(101,11,115,15),t["warm"])
        for x in (13,37,182,210):
            line(d,[(x,36),(x+3,92)],(9,12,28),3)
            line(d,[(x-8,43),(x+12,43)],(9,12,28),2)
        signboard(im,162,60,42,13,t["pink"],t["cyan"],16)
    # Replace cloned motifs with individually authored landmarks across the panorama.
    draw_panorama_landmarks(im, chapter, t)
    d = ImageDraw.Draw(im)
    # A handful of deliberately placed service details: AC units, ducts, fire escapes.
    for idx,x in enumerate((18,76,137,204)):
        y=77+(idx%2)*5
        rect(d,(x,y,x+13,y+5),(8,12,25),(49,66,85))
        for vx in (x+3,x+6,x+9):
            line(d,[(vx,y+1),(vx,y+4)],(69,100,119))
        if idx%2==0:
            line(d,[(x+15,y-3),(x+15,y+7)],t["pink"],1)
    # Street layer is composed last to keep the playable plane legible.
    street(im,t,chapter,rng)
    # Pixel-sized light blooms are composited behind the architecture, not over the hero.
    for x,y,c in ((48,58,t["pink"]),(194,61,t["cyan"]),(116,79,t["warm"])):
        glow(im,x,y,c,8,30)
    return im.convert("RGB")

def foreground(chapter):
    t=THEMES[chapter]
    im=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(im)
    rng=random.Random(44000+chapter*67)
    # Foreground cables frame the top edge, never crossing the central combat lane.
    line(d,[(0,9),(105,12),(210,7),(335,13),(465,9)],(3,5,14,230),2)
    line(d,[(0,8),(105,11),(210,6),(335,12),(465,8)],(*t["cyan"],105),1)
    line(d,[(690,10),(820,5),(950,12),(1090,7),(1240,12),(1399,8)],(3,5,14,220),2)
    # Hanging cable loops, brackets, roof lips and rain gutters.
    for x in (82,294,507,746,1011,1274):
        line(d,[(x,0),(x,10),(x+7,15),(x+7,21)],(4,6,16,220),2)
        rect(d,(x+4,19,x+10,22),(*t["pink"],150))
    # Close lamp housings sit near the extreme sides as cinematic framing.
    for x in (16,1381):
        rect(d,(x-5,54,x+5,84),(4,7,17,245),(*t["cyan"],125))
        rect(d,(x-2,59,x+2,76),(*t["cyan"],120))
        line(d,[(x,43),(x,54)],(4,7,17,245),2)
        glow(im,x,68,t["cyan"],12,25)
    # Rooftop silhouettes only occupy the lowest edge, preserving character readability.
    for x in range(0,1400,47):
        if (x//47+chapter)%3==0:
            rect(d,(x,112,x+20,119),(3,5,13,220))
            rect(d,(x+4,108,x+16,112),(5,8,18,220))
    # Sparse drifting leaf/paper silhouettes for foreground parallax.
    for i in range(14):
        x=(i*97+chapter*23)%1390
        y=25+(i*13)%68
        color=(*t["pink"],75) if i%2 else (*t["cyan"],65)
        rect(d,(x,y,x+2,y+1),color)
    return im

def main():
    for chapter in range(6):
        base=chapter_scene(chapter)
        base.resize((W*SCALE,H*SCALE),Image.Resampling.NEAREST).save(OUT/f"act_{chapter}.png",optimize=True)
        fg=foreground(chapter)
        fg.resize((W*SCALE,H*SCALE),Image.Resampling.NEAREST).save(OUT/f"foreground_{chapter}.png",optimize=True)
    # Quality gates: all six panoramas are distinct, full colour, correct canvas and not flat.
    from PIL import ImageStat
    signatures=set()
    for chapter in range(6):
        p=OUT/f"act_{chapter}.png"
        with Image.open(p) as im:
            assert im.size==(4200,360) and im.mode=="RGB", f"bad panorama {p}"
            colors=im.resize((350,30),Image.Resampling.NEAREST).getcolors(350*30)
            assert colors and len(colors)>70, f"background lacks color depth: {p}"
            stat=ImageStat.Stat(im)
            assert min(stat.stddev)>4.0, f"background is visually flat: {p}"
            signatures.add(im.resize((70,6)).tobytes())
        with Image.open(OUT/f"foreground_{chapter}.png") as fg:
            assert fg.size==(4200,360) and fg.mode=="RGBA"
            assert fg.getchannel("A").getbbox() is not None
    assert len(signatures)==6, "chapter backgrounds are not distinct"
    print("v2.1: six distinct 4200x360 RGB cyber-noir panoramas and six RGBA foreground layers validated.")

if __name__=="__main__":
    main()
