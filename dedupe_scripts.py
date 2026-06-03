#!/usr/bin/env python3
from optimize_html import MAIN_PAGES, dedupe_scripts
from pathlib import Path

ROOT = Path(__file__).parent
for rel in MAIN_PAGES:
    p = ROOT / rel
    html = dedupe_scripts(p.read_text(encoding="utf-8"), hero=(rel == "index.html"))
    p.write_text(html, encoding="utf-8")
    print("deduped", rel)
