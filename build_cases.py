#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build case pages from data/cases/*.json and update listing grids."""

from __future__ import annotations

import html
import json
import re
import subprocess
import tempfile
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


def normalize_vertical_videos(videos: list) -> list[dict]:
    normalized = []
    for item in videos:
        if isinstance(item, str):
            if item.strip():
                normalized.append({"src": item.strip(), "poster": None})
        elif isinstance(item, dict):
            src = (item.get("src") or item.get("file") or "").strip()
            poster = item.get("poster")
            if poster is not None:
                poster = str(poster).strip() or None
            if src:
                normalized.append({"src": src, "poster": poster})
    return normalized


def default_poster_filename(src: str) -> str:
    return f"{Path(src).stem}-poster.webp"


def should_auto_poster(slug: str, poster_setting: str | None, video_index: int) -> bool:
    if poster_setting == "auto":
        return True
    # Trifold: 3º vídeo sem poster manual → capa automática
    return slug == "trifold" and video_index == 2 and poster_setting is None


def generate_poster_from_video(slug: str, src: str) -> str | None:
    video_path = ROOT / "assets" / "cases" / slug / src
    if not video_path.exists():
        print(f"  warn: vídeo ausente para gerar poster: {video_path.relative_to(ROOT)}")
        return None

    poster_name = default_poster_filename(src)
    poster_path = video_path.parent / poster_name
    if poster_path.exists() and poster_path.stat().st_size > 0:
        return poster_name

    tmp_path = None
    try:
        from PIL import Image

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        for seek in ("0.5", "0"):
            result = subprocess.run(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-ss", seek, "-i", str(video_path),
                    "-vframes", "1", "-q:v", "2", tmp_path,
                ],
                capture_output=True,
                timeout=60,
                check=False,
            )
            if result.returncode == 0 and Path(tmp_path).stat().st_size > 0:
                break

        if not Path(tmp_path).exists() or Path(tmp_path).stat().st_size == 0:
            print(f"  warn: ffmpeg não gerou frame para {src}")
            return None

        Image.open(tmp_path).save(poster_path, "WEBP", quality=85, method=6)
        print(f"  generated poster {poster_path.relative_to(ROOT)}")
        return poster_name
    except Exception as exc:
        print(f"  warn: não foi possível gerar poster para {src}: {exc}")
        return None
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


def resolve_video_poster(slug: str, src: str, poster_setting: str | None, video_index: int) -> str | None:
    if poster_setting and poster_setting != "auto":
        return poster_setting

    if not should_auto_poster(slug, poster_setting, video_index):
        return None

    poster_name = default_poster_filename(src)
    poster_path = ROOT / "assets" / "cases" / slug / poster_name
    if poster_path.exists() and poster_path.stat().st_size > 0:
        return poster_name

    return generate_poster_from_video(slug, src)


def video_poster_attr(slug: str, poster: str | None) -> str:
    if not poster:
        return ""
    return f' poster="../assets/cases/{slug}/{esc(poster)}"'


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
            parts.append('<span class="inline-block w-[2px] h-[2px] rounded-full bg-[#ffffff] shrink-0"></span>')
        parts.append(f'<p class="text-[16px] text-[#ffffff]">{esc(service)}</p>')
    inner = "\n                ".join(parts)
    return f"""            <div class="flex flex-col gap-[4px]">
              <p class="text-[16px] font-[STIX_Two_Text_Italic] text-[#ffffff]/40">Serviços</p>
              <div class="flex flex-row flex-wrap items-center gap-[12px]">
                {inner}
              </div>
            </div>"""


def before_after_slider_block(slug: str, name: str, before: str, after: str) -> str:
    return f"""          <div class="flex flex-col items-stretch gap-[12px]">
            <div class="flex flex-col relative ba-container overflow-hidden w-[100%] aspect-[16/9] rounded-[4px] border-solid border-[#000000]/10 border-[1.5px]">
              <img class="object-cover absolute inset-0 w-full h-full ba-before" loading="lazy" src="../assets/cases/{slug}/{esc(before)}" alt="Logo antes — {esc(name)}" />
              <img class="object-cover absolute inset-0 w-full h-full ba-after" loading="lazy" src="../assets/cases/{slug}/{esc(after)}" alt="Logo depois — {esc(name)}" />
              <div class="flex flex-col ba-slider"></div>
            </div>
            <div class="flex flex-row items-center justify-between">
              <p class="text-[#171717]/40 text-[12px] font-[600]">ANTES</p>
              <p class="text-[#171717]/40 text-[12px] font-[600]">DEPOIS</p>
            </div>
          </div>"""


def approved_logo_block(slug: str, name: str, after: str) -> str:
    return f"""          <div class="grid-cols-[repeat(2,_1fr)] gap-[4px] flex flex-row">
            <div class="flex flex-col gap-[12px] w-[100%]">
              <div class="flex flex-col items-center border-solid border-[#171717]/10 rounded-[4px] border-[1.5px] overflow-hidden w-[100%] aspect-[16/9]">
                <img class="w-[100%] object-cover h-full" loading="lazy" src="../assets/cases/{slug}/{esc(after)}" alt="Alternativa aprovada — {esc(name)}" />
              </div>
              <p class="text-[#171717]/40 text-[12px] font-[600]">ALTERNATIVA APROVADA</p>
            </div>
          </div>"""


def visual_strategy_section(case: dict) -> str:
    assets = case["assets"]
    before = assets.get("logoBefore")
    after = assets.get("logoAfter")
    if not after:
        return ""

    slug = case["slug"]
    name = case.get("name") or slug
    blocks = []

    # Rebrand: logo antiga + logo nova → slider antes/depois
    if before and after:
        blocks.append(before_after_slider_block(slug, name, before, after))
    # Branding do zero: só logo nova → alternativa aprovada
    elif after:
        blocks.append(approved_logo_block(slug, name, after))

    if not blocks:
        return ""

    inner = "\n".join(blocks)
    return f"""      <hr class="border-t-[1px] border-[#000000]/20 bg-[#000000]/10 opacity-[50%]" />
      <div class="mr-auto ml-auto w-full flex flex-col w-[100%] max-w-[1280px] mr-[auto] ml-[auto] pr-[32px] pl-[32px] max-md:pl-[0px] max-md:pr-[0px]">
        <div class="flex flex-col gap-[24px]">
          <h2 class="leading-[1.1] tracking-[-0.01em] font-[STIX_Two_Text_Italic] font-[400] text-[24px] text-[#171717]">Estratégia Visual</h2>
{inner}
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


def mockups_header_section(case: dict) -> str:
    mockups = case.get("mockups") or []
    if not mockups:
        return ""
    return """      <hr class="border-t-[1px] border-[#000000]/20 bg-[#000000]/10 opacity-[50%]" />
      <div class="mr-auto ml-auto w-full flex flex-col w-[100%] max-w-[1280px] mr-[auto] ml-[auto] pr-[32px] pl-[32px] max-md:pl-[0px] max-md:pr-[0px]">
        <div class="flex flex-col gap-[16px]">
          <h2 class="leading-[1.1] tracking-[-0.01em] font-[STIX_Two_Text_Italic] font-[400] text-[24px] text-[#171717]">Materiais Produzidos</h2>
        </div>
      </div>"""


def mockups_gallery_section(case: dict) -> str:
    mockups = case.get("mockups") or []
    if not mockups:
        return ""
    slug = case["slug"]
    name = case.get("name") or slug
    items = []
    for index, filename in enumerate(mockups, start=1):
        alt = f"Mockup {index} — {name}"
        items.append(
            f"""          <div class="flex flex-col mockup-item">
            <img class="mockup-image w-[100%] object-cover" loading="lazy" src="../assets/cases/{slug}/{esc(filename)}" alt="{esc(alt)}" />
          </div>"""
        )
    inner = "\n".join(items)
    return f"""    <section class="flex flex-col w-[100%] items-center pt-[0px] pb-[0px]" id="mockup-section">
      <div class="flex flex-col w-[100%] items-stretch" id="collection-wrapper">
        <div class="flex flex-col gap-[1rem] w-[100%] overflow-visible" id="mockup-collection">
{inner}
        </div>
      </div>
    </section>"""


def audiovisual_section(case: dict) -> str:
    videos = normalize_vertical_videos(case.get("verticalVideos") or [])
    if not videos:
        return ""
    slug = case["slug"]
    blocks = []
    for index, video in enumerate(videos):
        filename = video["src"]
        poster_file = resolve_video_poster(slug, filename, video.get("poster"), index)
        poster = video_poster_attr(slug, poster_file)
        blocks.append(
            f"""            <div class="flex flex-col gap-[12px] w-[100%] items-center">
              <div class="flex flex-col rounded-[12px] overflow-hidden border-solid border-[1.5px] border-[#000000]/10">
                <video class="w-full aspect-[16/9] overflow-hidden object-cover h-[600px]" preload="metadata" controls src="../assets/cases/{slug}/{esc(filename)}"{poster}></video>
              </div>
            </div>"""
        )
    inner = "\n".join(blocks)
    return f"""      <hr class="border-t-[1px] border-[#000000]/20 bg-[#000000]/10 opacity-[50%]" />
      <div class="mr-auto ml-auto w-full flex flex-col w-[100%] max-w-[1280px] mr-[auto] ml-[auto] pr-[32px] pl-[32px] max-md:pl-[0px] max-md:pt-[0px] max-md:pr-[0px] max-md:pb-[0px]">
        <div class="flex flex-col gap-[24px]">
          <h2 class="leading-[1.1] tracking-[-0.01em] font-[STIX_Two_Text_Italic] font-[400] text-[24px] text-[#171717]">Audiovisual</h2>
          <div class="flex flex-row gap-[24px] max-md:flex max-md:flex-col">
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


CASE_ARROW_SVG = """<svg width="11" height="11" viewBox="0 0 11 11" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M9.34375 0C9.75 0 10.0938 0.34375 10.0938 0.75V8.25C10.0938 8.6875 9.75 9 9.34375 9C8.90625 9 8.59375 8.6875 8.59375 8.25V2.5625L1.375 9.78125C1.0625 10.0938 0.59375 10.0938 0.3125 9.78125C0 9.5 0 9.03125 0.3125 8.75L7.53125 1.53125H1.84375C1.40625 1.53125 1.09375 1.1875 1.09375 0.78125C1.09375 0.34375 1.40625 0.03125 1.84375 0.03125H9.34375V0Z" fill="white"/></svg>"""


def case_cta_next(slug: str, ordered_slugs: list[str], cases_by_slug: dict[str, dict]) -> str:
    link = "../cases.html"
    label = "Explorar cases"
    aria = "Ver todos os cases"
    if slug in ordered_slugs and len(ordered_slugs) > 1:
        nxt = ordered_slugs[(ordered_slugs.index(slug) + 1) % len(ordered_slugs)]
        if nxt != slug:
            nxt_case = cases_by_slug.get(nxt) or {}
            name = nxt_case.get("name") or nxt
            link = f"{esc(nxt)}.html"
            label = f"Próximo: {name}"
            aria = f"Ver case {name}"
    return f"""              <a href="{link}" class="case-cta case-cta--small case-cta-secondary no-underline focus:outline-none" aria-label="{esc(aria)}">
                <span>{esc(label)}</span>
              </a>"""


def case_cta_row(slug: str, ordered_slugs: list[str], cases_by_slug: dict[str, dict]) -> str:
    primary = """              <a href="../contato.html" class="case-cta case-cta--small case-cta-primary no-underline focus:outline-none" aria-label="Fale conosco">
                <span>fale conosco</span>
              </a>"""
    secondary = case_cta_next(slug, ordered_slugs, cases_by_slug)
    return f"""            <div class="case-cta-row case-cta-row--small">
{primary}
{secondary}
            </div>"""


def render_case(case: dict, ordered_slugs: list[str], cases_by_slug: dict[str, dict]) -> str:
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
        "{{MOCKUPS_SECTION}}": mockups_header_section(case),
        "{{MAIN_FILM_SECTION}}": main_film_section(case),
        "{{MOCKUPS_GALLERY_SECTION}}": mockups_gallery_section(case),
        "{{AUDIOVISUAL_SECTION}}": audiovisual_section(case),
        "{{RESULTS_HTML}}": results_html(case.get("results") or []),
        "{{TESTIMONIAL_SECTION}}": testimonial_section(case),
        "{{CASE_CTA_ROW}}": case_cta_row(slug, ordered_slugs, cases_by_slug),
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
    return f"""          <div class="flex-none snap-center">
            <a href="{prefix}cases/{slug}.html" class="case-card-link block no-underline">
            <div class="case-card h-[400px] relative overflow-hidden border-solid border-[#000000]/10 border-[1.5px] flex flex-row items-end rounded-[12px]">
              <div class="case-card-bg" style="background-image:url(/assets/cases/{slug}/{esc(hero)})" aria-hidden="true"></div>
              <div class="case-card-scrim" aria-hidden="true"></div>
              <span class="case-card-arrow" aria-hidden="true">{CASE_ARROW_SVG}</span>
              <div class="case-card-body flex flex-col w-[100%] pt-[24px] pr-[24px] pb-[24px] pl-[24px] relative z-[5] gap-[8px]">
                <h2 class="leading-[1.1] tracking-[-0.01em] text-[#ffffff] text-[24px] font-[DM_Sans_9pt_Regular] font-[400]">{esc(title)}</h2>
                <p class="text-[#ffffff]/60 text-[12px] w-[60%]">{esc(excerpt)}</p>
              </div>
            </div>
            </a>
          </div>"""


def featured_case_html(case: dict, prefix: str = "") -> str:
    slug = case["slug"]
    title = case.get("name") or slug
    excerpt = case.get("cardText") or ""
    if len(excerpt) > 100:
        excerpt = excerpt[:97] + "…"
    return f"""          <a href="{prefix}cases/{slug}.html" class="hero-featured-card no-underline" aria-label="Ver case {esc(title)}">
            <span class="hero-featured-arrow" aria-hidden="true">{CASE_ARROW_SVG}</span>
            <p class="hero-featured-label font-[STIX_Two_Text_Italic]">Case em destaque</p>
            <div class="hero-featured-copy">
              <p class="hero-featured-title font-[DM_Sans_9pt_Regular]">{esc(title)}</p>
              <p class="hero-featured-excerpt">{esc(excerpt)}</p>
            </div>
          </a>"""


def remove_stale_featured(content: str) -> str:
    pattern = re.compile(
        r"(<!-- CASES_FEATURED_END -->)\s*<a href=\"cases/[^\"]+\.html\" class=\"(?:gap-\[1rem\]|hero-featured-card)[^\"]*\".*?</a>\s*",
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
    cases_by_slug = {c["slug"]: c for c in cases}

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    for case in cases:
        slug = case["slug"]
        out_path = ROOT / "cases" / f"{slug}.html"
        out_path.write_text(render_case(case, ordered_slugs, cases_by_slug), encoding="utf-8")
        print(f"built cases/{slug}.html")

    update_listings(cases)
    print("done")


if __name__ == "__main__":
    main()
