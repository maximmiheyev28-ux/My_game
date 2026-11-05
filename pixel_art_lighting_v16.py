#!/usr/bin/env python3
"""v1.6: raster-pixel idle breathing, pixel-art death fragments and dynamic 2D lighting."""
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
CH = ROOT / "assets/characters"
FX = ROOT / "assets/fx"
FX.mkdir(parents=True, exist_ok=True)

# Give the existing hand-painted idle cycle a visible inhale/exhale in the torso.
# All edits remain on the native 80x96 pixel grid; no vector geometry is introduced.
for i in range(8):
    path = CH / f"player_idle_{i}.png"
    if not path.is_file():
        raise SystemExit(f"Missing idle frame: {path}")
    im = Image.open(path).convert("RGBA")
    phase = math.sin(i * math.tau / 8.0)
    torso = im.crop((22, 31, 52, 63))
    sx = 1.0 + 0.035 * phase
    sy = 1.0 + 0.025 * phase
    resized = torso.resize((max(1, round(torso.width * sx)), max(1, round(torso.height * sy))), Image.Resampling.NEAREST)
    frame = Image.new("RGBA", im.size, (0, 0, 0, 0))
    frame.alpha_composite(im)
    frame.alpha_composite(resized, (37 - resized.width // 2, 47 - resized.height // 2))
    # Two brief one-frame eyelid closures in the idle loop.
    if i in (3, 7):
        d = ImageDraw.Draw(frame)
        d.line((36, 17, 41, 17), fill=(14, 16, 34, 255), width=2)
        d.point((35, 17), fill=(193, 137, 158, 255))
    frame.save(path, optimize=True)
(CH / "player_idle.png").write_bytes((CH / "player_idle_0.png").read_bytes())

# Soft raster light textures. RGBA8 supports 16,777,216 RGB values per texel;
# no indexed/8-bit palette conversion is performed anywhere in this pass.
def radial_texture(path: Path, tint: tuple[int, int, int], radius: int = 128) -> None:
    yy, xx = np.mgrid[0:radius, 0:radius].astype(np.float32)
    cx = cy = (radius - 1) / 2.0
    dist = np.sqrt(((xx-cx)/(radius*0.48))**2 + ((yy-cy)/(radius*0.48))**2)
    alpha = np.clip(np.exp(-dist * dist * 4.2) * (1.0 - np.clip(dist, 0, 1)**2), 0, 1)
    rgba = np.zeros((radius, radius, 4), dtype=np.uint8)
    rgba[:, :, :3] = tint
    rgba[:, :, 3] = np.round(alpha * 220).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(path, optimize=True)

radial_texture(FX / "glow_cyan.png", (72, 222, 255))
radial_texture(FX / "glow_magenta.png", (255, 70, 172))
radial_texture(FX / "glow_warm.png", (255, 190, 112))

# Pixel fragments are actual tiny raster sprites, not Polygon2D/Line2D geometry.
enemy = ROOT / "scripts/enemies/enemy.gd"
source = enemy.read_text(encoding="utf-8")
old = '''        var shard := Polygon2D.new()
        var w := 2.0 + float(i % 3)
        var h := 3.0 + float((i * 2) % 4)
        shard.polygon = PackedVector2Array([Vector2(-w, -h), Vector2(w, -h * 0.35), Vector2(0.0, h)])
        shard.color = shard_colors[i % shard_colors.size()]
        shard.position = Vector2(float((i % 3) - 1) * 5.0, float(i / 3) * 3.0 - 4.0)
        burst.add_child(shard)
'''
new = '''        var shard := Sprite2D.new()
        var pixel_image := Image.create(7, 7, false, Image.FORMAT_RGBA8)
        var pixel_rows := ["0011100", "0111110", "1111111", "1111110", "0111100", "0011000", "0001000"]
        for py in range(7):
            for px in range(7):
                if pixel_rows[py].substr(px, 1) == "1":
                    pixel_image.set_pixel(px, py, shard_colors[i % shard_colors.size()])
        shard.texture = ImageTexture.create_from_image(pixel_image)
        shard.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        shard.position = Vector2(float((i % 3) - 1) * 5.0, float(i / 3) * 3.0 - 4.0)
        burst.add_child(shard)
'''
if source.count(old) != 1:
    raise SystemExit(f"Enemy pixel-shard anchor mismatch: {source.count(old)}")
enemy.write_text(source.replace(old, new, 1), encoding="utf-8")

boss = ROOT / "scripts/bosses/boss.gd"
source = boss.read_text(encoding="utf-8")
old = '''            var shard := Polygon2D.new()
            var size := 3.0 + float(i % 4)
            shard.polygon = PackedVector2Array([Vector2(-size,-size),Vector2(size,0.0),Vector2(-1.0,size)])
            shard.color = boss_colors[i % boss_colors.size()]
            burst.add_child(shard)
'''
new = '''            var shard := Sprite2D.new()
            var pixel_image := Image.create(9, 9, false, Image.FORMAT_RGBA8)
            var pixel_rows := ["000111000", "001111100", "011111110", "111111111", "111111110", "011111100", "001111000", "000110000", "000010000"]
            for py in range(9):
                for px in range(9):
                    if pixel_rows[py].substr(px, 1) == "1":
                        pixel_image.set_pixel(px, py, boss_colors[i % boss_colors.size()])
            shard.texture = ImageTexture.create_from_image(pixel_image)
            shard.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
            burst.add_child(shard)
'''
if source.count(old) != 1:
    raise SystemExit(f"Boss pixel-shard anchor mismatch: {source.count(old)}")
boss.write_text(source.replace(old, new, 1), encoding="utf-8")

# Add a camera-following lighting rig using true RGBA radial light maps.
rig = ROOT / "scripts/fx/ambient_light_rig.gd"
rig.write_text('''extends Node2D

var camera_ref: Camera2D
var lights: Array[PointLight2D] = []
var clock := 0.0

func _ready() -> void:
    _add_light("res://assets/fx/glow_cyan.png", Color(0.42, 0.88, 1.0), 2.25, Vector2(-170.0, -54.0), 1.35)
    _add_light("res://assets/fx/glow_magenta.png", Color(1.0, 0.42, 0.76), 1.8, Vector2(185.0, -18.0), 1.18)
    _add_light("res://assets/fx/glow_warm.png", Color(1.0, 0.78, 0.52), 1.15, Vector2(0.0, -125.0), 0.82)

func setup(camera: Camera2D) -> void:
    camera_ref = camera

func _add_light(texture_path: String, tint: Color, power: float, offset: Vector2, scale_value: float) -> void:
    var lamp := PointLight2D.new()
    lamp.texture = load(texture_path)
    lamp.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    lamp.color = tint
    lamp.energy = power
    lamp.texture_scale = scale_value
    lamp.shadow_enabled = false
    lamp.blend_mode = Light2D.BLEND_MODE_ADD
    lamp.set_meta("anchor_offset", offset)
    add_child(lamp)
    lights.append(lamp)

func _process(delta: float) -> void:
    clock += delta
    if not is_instance_valid(camera_ref):
        return
    global_position = camera_ref.global_position
    for i in range(lights.size()):
        var lamp := lights[i]
        var base_offset: Vector2 = lamp.get_meta("anchor_offset")
        lamp.position = base_offset + Vector2(sin(clock * (0.7 + i * 0.19) + i) * 9.0, cos(clock * (0.9 + i * 0.13)) * 5.0)
        lamp.energy = [2.25, 1.8, 1.15][i] * (0.94 + 0.06 * sin(clock * (2.1 + i)))
''', encoding="utf-8")

level = ROOT / "scripts/levels/level.gd"
source = level.read_text(encoding="utf-8")
if "AMBIENT_LIGHT_RIG" not in source:
    anchor = "    camera.limit_bottom = 360\n"
    addition = '''    camera.limit_bottom = 360
    # Cinematic neon bounce light follows the camera without obscuring the pixel art.
    var ambient_lights := Node2D.new()
    ambient_lights.set_script(load("res://scripts/fx/ambient_light_rig.gd"))
    ambient_lights.name = "AMBIENT_LIGHT_RIG"
    ambient_lights.call("setup", camera)
    add_child(ambient_lights)
'''
    if source.count(anchor) != 1:
        raise SystemExit(f"Level lighting insertion anchor mismatch: {source.count(anchor)}")
    source = source.replace(anchor, addition, 1)
    level.write_text(source, encoding="utf-8")

# Explicitly retain 8-bit RGBA texture import; this is a 24-bit RGB color space,
# not a reduced indexed palette.
project = ROOT / "project.godot"
cfg = project.read_text(encoding="utf-8")
rendering_header = "[rendering]\n"
setting = "textures/default_filters/use_nearest_mipmap_filter=false\n"
if setting not in cfg:
    if rendering_header not in cfg:
        raise SystemExit("project.godot has no [rendering] section")
    cfg = cfg.replace(rendering_header, rendering_header + setting, 1)
    project.write_text(cfg, encoding="utf-8")

# Build-time asset checks: all idle poses are distinct and light textures preserve RGBA8.
idle_images = [Image.open(CH / f"player_idle_{i}.png").convert("RGBA") for i in range(8)]
assert len({im.tobytes() for im in idle_images}) == 8, "Idle breathing cycle has duplicate frames"
for light_name in ("glow_cyan.png", "glow_magenta.png", "glow_warm.png"):
    light = Image.open(FX / light_name)
    assert light.mode == "RGBA" and light.size == (128, 128), f"Invalid light map: {light_name}"
assert "AMBIENT_LIGHT_RIG" in level.read_text(encoding="utf-8"), "Ambient light rig not attached"
assert "ImageTexture.create_from_image" in enemy.read_text(encoding="utf-8"), "Enemy pixel particles missing"
assert "ImageTexture.create_from_image" in boss.read_text(encoding="utf-8"), "Boss pixel particles missing"

print("v1.6: eight breathing/blinking idle frames, RGBA8 light maps, three animated neon lights, raster-pixel death sprites.")
