#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download remote assets from YCode backup into assets/ folder."""

import gzip
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

BACKUP = Path(__file__).parent / "backup-01-2026-05-24-22-52-57.ycode"
ASSETS_DIR = Path(__file__).parent / "assets"
MANIFEST = Path(__file__).parent / "assets-manifest.json"

MIME_EXT = {
    "image/webp": ".webp",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
}


def safe_name(filename: str) -> str:
    base = re.sub(r"[^\w.\-]+", "-", filename or "asset").strip("-")
    return base[:80] or "asset"


def local_filename(asset: dict) -> str:
    name = safe_name(asset.get("filename") or "asset")
    if "." not in name:
        ext = MIME_EXT.get(asset.get("mime_type", ""), "")
        name += ext
    prefix = asset["id"][:8]
    return f"{prefix}_{name}"


def download():
    with gzip.open(BACKUP, "rt", encoding="utf-8") as f:
        data = json.load(f)["data"]

    ASSETS_DIR.mkdir(exist_ok=True)
    manifest = {"by_id": {}, "by_url": {}, "files": {}}

    # Dedupe by URL — prefer published asset metadata
    by_url = {}
    for asset in data["assets"]:
        url = asset.get("public_url")
        if not url:
            continue
        existing = by_url.get(url)
        if not existing or asset.get("is_published") in (True, "true", "True"):
            by_url[url] = asset

    ok, fail = 0, 0
    for url, asset in sorted(by_url.items(), key=lambda x: x[1].get("filename", "")):
        fname = local_filename(asset)
        dest = ASSETS_DIR / fname
        rel = f"assets/{fname}"

        if dest.exists() and dest.stat().st_size > 0:
            print(f"  skip (exists) {fname}")
            ok += 1
        else:
            print(f"  download {fname} ...", end=" ", flush=True)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Dois-asset-downloader/1.0"})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    dest.write_bytes(resp.read())
                print(f"OK ({dest.stat().st_size // 1024} KB)")
                ok += 1
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                print(f"FAIL: {e}")
                fail += 1
                continue

        manifest["by_url"][url] = rel
        manifest["by_id"][asset["id"]] = rel
        manifest["files"][fname] = {"url": url, "id": asset["id"], "mime": asset.get("mime_type")}

        # bgImageVars often embed full url(...) — map those too
        url_in_css = f"url({url})"
        manifest["by_url"][url_in_css] = f"url({rel})"

    # Save embedded SVGs as files too (optional, for consistency)
    svg_count = 0
    for asset in data["assets"]:
        content = (asset.get("content") or "").strip()
        if not content or not content.startswith("<svg"):
            continue
        fname = local_filename(asset).rsplit(".", 1)[0] + ".svg"
        dest = ASSETS_DIR / fname
        rel = f"assets/{fname}"
        if not dest.exists():
            dest.write_text(content, encoding="utf-8")
        manifest["by_id"][asset["id"]] = rel
        svg_count += 1

    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nDone: {ok} downloaded/skipped, {fail} failed, {svg_count} SVGs saved")
    print(f"Manifest: {MANIFEST}")


if __name__ == "__main__":
    download()
