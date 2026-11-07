#!/usr/bin/env python3
"""Strict visual-asset QA for Последний сигнал. Runs after all art generators."""
from pathlib import Path
from PIL import Image, ImageStat, ImageChops
import math

ROOT = Path(__file__).resolve().parents[1]
BG = ROOT / "assets/backgrounds"
CH = ROOT / "assets/characters"
FX = ROOT / "assets/fx"
CIN = ROOT / "assets/cinematics/cutscene_atlas.webp"

def fail(message):
    raise SystemExit("PIXEL ART QA FAILED: " + message)

def rgb_metrics(image):
    rgb = image.convert("RGB")
    reduced = rgb.resize((max(1, rgb.width // 3), max(1, rgb.height // 3)), Image.Resampling.BOX)
    colors = len(reduced.getcolors(reduced.width * reduced.height) or [])
    lum = rgb.convert("L")
    contrast = ImageStat.Stat(lum).stddev[0]
    return colors, contrast

def alpha_ratio(image):
    alpha = image.getchannel("A")
    hist = alpha.histogram()
    total = image.width * image.height
    occupied = total - hist[0]
    bbox = alpha.getbbox()
    return occupied / total, bbox

def distinct_frame_metrics(paths, label, expected_size, loop=True):
    frames = []
    for path in paths:
        if not path.is_file():
            fail(f"{label}: missing {path.name}")
        with Image.open(path) as source:
            im = source.convert("RGBA")
            if im.size != expected_size:
                fail(f"{label}: {path.name} size {im.size}, expected {expected_size}")
            ratio, bbox = alpha_ratio(im)
            if bbox is None or ratio < 0.025:
                fail(f"{label}: {path.name} has too little visible sprite content ({ratio:.3%})")
            frames.append(im.copy())
    signatures = {im.tobytes() for im in frames}
    if len(signatures) != len(frames):
        fail(f"{label}: duplicate frames ({len(signatures)}/{len(frames)} unique)")
    changes = []
    transition_count = len(frames) if loop else len(frames) - 1
    for index in range(transition_count):
        a, b = frames[index], frames[(index + 1) % len(frames)]
        diff = ImageChops.difference(a, b).convert("RGBA")
        changed = sum(1 for px in diff.getdata() if px[3] or px[0] or px[1] or px[2])
        changes.append(changed / (expected_size[0] * expected_size[1]))
    if min(changes) < 0.0008:
        fail(f"{label}: animation has near-static transition ({min(changes):.3%} changed pixels)")
    if max(changes) > 0.38:
        fail(f"{label}: unstable animation transition ({max(changes):.1%} changed pixels)")
    return min(changes), max(changes)

def main():
    # Six panoramas: dimensions, mode, contrast, palette complexity and six distinct chapters.
    chapter_signatures = set()
    for chapter in range(6):
        path = BG / f"act_{chapter}.png"
        if not path.is_file():
            fail(f"missing chapter panorama {path.name}")
        with Image.open(path) as source:
            im = source.convert("RGB")
            if im.size != (4200, 360):
                fail(f"{path.name}: expected 4200x360, got {im.size}")
            colors, contrast = rgb_metrics(im)
            if colors < 80 or contrast < 18:
                fail(f"{path.name}: weak visual complexity (colors={colors}, contrast={contrast:.1f})")
            # A panorama must remain composed across its whole length, not just at its first landmark.
            for segment in range(7):
                crop = im.crop((segment * 600, 0, (segment + 1) * 600, 360))
                reduced = crop.resize((200, 120), Image.Resampling.BOX)
                segment_colors = len(reduced.getcolors(200 * 120) or [])
                segment_contrast = ImageStat.Stat(reduced.convert("L")).stddev[0]
                if segment_colors < 28 or segment_contrast < 9:
                    fail(f"{path.name}: underdeveloped panorama segment {segment + 1}/7 (colors={segment_colors}, contrast={segment_contrast:.1f})")
            chapter_signatures.add(im.resize((140, 12), Image.Resampling.BOX).tobytes())
        fg_path = BG / f"foreground_{chapter}.png"
        if not fg_path.is_file():
            fail(f"missing parallax foreground {fg_path.name}")
        with Image.open(fg_path) as source:
            fg = source.convert("RGBA")
            if fg.size != (4200, 360):
                fail(f"{fg_path.name}: wrong canvas size")
            ratio, bbox = alpha_ratio(fg)
            if bbox is None or not (0.001 <= ratio <= 0.30):
                fail(f"{fg_path.name}: implausible alpha coverage {ratio:.2%}")
    if len(chapter_signatures) != 6:
        fail("chapter panoramas are not sufficiently distinct")

    # Enemy and boss animation: all frames visible, non-duplicates, and genuinely changing.
    for kind in ("guard", "shooter", "hunter", "aberration"):
        distinct_frame_metrics([CH / f"{kind}_{i}.png" for i in range(6)], f"enemy/{kind}", (60, 64))
    for kind in ("warden", "kair", "double", "surgeon", "watcher", "sentry"):
        distinct_frame_metrics([CH / f"boss_{kind}_{i}.png" for i in range(6)], f"boss/{kind}", (96, 112))

    # Hero animation: validate all core action sequences, not only the run loop.
    hero_sequences = {
        "idle": 8, "run": 10, "attack": 8, "jump": 6, "fall": 6,
        "hurt": 6, "parry": 6, "stasis": 8, "death": 8
    }
    for action, count in hero_sequences.items():
        paths = [CH / f"player_{action}_{i}.png" for i in range(count)]
        distinct_frame_metrics(paths, f"hero/{action}", (96, 112), loop=(action != "death"))

    # Weather/FX assets must be real transparent pixel sprites, not empty placeholders.
    fx_names = ["pixel_rain", "pixel_steam", "pixel_window", "pixel_reflection"]
    fx_names += [f"pixel_petal_{i}" for i in range(6)]
    for name in fx_names:
        path = FX / f"{name}.png"
        if not path.is_file():
            fail(f"missing effect sprite {name}")
        with Image.open(path) as source:
            im = source.convert("RGBA")
            ratio, bbox = alpha_ratio(im)
            if bbox is None or ratio < 0.08:
                fail(f"{name}: empty or implausibly dense alpha ({ratio:.1%})")
            colors, _ = rgb_metrics(im)
            if colors < 2:
                fail(f"{name}: no color variation")

    # Six distinct cinematic panels in a lossless 3x2 atlas.
    if not CIN.is_file():
        fail("missing cinematic atlas")
    with Image.open(CIN) as source:
        atlas = source.convert("RGB")
        if atlas.size != (960, 360):
            fail(f"cinematic atlas dimensions {atlas.size}, expected (960, 360)")
        panels = []
        for chapter in range(6):
            box = ((chapter % 3) * 320, (chapter // 3) * 180,
                   (chapter % 3 + 1) * 320, (chapter // 3 + 1) * 180)
            panel = atlas.crop(box)
            colors, contrast = rgb_metrics(panel)
            if colors < 65 or contrast < 14:
                fail(f"cinematic panel {chapter}: low detail/contrast (colors={colors}, contrast={contrast:.1f})")
            panels.append(panel.resize((80, 45), Image.Resampling.BOX).tobytes())
        if len(set(panels)) != 6:
            fail("cinematic panels are duplicated or insufficiently distinct")

    print("STRICT PIXEL ART QA PASSED: 6 full-length panoramas, 6 parallax layers, 9 hero action loops, 24 enemy frames, 36 boss frames, 10 FX sprites, 6 cinematic panels.")
if __name__ == "__main__":
    main()
