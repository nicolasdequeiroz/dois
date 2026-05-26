#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rename assets/ files based on where they are used in the YCode backup.
Updates assets-manifest.json and regenerates HTML via export_ycode.py.
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

MIME_EXT = {
    "image/webp": ".webp",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
}


def sanitize(text: str, max_len: int = 48) -> str:
    s = re.sub(r"[^\w\-]+", "-", str(text or "").strip().lower())
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:max_len] or "asset"


def slug_of_page(page: dict) -> str:
    s = page.get("slug", "")
    if s in ("", None):
        return "home"
    if s == "*":
        return "case"
    return sanitize(page.get("name") or s, 24)


def load_backup():
    with gzip.open(BACKUP, "rt", encoding="utf-8") as f:
        return json.load(f)["data"]


def build_usage(data: dict) -> dict[str, list[dict]]:
    pages = {p["id"]: p for p in data["pages"]}
    comps = {c["id"]: c for c in data["components"]}
    folders = {f["id"]: f.get("name", "folder") for f in data.get("asset_folders", [])}
    assets_by_id = {a["id"]: a for a in data["assets"]}
    url_to_id = {a["public_url"]: a["id"] for a in data["assets"] if a.get("public_url")}

    usage: dict[str, list[dict]] = defaultdict(list)

    def register(aid: str, page_slug: str, path: str, label: str, slot: str, component: str | None = None):
        if not aid:
            return
        usage[aid].append(
            {
                "page": page_slug,
                "path": path,
                "label": label,
                "slot": slot,
                "component": component,
            }
        )

    def walk(layers: list, page_slug: str, parents: list[str], component: str | None = None):
        for node in layers:
            label_raw = (
                node.get("customName")
                or (node.get("attributes") or {}).get("id")
                or node.get("name")
            )
            labels = parents + [sanitize(label_raw)]
            path = "/".join(labels[-4:])

            if node.get("componentId") and comps.get(node["componentId"]):
                cname = comps[node["componentId"]].get("name", "component")
                walk(
                    comps[node["componentId"]].get("layers", []),
                    page_slug,
                    labels,
                    sanitize(cname),
                )

            label = labels[-1]
            vars_ = node.get("variables") or {}

            for slot in ("image", "video", "audio", "icon"):
                src = (vars_.get(slot) or {}).get("src")
                if isinstance(src, dict) and src.get("type") == "asset":
                    register(src["data"].get("asset_id"), page_slug, path, label, slot, component)

            bg = (vars_.get("backgroundImage") or {}).get("src")
            if isinstance(bg, dict) and bg.get("type") == "asset":
                register(bg["data"].get("asset_id"), page_slug, path, label, "background", component)

            bg_vars = (node.get("design") or {}).get("backgrounds", {}).get("bgImageVars") or {}
            for val in bg_vars.values():
                m = re.search(r"url\((https?://[^)]+)\)", val)
                if m and m.group(1) in url_to_id:
                    register(url_to_id[m.group(1)], page_slug, path, label, "background", component)

            walk(node.get("children") or [], page_slug, labels, component)

    for pl in data["page_layers"]:
        if pl.get("is_published") not in (True, "true", "True"):
            continue
        page = pages.get(pl["page_id"], {})
        walk(pl.get("layers", []), slug_of_page(page), [])

    for comp in data["components"]:
        if comp.get("is_published") not in (True, "true", "True"):
            continue
        walk(comp.get("layers", []), "component", [], sanitize(comp.get("name")))

    # CMS image fields (use item slug when available)
    fields = {f["id"]: f for f in data.get("collection_fields", [])}
    slug_fields = {
        f["id"]
        for f in data.get("collection_fields", [])
        if sanitize(f.get("name")) == "slug"
    }
    item_slugs = {}
    for v in data.get("collection_item_values", []):
        if v.get("field_id") in slug_fields:
            item_slugs[v["item_id"]] = sanitize(v.get("value"))

    for v in data.get("collection_item_values", []):
        val = v.get("value")
        aid = None
        if isinstance(val, str) and val in assets_by_id:
            aid = val
        elif isinstance(val, dict):
            aid = val.get("asset_id")
        if not aid:
            continue
        item = next((i for i in data["collection_items"] if i["id"] == v["item_id"]), {})
        col = next((c for c in data["collections"] if c["id"] == item.get("collection_id")), {})
        field = fields.get(v["field_id"], {})
        col_slug = sanitize(col.get("name", "cms"))
        item_slug = item_slugs.get(v["item_id"]) or sanitize(item.get("id", "")[:8])
        register(
            aid,
            col_slug,
            f"{item_slug}/{sanitize(field.get('name', 'field'))}",
            sanitize(field.get("name", "field")),
            "cms",
        )

    return usage, assets_by_id, folders


def pick_primary_use(uses: list[dict]) -> dict:
    """Pick the most representative usage for naming."""
    comp_pages: dict[str, set[str]] = defaultdict(set)
    for u in uses:
        if u.get("component"):
            comp_pages[u["component"]].add(u["page"])

    for comp, pgs in comp_pages.items():
        if len(pgs) > 1:
            preferred = [u for u in uses if u.get("component") == comp]
            # logo in navigation beats footer
            for u in preferred:
                if "logo" in u.get("path", "").lower():
                    return {**u, "_shared": True, "_comp": comp}
            return {**preferred[0], "_shared": True, "_comp": comp}

    # prefer explicit ids / custom labels
    for u in uses:
        if u.get("label") not in ("image", "icon", "layer", "div", "text"):
            return u
    for u in uses:
        if "logo" in u.get("path", "").lower() or "hero" in u.get("label", "").lower():
            return u
    return max(uses, key=lambda u: len(u.get("path", "")))


def short_library_name(asset: dict, folders: dict) -> str:
    folder = sanitize(folders.get(asset.get("asset_folder_id"), "library"))
    raw = asset.get("filename") or "asset"
    # shorten instagram / long imports
    if raw.lower().startswith("snapinsta"):
        for token in ("yarden", "trifold", "showreel", "meeting"):
            if token in raw.lower():
                return f"{folder}--{token}-video"[:80]
        return f"{folder}--imported-video"[:80]
    orig = sanitize(raw, 36)
    return f"{folder}--{orig}"[:80]


def choose_base_name(aid: str, uses: list[dict], asset: dict, folders: dict) -> str:
    if not uses:
        return short_library_name(asset, folders)

    use = pick_primary_use(uses)
    pages = {u["page"] for u in uses}

    if use.get("_shared"):
        prefix = "shared"
        parts = [prefix, sanitize(use["_comp"])]
        label = sanitize(use["label"], 24)
        if label not in ("image", "icon", "layer") and label not in parts:
            parts.append(label)
        elif "logo" in use.get("path", "").lower():
            parts.append("logo")
    elif len(pages) == 1:
        parts = [next(iter(pages))]
        path_part = sanitize(use["path"].replace("/", "--"), 55)
        label = sanitize(use["label"], 24)
        if path_part:
            parts.append(path_part)
        elif label not in ("image", "icon"):
            parts.append(label)
    else:
        for p in ("home", "case", "cases", "metodologia", "contato", "blog"):
            if p in pages:
                parts = [p]
                break
        else:
            parts = [sorted(pages)[0]]
        path_part = sanitize(use["path"].replace("/", "--"), 50)
        if path_part:
            parts.append(path_part)

    slot = sanitize(use.get("slot", ""), 10)
    if slot and slot not in ("image", "cms", "bg", "background") and parts[-1] != slot:
        parts.append(slot)

    name = "--".join(p for p in parts if p)
    return name[:80]


def main():
    data = load_backup()
    usage, assets_by_id, folders = build_usage(data)

    if not MANIFEST.exists():
        print("Run download_assets.py first.", file=sys.stderr)
        sys.exit(1)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    id_to_old: dict[str, str] = manifest.get("by_id", {})
    old_files = {Path(v).name: (aid, v) for aid, v in id_to_old.items()}

    # Map disk files -> asset id
    file_to_id: dict[str, str] = {}
    for aid, rel in id_to_old.items():
        file_to_id[Path(rel).name] = aid
    for fname in ASSETS_DIR.iterdir():
        if fname.name not in file_to_id:
            # try prefix match id
            prefix = fname.name.split("_")[0]
            for aid in assets_by_id:
                if aid.startswith(prefix):
                    file_to_id[fname.name] = aid
                    break

    used_names: dict[str, int] = {}
    id_to_new: dict[str, str] = {}
    renames: list[tuple[Path, Path]] = []

    for fname in sorted(ASSETS_DIR.iterdir()):
        if not fname.is_file():
            continue
        aid = file_to_id.get(fname.name)
        asset = assets_by_id.get(aid, {}) if aid else {}
        uses = usage.get(aid, []) if aid else []

        ext = MIME_EXT.get(asset.get("mime_type"), fname.suffix) or ".bin"
        base = choose_base_name(aid or fname.stem, uses, asset, folders)
        new_name = f"{base}{ext}"

        if new_name in used_names:
            used_names[new_name] += 1
            new_name = f"{base}-{used_names[new_name]}{ext}"
        else:
            used_names[new_name] = 1

        new_path = ASSETS_DIR / new_name
        if fname.resolve() != new_path.resolve():
            renames.append((fname, new_path))
        if aid:
            id_to_new[aid] = f"assets/{new_name}"

    # Apply renames (two-phase to avoid collisions)
    for old, new in renames:
        temp = old.with_suffix(old.suffix + ".renaming")
        old.rename(temp)
    for old, new in renames:
        temp = old.with_suffix(old.suffix + ".renaming")
        temp.rename(new)
        print(f"  {old.name} -> {new.name}")

    # Rebuild manifest
    new_manifest = {"by_id": {}, "by_url": {}, "files": {}}
    for aid, rel in id_to_new.items():
        new_manifest["by_id"][aid] = rel
        asset = assets_by_id.get(aid, {})
        url = asset.get("public_url")
        if url:
            new_manifest["by_url"][url] = rel
            new_manifest["by_url"][f"url({url})"] = f"url({rel})"
        new_manifest["files"][Path(rel).name] = {
            "id": aid,
            "url": url,
            "mime": asset.get("mime_type"),
            "usages": len(usage.get(aid, [])),
        }

    MANIFEST.write_text(json.dumps(new_manifest, indent=2), encoding="utf-8")
    print(f"\nRenamed {len(renames)} files. Manifest updated.")

    print("Regenerating HTML...")
    subprocess.run([sys.executable, str(ROOT / "export_ycode.py")], check=True)


if __name__ == "__main__":
    main()
