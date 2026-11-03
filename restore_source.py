#!/usr/bin/env python3
"""Restore the compressed Godot project stored in a base64 tar.gz archive."""
from __future__ import annotations

import base64
import io
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
full_archive = ROOT / ".source" / "source-full.b64"

if full_archive.is_file():
    encoded = full_archive.read_text(encoding="ascii").strip()
    source_label = full_archive.name
else:
    parts = sorted((ROOT / ".source").glob("part-*.b64"))
    expected = [f"part-{i:03d}.b64" for i in range(1, 38)]
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
except Exception as exc:
    raise SystemExit(f"Could not restore source archive: {exc}") from exc

print(f"Restored {len(members)} project entries from {source_label}.")
