#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download assets listed in assets-manifest.json (by_url) without YCode backup."""

import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
MANIFEST = ROOT / "assets-manifest.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Dois-asset-downloader/1.0"


def download_url(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  skip {dest.relative_to(ROOT)}")
        return True
    print(f"  download {dest.relative_to(ROOT)} ...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as resp:
            dest.write_bytes(resp.read())
        print(f"OK ({dest.stat().st_size // 1024} KB)")
        return True
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"FAIL: {e}")
        return False


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_url = data.get("by_url", {})

    # Unique remote URL -> local path (skip url(...) wrappers and duplicates)
    jobs = {}
    for remote, local in by_url.items():
        if not remote.startswith("http"):
            continue
        if local in jobs.values():
            continue
        jobs[remote] = local

    ok, fail = 0, 0
    for url, rel in sorted(jobs.items(), key=lambda x: x[1]):
        dest = ROOT / rel
        if download_url(url, dest):
            ok += 1
        else:
            fail += 1

    print(f"\nDone: {ok} ok, {fail} failed ({len(jobs)} unique files)")


if __name__ == "__main__":
    main()
