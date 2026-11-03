#!/usr/bin/env python3
"""Restore the compressed Godot project stored in .source/ base64 parts."""
from __future__ import annotations
import base64, io, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parts = sorted((ROOT / ".source").glob("part-*.b64"))
expected = [f"part-{i:03d}.b64" for i in range(1, 38)]
present = {p.name for p in parts}
missing = [name for name in expected if name not in present]
if missing:
    raise SystemExit("Source archive incomplete. Missing: " + ", ".join(missing))
encoded = "".join(p.read_text(encoding="ascii").strip() for p in parts)
try:
    data = base64.b64decode(encoded, validate=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            target = (ROOT / member.name).resolve()
            if target != ROOT and ROOT not in target.parents:
                raise SystemExit(f"Unsafe archive path: {member.name}")
        archive.extractall(ROOT, members=members)
except Exception as exc:
    raise SystemExit(f"Could not restore source archive: {exc}") from exc
print(f"Restored {len(members)} project entries from {len(parts)} parts.")
