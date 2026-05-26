#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Organize assets/ into subfolders by page usage (home, metodologia, shared, etc.).
Updates assets-manifest.json and regenerates HTML.
"""

from __future__ import annotations

import gzip
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
BACKUP = ROOT / "backup-01-2026-05-24-22-52-57.ycode"
ASSETS_DIR = ROOT / "assets"
MANIFEST = ROOT / "assets-manifest.json"

# Order matters: more specific prefixes first
FOLDER_RULES = [
    (r"^cases--trifold-", "cases/trifold"),
    (r"^cases--yarden-", "cases/yarden"),
    (r"^cases--", "cases"),
    (r"^home--", "home"),
    (r"^metodologia--", "metodologia"),
    (r"^contato--", "contato"),
    (r"^case--", "case"),
    (r"^cases\.html|^cases-", "cases"),  # fallback
    (r"^blog--", "blog"),
    (r"^401-password-required--", "401-password"),
    (r"^401-password--", "401-password"),
    (r"^401-password", "401-password"),
    (r"^404--", "404"),
    (r"^500--", "500"),
    (r"^shared--", "shared"),
    (r"^trifold--", "cases/trifold"),
    (r"^yarden--", "cases/yarden"),
    (r"^icons--", "icons"),
    (r"^mockups--", "mockups"),
    (r"^library--", "library"),
    (r"^component--", "shared"),
]


def strip_prefix(filename: str) -> tuple[str, str]:
    """Return (folder, basename) from current asset filename."""
    for pattern, folder in FOLDER_RULES:
        m = re.match(pattern, filename, re.I)
        if m:
            matched = m.group(0)
            rest = filename[len(matched) :]
            if rest.startswith("--"):
                rest = rest[2:]
            elif rest.startswith("-"):
                rest = rest[1:]
            return folder, rest or filename
    return "library", filename


def folder_from_usage(uses: list[dict]) -> str | None:
    """Derive folder from backup usage when filename has no prefix."""
    if not uses:
        return None
    pages = {u["page"] for u in uses}
    if any(u.get("_shared") or (u.get("component") and len(pages) > 1) for u in uses):
        return "shared"
    comp_pages: dict[str, set] = defaultdict(set)
    for u in uses:
        if u.get("component"):
            comp_pages[u["component"]].add(u["page"])
    for comp, pgs in comp_pages.items():
        if len(pgs) > 1:
            return "shared"
    page = uses[0]["page"]
    if page == "cases" and "trifold" in uses[0].get("path", ""):
        return "cases/trifold"
    if page in ("cases", "case"):
        for u in uses:
            if "yarden" in str(u.get("path", "")).lower():
                return "cases/yarden"
            if "trifold" in str(u.get("path", "")).lower():
                return "cases/trifold"
        return "cases"
    return page


def load_usage():
    sys.path.insert(0, str(ROOT))
    from rename_assets import build_usage, load_backup

    data = load_backup()
    usage, assets_by_id, _ = build_usage(data)
    return usage, assets_by_id


def main():
    if not ASSETS_DIR.exists():
        print("No assets/ folder.", file=sys.stderr)
        sys.exit(1)

    usage, assets_by_id = load_usage()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"by_id": {}, "by_url": {}, "files": {}}
    id_to_old_rel = manifest.get("by_id", {})

    # asset id -> current file path
    id_to_file: dict[str, Path] = {}
    for aid, rel in id_to_old_rel.items():
        p = ROOT / rel
        if p.exists():
            id_to_file[aid] = p

    # also map by filename for files not in manifest
    for f in ASSETS_DIR.rglob("*"):
        if f.is_file() and f.suffix not in (".renaming",):
            pass

    moves: list[tuple[Path, Path, str]] = []  # src, dest, asset_id
    used_dest: set[str] = set()

    # Process all files in assets root (flat) and one level? currently flat
    for src in sorted(ASSETS_DIR.iterdir()):
        if not src.is_file():
            continue

        # find asset id
        aid = None
        for a_id, rel in id_to_old_rel.items():
            if (ROOT / rel).name == src.name or rel.endswith(src.name):
                aid = a_id
                break
        if not aid:
            prefix = src.name.split("_")[0] if "_" in src.name else src.name.split("--")[0]
            for a_id in assets_by_id:
                if a_id.startswith(prefix[:8]):
                    aid = a_id
                    break

        folder, basename = strip_prefix(src.name)
        if folder == "library" and aid and usage.get(aid):
            alt = folder_from_usage(usage[aid])
            if alt:
                folder = alt

        dest_dir = ASSETS_DIR / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_name = basename
        dest = dest_dir / dest_name

        if dest.resolve() == src.resolve():
            continue

        n = 2
        while str(dest) in used_dest or (dest.exists() and dest.resolve() != src.resolve()):
            stem = Path(basename).stem
            ext = Path(basename).suffix
            dest = dest_dir / f"{stem}-{n}{ext}"
            n += 1

        used_dest.add(str(dest))
        moves.append((src, dest, aid or ""))

    # Two-phase move
    completed: list[tuple[Path, str]] = []  # dest path, asset_id
    for src, dest, aid in moves:
        tmp = src.with_suffix(src.suffix + ".moving")
        src.rename(tmp)
        tmp.rename(dest)
        rel = str(dest.relative_to(ROOT)).replace("\\", "/")
        print(f"  -> {rel}")
        completed.append((dest, aid))

    new_by_id = {}
    new_by_url = {}
    new_files = {}

    for dest, aid in completed:
        rel = str(dest.relative_to(ROOT)).replace("\\", "/")
        if aid:
            new_by_id[aid] = rel
            asset = assets_by_id.get(aid, {})
            url = asset.get("public_url")
            if url:
                new_by_url[url] = rel
                new_by_url[f"url({url})"] = f"url({rel})"
        new_files[dest.name] = {"path": rel, "id": aid or None}

    # Fill any remaining ids from old manifest
    for aid, old_rel in id_to_old_rel.items():
        if aid in new_by_id:
            continue
        old_name = Path(old_rel).name
        found = list(ASSETS_DIR.rglob(old_name))
        if found:
            rel = str(found[0].relative_to(ROOT)).replace("\\", "/")
            new_by_id[aid] = rel

    manifest_out = {"by_id": new_by_id, "by_url": new_by_url, "files": new_files}
    MANIFEST.write_text(json.dumps(manifest_out, indent=2), encoding="utf-8")
    print(f"\nOrganized {len(moves)} files. Manifest updated.")

    print("Regenerating HTML...")
    subprocess.run([sys.executable, str(ROOT / "export_ycode.py")], check=True)


if __name__ == "__main__":
    main()
