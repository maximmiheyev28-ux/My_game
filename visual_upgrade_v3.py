#!/usr/bin/env python3
"""v1.3 art pass: hand-posed character animation and richly textured parallax art."""
from pathlib import Path
import math, random
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
ROOT=Path.cwd(); BG=ROOT/'assets/backgrounds'; CH=ROOT/'assets/characters'; UI=ROOT/'assets/ui'
S=3
def sc(v): return int(round(v*S))
def poly(d,pts,fill,outline=None,width=1):
 p=[(sc(x),sc(y)) for x,y in pts]; d.polygon(p,fill=fill)
 if outline:d.line(p+[p[0]],fill=outline,width=max(1,sc(width)),joint='curve')
def line(d,pts,fill,width=1):d.line([(sc(x),sc(y)) for x,y in pts],fill=fill,width=max(1,sc(width)),joint='curve')
def rect(d,b,fill,outline=None,width=1):d.rectangle(tuple(sc(v) for v in b),fill=fill,outline=outline,width=max(1,sc(width)) if outline else 1)
def ell(d,b,fill,outline=None,width=1):d.ellipse(tuple(sc(v) for v in b),fill=fill,outline=outline,width=max(1,sc(width)) if outline else 1)
def save_pixel(im,path,size): im.resize(size,Image.Resampling.LANCZOS).resize(size,Image.Resampling.NEAREST).save(path,optimize=True)

def hero_frame(state,i,n):
 W,H=80,96; im=Image.new('RGBA',(W*S,H*S),(0,0,0,0)); d=ImageDraw.Draw(im); p=2*math.pi*i/n
 poses={
 'run':[(-15,10,-3,-34),(-10,5,-1,-20),(-4,-2,2,-8),(4,-10,3,8),(12,-15,1,22),(15,-9,-2,35),(9,2,-3,23),(1,10,-1,7),(-9,14,2,-12),(-15,8,1,-28)],
 'attack':[(-8,8,-7,-65),(-5,5,-12,-35),(0,0,-18,0),(8,-5,-20,48),(12,-8,-10,78),(5,-3,4,110)],
 'jump':[(-9,8,-4,-30),(-5,12,-8,-15),(1,10,-10,8),(8,4,-8,28),(11,-1,-4,10),(4,-8,0,-20)],
 'fall':[(-5,8,8,22),(-2,5,12,38),(5,0,15,50),(10,-4,10,24),(6,-8,2,-8),(-2,-2,-4,-25)],
 'hurt':[(-7,5,18,35),(-10,3,22,55),(-6,-2,17,80),(2,-7,8,65),(8,-4,0,25),(0,3,-5,-5)],
 'parry':[(-5,3,-2,-90),(-3,1,-4,-75),(0,0,-5,-55),(3,-2,-2,-40),(1,1,1,-65),(-3,3,0,-85)],
 'stasis':[(-2,3,-2,-25),(0,1,-3,-10),(2,-1,-2,5),(0,-2,0,20),(-2,0,2,5),(0,2,0,-12)],
 'idle':[(0,0,0,-10)]*8}
 rear,front,tilt,blade=poses[state][i%len(poses[state])]
 lift=max(0,math.sin(p))*4 if state=='run' else (8+math.sin(p)*4 if state=='jump' else 0)
 bob=math.sin(p*2)*1.1 if state in ('idle','run') else 0; cx=38+tilt*.12
 ell(d,(16,88,62,93),(3,4,16,160))
 wind=math.sin(p*1.4)*5 if state in ('run','idle','stasis') else (i-2.5)*1.8
 poly(d,[(30,20+bob),(19,14+bob),(7,11+wind),(17,23+wind),(5,31+wind),(24,29+bob),(33,26+bob)],'#7f123e','#210d26')
 poly(d,[(29,21+bob),(20,20+bob),(12,31+wind),(23,29+wind),(31,26+bob)],'#e43c70','#7c164a')
 line(d,[(27,23+bob),(17,28+wind),(10,32+wind)],'#ff9bb8')
 hip=(31,59+bob-lift*.35); knee=(29+rear*.56,72+bob-lift*.6); ankle=(25+rear,84+bob-lift)
 poly(d,[hip,(39,61+bob),(knee[0]+5,knee[1]),(ankle[0]+5,ankle[1]-1),(ankle[0]-3,ankle[1]+1),(knee[0]-5,knee[1]-2),(25,67+bob)],'#161a31','#070b19')
 line(d,[(30,64+bob),(knee[0]+2,knee[1]-3),(ankle[0]+1,ankle[1]-4)],'#48516d')
 poly(d,[(ankle[0]-5,ankle[1]-2),(ankle[0]+6,ankle[1]-3),(ankle[0]+11,ankle[1]+2),(ankle[0]+8,ankle[1]+5),(ankle[0]-8,ankle[1]+5)],'#080e20','#77819b')
 line(d,[(ankle[0]-4,ankle[1]+1),(ankle[0]+7,ankle[1]+1)],'#e04480')
 knee2=(43+front*.55,72+bob-lift*.55); ankle2=(48+front,85+bob-lift)
 poly(d,[(37,58+bob),(47,58+bob),(knee2[0]+4,knee2[1]),(ankle2[0]+3,ankle2[1]-1),(ankle2[0]-4,ankle2[1]+2),(knee2[0]-5,knee2[1]-2),(33,68+bob)],'#252c47','#080d1d')
 poly(d,[(ankle2[0]-5,ankle2[1]-3),(ankle2[0]+6,ankle2[1]-3),(ankle2[0]+11,ankle2[1]+2),(ankle2[0]+8,ankle2[1]+5),(ankle2[0]-8,ankle2[1]+5)],'#0a1021','#8b94aa')
 line(d,[(ankle2[0]-4,ankle2[1]),(ankle2[0]+7,ankle2[1])],'#e34c89')
 coat=math.sin(p*1.6)*4 if state in ('run','idle') else i-3
 poly(d,[(25,36+bob),(45,34+bob),(53,58+bob),(48,81+bob+coat),(38,73+bob),(31,88+bob-coat),(18,77+bob),(24,56+bob)],'#0b1127','#485271')
 poly(d,[(25,44+bob),(33,48+bob),(27,75+bob),(20,80+bob),(22,62+bob)],'#7e174b','#d43b78')
 poly(d,[(42,43+bob),(50,54+bob),(48,75+bob),(41,83+bob),(44,61+bob)],'#a31e58','#5a1649')
 line(d,[(25,48+bob),(22,67+bob),(19,77+bob)],'#e85a91'); line(d,[(44,48+bob),(48,62+bob),(46,75+bob)],'#e85a91')
 poly(d,[(26,25+bob),(43,23+bob),(51,42+bob),(46,61+bob),(28,61+bob),(21,43+bob)],'#11172e','#697593')
 poly(d,[(28,29+bob),(42,28+bob),(46,43+bob),(38,54+bob),(26,47+bob)],'#29324f','#10172c')
 poly(d,[(26,31+bob),(32,29+bob),(35,40+bob),(28,44+bob),(22,39+bob)],'#5b6682','#aab2c7')
 poly(d,[(39,29+bob),(46,33+bob),(49,43+bob),(42,45+bob),(36,38+bob)],'#1b2540','#7785a4')
 line(d,[(25,43+bob),(35,47+bob),(47,41+bob)],'#e94a8b',2); line(d,[(28,33+bob),(39,43+bob),(43,53+bob)],'#60eaff')
 ell(d,(35,40+bob,40,45+bob),'#6ef3ff','#f3ffff'); ell(d,(36,41+bob,38,43+bob),'#ffffff')
 rect(d,(23,57+bob,49,61+bob),'#080e20','#6c7894'); rect(d,(34,56+bob,40,63+bob),'#d43b78','#ff9fc7')
 rect(d,(23,61+bob,28,67+bob),'#1a2440','#71809a'); rect(d,(45,61+bob,50,66+bob),'#1a2440','#71809a')
 for x,y in ((26,38),(46,39),(29,53),(45,54)): ell(d,(x,y+bob,x+1.8,y+1.8),'#e4efff')
 rect(d,(33,19+bob,41,28+bob),'#bd8798'); ell(d,(27,5+bob,47,28+bob),'#c994a6','#090d1d')
 poly(d,[(26,15+bob),(25,8+bob),(31,2+bob),(42,1+bob),(50,7+bob),(49,15+bob),(44,11+bob),(39,8+bob),(33,11+bob)],'#080d20','#59627f')
 poly(d,[(28,8+bob),(20,16+bob),(22,29+bob),(29,24+bob),(31,14+bob)],'#11172e','#515d7a')
 poly(d,[(41,5+bob),(52,9+bob),(49,20+bob),(44,16+bob),(37,12+bob)],'#090f24','#515d7a')
 poly(d,[(27,8+bob),(37,5+bob),(45,10+bob),(37,14+bob),(32,22+bob),(28,16+bob)],'#131a32','#606988')
 poly(d,[(36,8+bob),(47,9+bob),(41,17+bob),(35,21+bob),(38,13+bob)],'#080e20')
 line(d,[(30,15+bob),(38,14+bob),(43,16+bob)],'#1b1022'); rect(d,(38,16+bob,42,17+bob),'#fff4e9'); rect(d,(39,16+bob,40,18+bob),'#52eaff')
 line(d,[(30,22+bob),(43,22+bob)],'#6f365d')
 poly(d,[(29,23+bob),(43,22+bob),(42,28+bob),(32,28+bob)],'#18213a','#b65d88'); line(d,[(32,25+bob),(41,25+bob)],'#ef5795')
 if state=='attack':
  hand=(55+math.cos(math.radians(blade))*7,39+math.sin(math.radians(blade))*7); arm=[(44,34+bob),(52,34+bob),(hand[0],hand[1]),(hand[0]-4,hand[1]+4),(42,45+bob)]
 elif state=='parry':
  hand=(54,22+i%2*2); arm=[(43,34+bob),(49,29+bob),(hand[0],hand[1]),(hand[0]-5,hand[1]+2),(42,43+bob)]
 elif state=='hurt':
  hand=(18,29+i%3*2); arm=[(27,34+bob),(22,31+bob),(hand[0],hand[1]),(hand[0]+3,hand[1]+5),(31,45+bob)]
 elif state=='run':
  hand=(48+front*.38,42-rear*.25); arm=[(43,34+bob),(50,36+bob),(hand[0],hand[1]),(hand[0]-4,hand[1]+5),(40,45+bob)]
 else:
  hand=(48,47+bob); arm=[(43,34+bob),(49,39+bob),(hand[0],hand[1]),(hand[0]-5,hand[1]+3),(40,45+bob)]
 poly(d,arm,'#1a2340','#8490ab'); ell(d,(hand[0]-2,hand[1]-2,hand[0]+3,hand[1]+3),'#c7a1aa','#fff0ef')
 poly(d,[(27,34+bob),(22,36+bob),(19,48+bob),(24,51+bob),(31,43+bob),(33,38+bob)],'#202943','#8490a9'); rect(d,(19,46+bob,25,51+bob),'#c4cddd')
 if state=='attack': angle=math.radians(blade); sx,sy=hand; ex=sx+31*math.cos(angle); ey=sy+31*math.sin(angle)
 elif state=='parry': sx,sy=hand; ex,ey=sx+20,sy-29
 elif state=='run': sx,sy=hand; ex,ey=sx+22,sy-15+math.sin(p)*5
 elif state=='stasis': sx,sy=hand; ex,ey=sx+19,sy-22
 else: sx,sy=hand; ex,ey=sx+23,sy-9
 line(d,[(sx-4,sy+3),(sx+4,sy-3)],'#d7a5b5',3); line(d,[(sx,sy),(ex,ey)],'#eff7ff',3)
 line(d,[(sx+1,sy-1),(ex-1,ey-1)],'#70eaff'); line(d,[(sx-1,sy+2),(ex-2,ey+2)],'#ef4e91')
 if state=='attack':
  a0=math.radians(blade-58); a1=math.radians(blade+28); pts=[]
  for j in range(18):
   a=a0+(a1-a0)*j/17; pts.append((sx+36*math.cos(a),sy+29*math.sin(a)))
  line(d,pts,(255,95,185,210),2); line(d,[(x,y-2) for x,y in pts],(180,240,255,190))
 if state=='stasis':
  for k in range(9):
   a=p*1.1+k*math.tau/9; x=40+math.cos(a)*27; y=49+math.sin(a)*27; rect(d,(x,y,x+2,y+2),'#7ceeff')
 if state=='hurt': line(d,[(17,16),(10,10),(7,4)],'#ff668e',2); ell(d,(11,31,14,34),'#ff567f')
 if state=='jump': line(d,[(17,55),(12,51),(9,46)],'#c8f5ff')
 return im

print('v1.3: replacing repeated/near-identical hero frames with hand-posed animation cycles')
cycles={'player_idle':('idle',8),'player_run':('run',10),'player_attack':('attack',6),'player_jump':('jump',6),'player_fall':('fall',6),'player_hurt':('hurt',6),'player_parry':('parry',6),'player_stasis':('stasis',6)}
for prefix,(state,count) in cycles.items():
 for i in range(count): save_pixel(hero_frame(state,i,count),CH/f'{prefix}_{i}.png',(80,96))
for prefix in ('player_idle','player_attack','player_jump','player_fall','player_hurt','player_parry'):
 (CH/f'{prefix}.png').write_bytes((CH/f'{prefix}_0.png').read_bytes())
(CH/'player_phase.png').write_bytes((CH/'player_stasis_0.png').read_bytes())

PALETTES=[('#ff63b8','#4fe4ff','#ffbf83'),('#ff625f','#72d6ec','#ffc17a'),('#45d7ee','#6ff5ff','#f4d69a'),('#f35fca','#8fa8ff','#ffd49b'),('#c86bff','#7af6d8','#ffad8c'),('#ff5c9e','#80eaff','#fff0b4')]
def enrich_background(chapter):
 path=BG/f'act_{chapter}.png'; im=Image.open(path).convert('RGB'); W,H=im.size; ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); rng=random.Random(90113+chapter*119); pink,cyan,gold=PALETTES[chapter]
 for seg in range(6):
  sx=seg*700
  for bx,base,scale in ((sx+95,267,.7),(sx+490,273,.85)):
   ww=170*scale
   for floor in range(3):
    y=base-floor*31; width=ww*(1-floor*.16)
    d.polygon([(bx-width*.6,y+25),(bx-width*.48,y-8),(bx-width*.25,y-25),(bx+width*.25,y-25),(bx+width*.48,y-8),(bx+width*.6,y+25),(bx+width*.42,y+19),(bx+width*.25,y+4),(bx-width*.25,y+4),(bx-width*.42,y+19)],fill=(9,12,31,245),outline=tuple(bytes.fromhex(pink[1:]))+(210,))
    for k in range(11):
     xx=bx-width/3+k*width/15; d.line((xx,y-15,xx+2,y+20),fill=(95,91,132,170),width=1)
    for k in range(5):
     xx=bx-width/4+k*width/8; d.rectangle((xx-3,y+1,xx+3,y+13),fill=tuple(bytes.fromhex(gold[1:]))+(190,))
  for bx in range(sx+8,sx+700,38):
   y=rng.randint(120,245); d.line((bx,y,bx,285),fill=(32,37,67,155),width=1)
   if rng.random()<.55:
    d.rectangle((bx+3,y+8,bx+9,y+19),fill=(8,12,29,235),outline=(90,93,132,170))
    d.rectangle((bx+5,y+10,bx+7,y+17),fill=tuple(bytes.fromhex(rng.choice([pink,cyan,gold])[1:]))+(200,))
   if rng.random()<.28:
    d.line((bx+13,y+18,bx+13,285),fill=(9,12,24,230),width=3)
    d.line((bx+14,y+18,bx+14,285),fill=(71,82,111,150),width=1)
  for k in range(8):
   x=sx+rng.randrange(20,680); y=rng.randrange(75,230)
   if k%3==0:
    d.rectangle((x,y,x+18,y+12),fill=(9,13,30,235),outline=tuple(bytes.fromhex(cyan[1:]))+(200,))
    d.rectangle((x+3,y+3,x+15,y+8),fill=tuple(bytes.fromhex(pink[1:]))+(180,))
   elif k%3==1:
    d.line((x,y+20,x,y-20),fill=(10,15,33,240),width=2); d.line((x-8,y-13,x+8,y-13),fill=tuple(bytes.fromhex(gold[1:]))+(220,))
   else:
    d.rectangle((x,y,x+25,y+14),fill=(9,14,31,225),outline=(78,92,129,180)); d.rectangle((x+4,y+3,x+21,y+10),fill=(26,37,64,235))
  for yy in (36,57,84):
   pts=[(sx+k*25,yy+int(math.sin(k/28*math.pi)*9)) for k in range(29)]
   d.line(pts,fill=(8,13,31,230),width=2)
   for x,y in pts[::7]: d.rectangle((x-2,y-2,x+2,y+2),fill=tuple(bytes.fromhex(cyan[1:]))+(160,))
  if chapter in (0,3,5):
   for tx in (sx+35,sx+665):
    d.line((tx,310,tx+8,248,tx-7,205,tx+5,167),fill=(25,16,35,250),width=7)
    for b in [[(tx+3,257),(tx-30,225),(tx-67,211)],[(tx-3,229),(tx+37,194),(tx+79,183)],[(tx+1,204),(tx-15,173),(tx-10,145)],[(tx+4,270),(tx+51,244),(tx+85,226)]]: d.line(b,fill=(25,16,39,255),width=3)
    for cx,cy,rx,ry in ((tx-56,208,34,19),(tx-18,177,36,22),(tx+26,192,35,21),(tx+67,182,30,17),(tx+66,227,25,16)):
     d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(100,30,93,220))
     for _ in range(130):
      x=cx+rng.randint(-rx,rx); y=cy+rng.randint(-ry,ry)
      if ((x-cx)/rx)**2+((y-cy)/ry)**2<1: d.rectangle((x,y,x+2,y+2),fill=rng.choice([(226,64,164,245),(250,103,188,245),(255,159,214,240),(255,206,229,230)]))
  for lx in (sx+115,sx+585):
   ly=248; d.line((lx,ly-60,lx,ly-18),fill=(12,14,30,250),width=4)
   d.rectangle((lx-13,ly-20,lx+13,ly+20),fill=(8,10,25,250),outline=(99,74,123,240),width=2)
   d.rectangle((lx-8,ly-14,lx+8,ly+14),fill=tuple(bytes.fromhex(gold[1:]))+(235,))
   d.line((lx-5,ly-12,lx-5,ly+12),fill=(255,242,213,245),width=2)
 for _ in range(17000):
  x=rng.randrange(W); y=rng.randrange(H)
  if y<285:d.rectangle((x,y,x+rng.choice([1,1,2]),y+rng.choice([1,2])),fill=rng.choice([(160,174,218,35),(8,10,25,90),(255,126,194,38),(74,198,233,34)]))
 for _ in range(2100):
  x=rng.randrange(W); y=rng.randrange(290,H); d.line((x,y,min(W-1,x+rng.randrange(3,27)),y+rng.choice([-1,0,0,1])),fill=rng.choice([(255,91,177,105),(73,221,246,110),(255,194,125,95),(120,123,190,75)]),width=1)
 im=Image.alpha_composite(im.convert('RGBA'),ov); arr=np.asarray(im.convert('RGB')); bright=((arr[:,:,0]>145)&(arr[:,:,2]>130))|((arr[:,:,1]>165)&(arr[:,:,2]>175))
 glow=np.zeros((H,W,4),dtype=np.uint8); glow[:,:,:3]=arr; glow[:,:,3]=bright.astype(np.uint8)*55
 im=Image.alpha_composite(im,Image.fromarray(glow,'RGBA').filter(ImageFilter.GaussianBlur(3.5)))
 im.convert('RGB').save(path,optimize=True)
for i in range(6):enrich_background(i)

def make_foreground(chapter):
 W,H=4200,360; im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); rng=random.Random(301+chapter*17); pink,cyan,gold=PALETTES[chapter]; pc=tuple(bytes.fromhex(pink[1:])); cc=tuple(bytes.fromhex(cyan[1:])); gc=tuple(bytes.fromhex(gold[1:]))
 for seg in range(6):
  sx=seg*700
  for x,yy,scale in ((sx-12,180,.75),(sx+660,166,.88)):
   ww=190*scale
   d.polygon([(x-ww*.6,yy+25),(x-ww*.48,yy-8),(x-ww*.25,yy-25),(x+ww*.25,yy-25),(x+ww*.48,yy-8),(x+ww*.6,yy+25),(x+ww*.42,yy+19),(x+ww*.25,yy+4),(x-ww*.25,yy+4),(x-ww*.42,yy+19)],fill=(7,10,26,245),outline=(*pc,220))
   for k in range(13):
    xx=x-ww*.4+k*ww*.8/12; d.line((xx,yy-8,xx+3,yy+20),fill=(88,85,128,210),width=2)
   d.line((x-ww*.55,yy+23,x-ww*.45,yy-7,x-ww*.24,yy-22,x+ww*.24,yy-22,x+ww*.45,yy-7,x+ww*.55,yy+23),fill=(*cc,220),width=2)
  if chapter in (0,3,5):
   tx=sx+(30 if seg%2==0 else 665); d.line((tx-55,-10,tx-12,22,tx+24,48,tx+75,62),fill=(21,14,34,255),width=12)
   for b in [[(tx-15,20),(tx-42,0),(tx-68,-3)],[(tx+12,40),(tx+47,17),(tx+84,10)],[(tx+42,53),(tx+66,78),(tx+105,88)],[(tx-28,8),(tx-15,-12),(tx+2,-24)]]:d.line(b,fill=(25,16,39,255),width=5)
   for cx,cy,rx,ry in ((tx-51,2,36,18),(tx-15,24,39,22),(tx+29,40,38,21),(tx+75,59,35,20),(tx+3,-7,31,17)):
    d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(101,30,101,210))
    for _ in range(180):
     x=cx+rng.randint(-rx,rx); y=cy+rng.randint(-ry,ry)
     if ((x-cx)/rx)**2+((y-cy)/ry)**2<1:d.rectangle((x,y,x+2,y+2),fill=rng.choice([(255,105,187,250),(255,163,216,250),(255,210,232,240),(222,65,172,250)]))
  for lx in (sx+92,sx+608):
   d.line((lx,0,lx,55),fill=(10,13,28,250),width=4); d.rectangle((lx-15,52,lx+15,97),fill=(7,9,22,250),outline=(*pc,235),width=2)
   d.rectangle((lx-9,59,lx+9,90),fill=(*gc,235)); d.line((lx-7,61,lx-7,87),fill=(255,244,217,245),width=2)
   d.rectangle((lx-19,48,lx+19,55),fill=(14,12,30,250),outline=(*cc,235),width=1)
  for y in (17,39,65):
   pts=[(sx+k*35,y+int(math.sin(k/20*math.pi)*7)) for k in range(21)]; d.line(pts,fill=(8,11,25,245),width=2)
 im.save(BG/f'foreground_{chapter}.png',optimize=True)
for i in range(6):make_foreground(i)

player=ROOT/'scripts/player/player.gd'; s=player.read_text(encoding='utf-8')
s=s.replace('visual.scale = Vector2(0.8, 0.8)','visual.scale = Vector2(1.08, 1.08)')
s=s.replace('visual.position.y = -32.0','visual.position.y = -40.0')
s=s.replace('visual.position.y = -32.0 + sin(animation_clock * 7.0) * 1.2','visual.position.y = -40.0 + sin(animation_clock * 7.0) * 1.2')
s=s.replace('visual.position.y = -32.0 + absf(sin(animation_clock * 26.0)) * 2.0','visual.position.y = -40.0 + absf(sin(animation_clock * 26.0)) * 2.0')
s=s.replace('visual.position.y = -32.0 + bob','visual.position.y = -40.0 + bob')
s=s.replace('var cadence := 0.065 if dash_timer > 0.0 else 0.078','var cadence := 0.052 if dash_timer > 0.0 else 0.064')
s=s.replace('int(animation_clock * 14.0) % TEX_HURT.size()','int(animation_clock * 18.0) % TEX_HURT.size()')
s=s.replace('int(animation_clock * 11.0) % TEX_STASIS.size()','int(animation_clock * 13.0) % TEX_STASIS.size()')
player.write_text(s,encoding='utf-8')

portrait=Image.new('RGBA',(128,128),(6,8,22,255)); pd=ImageDraw.Draw(portrait)
pd.rectangle((3,3,124,124),fill=(13,13,36,255),outline=(222,48,157,255),width=3); pd.rectangle((8,8,120,120),outline=(73,220,255,220),width=1)
face=hero_frame('idle',2,8).crop((18*S,0,61*S,43*S)).resize((94,94),Image.Resampling.NEAREST); portrait.alpha_composite(face,(17,18))
pd.rectangle((12,109,116,115),fill=(5,8,21,255)); pd.rectangle((12,109,67,112),fill=(236,56,148,255)); pd.rectangle((67,109,116,112),fill=(67,224,255,255))
portrait.save(UI/'hero_portrait.png',optimize=True)
print('v1.3 art pass complete: 52 hand-posed hero frames, six textured panoramas and six detailed foreground layers.')
