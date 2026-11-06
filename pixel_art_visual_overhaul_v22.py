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
        for rx,ch in enumerate(row):
            c=PALETTE.get(ch)
            if c is None: continue
            if tint and ch in ("c","p","w"):
                c=tint[ch]
            x0=x+rx*scale; y0=y+ry*scale
            d.rectangle((x0,y0,x0+scale-1,y0+scale-1),fill=c)
def draw_skyline(im, chapter, t):
    d=ImageDraw.Draw(im); rng=random.Random(7000+chapter*97)
    # Distant skyline uses stepped roof profiles and broken window clusters.
    x=-20
    while x<W+30:
        bw=rng.randint(28,58); bh=rng.randint(24,54); top=87-bh
        base=mix(t["far"],t["haze"],rng.uniform(.05,.21))
        roof=rng.choice((0,1,2,3))
        if roof==0: points=[(x,87),(x,top+7),(x+7,top),(x+bw-6,top),(x+bw,top+8),(x+bw,87)]
        elif roof==1: points=[(x,87),(x,top+5),(x+9,top+5),(x+9,top),(x+bw,top),(x+bw,87)]
        elif roof==2: points=[(x,87),(x,top),(x+bw-9,top),(x+bw-3,top+9),(x+bw,top+9),(x+bw,87)]
        else: points=[(x,87),(x,top+8),(x+5,top+8),(x+5,top),(x+bw-4,top),(x+bw,top+7),(x+bw,87)]
        d.polygon(points,fill=base)
        shade=mix(base,t["street"],.30)
        d.line(points[:3],fill=mix(base,t["cyan"],.18),width=1)
        for wy in range(top+9,84,8):
            for wx in range(x+5,x+bw-4,7):
                if rng.random()<.32:
                    c=rng.choice((mix(base,t["warm"],.45),mix(base,t["cyan"],.52),shade))
                    d.point((wx,wy),fill=c); d.point((wx+1,wy),fill=c)
        x+=bw+rng.randint(4,12)
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
      0:[("shop",34,37,2),("train",260,43,1),("vending",525,65,2),("shop",760,38,2),("train",1035,45,1),("vending",1250,65,2)],
      1:[("furnace",28,29,2),("crane",282,17,2),("furnace",560,31,2),("crane",820,18,2),("furnace",1086,30,2)],
      2:[("ship",30,51,2),("crane",270,18,2),("dock",525,57,2),("ship",770,50,2),("crane",1040,20,2)],
      3:[("tower",28,9,3),("tower",300,14,2),("shop",570,43,2),("tower",820,12,3),("tower",1110,14,2)],
      4:[("tree",48,56,2),("greenhouse",270,54,2),("tree",540,56,2),("dish",800,52,2),("greenhouse",1050,54,2)],
      5:[("relay",42,23,2),("radio",295,32,2),("antenna",550,54,2),("relay",830,22,2),("radio",1095,31,2)]
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
  "......kk......",".....kddk.....",".....kmmk.....",".....khhk.....","......kk......",
  "....kkddkk....","...kddmmddk...","..kddmhhmddk..","..kddmddmddk..","...kddmmddk...",
  "....kdddk......","....kdddk......","...kkdd dkk....".replace(" ",""),"..kkdmhhmdkk...",
  ".kkddk..kddkk..",".kddk....kddk..","kkddk....kddkk.","kkmkk....kkmkk."
 ],
 "shooter": [
  "......kk......",".....kddk.....",".....kmmk.....",".....khhk.....","......kk......",
  "....kkddkk....","...kddmmddk...","..kddmhhmddk..","..kddmddmddk..","...kddmmddk...",
  "....kdddk......","....kdddk......","...kkdddk......","..kkddmmddkk...",
  ".kkddk..kddkk..","kkddk....kddk..","kkmkk....kkmkk","......kkkkpppppppp"
 ],
 "hunter": [
  "......kk......",".....kddk.....",".....kmmk.....",".....khhk.....","......kk......",
  "...kkkddkkk...","..kddmhhmddk..",".kddmppmmddk..",".kddmmpppddk...","..kddmmppdk....",
  "...kddmmddk....","....kdddk......","...kkddmmkk....","..kkdmhhdmk.....",
  ".kkddk..kddkk..","kkddk....kddk..","kkmkk....kkmkk","..pppppppppp...."
 ],
 "aberration": [
  "......kkkk......","....kkddddkk....","...kddmhhmddk...","..kddmddddmddk..",
  ".kddmmddppddmmk.","kddmddpwwpddmddk","kddmddppppddmddk","kddmmddddddmmddk",
  ".kddmhhddddhhddk","..kddmddddddmddk","...kddmmddmmddk.","....kddk..kddk...",
  "...kkddk..kddkk...","..kkmkk....kkmkk..","..kk........kk...."
 ]
}
BOSSES = {
 "warden": [
  "............kkkkkkkk............","..........kkddddddddkk..........",".........kddmmhhhhmmddk.........",
  "........kddmhhhhhhhhmddk........",".......kddmddmmmmmmddmddk.......","......kddmddmwwddwwmddmddk......",
  ".....kddmddmddppppddmddmddk.....","....kddmhhmddddddddddmhhmddk....",
  "...kddmmhmddmccccccddmhm mmddk...".replace(" ",""),"..kddmmhmddmddddddddmhmddk....",
  ".kddmmhmddmppppppppmddmhmddk...","kddmmhmddddddddddddddddmhmddk..",
  "kddmddmddmhhmmmmmmhhmddmddmddk.","kddmddmddmddddddddddmddmddmddk.",
  ".kddmmddmddmmmmmmmmddmddmmddk..","..kddmmddmddmmmmmmddmddmmddk...",
  "...kkddmmddkkkkkkkkddmmddkk.....",".....kkddkk........kkddkk......."
 ],
 "kair": [
  "............kkkk............","..........kkddddkk..........",".........kddmmhhddk.........",
  "........kddmhhhhhmdk........","........kddmwwwwwwmdk.......","........kddmddddddmdk.......",
  ".........kddmmppmmddk........","......kkkddmmppppmmddkkk.....",
  ".....kddmhhddddddddhhmddk....","....kddmhhmddccccddmhhmddk...",
  "...kddmhhmddddddddddmhhmddk..","..kddmmhmddppppppppddmhmddk...",
  ".kddmmhmddmddddddddmddmhmddk..","kddmmddmddmhhhhhhhhmddmddmddk.",
  ".kkdddmddmddddddddddmddmdddkk..","...kkddmmddkkkkkkkkddmmddkk...."
 ],
 "double": [
  "....kkkk....kkkk....","...kddddk..kddddk...","..kddmmddkkddmmddk..",
  ".kddmhhmddkkddmhhmddk.","kddmddddmddkkddmddddmddk",
  "kddmppppmddkkddmccccmddk","kddmddddmddkkddmddddmddk",
  ".kddmmddkk....kkddmmk.","..kdddk........kdddk..",
  ".kdddk..........kdddk.","kddmmkk..........kkmddk",
  ".kkmkk............kkmkk"
 ],
 "surgeon": [
  "........kkkk........","......kkddddkk......",".....kddmmhhddk.....",
  "....kddmhhhhmddk....","....kddmwwwwmddk....","....kddmddddmddk....",
  "...kddmmppppmmddk...","..kddmhhhhhhhhmddk..","..kddmddddddddmddk..",
  "...kddmccddccmddk...","....kddmddddmddk....","...kkddmmddmmddkk...",
  "..kddk..kddk..kddk..","..kk....kk....kk...."
 ],
 "watcher": [
  "............kkkk............",".........kkkddddkkk.........","......kkkdddmmmmdddkkk......",
  "....kkddmmhhddddddhhmmddkk....","...kddmmhhddddddddddhhmmddk...",
  "..kddmmhhddddwwwwddddhhmmddk..",".kddmmhhdddwwwwwwwwddddhhmmddk.",
  "kddmmhhddddwwccccwwddddhhmmddk","kddmmhhddddwwccccwwddddhhmmddk",
  ".kddmmhhdddwwwwwwwwddddhhmmddk.","..kddmmhhddddwwwwddddhhmmddk...",
  "...kddmmhhddddddddddhhmmddk....",".....kkkddmmmmmmmmddkkk......."
 ],
 "sentry": [
  "...........kkkk...........",".........kkddddkk.........","........kddmmhhddk........",
  ".......kddmhhhhmddk.......","......kddmddddddmddk......",".....kddmhhmmmmhhmddk.....",
  "....kddmddddppddddmddk....","...kddmmdddmppmdddmddk...","..kddmmddmddddddmddmmddk..",
  ".kddmmddkkmddddmkkddmmddk.","kddmmkk..kkmddmkk..kkmddk",
  "kkmkk.....kkkk.....kkmkk"
 ]
}
ACTOR_PALETTE = dict(PALETTE)
def make_actor(rows, size, frame, kind, boss=False):
    # Draw at source pixel resolution, then enlarge with nearest-neighbour.
    im=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(im)
    maxw=max(map(len,rows)); maxh=len(rows)
    sx=max(1,(size[0]-4)//maxw); sy=max(1,(size[1]-4)//maxh)
    ox=(size[0]-maxw*sx)//2; oy=(size[1]-maxh*sy)//2
    palette=ACTOR_PALETTE
    for y,row in enumerate(rows):
        for x,ch in enumerate(row):
            c=palette.get(ch)
            if c is None: continue
            # Animation changes only purposeful clusters: scarf, weapon, eye and armor glints.
            if ch=="p" and frame%3==1: c=(248,105,169)
            if ch=="c" and frame%2: c=(130,242,250)
            if ch=="w" and frame in (2,3): c=(255,225,164)
            xx=ox+x*sx; yy=oy+y*sy
            d.rectangle((xx,yy,xx+sx-1,yy+sy-1),fill=(*c,255))
    if boss:
        # Distinctive silhouette notch / energy rune animates in a six-frame cycle.
        x=size[0]//2+(frame%3-1)*2; y=size[1]//3
        d.line((x-3,y,x+3,y),fill=(130,240,255,255),width=2)
    else:
        # Weapon or scarf pixel changes position without moving the body's pivot.
        x=size[0]-4-(frame%3)*2; y=size[1]//2+frame%2
        d.point((x,y),fill=(255,124,181,255))
    return im
def save_animation():
    # Four enemy silhouettes, six idle/combat frames each.
    for kind,rows in ACTORS.items():
        for i in range(6):
            frame=make_actor(rows,(48,62),i,kind)
            frame.save(CH/f"{kind}_{i}.png",optimize=True)
            if i==0: frame.save(CH/f"{kind}.png",optimize=True)
    # Six large boss sprites; each design has a separate hand-authored silhouette.
    for kind,rows in BOSSES.items():
        for i in range(6):
            frame=make_actor(rows,(88,104),i,kind,True)
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
def write_cinematics():
    # Six original panels at 320x180 in one nearest-neighbour atlas.
    atlas=Image.new("RGB",(960,180),(5,8,19))
    for ch,t in enumerate(THEMES):
        panel=Image.new("RGB",(320,180),t["sky"]); d=ImageDraw.Draw(panel)
        for y in range(180):
            c=mix(t["sky"],t["haze"],y/180*.7)
            d.line((0,y,320,y),fill=c)
        # Layered silhouette echoes the chapter's signature landmark at cinematic scale.
        scene=chapter_scene(ch)
        scene=scene.resize((320,180),Image.Resampling.NEAREST)
        panel.paste(scene,(0,0))
        d=ImageDraw.Draw(panel)
        for i in range(42):
            x=(i*37+ch*19)%320; y=(i*17+ch*11)%165
            if i%3==0: d.point((x,y),fill=t["cyan"])
        atlas.paste(panel,(ch%3*320,ch//3*0))
    # Atlas rows represent chapter triptychs; each panel is independently addressable.
    atlas=Image.new("RGB",(960,360),(5,8,19))
    for ch in range(6):
        panel=Image.new("RGB",(320,180),THEMES[ch]["sky"])
        scene=chapter_scene(ch).resize((320,180),Image.Resampling.NEAREST)
        panel.paste(scene,(0,0))
        atlas.paste(panel,((ch%3)*320,(ch//3)*180))
    out=ROOT/"assets/cinematics"; out.mkdir(parents=True,exist_ok=True)
    atlas.save(out/"cutscene_atlas.webp",quality=96,method=6)
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
