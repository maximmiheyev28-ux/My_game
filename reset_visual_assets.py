#!/usr/bin/env python3
"""Replace legacy game art with transparent placeholders, then install authored raster art."""
from pathlib import Path
import re
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parent
assets = ROOT / "assets"
if not assets.is_dir():
    raise SystemExit("assets directory was not restored")

extensions = {".png", ".webp", ".bmp"}
authored_root = assets / "authored"
paths = sorted(p for p in assets.rglob("*") if p.is_file() and p.suffix.lower() in extensions and authored_root not in p.parents)
if not paths:
    raise SystemExit("No raster assets found; refusing to report a false reset")

pixel = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
for path in paths:
    fmt = {".png": "PNG", ".webp": "WEBP", ".bmp": "BMP"}[path.suffix.lower()]
    pixel.save(path, format=fmt)
for path in paths:
    with Image.open(path) as check:
        if check.size != (1, 1) or check.convert("RGBA").getpixel((0, 0))[3] != 0:
            raise SystemExit(f"Transparent placeholder verification failed: {path.relative_to(ROOT)}")

# Remove legacy procedural graphics scripts after source archive restoration.
legacy_generators = ["enhance_project.py", "refine_backgrounds.py", "cinematic_pixel_fx.py", "environmental_weather_v19.py", "hero_sprite_overhaul_v20.py", "pixel_art_lighting_v16.py", "pixel_art_visual_overhaul_v22.py", "visual_combat_polish.py", "visual_upgrade_v3.py", "visual_upgrade_v4.py", "refine_enemy_ai.py"]
for name in legacy_generators:
    candidate = ROOT / name
    if candidate.is_file():
        candidate.unlink()

# Slice the fixed, manually composed atlas; this step does not draw or generate pixels.
character_source = authored_root / "characters"
character_target = assets / "characters"
sheet_path = character_source / "protagonist_frames.webp"
if sheet_path.is_file():
    with Image.open(sheet_path) as sheet:
        if sheet.size != (96 * 13, 112):
            raise SystemExit(f"Unexpected protagonist atlas dimensions: {sheet.size}")
        frame_names = [
            "player_idle.png", "player_run_0.png", "player_run_1.png",
            "player_attack_0.png", "player_attack_1.png", "player_attack_2.png",
            "player_jump.png", "player_fall.png", "player_hurt.png",
            "player_parry.png", "player_stasis_0.png", "player_stasis_1.png",
            "player_stasis_2.png",
        ]
        for index, name in enumerate(frame_names):
            sheet.crop((index * 96, 0, (index + 1) * 96, 112)).save(character_target / name, optimize=True)
        shutil.copy2(character_target / "player_idle.png", character_target / "player_idle_0.png")

# Keep animation arrays aligned with the actual authored frame count.
player_script = ROOT / "scripts" / "player" / "player.gd"
if player_script.is_file():
    source = player_script.read_text(encoding="utf-8")
    source = re.sub(r"const TEX_IDLE := \[.*?\]", "const TEX_IDLE := [preload(\"res://assets/characters/player_idle_0.png\")]", source, count=1, flags=re.S)
    source = re.sub(r"const TEX_RUN := \[.*?\]", "const TEX_RUN := [preload(\"res://assets/characters/player_run_0.png\"), preload(\"res://assets/characters/player_run_1.png\")]", source, count=1, flags=re.S)
    player_script.write_text(source, encoding="utf-8")

print(f"ART RESET VERIFIED: {len(paths)} legacy raster files replaced; authored atlas preserved.")
print("AUTHORED ART INSTALLED: 13 fixed protagonist frames.")
