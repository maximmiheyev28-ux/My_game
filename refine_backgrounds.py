#!/usr/bin/env python3
"""Create original, restrained pixel-art panoramas and parallax foregrounds."""
from pathlib import Path
import math, random
from PIL import Image, ImageDraw

ROOT = Path.cwd()
OUT = ROOT / "assets" / "backgrounds"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 4200, 360
# sky, horizon, distant city, middle city, foreground, pink, cyan
P = [
    ("#080b20","#1b1832","#151c32","#10172b","#080d1b","#d65b9a","#55c9df"),
    ("#100d1c","#2a1d2b","#201d30","#151b2b","#0a101d","#d16b58","#69c6d2"),
    ("#071525","#153044","#142a40","#102238","#071421","#4cbbd1","#b2c6d6"),
    ("#0c0b21","#261a35","#1d1b38","#15172e","#090d1f","#c45ba9","#7b9de0"),
    ("#090d20","#1d2039","#1a2038","#141a31","#080c1c","#9a78d0","#62c7c2"),
    ("#100a20","#27182f","#1e1a36","#15162d","#090d1d","#d45a91","#5bc9dc"),
]
def col(h):
    h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def mix(a,b,t):
    return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))

def panorama(ch):
    sky,horizon,far,mid,near,pink,cyan=P[ch]
    rng=random.Random(7100+ch*131)
    im=Image.new("RGB",(W,H)); px=im.load()
    c0,c1,c2=col(sky),col(horizon),col(near)
    for y in range(H):
        c=mix(c0,c1,y/210) if y<210 else mix(c1,c2,(y-210)/150)
        for x in range(W):
            v=int(1.2*math.sin(x*.002+ch)*math.sin(y*.02))
            px[x,y]=tuple(max(0,min(255,q+v)) for q in c)
    d=ImageDraw.Draw(im,"RGBA"); a,b=col(pink),col(cyan)

    # Distant light and sparse stars.
    for _ in range(260):
        x,y=rng.randrange(W),rng.randrange(12,178)
        d.rectangle((x,y,x+rng.choice((1,1,2)),y+1),fill=(*rng.choice((a,b,(155,170,200))),rng.randrange(35,105)))
    if ch in (0,3,5):
        x=430+ch*113; y=82; r=42 if ch!=5 else 34
        d.ellipse((x-r-12,y-r-12,x+r+12,y+r+12),fill=(*a,16))
        d.ellipse((x-r,y-r,x+r,y+r),fill=(222,188,204,220))
        d.rectangle((x-2,y-r-3,x+r,y-r+2),fill=(*col(sky),255))
    else:
        x=(560+ch*590)%W; y=112
        d.ellipse((x-34,y-34,x+34,y+34),fill=(*b,20),outline=(*b,120),width=2)

    # Far skyline: varied heights and a few lit windows, leaving negative space above.
    x=-12
    while x<W:
        w=rng.randint(52,118); h=rng.randint(72,145); base=253+rng.randint(-7,7)
        shade=mix(col(far),col(horizon),rng.uniform(.05,.26))
        d.rectangle((x,base-h,x+w,base),fill=(*shade,245))
        roof=rng.randrange(4)
        if roof==0: d.rectangle((x+w//3,base-h-9,x+2*w//3,base-h+2),fill=(*shade,245))
        elif roof==1: d.line((x+w//2,base-h,x+w//2,base-h-18),fill=(*b,130),width=1)
        for _ in range(rng.randint(2,6)):
            wx=x+rng.randint(7,max(8,w-8)); wy=base-rng.randint(13,max(14,h-6))
            wc=a if rng.random()<.24 else b
            d.rectangle((wx,wy,wx+2,wy+5),fill=(*wc,rng.randint(95,175)))
        x+=w+rng.randint(12,25)

    # Middle skyline: darker blocks create clear depth behind the combat plane.
    x=-25
    while x<W:
        w=rng.randint(48,104); h=rng.randint(32,82); base=278+rng.randint(-3,3)
        shade=mix(col(near),col(mid),.48)
        d.rectangle((x,base-h,x+w,base),fill=(*shade,255))
        for _ in range(rng.randint(1,4)):
            wx=x+rng.randint(6,max(7,w-8)); wy=base-rng.randint(10,max(11,h-5))
            d.rectangle((wx,wy,wx+2,wy+4),fill=(*rng.choice((a,b)),rng.randint(80,140)))
        x+=w+rng.randint(25,48)

    # Chapter landmarks vary by section instead of repeating a single prop six times.
    for seg in range(6):
        sx=seg*700; cx=sx+rng.randint(250,460)
        if ch in (0,3) and seg in (0,3):
            d.rectangle((cx-42,220,cx+42,268),fill=(8,11,25,255))
            d.polygon([(cx-72,224),(cx-53,207),(cx-25,199),(cx+25,199),(cx+53,207),(cx+72,224),
                       (cx+49,220),(cx+24,214),(cx-24,214),(cx-49,220)],fill=(19,19,41,255),outline=(*a,205))
            d.line((cx-36,230,cx+36,230),fill=(*b,130),width=1)
        elif ch in (0,3) and seg in (2,5):
            tx=cx+rng.choice((-90,90))
            d.line((tx,276,tx+4,220,tx-7,182),fill=(17,13,31,255),width=6)
            d.line((tx,228,tx-36,196),fill=(17,13,31,255),width=4)
            d.line((tx+1,214,tx+40,181),fill=(17,13,31,255),width=4)
            for ox,oy,rx,ry in ((-40,194,24,13),(0,176,29,16),(42,184,24,13)):
                d.ellipse((tx+ox-rx,oy-ry,tx+ox+rx,oy+ry),fill=(94,39,90,215))
                for _ in range(22):
                    xx=tx+ox+rng.randint(-rx,rx); yy=oy+rng.randint(-ry,ry)
                    d.rectangle((xx,yy,xx+2,yy+2),fill=(*a,170))
        elif ch==1 and seg%2==0:
            for ox,top in ((-32,145),(30,165)):
                d.rectangle((cx+ox-7,top,cx+ox+7,270),fill=(9,13,25,255))
                d.rectangle((cx+ox-10,top-5,cx+ox+10,top+3),fill=(29,23,37,255),outline=(*a,140))
            d.rectangle((cx-76,226,cx+76,240),fill=(10,14,27,255),outline=(*a,120))
        elif ch==1:
            d.line((cx-92,265,cx+82,160),fill=(12,17,31,255),width=4)
            d.line((cx-58,265,cx-58,192),fill=(12,17,31,255),width=4)
            d.line((cx+52,178,cx+52,265),fill=(12,17,31,255),width=4)
            d.line((cx-58,192,cx+52,178),fill=(*b,110),width=1)
        elif ch==2 and seg in (1,4):
            d.ellipse((cx-58,190,cx+58,290),fill=(9,24,39,245),outline=(*b,180),width=2)
            d.arc((cx-43,201,cx+43,276),180,360,fill=(*b,130),width=2)
            d.line((cx,180,cx,268),fill=(*a,120),width=1)
        elif ch==2:
            for ox in (-46,0,46):
                tip=176-rng.randint(0,28)
                d.line((cx+ox,268,cx+ox,tip),fill=(9,17,31,255),width=3)
                d.ellipse((cx+ox-4,tip-7,cx+ox+4,tip+1),fill=(*b,155))
        elif ch==4 and seg%2==0:
            d.polygon([(cx-43,263),(cx-20,159),(cx+4,137),(cx+28,164),(cx+48,263)],
                      fill=(12,14,35,255),outline=(*a,185))
            d.polygon([(cx-88,247),(cx-60,212),(cx-36,245)],fill=(16,17,42,230))
            d.polygon([(cx+58,247),(cx+87,205),(cx+112,247)],fill=(16,17,42,230))
        elif ch==4:
            d.polygon([(cx-68,258),(cx-26,182),(cx+2,194),(cx+42,250)],fill=(12,14,35,245),outline=(*b,150))
        elif ch==5 and seg in (2,5):
            d.ellipse((cx-66,150,cx+66,282),outline=(*b,160),width=2)
            d.ellipse((cx-49,167,cx+49,265),outline=(*a,115),width=1)
            d.rectangle((cx-10,205,cx+10,268),fill=(10,13,29,255))
            d.line((cx,144,cx,268),fill=(*a,140),width=2)
        elif ch==5:
            for ox in (-38,0,38):
                tip=184-rng.randint(0,26)
                d.line((cx+ox,270,cx+ox,tip),fill=(9,13,29,255),width=5)
                d.rectangle((cx+ox-5,tip+2,cx+ox+5,tip+10),fill=(*b,100))

    # Thin horizon rails and a wet, dark play surface.
    d.rectangle((0,278,W,H),fill=(5,8,18,255))
    d.line((0,278,W,278),fill=(*b,145),width=2)
    d.line((0,283,W,283),fill=(*a,42),width=1)
    for _ in range(430):
        x,y=rng.randrange(W),rng.randrange(286,H); length=rng.randint(4,34)
        cc=a if rng.random()<.43 else b
        d.line((x,y,min(W-1,x+length),y),fill=(*cc,rng.randint(35,95)),width=1)
    for seg in range(6):
        sx=seg*700
        for _ in range(8):
            x=sx+rng.randint(60,640); y=rng.randint(286,330)
            d.line((x,y,x+rng.randint(1,3),y+24),fill=(*b,35),width=1)
    for _ in range(100):
        x,y=rng.randrange(W),rng.randrange(30,278)
        d.line((x,y,x-1,y+rng.randint(4,9)),fill=(*b,rng.randint(18,44)),width=1)
    im.save(OUT/f"act_{ch}.png",optimize=True)

def foreground(ch):
    _,_,_,_,_,pink,cyan=P[ch]; a,b=col(pink),col(cyan)
    rng=random.Random(9200+ch*83)
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im,"RGBA")
    for seg in range(6):
        sx=seg*700
        if seg%2==ch%2:
            y=rng.randint(24,58)
            d.line((sx+18,y,sx+350,y+8,sx+682,y-4),fill=(8,11,24,190),width=3)
            d.line((sx+18,y-1,sx+350,y+7,sx+682,y-5),fill=(*b,75),width=1)
        lx=sx+rng.choice((38,655))
        d.line((lx,185,lx,278),fill=(7,9,20,235),width=4)
        d.rectangle((lx-10,204,lx+10,240),fill=(7,10,22,250),outline=(*a,155),width=1)
        d.rectangle((lx-4,210,lx+4,234),fill=(*b,105))
        for _ in range(8):
            x=sx+rng.randint(20,680); y=rng.randint(120,260)
            d.rectangle((x,y,x+1,y+2),fill=(*a,70))
    im.save(OUT/f"foreground_{ch}.png",optimize=True)

for chapter in range(6):
    panorama(chapter)
    foreground(chapter)
print("Generated six chapter panoramas and six restrained parallax foreground layers.")
