#!/usr/bin/env python3
"""v2.2 authored pixel-art pass: chapter scenery, character sprites and motion sprites."""
from __future__ import annotations
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

ROOT = Path(__file__).resolve().parent
BG = ROOT / "assets/backgrounds"
CH = ROOT / "assets/characters"
FX = ROOT / "assets/fx"
BG.mkdir(parents=True, exist_ok=True); CH.mkdir(parents=True, exist_ok=True); FX.mkdir(parents=True, exist_ok=True)
W,H,S = 1400,120,3

THEMES = [
 {"sky":(7,10,26),"haze":(43,29,57),"far":(22,29,52),"mid":(15,23,42),"near":(8,13,26),"street":(4,7,17),"pink":(244,69,145),"cyan":(66,211,235),"warm":(255,188,123),"moon":(202,185,205)},
 {"sky":(15,10,20),"haze":(61,35,39),"far":(40,30,42),"mid":(27,22,34),"near":(15,15,25),"street":(6,8,15),"pink":(255,105,83),"cyan":(104,197,203),"warm":(255,190,112),"moon":(219,185,151)},
 {"sky":(5,17,28),"haze":(25,57,68),"far":(21,48,62),"mid":(15,36,49),"near":(8,23,34),"street":(4,10,19),"pink":(75,194,215),"cyan":(111,227,237),"warm":(241,189,131),"moon":(174,212,215)},
 {"sky":(10,9,28),"haze":(56,34,69),"far":(35,28,61),"mid":(24,21,47),"near":(13,13,32),"street":(5,7,18),"pink":(226,89,188),"cyan":(111,157,242),"warm":(248,177,151),"moon":(194,178,222)},
 {"sky":(9,15,29),"haze":(41,51,65),"far":(29,44,62),"mid":(20,33,48),"near":(10,20,32),"street":(5,10,19),"pink":(181,131,219),"cyan":(94,207,194),"warm":(247,194,135),"moon":(184,202,212)},
 {"sky":(16,9,26),"haze":(60,31,58),"far":(41,27,54),"mid":(28,19,43),"near":(14,13,29),"street":(6,7,17),"pink":(245,75,137),"cyan":(76,203,230),"warm":(255,179,116),"moon":(216,173,192)}
]
def mix(a,b,t): return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))
def px(d,x,y,c):
    if 0 <= x < W and 0 <= y < H: d.point((int(x),int(y)),fill=c)

# Pixel maps use material clusters: ink, deep shade, midtone, edge light, neon and warm bounce.
PALETTE = {
 ".":None,"k":(5,8,18),"d":(14,22,38),"m":(39,59,76),"h":(99,132,151),
 "c":(54,204,226),"p":(228,65,139),"w":(247,187,116),"r":(135,67,53),
 "g":(48,117,83),"l":(111,173,116),"v":(89,76,139),"b":(19,38,58)
}
MAPS = {
 "shop": [
 "......................",".......kkkkkk.........",".....kkddddddkk.......","...kkddmmmmmmddkk.....",
 "..kddmhhhhhhhhmddk....",".kddmhddddddddhmddk...","kddmhpccccccpphmddk...","kddmhpmmmmmmdphmddk...",
 "kddmhppppppppphmddk...","kddmdddddddddddmddk...","kddmhhmmhhmmhhmmddk...","kddmhhmmhhmmhhmmddk...",
 "kddmddddddddddddmddk..","kddmccddwwddccdmddk..","kddmccddwwddccdmddk..","kddmddddddddddddmddk..",
 "kddmppppppppppppmddk..","kddmppppppppppppmddk..","kddmddmmmmmmmmddmddk.","kddmddmhhhhhhmddmddk.",
 "kddmddmhhhhhhmddmddk.","kddddddddddddddddddk.","kkkkkkkkkkkkkkkkkkkkk"
 ],
 "train": [
 "........................................","....kkkkkkkkkkkkkkkkkkkkkkkkkkkkkk......",
 "..kkddddddddddddddddddddddddddddddkk....",".kddmhhhhhhhhhhhhhhhhhhhhhhhhhhhhhmddk...",
 "kddmddccccddccccddccccddccccddccccddmddk..","kddmddccccddccccddccccddccccddccccddmddk..",
 "kddmddddddddddddddddddddddddddddddddmddk..","kddmppppppppppppppppppppppppppppppppmddk..",
 "kddmddmmmmddmmmmddmmmmddmmmmddmmmmddmddk..","kddmddmhhmddmhhmddmhhmddmhhmddmhhmddmddk..",
 "kddmddddddddddddddddddddddddddddddddmddk..","kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
 ],
 "furnace": [
 "....................kkkkkkkk...............",".................kkddddddddkk.............",
 "...............kkddmmmmmmmmddkk...........","............kkddmmmmmmmmmmmmmmddkk........",
 "..........kkddmmmhhhhhhhhhhhhmmmddkk.......","........kkddmmhhddddddddddddhhmmddkk.......",
 ".......kddmmhhdrrrrrrrrrrrrrrdhhmmddk.......","......kddmmhhdrrwwwwwwwwwwwwrrdhhmmddk.....",
 ".....kddmmhhddrrwwwwwwwwwwwwrrddhhmmddk....","....kddmmhhdddrrrrrrrrrrrrrrddddhhmmddk....",
 "...kddmmhhddddmhhhhhhhhhhhhmddddhhmmddk....","..kddmmhhdddddmdddddddddddddmddddd hhmmddk..",
 ".kddmmhhddddddmccddccddccddmddddddhhmmddk.",
 "kddmmhhdddddddmdddddddddddddmddddddhhmmddk.",
 "kddmmhhdddddddmhhmmhhmmhhmmhmddddddhhmmddk.",
 "kddmmhhdddddddmdddddddddddddmddddddhhmmddk.",
 "kddmmhhdddddddmrrrrrrrrrrrrrrmddddddhhmmddk.",
 "kddmmhhdddddddmrrrrwwwwwwrrrrmddddddhhmmddk.",
 "kddmmhhdddddddmrrrrwwwwwwrrrrmddddddhhmmddk.",
 "kddmmhhdddddddmrrrrrrrrrrrrrrmddddddhhmmddk.",
 "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
 ],
 "crane": [
 "......kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk.....",
 "......kdddddddddddddddddddddddddddddddddddddddk......",
 "......kmmhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhmk......",
 "......kmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmk.......",
 "......kmmk..................................kmmk......",
 "......kmmk..................................kmmk......",
 "......kmmk..............kkkkkk.............kmmk......",
 "......kmmk..............kddddk.............kmmk......",
 "......kmmk..............kddddk.............kmmk......",
 "......kmmk..............kddddk.............kmmk......",
 "......kmmk..............kddddk.............kmmk......",
 "......kmmk..............kddddk.............kmmk......",
 "......kmmk..............kddddk.............kmmk......",
 "......kmmk..............kddddk.............kmmk......",
 "......kmmk..............kddddk.............kmmk......",
 "......kmmk..............kddddk.............kmmk......",
 "......kkkk..............kkkkk.............kkkkk......"
 ],
 "ship": [
 "..........................................................","........kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk........",
 ".....kkkkdddddddddddddddddddddddddddddddddddddkkkk......","...kkddmmmhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhmmmmddkk....",
 "..kddmmhddmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmddhhmmddk...",
 ".kddmmhddmwwddmwwddmwwddmwwddmwwddmwwddmwwddmddhhmmddk...",
 "kddmmhddmddmddmddmddmddmddmddmddmddmddmddmddmddhmmdddk..",
 "kddmmhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhmdddk..",
 ".kddmmrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrmmddk...",
 "..kkddmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmddkk.....",
 "....kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk........"
 ],
 "tower": [
 "..................kkkkkk..................","...............kkkkddddkkk................",
 "............kkkkdddmmmmddkkk.............","..........kkdddmmmhhhhhhmmmddkk.........",
 ".........kddmmmhhddddddddhhmmmddk........","........kddmmhhddddddddddddhhmmddk.......",
 ".......kddmmhhdmwwdmwwdmwwdmhdhhmmddk......",
 "......kddmmhhdmwwdmwwdmwwdmhdhhmmddk......",
 "......kddmmhhdmwwdmwwdmwwdmhdhhmmddk......",
 ".....kddmmhhddddddddddddddddddhhmmddk.....",
 ".....kddmmhhccccccccccccccccccchhmmddk.....",
 ".....kddmmhhddddddddddddddddddhhmmddk.....",
 ".....kddmmhhdmwwdmwwdmwwdmwwdmhmmddk......",
 ".....kddmmhhdmwwdmwwdmwwdmwwdmhmmddk......",
 ".....kddmmhhddddddddddddddddddhhmmddk.....",
 ".....kddmmhhccccccccccccccccccchhmmddk.....",
 ".....kddmmhhddddddddddddddddddhhmmddk.....",
 ".....kddmmhhdmwwdmwwdmwwdmwwdmhmmddk......",
 ".....kddmmhhddddddddddddddddddhhmmddk.....",
 ".....kddmmhhpppppppppppppppppphhmmddk.....",
 ".....kddmmhhddddddddddddddddddhhmmddk.....",
 ".....kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk......"
 ],
 "greenhouse": [
 "..............................................",".................kkkkkkkkkkkk...............",
 "..............kkddddddddddddddkk.............","............kkddmmhhhhhhhhhhmmddkk...........",
 "..........kkddmmhhddddddddddhhmmddkk.........","........kkddmmhhddddddddddddddhhmmddkk.......",
 "......kkddmmhhddgddgddgddgddgddgddhhmmddkk....",
 "....kkddmmhhddgllggllggllggllggllddhhmmddkk...",
 "...kddmmhhddddgllggllggllggllgglldddddhhmmddk..",
 "..kddmmhhddddddddddddddddddddddddddddhhmmddk..",
 ".kddmmhhddddddddddddddddddddddddddddddhhmmddk.",
 "kddmmhhddddddddddddddddddddddddddddddddhhmmddk",
 "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
 ],
 "tree": [
 ".............gggg.............","..........ggglllggg...........",
 "........ggllllllggg..........","......ggllgllllgllgg..........",
 ".....ggllggggggggllgg.........","....ggllgg......ggllgg........",
 "....gllgg..........gllg.......",".....gllg....kk....gllg.......",
 "......gllg..kmmk..gllg........",".......gllg.kmmmk.gllg........",
 "........gggkmmmmkggg..........","...........kmmmmk.............",
 "...........kmmmmk.............","...........kmmhmk.............",
 "...........kmmhmk.............","..........kkmmmkk.............",
 ".........kk..kmmk..............","........k....kmmk..............",
 ".............kkkk.............."
 ],
 "radar": [
 "..............kkkkkkkk..............","..........kkkkddddddddkkkk..........",
 ".......kkkddmmmmhhhhmmmmddkkk.......",".....kkddmmhhddddddddddhhmmddkk.....",
 "...kkddmmhhddddddddddddddhhmmddkk...",".kkddmmhhddddddccccccddddddhhmmddkk.",
 "kddmmhhddddddccddddccddddddhhmmddk..","kddmmhhddddddcddddddcddddddhhmmddk..",
 "kddmmhhdddddddccccccddddddd hhmmddk.".replace(" ",""),
 "kddmmhhddddddddddddddddddddhhmmddk...","kddmmhhddddddddkkkkddddddddhhmmddk...",
 ".kkddmmhhddddkkddddkkddddhhmmddkk.....","...kkddmmhhkkddddddddkkhhmmddkk.......",
 ".....kkkkkkddddddddddddkkkkkk..........","..........kkkkkkkkkkkk..............."
 ],
 "vending": [
 "........kkkkkkkkkkkk........","......kkddddddddddddkk......",".....kddmhhhhhhhhhhmddk.....",
 "....kddmddppppppppddmddk....","....kddmddpwwwwwwpddmddk....","....kddmddpwwwwwwpddmddk....",
 "....kddmddppppppppddmddk....","....kddmddddddddddddmddk....","....kddmddccddccddccmddk....",
 "....kddmddccddccddccmddk....","....kddmddddddddddddmddk....","....kddmhhhhhhhhhhmddk.....",
 "....kkkkkkkkkkkkkkkkkk......"
 ],
 "dish": [
 "................kkkk...............",".............kkkddddkkk............",
 "..........kkkddmmmmmmddkkk.........",".......kkkddmmhhhhhhhhmmddkkk......",
 "....kkkddmmhhddddddddddhhmmddkkk....","..kkddmmhhddddddddddddddddhhmmddkk..",
 ".kddmmhhddddddddddddddddddddhhmmddk.","..kkddmmhhddddddddddddddddhhmmddkk...",
 "....kkkddmmhhddddddddddhhmmddkkk.....",".......kkkddmmhhhhhhhhmmddkkk........",
 "..........kkkkkkkkkkkkkk.............","...............kmmk..................",
 "...............kmmk..................","...............kmmk..................",
 "...............kkkk.................."
 ],
 "relay": [
 "..................kk..................","...............kkkmmkkk...............",
 ".............kkkddmmmmddkkk............","..........kkkddmmmhhhhmmmddkkk.........",
 "........kkkddmmhhddddddddhhmmddkk.......",".......kddmmhhddddddddddddhhmmddk.......",
 "......kddmmhhccccccccccccccchhmmddk......","......kddmmhhddddddddddddddhhmmddk.......",
 "......kddmmhhpppppppppppppphhmmddk.......","......kddmmhhddddddddddddddhhmmddk.......",
 "......kddmmhhccccccccccccccchhmmddk......","......kddmmhhddddddddddddddhhmmddk.......",
 "......kddmmhhpppppppppppppphhmmddk.......","......kddmmhhddddddddddddddhhmmddk.......",
 "......kddmmhhccccccccccccccchhmmddk......","......kddmmhhddddddddddddddhhmmddk.......",
 "......kddmmhhddddddddddddddhhmmddk.......","......kkkkkkkkkkkkkkkkkkkkkkkkkk........"
 ],
 "radio": [
 "....................kkkk....................","...............kkkkddddkkkk...............",
 "............kkkkdddmmmmdddkkkk............",".........kkkddmmmhhhhhhhhmmmddkkk.........",
 "......kkkddmmhhddddddddddddhhmmddkkk.......",".....kddmmhhddddddccccccddddddhhmmddk......",
 "....kddmmhhddddccddddddddccddddhhmmddk......","...kddmmhhdddcddddddddddddcddd hhmmddk......".replace(" ",""),
 "..kddmmhhddddddccccccccccddddddhhmmddk......","...kddmmhhddddddddddddddddddddhhmmddk......",
 "....kddmmhhddddddddddddddddddhhmmddk.......",".....kddmmhhhhhhhhhhhhhhhhhhmmddk.........",
 "......kkkkkkkkkkkkkkkkkkkkkkkkk............"
 ],
 "dock": [
 ".........kkkkkkkkkkkkkkkkkkkkkkkkkkkk.........","......kkkddddddddddddddddddddddddddkkk......",
 "...kkkddmmhhhhhhhhhhhhhhhhhhhhhhhhmmddkkk...","kkddmmhhddddddddddddddddddddddddddddhhmmddkk",
 "kddmmhhddddddddddddddddddddddddddddddhhmmddk","kddmmhhddddddddddddddddddddddddddddddhhmmddk",
 "kddmmhhddddddddddddddddddddddddddddddhhmmddk","kddmmhhccccccccccccccccccccccccccccccchhmmddk",
 ".kkddmmhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhmmddkk.","...kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk......"
 ],
 "antenna": [
 "............kk..............","..........kkmkk............","........kkmmmmmkk..........",
 "......kkmmhhhmmmkk.........","....kkmmhhddd hhmmkk.......".replace(" ",""),
 "...kmmhhddddddd hhmmk......".replace(" ",""),"..kmmhhdddddddddhhmmk.....",
 ".kmmhhddddddddddddhhmmk....","kmmhhddddddddddddddhhmmk...","kmmhhddddddddddddddhhmmk...",
 ".kmmhhddddddddddddhhmmk....","..kmmhhdddddddddhhmmk......","...kkmmhhddddd hhmmkk......".replace(" ",""),
 ".....kkmmhhhhmmmkk.........",".......kkkkkkkk..........."
 ]
}
def draw_map(im, x, y, rows, tint=None, scale=1):
    d=ImageDraw.Draw(im)
    for ry,row in enumerate(rows):
        row=row.replace(" ","")
        for rx,ch in enumerate(row):
            c=PALETTE.get(ch)
            if c is None: continue
            if tint and ch in ("c","p","w"):
                c=tint[ch]
            x0=x+rx*scale; y0=y+ry*scale
            d.rectangle((x0,y0,x0+scale-1,y0+scale-1),fill=c)
def draw_skyline(im, chapter, t):
    """Layered raster architecture: clustered windows, recessed bays and roof hardware."""
    d=ImageDraw.Draw(im); rng=random.Random(7000+chapter*97)
    wall_base=mix(t["far"],t["mid"],.28)
    wall_shadow=mix(wall_base,t["sky"],.34)
    edge_light=mix(wall_base,t["cyan"],.20)
    warm_light=mix(wall_base,t["warm"],.29)
    cool_light=mix(wall_base,t["cyan"],.37)
    x=-28
    while x<W+36:
        bw=rng.randint(25,53); bh=rng.randint(28,61); base=88+rng.randint(-2,2)
        top=base-bh; style=rng.randrange(5)
        # Pixel-stepped roofline with a different silhouette per building.
        for yy in range(bh):
            if style==0: inset=0 if yy>4 else (4 if yy<2 else 2)
            elif style==1: inset=0 if yy>7 else max(0,8-yy)
            elif style==2: inset=0 if yy>3 else (2 if yy==0 else 1)
            elif style==3: inset=0 if yy>5 else (6 if yy<2 else 3)
            else: inset=1 if yy<3 else (0 if yy%11<8 else 2)
            left=x+inset; right=x+bw-inset-1
            if right<=left: continue
            for xx in range(left,right+1):
                if xx==left: color=edge_light
                elif xx==right: color=wall_shadow
                elif yy<3: color=mix(wall_base,t["haze"],.18)
                else: color=wall_base
                # Recessed slab joints and occasional repaired concrete patches.
                if yy>7 and yy%9==0 and xx>left+2 and xx<right-2:
                    color=mix(color,t["sky"],.16)
                d.point((xx,top+yy),fill=color)
        # Irregular ledges, exposed conduits and window bays make each facade readable.
        for floor_y in range(top+8,base-3,9):
            if rng.random()<.72:
                end=x+bw-rng.randint(3,9)
                d.line((x+3,floor_y,end,floor_y),fill=mix(wall_base,t["haze"],.30),width=1)
            for wx in range(x+5,x+bw-6,7):
                if rng.random() < (0.66 if style in (1,3) else 0.48):
                    wy=floor_y-rng.randint(2,4)
                    # Dark inset, side bevel, glass pane, and a single reflection pixel.
                    d.point((wx,wy),fill=wall_shadow)
                    d.point((wx+1,wy),fill=wall_shadow)
                    d.point((wx,wy+1),fill=wall_shadow)
                    glass=rng.choice((cool_light,warm_light,mix(wall_shadow,t["cyan"],.24)))
                    d.point((wx+1,wy+1),fill=glass)
                    if rng.random()<.42: d.point((wx+2,wy+1),fill=mix(glass,t["sky"],.20))
                    if rng.random()<.28: d.point((wx+1,wy+2),fill=mix(glass,t["haze"],.35))
        # Roof silhouettes: antennae, lift rooms, vents and offset parapets.
        if style in (0,3):
            for k in range(rng.randint(1,3)):
                rx=x+rng.randint(5,max(6,bw-6))
                d.point((rx,top-1),fill=wall_shadow)
                d.point((rx,top-2),fill=edge_light if k==0 else wall_shadow)
                if k==0: d.line((rx,top-3,rx,top-6),fill=wall_shadow,width=1)
        elif style==1 and bw>35:
            d.line((x+5,top+2,x+bw-5,top+2),fill=mix(wall_base,t["cyan"],.20),width=1)
            d.point((x+bw//2,top-1),fill=wall_shadow)
        if style==2 and bh>40:
            # Narrow external fire escape with interrupted landings.
            ex=x+bw-5
            d.line((ex,top+7,ex,base-5),fill=wall_shadow,width=1)
            for fy in range(top+13,base-5,14):
                d.line((ex-3,fy,ex+1,fy),fill=edge_light,width=1)
        if style==4 and bw>37:
            # Small rooftop machinery cluster, drawn as a dark body with lit service panel.
            rx=x+bw//2
            for dx,dy,col in ((0,-2,wall_shadow),(-1,-1,edge_light),(0,-1,wall_shadow),(1,-1,wall_shadow),(0,0,cool_light)):
                d.point((rx+dx,top+dy),fill=col)
        # A few wall-mounted AC units with grille pixels and a dangling service cable.
        if bw>31 and rng.random()<.44:
            ax=x+rng.randint(5,bw-9); ay=top+bh//2
            d.point((ax,ay),fill=wall_shadow); d.point((ax+1,ay),fill=edge_light)
            d.point((ax,ay+1),fill=wall_shadow); d.point((ax+1,ay+1),fill=cool_light)
            d.line((ax+1,ay+2,ax+1,ay+4),fill=wall_shadow,width=1)
        x+=bw+rng.randint(4,11)
def draw_street_frontage(im, chapter, t):
    """Compose a continuous, district-specific street with non-repeating buildings and lived-in details."""
    rng=random.Random(14600+chapter*733)
    d=ImageDraw.Draw(im)
    # Each chapter has a different urban function, street furniture language and facade materials.
    districts=[
      {"materials":[(35,43,61),(54,52,65),(24,35,53),(74,54,67)],"accent":t["pink"],"kind":"night market"},
      {"materials":[(61,42,38),(45,39,43),(79,53,43),(33,38,45)],"accent":t["warm"],"kind":"foundry row"},
      {"materials":[(24,52,62),(30,66,72),(42,56,65),(19,43,55)],"accent":t["cyan"],"kind":"harbor street"},
      {"materials":[(39,34,66),(53,39,72),(31,32,57),(69,43,76)],"accent":t["pink"],"kind":"neon arcade"},
      {"materials":[(38,57,56),(53,66,63),(36,47,61),(67,66,57)],"accent":t["cyan"],"kind":"overgrown quarter"},
      {"materials":[(51,37,57),(67,42,57),(38,35,55),(76,49,62)],"accent":t["pink"],"kind":"signal district"}
    ][chapter]
    # Each district has its own street grain: narrow retail lots, industrial sheds, dock warehouses,
    # vertical arcade blocks, low garden houses, or fortified signal infrastructure.
    profiles=[
        {"width":(58,112),"top":(43,65),"roof":(0,1,2,3,4),"sign":.96},
        {"width":(132,218),"top":(22,43),"roof":(0,0,1,3,4),"sign":.38},
        {"width":(104,184),"top":(38,59),"roof":(0,1,2,4,4),"sign":.48},
        {"width":(66,126),"top":(17,43),"roof":(0,1,1,2,3,4),"sign":.94},
        {"width":(116,204),"top":(48,70),"roof":(0,2,2,3,4),"sign":.42},
        {"width":(88,158),"top":(26,51),"roof":(0,1,2,3,4),"sign":.72}
    ][chapter]
    # A continuous row of attached buildings; widths and rooflines vary, no repeated modular pattern.
    x=-18
    building=0
    while x<W+20:
        bw=rng.randint(*profiles["width"])
        top=rng.randint(*profiles["top"])
        base=104+rng.randint(-2,2)
        wall=rng.choice(districts["materials"])
        shadow=mix(wall,t["sky"],.48)
        edge=mix(wall,t["moon"],.24)
        steel=mix(wall,t["moon"],.38)
        rust=mix(wall,t["warm"],.52)
        # Individual roof silhouette: parapet, sloped cap, setback, or rooftop room.
        roof=rng.choice(profiles['roof'])
        if roof==0:
            d.rectangle((x,top+4,x+bw,base),fill=wall)
            d.line((x,top+4,x+bw,top+4),fill=edge,width=2)
            d.rectangle((x+8,top-2,x+bw-10,top+3),fill=shadow)
        elif roof==1:
            d.rectangle((x+5,top,x+bw-3,base),fill=wall)
            d.line((x+5,top,x+bw-3,top),fill=edge,width=2)
            d.rectangle((x+14,top-5,x+bw-18,top-1),fill=shadow)
        elif roof==2:
            d.rectangle((x,top+8,x+bw,base),fill=wall)
            d.rectangle((x+3,top+2,x+bw-8,top+7),fill=shadow)
            d.line((x+3,top+2,x+bw-8,top+2),fill=edge)
        elif roof==3:
            d.rectangle((x,top+3,x+bw,base),fill=wall)
            d.rectangle((x+bw//2,top-7,x+bw-8,top+2),fill=shadow)
            d.line((x+bw//2,top-7,x+bw-8,top-7),fill=edge)
        else:
            d.rectangle((x+2,top+5,x+bw-2,base),fill=wall)
            for sx in range(x+4,x+bw-8,11):
                d.point((sx,top+3),fill=edge)
        # Facade seams, water stains and patched masonry form irregular texture clusters.
        for yy in range(top+9,base-4,7):
            if rng.random()<.52:
                xx=x+rng.randint(4,max(5,bw-16))
                d.line((xx,yy,min(x+bw-4,xx+rng.randint(5,19)),yy),fill=shadow)
            if rng.random()<.25:
                xx=x+rng.randint(4,max(5,bw-8))
                d.line((xx,yy,xx, min(base-3,yy+rng.randint(3,10))),fill=mix(wall,t["sky"],.25))
        # Upper windows: each bay has a dark inset, sill, reflection and occasional lit room.
        window_y=top+rng.randint(12,19)
        while window_y<82:
            for wx in range(x+10,x+bw-10,rng.choice((17,19,23,27))):
                ww=rng.randint(6,11); wh=rng.randint(7,12)
                d.rectangle((wx,window_y,wx+ww,window_y+wh),fill=shadow)
                d.line((wx,window_y+wh,wx+ww,window_y+wh),fill=edge)
                d.line((wx+2,window_y+2,wx+2,window_y+wh-2),fill=mix(t["cyan"],wall,.46))
                if rng.random()<.64:
                    glow=rng.choice((t["warm"],t["cyan"],t["pink"]))
                    d.rectangle((wx+3,window_y+2,wx+ww-2,window_y+wh-2),fill=mix(glow,wall,.14))
                    d.point((wx+3,window_y+2),fill=mix(glow,(255,255,245),.12))
                if rng.random()<.28:
                    d.line((wx-1,window_y+wh+2,wx+ww+1,window_y+wh+2),fill=shadow,width=2)
            window_y+=rng.randint(15,21)
        # Street-level use differs per building: shop, service door, loading bay or shutter.
        frontage=rng.randrange(5)
        door_x=x+rng.randint(9,max(10,bw-24))
        if frontage==0:
            # Glass shopfront with a deep frame, counter silhouette and uneven awning.
            d.rectangle((door_x,78,door_x+20,base),fill=shadow)
            d.rectangle((door_x+2,80,door_x+18,96),fill=mix(t["cyan"],wall,.52))
            d.line((door_x+2,82,door_x+17,82),fill=t["moon"])
            d.rectangle((door_x-3,74,door_x+23,77),fill=districts["accent"])
            for ax in range(door_x-2,door_x+24,5):
                d.line((ax,74,ax+2,78),fill=mix(districts["accent"],t["moon"],.24))
            d.rectangle((door_x+3,98,door_x+17,base-2),fill=shadow)
        elif frontage==1:
            # Heavy industrial shutter, with ribs and a warning lamp.
            d.rectangle((door_x,80,door_x+25,base),fill=shadow)
            for sy in range(83,base-2,4):
                d.line((door_x+2,sy,door_x+23,sy),fill=mix(wall,t["moon"],.16))
            d.point((door_x+22,78),fill=t["warm"])
        elif frontage==2:
            # Recessed residential entrance, lintel and offset steps.
            d.rectangle((door_x,78,door_x+13,base),fill=shadow)
            d.rectangle((door_x+3,82,door_x+10,base-2),fill=mix(wall,t["sky"],.30))
            d.point((door_x+9,91),fill=t["warm"])
            d.line((door_x-4,base-4,door_x+17,base-4),fill=edge)
            d.line((door_x-7,base-1,door_x+19,base-1),fill=edge)
        elif frontage==3:
            # Deep loading arch and stacked crates.
            d.rectangle((door_x,79,door_x+24,base),fill=shadow)
            d.rectangle((door_x+3,83,door_x+21,base),fill=mix(wall,t["sky"],.32))
            d.rectangle((door_x+27,91,door_x+36,base-2),fill=shadow)
            d.line((door_x+28,94,door_x+35,94),fill=edge)
        else:
            # Narrow service window and a patched metal door.
            d.rectangle((door_x,82,door_x+12,base),fill=shadow)
            d.rectangle((door_x+2,85,door_x+9,91),fill=mix(t["cyan"],wall,.65))
            d.point((door_x+9,98),fill=t["warm"])
        # District-specific facade grammar: the street must change its construction,
        # not merely its palette. These overlays alter the building's actual use and silhouette.
        if chapter == 0:
            # Dense market frontage: striped canvas awnings, hanging lamps and narrow shop bays.
            awn_y=76+rng.randint(-2,2)
            awn_w=min(bw-12,rng.randint(24,42))
            awn_x=x+rng.randint(5,max(6,bw-awn_w-4))
            d.rectangle((awn_x,awn_y,awn_x+awn_w,awn_y+2),fill=shadow)
            for ax in range(awn_x,awn_x+awn_w,5):
                d.polygon([(ax,awn_y),(min(awn_x+awn_w,ax+4),awn_y),(min(awn_x+awn_w,ax+3),awn_y+5),(ax+1,awn_y+5)],fill=districts["accent"] if (ax//5)%2 else mix(districts["accent"],t["moon"],.30))
            d.line((awn_x+2,awn_y+6,awn_x+awn_w-2,awn_y+6),fill=edge)
            d.point((awn_x+awn_w+2,awn_y-3),fill=t["warm"])
        elif chapter == 1:
            # Foundry frontage: heavy riveted lintels, broad corrugated steel doors and heat vents.
            bay_x=x+rng.randint(8,max(9,bw-38)); bay_w=min(bw-12,rng.randint(27,42))
            d.rectangle((bay_x,77,bay_x+bay_w,base),fill=shadow)
            d.line((bay_x,77,bay_x+bay_w,77),fill=steel,width=2)
            for gy in range(81,base-2,5):
                d.line((bay_x+2,gy,bay_x+bay_w-2,gy),fill=mix(wall,t["moon"],.13))
            for rx in (bay_x+3,bay_x+bay_w-3):
                d.point((rx,80),fill=t["warm"]); d.point((rx,base-4),fill=rust)
            if rng.random()<.7:
                px=x+bw-rng.randint(8,14)
                d.rectangle((px,top+7,px+5,base-5),fill=shadow)
                for py in range(top+12,base-7,9): d.line((px-2,py,px+7,py),fill=rust)
        elif chapter == 2:
            # Harbor warehouses: tall loading portals, hoist rails and cargo identification panels.
            bay_x=x+rng.randint(7,max(8,bw-34)); bay_w=min(bw-10,rng.randint(25,39))
            d.rectangle((bay_x,74,bay_x+bay_w,base),fill=shadow)
            d.line((bay_x,74,bay_x+bay_w,74),fill=edge,width=2)
            d.line((bay_x+3,78,bay_x+3,base-2),fill=mix(t["cyan"],wall,.34),width=2)
            for gy in range(82,base-3,7): d.line((bay_x+6,gy,bay_x+bay_w-3,gy),fill=mix(wall,t["moon"],.16))
            d.rectangle((bay_x+bay_w+3,84,bay_x+bay_w+8,96),fill=rust)
            d.line((bay_x+bay_w+5,78,bay_x+bay_w+5,83),fill=t["warm"],width=2)
        elif chapter == 3:
            # Arcade district: vertical light boxes, recessed glass columns and illuminated fins.
            fin_x=x+rng.randint(6,max(7,bw-10))
            d.rectangle((fin_x,top+8,fin_x+3,base-4),fill=shadow)
            d.line((fin_x+1,top+10,fin_x+1,base-7),fill=districts["accent"],width=2)
            d.point((fin_x+2,top+12),fill=t["moon"])
            if bw>76:
                glass_x=x+bw//2-8
                d.rectangle((glass_x,78,glass_x+15,base-2),fill=shadow)
                d.rectangle((glass_x+2,81,glass_x+13,base-5),fill=mix(t["cyan"],wall,.42))
                d.line((glass_x+7,81,glass_x+7,base-5),fill=t["pink"])
        elif chapter == 4:
            # Garden quarter: timber gables, porch posts, planter boxes and climbing vines.
            gx=x+bw//2
            d.polygon([(gx-15,top+7),(gx,top-4),(gx+15,top+7)],fill=shadow)
            d.line((gx-15,top+7,gx,top-4,gx+15,top+7),fill=edge,width=2)
            d.rectangle((gx-12,top+8,gx+12,top+12),fill=mix(wall,t["moon"],.16))
            for vx in (x+7,x+bw-9):
                d.line((vx,top+24,vx-2,base-3),fill=(42,89,66),width=2)
                for vy in range(top+31,base-8,11):
                    d.ellipse((vx-4,vy-2,vx+2,vy+3),fill=(55,112,74))
            d.rectangle((x+8,base-7,x+24,base-3),fill=(37,76,54))
        else:
            # Signal district: armored concrete plates, narrow observation slits and cable ducts.
            for seam_y in (top+8,top+26,top+44):
                if seam_y<base-4: d.line((x+4,seam_y,x+bw-4,seam_y),fill=shadow,width=2)
            slit_x=x+bw//2-rng.randint(3,7)
            d.rectangle((slit_x,top+13,slit_x+5,top+25),fill=shadow)
            d.line((slit_x+2,top+15,slit_x+2,top+22),fill=t["cyan"])
            d.line((x+bw-7,top+5,x+bw-7,base-4),fill=mix(wall,t["moon"],.18),width=2)
            d.point((x+bw-7,top+4),fill=t["pink"])
        # Signs are unique per building in size, placement and neon hue.
        if rng.random()<profiles['sign']:
            sy=rng.randint(68,75); sx=x+rng.randint(8,max(9,bw-36))
            sw=rng.randint(18,min(43,max(19,bw-12)))
            sign=rng.choice((t["pink"],t["cyan"],t["warm"]))
            d.rectangle((sx-2,sy-2,sx+sw,sy+3),fill=shadow)
            d.line((sx,sy-1,sx+sw-2,sy-1),fill=sign,width=2)
            for q in range(sx+2,sx+sw-2,4):
                d.point((q,sy+1),fill=mix(sign,t["moon"],.34))
        # Chapter-specific urban infrastructure: pipes, balconies, cables and exhausts.
        detail=rng.randrange(6)
        if detail==0:
            px=x+bw-8
            d.line((px,top+7,px,base-2),fill=shadow,width=2)
            for py in range(top+15,base-5,13):
                d.line((px-2,py,px+2,py),fill=edge)
        elif detail==1 and bw>100:
            bx=x+rng.randint(18,bw-35); by=top+27
            d.line((bx,by,bx+27,by),fill=edge)
            d.line((bx,by,bx,by+8),fill=edge)
            d.line((bx+27,by,bx+27,by+8),fill=edge)
            d.line((bx-3,by+8,bx+30,by+8),fill=shadow,width=2)
            d.point((bx+4,by-2),fill=t["cyan"])
        elif detail==2:
            ax=x+rng.randint(12,max(13,bw-18)); ay=top+31
            d.rectangle((ax,ay,ax+8,ay+5),fill=shadow)
            d.line((ax+2,ay+2,ax+7,ay+2),fill=edge)
            d.line((ax+4,ay+5,ax+4,ay+10),fill=shadow)
        elif detail==3:
            # Fire escape with broken landings, not a repeated full-height ladder.
            ex=x+bw-13
            d.line((ex,top+16,ex,base-7),fill=shadow)
            for fy in range(top+24,base-7,17):
                d.line((ex-7,fy,ex+2,fy),fill=edge)
                d.point((ex-7,fy-1),fill=shadow)
        elif detail==4:
            # Roof exhaust and a drifting steam tuft.
            vx=x+rng.randint(12,max(13,bw-15)); vy=top-3
            d.rectangle((vx,vy,vx+7,top+2),fill=shadow)
            d.line((vx+2,vy-3,vx+2,vy-7),fill=edge)
            d.point((vx+5,vy-9),fill=mix(t["haze"],t["moon"],.42))
        else:
            # Exterior cable loop and a junction box.
            cx=x+rng.randint(10,max(11,bw-12)); cy=top+9
            d.line((cx,cy,cx+5,cy+5,cx+11,cy+2),fill=shadow)
            d.rectangle((cx+9,cy+3,cx+13,cy+7),fill=edge)
        # Small lived-in clutter at the threshold: bins, crates, bags and a bike silhouette.
        if rng.random()<.55:
            bx=x+rng.randint(7,max(8,bw-12))
            d.rectangle((bx,base-9,bx+6,base-2),fill=shadow)
            d.line((bx+1,base-8,bx+5,base-8),fill=mix(t["cyan"],wall,.35))
        if rng.random()<.30:
            bx=x+rng.randint(10,max(11,bw-22))
            d.ellipse((bx,base-7,bx+5,base-2),outline=shadow)
            d.ellipse((bx+13,base-7,bx+18,base-2),outline=shadow)
            d.line((bx+2,base-5,bx+10,base-9,bx+15,base-5),fill=edge)
        # Narrow gaps contain drainpipes, fireproof joints and scraps of reflected light.
        d.line((x+bw,top+7,x+bw,base),fill=shadow)
        x+=bw-2
        building+=1
    # Continuous sidewalk, curb and asphalt bind the separate facades into one street.
    d.rectangle((0,105,W-1,109),fill=mix(t["near"],t["moon"],.10))
    d.line((0,105,W-1,105),fill=mix(t["near"],t["cyan"],.30))
    d.rectangle((0,110,W-1,H-1),fill=t["street"])
    # Broken puddle rims and neon reflections: irregular, localised highlights rather than repeated stripes.
    for i in range(86):
        x0=rng.randrange(W); y0=rng.randrange(111,H)
        length=rng.randint(3,24)
        hue=rng.choice((t["cyan"],t["pink"],t["warm"],t["moon"]))
        shade=mix(t["street"],hue,rng.uniform(.20,.58))
        d.line((x0,y0,min(W-1,x0+length),y0),fill=shade,width=1)
        if rng.random()<.32 and y0+1<H:
            d.point((min(W-1,x0+rng.randint(0,length)),y0+1),fill=mix(shade,t["street"],.35))
    # Curb chips, drain grates and scattered road repairs break the long horizontal plane.
    for x0 in range(17,W, rng.randint(43,61)):
        d.line((x0,106,x0+2,108),fill=mix(t["near"],t["moon"],.34))
        if rng.random()<.42:
            d.line((x0+5,114,x0+12,114),fill=mix(t["street"],t["moon"],.30))
    # District signatures: waterfront bollards, foundry pipes, garden growth, or transit markings.
    if chapter==0:
        for bx in (96,418,887,1248):
            d.rectangle((bx,100,bx+3,109),fill=(75,67,79))
            d.point((bx+1,99),fill=t["warm"])
    elif chapter==1:
        for bx in (165,503,1018,1320):
            d.line((bx,95,bx,109),fill=(103,72,54),width=3)
            d.point((bx+1,94),fill=t["warm"])
    elif chapter==2:
        for bx in (112,374,762,1190):
            d.rectangle((bx,98,bx+7,109),fill=(24,61,70))
            d.line((bx+1,101,bx+6,101),fill=t["cyan"])
    elif chapter==3:
        for bx in (76,342,695,1060,1328):
            d.line((bx,96,bx+7,109),fill=mix(t["pink"],t["sky"],.38),width=2)
    elif chapter==4:
        for bx in (138,457,825,1166):
            d.line((bx,101,bx+2,92,bx+5,101),fill=(60,105,75),width=2)
            d.point((bx+3,91),fill=(107,163,105))
    else:
        for bx in (128,451,793,1162):
            d.rectangle((bx,101,bx+9,108),fill=(50,42,65))
            d.point((bx+4,100),fill=t["pink"])
    # Overhead service cables are sagged and interrupted, not a repeated decorative stripe.
    for x0 in (35,286,611,944,1260):
        y0=rng.randint(13,25)
        d.line((x0,y0,x0+65,y0+5,x0+143,y0+2),fill=mix(t["sky"],t["moon"],.32))
        if chapter in (0,3,5):
            d.point((x0+66,y0+5),fill=t["cyan"])
    return building


def draw_district_landmarks(im, chapter, t):
    """Add unmistakable, district-specific silhouettes and foreground story details."""
    d=ImageDraw.Draw(im)
    ink=(5,8,18); deep=mix(t["near"],t["sky"],.35)
    steel=mix(t["mid"],t["moon"],.22); rust=mix(t["warm"],(91,48,43),.42)
    # Landmarks are asymmetrical focal points, not repeated facade modules.
    if chapter == 0:  # crowded night-market corner and elevated pedestrian bridge
        d.polygon([(170,54),(192,42),(226,42),(244,52),(244,62),(170,62)],fill=(36,28,48))
        d.line((170,53,192,41,226,41,244,51),fill=t["pink"],width=2)
        d.rectangle((181,55,234,67),fill=deep); d.rectangle((188,58,197,66),fill=t["warm"])
        d.line((205,54,205,91),fill=ink,width=3); d.line((205,55,205,91),fill=steel)
        d.line((0,35,154,42,270,39),fill=ink,width=3); d.line((0,34,154,41,270,38),fill=t["moon"])
        for x in (48,89,132,236):
            d.line((x,38,x,45),fill=ink,width=2); d.rectangle((x-3,45,x+3,51),fill=t["pink"])
            d.point((x,46),fill=(255,214,164))
        # stacked produce crates, fabric awnings and a rain-darkened shop threshold
        for x,y in ((275,88),(286,91),(303,86),(317,92)):
            d.rectangle((x,y,x+9,y+8),fill=(48,38,48)); d.line((x,y,x+8,y),fill=t["warm"])
            d.line((x+2,y+2,x+2,y+6),fill=steel)
    elif chapter == 1:  # foundry stacks, furnace mouth and overhead steam pipe
        for x,h,w in ((260,38,13),(276,52,17),(1045,44,15),(1064,34,12)):
            y=102-h
            d.polygon([(x,y+6),(x+3,y),(x+w-3,y),(x+w,y+6),(x+w-1,103),(x+1,103)],fill=(37,31,36))
            d.line((x+2,y+4,x+w-2,y+4),fill=rust,width=2)
            d.rectangle((x+4,y+11,x+w-4,y+17),fill=(117,57,43))
            for yy in range(y+21,100,7): d.point((x+w//2,yy),fill=(171,83,48))
            d.line((x+2,100,x+w-2,100),fill=steel)
        d.line((260,57,260,49,292,49,292,57),fill=ink,width=4)
        d.line((260,56,260,48,292,48,292,56),fill=rust,width=2)
        for x,y in ((269,39),(277,32),(285,26),(1051,45),(1058,37)):
            d.ellipse((x,y,x+8,y+4),fill=(68,58,63))
            d.line((x+2,y+3,x+9,y+1),fill=(100,86,83))
        d.rectangle((430,84,482,104),fill=(27,24,30))
        d.rectangle((437,89,475,103),fill=(106,47,35))
        d.rectangle((444,92,468,101),fill=(255,112,58))
        for x in range(447,468,5): d.line((x,93,x,100),fill=(255,190,94))
    elif chapter == 2:  # dockside crane, ship bow and mooring gear
        d.polygon([(170,79),(204,73),(238,77),(263,88),(282,100),(164,100)],fill=(18,43,55))
        d.line((171,80,204,74,239,78,263,89),fill=t["cyan"],width=2)
        d.rectangle((192,66,245,77),fill=(27,53,62))
        for x in (199,211,223,235): d.rectangle((x,68,x+7,75),fill=(91,112,112))
        d.line((205,66,205,55,242,55,254,64),fill=ink,width=4)
        d.line((205,65,205,54,242,54,254,63),fill=steel,width=2)
        d.line((242,55,242,78),fill=ink,width=2); d.line((242,56,242,78),fill=t["warm"])
        d.line((188,55,260,55),fill=ink,width=3); d.line((188,54,260,54),fill=steel)
        d.line((188,54,174,66),fill=steel,width=2)
        for x in (180,193,253,266):
            d.rectangle((x,94,x+7,106),fill=(25,48,58)); d.line((x,95,x+6,95),fill=t["cyan"])
        # wet dock edge, bollards and rope loops
        d.line((0,108,420,108),fill=(42,101,111),width=1)
        for x in (64,151,294,366):
            d.rectangle((x,99,x+4,109),fill=(65,83,88)); d.ellipse((x-3,97,x+7,101),outline=steel)
            d.line((x+2,100,x+18,105,x+27,104),fill=(79,112,117))
    elif chapter == 3:  # dense arcade canopy with deep arch and layered signage
        d.polygon([(480,63),(492,43),(511,32),(540,32),(558,45),(568,63)],fill=(29,22,54))
        d.line((480,63,492,43,511,32,540,32,558,45,568,63),fill=t["pink"],width=2)
        d.arc((496,43,552,94),180,360,fill=t["cyan"],width=3)
        d.rectangle((501,67,547,103),fill=(14,14,34))
        for x in range(506,545,7):
            d.line((x,70,x,100),fill=(57,48,91))
            if x%2: d.point((x+2,82),fill=t["pink"])
        for x,y,w,col in ((405,54,47,t["cyan"]),(575,48,59,t["pink"]),(628,68,34,t["warm"])):
            d.rectangle((x-3,y-3,x+w,y+5),fill=ink)
            d.line((x,y,x+w-2,y),fill=col,width=2)
            for q in range(x+3,x+w-3,5): d.point((q,y+3),fill=mix(col,t["moon"],.4))
        d.line((460,26,460,91),fill=ink,width=3); d.line((461,26,461,91),fill=steel)
        d.line((460,29,495,29),fill=ink,width=3); d.line((460,28,495,28),fill=t["pink"])
        for x in (458,493,562): d.point((x,94),fill=t["cyan"])
    elif chapter == 4:  # greenhouse roof, overgrown walls and mature street trees
        d.polygon([(250,77),(274,48),(303,34),(335,48),(359,77)],fill=(25,46,47))
        d.line((250,77,274,48,303,34,335,48,359,77),fill=(91,139,119),width=2)
        d.line((274,48,274,89,335,89,335,48),fill=(74,118,105),width=2)
        for x in (285,301,317,330):
            d.line((x,45,x,88),fill=(72,111,103))
        d.line((260,69,350,69),fill=(83,132,113))
        for x,y in ((275,60),(290,53),(311,58),(327,66),(300,74)):
            d.point((x,y),fill=(133,189,131)); d.point((x+1,y+1),fill=(69,133,95))
        for x in (92,390,850,1190):
            d.line((x,102,x+1,72),fill=(45,76,58),width=3)
            for ox,oy in ((-10,75),(0,65),(9,78),(-4,84),(8,88)):
                d.ellipse((x+ox-5,oy-4,x+ox+6,oy+5),fill=(30,68,54))
                d.point((x+ox+2,oy-2),fill=(99,153,100))
            d.line((x-5,103,x+8,103),fill=(84,105,76),width=2)
        # broken paving interrupted by weeds
        for x in range(20,1400,73):
            d.line((x,112,x+13,112),fill=(44,66,59))
            if x%3: d.line((x+5,109,x+4,105),fill=(75,130,83))
    else:  # fortified signal district: relay mast, dish and armored service gantry
        d.polygon([(640,72),(654,57),(668,72),(668,105),(640,105)],fill=(26,23,43))
        d.line((640,72,654,57,668,72),fill=t["pink"],width=2)
        d.rectangle((647,75,661,101),fill=(11,15,31))
        for y in (80,87,94): d.line((650,y,658,y),fill=t["cyan"],width=1)
        d.line((654,57,654,9),fill=ink,width=4); d.line((654,57,654,9),fill=steel,width=1)
        d.line((654,15,638,28,654,25,670,35),fill=ink,width=3)
        d.line((654,15,638,28,654,25,670,35),fill=t["pink"],width=1)
        d.ellipse((624,33,647,53),outline=steel,width=2)
        d.ellipse((628,37,643,49),outline=t["cyan"],width=1)
        d.line((635,42,654,25),fill=ink,width=2)
        d.rectangle((1110,65,1172,105),fill=(24,21,39))
        d.rectangle((1116,71,1166,99),fill=(11,17,32))
        for y in (75,83,91): d.line((1119,y,1162,y),fill=(51,77,103),width=2)
        for x in (1122,1133,1144,1155): d.point((x,79),fill=t["pink"])
        d.line((1098,62,1186,62),fill=ink,width=4); d.line((1098,61,1186,61),fill=t["cyan"],width=1)
        for x in (1103,1180): d.line((x,62,x,105),fill=steel,width=2)
    # Small, unique ground-level traces connect landmark to the same continuous street.
    for x in (38, 512, 932, 1360):
        d.line((x,107,x+18,107),fill=mix(t["street"],t["moon"],.32))
        d.point((x+5,106),fill=t["cyan"] if chapter in (0,2,3,5) else t["warm"])



def draw_art_direction_pass(im, chapter, t):
    """Hand-composed focal architecture, material breakup and depth cues for each chapter."""
    d=ImageDraw.Draw(im)
    ink=(4,7,16); black=(7,10,19); wet=(9,16,27)
    steel=mix(t["mid"],t["moon"],.34); cold=mix(t["cyan"],t["moon"],.28)
    rust=mix(t["warm"],(139,67,48),.48)
    warm=mix(t["warm"],(255,225,174),.22); accent=t["pink"]
    # Every act receives a unique, large-scale silhouette with a readable light hierarchy.
    if chapter==0:
        # Suspended night-market canopy: layered tarpaulin, ribbed supports and warm lanterns.
        d.polygon([(352,49),(382,35),(457,35),(488,48),(482,54),(360,54)],fill=(29,23,39))
        d.line([(352,49),(382,34),(457,34),(488,47)],fill=ink,width=4)
        d.line([(354,47),(383,37),(456,37),(485,49)],fill=accent,width=2)
        for x in range(370,481,13):
            d.line((x,40,x-2,52),fill=mix(accent,t["moon"],.25),width=2)
            d.point((x-2,53),fill=warm)
        d.line((360,55,360,91),fill=ink,width=3); d.line((480,53,480,92),fill=ink,width=3)
        d.line((361,56,480,56),fill=steel)
        # Stall counter with uneven goods, stacked boxes and a tiny illuminated menu.
        d.polygon([(370,76),(455,76),(465,82),(465,103),(365,103),(365,82)],fill=(21,20,32))
        d.line((366,82,463,82),fill=warm,width=2)
        for x,y,c in ((378,73,t["cyan"]),(391,71,t["pink"]),(405,74,t["warm"]),(422,70,t["cyan"]),(439,74,t["pink"])):
            d.rectangle((x,y,x+5,y+7),fill=mix(c,black,.2)); d.point((x+1,y),fill=warm)
        d.rectangle((447,60,463,75),fill=black); d.rectangle((449,62,461,72),fill=mix(t["cyan"],black,.38))
        d.line((451,65,459,65),fill=t["cyan"]); d.line((451,68,457,68),fill=t["pink"])
        for x in (338,493,530):
            d.line((x,25,x,39),fill=ink,width=2); d.rectangle((x-3,39,x+3,46),fill=accent)
            d.point((x,40),fill=(255,232,187))
        # hanging cable loops and rain-darkened awning folds
        d.line((320,20,355,26,395,23,431,29),fill=ink,width=2)
        d.line((320,21,355,27,395,24,431,30),fill=steel)
    elif chapter==1:
        # Blast-furnace stack with refractory bands, glowing throat and service gantry.
        d.polygon([(565,105),(574,49),(588,38),(625,38),(640,50),(649,105)],fill=(28,25,30))
        d.line((574,51,588,37,625,37,640,50),fill=steel,width=2)
        d.polygon([(582,52),(590,44),(623,44),(633,53),(628,96),(587,96)],fill=(54,39,38))
        for y in (58,70,83):
            d.line((584,y,634,y+1),fill=(102,67,53),width=2)
            d.point((588,y-1),fill=warm); d.point((629,y),fill=rust if 'rust' in locals() else (137,67,49))
        d.rectangle((592,76,624,101),fill=(20,17,22))
        d.rectangle((597,81,619,98),fill=(157,59,38))
        d.rectangle((601,84,615,96),fill=(255,112,54))
        for x in range(602,616,4): d.line((x,85,x,95),fill=(255,191,91))
        d.line((573,58,550,58,550,66),fill=steel,width=3)
        d.line((641,58,666,58,666,68),fill=steel,width=3)
        # steam manifold, valves and a hanging chain
        d.line((520,29,520,35,690,35,690,48),fill=ink,width=5)
        d.line((520,29,520,34,690,34,690,48),fill=(119,83,67),width=2)
        for x in (540,576,640,676):
            d.ellipse((x-3,30,x+3,37),outline=steel,width=1); d.line((x,24,x,31),fill=warm)
        d.line((674,48,674,80),fill=ink,width=2)
        for y in (53,61,69,77): d.point((674,y),fill=rust)
        # molten spill channel and heat shimmer
        d.polygon([(570,103),(596,99),(627,102),(652,109),(560,109)],fill=(32,22,24))
        d.line((575,105,601,102,624,105),fill=(226,91,48),width=2)
        d.line((585,108,609,106),fill=(255,145,67))
    elif chapter==2:
        # Harbor gantry crane with braced legs, cable trolley and suspended container.
        d.line((770,19,770,104),fill=ink,width=7); d.line((770,20,770,103),fill=steel,width=2)
        d.line((770,22,903,22,927,34),fill=ink,width=7)
        d.line((771,20,901,20,925,32),fill=(102,126,130),width=3)
        d.line((788,22,770,44,770,54),fill=steel,width=2)
        d.line((870,22,892,44,892,96),fill=ink,width=4)
        d.line((871,23,891,44,891,96),fill=steel,width=2)
        d.rectangle((850,26,876,33),fill=(34,53,63)); d.point((855,28),fill=t["warm"])
        d.line((862,33,862,58),fill=ink,width=2); d.line((861,34,861,58),fill=t["warm"])
        d.line((857,58,867,58,862,66,857,58),fill=steel)
        d.polygon([(824,67),(880,67),(884,100),(820,100)],fill=(24,48,58))
        d.line((824,68,879,68),fill=t["cyan"],width=2)
        for x in range(830,879,10):
            d.line((x,72,x,97),fill=(47,79,87))
            d.point((x+2,76),fill=t["warm"] if x%3==0 else t["cyan"])
        # ship hull with bow rake, deckhouse, portholes and broken wake
        d.polygon([(248,86),(292,83),(326,75),(357,79),(391,90),(418,96),(408,105),(272,105),(257,98)],fill=(13,35,48))
        d.line((250,86,292,83,326,75,357,79,391,90),fill=(81,164,171),width=2)
        d.line((267,96,399,96,409,101),fill=(38,95,110),width=2)
        d.rectangle((308,61,357,81),fill=(26,47,58))
        d.rectangle((316,65,350,75),fill=(70,105,112))
        for x in (319,330,341): d.rectangle((x,67,x+4,72),fill=(176,199,190))
        d.line((332,61,332,45,374,45),fill=steel,width=2)
        d.line((374,45,389,56),fill=ink,width=3); d.line((374,46,388,56),fill=t["warm"])
        for x in (284,301,370,388): d.ellipse((x,98,x+3,101),fill=t["warm"])
        # wet ropes and mooring bollards
        for x in (224,440,720,945):
            d.rectangle((x,99,x+5,109),fill=(39,62,69)); d.ellipse((x-2,97,x+7,101),outline=steel)
            d.line((x+2,101,x+13,105,x+23,104),fill=(66,112,122))
    elif chapter==3:
        # Grand transit arcade: deep stone arch, nested neon ribs, glazed entrance.
        d.polygon([(635,105),(641,68),(658,43),(687,29),(723,29),(751,44),(768,70),(774,105)],fill=(20,18,43))
        d.line((635,105,641,68,658,43,687,29,723,29,751,44,768,70,774,105),fill=ink,width=5)
        d.line((642,103,648,70,664,48,689,35,721,35,744,49,761,72,767,103),fill=accent,width=2)
        d.arc((654,43,754,135),180,360,fill=t["cyan"],width=3)
        d.arc((663,51,745,128),180,360,fill=mix(t["pink"],t["moon"],.32),width=2)
        d.rectangle((659,74,750,106),fill=(8,12,30))
        d.rectangle((670,79,739,105),fill=(14,18,39))
        for x in range(675,738,9):
            d.line((x,81,x,103),fill=(43,45,78),width=1)
            d.point((x+2,87),fill=t["cyan"] if x%2 else t["pink"])
        d.line((679,104,730,104),fill=t["warm"],width=2)
        # Tall illuminated blade signs and layered shop marquees
        for x,y,h,c in ((590,31,55,t["cyan"]),(785,20,68,t["pink"]),(813,45,42,t["warm"]),(550,53,35,t["pink"])):
            d.rectangle((x-3,y-2,x+5,y+h),fill=ink)
            d.line((x,y,x,y+h-2),fill=c,width=2)
            for yy in range(y+6,y+h-4,9): d.point((x+2,yy),fill=warm)
        for x,y,w,c in ((568,62,46,t["pink"]),(785,76,55,t["cyan"]),(858,58,39,t["warm"])):
            d.rectangle((x-3,y-3,x+w,y+5),fill=black)
            d.line((x,y,x+w-2,y),fill=c,width=2)
            for q in range(x+3,x+w-3,6): d.point((q,y+3),fill=mix(c,t["moon"],.4))
        # Glass canopy crossbars
        d.line((614,52,635,38,654,37),fill=steel,width=2)
        d.line((760,40,787,51,808,70),fill=steel,width=2)
    elif chapter==4:
        # Old-growth tree with branching silhouette, layered foliage clusters and rim-lit leaves.
        d.polygon([(655,106),(666,87),(672,65),(684,48),(697,30),(704,31),(700,54),(716,44),(730,29),(737,32),(729,54),(749,47),(762,53),(744,65),(728,70),(718,88),(723,106)],fill=(23,47,43))
        d.line((699,104,699,73,687,58),fill=(78,102,70),width=4)
        d.line((701,77,718,61,735,51),fill=(75,115,77),width=3)
        for x,y,rx,ry in ((673,51,15,8),(690,38,16,10),(711,34,17,9),(735,43,17,10),(750,57,15,9),(676,67,14,8),(720,63,18,9),(742,70,12,7),(692,78,12,7)):
            d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(27,66,55))
            d.arc((x-rx,y-ry,x+rx,y+ry),195,330,fill=(91,151,100),width=2)
            for ox,oy in ((-5,-2),(2,-4),(7,1),(-1,3)):
                d.point((x+ox,y+oy),fill=(121,177,111) if (x+ox)%2 else (65,132,87))
        # greenhouse conservatory: pitched glass roof, metal ribs, fogged panes.
        d.polygon([(930,103),(946,65),(1000,38),(1055,65),(1072,103)],fill=(17,39,41))
        d.line((930,103,946,65,1000,38,1055,65,1072,103),fill=(86,143,120),width=3)
        d.line((946,65,1055,65),fill=(75,123,107),width=2)
        for x in (960,980,1000,1020,1040):
            d.line((x,58+abs(x-1000)//3,x,101),fill=(66,110,98),width=2)
            d.point((x+2,75),fill=(140,192,143))
        d.line((937,91,1065,91),fill=(70,125,107),width=1)
        # tangled vines bridge the architecture and foreground.
        for x in (610,785,900,1090,1190):
            d.line((x,46,x-5,59,x+3,73,x-2,89,x+4,103),fill=(38,82,59),width=2)
            for y in (59,73,88):
                d.ellipse((x-8,y-3,x-2,y+2),fill=(55,116,72))
                d.point((x-6,y-2),fill=(129,174,103))
    else:
        # Monolithic relay bastion, stepped armored shoulders and inset reactor core.
        d.polygon([(565,105),(565,63),(585,45),(616,45),(635,31),(685,31),(706,46),(735,46),(754,67),(754,105)],fill=(21,20,39))
        d.line((565,64,585,44,616,44,635,30,685,30,706,45,735,45,754,66),fill=steel,width=2)
        d.polygon([(588,101),(588,66),(608,54),(681,54),(709,68),(731,101)],fill=(31,31,53))
        d.line((590,68,609,56,680,56,708,69),fill=(94,85,119),width=2)
        d.rectangle((630,64,674,101),fill=(8,14,31))
        d.rectangle((637,70,667,95),fill=(20,37,57))
        d.rectangle((642,75,662,90),fill=(23,93,112))
        d.line((645,78,659,78),fill=t["cyan"],width=2)
        d.line((645,83,659,83),fill=t["pink"])
        d.line((645,88,659,88),fill=t["cyan"],width=2)
        for x in (596,615,690,713):
            d.line((x,69,x,98),fill=(88,81,111),width=2)
            for y in (74,84,94): d.point((x,y),fill=t["pink"] if y==84 else steel)
        # Signal mast and directional microwave dishes with braced stays.
        d.line((651,31,651,3),fill=ink,width=5); d.line((651,30,651,3),fill=steel,width=2)
        d.line((651,12,625,24,651,21,679,34),fill=ink,width=3)
        d.line((651,12,625,24,651,21,679,34),fill=t["cyan"],width=1)
        d.ellipse((604,28,632,53),outline=steel,width=2)
        d.arc((607,31,629,51),205,335,fill=t["pink"],width=2)
        d.line((617,40,651,18),fill=ink,width=2)
        d.line((679,34,700,17,715,17),fill=ink,width=2)
        d.line((679,33,700,16,715,16),fill=t["warm"])
        # Cable trench and signal pylons
        for x in (540,760,810,1130):
            d.line((x,17,x,104),fill=ink,width=3); d.line((x+1,18,x+1,103),fill=(67,64,92))
            for y in (27,48,69,90): d.point((x+2,y),fill=t["cyan"] if y%2 else t["pink"])
        d.line((0,17,550,25,820,18,1400,24),fill=ink,width=2)
        d.line((0,18,550,26,820,19,1400,25),fill=steel)
    # Material micro-detail: chipped edges, rivets, window reflections and local bounce.
    # Deliberately deterministic, irregular clusters avoid a procedural tiled appearance.
    rng=random.Random(90210+chapter*313)
    for i in range(190):
        x=rng.randrange(18,W-18); y=rng.randrange(12,104)
        if i%5==0:
            c=mix(t["haze"],t["moon"],rng.uniform(.12,.34))
            d.point((x,y),fill=c)
        elif i%5==1:
            d.line((x,y,min(W-1,x+rng.randint(2,7)),y),fill=mix(t["near"],t["moon"],.18))
        elif i%5==2:
            d.point((x,y),fill=mix(t["sky"],t["cyan"],.38))
        elif i%5==3:
            d.point((x,y),fill=mix(t["near"],t["warm"],.25))
    # Foreground rain glints are short, broken reflections tied to nearby light sources.
    for x,y,c in ((370,113,t["pink"]),(455,116,t["warm"]),(640,111,t["cyan"]),(875,115,t["cyan"]),(1010,112,t["warm"]),(1210,116,t["pink"])):
        d.line((x,y,x+13,y),fill=mix(t["street"],c,.42),width=1)
        d.point((x+3,y-1),fill=mix(t["street"],c,.58))


def draw_facade_sculpture_pass(im, chapter, t):
    """Break up procedural facade rhythm with three district-specific architectural anchors."""
    d=ImageDraw.Draw(im)
    rng=random.Random(55190+chapter*211)
    ink=mix(t["sky"],t["street"],.30)
    steel=mix(t["mid"],t["moon"],.42)
    warm=mix(t["warm"],t["haze"],.20)
    cyan=mix(t["cyan"],t["mid"],.18)
    # Keep the signature structures in clear gaps between each chapter's main landmark.
    anchors=[
        (105,760,1190),(115,865,1190),(75,1080,1280),
        (115,340,1110),(125,390,1280),(120,960,1205)
    ][chapter]
    for idx,x in enumerate(anchors):
        w=(82,104,92)[idx]
        top=(rng.randint(30,47),rng.randint(24,42),rng.randint(35,52))[idx]
        base=103
        wall=mix(t["far"] if idx==0 else t["mid"],t["haze"],.20+rng.random()*.12)
        shade=mix(wall,ink,.55)
        edge=mix(wall,t["moon"],.32)
        # A stepped, offset crown gives each anchor a distinct skyline silhouette.
        d.polygon([(x,top+9),(x+9,top+9),(x+9,top+2),(x+28,top+2),
                   (x+28,top-5),(x+w-18,top-5),(x+w-18,top+4),
                   (x+w-5,top+4),(x+w,top+12),(x+w,base),(x,base)],fill=wall)
        d.line((x+9,top+2,x+28,top+2,x+28,top-5,x+w-18,top-5,
                x+w-18,top+4,x+w-5,top+4),fill=edge,width=2)
        # Deep vertical bays and uneven window groups, deliberately not a regular grid.
        for bx,by,bw,bh in ((x+13,top+18,13,19),(x+37,top+11,17,27),
                             (x+64,top+23,11,16)):
            d.rectangle((bx-2,by-2,bx+bw+2,by+bh+2),fill=shade)
            d.rectangle((bx,by,bx+bw,by+bh),fill=mix(wall,ink,.28))
            d.line((bx+2,by+2,bx+bw-2,by+2),fill=cyan)
            d.line((bx+2,by+bh-2,bx+bw-2,by+bh-2),fill=mix(edge,wall,.35))
            d.line((bx+bw//2,by+3,bx+bw//2,by+bh-3),fill=shade)
            if (idx+chapter)%2==0:
                d.rectangle((bx+3,by+5,bx+bw//2-1,by+bh//2),fill=mix(t["warm"],wall,.28))
        if chapter==0:
            # Market building: projecting timber balconies, hanging sign and folded awning.
            for yy in (top+33,top+53):
                d.line((x+5,yy,x+w-5,yy),fill=shade,width=3)
                d.line((x+8,yy+2,x+8,yy+8),fill=edge)
                d.line((x+w-9,yy+2,x+w-9,yy+8),fill=edge)
            d.polygon([(x+20,top+42),(x+59,top+42),(x+65,top+48),(x+15,top+48)],fill=t["pink"])
            d.line((x+24,top+44,x+59,top+44),fill=warm,width=1)
            d.line((x+75,top+10,x+75,top+28),fill=ink,width=2)
            d.rectangle((x+68,top+27,x+83,top+38),fill=shade)
            d.line((x+70,top+29,x+81,top+29),fill=t["warm"],width=2)
        elif chapter==1:
            # Foundry block: huge segmented exhaust, pressure pipes and riveted braces.
            d.rectangle((x+48,top-12,x+69,top+8),fill=shade)
            d.rectangle((x+52,top-16,x+65,top-12),fill=edge)
            for yy in range(top+18,base-7,8):
                d.line((x+4,yy,x+w-5,yy),fill=mix(wall,t["moon"],.13))
                d.point((x+7,yy+1),fill=warm); d.point((x+w-8,yy+1),fill=warm)
            d.line((x+24,top+9,x+24,base-5),fill=edge,width=2)
            d.line((x+29,top+9,x+29,base-5),fill=shade)
            d.line((x+35,top+19,x+43,top+27,x+35,top+35),fill=warm,width=2)
        elif chapter==2:
            # Harbor shed: sawtooth roof, loading gantry and corrugated sliding doors.
            d.polygon([(x+4,top+8),(x+25,top-5),(x+48,top+8),(x+70,top-5),(x+w,top+8)],fill=shade)
            d.line((x+4,top+8,x+25,top-5,x+48,top+8,x+70,top-5,x+w,top+8),fill=edge,width=2)
            d.rectangle((x+18,top+48,x+61,base),fill=shade)
            for xx in range(x+22,x+60,6):
                d.line((xx,top+51,xx,base-3),fill=mix(t["cyan"],wall,.48))
            d.line((x+12,top+37,x+w-8,top+37),fill=t["cyan"],width=2)
            d.line((x+14,top+34,x+14,top+43),fill=edge)
            d.line((x+w-12,top+34,x+w-12,top+43),fill=edge)
        elif chapter==3:
            # Arcade tower: vertical neon fins, layered marquee and a recessed glass spine.
            for xx in (x+12,x+29,x+74):
                d.rectangle((xx,top+7,xx+4,base-4),fill=shade)
                d.line((xx+2,top+10,xx+2,base-8),fill=t["pink"] if xx%2 else t["cyan"],width=2)
            d.rectangle((x+34,top+38,x+68,base-4),fill=shade)
            d.rectangle((x+37,top+41,x+65,base-7),fill=mix(t["cyan"],wall,.55))
            for yy in range(top+44,base-8,8):
                d.line((x+39,yy,x+63,yy),fill=mix(t["moon"],t["cyan"],.25))
            d.polygon([(x+5,top+30),(x+80,top+30),(x+73,top+36),(x+10,top+36)],fill=t["pink"])
        elif chapter==4:
            # Garden house: broken gable, timber braces, ivy and illuminated planters.
            d.polygon([(x+4,top+15),(x+25,top-8),(x+51,top+4),(x+78,top-4),(x+w,top+17)],fill=shade)
            d.line((x+4,top+15,x+25,top-8,x+51,top+4,x+78,top-4,x+w,top+17),fill=edge,width=2)
            for xx in (x+11,x+w-13):
                d.line((xx,top+29,xx-3,base-5),fill=(42,96,67),width=2)
                for yy in range(top+37,base-8,12):
                    d.ellipse((xx-5,yy-3,xx+2,yy+3),fill=(49,112,72))
            d.rectangle((x+32,base-12,x+61,base-6),fill=(34,82,55))
            for xx in range(x+35,x+60,7): d.point((xx,base-10),fill=t["cyan"])
        else:
            # Signal bastion: armored buttresses, observation slits and exposed cable runs.
            for xx in (x+8,x+31,x+w-15):
                d.polygon([(xx,top+16),(xx+8,top+10),(xx+13,base),(xx+4,base)],fill=shade)
                d.line((xx+7,top+15,xx+10,base-3),fill=edge)
            for yy in (top+30,top+51,top+72):
                d.line((x+16,yy,x+w-18,yy),fill=shade,width=3)
            d.rectangle((x+48,top+24,x+59,top+39),fill=ink)
            d.line((x+53,top+27,x+53,top+36),fill=t["cyan"],width=2)
            d.line((x+w-7,top+4,x+w-7,base-3),fill=t["pink"],width=2)
        # Grounded contact shadow, bolts and a few chipped masonry highlights.
        d.line((x+3,base-1,x+w-2,base-1),fill=ink,width=2)
        for j in range(7):
            bx=x+8+(j*13+idx*5)%(w-16); by=top+14+(j*11)%(base-top-20)
            d.point((bx,by),fill=edge if j%2 else shade)

def chapter_scene(ch):
    t=THEMES[ch]; rng=random.Random(3200+ch*901)
    im=Image.new("RGB",(W,H),t["sky"]); d=ImageDraw.Draw(im)
    for y in range(H):
        c=mix(t["sky"],t["haze"],min(1,y/78))
        if y>74: c=mix(t["haze"],t["street"],(y-74)/46)
        d.line((0,y,W,y),fill=c)
    # Sparse stepped cloud bands and distant aircraft beacons.
    for i in range(24):
        x=(i*61+ch*37)%W; y=10+(i*19)%43
        d.line((x,y,x+8+(i%9)*3,y),fill=mix(t["sky"],t["haze"],.45),width=1)
        if i%5==0: d.point((x+3,y+2),fill=t["cyan"])
    # District-specific neon haze: stepped light pools behind the roofline, quantised to pixel bands.
    glow_sources={
        0:[(180,t["pink"]),(760,t["warm"]),(1210,t["cyan"])],
        1:[(330,t["warm"]),(1030,t["pink"])],
        2:[(220,t["cyan"]),(930,t["warm"])],
        3:[(140,t["pink"]),(520,t["cyan"]),(1110,t["pink"])],
        4:[(390,t["cyan"]),(1050,t["warm"])],
        5:[(260,t["pink"]),(700,t["cyan"]),(1190,t["warm"])]
    }[ch]
    for sx, hue in glow_sources:
        for band in range(11):
            y=34+band*3
            spread=24+band*13
            strength=max(.04,.24-band*.014)
            d.line((max(0,sx-spread),y,min(W-1,sx+spread),y),
                   fill=mix(t["haze"],hue,strength),width=1)
    draw_skyline(im,ch,t)
    # Ground plane: layered curb, rail glints and reflection streaks with irregular breaks.
    d=ImageDraw.Draw(im)
    d.rectangle((0,92,W,119),fill=t["street"])
    d.line((0,92,W,92),fill=mix(t["near"],t["cyan"],.25),width=1)
    for i in range(120):
        x=(i*113+ch*29)%W; y=95+(i*7)%22
        color=mix(t["street"],(t["cyan"] if i%3 else t["pink"]),.18 if i%2 else .34)
        d.line((x,y,x+1+(i*7)%13,y),fill=color,width=1+(i%4==0))
    for x in range(0,W,91):
        d.line((x,115,x+7,115),fill=mix(t["street"],t["cyan"],.34),width=1)
    # Composite the continuous frontage last so its sidewalk, doors and curb are not buried by the road pass.
    draw_street_frontage(im,ch,t)
    draw_facade_sculpture_pass(im,ch,t)
    draw_district_landmarks(im,ch,t)
    draw_art_direction_pass(im,ch,t)
    # A few foreground cable/roof fragments frame the panoramic composition.
    for x in (20,430,870,1280):
        d.line((x,3,x+46,8,x+94,5),fill=(4,7,16),width=2)
        d.line((x,2,x+46,7,x+94,4),fill=mix(t["street"],t["cyan"],.38),width=1)
    return im

ACTORS = {
 "guard": [
  ".........kkkkkk.........","........kddddddk........","........kmmhhhhmk.......",
  "........kdhccccdk.......","........kddccccdk.......",".........kddddk.........",
  ".....kkkddmmmmddkkk.....","...kkdmmhhddddhhmm dkk...".replace(" ",""),
  "..kddmhhmmddddmmhhmddk..",".kddmhhmddmwwmddmhhmddk.",
  "kddmddmmddmddmddmmddmddk","kddmddmmddmppmddmmddmddk",
  ".kddmmhddmddddmddhmmddk..","..kkdmmddmhhhhmddmm dkk...".replace(" ",""),
  "...kkddmmddddddmmddkk....","....kddmddmmmmddmddk.....",
  "...kkdddk......kdddkk....","..kkdddmk......kdmddkk...",
  ".kkdddmkk......kkmdddkk..","kkmhhkk............kkhhmkk",
  "kkmmkk..............kkmmkk"
 ],
 "shooter": [
  ".........kkkkkk...............","........kddddddk..............","........kmmhhhhmk.............",
  "........kdhccccdk.............","........kddccccdk.............",".........kddddk...............",
  ".....kkkddmmmmddkkk...........","...kkdmmhhddddhhmm dkk.........".replace(" ",""),
  "..kddmhhmmddddmmhhmddk.........",".kddmhhmddmwwmddmhhmddk........",
  "kddmddmmddmddmddmmddmddk.......","kddmddmmddmppmddmmddmddk.......",
  ".kddmmhddmddddmddhmmddk.........","..kkdmmddmhhhhmddmm dkk........".replace(" ",""),
  "...kkddmmddddddmmddkk....kkkkkkkk","....kddmddmmmmddmddk....kmmmmmmmk",
  "...kkdddk......kdddkk....kcccccck","..kkdddmk......kdmddkk..kddddddk",
  ".kkdddmkk......kkmdddkk.kkkkkkkkkk","kkmhhkk............kkhhmkk",
  "kkmmkk..............kkmmkk"
 ],
 "hunter": [
  ".........kkkk.............","........kddddk............","........kmmhhmk...........",
  "........kdhccdk...........","........kddccdk...........",".........kdddk............",
  ".....kkkddmmmmkk..........","...kkdmmhhddddmddkk.......",
  "..kddmhhddmdddhmdddk......",".kddmppddmwwddmmdddk......",
  "kddmmppddmdddddmmdddk......","kddmddmmddppdddmdddk.......",
  ".kddmmhddmddddmddmmk.......","..kkdmmddmhhhhmddkk........",
  "...kkddmmddddmmddkk.........","....kddmddmmddmddk.........",
  "...kkdddk......kdddkk.......","..kkdddmk......kdmddkk......",
  ".kkdddmkk......kkmdddkk.....","kkmhhkk............kkhhmkk",
  "kkmmkk..............kkmmkk"
 ],
 "aberration": [
  "........kkkkkkkk........",".....kkkddddddddkkk......","...kkddmmhhhhhhmmddkk....",
  "..kddmmhhddddddhhmmddk...",".kddmmhddppppppddhmmddk..","kddmmhddpwwccwwpdhmmddk.",
  "kddmmhddpppccpppdhmmddk..",".kddmmhhddppppddhhmmddk..","..kddmmhhddddddhhmmddk...",
  "...kkddmmhddddhhmmddkk....",".....kkdmmhhhhmmddkk......",
  "...kkdmmddkkkkddmmddkk....","..kddmmddk....kddmmddk....",
  ".kddmmddk......kddmmddk...","kddmmddk........kddmmddk..",
  ".kkdddk..........kdddkk...","..kkmkk..........kkmkk...."
 ]
}
BOSSES = {
 "warden": [
  "..............kkkkkk..............","............kkddddddkk............",
  "..........kkddmmhhhhmmddkk.........",".........kddmmhddddddhmmddk........",
  "........kddmmhddwwwwddhmmddk.......",".......kddmmhddwccccwddhmmddk......",
  "......kddmmhhddddddddddhhmmddk......","....kkddmmhhhhmmmmmmmmhhhhmmddkk....",
  "..kkddmmhddmmmmmmmmmmmmmmmmddhmmddkk..",
  ".kddmmhddmhhddppppppddhhmdmhhmmddk...",
  "kddmmhddmhhddddddddddddhhmdmhhmmddk...",
  "kddmmhhddmccddmmmmddccmddhhmmddk......",
  "kddmmhhddmccddmmmmddccmddhhmmddk......",
  ".kddmmhhddmmmmmmmmmmmmddhhmmddk........",
  "..kkddmmhhmhhhhhhhhhhmhhmmddkk..........",
  "....kkddmmddddddddddddddmmddkk...........",
  ".....kkddmmddmmmmmmmmddmmddkk............",
  "......kkdmmddmddddddmddmddkk.............",
  ".....kkddmddkk......kkddmddkk............",
  "...kkmmhkk............kkhmmkk............",
  "..kkmmkk..............kkmmkk............."
 ],
 "kair": [
  "...............kkkk...............",".............kkddddkk.............",
  "............kddmmhhddk............","............kddmhhhhmdk...........",
  "............kddmwwwwmdk............",".............kddmmmmdk.............",
  "...........kkddmmppmmddkk...........",
  "..........kddmhhddddhhmmddk..........",
  ".........kddmhhmddddmhhmmddk.........",
  "........kddmmhhmccccmhhmmddk........",
  ".......kddmmhhmddddddmhhmmddk.......",
  "......kddmmhhmppppppppmhhmmddk......",
  ".....kddmmhhmddddddddddmhhmmddk.....",
  "....kddmmhhmddhhhhhhhhddmhhmmddk....",
  "...kddmmhhmddmmmmmmmmmmddmhhmmddk...",
  "..kddmmhhmddmddddddddddmddmhhmmddk..",
  ".kddmmhhmddmddmmmmmmddmddmhhmmddk...",
  "kddmmhhmddmddmddddddmddmddmhhmmddk...",
  "kkddmmddkkddkk......kkddkkddmmddkk.....",
  "..kkmmkk....kk......kk....kkmmkk.......",
  "....kk..........................kk....."
 ],
 "double": [
  ".....kkkkkk.............kkkkkk.....",
  "...kkddddddkk.........kkddddddkk...",
  "..kddmmhhhhmmddk.....kddmmhhhhmmddk..",
  ".kddmhhcccc hhmdk...kdmhcc cc hhmdk.".replace(" ",""),
  "kddmhhddddddddhmmddkddmmhddddddddhhmddk",
  "kddmmhppppppmmddk.kddmmpppppphmmddk",
  "kddmmhddddddhmmddkddmmhddddddhmmddk",
  ".kddmmhhddddhhmmddkkddmmhhddddhhmmddk.",
  "..kkddmmhhhhmmddkk..kkddmmhhhhmmddkk..",
  "....kkddmmmmddkk......kkddmmmmddkk....",
  "...kddmmddmmddk........kddmmddmmddk...",
  "..kddmmk..kddmmk......kmmddk..kmmddk..",
  ".kddmmk....kddmmk....kmmddk....kmmddk.",
  "kkmmkk......kkmmkk..kkmmkk......kkmmkk",
  ".kkddmhhhhmddkk......kkddmhhhhmddkk.",
  "..kkddmccccmddkk....kkddmccccmddkk..",
  "...kkddmmddmmddkk..kkddmmddmmddkk...",
  "....kkdddk..kdddk....kdddk..kdddk....",
  "...kkmmkk....kkmmkk..kkmmkk....kkmmkk",
  "..kkmkk........kkmkk..kkmkk........kkmkk"
 ],
 "surgeon": [
  ".............kkkkkk............","..........kkkddddddkkk.........",
  ".........kddmmhhhhhmmddk........","........kddmmhhhhhhhmmddk.......",
  ".......kddmmhhwwwww hhmmddk......".replace(" ",""),
  "......kddmmhhwcccccwhhmmddk.....",".....kddmmhhddddddddhhmmddk....",
  "....kddmmhhddppppppddhhmmddk...","...kddmmhhddppppppppddhhmmddk..",
  "..kddmmhhddmddddddddmddhhmmddk..",
  ".kddmmhhddmccddddccdmddhhmmddk..",
  "kddmmhhddmdddddddddddmddhhmmddk.",
  ".kddmmhhddmmmmmmmmmmmmddhhmmddk..",
  "..kkddmmhhhhhhhhhhhhhhmmddkk....",
  "...kkddmmddddddddddddddmmddkk.....",
  "....kkddmmddkkkkkkkddmmddkk........",
  "...kkddmmddk.......kddmmddkk.......",
  "..kkddmmddk.........kddmmddkk......",
  ".kkmmddkk.............kkddmmkk......",
  "kkmmkk...................kkmmkk....."
 ],
 "watcher": [
  "..............kkkkkk..............","..........kkkkddddddkkkk..........",
  ".......kkkddmmmmhhhhmmmmddkkk......",
  "....kkddmmhhddddddddddddhhmmddkk....",
  "...kddmmhhdddwwwwwwwwddddhhmmddk...",
  "..kddmmhhddwwccccccwwddhhmmddk......",
  ".kddmmhhddwccmmmmmmccwddhhmmddk.....",
  "kddmmhhddwcmhhhhhhm mcwddhhmmddk...".replace(" ",""),
  "kddmmhhddwcmhwwwwwwhm mcwddhhmmddk.".replace(" ",""),
  ".kddmmhhddwcmhhhhhhm mcwddhhmmddk...".replace(" ",""),
  "..kddmmhhddwwccccccwwddhhmmddk......",
  "...kddmmhhdddwwwwwwwwddddhhmmddk....",
  "....kkddmmhhddddddddddhhmmddkk......",
  "......kkddmmhhhhhhhhhhmmddkk.........",
  "........kkkddddddddddkkk............",
  ".........kkddmmmmmmddkk..............",
  "..........kkddccccddkk...............",
  "...........kkddddddkk................"
 ],
 "sentry": [
  "..............kkkkkk..............","............kkddddddkk............",
  "..........kkddmmhhhhmmddkk.........",
  ".........kddmmhhcccc hhmmddk........".replace(" ",""),
  "........kddmmhhddddddhhmmddk........",
  ".......kddmmhhddppddhhmmddk.......",
  "......kddmmhhddddddddhhmmddk......",
  ".....kddmmhhddmmmmmmddhhmmddk.....",
  "....kddmmhhddmwwwwwwmddhhmmddk....",
  "...kddmmhhddmwwccccwwmddhhmmddk...",
  "....kddmmhhddmmmmmmmmddhhmmddk....",
  ".....kkddmmhhhhhhhhhhmmddkk.........",
  ".......kkkddddddddddkkk............",
  ".........kkddmmmmddkk..............",
  ".........kkddmkkmddkk...............",
  "......kkkmmkk...kkmmkkk..............",
  ".....kkmmkk.......kkmmkk............."
 ]
}
ACTOR_PALETTE = dict(PALETTE)
def make_actor(rows, size, frame, kind, boss=False):
    # Trim transparent map margins, keep square source pixels, and scale with nearest-neighbour.
    rows=[row.strip(".") for row in rows]
    if boss:
        # The boss maps are designed as compact pixel sketches; duplicate rows
        # to expand the vertical anatomy while retaining square pixel clusters.
        rows=[row for row in rows for _ in range(2)]
    maxw=max(map(len,rows)); maxh=len(rows)
    # Six-frame pose cycle: small pixel-grid body bob and opposing leg swing.
    bob=(0,-1,-1,0,1,0)[frame%6]
    maxh += abs(bob)
    cell=max(1,min((size[0]-4)//max(map(len,rows)),(size[1]-4)//len(rows)))
    im=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(im)
    ox=(size[0]-max(map(len,rows))*cell)//2; oy=(size[1]-len(rows)*cell)//2+bob*cell
    for y,row in enumerate(rows):
        for x,ch in enumerate(row):
            col=ACTOR_PALETTE.get(ch)
            if col is None: continue
            # Animation changes small authored highlight clusters, not whole-body geometry.
            if ch=="p" and frame%3==1: col=(248,105,169)
            if ch=="c" and frame%2: col=(130,242,250)
            if ch=="w" and frame in (2,3): col=(255,225,164)
            if boss and ch in ("h","m") and frame in (1,2,4,5):
                col=mix(col, (126,231,241), .18 if ch=="h" else .10)
            # Walking frames shift the lower-leg pixel clusters in opposite directions.
            if not boss and y >= maxh-5 and frame in (1,2,4,5):
                x_shift = (1 if x < maxw//2 else -1) if frame in (1,2) else (-1 if x < maxw//2 else 1)
            elif boss and y >= int(maxh*.22) and y <= int(maxh*.62) and frame in (1,2,4,5) and (x < maxw*.18 or x > maxw*.82):
                # Heavy boss idle: shoulder plates and hanging arms move in an opposing rhythm.
                x_shift = (-1 if x < maxw*.5 else 1) if frame in (1,2) else (1 if x < maxw*.5 else -1)
            elif not boss and y >= int(maxh*.27) and y <= int(maxh*.60) and frame in (1,2,4,5):
                # Opposing shoulder/forearm motion produces a readable six-frame gait.
                if x < maxw*.22:
                    x_shift = -1 if frame in (1,2) else 1
                elif x > maxw*.78:
                    x_shift = 1 if frame in (1,2) else -1
                else:
                    x_shift = 0
            else:
                x_shift = 0
            xx=ox+(x+x_shift)*cell; yy=oy+y*cell
            d.rectangle((xx,yy,xx+cell-1,yy+cell-1),fill=(*col,255))
    if boss:
        # Chest rune and eye glow breathe over the idle loop; arm plates move above.
        x=size[0]//2+(frame%3-1)*2; y=size[1]//3
        rune=(150,245,255,255) if frame in (2,3) else (76,195,227,255)
        d.point((x,y),fill=rune)
        d.point((x+1,y),fill=rune)
        d.point((x,y+1),fill=(255,116,177,255) if frame in (3,4) else rune)
    else:
        # Individual blade / scarf glint advances one pixel at a time.
        x=size[0]-5-(frame%3); y=size[1]//2+frame%2
        d.point((x,y),fill=(255,124,181,255))
    return im

def save_animation():
    # Four enemy silhouettes, six idle/combat frames each.
    for kind,rows in ACTORS.items():
        for i in range(6):
            frame=make_actor(rows,(60,64),i,kind)
            frame.save(CH/f"{kind}_{i}.png",optimize=True)
            if i==0: frame.save(CH/f"{kind}.png",optimize=True)
    # Six large boss sprites; each design has a separate hand-authored silhouette.
    for kind,rows in BOSSES.items():
        for i in range(6):
            frame=make_actor(rows,(96,112),i,kind,True)
            frame.save(CH/f"boss_{kind}_{i}.png",optimize=True)
            if i==0: frame.save(CH/f"boss_{kind}.png",optimize=True)

def save_weather():
    # Pixel sprites for animated rain, falling petals, chimney steam, windows and reflections.
    sprites={
      "pixel_rain":["....c.","...cc.","..c...","cc....","c....."],
      "pixel_steam":["...hh...","..h..h..",".h....h.","h......h","..h..h..","...hh..."],
      "pixel_window":["kkkkkk","kccddk","kccddk","kddwwk","kkkkkk"],
      "pixel_reflection":["..............","..cccc........",".....ccccc....","..........cc..","...ppp........",".............."]
    }
    for i in range(6):
        petal=[
          "....pp....","...pppp...","..pphhpp..",".pphhhhpp.",
          "..pphhpp..","...pppp...","....pp....",".....p...."
        ]
        im=Image.new("RGBA",(10,10),(0,0,0,0)); draw_map(im,0,1,petal,scale=1)
        d=ImageDraw.Draw(im); d.point((2+i%3,5),fill=(255,181,208,255))
        im.save(FX/f"pixel_petal_{i}.png",optimize=True)
    for name,rows in sprites.items():
        im=Image.new("RGBA",(len(rows[0]),len(rows)),(0,0,0,0))
        # Transparent palette is preserved; maps are deliberately sparse.
        for y,row in enumerate(rows):
            for x,ch in enumerate(row):
                c=PALETTE.get(ch)
                if c and name=="pixel_steam":
                    # Three-tone cool steam: lit crest, body midtone, transparent blue-grey fringe.
                    steam_palette={
                      (0,0):(222,235,239,225),(1,0):(188,211,222,205),(2,0):(157,190,207,180),
                      (3,0):(126,165,188,150),(4,0):(154,190,207,175),(5,0):(191,215,225,205),(6,0):(220,234,239,220),
                      (1,1):(174,204,218,190),(2,1):(139,177,198,165),(3,1):(113,155,180,145),(4,1):(137,177,198,165),(5,1):(177,207,220,190),
                      (0,2):(139,178,198,160),(1,2):(121,164,187,145),(2,2):(111,154,180,135),(5,2):(126,170,192,145),(6,2):(145,184,202,160),
                      (0,3):(118,158,183,135),(1,3):(105,149,176,125),(5,3):(112,156,181,130),(6,3):(126,168,190,140),
                      (1,4):(153,188,207,160),(2,4):(128,170,192,145),(4,4):(133,174,195,150),(5,4):(163,197,213,170),
                      (2,5):(185,211,224,185),(3,5):(158,191,209,165),(4,5):(190,215,226,190)
                    }
                    rgba=steam_palette.get((x,y),(c[0],c[1],c[2],110))
                    im.putpixel((x,y),rgba)
                elif c: im.putpixel((x,y),(*c,255))
        im.save(FX/f"{name}.png",optimize=True)
def save_foreground(ch):
    t=THEMES[ch]; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    for x in (28,330,710,1080,1340):
        d.line((x,0,x+34,7,x+78,4),fill=(3,5,13,235),width=2)
        d.point((x+32,6),fill=(*t["cyan"],180))
    for x in (12,1380):
        rows=["..kkkk..",".kddddk.","kddccddk","kddccddk","kddccddk",".kddddk.","..kkkk.."]
        temp=Image.new("RGBA",(8,7),(0,0,0,0))
        for y,row in enumerate(rows):
            for rx,ch in enumerate(row):
                c=PALETTE.get(ch)
                if c: temp.putpixel((rx,y),(*c,230))
        im.alpha_composite(temp,(x-4,73))
    im.resize((W*S,H*S),Image.Resampling.NEAREST).save(BG/f"foreground_{ch}.png",optimize=True)
def write_backgrounds():
    signatures=set()
    for ch in range(6):
        im=chapter_scene(ch)
        final=im.resize((W*S,H*S),Image.Resampling.NEAREST).convert('RGBA')
        d=ImageDraw.Draw(final,'RGBA')
        rng=random.Random(48100+ch*733); t=THEMES[ch]
        # Grounded wall pilasters and drainpipes run continuously to the pavement.
        for x in range(70,4140,157):
            top=rng.randint(135,180); bottom=rng.randint(252,278); w=rng.choice((5,7,9,12))
            d.rectangle((x,top,x+w,bottom),fill=(3,6,15,90))
            d.line((x+w+1,top+3,x+w+1,bottom-2),fill=(*t['moon'],75),width=2)
            if rng.random()<.55:
                px=x+rng.randint(14,38)
                d.line((px,top-5,px,bottom+28),fill=(5,8,17,235),width=4)
                d.line((px+1,top-5,px+1,bottom+28),fill=(*t['moon'],90),width=1)
                for yy in range(top+25,bottom,34): d.line((px-5,yy,px+5,yy),fill=(*t['warm'],115),width=2)
        # Recessed windows, reflected panes and occasional lit interiors.
        for _ in range(190):
            x=rng.randrange(18,4180); y=rng.randrange(145,258); ww=rng.choice((7,9,12,16)); hh=rng.choice((9,12,15))
            d.rectangle((x-2,y-2,x+ww+2,y+hh+2),fill=(3,6,15,185))
            glass=t['cyan'] if rng.random()<.56 else t['warm']; alpha=rng.randint(75,155) if rng.random()<.27 else rng.randint(18,60)
            d.rectangle((x,y,x+ww,y+hh),fill=(*glass,alpha))
            d.line((x+1,y+1,x+ww-1,y+1),fill=(220,238,246,min(150,alpha+35)),width=1)
        # Wall-mounted awnings have brackets and hanging supports.
        for x in range(110,4100,317):
            y=rng.randint(208,246); width=rng.randint(38,76); accent=t['pink'] if rng.random()<.5 else t['cyan']
            d.rectangle((x,y,x+width,y+5),fill=(5,8,18,230),outline=(*accent,190),width=1)
            for k in range(0,width,8): d.line((x+k,y+6,x+k+3,y+13),fill=(*accent,125),width=2)
            d.line((x+5,y+14,x+5,y+24),fill=(5,8,18,220),width=2)
            d.line((x+width-5,y+14,x+width-5,y+24),fill=(5,8,18,220),width=2)
        # Street fixtures rise from the pavement and cast connected shadows.
        for x in range(100,4200,389):
            base=352; h=rng.randint(22,42)
            d.ellipse((x-20,base-5,x+28,base+2),fill=(0,0,0,110))
            d.rectangle((x-3,base-h,x+3,base),fill=(7,10,19,235))
            d.rectangle((x-7,base-h-4,x+7,base-h+3),fill=(6,9,18,245),outline=(*t['cyan'],150),width=1)
        # Converging pavement seams and reflections stay on the road surface.
        for x in range(0,4200,210): d.line((x,359,x+int((2100-x)*.035),281),fill=(90,115,145,28),width=1)
        for _ in range(150):
            x=rng.randrange(4200); y=rng.randrange(286,356); length=rng.randint(5,52); hue=t['cyan'] if rng.random()<.62 else t['pink']
            d.line((x,y,min(4199,x+length),y+rng.choice((-1,0,1))),fill=(*hue,rng.randint(20,75)),width=rng.choice((1,2,3)))
        final.convert('RGB').save(BG/f'act_{ch}.png',optimize=True)
        save_foreground(ch)
        signatures.add(im.resize((140,12),Image.Resampling.NEAREST).tobytes())
    assert len(signatures)==6,"Chapter scenes must be visually distinct"
def cinematic_panel(ch):
    """A dedicated 16:9 pixel-art establishing shot; never stretch a 1400x120 panorama."""
    t=THEMES[ch]; rng=random.Random(8800+ch*71)
    im=Image.new("RGB",(320,180),t["sky"]); d=ImageDraw.Draw(im)
    for y in range(180):
        amt=min(1.0,y/142.0)
        col=mix(t["sky"],t["haze"],amt*.78)
        if y>112: col=mix(t["haze"],t["street"],(y-112)/68)
        d.line((0,y,319,y),fill=col)
    # Sparse cloud fragments and distant signal lights on the upper third.
    for i in range(28):
        x=(i*43+ch*29)%320; y=13+(i*17)%66
        if i%4==0:
            d.point((x,y),fill=mix(t["haze"],t["moon"],.22))
            d.point((x+1,y),fill=mix(t["haze"],t["moon"],.22))
        elif i%3==0:
            d.line((x,y,x+3+(i%5),y),fill=mix(t["sky"],t["haze"],.56),width=1)
    # Distant towers use thin, staggered pixel courses to leave clear negative space.
    x=-8
    while x<328:
        bw=rng.randint(13,27); bh=rng.randint(26,62); top=118-bh
        body=mix(t["far"],t["haze"],.12)
        for yy in range(bh):
            inset=(3 if yy<2 else 1 if yy<5 else 0) if (x//17+ch)%3==0 else (1 if yy<3 else 0)
            for xx in range(inset,bw-inset):
                color=mix(body,t["sky"],.24) if xx==bw-inset-1 else body
                d.point((x+xx,top+yy),fill=color)
        for wy in range(top+8,116,8):
            for wx in range(x+3,x+bw-3,5):
                if rng.random()<.28:
                    color=t["warm"] if rng.random()<.25 else mix(body,t["cyan"],.36)
                    d.point((wx,wy),fill=color)
                    if rng.random()<.4: d.point((wx+1,wy),fill=color)
        x+=bw+rng.randint(3,8)
    # Landmark compositions are distinct and are drawn from authored pixel maps.
    tint={"c":t["cyan"],"p":t["pink"],"w":t["warm"]}
    setpieces={
      0:[("shop",49,61,3),("train",185,83,2)],
      1:[("furnace",48,58,3),("crane",188,58,2)],
      2:[("ship",34,101,3),("crane",188,52,2)],
      3:[("tower",92,17,3),("radar",208,76,2)],
      4:[("tree",52,73,4),("greenhouse",176,92,2)],
      5:[("radar",47,67,3),("relay",196,49,2)]
    }[ch]
    for name,sx,sy,scale in setpieces: draw_map(im,sx,sy,MAPS[name],tint,scale)
    d=ImageDraw.Draw(im)
    # Foreground silhouettes anchor the shot, with broken curb reflections and cable ends.
    d.line((0,148,319,148),fill=mix(t["near"],t["cyan"],.20),width=1)
    for x in range(0,320,29):
        height=6+(x*7+ch*11)%20
        for yy in range(180-height,180):
            d.point((x,yy),fill=mix(t["street"],t["near"],.34))
            if x%3==0: d.point((x+1,yy),fill=mix(t["street"],t["near"],.25))
        if x%2==0:
            d.point((x+2,180-height),fill=mix(t["near"],t["cyan"],.18))
    for i in range(35):
        x=(i*47+ch*13)%318; y=151+(i*7)%26
        c=mix(t["street"],t["cyan"] if i%2 else t["pink"],.22 if i%3 else .42)
        d.line((x,y,min(319,x+2+(i*5)%10),y),fill=c,width=1)
    # A few close rain streaks and deliberate neon glints finish the composition.
    for i in range(25):
        x=(i*61+ch*23)%319; y=30+(i*19)%110
        if i%3==0: d.point((x,y),fill=mix(t["sky"],t["cyan"],.72))
    d.point((160,145),fill=t["warm"])
    d.point((161,145),fill=t["warm"])
    return im

def write_cinematics():
    """Build six hand-composed 320x180 shots in the 3x2 atlas expected by Godot."""
    atlas=Image.new("RGB",(960,360),(5,8,19))
    for ch in range(6):
        panel=cinematic_panel(ch)
        atlas.paste(panel,((ch%3)*320,(ch//3)*180))
    out=ROOT/"assets/cinematics"; out.mkdir(parents=True,exist_ok=True)
    # Lossless WebP preserves the intentional single-pixel clusters.
    atlas.save(out/"cutscene_atlas.webp",lossless=True,method=6)
def validate():
    from PIL import ImageStat
    bg_signatures=set()
    for ch in range(6):
        with Image.open(BG/f"act_{ch}.png") as im:
            assert im.size==(4200,360) and im.mode=="RGB", f"chapter {ch}: invalid panorama canvas"
            # Measure a broad, area-filtered sample: nearest-neighbour sampling at
            # 140x12 can alias thin pixel-art details and falsely reject rich scenes.
            reduced=im.resize((1400,120),Image.Resampling.BOX)
            colors=reduced.getcolors(1400*120) or []
            assert len(colors)>80, f"chapter {ch}: insufficient palette complexity ({len(colors)} sampled colors)"
            assert min(ImageStat.Stat(im).stddev)>7, f"chapter {ch}: flat color distribution"
            signature=im.resize((140,12),Image.Resampling.BOX)
            bg_signatures.add(signature.tobytes())
        with Image.open(BG/f"foreground_{ch}.png") as im:
            assert im.size==(4200,360) and im.mode=="RGBA" and im.getchannel("A").getbbox(), f"chapter {ch}: invalid parallax plane"
    assert len(bg_signatures)==6, "Chapter backgrounds must be genuinely distinct"
    for kind in ACTORS:
        paths=[CH/f"{kind}_{i}.png" for i in range(6)]
        assert all(p.is_file() for p in paths), f"{kind}: missing animation frame"
        assert len({p.read_bytes() for p in paths})==6, f"{kind}: duplicate animation frames"
        for path in paths:
            with Image.open(path) as im:
                assert im.size==(60,64) and im.mode=="RGBA", f"{path}: wrong enemy frame format"
                assert im.getchannel("A").getbbox() is not None, f"{path}: empty sprite"
    for kind in BOSSES:
        paths=[CH/f"boss_{kind}_{i}.png" for i in range(6)]
        assert all(p.is_file() for p in paths), f"boss {kind}: missing frame"
        assert len({p.read_bytes() for p in paths})==6, f"boss {kind}: duplicate animation frames"
        for path in paths:
            with Image.open(path) as im:
                assert im.size==(96,112) and im.mode=="RGBA", f"{path}: wrong boss frame format"
                assert im.getchannel("A").getbbox() is not None, f"{path}: empty sprite"
    for name in ("pixel_rain","pixel_steam","pixel_window","pixel_reflection"):
        with Image.open(FX/f"{name}.png") as im:
            assert im.mode=="RGBA" and im.getchannel("A").getbbox(), f"missing/empty FX sprite {name}"
    for i in range(6):
        with Image.open(FX/f"pixel_petal_{i}.png") as im:
            assert im.mode=="RGBA" and im.getchannel("A").getbbox(), f"empty petal frame {i}"
    with Image.open(ROOT/"assets/cinematics/cutscene_atlas.webp") as atlas:
        assert atlas.size==(960,360), "Cinematic atlas has the wrong 3x2 panel dimensions"
        signatures=set()
        for ch in range(6):
            box=((ch%3)*320,(ch//3)*180,(ch%3+1)*320,(ch//3+1)*180)
            signatures.add(atlas.crop(box).resize((80,45)).tobytes())
        assert len(signatures)==6, "Cinematic panels must be visually distinct"
def main():
    write_backgrounds(); save_animation(); save_weather(); write_cinematics(); validate()
    print("v2.2 QA: 6 chapter scenes, 6 parallax layers, 24 enemy frames, 36 boss frames, 30 weather sprites, cinematic atlas.")
if __name__=="__main__": main()
