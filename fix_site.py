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

    content = normalize_nav_cta(content)

    content = remove_footer_blog_link(content)

    # Footer links: p with href -> a
    for page in [
        "index.html",
        "cases.html",
        "metodologia.html",
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


def normalize_nav_cta(content: str) -> str:
    pattern = re.compile(
        r'<a class="font-\[DM_Sans_9pt_Regular\][^"]*max-md:order-2[^"]*" '
        r'href="([^"]*contato\.html)"><span>Contato</span></a>',
        re.IGNORECASE,
    )

    def repl(match: re.Match) -> str:
        return (
            f'<a class="nav-cta font-dm-sans-9pt-regular font-bold uppercase '
            f'tracking-[0.025em] text-[12px] max-md:order-2 no-underline" '
            f'href="{match.group(1)}"><span>Contato</span></a>'
        )

    return pattern.sub(repl, content)


def remove_footer_blog_link(content: str) -> str:
    pattern = re.compile(
        r'\s*<a class="focus:outline-none nav-link[^"]*" '
        r'href="(?:\.\./)?blog\.html">Blog</a>',
        re.IGNORECASE,
    )
    return pattern.sub("", content)


WHATSAPP_URL = "https://wa.me/554488447212"

WHATSAPP_ICON_SVG = (
    '<svg width="21" height="21" viewBox="0 0 21 21" fill="none" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path d="M17.8125 3.09375C19.7812 5.0625 21 7.64062 21 10.4531C21 16.1719 16.2188 20.8594 10.4531 20.8594C8.71875 20.8594 7.03125 20.3906 5.48438 19.5938L0 21L1.45312 15.6094C0.5625 14.0625 0.046875 12.2812 0.046875 10.4062C0.046875 4.6875 4.73438 0 10.4531 0C13.2656 0 15.8906 1.125 17.8125 3.09375ZM10.4531 19.0781C15.2344 19.0781 19.2188 15.1875 19.2188 10.4531C19.2188 8.10938 18.2344 5.95312 16.5938 4.3125C14.9531 2.67188 12.7969 1.78125 10.5 1.78125C5.71875 1.78125 1.82812 5.67188 1.82812 10.4062C1.82812 12.0469 2.29688 13.6406 3.14062 15.0469L3.375 15.375L2.48438 18.5625L5.76562 17.6719L6.04688 17.8594C7.40625 18.6562 8.90625 19.0781 10.4531 19.0781ZM15.2344 12.6094C15.4688 12.75 15.6562 12.7969 15.7031 12.9375C15.7969 13.0312 15.7969 13.5469 15.5625 14.1562C15.3281 14.7656 14.2969 15.3281 13.8281 15.375C12.9844 15.5156 12.3281 15.4688 10.6875 14.7188C8.0625 13.5938 6.375 10.9688 6.23438 10.8281C6.09375 10.6406 5.20312 9.42188 5.20312 8.10938C5.20312 6.84375 5.85938 6.23438 6.09375 5.95312C6.32812 5.67188 6.60938 5.625 6.79688 5.625C6.9375 5.625 7.125 5.625 7.26562 5.625C7.45312 5.625 7.64062 5.57812 7.875 6.09375C8.0625 6.60938 8.625 7.875 8.67188 8.01562C8.71875 8.15625 8.76562 8.29688 8.67188 8.48438C8.20312 9.46875 7.64062 9.42188 7.92188 9.89062C8.95312 11.625 9.9375 12.2344 11.4844 12.9844C11.7188 13.125 11.8594 13.0781 12.0469 12.9375C12.1875 12.75 12.7031 12.1406 12.8438 11.9062C13.0312 11.625 13.2188 11.6719 13.4531 11.7656C13.6875 11.8594 14.9531 12.4688 15.2344 12.6094Z" fill="white"/>'
    "</svg>"
)


def whatsapp_floater_markup(prefix: str = "") -> str:
    return (
        f'<a class="whatsapp-floater" href="{WHATSAPP_URL}" target="_blank" '
        f'rel="noopener noreferrer" aria-label="Falar no WhatsApp">'
        f"{WHATSAPP_ICON_SVG}"
        f"</a>"
    )


HERO_BTTN_ARROW = (
    '<span class="bttn-arrow-block rounded-full flex items-center justify-center w-[36px] h-[36px] '
    'shrink-0 bg-[#ffffff]/10" aria-hidden="true">'
    '<svg width="11" height="11" viewBox="0 0 11 11" fill="none" xmlns="http://www.w3.org/2000/svg" '
    'aria-hidden="true"><path d="M9.34375 0C9.75 0 10.0938 0.34375 10.0938 0.75V8.25C10.0938 8.6875 '
    "9.75 9 9.34375 9C8.90625 9 8.59375 8.6875 8.59375 8.25V2.5625L1.375 9.78125C1.0625 10.0938 "
    "0.59375 10.0938 0.3125 9.78125C0 9.5 0 9.03125 0.3125 8.75L7.53125 1.53125H1.84375C1.40625 "
    "1.53125 1.09375 1.1875 1.09375 0.78125C1.09375 0.34375 1.40625 0.03125 1.84375 0.03125H9.34375V0Z"
    ' fill="white"/></svg></span>'
)

YCODE_GARBAGE_CLASSES = frozenset({"w-a", "w-u", "w-uto", "w-ut", "w-vw", "w-%"})
CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')

DUPLICATE_SECTION_CLASS_RE = re.compile(
    r'(class="h-auto flex flex-col overflow-hidden h-\[auto\] pl-\[5%\] pr-\[5%\] pt-\[140px\] pb-\[140px\])\s+\1'
)


def strip_ycode_garbage_classes(content: str) -> str:
    def repl(match: re.Match) -> str:
        classes = [c for c in match.group(1).split() if c not in YCODE_GARBAGE_CLASSES]
        return f'class="{" ".join(classes)}"'

    return CLASS_ATTR_RE.sub(repl, content)


def cleanup_ycode_artifacts(content: str, rel: str) -> str:
    """Remove common YCode export noise from HTML."""
    content = content.replace("[&#x27;block&#x27;] ", "")
    content = content.replace(" top-au", "")
    content = strip_ycode_garbage_classes(content)
    content = DUPLICATE_SECTION_CLASS_RE.sub(r"\1", content)
    content = content.replace("no-nderline", "no-underline")
    content = content.replace("no-u ", "no-underline ")
    content = content.replace('no-u"', 'no-underline"')

    content = content.replace(
        "flex-wrap w-a flex flex-row gap-[10px]",
        "inline-flex flex-row items-center gap-[10px]",
    )
    content = content.replace(
        "flex-wrap flex flex-row gap-[10px]",
        "inline-flex flex-row items-center gap-[10px]",
    )
    content = content.replace(
        'h-auto max-w-full h-[auto] max-w-[100%]',
        "h-auto max-w-full",
    )
    content = content.replace('alt="Image description"', 'alt="" aria-hidden="true"')

    # Hero CTA: SVG inline (export corrompia o arquivo .svg em pixels)
    content = re.sub(
        r'<span class="bttn-arrow-block[^"]*">'
        r"\s*<img[^>]*hero-text-bttn-arrow-block-image\.svg[^>]*/>\s*</span>",
        HERO_BTTN_ARROW,
        content,
    )
    content = re.sub(
        r'<div class="rounded-full[^"]*" id="arrow-block">\s*'
        r'<img[^>]*hero-text-bttn-arrow-block-image\.svg[^>]*/>\s*</div>',
        HERO_BTTN_ARROW,
        content,
    )
    content = re.sub(
        r'<img[^>]*hero-text-bttn-arrow-block-image\.svg[^>]*/>',
        HERO_BTTN_ARROW,
        content,
    )

    content = dedupe_bttn_ids(content)
    content = ensure_hero_bttn_id(content, rel)
    return content


def ensure_hero_bttn_id(content: str, rel: str) -> str:
    """Primeiro .site-bttn da home (hero) mantém id=\"bttn\" para scripts/estilos."""
    if rel != "index.html":
        return content
    marker = 'id="hero-text"'
    pos = content.find(marker)
    if pos == -1:
        return content
    bttn = content.find('class="site-bttn', pos)
    if bttn == -1:
        return content
    tag_start = content.rfind("<a ", pos, bttn + 5)
    if tag_start == -1:
        return content
    close = content.find(">", tag_start)
    if close == -1:
        return content
    tag_chunk = content[tag_start:close]
    if 'id="bttn"' in tag_chunk:
        return content
    if 'href="contato.html"' not in tag_chunk:
        return content
    new_tag = tag_chunk.replace('class="site-bttn', 'id="bttn" class="site-bttn', 1)
    return content[:tag_start] + new_tag + content[close:]


def _ensure_class_on_tag(content: str, id_pos: int, class_name: str) -> str:
    class_attr = content.rfind('class="', max(0, id_pos - 800), id_pos)
    if class_attr == -1:
        return content
    snippet = content[class_attr : id_pos + 40]
    if class_name in snippet:
        return content
    insert_at = class_attr + len('class="')
    return content[:insert_at] + f"{class_name} " + content[insert_at:]


def dedupe_bttn_ids(content: str) -> str:
    """Keep one id=\"bttn\"; demais CTAs iguais usam .site-bttn."""
    marker = 'id="bttn"'
    first = content.find(marker)
    if first == -1:
        return content

    content = _ensure_class_on_tag(content, first, "site-bttn")
    offset = first + len(marker)
    while True:
        pos = content.find(marker, offset)
        if pos == -1:
            break
        content = _ensure_class_on_tag(content, pos, "site-bttn")
        content = content[:pos] + content[pos + len(marker) :]
        offset = pos

    return content


def normalize_whatsapp_floater(content: str, rel: str) -> str:
    if "wa.me/554488447212" not in content:
        return content
    prefix = "../" if rel.startswith("cases/") else ""
    pattern = re.compile(
        r'<a\s[^>]*href=["\']https://wa\.me/554488447212["\'][^>]*>.*?</a>',
        re.DOTALL | re.IGNORECASE,
    )
    return pattern.sub(whatsapp_floater_markup(prefix), content, count=1)


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
    text = normalize_whatsapp_floater(text, rel)
    text = fix_root_relative_background_urls(text)
    text = cleanup_ycode_artifacts(text, rel)
    path.write_text(text, encoding="utf-8")
    print(f"fixed {rel}")


def main():
    for rel in HTML_FILES:
        process_file(rel)
    print("done")


if __name__ == "__main__":
    main()
