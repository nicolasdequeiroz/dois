#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build case pages from data/cases/*.json and update listing grids."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data" / "cases"
TEMPLATE_PATH = ROOT / "cases" / "_template.html"
DOMAIN = "https://doisintelligence.com.br"

GRID_START = "<!-- CASES_GRID_START -->"
GRID_END = "<!-- CASES_GRID_END -->"
FEATURED_START = "<!-- CASES_FEATURED_START -->"
FEATURED_END = "<!-- CASES_FEATURED_END -->"


def load_index() -> list[dict]:
    data = json.loads((DATA_DIR / "index.json").read_text(encoding="utf-8"))
    items = [c for c in data["cases"] if c.get("published", True)]
    return sorted(items, key=lambda c: c.get("order", 999))


def load_case(slug: str) -> dict:
    path = DATA_DIR / f"{slug}.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing case data: {path}")
    case = json.loads(path.read_text(encoding="utf-8"))
    case.setdefault("slug", slug)
    case.setdefault("assets", {})
    case.setdefault("services", [])
    case.setdefault("mockups", [])
    case.setdefault("verticalVideos", [])
    case.setdefault("results", [])
    case.setdefault("testimonial", {})
    case.setdefault("seo", {})
    return case


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def paragraphs_html(paragraphs: list[str]) -> str:
    return "".join(f"<p>{esc(p)}</p>" for p in paragraphs if p and p.strip())


def meta_segment(segment: str) -> str:
    if not segment:
        return ""
    return f"""            <div class="flex flex-col gap-[4px]">
              <p class="text-[16px] font-[STIX_Two_Text_Italic] text-[#ffffff]/40">Segmento</p>
              <p class="text-[16px] text-[#ffffff]">{esc(segment)}</p>
            </div>"""


def meta_duration(duration: str) -> str:
    if not duration:
        return ""
    return f"""            <div class="flex flex-col gap-[4px]">
              <p class="text-[16px] font-[STIX_Two_Text_Italic] text-[#ffffff]/40">Duração</p>
              <p class="text-[16px] text-[#ffffff]">{esc(duration)}</p>
            </div>"""


def meta_services(services: list[str]) -> str:
    if not services:
        return ""
    parts = []
    for i, service in enumerate(services):
        if i > 0:
            parts.append('<div class="flex flex-col w-[2px] h-[2px] mr-[8px] bg-[#ffffff]"></div>')
        parts.append(f'<p class="text-[16px] text-[#ffffff] pr-[0px] mr-[0px]">{esc(service)}</p>')
    inner = "\n                  ".join(parts)
    return f"""            <div class="flex flex-col gap-[4px]">
              <p class="text-[16px] font-[STIX_Two_Text_Italic] text-[#ffffff]/40">Serviços</p>
              <div class="flex flex-row gap-[0px] max-md:flex-nowrap">
                <div class="flex-nowrap justify-start gap-[8px] items-center flex flex-row max-md:flex-nowrap">
                  {inner}
                </div>
              </div>
            </div>"""


def visual_strategy_section(case: dict) -> str:
    assets = case["assets"]
    before = assets.get("logoBefore")
    after = assets.get("logoAfter")
    if not before or not after:
        return ""
    slug = case["slug"]
    return f"""      <hr class="border-t-[1px] border-[#000000]/20 bg-[#000000]/10 opacity-[50%]" />
      <div class="mr-auto ml-auto w-full flex flex-col w-[100%] max-w-[1280px] mr-[auto] ml-[auto] pr-[32px] pl-[32px] max-md:pl-[0px] max-md:pr-[0px]">
        <div class="flex flex-col gap-[24px]">
          <h2 class="leading-[1.1] tracking-[-0.01em] font-[STIX_Two_Text_Italic] font-[400] text-[24px] text-[#171717]">Estratégia Visual</h2>
          <div class="flex flex-col items-stretch gap-[12px]">
            <div class="flex flex-col relative ba-container overflow-hidden w-[100%] aspect-[16/9] rounded-[4px] border-solid border-[#000000]/10 border-[1.5px]">
              <img class="object-cover absolute inset-0 w-full h-full ba-before" loading="lazy" src="../assets/cases/{slug}/{esc(before)}" alt="Logo antes — {esc(case['name'])}" />
              <img class="object-cover absolute inset-0 w-full h-full ba-after" loading="lazy" src="../assets/cases/{slug}/{esc(after)}" alt="Logo depois — {esc(case['name'])}" />
              <div class="flex flex-col ba-slider"></div>
            </div>
            <div class="flex flex-row items-center justify-between">
              <p class="text-[#171717]/40 text-[12px] font-[600]">ANTES</p>
              <p class="text-[#171717]/40 text-[12px] font-[600]">DEPOIS</p>
            </div>
          </div>
          <div class="grid-cols-[repeat(2,_1fr)] gap-[4px] flex flex-row">
            <div class="flex flex-col gap-[12px] w-[100%]">
              <div class="flex flex-col items-center border-solid border-[#171717]/10 rounded-[4px] border-[1.5px] overflow-hidden w-[100%] aspect-[16/9]">
                <img class="w-[100%] object-cover h-full" loading="lazy" src="../assets/cases/{slug}/{esc(after)}" alt="Alternativa aprovada — {esc(case['name'])}" />
              </div>
              <p class="text-[#171717]/40 text-[12px] font-[600]">ALTERNATIVA APROVADA</p>
            </div>
          </div>
        </div>
      </div>"""


def main_film_section(case: dict) -> str:
    film = case["assets"].get("mainFilm")
    if not film:
        return ""
    slug = case["slug"]
    return f"""      <hr class="border-t-[1px] border-[#000000]/20 bg-[#000000]/10 opacity-[50%]" />
      <div class="mr-auto ml-auto w-full flex flex-col w-[100%] max-w-[1280px] mr-[auto] ml-[auto] pr-[32px] pl-[32px]">
        <div class="flex flex-col gap-[24px]">
          <h2 class="leading-[1.1] tracking-[-0.01em] font-[STIX_Two_Text_Italic] font-[400] text-[24px] text-[#171717]">Materiais Produzidos</h2>
          <div class="flex flex-col gap-[12px] items-start w-[100%]">
            <video class="w-full h-auto aspect-[16/9] overflow-hidden" preload="metadata" controls src="../assets/cases/{slug}/{esc(film)}"></video>
            <p class="text-[#171717]/40 text-[12px] font-[600]">FILME DE LANÇAMENTO</p>
          </div>
        </div>
      </div>"""


def mockups_gallery_section(case: dict) -> str:
    mockups = case.get("mockups") or []
    if not mockups:
        return ""
    slug = case["slug"]
    cells = []
    for filename in mockups:
        cells.append(
            f"""            <div class="flex flex-col gap-[12px] w-[100%]">
              <div class="flex flex-col items-center border-solid border-[#171717]/10 rounded-[4px] border-[1.5px] overflow-hidden w-[100%] aspect-[16/9]">
                <img class="w-[100%] object-cover h-full" loading="lazy" src="../assets/cases/{slug}/{esc(filename)}" alt="" />
              </div>
            </div>"""
        )
    grid = "\n".join(cells)
    return f"""    <section class="flex flex-col w-[100%] items-center pt-[0px] pb-[90px] pl-[5%] pr-[5%]">
      <div class="mr-auto ml-auto w-full flex flex-col w-[100%] max-w-[1280px] mr-[auto] ml-[auto] pr-[32px] pl-[32px]">
        <div class="flex flex-col gap-[24px]">
          <h2 class="leading-[1.1] tracking-[-0.01em] font-[STIX_Two_Text_Italic] font-[400] text-[24px] text-[#171717]">Materiais de marca</h2>
          <div class="grid grid-cols-[repeat(2,_1fr)] gap-[16px] max-md:grid-cols-1">
{grid}
          </div>
        </div>
      </div>
    </section>"""


def audiovisual_section(case: dict) -> str:
    videos = case.get("verticalVideos") or []
    if not videos:
        return ""
    slug = case["slug"]
    blocks = []
    for filename in videos:
        blocks.append(
            f"""            <div class="flex flex-col gap-[12px] w-[100%] items-center">
              <div class="flex flex-col rounded-[4px] overflow-hidden border-solid border-[1.5px] border-[#000000]/10">
                <video class="w-full aspect-[16/9] overflow-hidden object-cover h-[600px]" preload="metadata" controls src="../assets/cases/{slug}/{esc(filename)}"></video>
              </div>
            </div>"""
        )
    inner = "\n".join(blocks)
    return f"""      <hr class="border-t-[1px] border-[#000000]/20 bg-[#000000]/10 opacity-[50%]" />
      <div class="mr-auto ml-auto w-full flex flex-col w-[100%] max-w-[1280px] mr-[auto] ml-[auto] pr-[32px] pl-[32px] max-md:pl-[0px] max-md:pt-[0px] max-md:pr-[0px] max-md:pb-[0px]">
        <div class="flex flex-col gap-[24px]">
          <h2 class="leading-[1.1] tracking-[-0.01em] font-[STIX_Two_Text_Italic] font-[400] text-[24px] text-[#171717]">Audiovisual</h2>
          <div class="flex flex-row gap-[48px] max-md:flex max-md:flex-col">
{inner}
          </div>
        </div>
      </div>"""


def results_html(results: list[dict]) -> str:
    parts = []
    for item in results:
        value = item.get("value", "")
        label = item.get("label", "")
        if not value:
            continue
        parts.append(f"<h2>{esc(value)}</h2><p>{esc(label)}</p>")
    return "".join(parts)


def testimonial_section(case: dict) -> str:
    t = case.get("testimonial") or {}
    quote = (t.get("quote") or "").strip()
    name = (t.get("name") or "").strip()
    role = (t.get("role") or "").strip()
    photo = case["assets"].get("clientPhoto")
    if not quote and not name:
        return ""
    slug = case["slug"]
    photo_html = ""
    if photo:
        photo_html = f'<img class="object-cover w-[80px] h-[80px] rounded-[999px]" loading="lazy" src="../assets/cases/{slug}/{esc(photo)}" alt="{esc(name)}" />'
    return f"""          <div class="flex flex-col">
            <div class="flex flex-col pl-[48px] pt-[48px] pr-[48px] pb-[48px] bg-[#000000]/5 rounded-[16px] gap-[24px] max-md:pl-[32px] max-md:pt-[32px] max-md:pr-[32px] max-md:pb-[32px]">
              <p class="font-[STIX_Two_Text_Italic] text-[24px] max-md:text-[18px]">{esc(quote)}</p>
              <div class="gap-[16px] flex flex-row items-center">
                {photo_html}
                <div class="flex flex-col gap-[4px]">
                  <p class="text-[16px] font-[700]">{esc(name)}</p>
                  <p class="text-[12px] opacity-[40%]">{esc(role)}</p>
                </div>
              </div>
            </div>
          </div>"""


def next_case_link(slug: str, ordered_slugs: list[str]) -> str:
    if slug not in ordered_slugs:
        return """              <a class="flex flex-row items-center justify-center pt-[8px] pb-[8px] text-[14px] bg-[#e5e5e5] text-[#171717] pl-[24px] pr-[24px] rounded-[999px] no-underline" href="../cases.html">
                <span>Ver todos os cases</span>
              </a>"""
    idx = ordered_slugs.index(slug)
    nxt = ordered_slugs[(idx + 1) % len(ordered_slugs)]
    if nxt == slug:
        return """              <a class="flex flex-row items-center justify-center pt-[8px] pb-[8px] text-[14px] bg-[#e5e5e5] text-[#171717] pl-[24px] pr-[24px] rounded-[999px] no-underline" href="../cases.html">
                <span>Ver todos os cases</span>
              </a>"""
    return f"""              <a class="flex flex-row items-center justify-center pt-[8px] pb-[8px] text-[14px] bg-[#e5e5e5] text-[#171717] pl-[24px] pr-[24px] rounded-[999px] no-underline" href="{esc(nxt)}.html">
                <span>Próximo case</span>
              </a>"""


def render_case(case: dict, ordered_slugs: list[str]) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    slug = case["slug"]
    assets = case["assets"]
    hero = assets.get("heroImage") or "imagem-principal.webp"
    seo = case.get("seo") or {}
    seo_title = seo.get("title") or f"Case {case.get('name', slug)} — Dois Intelligence"
    seo_desc = seo.get("description") or case.get("cardText") or f"Case {case.get('name', slug)} pela Dois Intelligence."

    replacements = {
        "{{SLUG}}": esc(slug),
        "{{NAME}}": esc(case.get("name", slug)),
        "{{HEADLINE}}": esc(case.get("headline", "")),
        "{{HERO_IMAGE}}": esc(hero),
        "{{SEO_TITLE}}": esc(seo_title),
        "{{SEO_DESCRIPTION}}": esc(seo_desc),
        "{{INTRO_HTML}}": paragraphs_html(case.get("intro") or []),
        "{{META_SEGMENT}}": meta_segment(case.get("segment") or ""),
        "{{META_DURATION}}": meta_duration(case.get("duration") or ""),
        "{{META_SERVICES}}": meta_services(case.get("services") or []),
        "{{CHALLENGE_HTML}}": paragraphs_html(case.get("challenge") or []),
        "{{STRATEGIC_DECISION_HTML}}": paragraphs_html(case.get("strategicDecision") or []),
        "{{APPLIED_STRATEGY_HTML}}": paragraphs_html(case.get("appliedStrategy") or []),
        "{{VISUAL_STRATEGY_SECTION}}": visual_strategy_section(case),
        "{{MOCKUPS_SECTION}}": "",
        "{{MAIN_FILM_SECTION}}": main_film_section(case),
        "{{MOCKUPS_GALLERY_SECTION}}": mockups_gallery_section(case),
        "{{AUDIOVISUAL_SECTION}}": audiovisual_section(case),
        "{{RESULTS_HTML}}": results_html(case.get("results") or []),
        "{{TESTIMONIAL_SECTION}}": testimonial_section(case),
        "{{NEXT_CASE_LINK}}": next_case_link(slug, ordered_slugs),
    }

    out = template
    for key, value in replacements.items():
        out = out.replace(key, value)
    return out


def case_card_html(case: dict, prefix: str = "") -> str:
    slug = case["slug"]
    assets = case["assets"]
    hero = assets.get("heroImage") or "imagem-principal.webp"
    title = case.get("name") or slug
    excerpt = case.get("cardText") or ""
    return f"""          <div class="flex-none snap-center w-vw w-% w-% w-vw">
            <a href="{prefix}cases/{slug}.html" class="block no-underline">
            <div class="h-[400px] bg-cover bg-center bg-no-repeat relative overflow-hidden border-solid border-[#000000]/10 border-[1.5px] flex flex-row items-end rounded-[12px]" style="background-image:url(/assets/cases/{slug}/{esc(hero)})">
              <div class="flex flex-col w-[100%] pt-[24px] pr-[24px] pb-[24px] pl-[24px] relative z-[5] gap-[8px]">
                <h2 class="leading-[1.1] tracking-[-0.01em] text-[#ffffff] text-[24px] font-[DM_Sans_9pt_Regular] font-[400]">{esc(title)}</h2>
                <p class="text-[#ffffff]/60 text-[12px] w-[60%]">{esc(excerpt)}</p>
              </div>
            </div>
            </a>
          </div>"""


def featured_case_html(case: dict, prefix: str = "") -> str:
    slug = case["slug"]
    assets = case["assets"]
    logo = assets.get("logoCard") or assets.get("logoAfter")
    title = case.get("name") or slug
    logo_src = f"{prefix}assets/cases/{slug}/{logo}" if logo else f"{prefix}assets/cases/{slug}/{assets.get('heroImage', 'imagem-principal.webp')}"
    return f"""          <a href="{prefix}cases/{slug}.html" class="gap-[1rem] flex flex-row items-center pb-[24px] pl-[24px] pt-[24px] pr-[48px] relative no-underline">
            <img class="object-cover rounded-[8px] w-[120px] h-[80px]" loading="lazy" src="{logo_src}" alt="{esc(title)}" />
            <div class="flex flex-col gap-[2px]">
              <p class="text-[16px] font-[STIX_Two_Text_Italic] text-[#ffffff]/40">Em destaque</p>
              <p class="text-[#ffffff] text-[24px] font-[DM_Sans_9pt_Regular] font-[400]">{esc(title)}</p>
            </div>
            <div class="absolute top-[0px] right-[0px] flex flex-row items-center w-[40px] h-[40px]">
              <img class="w-[100%] object-cover" loading="lazy" src="{prefix}assets/home/hero-text-bttn-arrow-block-image.svg" alt="" />
            </div>
          </a>"""


def remove_stale_featured(content: str) -> str:
    pattern = re.compile(
        r"(<!-- CASES_FEATURED_END -->)\s*<a href=\"cases/[^\"]+\.html\" class=\"gap-\[1rem\].*?</a>\s*",
        re.DOTALL,
    )
    return pattern.sub(r"\1\n", content)


def remove_stale_cards(content: str) -> str:
    """Drop legacy hardcoded cards left after CASES_GRID_END."""
    pattern = re.compile(
        r"(<!-- CASES_GRID_END -->)\s*(?:\s*<div class=\"flex-none snap-center.*?</a>\s*</div>\s*)+",
        re.DOTALL,
    )
    return pattern.sub(r"\1\n", content)


def patch_between(content: str, start: str, end: str, replacement: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(content):
        raise ValueError(f"Markers not found: {start} ... {end}")
    block = f"{start}\n{replacement}\n          {end}"
    return pattern.sub(block, content, count=1)


def update_listings(cases: list[dict]) -> None:
    grid = "\n".join(case_card_html(c) for c in cases)
    cases_html = ROOT / "cases.html"
    text = remove_stale_cards(cases_html.read_text(encoding="utf-8"))
    text = patch_between(text, GRID_START, GRID_END, grid)
    cases_html.write_text(text, encoding="utf-8")
    print(f"updated {cases_html.name} grid ({len(cases)} cases)")

    index_html = ROOT / "index.html"
    text = remove_stale_cards(index_html.read_text(encoding="utf-8"))
    text = patch_between(text, GRID_START, GRID_END, grid)
    featured = next((c for c in cases if c.get("featured")), cases[0] if cases else None)
    if featured and FEATURED_START in text:
        text = remove_stale_featured(text)
        text = patch_between(text, FEATURED_START, FEATURED_END, featured_case_html(featured))
    index_html.write_text(text, encoding="utf-8")
    print(f"updated {index_html.name} grid + featured")


def ensure_markers() -> None:
    for rel in ("cases.html", "index.html"):
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        changed = False
        if GRID_START not in text:
            text = text.replace(
                '        <div class="grid grid-cols-[repeat(2,_1fr)] gap-[24px] max-md:flex max-md:flex-col max-md:gap-[16px]">',
                f'        <div class="grid grid-cols-[repeat(2,_1fr)] gap-[24px] max-md:flex max-md:flex-col max-md:gap-[16px]">\n          {GRID_START}\n          {GRID_END}',
                1,
            )
            changed = True
        if rel == "index.html" and FEATURED_START not in text:
            text = text.replace(
                '        <div class="rounded-[12px] backdrop-blur-[10px] gap-[16px] bg-[#ffffff]/5 flex flex-row items-center pl-[0px] pt-[0px] pr-[0px] pb-[0px]">',
                f'        <div class="rounded-[12px] backdrop-blur-[10px] gap-[16px] bg-[#ffffff]/5 flex flex-row items-center pl-[0px] pt-[0px] pr-[0px] pb-[0px]">\n          {FEATURED_START}\n          {FEATURED_END}',
                1,
            )
            changed = True
        if changed:
            path.write_text(text, encoding="utf-8")
            print(f"added markers to {rel}")


def main() -> None:
    ensure_markers()
    index = load_index()
    ordered_slugs = [item["slug"] for item in index]
    cases = [load_case(slug) for slug in ordered_slugs]

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    for case in cases:
        slug = case["slug"]
        out_path = ROOT / "cases" / f"{slug}.html"
        out_path.write_text(render_case(case, ordered_slugs), encoding="utf-8")
        print(f"built cases/{slug}.html")

    update_listings(cases)
    print("done")


if __name__ == "__main__":
    main()
