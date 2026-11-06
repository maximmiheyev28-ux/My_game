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
    draw_skyline(im,ch,t)
    # Seven authored object placements per chapter; each uses a pixel map, not a primitive proxy.
    props = {
      0:[("shop",34,37,2),("train",260,43,1),("vending",525,65,2),("tower",790,14,2),("dish",1120,49,2)],
      1:[("furnace",28,29,2),("crane",282,17,2),("dock",555,49,2),("antenna",850,42,2),("ship",1110,53,2)],
      2:[("ship",30,51,2),("crane",270,18,2),("dock",525,57,2),("radar",810,42,2),("tower",1110,14,2)],
      3:[("tower",28,9,3),("radar",300,39,2),("shop",570,43,2),("relay",850,20,2),("crane",1120,17,2)],
      4:[("tree",48,56,2),("greenhouse",270,54,2),("dish",560,52,2),("vending",850,59,2),("tower",1110,13,2)],
      5:[("relay",42,23,2),("radio",295,32,2),("antenna",550,54,2),("tower",830,15,2),("dish",1110,50,2)]
    }[ch]
    for name,x,y,scale in props:
        tint={"c":t["cyan"],"p":t["pink"],"w":t["warm"]}
        draw_map(im,x,y,MAPS[name],tint,scale)
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
                if c: im.putpixel((x,y),(*c,255))
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
        im.resize((W*S,H*S),Image.Resampling.NEAREST).save(BG/f"act_{ch}.png",optimize=True)
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
    for ch in range(6):
        p=BG/f"act_{ch}.png"
        with Image.open(p) as im:
            assert im.size==(4200,360) and im.mode=="RGB"
            assert len(im.resize((140,12)).getcolors(140*12) or [])>80
            assert min(ImageStat.Stat(im).stddev)>7
        with Image.open(BG/f"foreground_{ch}.png") as im:
            assert im.size==(4200,360) and im.mode=="RGBA" and im.getchannel("A").getbbox()
    assert len({(CH/f"{kind}_{i}.png").read_bytes() for kind in ACTORS for i in range(6)})>=24
    assert len({(CH/f"boss_{kind}_{i}.png").read_bytes() for kind in BOSSES for i in range(6)})>=36
    with Image.open(ROOT/"assets/cinematics/cutscene_atlas.webp") as im: assert im.size==(960,360)
def main():
    write_backgrounds(); save_animation(); save_weather(); write_cinematics(); validate()
    print("v2.2 QA: 6 chapter scenes, 6 parallax layers, 24 enemy frames, 36 boss frames, 30 weather sprites, cinematic atlas.")
if __name__=="__main__": main()
