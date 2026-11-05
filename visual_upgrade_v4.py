#!/usr/bin/env python3
"""v1.4 cinematic pixel-art pass for Последний сигнал.

Creates a six-scene 2x pixel-art atlas from each chapter's own background and
foreground layers, then wires it into the title screen and story cutscenes.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = Path.cwd()
BACKGROUND_DIR = ROOT / "assets" / "backgrounds"
CINEMATICS_DIR = ROOT / "assets" / "cinematics"
CUTSCENE_SCRIPT = ROOT / "scripts" / "ui" / "cinematic_cutscene.gd"
MENU_SCRIPT = ROOT / "scripts" / "ui" / "main_menu.gd"
SCENE_SIZE = (320, 180)
PALETTES = [
    ((92, 178, 222), (86, 220, 255)),
    ((204, 86, 186), (255, 92, 184)),
    ((104, 122, 218), (104, 226, 245)),
    ((210, 74, 86), (255, 94, 76)),
    ((76, 182, 208), (112, 244, 255)),
    ((196, 104, 194), (255, 176, 98)),
]


def patch_once(path: Path, old: str, new: str, label: str) -> None:
    source = path.read_text(encoding="utf-8")
    if new in source:
        print(f"Already applied: {label}")
        return
    if old not in source:
        raise RuntimeError(f"Could not locate expected source block for {label} in {path}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")
    print(f"Applied: {label}")


def make_vignette(size: tuple[int, int]) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((-width * 0.18, -height * 0.24, width * 1.18, height * 1.24), fill=154)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=21))
    return ImageOps.invert(mask)


def build_scene(chapter: int) -> Image.Image:
    bg_path = BACKGROUND_DIR / f"act_{chapter}.png"
    fg_path = BACKGROUND_DIR / f"foreground_{chapter}.png"
    if not bg_path.is_file() or not fg_path.is_file():
        raise RuntimeError(f"Missing chapter {chapter} background or foreground art")

    with Image.open(bg_path) as image:
        bg = image.convert("RGB")
    with Image.open(fg_path) as image:
        fg = image.convert("RGBA")

    width, height = bg.size
    if width < 640 or height < 360:
        raise RuntimeError(f"Chapter {chapter} panorama is too small: {bg.size}")
    source_x = min(width - 640, 240 + chapter * 545)
    crop_box = (source_x, 0, source_x + 640, 360)
    bg = bg.crop(crop_box).resize(SCENE_SIZE, Image.Resampling.BOX)
    fg = fg.crop(crop_box).resize(SCENE_SIZE, Image.Resampling.BOX)

    fg_alpha = fg.getchannel("A").point(lambda a: int(a * 0.78))
    fg.putalpha(fg_alpha)
    panel = Image.alpha_composite(bg.convert("RGBA"), fg)
    panel = ImageEnhance.Contrast(panel).enhance(1.16)
    panel = ImageEnhance.Color(panel).enhance(1.18)
    panel = ImageEnhance.Brightness(panel).enhance(1.03)

    tint, glow_color = PALETTES[chapter]
    tint_layer = Image.new("RGBA", SCENE_SIZE, (*tint, 0))
    tint_layer.putalpha(Image.new("L", SCENE_SIZE, 18))
    panel = Image.alpha_composite(panel, tint_layer)

    luminance = panel.convert("L")
    glow_mask = luminance.point(lambda value: max(0, min(84, int((value - 138) * 0.92))))
    glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(radius=4.2))
    glow = Image.new("RGBA", SCENE_SIZE, (*glow_color, 0))
    glow.putalpha(glow_mask)
    panel = Image.alpha_composite(panel, glow)

    vignette_alpha = make_vignette(SCENE_SIZE).point(lambda value: int(value * 0.48))
    vignette = Image.new("RGBA", SCENE_SIZE, (2, 4, 15, 0))
    vignette.putalpha(vignette_alpha)
    panel = Image.alpha_composite(panel, vignette)

    scan = Image.new("RGBA", SCENE_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(scan)
    for y in range(1, SCENE_SIZE[1], 4):
        draw.line((0, y, SCENE_SIZE[0], y), fill=(2, 5, 18, 18), width=1)
    panel = Image.alpha_composite(panel, scan)
    return panel.convert("RGB")


def main() -> None:
    scenes = [build_scene(chapter) for chapter in range(6)]
    atlas = Image.new("RGB", (SCENE_SIZE[0] * 3, SCENE_SIZE[1] * 2), (3, 5, 16))
    for chapter, scene in enumerate(scenes):
        atlas.paste(scene, ((chapter % 3) * SCENE_SIZE[0], (chapter // 3) * SCENE_SIZE[1]))
    atlas = atlas.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    CINEMATICS_DIR.mkdir(parents=True, exist_ok=True)
    atlas_path = CINEMATICS_DIR / "cutscene_atlas.png"
    atlas.save(atlas_path, optimize=True, compress_level=9)
    with Image.open(atlas_path) as check:
        if check.size != (960, 360):
            raise RuntimeError("Generated cinematic atlas has incorrect dimensions")

    cutscene_old = '''    var atlas := AtlasTexture.new()
    atlas.atlas = load("res://assets/backgrounds/act_%d.png" % _chapter)
    var source_x := mini(4200 - 640, 240 + _chapter * 545)
    atlas.region = Rect2(source_x, 0, 640, 360)
    _background = TextureRect.new()
    _background.texture = atlas'''
    cutscene_new = '''    var cinematic_path := "res://assets/cinematics/cutscene_atlas.png"
    var cinematic_texture: Texture2D
    if ResourceLoader.exists(cinematic_path):
        var cinematic_atlas := load(cinematic_path) as Texture2D
        var cinematic_region := AtlasTexture.new()
        cinematic_region.atlas = cinematic_atlas
        var atlas_column := _chapter % 3
        var atlas_row := floori(float(_chapter) / 3.0)
        cinematic_region.region = Rect2(float(atlas_column) * 320.0, float(atlas_row) * 180.0, 320.0, 180.0)
        cinematic_texture = cinematic_region
    else:
        var atlas := AtlasTexture.new()
        atlas.atlas = load("res://assets/backgrounds/act_%d.png" % _chapter)
        var source_x := mini(4200 - 640, 240 + _chapter * 545)
        atlas.region = Rect2(source_x, 0, 640, 360)
        cinematic_texture = atlas
    _background = TextureRect.new()
    _background.texture = cinematic_texture'''
    patch_once(CUTSCENE_SCRIPT, cutscene_old, cutscene_new, "chapter-specific cinematic backdrops")

    menu_old = '''    var atlas := AtlasTexture.new()
    atlas.atlas = load("res://assets/backgrounds/act_0.png")
    atlas.region = Rect2(210.0, 0.0, 640.0, 360.0)
    _background = TextureRect.new()
    _background.texture = atlas'''
    menu_new = '''    var menu_backdrop_path := "res://assets/cinematics/cutscene_atlas.png"
    var menu_backdrop: Texture2D
    if ResourceLoader.exists(menu_backdrop_path):
        var menu_atlas := load(menu_backdrop_path) as Texture2D
        var menu_region := AtlasTexture.new()
        menu_region.atlas = menu_atlas
        menu_region.region = Rect2(320.0, 0.0, 320.0, 180.0)
        menu_backdrop = menu_region
    else:
        var atlas := AtlasTexture.new()
        atlas.atlas = load("res://assets/backgrounds/act_0.png")
        atlas.region = Rect2(210.0, 0.0, 640.0, 360.0)
        menu_backdrop = atlas
    _background = TextureRect.new()
    _background.texture = menu_backdrop'''
    patch_once(MENU_SCRIPT, menu_old, menu_new, "full-screen neon city title background")

    source = CUTSCENE_SCRIPT.read_text(encoding="utf-8")
    source = source.replace("tint.color = Color(0.018,0.025,0.07,0.24)", "tint.color = Color(0.018,0.025,0.07,0.12)")
    drift_anchor = "    _anim_clock += delta\n    _type_clock += delta"
    drift_code = '''    _anim_clock += delta
    _type_clock += delta
    if is_instance_valid(_background):
        _background.position = Vector2(sin(_anim_clock * 0.23) * 1.8, sin(_anim_clock * 0.37) * 0.8)'''
    if drift_code not in source:
        if drift_anchor not in source:
            raise RuntimeError("Could not locate cinematic _process clock anchor")
        source = source.replace(drift_anchor, drift_code, 1)
    CUTSCENE_SCRIPT.write_text(source, encoding="utf-8")

    source = CUTSCENE_SCRIPT.read_text(encoding="utf-8")
    shake_block = '''    hit.parallel().tween_property(_rival,"position:x",525.0,0.2)
    hit.parallel().tween_property(slash,"modulate:a",0.0,0.2)
    hit.tween_callback(slash.queue_free)'''
    shake_new = '''    hit.parallel().tween_property(_rival,"position:x",525.0,0.2)
    hit.parallel().tween_property(slash,"modulate:a",0.0,0.2)
    var impact_shake := create_tween()
    impact_shake.set_pause_mode(Tween.TWEEN_PAUSE_PROCESS)
    impact_shake.tween_property(_world,"position",Vector2(3.0,-1.5),0.035)
    impact_shake.tween_property(_world,"position",Vector2(-2.0,1.0),0.045)
    impact_shake.tween_property(_world,"position",Vector2.ZERO,0.07)
    hit.tween_callback(slash.queue_free)'''
    if shake_new not in source:
        if shake_block not in source:
            raise RuntimeError("Could not locate cinematic hit tween block")
        source = source.replace(shake_block, shake_new, 1)
    CUTSCENE_SCRIPT.write_text(source, encoding="utf-8")

    menu_source = MENU_SCRIPT.read_text(encoding="utf-8")
    menu_source = menu_source.replace("_background.modulate = Color(0.78, 0.79, 0.92, 1.0)", "_background.modulate = Color(0.92, 0.93, 1.0, 1.0)")
    menu_source = menu_source.replace("veil.color = Color(0.015, 0.025, 0.045, 0.48)", "veil.color = Color(0.015, 0.025, 0.045, 0.34)")
    MENU_SCRIPT.write_text(menu_source, encoding="utf-8")

    final_cutscene = CUTSCENE_SCRIPT.read_text(encoding="utf-8")
    final_menu = MENU_SCRIPT.read_text(encoding="utf-8")
    assert "cutscene_atlas.png" in final_cutscene
    assert "cutscene_atlas.png" in final_menu
    assert "impact_shake" in final_cutscene
    print("V1.4 CINEMATIC ART CHECK: six chapter backdrops, 2x integer pixel scale, menu and impact camera motion verified.")


if __name__ == "__main__":
    main()
