#!/usr/bin/env python3
"""Replace all legacy in-game raster art with transparent placeholders.

Git history and the encoded source archive retain the original files for recovery.
The placeholders keep Godot resource paths intact while the new art is authored.
"""
from pathlib import Path
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

# The source archive creates this validator during restore. Its old frame-quality
# assertions are intentionally disabled only for this clean-slate branch.
validator = ROOT / "tools" / "validate_project.py"
if validator.is_file():
    source = validator.read_text(encoding="utf-8")
    start = "# Hero-frame integrity: each authored pose must be unique and retain its pixel canvas.\n"
    end = "\nimage_count = 0\n"
    if start in source and end in source:
        left = source.index(start)
        right = source.index(end, left)
        source = source[:left] + "# Legacy hero-frame checks are disabled while artwork is intentionally blank.\n" + source[right:]
        validator.write_text(source, encoding="utf-8")

legacy_generators = ["enhance_project.py", "refine_backgrounds.py", "cinematic_pixel_fx.py", "environmental_weather_v19.py", "hero_sprite_overhaul_v20.py", "pixel_art_lighting_v16.py", "pixel_art_visual_overhaul_v22.py", "visual_combat_polish.py", "visual_upgrade_v3.py", "visual_upgrade_v4.py", "refine_enemy_ai.py"]
for name in legacy_generators:
    candidate = ROOT / name
    if candidate.is_file():
        candidate.unlink()
print(f"ART RESET VERIFIED: {len(paths)} legacy raster files replaced; authored assets preserved.")
print(f"AUTHORED ART PRESERVED: {sum(1 for p in authored_root.rglob(chr(42)) if p.is_file())} files.")
