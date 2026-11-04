#!/usr/bin/env python3
"""Restore the compressed Godot project stored in a base64 tar.gz archive."""
from __future__ import annotations

import base64
import io
import gzip
import hashlib
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
full_archive = ROOT / ".source" / "source-full.b64"

if full_archive.is_file():
    encoded = full_archive.read_text(encoding="ascii").strip()
    source_label = full_archive.name
else:
    parts = sorted((ROOT / ".source").glob("part-*.b64"))
    expected = [f"part-{i:03d}.b64" for i in range(1, 53)]
    present = {part.name for part in parts}
    missing = [name for name in expected if name not in present]
    if missing:
        raise SystemExit("Source archive incomplete. Missing: " + ", ".join(missing))
    encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
    source_label = f"{len(parts)} split parts"

try:
    data = base64.b64decode(encoded, validate=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise SystemExit(f"Unsupported archive entry: {member.name}")
            target = (ROOT / member.name).resolve()
            if target != ROOT and ROOT not in target.parents:
                raise SystemExit(f"Unsafe archive path: {member.name}")
        archive.extractall(ROOT, members=members)

    def replace_once(path: Path, old_text: str, new_text: str, description: str) -> None:
        current = path.read_text(encoding="utf-8")
        if old_text in current:
            path.write_text(current.replace(old_text, new_text, 1), encoding="utf-8")
        elif new_text not in current:
            raise SystemExit(f"Could not apply compatibility patch: {description}")

    # Godot 4.7.2 needs an explicit type for this choice dictionary.
    game_state = ROOT / "scripts" / "game" / "game_state.gd"
    replace_once(
        game_state,
        "var data := CHOICES[clampi(chapter_index, 0, CHOICES.size()-1)]",
        "var data: Dictionary = CHOICES[clampi(chapter_index, 0, CHOICES.size()-1)]",
        "choice dictionary type",
    )

    # Keep the standard prebuilt APK template: SDK overrides require Gradle Build.
    export_preset = ROOT / "export_presets.cfg"
    preset_text = export_preset.read_text(encoding="utf-8")
    preset_lines = [
        line for line in preset_text.splitlines(keepends=True)
        if not line.startswith("gradle_build/min_sdk=")
        and not line.startswith("gradle_build/target_sdk=")
    ]
    preset_text = "".join(preset_lines)
    if "gradle_build/use_gradle_build=false" not in preset_text:
        raise SystemExit("Android preset is not configured for the prebuilt APK template.")
    export_preset.write_text(preset_text, encoding="utf-8")

    # Android export requires ETC2/ASTC textures on Linux hosts.
    project_config = ROOT / "project.godot"
    config_text = project_config.read_text(encoding="utf-8")
    rendering_header = "[rendering]\n"
    texture_setting = "textures/vram_compression/import_etc2_astc=true\n"
    if texture_setting not in config_text:
        if rendering_header not in config_text:
            raise SystemExit("Could not find the [rendering] section in project.godot.")
        config_text = config_text.replace(rendering_header, rendering_header + texture_setting, 1)
        project_config.write_text(config_text, encoding="utf-8")

    # Update the offline validator to check the prebuilt-template configuration.
    validator = ROOT / "tools" / "validate_project.py"
    replace_once(
        validator,
        'if \'gradle_build/min_sdk=24\' not in export_config:\n    errors.append("Android minimum SDK setting is not 24")\n',
        'if "gradle_build/use_gradle_build=false" not in export_config:\n'
        '    errors.append("Android export should use the prebuilt APK template")\n'
        'if "gradle_build/min_sdk=" in export_config or "gradle_build/target_sdk=" in export_config:\n'
        '    errors.append("SDK level overrides require Gradle Build and must be omitted for the prebuilt template")\n',
        "Android preset validation rule",
    )

    # The cinematic title references the chapter field stored on the director.
    cutscene = ROOT / "scripts" / "ui" / "cinematic_cutscene.gd"
    replace_once(
        cutscene,
        'chapter_tag.text = "КОНТУР // КИНЕМАТОГРАФИЧЕСКАЯ ЗАПИСЬ  %02d" % (chapter+1)',
        'chapter_tag.text = "КОНТУР // КИНЕМАТОГРАФИЧЕСКАЯ ЗАПИСЬ  %02d" % (_chapter+1)',
        "cinematic chapter title scope",
    )

except Exception as exc:
    raise SystemExit(f"Could not restore source archive: {exc}") from exc

print(f"Restored {len(members)} project entries from {source_label}.")

# Reassemble and verify the compressed visual/audio/gameplay generator.
enhancement_dir = ROOT / ".source" / "enhance"
enhancement_parts = sorted(enhancement_dir.glob("part-*.b64"))
if enhancement_parts:
    expected_parts = [f"part-{i:03d}.b64" for i in range(1, 8)]
    present = {part.name for part in enhancement_parts}
    missing = [name for name in expected_parts if name not in present]
    if missing:
        raise SystemExit("Enhancement generator incomplete. Missing: " + ", ".join(missing))
    packed_text = "".join((enhancement_dir / name).read_text(encoding="ascii").strip() for name in expected_parts)
    helper_bytes = gzip.decompress(base64.b64decode(packed_text, validate=True))
    helper_sha256 = hashlib.sha256(helper_bytes).hexdigest()
    if len(helper_bytes) != 101130 or helper_sha256 != "3900b793d6b5cd9ac6be277af118521035b567902d1beb4edd6fd80003b0fc13":
        raise SystemExit("Enhancement generator checksum mismatch.")
    helper_text = helper_bytes.decode("utf-8")
    # GDScript uses % for integer remainder; // is not a GDScript operator.
    helper_text = helper_text.replace("if (x//48)%2==0", "if (int(x / 48.0) % 2) == 0")
    (ROOT / "enhance_project.py").write_text(helper_text, encoding="utf-8")
    print(f"Restored visual/audio generator: {len(helper_bytes)} bytes; SHA-256 verified.")
    print("Applied GDScript platform-renderer syntax fix.")

