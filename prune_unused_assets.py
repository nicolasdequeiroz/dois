#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove YCode bloat: assets not referenced in HTML and unused error pages."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
MANIFEST = ROOT / "assets-manifest.json"
HTML_GLOB = ["*.html", "cases/*.html"]

# Explicit removals from YCode audit (duplicates / export orphans)
EXTRA_REMOVE = {
    "assets/cases/trifold/trifold-old-logo.webp",
    "assets/cases/trifold/trifuca-new-logo.webp",
    "assets/cases/yarden/bag-yarden-2.png",
    "assets/cases/yarden/fachada-yarden.jpg",
    "assets/cases/yarden/gourmet.webp",
    "assets/cases/yarden/video-showreel-1.mp4",
    "assets/cases/yarden/video-showreel-2.mp4",
    "assets/cases/yarden/video-showreel-3.mp4",
}

REMOVE_DIRS = [
    ASSETS / "mockups",
    ASSETS / "icons",
    ASSETS / "401-password",
]

REMOVE_PAGES = [
    ROOT / "401-password.html",
    ROOT / "500.html",
]

KEEP_LIBRARY = {"dois-black-1.svg"}


def collect_html_asset_refs() -> set[str]:
    refs: set[str] = set()
    for pattern in HTML_GLOB:
        for path in ROOT.glob(pattern):
            text = path.read_text(encoding="utf-8")
            for m in re.finditer(
                r"(?:\.\./)?assets/[a-zA-Z0-9_\-./%çãíéóúâêôüñÇÃÍÉÓÚÂÊÔÜÑ]+",
                text,
            ):
                refs.add(m.group(0).replace("../", ""))
    return refs


def _local_path(value: str) -> str:
    return value.replace("url(", "").replace(")", "").strip()


def prune_manifest(keep_paths: set[str]) -> None:
    if not MANIFEST.exists():
        return
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for key in ("by_id", "by_url"):
        if key not in data:
            continue
        data[key] = {
            k: v
            for k, v in data[key].items()
            if _local_path(v) in keep_paths
        }
    if "files" in data:
        data["files"] = {
            k: v
            for k, v in data["files"].items()
            if f"assets/{k}" in keep_paths or k in keep_paths
        }
    MANIFEST.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    refs = collect_html_asset_refs()
    keep_paths = refs | {"assets/shared/slider.js"}

    removed_files = 0
    removed_bytes = 0

    for d in REMOVE_DIRS:
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file():
                    removed_bytes += f.stat().st_size
                    removed_files += 1
            shutil.rmtree(d)
            print(f"removed dir {d.relative_to(ROOT)}/")

    lib = ASSETS / "library"
    if lib.exists():
        for f in lib.iterdir():
            if f.is_file() and f.name not in KEEP_LIBRARY:
                removed_bytes += f.stat().st_size
                removed_files += 1
                f.unlink()
                print(f"removed {f.relative_to(ROOT)}")

    for rel in EXTRA_REMOVE:
        path = ROOT / rel
        if path.is_file():
            removed_bytes += path.stat().st_size
            removed_files += 1
            path.unlink()
            print(f"removed {rel}")

    if ASSETS.exists():
        for path in sorted(ASSETS.rglob("*")):
            if not path.is_file() or path.name == ".DS_Store":
                continue
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            if rel not in keep_paths:
                removed_bytes += path.stat().st_size
                removed_files += 1
                path.unlink()
                print(f"removed unreferenced {rel}")

    for page in REMOVE_PAGES:
        if page.exists():
            removed_bytes += page.stat().st_size
            page.unlink()
            print(f"removed page {page.name}")

    # Empty dirs
    for path in sorted(ASSETS.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
            print(f"removed empty dir {path.relative_to(ROOT)}")

    # Manifest only lists kept local paths
    manifest_keep = keep_paths.copy()
    prune_manifest(manifest_keep)

    print(f"\nDone: {removed_files} files removed ({removed_bytes / 1024 / 1024:.1f} MB)")
    print(f"Kept {len(keep_paths)} asset paths referenced in HTML")


if __name__ == "__main__":
    main()
