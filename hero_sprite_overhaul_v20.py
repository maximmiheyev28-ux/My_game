#!/usr/bin/env python3
"""v2.0: replace the hero's procedural placeholder poses with a coherent pixel-art animation set."""
from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
CHAR = ROOT / "assets" / "characters"
UI = ROOT / "assets" / "ui"
SIZE = (96, 112)

# A restrained, reusable palette keeps the sprite readable against neon scenes.
C = {
    "clear": (0, 0, 0, 0), "outline": (6, 9, 19, 255), "ink": (10, 15, 29, 255),
    "deep": (15, 24, 42, 255), "navy": (24, 36, 58, 255), "blue": (35, 53, 78, 255),
    "mid": (51, 73, 99, 255), "steel": (88, 116, 143, 255), "light": (139, 165, 183, 255),
    "pale": (195, 216, 224, 255), "skin": (151, 127, 139, 255), "skin_hi": (205, 164, 163, 255),
    "magenta": (174, 41, 105, 255),
    "pink": (222, 54, 125, 255), "pink_hi": (255, 111, 169, 255), "pink_dark": (99, 28, 70, 255),
    "cyan": (49, 201, 225, 255), "cyan_hi": (141, 244, 255, 255), "cyan_dark": (25, 104, 137, 255),
    "gold": (226, 178, 112, 255), "white": (240, 249, 250, 255), "shadow": (4, 7, 16, 150),
    "violet": (91, 72, 132, 255), "violet_hi": (133, 112, 180, 255),
}


def col(name: str):
    return C[name]


def poly(d: ImageDraw.ImageDraw, pts, fill, outline="outline", width=1):
    points = [(int(round(x)), int(round(y))) for x, y in pts]
    d.polygon(points, fill=col(fill))
    if outline:
        d.line(points + [points[0]], fill=col(outline), width=width, joint="curve")


def ln(d, pts, fill, width=1):
    points = [(int(round(x)), int(round(y))) for x, y in pts]
    d.line(points, fill=col(fill), width=width, joint="curve")


def rect(d, xy, fill, outline=None):
    box = tuple(int(round(v)) for v in xy)
    d.rectangle(box, fill=col(fill), outline=col(outline) if outline else None)


def px(d, x, y, fill):
    d.point((int(round(x)), int(round(y))), fill=col(fill))


def draw_leg(d, hip, knee, ankle, boot_dir=1, armor_side="cyan"):
    hx, hy = hip
    kx, ky = knee
    ax, ay = ankle
    poly(d, [(hx-5, hy-2), (hx+5, hy-2), (kx+5, ky+2), (ax+4, ay+2),
             (ax-4, ay+3), (kx-6, ky+3), (hx-8, hy+4)], "outline")
    poly(d, [(hx-3, hy), (hx+3, hy), (kx+3, ky), (ax+2, ay), (ax-3, ay+1),
             (kx-4, ky+1), (hx-5, hy+3)], "navy", "blue")
    poly(d, [(kx-4, ky-4), (kx+2, ky-5), (kx+5, ky), (kx+2, ky+5),
             (kx-4, ky+4), (kx-6, ky)], "blue", "steel")
    ln(d, [(kx-3, ky-2), (kx+1, ky-3), (kx+3, ky)], "light")
    poly(d, [(kx-3, ky+5), (kx+3, ky+3), (ax+3, ay-2), (ax+1, ay+3),
             (ax-3, ay+4), (kx-5, ky+8)], "deep", "outline")
    ln(d, [(kx+1, ky+7), (ax, ay+1), (ax-2, ay+3)], "cyan" if armor_side == "cyan" else "pink", 1)
    rect(d, (ax-3, ay-1, ax+3, ay+3), "steel")
    ln(d, [(ax-3, ay), (ax+2, ay+1)], "pale")
    bx = ax + (5 if boot_dir >= 0 else -5)
    poly(d, [(ax-4, ay+2), (ax+3, ay+2), (bx+6, ay+7), (bx+5, ay+11),
             (bx-6, ay+11), (ax-5, ay+7)], "outline")
    poly(d, [(ax-3, ay+3), (ax+2, ay+3), (bx+4, ay+7), (bx+3, ay+9),
             (bx-4, ay+9), (ax-4, ay+6)], "mid", "steel")
    ln(d, [(bx-4, ay+8), (bx+3, ay+8)], "cyan" if armor_side == "cyan" else "pink")
    px(d, bx+1, ay+5, "white")


def draw_scarf(d, frame, state, bob):
    phase = frame * math.tau / max(1, 10 if state == "run" else 8)
    flutter = math.sin(phase * (1.0 if state != "run" else 1.8))
    lift = math.cos(phase) * (4 if state in ("run", "jump", "fall") else 2)
    reach = 0
    if state == "run":
        reach = 7 + int((1 + flutter) * 2)
    elif state == "attack":
        reach = 2 + int((frame % 3) * 2)
    elif state in ("jump", "fall"):
        reach = 5
    elif state == "hurt":
        reach = -2
    poly(d, [(42, 36+bob), (34, 32+bob), (25-reach, 25+bob-lift),
             (12-reach, 27+bob-lift), (20-reach, 35+bob), (31, 41+bob)], "pink_dark", "outline")
    poly(d, [(40, 40+bob), (32, 39+bob), (23-reach, 43+bob+lift),
             (10-reach, 51+bob+lift), (18-reach, 55+bob+lift), (34, 47+bob)], "pink", "outline")
    ln(d, [(39, 38+bob), (28-reach//2, 31+bob-lift), (17-reach, 29+bob-lift)], "pink_hi", 2)
    ln(d, [(37, 44+bob), (27-reach//2, 47+bob+lift), (17-reach, 51+bob+lift)], "pink_hi")
    px(d, 22-reach, 33+bob-lift, "white")
    poly(d, [(39, 34+bob), (53, 34+bob), (58, 42+bob), (50, 48+bob),
             (39, 43+bob), (35, 38+bob)], "pink", "outline")
    ln(d, [(39, 38+bob), (50, 42+bob), (56, 40+bob)], "pink_hi", 2)


def draw_head(d, hx, hy, blink=False):
    poly(d, [(hx-6, hy+13), (hx+7, hy+12), (hx+8, hy+23), (hx-6, hy+23)], "skin", "outline")
    poly(d, [(hx-11, hy-7), (hx-7, hy-15), (hx+5, hy-17), (hx+13, hy-8),
             (hx+12, hy+7), (hx+7, hy+17), (hx-5, hy+16), (hx-12, hy+7)], "outline")
    poly(d, [(hx-9, hy-6), (hx-5, hy-13), (hx+5, hy-14), (hx+10, hy-7),
             (hx+9, hy+5), (hx+5, hy+12), (hx-5, hy+11), (hx-10, hy+4)], "skin", "steel")
    poly(d, [(hx+1, hy-10), (hx+9, hy-6), (hx+8, hy+5), (hx+4, hy+11), (hx-1, hy+6)], "skin", None)
    ln(d, [(hx-8, hy+1), (hx-5, hy+4), (hx-3, hy+4)], "skin_hi")
    poly(d, [(hx-10, hy+3), (hx+9, hy+2), (hx+8, hy+10), (hx+3, hy+14),
             (hx-6, hy+12), (hx-10, hy+8)], "deep", "outline")
    ln(d, [(hx-7, hy+7), (hx-2, hy+8), (hx+4, hy+7)], "steel")
    px(d, hx+5, hy+10, "pink")
    if blink:
        ln(d, [(hx-7, hy-1), (hx-1, hy-2), (hx+6, hy-1)], "pink_hi", 2)
    else:
        poly(d, [(hx-8, hy-3), (hx-1, hy-5), (hx+6, hy-3), (hx+7, hy),
                 (hx+1, hy-1), (hx-6, hy)], "outline", None)
        ln(d, [(hx-6, hy-2), (hx-1, hy-3), (hx+5, hy-2)], "pink_hi", 2)
        px(d, hx+2, hy-2, "cyan_hi")
    poly(d, [(hx-13, hy-4), (hx-15, hy-14), (hx-8, hy-22), (hx+1, hy-23),
             (hx+10, hy-18), (hx+16, hy-9), (hx+12, hy-2), (hx+7, hy-9),
             (hx+1, hy-12), (hx-4, hy-7), (hx-7, hy-1), (hx-10, hy+5)], "outline")
    poly(d, [(hx-11, hy-13), (hx-7, hy-20), (hx+1, hy-21), (hx+8, hy-17),
             (hx+12, hy-10), (hx+6, hy-13), (hx+1, hy-15), (hx-4, hy-11)], "navy", None)
    poly(d, [(hx-14, hy-13), (hx-20, hy-17), (hx-15, hy-8), (hx-12, hy-2)], "deep", "outline")
    ln(d, [(hx-10, hy-15), (hx-5, hy-20), (hx+2, hy-20)], "violet_hi")
    ln(d, [(hx+3, hy-18), (hx+10, hy-14), (hx+13, hy-9)], "pink")
    ln(d, [(hx-12, hy-9), (hx-9, hy-14), (hx-4, hy-16)], "cyan")
    px(d, hx+9, hy-12, "white")


def draw_torso(d, cx, cy):
    poly(d, [(cx-12, cy-14), (cx+5, cy-17), (cx+15, cy-8), (cx+13, cy+12),
             (cx+8, cy+24), (cx-9, cy+22), (cx-16, cy+10), (cx-17, cy-2)], "outline")
    poly(d, [(cx-11, cy-12), (cx+4, cy-14), (cx+12, cy-7), (cx+10, cy+10),
             (cx+6, cy+20), (cx-8, cy+18), (cx-13, cy+8), (cx-14, cy-2)], "navy", "blue")
    poly(d, [(cx-8, cy-10), (cx+1, cy-13), (cx+5, cy-5), (cx+2, cy+5),
             (cx-6, cy+3), (cx-11, cy-3)], "mid", "steel")
    poly(d, [(cx+2, cy-12), (cx+10, cy-7), (cx+8, cy+4), (cx+3, cy+9), (cx-1, cy+1)], "deep", "steel")
    ln(d, [(cx-7, cy-7), (cx-2, cy-10), (cx+1, cy-5)], "pale")
    ln(d, [(cx+4, cy-8), (cx+8, cy-5), (cx+6, cy+1)], "cyan")
    ln(d, [(cx-11, cy-4), (cx-2, cy+1), (cx+7, cy+7)], "pink", 3)
    ln(d, [(cx-10, cy-4), (cx-1, cy+1), (cx+6, cy+6)], "pink_hi")
    rect(d, (cx-1, cy+1, cx+4, cy+6), "outline")
    rect(d, (cx, cy+2, cx+2, cy+4), "cyan_hi")
    poly(d, [(cx-10, cy+16), (cx+8, cy+15), (cx+12, cy+22), (cx+5, cy+27),
             (cx-9, cy+25), (cx-14, cy+21)], "deep", "outline")
    rect(d, (cx-8, cy+18, cx+8, cy+21), "pink_dark", "pink")
    rect(d, (cx-1, cy+17, cx+4, cy+22), "steel", "pale")
    px(d, cx+1, cy+19, "cyan_hi")
    poly(d, [(cx-13, cy+8), (cx-18, cy+16), (cx-14, cy+27), (cx-9, cy+23)], "outline")
    ln(d, [(cx-14, cy+15), (cx-12, cy+22)], "pink")


def draw_arm(d, shoulder, elbow, wrist, side="front"):
    sx, sy = shoulder
    ex, ey = elbow
    wx, wy = wrist
    ln(d, [(sx, sy), (ex, ey), (wx, wy)], "outline", 9)
    ln(d, [(sx, sy), (ex, ey), (wx, wy)], "navy", 6)
    ln(d, [(sx-1, sy-1), (ex-1, ey-1), (wx-1, wy-1)], "steel", 2)
    rect(d, (ex-3, ey-3, ex+2, ey+2), "blue", "steel")
    px(d, ex, ey-2, "cyan" if side == "front" else "pink")
    rect(d, (wx-3, wy-3, wx+3, wy+3), "deep", "light")
    poly(d, [(wx-3, wy-2), (wx+2, wy-3), (wx+5, wy), (wx+3, wy+4),
             (wx-2, wy+4), (wx-5, wy+1)], "mid", "pale")
    px(d, wx+2, wy, "white")


def draw_katana(d, hand, angle_deg=-24, length=32, swing=False):
    hx, hy = hand
    angle = math.radians(angle_deg)
    tip = (hx + math.cos(angle) * length, hy + math.sin(angle) * length)
    vx = math.cos(angle)
    vy = math.sin(angle)
    nx = -vy
    ny = vx
    base = (hx+4, hy-3)
    tip_outline = (tip[0]+nx*1.6, tip[1]+ny*1.6)
    poly(d, [base, (base[0]+nx*3, base[1]+ny*3), tip_outline,
             (tip[0]-nx*1.0, tip[1]-ny*1.0)], "outline", None)
    ln(d, [(hx-4, hy+4), (hx+4, hy-4)], "outline", 5)
    ln(d, [(hx-3, hy+3), (hx+3, hy-3)], "pink", 2)
    ln(d, [(hx-4, hy-2), (hx+5, hy+3)], "pale", 2)
    px(d, hx-1, hy, "cyan_hi")
    ln(d, [(base[0]+nx, base[1]+ny), (tip[0]+nx*0.5, tip[1]+ny*0.5)], "white", 2)
    ln(d, [(base[0]-nx, base[1]-ny), (tip[0]-nx*0.8, tip[1]-ny*0.8)], "cyan_hi")
    if swing:
        px(d, int((hx+tip[0])/2), int((hy+tip[1])/2)-3, "pink_hi")


def draw_hero(state: str, frame: int, count: int) -> Image.Image:
    im = Image.new("RGBA", SIZE, C["clear"])
    d = ImageDraw.Draw(im)
    p = frame * math.tau / max(1, count)
    bob = 0.0
    lean = 0.0
    crouch = 0.0
    blink = False
    if state == "idle":
        bob = -1.0 + math.sin(p) * 1.1
        blink = frame in (3,)
    elif state == "run":
        bob = -2.0 + abs(math.sin(p)) * 2.3
        lean = 2.0
    elif state == "attack":
        lean = [0, 1, 4, 7, 5, 1, -1, 0][frame]
        crouch = [0, 0, 1, 2, 2, 1, 0, 0][frame]
        bob = [0, -1, -2, -3, -2, -1, 0, 0][frame]
    elif state == "jump":
        bob = -5.0 - math.sin(p) * 2.0
        crouch = 1.0
    elif state == "fall":
        bob = -2.0 + math.sin(p) * 1.5
        lean = -2.0
    elif state == "hurt":
        lean = -5.0 + frame * 0.5
        bob = -1.0 + frame * 0.3
    elif state == "parry":
        lean = 1.0
        crouch = 1.0
    elif state == "stasis":
        bob = -2.0 + math.sin(p * 2.0) * 1.2
    elif state == "death":
        lean = -3.0 - frame * 0.7
        bob = frame * 1.25
        crouch = frame * 1.5

    hip_y = 70 + crouch + bob
    if state == "run":
        s = math.sin(p)
        c = math.cos(p)
        left_knee = (42 + s*7, 84 - max(0, c)*3 + crouch + bob)
        left_ankle = (38 + s*15, 99 - max(0, c)*7 + crouch + bob)
        right_knee = (53 - s*7, 83 - max(0, -c)*3 + crouch + bob)
        right_ankle = (56 - s*15, 99 - max(0, -c)*7 + crouch + bob)
    elif state == "jump":
        left_knee, left_ankle = (37, 82+bob), (31, 92+bob)
        right_knee, right_ankle = (56, 80+bob), (64, 91+bob)
    elif state == "fall":
        left_knee, left_ankle = (39, 82+bob), (34, 96+bob)
        right_knee, right_ankle = (55, 80+bob), (61, 95+bob)
    elif state == "hurt":
        left_knee, left_ankle = (37, 84+bob), (31, 100+bob)
        right_knee, right_ankle = (54, 83+bob), (59, 101+bob)
    elif state == "death":
        left_knee, left_ankle = (38-frame, 84+crouch+bob), (31-frame*2, 99+crouch+bob)
        right_knee, right_ankle = (54, 84+crouch+bob), (61, 100+crouch+bob)
    elif state == "attack":
        left_knee, left_ankle = (37, 83+crouch+bob), (30, 101+crouch+bob)
        right_knee, right_ankle = (56, 83+crouch+bob), (63, 101+crouch+bob)
    else:
        left_knee, left_ankle = (39, 84+crouch+bob), (36, 100+crouch+bob)
        right_knee, right_ankle = (54, 84+crouch+bob), (57, 101+crouch+bob)

    if state in ("idle", "run", "attack", "hurt", "parry", "stasis"):
        d.ellipse((24, 104, 72, 109), fill=C["shadow"])

    draw_scarf(d, frame, state, bob)
    draw_leg(d, (43+lean, hip_y), left_knee, left_ankle, boot_dir=1, armor_side="pink")
    draw_leg(d, (52+lean, hip_y), right_knee, right_ankle, boot_dir=1, armor_side="cyan")

    cx = 47 + lean
    cy = 53 + bob
    draw_torso(d, cx, cy)

    if state == "run":
        swing = math.sin(p)
        back_elbow = (28 + swing*5, 49 - swing*5 + bob)
        back_wrist = (25 + swing*10, 59 - swing*8 + bob)
    elif state == "hurt":
        back_elbow, back_wrist = (26, 45+bob), (19, 37+bob)
    elif state == "attack":
        back_elbow, back_wrist = (28, 51+bob), (34, 61+bob)
    else:
        back_elbow, back_wrist = (29, 51+bob), (25, 59+bob)
    draw_arm(d, (35+lean, 43+bob), back_elbow, back_wrist, side="back")

    head_drop = 1 if state in ("attack", "hurt", "death") else 0
    hx = 48 + lean
    hy = 20 + bob + head_drop
    draw_head(d, hx, hy, blink=blink)

    if state == "attack":
        front_wrist = [(60,47),(64,39),(69,32),(73,41),(70,50),(63,57),(58,54),(57,49)][frame]
        front_elbow = [(56,48),(58,42),(60,39),(64,42),(64,48),(61,51),(58,52),(56,50)][frame]
        blade_angles = [-70,-91,-50,-12,18,38,-16,-48]
        blade_lengths = [32,35,38,42,40,38,35,31]
    elif state == "parry":
        front_wrist = [(63,37),(65,33),(68,29),(68,30),(65,33),(62,37)][frame]
        front_elbow = [(57,43),(59,40),(62,38),(62,39),(59,42),(57,45)][frame]
        blade_angles, blade_lengths = [-58,-67,-78,-72,-55,-43], [33,34,36,36,34,33]
    elif state == "run":
        swing = math.sin(p)
        front_elbow = (57 - swing*5, 49 + swing*4 + bob)
        front_wrist = (60 - swing*9, 59 - swing*7 + bob)
        blade_angles, blade_lengths = [-28 + math.sin(p)*9]*count, [38]*count
    elif state == "hurt":
        front_elbow, front_wrist = (58, 50+bob), (65, 58+bob)
        blade_angles, blade_lengths = [18]*count, [30]*count
    else:
        front_elbow, front_wrist = (58, 48+bob), (62, 53+bob)
        blade_angles, blade_lengths = [-25 + math.sin(p)*4]*count, [32]*count
    draw_arm(d, (58+lean, 43+bob), front_elbow, front_wrist, side="front")
    draw_katana(d, front_wrist, blade_angles[frame], blade_lengths[frame], state == "attack")

    rect(d, (cx-13, cy+5, cx-10, cy+10), "pink")
    rect(d, (cx+8, cy+10, cx+10, cy+14), "cyan")
    ln(d, [(cx-7, cy+11), (cx-4, cy+15), (cx+3, cy+15)], "steel")
    rect(d, (cx-13, cy+24, cx-8, cy+28), "pink_dark", "pink")
    rect(d, (cx+7, cy+23, cx+11, cy+27), "deep", "steel")
    px(d, cx+9, cy+24, "cyan_hi")
    if state == "stasis":
        for j in range(5):
            a = p + j*math.tau/5
            ex = 48 + math.cos(a)*27
            ey = 56 + math.sin(a)*23
            rect(d, (ex, ey, ex+1, ey+2), "cyan_hi" if j % 2 == 0 else "pink_hi")
    if state == "hurt":
        px(d, 18, 22+bob, "pink_hi")
        px(d, 13, 18+bob, "cyan_hi")
    if state == "death":
        for j in range(1, min(6, frame+2)):
            px(d, 70 + (j%2)*3, 55 + j*5, "cyan" if j%2 else "pink")

    if state == "death":
        im = im.rotate(-frame * 3.0, resample=Image.Resampling.NEAREST, center=(47, 103), fillcolor=C["clear"])
    return im


def write_frames():
    CHAR.mkdir(parents=True, exist_ok=True)
    UI.mkdir(parents=True, exist_ok=True)
    cycles = {
        "idle": 8, "run": 10, "attack": 8, "jump": 6, "fall": 6,
        "hurt": 6, "parry": 6, "stasis": 8, "death": 8,
    }
    for state, count in cycles.items():
        for frame in range(count):
            draw_hero(state, frame, count).save(CHAR / f"player_{state}_{frame}.png", optimize=True)
        draw_hero(state, 0, count).save(CHAR / f"player_{state}.png", optimize=True)
    draw_hero("idle", 0, 8).save(CHAR / "player_idle.png", optimize=True)
    draw_hero("attack", 3, 8).save(CHAR / "player_attack.png", optimize=True)
    draw_hero("stasis", 0, 8).save(CHAR / "player_phase.png", optimize=True)

    source = draw_hero("idle", 0, 8)
    crop = source.crop((15, 0, 88, 76)).resize((88, 88), Image.Resampling.NEAREST)
    portrait = Image.new("RGBA", (96, 96), (7, 11, 24, 255))
    pd = ImageDraw.Draw(portrait)
    pd.rectangle((1, 1, 94, 94), outline=col("pink"), width=2)
    pd.line((4, 6, 4, 89), fill=col("cyan"), width=1)
    portrait.alpha_composite(crop, (4, 4))
    pd.line((8, 90, 88, 90), fill=col("pink_hi"), width=1)
    portrait.save(UI / "hero_portrait.png", optimize=True)


def patch_player_script():
    path = ROOT / "scripts" / "player" / "player.gd"
    source = path.read_text(encoding="utf-8")
    source = source.replace("visual.scale = Vector2(0.72, 0.72)", "visual.scale = Vector2(0.64, 0.64)")
    old_attack = """const TEX_ATTACK := [
    preload("res://assets/characters/player_attack_0.png"),
    preload("res://assets/characters/player_attack_1.png"),
    preload("res://assets/characters/player_attack_2.png"),
    preload("res://assets/characters/player_attack_3.png"),
    preload("res://assets/characters/player_attack_4.png"),
    preload("res://assets/characters/player_attack_5.png")
]"""
    new_attack = "const TEX_ATTACK := [\n" + ",\n".join(
        f'    preload("res://assets/characters/player_attack_{i}.png")' for i in range(8)
    ) + "\n]"
    if "player_attack_7.png" not in source:
        if old_attack not in source:
            raise SystemExit("v2.0: could not find the existing TEX_ATTACK declaration")
        source = source.replace(old_attack, new_attack, 1)
    old_stasis = """const TEX_STASIS := [
    preload("res://assets/characters/player_stasis_0.png"),
    preload("res://assets/characters/player_stasis_1.png"),
    preload("res://assets/characters/player_stasis_2.png"),
    preload("res://assets/characters/player_stasis_3.png"),
    preload("res://assets/characters/player_stasis_4.png"),
    preload("res://assets/characters/player_stasis_5.png")
]"""
    new_stasis = "const TEX_STASIS := [\n" + ",\n".join(
        f'    preload("res://assets/characters/player_stasis_{i}.png")' for i in range(8)
    ) + "\n]"
    if "player_stasis_7.png" not in source:
        if old_stasis not in source:
            raise SystemExit("v2.0: could not find the existing TEX_STASIS declaration")
        source = source.replace(old_stasis, new_stasis, 1)
    insert_after = "const TEX_STASIS := [\n" + ",\n".join(
        f'    preload("res://assets/characters/player_stasis_{i}.png")' for i in range(8)
    ) + "\n]"
    death_decl = "\nconst TEX_DEATH := [\n" + ",\n".join(
        f'    preload("res://assets/characters/player_death_{i}.png")' for i in range(8)
    ) + "\n]"
    if "const TEX_DEATH" not in source:
        source = source.replace(insert_after, insert_after + death_decl, 1)
    if "var death_timer := 0.0" not in source:
        source = source.replace("var input_locked := false", "var input_locked := false\nvar death_timer := 0.0", 1)
    source = source.replace(
        """    if input_locked:
        return""",
        """    if input_locked:
        if death_timer > 0.0:
            death_timer = maxf(0.0, death_timer - delta)
            var death_progress := 1.0 - death_timer / 0.64
            var death_frame := mini(TEX_DEATH.size() - 1, int(death_progress * TEX_DEATH.size()))
            visual.texture = TEX_DEATH[death_frame]
            visual.flip_h = facing < 0
            visual.position.y = -36.0 + death_progress * 3.0
            visual.modulate = Color(0.88, 0.96, 1.0, 1.0)
            visual.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
            if death_timer <= 0.0:
                get_tree().reload_current_scene()
        return""",
        1,
    )
    source = source.replace(
        """        died.emit()
        Game.record_death()
        get_tree().reload_current_scene()""",
        """        died.emit()
        Game.record_death()
        death_timer = 0.64""",
        1,
    )
    source = source.replace("int(animation_clock * 18.0) % TEX_HURT.size()", "int(animation_clock * 28.0) % TEX_HURT.size()")
    if "player_death_7.png" not in source:
        raise SystemExit("v2.0: death frame preload declaration was not installed")
    path.write_text(source, encoding="utf-8")


def strengthen_validator():
    path = ROOT / "tools" / "validate_project.py"
    source = path.read_text(encoding="utf-8")
    if '"assets/characters/player_death_7.png"' not in source:
        source = source.replace(
            '    *[f"assets/characters/player_attack_{i}.png" for i in range(6)],',
            '    *[f"assets/characters/player_attack_{i}.png" for i in range(8)],\n'
            '    *[f"assets/characters/player_death_{i}.png" for i in range(8)],',
        )
        source = source.replace(
            '    *[f"assets/characters/player_stasis_{i}.png" for i in range(6)],',
            '    *[f"assets/characters/player_stasis_{i}.png" for i in range(8)],',
        )
    marker = "image_count = 0\n"
    quality = '''# Hero-frame integrity: each authored pose must be unique and retain its pixel canvas.\n'''
    quality += '''hero_cycles = {"idle": 8, "run": 10, "attack": 8, "jump": 6, "fall": 6, "hurt": 6, "parry": 6, "stasis": 8, "death": 8}\n'''
    quality += '''for mode, count in hero_cycles.items():\n'''
    quality += '''    frames = [ROOT / "assets" / "characters" / f"player_{mode}_{i}.png" for i in range(count)]\n'''
    quality += '''    digests = set()\n'''
    quality += '''    for frame_path in frames:\n'''
    quality += '''        try:\n'''
    quality += '''            with Image.open(frame_path) as frame_image:\n'''
    quality += '''                if frame_image.size != (96, 112) or frame_image.mode != "RGBA":\n'''
    quality += '''                    errors.append(f"Hero sprite dimensions/mode regression: {frame_path.relative_to(ROOT)}")\n'''
    quality += '''                digests.add(frame_image.convert("RGBA").tobytes())\n'''
    quality += '''        except Exception:\n'''
    quality += '''            pass\n'''
    quality += '''    if len(digests) != count:\n'''
    quality += '''        errors.append(f"Hero {mode} cycle has repeated frames: {len(digests)}/{count} unique")\n\n'''
    if "hero-frame integrity" not in source:
        if marker not in source:
            raise SystemExit("v2.0: could not find validator insertion point")
        source = source.replace(marker, quality + marker, 1)
    path.write_text(source, encoding="utf-8")


def main():
    write_frames()
    patch_player_script()
    strengthen_validator()
    for state, count in {"idle":8,"run":10,"attack":8,"jump":6,"fall":6,"hurt":6,"parry":6,"stasis":8,"death":8}.items():
        frames = [Image.open(CHAR / f"player_{state}_{i}.png").convert("RGBA") for i in range(count)]
        hashes = {frame.tobytes() for frame in frames}
        assert len(hashes) == count, f"{state}: repeated sprite frames"
        assert all(frame.size == SIZE for frame in frames)
    print("v2.0: generated 66 unique 96x112 RGBA hero frames across nine animation cycles; updated death playback and project validation.")


if __name__ == "__main__":
    main()
