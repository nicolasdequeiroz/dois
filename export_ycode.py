#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export all pages from a YCode .ycode backup to static HTML files."""

from __future__ import annotations

import base64
import gzip
import html
import json
import re
from copy import deepcopy
from pathlib import Path

BACKUP = Path(__file__).parent / "backup-01-2026-05-24-22-52-57.ycode"
OUT_DIR = Path(__file__).parent
MANIFEST_PATH = OUT_DIR / "assets-manifest.json"
FONTS_MANIFEST_PATH = OUT_DIR / "fonts-manifest.json"
_local_manifest: dict | None = None
_fonts_manifest: dict | None = None
USE_LOCAL_ASSETS = True

SELF_CLOSING = {"img", "hr", "input", "br", "meta", "link", "source", "track", "area", "col", "embed", "wbr"}

LAYER_NAME_TO_TAG = {
    "text": "p",
    "heading": "h2",
    "richText": "div",
    "span": "span",
    "label": "label",
    "image": "img",
    "icon": "span",
    "video": "video",
    "audio": "audio",
    "body": "div",
}


def load_backup():
    with gzip.open(BACKUP, "rt", encoding="utf-8") as f:
        return json.load(f)


def setting(data, key, default=""):
    for s in data.get("settings", []):
        if s.get("key") == key:
            return s.get("value", default)
    return default


def slug_to_path(slug: str, name: str, is_index: bool = False) -> Path:
    if is_index or slug in ("", None):
        return OUT_DIR / "index.html"
    if slug == "*":
        return OUT_DIR / "_case-template.html"
    safe = re.sub(r"[^\w\-]", "-", str(slug)).strip("-") or "page"
    return OUT_DIR / f"{safe}.html"


def build_assets_map(assets):
    m = {}
    for a in assets:
        if a.get("is_published") in (True, "true", "True"):
            m[a["id"]] = a
        elif a["id"] not in m:
            m[a["id"]] = a
    return m


def load_manifest() -> dict:
    global _local_manifest
    if _local_manifest is None:
        if MANIFEST_PATH.exists():
            _local_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        else:
            _local_manifest = {"by_id": {}, "by_url": {}}
    return _local_manifest


def local_asset_path(asset_id: str | None, from_file: Path | None) -> str | None:
    if not USE_LOCAL_ASSETS or not asset_id:
        return None
    rel = load_manifest().get("by_id", {}).get(asset_id)
    if not rel:
        return None
    return rel_href(rel, from_file) if from_file else rel


def localize_css_value(value: str, from_file: Path) -> str:
    if not USE_LOCAL_ASSETS:
        return value
    manifest = load_manifest()
    if value in manifest.get("by_url", {}):
        mapped = manifest["by_url"][value]
        if mapped.startswith("url("):
            inner = mapped[4:-1]
            return f"url({rel_href(inner, from_file)})"
        return mapped
    return value


def resolve_asset_url(asset, from_file: Path | None = None) -> str:
    if not asset:
        return ""
    aid = asset.get("id")
    local = local_asset_path(aid, from_file)
    if local:
        return local

    content = asset.get("content") or ""
    if content:
        if content.startswith("data:"):
            return content
        if content.strip().startswith("<"):
            encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
            return f"data:image/svg+xml;base64,{encoded}"

    url = asset.get("public_url")
    if url and USE_LOCAL_ASSETS:
        rel = load_manifest().get("by_url", {}).get(url)
        if rel:
            return rel_href(rel, from_file) if from_file else rel
    if url:
        return url
    return ""


def build_field_values(data):
    fields_by_id = {f["id"]: f for f in data.get("collection_fields", [])}
    item_vals = {}
    for v in data.get("collection_item_values", []):
        iid = v.get("item_id")
        fid = v.get("field_id")
        item_vals.setdefault(iid, {})[fid] = v.get("value")
    items_by_col = {}
    for item in data.get("collection_items", []):
        cid = item.get("collection_id")
        items_by_col.setdefault(cid, [])
        if not any(x["id"] == item["id"] for x in items_by_col[cid]):
            items_by_col[cid].append(item)
    return fields_by_id, item_vals, items_by_col


def get_variable_content(var):
    if not var or "data" not in var:
        return ""
    data = var["data"]
    if isinstance(data, dict):
        return data.get("content", "") or ""
    return str(data)


def resolve_src(var, assets_map, from_file: Path, field_ctx=None):
    if not var:
        return ""
    if var.get("type") == "asset":
        aid = var.get("data", {}).get("asset_id")
        return resolve_asset_url(assets_map.get(aid), from_file) if aid else ""
    if var.get("type") == "field" and field_ctx is not None:
        fid = var.get("data", {}).get("field_id")
        val = field_ctx.get(fid, "")
        if isinstance(val, str) and val in assets_map:
            return resolve_asset_url(assets_map[val], from_file)
        if isinstance(val, dict):
            aid = val.get("asset_id")
            if aid:
                return resolve_asset_url(assets_map.get(aid), from_file)
        return str(val) if val else ""
    if var.get("type") in ("dynamic_text", "static_text"):
        return get_variable_content(var)
    return get_variable_content(var)


def get_classes(layer):
    c = layer.get("classes") or ""
    if isinstance(c, list):
        return " ".join(str(x) for x in c).strip()
    return str(c).strip()


def get_layer_tag(layer):
    if layer.get("id") == "body" or layer.get("name") == "body":
        return "div"
    if layer.get("settings", {}).get("tag"):
        return layer["settings"]["tag"]
    return LAYER_NAME_TO_TAG.get(layer.get("name"), layer.get("name") or "div")


def tiptap_to_html(doc):
    if not doc or not isinstance(doc, dict):
        return ""
    parts = []
    for block in doc.get("content") or []:
        inline = []
        for node in block.get("content") or []:
            if node.get("type") == "text":
                text = html.escape(node.get("text", ""))
                for mark in node.get("marks") or []:
                    if mark.get("type") == "bold":
                        text = f"<strong>{text}</strong>"
                    elif mark.get("type") == "italic":
                        text = f"<em>{text}</em>"
                inline.append(text)
        if inline:
            parts.append("".join(inline))
    return "<br>".join(parts) if parts else ""


def get_text_html(layer, field_ctx=None):
    text_var = (layer.get("variables") or {}).get("text")
    if not text_var:
        return None
    if text_var.get("type") == "field" and field_ctx is not None:
        fid = text_var.get("data", {}).get("field_id")
        val = field_ctx.get(fid, "")
        if isinstance(val, dict) and val.get("type") == "doc":
            return tiptap_to_html(val) or None
        return html.escape(str(val)) if val else None
    if text_var.get("type") == "dynamic_text":
        content = get_variable_content(text_var)
        return html.escape(content) if content else None
    if text_var.get("type") == "dynamic_rich_text":
        doc = (text_var.get("data") or {}).get("content")
        return tiptap_to_html(doc) or None
    return None


def rel_href(target: str, from_file: Path) -> str:
    """Build href relative to the exporting HTML file's directory."""
    import os

    target_path = OUT_DIR / target
    start = from_file.parent
    try:
        return os.path.relpath(str(target_path), str(start))
    except ValueError:
        return target


def build_page_href(page_id: str, page_paths: dict, from_file: Path, collection_slug: str | None = None) -> str:
    if collection_slug:
        target = f"cases/{collection_slug}.html"
    else:
        target = page_paths.get(page_id, "index.html")
    return rel_href(target, from_file)


def build_link_attrs(link, page_paths, from_file: Path, field_ctx=None):
    if not link:
        return []
    attrs = []
    ltype = link.get("type")
    if ltype == "url":
        href = get_variable_content(link.get("url"))
        if href:
            attrs.append(f'href="{html.escape(href, quote=True)}"')
    elif ltype == "page":
        page = link.get("page") or {}
        pid = page.get("id")
        if pid:
            item_slug = None
            if page.get("collection_item_id") == "current-collection" and field_ctx:
                slug_fid = field_ctx.get("_slug_field_id")
                if slug_fid:
                    item_slug = field_ctx.get(slug_fid)
            href = build_page_href(pid, page_paths, from_file, item_slug)
            attrs.append(f'href="{html.escape(href, quote=True)}"')
    if link.get("target"):
        attrs.append(f'target="{html.escape(link["target"], quote=True)}"')
    if link.get("rel"):
        attrs.append(f'rel="{html.escape(link["rel"], quote=True)}"')
    return attrs


def build_attrs(layer, tag, cls, assets_map, field_ctx, page_paths, from_file: Path):
    attrs = []
    if cls:
        attrs.append(f'class="{html.escape(cls, quote=True)}"')
    lid = (layer.get("attributes") or {}).get("id")
    if lid:
        attrs.append(f'id="{html.escape(str(lid), quote=True)}"')
    for k, v in (layer.get("attributes") or {}).items():
        if k in ("id", "style"):
            continue
        if v is not None and v is not False:
            attrs.append(k if v is True else f'{k}="{html.escape(str(v), quote=True)}"')

    vars_ = layer.get("variables") or {}

    if layer.get("name") == "image" or tag == "img":
        img = vars_.get("image", {})
        src = resolve_src(img.get("src"), assets_map, from_file, field_ctx)
        alt = resolve_src(img.get("alt"), assets_map, from_file, field_ctx) or get_variable_content(img.get("alt")) or ""
        if src:
            attrs.append(f'src="{html.escape(src, quote=True)}"')
        attrs.append(f'alt="{html.escape(str(alt), quote=True)}"')

    if layer.get("name") == "video" or tag == "video":
        src = resolve_src(vars_.get("video", {}).get("src"), assets_map, from_file, field_ctx)
        if src:
            attrs.append(f'src="{html.escape(src, quote=True)}"')

    style_parts = []
    bg_design = (layer.get("design") or {}).get("backgrounds") or {}
    bg_vars = bg_design.get("bgImageVars") or {}
    if bg_vars:
        style_parts.append(
            "; ".join(f"{k}: {localize_css_value(v, from_file)}" for k, v in bg_vars.items())
        )
    elif vars_.get("backgroundImage", {}).get("src"):
        url = resolve_src(vars_["backgroundImage"]["src"], assets_map, from_file, field_ctx)
        if url:
            style_parts.append(f"background-image:url({url})")
    if style_parts:
        attrs.append(f'style="{html.escape("; ".join(style_parts), quote=True)}"')

    link = vars_.get("link")
    link_attrs = build_link_attrs(link, page_paths, from_file, field_ctx)
    if link_attrs and tag == "a":
        attrs.extend(link_attrs)
    elif link_attrs:
        # wrap in href on div with onclick? keep as data-href for manual fix
        for a in link_attrs:
            if a.startswith("href="):
                attrs.append(a)

    return attrs


def expand_component(layer, components):
    cid = layer.get("componentId") or layer.get("component_id")
    if not cid:
        return [layer]
    comp = components.get(cid)
    if not comp or not comp.get("layers"):
        return [layer]
    out = []
    for cl in comp["layers"]:
        merged = deepcopy(cl)
        if layer.get("attributes"):
            merged.setdefault("attributes", {}).update(layer["attributes"])
        if layer.get("classes"):
            base = merged.get("classes", "")
            merged["classes"] = f"{layer['classes']} {base}".strip()
        out.append(merged)
    return out


def collection_items_for_layer(layer, items_by_col):
    coll = (layer.get("variables") or {}).get("collection")
    if not coll:
        return []
    cid = coll.get("id")
    items = list(items_by_col.get(cid, []))
    limit = coll.get("limit")
    if limit:
        items = items[: int(limit)]
    return items


def layer_to_html(layer, assets_map, components, item_vals, items_by_col, page_paths, from_file: Path, indent=0, field_ctx=None):
    pad = "  " * indent
    coll = (layer.get("variables") or {}).get("collection")
    if coll and layer.get("children"):
        items = collection_items_for_layer(layer, items_by_col)
        parts = []
        for item in items:
            ctx = dict(item_vals.get(item["id"], {}))
            # slug field for case links
            cid = coll.get("id")
            for fid, val in ctx.items():
                pass
            parts.extend(
                layer_to_html(child, assets_map, components, item_vals, items_by_col, page_paths, from_file, indent + 1, ctx)
                for child in layer.get("children", [])
            )
        tag = get_layer_tag(layer)
        cls = get_classes(layer)
        attrs = build_attrs(layer, tag, cls, assets_map, field_ctx, page_paths, from_file)
        attr_str = f" {' '.join(attrs)}" if attrs else ""
        inner = "\n".join(parts)
        return f"{pad}<{tag}{attr_str}>\n{inner}\n{pad}</{tag}>"

    if layer.get("componentId") or layer.get("component_id"):
        return "\n".join(
            layer_to_html(exp, assets_map, components, item_vals, items_by_col, page_paths, from_file, indent, field_ctx)
            for exp in expand_component(layer, components)
        )

    tag = get_layer_tag(layer)
    cls = get_classes(layer)
    attrs = build_attrs(layer, tag, cls, assets_map, field_ctx, page_paths, from_file)
    attr_str = f" {' '.join(attrs)}" if attrs else ""

    if layer.get("name") == "icon":
        icon_src = (layer.get("variables") or {}).get("icon", {}).get("src")
        if icon_src and icon_src.get("type") == "static_text":
            content = get_variable_content(icon_src)
            if content.strip().startswith("<"):
                return pad + content
        svg = resolve_src(icon_src, assets_map, from_file, field_ctx) if icon_src else ""
        if svg and not svg.strip().startswith("<") and svg.startswith("assets/"):
            return f'{pad}<span class="{html.escape(cls, quote=True)}"><img src="{html.escape(svg, quote=True)}" alt="" /></span>'
        if svg and svg.strip().startswith("<"):
            return pad + svg
        if svg:
            return f'{pad}<span class="{html.escape(cls, quote=True)}"><img src="{html.escape(svg, quote=True)}" alt="" /></span>'
        return ""

    text_html = get_text_html(layer, field_ctx)

    if tag in SELF_CLOSING:
        return f"{pad}<{tag}{attr_str} />"

    children = layer.get("children") or []
    open_tag = f"{pad}<{tag}{attr_str}>"
    close_tag = f"</{tag}>"

    if text_html and not children:
        return f"{open_tag}{text_html}{close_tag}"
    if not children:
        return f"{open_tag}{close_tag}"

    child_html = "\n".join(
        layer_to_html(c, assets_map, components, item_vals, items_by_col, page_paths, from_file, indent + 1, field_ctx)
        for c in children
    )
    return f"{open_tag}\n{child_html}\n{pad}{close_tag}"


def load_fonts_manifest() -> dict:
    global _fonts_manifest
    if _fonts_manifest is None:
        if FONTS_MANIFEST_PATH.exists():
            _fonts_manifest = json.loads(FONTS_MANIFEST_PATH.read_text(encoding="utf-8"))
        else:
            _fonts_manifest = {"faces": [], "inter": []}
    return _fonts_manifest


def build_font_faces(fonts, from_file: Path):
    blocks = []
    manifest = load_fonts_manifest()

    if manifest.get("faces"):
        for face in manifest["faces"]:
            fam = face["family"]
            href = rel_href(face["file"], from_file)
            fmt = face.get("format", "woff2")
            blocks.append(
                f"@font-face {{\n  font-family: '{fam}';\n  src: url('{href}') format('{fmt}');\n  font-display: swap;\n}}"
            )
    else:
        seen = set()
        for f in fonts:
            fam = f.get("family") or f.get("name")
            url = f.get("url")
            if not fam or not url or fam in seen:
                continue
            seen.add(fam)
            ext = "truetype" if ".ttf" in url else "woff2"
            blocks.append(
                f"@font-face {{\n  font-family: '{fam}';\n  src: url('{url}') format('{ext}');\n  font-display: swap;\n}}"
            )

    for face in manifest.get("inter", []):
        fam = face["family"]
        href = rel_href(face["file"], from_file)
        weight = face.get("weight", "400")
        blocks.append(
            f"@font-face {{\n  font-family: '{fam}';\n  font-weight: {weight};\n  src: url('{href}') format('woff2');\n  font-display: swap;\n}}"
        )

    return "\n".join(blocks)


def render_page(page, page_layer, data, assets_map, components, item_vals, items_by_col, page_paths, out_path: Path, field_ctx=None):
    body_html = "\n".join(
        layer_to_html(layer, assets_map, components, item_vals, items_by_col, page_paths, out_path, 1, field_ctx)
        for layer in page_layer["layers"]
    )

    published_css = setting(data, "published_css", "")
    generated_css = page_layer.get("generated_css", "")
    font_css = build_font_faces(data.get("fonts", []), out_path)

    page_cc = page.get("settings", {}).get("custom_code", {})
    head_extra = setting(data, "custom_code_head", "")
    body_extra = setting(data, "custom_code_body", "")
    page_head = page_cc.get("head", "")
    page_body = page_cc.get("body", "")

    seo = page.get("settings", {}).get("seo", {})
    title = seo.get("title") or page.get("name") or setting(data, "site_name", "Site")
    description = seo.get("description") or setting(data, "site_description", "")

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(str(title))}</title>
  <meta name="description" content="{html.escape(str(description))}" />
  <style>
{font_css}
  </style>
  <style>
{published_css}
  </style>
  <style>
{generated_css}
  </style>
  {head_extra}
  {page_head}
</head>
<body>
{body_html}
  {body_extra}
  {page_body}
</body>
</html>
"""


def unique_pages(pages):
    seen = set()
    for p in pages:
        if p["id"] not in seen:
            seen.add(p["id"])
            yield p


def main():
    raw = load_backup()
    data = raw["data"]
    pages = list(unique_pages(data["pages"]))
    assets_map = build_assets_map(data["assets"])

    components = {}
    for c in data["components"]:
        if c.get("is_published") in (True, "true", "True"):
            components[c["id"]] = c
        elif c["id"] not in components:
            components[c["id"]] = c

    fields_by_id, item_vals, items_by_col = build_field_values(data)

    # Build path map for internal links
    page_paths = {}
    for p in pages:
        rel = slug_to_path(p.get("slug", ""), p.get("name", ""), p.get("is_index"))
        page_paths[p["id"]] = rel.name if rel.parent == OUT_DIR else str(rel.relative_to(OUT_DIR))

    layer_by_page = {}
    for pl in data["page_layers"]:
        if pl.get("is_published") not in (True, "true", "True"):
            continue
        pid = pl.get("page_id")
        if pid not in layer_by_page:
            layer_by_page[pid] = pl

    exported = []

    for page in pages:
        pl = layer_by_page.get(page["id"])
        if not pl:
            print(f"SKIP (no layers): {page['name']}")
            continue

        slug = page.get("slug", "")
        out_path = slug_to_path(slug, page.get("name", ""), page.get("is_index"))

        if slug == "*":
            # Dynamic case template: export one file per collection item
            col_id = None
            for c in data["collections"]:
                if c.get("name") == "Cases":
                    col_id = c["id"]
                    break
            slug_field_id = None
            if col_id:
                for f in data["collection_fields"]:
                    if f.get("collection_id") == col_id and (f.get("name") or "").lower() == "slug":
                        slug_field_id = f["id"]
                        break
            cases_dir = OUT_DIR / "cases"
            cases_dir.mkdir(exist_ok=True)
            items = items_by_col.get(col_id, []) if col_id else []
            seen_items = set()
            for item in items:
                if item["id"] in seen_items:
                    continue
                seen_items.add(item["id"])
                ctx = dict(item_vals.get(item["id"], {}))
                if slug_field_id:
                    ctx["_slug_field_id"] = slug_field_id
                item_slug = ctx.get(slug_field_id, item["id"][:8])
                safe_slug = re.sub(r"[^\w\-]", "-", str(item_slug)).strip("-")
                case_path = cases_dir / f"{safe_slug}.html"
                doc = render_page(page, pl, data, assets_map, components, item_vals, items_by_col, page_paths, case_path, ctx)
                case_path.write_text(doc, encoding="utf-8")
                exported.append(case_path)
                print(f"  cases/{safe_slug}.html")
            continue

        doc = render_page(page, pl, data, assets_map, components, item_vals, items_by_col, page_paths, out_path)
        out_path.write_text(doc, encoding="utf-8")
        exported.append(out_path)
        print(f"  {out_path.name}")

    print(f"\nExported {len(exported)} files to {OUT_DIR}")


if __name__ == "__main__":
    main()
