#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply GitHub Pages fixes to exported HTML files."""

import re
from pathlib import Path

ROOT = Path(__file__).parent
DOMAIN = "https://doisintelligence.com.br"
SLIDER_SCRIPT = "assets/shared/slider.js"

# path from file -> slider script src
SLIDER_SRC = {
    "": SLIDER_SCRIPT,
    "cases/": "../" + SLIDER_SCRIPT,
}

PAGE_META = {
    "index.html": {
        "title": "Dois Intelligence — Branding imobiliário",
        "description": "Consultoria de branding e posicionamento para o mercado imobiliário. Metodologia Intelligence para construtoras e incorporadoras.",
        "path": "",
    },
    "cases.html": {
        "title": "Cases — Dois Intelligence",
        "description": "Cases de branding imobiliário: Trifold, Yarden e mais projetos da Dois Intelligence.",
        "path": "cases.html",
    },
    "metodologia.html": {
        "title": "Metodologia — Dois Intelligence",
        "description": "Conheça a Metodologia Intelligence da Dois Intelligence para posicionar seu empreendimento.",
        "path": "metodologia.html",
    },
    "contato.html": {
        "title": "Contato — Dois Intelligence",
        "description": "Fale com a Dois Intelligence. Branding e consultoria para o mercado imobiliário.",
        "path": "contato.html",
    },
    "blog.html": {
        "title": "Blog — Dois Intelligence",
        "description": "Em breve: conteúdos sobre branding imobiliário da Dois Intelligence.",
        "path": "blog.html",
    },
    "404.html": {
        "title": "Página não encontrada — Dois Intelligence",
        "description": "A página que você procura não existe.",
        "path": "404.html",
    },
    "cases/trifold.html": {
        "title": "Case Trifold — Dois Intelligence",
        "description": "Case de branding imobiliário Trifold pela Dois Intelligence.",
        "path": "cases/trifold.html",
    },
    "cases/yarden.html": {
        "title": "Case Yarden — Dois Intelligence",
        "description": "Case de branding imobiliário Yarden pela Dois Intelligence.",
        "path": "cases/yarden.html",
    },
}

SLIDER_CORRUPT_RE = re.compile(
    r' gap-&lt;script&gt;.*?&lt;/script&gt;( gap-&lt;script&gt;.*?&lt;/script&gt;)*',
    re.DOTALL,
)

HTML_FILES = [
    "index.html",
    "cases.html",
    "metodologia.html",
    "contato.html",
    "blog.html",
    "404.html",
    "cases/trifold.html",
    "cases/yarden.html",
]


def prefix_for(rel: str) -> str:
    return "../" if rel.startswith("cases/") else ""


def fix_slider(content: str, rel: str) -> str:
    if "gap-&lt;script&gt;" not in content:
        return content
    content = SLIDER_CORRUPT_RE.sub("", content)
    # Restore sensible gap on the corrupted div
    content = content.replace(
        'class="flex flex-col w-[100%]"',
        'class="flex flex-col w-[100%] gap-[1rem]"',
        1,
    )
    src = SLIDER_SRC["cases/"] if rel.startswith("cases/") else SLIDER_SCRIPT
    tag = f'  <script src="{src}"></script>\n'
    if "slider.js" not in content:
        content = content.replace(
            '  <script src="https://unpkg.com/lenis@1.1.20/dist/lenis.min.js"></script>',
            tag + '  <script src="https://unpkg.com/lenis@1.1.20/dist/lenis.min.js"></script>',
            1,
        )
    return content


def fix_case_links(content: str, rel: str) -> str:
    content = content.replace('href="_case-template.html"', "")
    content = content.replace('href="../_case-template.html"', "")
    return content


def fix_nav_and_footer(content: str, rel: str) -> str:
    p = prefix_for(rel)

    # Logo
    content = content.replace(
        f'<div class="flex items-center justify-center text-[#ffffff] max-md:order-1" id="logo" href="{p}index.html">',
        f'<a class="flex items-center justify-center text-[#ffffff] max-md:order-1 no-underline" id="logo" href="{p}index.html">',
    )
    content = content.replace(
        f'<img class="h-auto max-w-full h-[auto] max-w-[100%] w-[100px]" src="{p}assets/shared/navigation--logo.svg" alt="" href="{p}index.html" />',
        f'<img class="h-auto max-w-full h-[auto] max-w-[100%] w-[100px]" src="{p}assets/shared/navigation--logo.svg" alt="Dois Intelligence" />',
    )
    # Close logo div -> a (first occurrence after nav logo img)
    content = content.replace(
        f'<img class="h-auto max-w-full h-[auto] max-w-[100%] w-[100px]" src="{p}assets/shared/navigation--logo.svg" alt="Dois Intelligence" />\n            </div>',
        f'<img class="h-auto max-w-full h-[auto] max-w-[100%] w-[100px]" src="{p}assets/shared/navigation--logo.svg" alt="Dois Intelligence" />\n            </a>',
        1,
    )

    # Contato button in nav (YCode exports button+href)
    content = re.sub(
        r'<button class="(font-\[DM_Sans_9pt_Regular\][^"]*max-md:order-2)" href="('
        + re.escape(p)
        + r'contato\.html)">\s*<span>Contato</span>\s*</a>',
        r'<a class="\1 no-underline" href="\2"><span>Contato</span></a>',
        content,
    )
    content = re.sub(
        r'<button class="(font-\[DM_Sans_9pt_Regular\][^"]*max-md:order-2)" href="('
        + re.escape(p)
        + r'contato\.html)">\s*<span>Contato</span>\s*</button>',
        r'<a class="\1 no-underline" href="\2"><span>Contato</span></a>',
        content,
    )

    # Footer links: p with href -> a
    for page in [
        "index.html",
        "cases.html",
        "metodologia.html",
        "blog.html",
        "contato.html",
    ]:
        content = content.replace(
            f'<p class="focus:outline-none nav-link uppercase no-underline opacity-[60%] hover:opacity-[100%] text-[#ffffff] font-[DM_Sans_9pt_Regular] font-[400] tracking-[0.1em] text-[12px]" href="{p}{page}">',
            f'<a class="focus:outline-none nav-link uppercase no-underline opacity-[60%] hover:opacity-[100%] text-[#ffffff] font-[DM_Sans_9pt_Regular] font-[400] tracking-[0.1em] text-[12px]" href="{p}{page}">',
        )
        label = page.replace(".html", "").capitalize()
        if page == "index.html":
            label = "Home"
        content = content.replace(f">{label}</p>", f">{label}</a>")

    # WhatsApp floating
    content = re.sub(
        r'<div class="([^"]*)" href="(https://wa\.me/554488447212)">',
        r'<a class="\1" href="\2" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp">',
        content,
        count=1,
    )
    # Close whatsapp - find zap img block
    if 'aria-label="WhatsApp"' in content and "wa.me" in content:
        content = content.replace(
            f'<img class="[^"]*" src="{p}assets/shared/zap.svg"',
            f'<img class="w-[32px] h-[32px]" src="{p}assets/shared/zap.svg"',
            1,
        )

    return content


def fix_case_cards_manual(content: str, rel: str) -> str:
    """Case listing grids are generated by build_cases.py."""
    if "<!-- CASES_GRID_START -->" in content:
        return content
    return content


def hide_form_placeholders(content: str) -> str:
    content = content.replace(
        '<div class="bg-[#fee2e2] text-[#991b1b] text-[14px] font-[500] px-[1.5rem] py-[1rem] rounded-[0.75rem]">',
        '<div class="hidden bg-[#fee2e2] text-[#991b1b] text-[14px] font-[500] px-[1.5rem] py-[1rem] rounded-[0.75rem]">',
    )
    content = content.replace(
        '<div class="bg-[#d1fae5] text-[#065f46] text-[14px] font-[500] px-[1.5rem] py-[1rem] rounded-[0.75rem]">',
        '<div class="hidden bg-[#d1fae5] text-[#065f46] text-[14px] font-[500] px-[1.5rem] py-[1rem] rounded-[0.75rem]">',
    )
    return content


def fix_forms(content: str, rel: str) -> str:
    p = prefix_for(rel)
    # Until Formspree: CTA via WhatsApp on submit
    wa = "https://wa.me/554488447212?text=Ol%C3%A1%2C%20gostaria%20de%20falar%20com%20a%20Dois%20Intelligence"
    content = content.replace(
        '<form class="flex flex-col w-full gap-[24px] items-end" action="" method="POST">',
        f'<form class="flex flex-col w-full gap-[24px] items-end" action="{wa}" method="get" target="_blank" rel="noopener noreferrer">',
    )
    # Form submit buttons only (not hero CTA)
    content = re.sub(
        r'(<form[^>]*>[\s\S]*?<button[^>]*type=")button(")',
        r"\1submit\2",
        content,
        count=1,
    )
    return content


def fix_hero_cta(content: str, rel: str) -> str:
    if rel != "index.html":
        return content
    p = prefix_for(rel)
    old = (
        '          <div class="justify-center border-[transparent] border-[1px] border-solid focus:outline-none leading-[1.5em] font-dm-sans-9pt-regular rounded-[9999px] tracking-[0px] backdrop-blur-[8px] opacity-[100%] items-center text-[16px] font-semibold font-[DM_Sans_9pt_Regular] leading-[1.5] tracking-[0] uppercase pt-[8px] pr-[8px] pb-[8px] pl-[20px] mt-[36px] border-transparent bg-[#ffffff]/10 text-[#ffffff] flex-wrap w-a flex flex-row gap-[10px] w-a w-u w-uto w-ut" id="bttn" type="button">'
    )
    new = (
        f'          <a href="{p}contato.html" class="justify-center border-[transparent] border-[1px] border-solid focus:outline-none leading-[1.5em] font-dm-sans-9pt-regular rounded-[9999px] tracking-[0px] backdrop-blur-[8px] opacity-[100%] items-center text-[16px] font-semibold font-[DM_Sans_9pt_Regular] leading-[1.5] tracking-[0] uppercase pt-[8px] pr-[8px] pb-[8px] pl-[20px] mt-[36px] border-transparent bg-[#ffffff]/10 text-[#ffffff] flex-wrap w-a flex flex-row gap-[10px] w-a w-u w-uto w-ut no-underline" id="bttn">'
    )
    if old in content:
        content = content.replace(old, new, 1)
        content = content.replace(
            "            </div>\n          </div>\n        </div>\n      </div>\n      <div class=\"flex flex-col absolute top-au\"",
            "            </div>\n          </a>\n        </div>\n      </div>\n      <div class=\"flex flex-col absolute top-au\"",
            1,
        )
    return content


def fix_case_page_buttons(content: str, rel: str) -> str:
    if rel == "cases/trifold.html":
        content = content.replace(
            'type="button" href="../_case-template.html"',
            'href="../cases.html"',
        )
        content = re.sub(
            r"<button([^>]*href=\"../cases\.html\"[^>]*)>",
            r"<a\1>",
            content,
        )
        content = content.replace("</button>", "</a>", 1)
    if rel == "cases/yarden.html":
        content = content.replace(
            'type="button" href="../_case-template.html"',
            'href="../cases.html"',
        )
        content = re.sub(
            r"<button([^>]*href=\"../cases\.html\"[^>]*)>",
            r"<a\1>",
            content,
        )
        content = content.replace("</button>", "</a>", 1)
    return content


def inject_seo(content: str, rel: str) -> str:
    meta = PAGE_META.get(rel)
    if not meta:
        return content
    canonical = f"{DOMAIN}/{meta['path']}" if meta["path"] else f"{DOMAIN}/"
    og_image = f"{DOMAIN}/assets/library/dois-black-1.svg"

    content = re.sub(r"<title>[^<]*</title>", f"<title>{meta['title']}</title>", content, count=1)
    content = re.sub(
        r'<meta name="description" content="[^"]*" />',
        f'<meta name="description" content="{meta["description"]}" />',
        content,
        count=1,
    )

    head_extra = f"""  <link rel="canonical" href="{canonical}" />
  <link rel="icon" href="{DOMAIN}/assets/library/dois-black-1.svg" type="image/svg+xml" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:title" content="{meta['title']}" />
  <meta property="og:description" content="{meta['description']}" />
  <meta property="og:image" content="{og_image}" />
  <meta name="twitter:card" content="summary_large_image" />
"""
    if "rel=\"canonical\"" not in content:
        content = content.replace("</head>", head_extra + "</head>", 1)

    # Fix favicon path for case subpages
    if rel.startswith("cases/"):
        content = content.replace(
            'href="/assets/library/dois-black-1.svg"',
            'href="../assets/library/dois-black-1.svg"',
        )
        content = content.replace(f'content="{og_image}"', f'content="{DOMAIN}/assets/library/dois-black-1.svg"')

    return content


def fix_blog_body(content: str, rel: str) -> str:
    if rel != "blog.html":
        return content
    p = ""
    snippet = f"""  <main class="min-h-[60vh] flex flex-col items-center justify-center px-[32px] py-[120px] text-center bg-[#0a0a0a] text-[#ffffff]">
    <h1 class="font-[STIX_Two_Text] text-[48px] mb-[16px]">Blog</h1>
    <p class="font-[DM_Sans_9pt_Regular] text-[18px] opacity-[60%] max-w-[480px]">Em breve publicaremos conteúdos sobre branding imobiliário.</p>
    <a href="{p}index.html" class="mt-[32px] uppercase tracking-[0.1em] text-[12px] opacity-[80%] hover:opacity-100 no-underline text-[#ffffff]">Voltar ao início</a>
  </main>
"""
    content = content.replace("<body>\n  <div></div>", f"<body>\n{snippet}")
    return content


def fix_root_relative_background_urls(content: str) -> str:
    """Make asset URLs in backgrounds root-relative.

    When background-image comes from assets/shared/tailwind.css via
    var(--bg-img), relative url(assets/...) resolves against the stylesheet
    (e.g. assets/shared/assets/home/...) instead of the site root.
    """
    content = re.sub(
        r"(--bg-img(?:-mobile)?):\s*url\((?!['\"]?/)(?:\.\./)?(assets/[^)\s]+)\)",
        r"\1: url(/\2)",
        content,
    )
    content = re.sub(
        r"background-image:url\((?!/)(?:\.\./)?(assets/[^)]+)\)",
        r"background-image:url(/\1)",
        content,
    )
    return content


def close_whatsapp_anchor(content: str) -> str:
    if 'aria-label="WhatsApp"' not in content:
        return content
    # Replace closing </div> after zap icon for whatsapp floater
    idx = content.find('aria-label="WhatsApp"')
    if idx == -1:
        return content
    zap = content.find("assets/shared/zap.svg", idx)
    if zap == -1:
        return content
    end = content.find("</div>", zap)
    if end != -1:
        content = content[:end] + "</a>" + content[end + len("</div>") :]
    return content


def process_file(rel: str) -> None:
    path = ROOT / rel
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = fix_slider(text, rel)
    text = fix_case_links(text, rel)
    text = fix_nav_and_footer(text, rel)
    text = fix_case_cards_manual(text, rel)
    text = hide_form_placeholders(text)
    text = fix_forms(text, rel)
    text = fix_hero_cta(text, rel)
    text = fix_case_page_buttons(text, rel)
    text = inject_seo(text, rel)
    text = fix_blog_body(text, rel)
    text = close_whatsapp_anchor(text)
    text = fix_root_relative_background_urls(text)
    path.write_text(text, encoding="utf-8")
    print(f"fixed {rel}")


def main():
    for rel in HTML_FILES:
        process_file(rel)
    print("done")


if __name__ == "__main__":
    main()
