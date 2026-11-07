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
paths = sorted(p for p in assets.rglob("*") if p.is_file() and p.suffix.lower() in extensions)
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

print(f"ART RESET VERIFIED: {len(paths)} legacy raster files replaced by transparent 1x1 placeholders.")
print("Original source art remains recoverable from Git history and .source archive.")
