#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 2: externalize CSS/JS, slim blog/404, fix export corruption."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SHARED = ROOT / "assets" / "shared"

MAIN_PAGES = [
    "index.html",
    "cases.html",
    "metodologia.html",
    "contato.html",
    "cases/trifold.html",
    "cases/yarden.html",
]

CORRUPT_CLASS = re.compile(
    r'\s*rounded-&lt;svg[^"]*"',
    re.IGNORECASE,
)


def extract_style_blocks(html: str) -> list[str]:
    return re.findall(r"<style>(.*?)</style>", html, re.DOTALL)


def replace_style_blocks(html: str, links: str) -> str:
    """Remove all inline styles; inject link tags before </head>."""
    html = re.sub(r"\s*<style>.*?</style>", "", html, flags=re.DOTALL)
    if links.strip() and "</head>" in html:
        html = html.replace("</head>", links + "\n</head>", 1)
    return html


def prefix_for(rel: str) -> str:
    return "../" if rel.startswith("cases/") else ""


def asset_href(rel: str, file: str) -> str:
    return f'{prefix_for(rel)}assets/shared/{file}'


def build_stylesheet_links(rel: str, *, index_extra: bool = False, case_extra: bool = False) -> str:
    p = prefix_for(rel)
    lines = [
        f'  <link rel="stylesheet" href="{p}assets/shared/fonts.css" />',
        f'  <link rel="stylesheet" href="{p}assets/shared/tailwind.css" />',
        f'  <link rel="stylesheet" href="{p}assets/shared/base.css" />',
    ]
    if case_extra:
        lines.append(f'  <link rel="stylesheet" href="{p}assets/shared/case-extra.css" />')
        lines.append(f'  <link rel="stylesheet" href="{p}assets/shared/case-anim.css" />')
    if index_extra:
        lines.append(f'  <link rel="stylesheet" href="{p}assets/shared/index-extra.css" />')
    return "\n".join(lines) + "\n"


def extract_scripts(html: str, start_marker: str, end_marker: str = "</script>") -> str | None:
    idx = html.find(start_marker)
    if idx == -1:
        return None
    start = html.rfind("<script>", 0, idx)
    if start == -1:
        start = idx
    end = html.find(end_marker, idx) + len(end_marker)
    return html[start:end]


def strip_inline_script(html: str, marker: str) -> str:
    """Remove one inline <script> block that contains marker."""
    idx = html.find(marker)
    if idx == -1:
        return html
    start = html.rfind("<script>", 0, idx)
    if start == -1:
        return html
    end = html.find("</script>", idx) + len("</script>")
    return html[:start] + html[end:]


def fix_corruption(html: str) -> str:
    html = CORRUPT_CLASS.sub(' rounded-[8px]"', html)
    # Stray closing tag after WhatsApp (index)
    html = html.replace(
        'alt="Image description" />\n    </a>\n  </a>\n  <script src="assets/shared/slider.js"',
        'alt="Image description" />\n    </a>\n  <script src="assets/shared/slider.js"',
    )
    html = html.replace(
        'alt="Image description" />\n    </a>\n  </a>\n  <script src="../assets/shared/slider.js"',
        'alt="Image description" />\n    </a>\n  <script src="../assets/shared/slider.js"',
    )
    # Hero CTA closed with </div> instead of </a> (metodologia section on index)
    html = html.replace(
        'src="assets/home/hero-text-bttn-arrow-block-image.svg" alt="" />\n            </div>\n          </div>\n        </div>\n      </div>\n      <img class="w-full h-full',
        'src="assets/home/hero-text-bttn-arrow-block-image.svg" alt="" />\n            </div>\n          </a>\n        </div>\n      </div>\n      <img class="w-full h-full',
    )
    return html


def inject_shared_scripts(html: str, rel: str, *, hero: bool = False) -> str:
    p = prefix_for(rel)
    tags = [
        f'  <script src="https://unpkg.com/lenis@1.1.20/dist/lenis.min.js"></script>',
        f'  <script src="{p}assets/shared/lenis-init.js"></script>',
        f'  <script src="{p}assets/shared/mobile-menu.js"></script>',
    ]
    if hero:
        tags.append(f'  <script src="{p}assets/shared/hero-intro.js"></script>')
    block = "\n".join(tags) + "\n"

    if "lenis-init.js" in html:
        return html
    if "</body>" in html:
        return html.replace("</body>", block + "</body>", 1)
    return html + block


def dedupe_scripts(html: str, *, hero: bool = False) -> str:
    """Remove inline copies after external JS files exist."""
    if (SHARED / "lenis-init.js").exists():
        html = strip_inline_script(html, "initLenisGlobal")
    if (SHARED / "mobile-menu.js").exists():
        html = strip_inline_script(html, "initMobileMenu")
    if hero and (SHARED / "hero-intro.js").exists():
        html = strip_inline_script(html, "runIntroAnimation")
    # Remove duplicate lenis CDN if inject added it at bottom
    if html.count("lenis@1.1.20") > 1:
        first = html.find('unpkg.com/lenis@1.1.20')
        second = html.find('unpkg.com/lenis@1.1.20', first + 1)
        if second != -1:
            line_start = html.rfind("<script", 0, second)
            line_end = html.find("</script>", second) + len("</script>")
            html = html[:line_start] + html[line_end:]
    return html


def remove_duplicate_lenis_script(html: str) -> str:
    """Remove inline Lenis init if present."""
    return strip_inline_script(html, "function initLenisGlobal")


def remove_duplicate_menu_script(html: str) -> str:
    return strip_inline_script(html, "function initMobileMenu")


def remove_duplicate_hero_script(html: str) -> str:
    return strip_inline_script(html, "function runIntroAnimation")


def write_shared_assets() -> None:
    SHARED.mkdir(parents=True, exist_ok=True)
    index_html = (ROOT / "index.html").read_text(encoding="utf-8")
    case_html = (ROOT / "cases/trifold.html").read_text(encoding="utf-8")
    blocks_i = extract_style_blocks(index_html)
    blocks_c = extract_style_blocks(case_html)

    fonts = blocks_i[0]
    fonts = re.sub(r"url\(['\"]fonts/", "url('/fonts/", fonts)
    fonts = re.sub(r"url\(['\"]\.\./fonts/", "url('/fonts/", fonts)
    (SHARED / "fonts.css").write_text(fonts.strip() + "\n", encoding="utf-8")

    (SHARED / "tailwind.css").write_text(blocks_i[1].strip() + "\n", encoding="utf-8")

    # base + lenis (index block index 3 in 0-based from 9 blocks - the one with html.lenis)
    base_idx = next(i for i, b in enumerate(blocks_i) if "html.lenis" in b or "OBRIGATÓRIO" in b)
    (SHARED / "base.css").write_text(blocks_i[base_idx].strip() + "\n", encoding="utf-8")

    index_extra_parts = []
    for i, b in enumerate(blocks_i):
        if i <= 2 or i == base_idx:
            continue
        if "tailwindcss" in b[:200]:
            continue
        index_extra_parts.append(b.strip())
    (SHARED / "index-extra.css").write_text(
        "\n\n".join(index_extra_parts) + "\n", encoding="utf-8"
    )

    (SHARED / "case-extra.css").write_text(blocks_c[2].strip() + "\n", encoding="utf-8")
    case_anim = "\n\n".join(blocks_c[4:6])
    (SHARED / "case-anim.css").write_text(case_anim.strip() + "\n", encoding="utf-8")

    (SHARED / "minimal.css").write_text(
        """/* Páginas leves (blog, 404) */
body {
  margin: 0;
  min-height: 100vh;
  background: #0a0a0a;
  color: #ffffff;
  font-family: 'DM Sans 9pt Regular', ui-sans-serif, sans-serif;
}
.site-header {
  padding: 16px 32px;
  display: flex;
  justify-content: center;
}
.site-header img { width: 100px; height: auto; }
.page-main {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120px 32px;
  text-align: center;
}
.page-main h1 {
  font-family: 'STIX Two Text', serif;
  font-size: clamp(32px, 6vw, 48px);
  font-weight: 400;
  margin: 0 0 16px;
}
.page-main p {
  font-size: 18px;
  opacity: 0.6;
  max-width: 480px;
  margin: 0 0 32px;
  line-height: 1.5;
}
.page-main a {
  color: #ffffff;
  opacity: 0.8;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 12px;
}
.page-main a:hover { opacity: 1; }
""",
        encoding="utf-8",
    )

    # JS extraction
    lenis_m = re.search(
        r"<script>\s*\(function\(\)\s*\{\s*function initLenisGlobal\(\).*?\}\)\(\);\s*</script>",
        index_html,
        re.DOTALL,
    )
    if lenis_m:
        body = lenis_m.group(0)
        body = body.replace("<script>", "").replace("</script>", "").strip()
        (SHARED / "lenis-init.js").write_text(body + "\n", encoding="utf-8")

    menu_m = re.search(
        r"<script>\s*\(function\(\)\s*\{\s*function initMobileMenu\(\).*?\}\)\(\);\s*</script>",
        index_html,
        re.DOTALL,
    )
    if menu_m:
        body = menu_m.group(0).replace("<script>", "").replace("</script>", "").strip()
        (SHARED / "mobile-menu.js").write_text(body + "\n", encoding="utf-8")

    hero_m = re.search(
        r"<script>\s*// =+\s*\n// 1\. SCRIPT DE ANIMAÇÃO GSAP.*?runIntroAnimation.*?</script>",
        index_html,
        re.DOTALL,
    )
    if hero_m:
        body = hero_m.group(0).replace("<script>", "").replace("</script>", "").strip()
        (SHARED / "hero-intro.js").write_text(body + "\n", encoding="utf-8")

    print("Wrote shared CSS/JS to assets/shared/")


def optimize_main_page(rel: str) -> None:
    path = ROOT / rel
    html = path.read_text(encoding="utf-8")
    is_index = rel == "index.html"
    is_case = rel.startswith("cases/")

    links = build_stylesheet_links(
        rel, index_extra=is_index, case_extra=is_case
    )
    html = replace_style_blocks(html, links)
    html = fix_corruption(html)
    html = inject_shared_scripts(html, rel, hero=is_index)
    html = dedupe_scripts(html, hero=is_index)

    # GSAP: main pages need gsap; cases need scrolltrigger
    if is_case and "ScrollTrigger.min.js" not in html:
        pass  # already in head

    path.write_text(html, encoding="utf-8")
    print(f"optimized {rel}")


def write_light_page(name: str, title: str, description: str, canonical_path: str, body_inner: str) -> None:
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <link rel="stylesheet" href="/assets/shared/fonts.css" />
  <link rel="stylesheet" href="/assets/shared/minimal.css" />
  <link rel="canonical" href="https://doisintelligence.com.br/{canonical_path}" />
  <link rel="icon" href="/assets/library/dois-black-1.svg" type="image/svg+xml" />
</head>
<body>
  <header class="site-header">
    <a href="/index.html"><img src="/assets/shared/navigation--logo.svg" alt="Dois Intelligence" /></a>
  </header>
  <main class="page-main">
{body_inner}
  </main>
</body>
</html>
"""
    (ROOT / name).write_text(html, encoding="utf-8")
    print(f"wrote light page {name}")


def main() -> None:
    write_shared_assets()
    for rel in MAIN_PAGES:
        optimize_main_page(rel)

    write_light_page(
        "blog.html",
        "Blog — Dois Intelligence",
        "Em breve: conteúdos sobre branding imobiliário da Dois Intelligence.",
        "blog.html",
        """    <h1>Blog</h1>
    <p>Em breve publicaremos conteúdos sobre branding imobiliário.</p>
    <a href="/index.html">Voltar ao início</a>""",
    )
    write_light_page(
        "404.html",
        "Página não encontrada — Dois Intelligence",
        "A página que você procura não existe.",
        "404.html",
        """    <h1>404</h1>
    <p>Esta página não existe ou foi movida.</p>
    <a href="/index.html">Ir para a home</a>""",
    )

    for rel in MAIN_PAGES:
        lines = len((ROOT / rel).read_text(encoding="utf-8").splitlines())
        kb = (ROOT / rel).stat().st_size // 1024
        print(f"  {rel}: {lines} lines, {kb} KB")


if __name__ == "__main__":
    main()
