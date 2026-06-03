#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download fonts from fonts-manifest.json + Inter from Google Fonts."""

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
FONTS_DIR = ROOT / "fonts"
MANIFEST = ROOT / "fonts-manifest.json"
INTER_CSS = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def download_url(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  skip {dest.name}")
        return True
    print(f"  download {dest.name} ...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as resp:
            dest.write_bytes(resp.read())
        print(f"OK ({dest.stat().st_size // 1024} KB)")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def download_inter(manifest: dict) -> None:
    print("Inter (Google Fonts)")
    req = urllib.request.Request(INTER_CSS, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        css = resp.read().decode("utf-8")

    inter_faces = []
    for block in re.findall(r"@font-face\s*\{([^}]+)\}", css, re.DOTALL):
        weight = re.search(r"font-weight:\s*(\d+)", block)
        url_m = re.search(r"url\((https://[^)]+)\)", block)
        if not url_m:
            continue
        w = weight.group(1) if weight else "400"
        fname = f"inter-{w}.woff2"
        dest = FONTS_DIR / fname
        if download_url(url_m.group(1), dest):
            inter_faces.append(
                {
                    "family": "Inter",
                    "weight": w,
                    "file": f"fonts/{fname}",
                    "format": "woff2",
                }
            )
    manifest["inter"] = inter_faces


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    FONTS_DIR.mkdir(exist_ok=True)

    for face in manifest.get("faces", []):
        url = face.get("url")
        rel = face.get("file")
        if not url or not rel:
            continue
        print(face.get("family", rel))
        download_url(url, ROOT / rel)

    download_inter(manifest)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest updated: {MANIFEST}")


if __name__ == "__main__":
    main()
