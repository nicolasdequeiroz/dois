#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download fonts from YCode backup and Google Fonts (Inter)."""

import gzip
import json
import re
import urllib.request
from pathlib import Path

BACKUP = Path(__file__).parent / "backup-01-2026-05-24-22-52-57.ycode"
FONTS_DIR = Path(__file__).parent / "fonts"
MANIFEST = Path(__file__).parent / "fonts-manifest.json"

INTER_CSS = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def safe_filename(family: str, url: str) -> str:
    ext = ".woff2" if ".woff2" in url else ".ttf" if ".ttf" in url else ".woff"
    slug = re.sub(r"[^\w\-]+", "-", family.lower()).strip("-")
    return f"{slug}{ext}"


def download_url(url: str, dest: Path) -> bool:
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

    # Each @font-face block with url and font-weight
    blocks = re.findall(
        r"@font-face\s*\{([^}]+)\}",
        css,
        re.DOTALL,
    )
    inter_faces = []
    for block in blocks:
        weight = re.search(r"font-weight:\s*(\d+)", block)
        url_m = re.search(r"url\((https://[^)]+)\)", block)
        if not url_m:
            continue
        url = url_m.group(1)
        w = weight.group(1) if weight else "400"
        fname = f"inter-{w}.woff2"
        dest = FONTS_DIR / fname
        if download_url(url, dest):
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
    with gzip.open(BACKUP, "rt", encoding="utf-8") as f:
        fonts = json.load(f)["data"]["fonts"]

    FONTS_DIR.mkdir(exist_ok=True)
    manifest = {"faces": []}
    seen_families = set()

    for font in fonts:
        family = font.get("family") or font.get("name")
        url = font.get("url")
        if not family or not url or family in seen_families:
            continue
        seen_families.add(family)

        fname = safe_filename(family, url)
        dest = FONTS_DIR / fname
        fmt = "woff2" if fname.endswith(".woff2") else "truetype"

        print(family)
        if dest.exists() and dest.stat().st_size > 0:
            print(f"  skip (exists) {fname}")
        else:
            download_url(url, dest)

        manifest["faces"].append(
            {
                "family": family,
                "file": f"fonts/{fname}",
                "format": fmt,
                "url": url,
            }
        )

    download_inter(manifest)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest: {MANIFEST}")


if __name__ == "__main__":
    main()
