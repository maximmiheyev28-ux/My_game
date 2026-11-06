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
