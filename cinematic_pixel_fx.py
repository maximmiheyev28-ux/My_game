#!/usr/bin/env python3
"""v1.8: generate a native-resolution pixel slash and add cutscene foreground parallax."""
from pathlib import Path
import math
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
FX = ROOT / "assets" / "fx"
FX.mkdir(parents=True, exist_ok=True)

# Eight hand-authored raster frames: a stepped cyan/magenta katana arc with
# a white-hot core and discrete pixel sparks. No vector assets at runtime.
W, H = 128, 80
for frame_index in range(8):
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    progress = (frame_index + 1) / 8.0
    cx, cy = 64, 42
    start_angle = 205
    end_angle = 205 + 125 * progress
    box_outer = (cx - 43, cy - 34, cx + 43, cy + 34)
    box_inner = (cx - 39, cy - 30, cx + 39, cy + 30)
    draw.arc(box_outer, start=start_angle, end=end_angle, fill=(255, 56, 164, 220), width=5)
    draw.arc(box_inner, start=start_angle + 2, end=end_angle - 2, fill=(66, 215, 255, 245), width=3)
    draw.arc((cx - 35, cy - 26, cx + 35, cy + 26), start=start_angle + 5,
             end=end_angle - 5, fill=(238, 250, 255, 255), width=1)

    # A stepped diagonal blade trail gives the impact a strong readable silhouette.
    slash_end_x = 18 + round(progress * 88)
    slash_end_y = 62 - round(progress * 44)
    slash_points = []
    for step in range(13):
        t = step / 12.0
        px = 18 + round((slash_end_x - 18) * t)
        py = 62 - round((62 - slash_end_y) * t) + (1 if step % 2 else 0)
        slash_points.append((px, py))
    draw.line(slash_points, fill=(255, 56, 164, 225), width=5)
    draw.line(slash_points, fill=(66, 215, 255, 255), width=3)
    draw.line(slash_points, fill=(242, 251, 255, 255), width=1)

    # Break the smooth curves into visible pixel notches and flying fragments.
    for spark_index in range(11):
        t = (spark_index + 0.5) / 11.0
        angle = math.radians(start_angle + (end_angle - start_angle) * t)
        radius = 43 + (spark_index % 3) * 3
        x = round(cx + math.cos(angle) * radius)
        y = round(cy + math.sin(angle) * radius * 0.72)
        color = (255, 106, 191, 255) if spark_index % 2 else (113, 231, 255, 255)
        draw.rectangle((x, y, x + 2, y + 2), fill=color)

    for shard_index in range(5):
        angle = math.radians(215 + shard_index * 23 + frame_index * 2)
        distance = 18 + frame_index * 2 + shard_index * 3
        x = round(cx + math.cos(angle) * distance)
        y = round(cy + math.sin(angle) * distance * 0.75)
        draw.rectangle((x, y, x + 1 + (shard_index % 2), y + 1), fill=(221, 248, 255, 255))

    # A short impact core blooms only in the middle frames.
    if 2 <= frame_index <= 5:
        alpha = 255 if frame_index in (3, 4) else 175
        draw.rectangle((slash_end_x - 3, slash_end_y - 2, slash_end_x + 3, slash_end_y + 2), fill=(235, 251, 255, alpha))
        draw.rectangle((slash_end_x - 1, slash_end_y - 4, slash_end_x + 1, slash_end_y + 4), fill=(255, 94, 184, alpha))
    image.save(FX / f"cutscene_slash_{frame_index}.png", optimize=True)

frames = [Image.open(FX / f"cutscene_slash_{i}.png").convert("RGBA") for i in range(8)]
assert len({frame.tobytes() for frame in frames}) == 8, "Cutscene slash frames are not unique"
assert all(frame.size == (W, H) for frame in frames), "Cutscene slash dimensions changed"

cutscene = ROOT / "scripts" / "ui" / "cinematic_cutscene.gd"
source = cutscene.read_text(encoding="utf-8")

world_anchor = """    var fx := Node2D.new()
    fx.set_script(FX_SCRIPT)
    _world.add_child(fx)
"""
world_addition = world_anchor + """
    # Independent foreground atlas creates a second parallax plane in cutscenes.
    var foreground_atlas := AtlasTexture.new()
    foreground_atlas.atlas = load("res://assets/backgrounds/foreground_%d.png" % _chapter)
    foreground_source_x = min(4200 - 640, 240 + _chapter * 545)
    foreground_atlas.region = Rect2(foreground_source_x, 0, 640, 360)
    _foreground = TextureRect.new()
    _foreground.texture = foreground_atlas
    _foreground.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    _foreground.stretch_mode = TextureRect.STRETCH_SCALE
    _foreground.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _foreground.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    _foreground.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _foreground.z_index = 10
    _root.add_child(_foreground)
"""
if "_foreground = TextureRect.new()" not in source:
    if source.count(world_anchor) != 1:
        raise SystemExit(f"Cutscene foreground insertion anchor mismatch: {source.count(world_anchor)}")
    source = source.replace(world_anchor, world_addition, 1)

slash_old = """    var slash := Line2D.new()
    slash.points = PackedVector2Array([Vector2(205,214),Vector2(275,185),Vector2(348,206),Vector2(408,170)])
    slash.width = 5.0
    slash.default_color = Color(0.94,0.28,0.57,0.94)
    slash.add_point(Vector2(408,170))
    _world.add_child(slash)
"""
slash_new = """    var slash_frames := SpriteFrames.new()
    slash_frames.add_animation("katana")
    slash_frames.set_animation_speed("katana", 24.0)
    slash_frames.set_animation_loop("katana", false)
    for frame_index in range(8):
        slash_frames.add_frame("katana", load("res://assets/fx/cutscene_slash_%d.png" % frame_index))
    var slash := AnimatedSprite2D.new()
    slash.sprite_frames = slash_frames
    slash.animation = "katana"
    slash.position = Vector2(320, 190)
    slash.scale = Vector2(2.1, 2.1)
    slash.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    _world.add_child(slash)
    slash.play()
    slash.animation_finished.connect(slash.queue_free)
"""
if "slash_frames.add_animation(\"katana\")" not in source:
    if source.count(slash_old) != 1:
        raise SystemExit(f"Cutscene slash insertion anchor mismatch: {source.count(slash_old)}")
    source = source.replace(slash_old, slash_new, 1)

process_anchors = [
    """    if is_instance_valid(_background):
        _background.position.x = sin(_anim_clock * 0.34) * 2.5
""",
    """    if is_instance_valid(_background):
        _background.position = Vector2(sin(_anim_clock * 0.23) * 1.8, sin(_anim_clock * 0.37) * 0.8)"""
]
if "_foreground.position.x = sin(_anim_clock" not in source:
    for process_anchor in process_anchors:
        if source.count(process_anchor) == 1:
            process_new = process_anchor + """    if is_instance_valid(_foreground):
        _foreground.position.x = sin(_anim_clock * 0.22 + 0.8) * 4.5
"""
            source = source.replace(process_anchor, process_new, 1)
            break
    else:
        raise SystemExit("Cutscene background drift anchor not found for either v1.3 or v1.4.")

if "var _foreground: TextureRect" not in source:
    field_anchor = "var _background: TextureRect\n"
    if source.count(field_anchor) != 1:
        raise SystemExit("Cutscene foreground member declaration anchor mismatch")
    source = source.replace(field_anchor, field_anchor + "var _foreground: TextureRect\n", 1)

cutscene.write_text(source, encoding="utf-8")
assert "AnimatedSprite2D.new()" in source, "Raster slash animation was not installed"
assert "_foreground.position.x" in source, "Foreground parallax was not installed"
print("v1.8: generated 8 unique 128x80 pixel slash frames and added animated cutscene parallax.")
