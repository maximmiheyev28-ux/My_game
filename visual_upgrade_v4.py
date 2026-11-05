#!/usr/bin/env python3
"""v1.4 cinematic art pass for Последний сигнал.

Installs two original pixel-art atlases containing six chapter-specific
backdrops and wires them into chapter intros and the title screen.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image

ROOT = Path.cwd()
CINEMATICS = ROOT / "assets" / "cinematics"
CUTSCENE_SCRIPT = ROOT / "scripts" / "ui" / "cinematic_cutscene.gd"
MENU_SCRIPT = ROOT / "scripts" / "ui" / "main_menu.gd"


def require_file(path: Path) -> None:
    if not path.is_file() or path.stat().st_size < 1024:
        raise RuntimeError(f"Missing or too-small visual asset: {path}")


def patch_once(path: Path, old: str, new: str, label: str) -> None:
    source = path.read_text(encoding="utf-8")
    if new in source:
        print(f"Already applied: {label}")
        return
    if old not in source:
        raise RuntimeError(f"Could not locate expected source block for {label} in {path}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")
    print(f"Applied: {label}")


def main() -> None:
    for strip_index in range(2):
        image_path = CINEMATICS / f"cutscene_strip_{strip_index}.webp"
        require_file(image_path)
        with Image.open(image_path) as image:
            if image.size != (1920, 360):
                raise RuntimeError(f"Unexpected cinematic atlas dimensions for {image_path}: {image.size}")
            if image.mode not in ("P", "RGB", "RGBA"):
                raise RuntimeError(f"Unsupported image mode for {image_path}: {image.mode}")

    cutscene_old = '''    var atlas := AtlasTexture.new()
    atlas.atlas = load("res://assets/backgrounds/act_%d.png" % _chapter)
    var source_x := mini(4200 - 640, 240 + _chapter * 545)
    atlas.region = Rect2(source_x, 0, 640, 360)
    _background = TextureRect.new()
    _background.texture = atlas'''
    cutscene_new = '''    var strip_index := 0 if _chapter < 3 else 1
    var local_chapter := _chapter % 3
    var cinematic_path := "res://assets/cinematics/cutscene_strip_%d.webp" % strip_index
    var cinematic_texture: Texture2D
    if ResourceLoader.exists(cinematic_path):
        var cinematic_atlas := load(cinematic_path) as Texture2D
        var cinematic_region := AtlasTexture.new()
        cinematic_region.atlas = cinematic_atlas
        cinematic_region.region = Rect2(float(local_chapter) * 640.0, 0.0, 640.0, 360.0)
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
    menu_new = '''    var menu_backdrop_path := "res://assets/cinematics/cutscene_strip_0.webp"
    var menu_backdrop: Texture2D
    if ResourceLoader.exists(menu_backdrop_path):
        var menu_atlas := load(menu_backdrop_path) as Texture2D
        var menu_region := AtlasTexture.new()
        menu_region.atlas = menu_atlas
        menu_region.region = Rect2(640.0, 0.0, 640.0, 360.0)
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
    assert "cutscene_strip_%d.webp" in final_cutscene
    assert "cutscene_strip_0.webp" in final_menu
    assert "impact_shake" in final_cutscene
    print("V1.4 CINEMATIC ART CHECK: two 1920x360 WebP atlases with six 640x360 chapter scenes verified and wired.")


if __name__ == "__main__":
    main()
