#!/usr/bin/env python3
"""Add a true slower-moving foreground art plane to each of the six levels."""
from pathlib import Path
import random
from PIL import Image, ImageDraw

ROOT = Path.cwd()
BG = ROOT / 'assets' / 'backgrounds'
BG.mkdir(parents=True, exist_ok=True)
PALETTES = [
    ('#ff4eae','#46dfff','#ffb86f'),('#ff5a63','#62c9e5','#ffb45e'),
    ('#45d4e8','#62f2ff','#e8c78b'),('#ff5bc9','#7b94ff','#ffd18c'),
    ('#c75dff','#73ffd4','#f9a77f'),('#ff55a6','#74eaff','#fff0ad')
]

for chapter,(pink,cyan,gold) in enumerate(PALETTES):
    rng=random.Random(7719+chapter*91)
    im=Image.new('RGBA',(4200,360),(0,0,0,0))
    d=ImageDraw.Draw(im,'RGBA')
    pc=tuple(int(pink[i:i+2],16) for i in (1,3,5))
    cc=tuple(int(cyan[i:i+2],16) for i in (1,3,5))
    gc=tuple(int(gold[i:i+2],16) for i in (1,3,5))
    for seg in range(6):
        sx=seg*700
        if chapter in (0,3):
            # Foreground branches arch into the frame from above and the side.
            bx=sx+rng.choice([35,655])
            branch=(21,16,43,245)
            d.line([(bx-70,-15),(bx-35,18),(bx+5,38),(bx+65,67),(bx+125,76)],fill=branch,width=10)
            d.line([(bx-35,18),(bx-13,-4),(bx+32,-18)],fill=branch,width=6)
            d.line([(bx+22,47),(bx+74,25),(bx+120,18)],fill=branch,width=5)
            d.line([(bx+54,64),(bx+86,94),(bx+133,112)],fill=branch,width=4)
            clusters=[(-45,5,40,22),(0,28,47,24),(49,54,44,21),(98,71,37,18),(26,-4,34,18)]
            for ox,oy,rx,ry in clusters:
                x=bx+ox; y=oy
                d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(116,35,113,205))
                d.ellipse((x-rx*.72,y-ry*.68,x+rx*.72,y+ry*.68),fill=(218,65,162,225))
                for _ in range(65):
                    px=x+rng.randint(-rx,rx); py=y+rng.randint(-ry,ry)
                    if ((px-x)/rx)**2+((py-y)/ry)**2 < 1:
                        c=rng.choice([(255,154,216,245),(255,206,234,250),(239,91,183,240)])
                        d.rectangle((px,py,px+2,py+2),fill=c)
        else:
            # Industrial conduits, hanging service cables and reactor braces.
            for k in range(4):
                y=8+k*22+rng.randint(-3,4)
                d.line((sx-25,y,sx+725,y+rng.randint(-14,14)),fill=(14,19,39,245),width=3 if k%2 else 2)
                if k%2==0:
                    for x in range(sx+70,sx+680,170):
                        d.rectangle((x-2,y-2,x+2,y+2),fill=(*pc,240))
            for x in (sx+95,sx+605):
                d.line((x,0,x,38),fill=(12,18,37,250),width=4)
                d.rounded_rectangle((x-8,35,x+8,62),radius=3,fill=(9,12,30,250),outline=(*cc,245),width=2)
                d.rectangle((x-3,42,x+3,55),fill=(*gc,235))
        # Vertical neon signboards and ornate lamps at the extreme viewport edges.
        sign_x=sx+(28 if seg%2==0 else 624)
        d.rectangle((sign_x,113,sign_x+28,213),fill=(7,9,25,246),outline=(*pc,245),width=2)
        d.rectangle((sign_x+4,117,sign_x+24,209),fill=(19,15,44,240),outline=(*cc,225),width=1)
        for j in range(7):
            yy=124+j*11
            d.rectangle((sign_x+10,yy,sign_x+18,yy+5),fill=(*gc,235) if j%3==0 else (*pc,235))
        lx=sx+(660 if seg%2==0 else 40); ly=237
        d.line((lx,ly-100,lx,ly-23),fill=(16,16,35,255),width=3)
        d.rectangle((lx-12,ly-23,lx+12,ly+18),fill=(11,11,29,250),outline=(*pc,250),width=2)
        d.rectangle((lx-7,ly-17,lx+7,ly+13),fill=(*gc,225))
        d.line((lx-7,ly-2,lx+7,ly-2),fill=(255,239,205,250),width=2)
        d.rectangle((lx-15,ly-28,lx+15,ly-23),fill=(22,19,43,255),outline=(*cc,245),width=1)
        d.rectangle((lx-15,ly+18,lx+15,ly+23),fill=(22,19,43,255),outline=(*pc,245),width=1)
    # A few near-camera drifting sparks and blossom fragments.
    for _ in range(320):
        x=rng.randrange(4200); y=rng.randrange(10,255); size=rng.choice([1,2,2,3])
        c=rng.choice([(255,119,190,170),(255,196,225,190),(109,230,249,145),(255,212,151,135)])
        d.polygon([(x,y),(x+size*2,y+1),(x+size,y+size*2),(x-1,y+size)],fill=c)
    im.save(BG/f'foreground_{chapter}.png',optimize=True)

fx=ROOT/'scripts'/'fx'/'parallax_layer.gd'
fx.parent.mkdir(parents=True,exist_ok=True)
fx.write_text('''extends Node2D

var camera: Camera2D
var factor := 0.58

func setup(camera_ref: Camera2D, parallax_factor: float = 0.58) -> void:
    camera = camera_ref
    factor = clampf(parallax_factor, 0.0, 0.95)

func _process(_delta: float) -> void:
    if is_instance_valid(camera):
        global_position.x = camera.global_position.x * factor
''',encoding='utf-8')

level=ROOT/'scripts'/'levels'/'level.gd'
s=level.read_text(encoding='utf-8')
if 'const PARALLAX_SCRIPT' not in s:
    s=s.replace('extends Node2D\n','extends Node2D\n\nconst PARALLAX_SCRIPT := preload("res://scripts/fx/parallax_layer.gd")\n',1)
if 'background.z_index = -10' not in s:
    s=s.replace('    background.centered = false\n','    background.centered = false\n    background.z_index = -10\n',1)
if 'foreground_%d.png' not in s:
    anchor='    camera.limit_bottom = 360\n'
    addition='''    camera.limit_bottom = 360
    # Independent near-camera art plane moves slower than the world camera.
    var foreground_layer := Node2D.new()
    foreground_layer.set_script(PARALLAX_SCRIPT)
    foreground_layer.call("setup", camera, 0.58)
    var foreground_sprite := Sprite2D.new()
    foreground_sprite.texture = load("res://assets/backgrounds/foreground_%d.png" % chapter)
    foreground_sprite.centered = false
    foreground_sprite.position = Vector2.ZERO
    foreground_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    foreground_sprite.z_index = -5
    foreground_layer.add_child(foreground_sprite)
    add_child(foreground_layer)
'''
    if anchor not in s:
        raise SystemExit('Camera setup insertion point not found.')
    s=s.replace(anchor,addition,1)
level.write_text(s,encoding='utf-8')
print('Parallax foreground: six transparent layers + camera-follow script + Level integration.')
