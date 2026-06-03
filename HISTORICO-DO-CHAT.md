# Histórico do trabalho — site Dois Intelligence

Documento consolidado de tudo o que foi feito nesta conversa (e continuações), para referência ao mover o projeto ou retomar o trabalho com outra IA.

**Projeto:** site estático exportado do YCode em `/Users/nicolasazevedo/Documents/Dois`  
**Domínio alvo:** `doisintelligence.com.br` (GitHub Pages)  
**Estado no fim do chat:** ajustes locais prontos; usuário pediu para **não publicar no Git ainda**

---

## 1. Objetivo geral

Preparar o site **Dois Intelligence** para GitHub Pages com domínio customizado, corrigir problemas do export YCode, reduzir peso do repositório, externalizar CSS/JS repetido, documentar o design system e implementar um **CMS fake em JSON** para os cases — sem backend, sem build Node, mantendo HTML estático.

---

## 2. Fase 1 — GitHub Pages e correções pós-export

### Scripts criados ou usados

| Script | Função |
|--------|--------|
| `download_from_manifest.py` | Baixa mídia do `assets-manifest.json` (sem depender do backup `.ycode`) |
| `download_fonts_from_manifest.py` | Baixa fontes (STIX, DM Sans, Inter) |
| `fix_site.py` | Correções globais no HTML exportado |

### O que `fix_site.py` faz

- Links `_case-template` → `cases/*.html`
- Converte elementos clicáveis em `<a>` reais (logo, footer, WhatsApp, CTAs)
- Extrai/corrige slider corrompido pelo YCode
- Formulários → redirecionamento WhatsApp
- SEO: title, description, canonical, Open Graph
- `CNAME` para `doisintelligence.com.br`
- `blog.html` como página “Em breve”
- URLs de fundo em **caminho absoluto** `/assets/...` (ver bug da hero, seção 4)
- Grids de cases passaram a ser gerados por `build_cases.py` (seção 7)

### Outros arquivos

- `.gitignore`, `README.md`, `CNAME`
- Git inicializado (commit inicial ~99 arquivos); push/`gh` não concluído pelo usuário

---

## 3. Fase 2 — Limpeza de “lixo” YCode

### Script: `prune_unused_assets.py`

Removeu **~130,5 MB** de assets não referenciados no HTML:

- Quase todo `assets/mockups/` (~68 MB)
- Quase todo `assets/library/` (ficou só `dois-black-1.svg`)
- `assets/icons/`, duplicatas, mídia Yarden não usada
- Páginas `401-password.html`, `500.html`

**Resultado:** `assets/` caiu de ~192 MB para **~61 MB** (~27 arquivos usados no HTML na época).

**Bug corrigido:** primeira versão do prune tinha lógica invertida no manifest; restaurado do git e filtrado de novo.

---

## 4. Fase 3 — Otimização HTML

### Script: `optimize_html.py`

Extraiu CSS/JS repetido para `assets/shared/`:

| Arquivo | Conteúdo |
|---------|----------|
| `fonts.css` | @font-face |
| `tailwind.css` | Tailwind v4 compilado (~34 KB, uma cópia) |
| `base.css` | Lenis, resets |
| `index-extra.css`, `case-extra.css`, `case-anim.css` | Estilos por tipo de página |
| `lenis-init.js`, `mobile-menu.js`, `hero-intro.js` | Scripts compartilhados |
| `slider.js` | Carrossel de cases |

- `blog.html` e `404.html` ficaram leves (~1 KB)
- `index.html` encolheu muito (ex.: ~128 KB → ~36 KB após dedupe)

### `dedupe_scripts.py` / função em `optimize_html.py`

Remove scripts inline duplicados (Lenis, menu, hero) que o export repetia 2–3× por página.

**Workflow pós re-export YCode:** rodar `fix_site.py` e `optimize_html.py` de novo.

---

## 5. Bug corrigido — hero sem imagem de fundo

### Sintoma

Após externalizar o Tailwind, a foto do `#hero` sumia (fundo branco/vazio).

### Causa

O hero usa `background-image: var(--bg-img)` definido em `assets/shared/tailwind.css`. Com `--bg-img: url(assets/home/...)` no HTML, o navegador resolvia o `url()` **em relação ao CSS** (`assets/shared/`), gerando:

`assets/shared/assets/home/...` → 404.

### Correção

URLs de fundo passaram a ser **absolutas na raiz do site**: `/assets/...`

Arquivos afetados: `index.html`, `metodologia.html`, `cases.html`, `cases/trifold.html`, `cases/yarden.html`.

Função `fix_root_relative_background_urls()` adicionada em `fix_site.py` para reaplicar após re-export.

### Nota sobre a intro

A intro branca (“Marcas fortes são”) é normal por alguns segundos (`hero-intro.js` + GSAP). Depois a overlay some e a hero aparece.

---

## 6. Design system documentado

Criado **`DESIGN-SYSTEM.md`** na raiz — referência para IA e para novas seções:

- Personalidade da marca (premium, imobiliário, monocromático)
- Paleta (`#333333`, `#171717`, `#1e1e1e`, brancos com opacidade, formulários)
- Tipografia (DM Sans + STIX Two Text Italic), escala desktop/mobile
- Layout (container 1280px, padding 5%/32px)
- Componentes (navbar pill, CTA `#bttn`, cards, footer, WhatsApp)
- Templates de seção (hero escura, bloco claro, metodologia fullscreen, case longform)
- Regra `/assets/...` para imagens de fundo
- Checklist para páginas novas

**Uso com IA:** incluir `@DESIGN-SYSTEM.md` no prompt ao criar conteúdo ou layout.

---

## 7. CMS fake para Cases (JSON + build estático)

### Problema

- `cases/trifold.html` e `cases/yarden.html` eram páginas irmãs (~400 linhas) com **textos vazios** (campos da coleção YCode não hidrataram no export)
- Listagens em `index.html`, `cases.html` e `fix_site.py` tinham Trifold/Yarden **hardcoded**
- Escalar para N cases exigia duplicar HTML manualmente

### Solução implementada

**Fonte de verdade:** JSON editável + template HTML + script de build.

```
data/cases/
  index.json          ← lista (slug, order, featured, published)
  trifold.json        ← conteúdo completo
  yarden.json         ← estrutura pronta, textos vazios
  README.md           ← documentação dos campos

cases/
  _template.html      ← layout único (placeholders {{...}})

build_cases.py        ← “publicar”
assets/shared/case-page.js  ← slider antes/depois, big numbers, vídeos
```

### Campos JSON (espelho do YCode)

Metadados e hero: `name`, `slug`, `cardText`, `segment`, `duration`, `services[]`, `headline`, `intro[]`, `assets.heroImage`

Corpo: `challenge[]`, `strategicDecision[]`, `appliedStrategy[]`, `assets.logoBefore/After`, `assets.mainFilm`, `mockups[]`, `verticalVideos[]`

Resultados: `results[]` (`value` + `label`), `testimonial` (`quote`, `name`, `role`), `assets.clientPhoto`

SEO: `seo.title`, `seo.description`

Listagem: em `index.json`, `featured: true` define o case “Em destaque” na home.

### Comando

```bash
python3 build_cases.py
```

Gera:

- `cases/{slug}.html` para cada case publicado
- Grid entre `<!-- CASES_GRID_START -->` e `<!-- CASES_GRID_END -->` em `cases.html` e `index.html`
- Bloco featured entre `<!-- CASES_FEATURED_START -->` e `<!-- CASES_FEATURED_END -->` na home

### Trifold

Preenchido com dados dos prints do YCode (headline, contexto, desafio, decisão, logos, estratégia, vídeos, depoimento Alexandre Nicolau, big numbers 87% / +7K / 3x).

**Pendências Trifold:**

- `mockups[]` vazio — mockups foram removidos na limpeza de assets; recolocar arquivos em `assets/cases/trifold/` e listar no JSON
- `filmePrincipal` vazio no YCode — seção omitida até haver arquivo
- `duration` vazio — coluna oculta no template

### Yarden

JSON criado com assets existentes (hero + 3 vídeos); **textos ainda vazios** — aguarda conteúdo do YCode ou edição manual.

### Novo case (fluxo)

1. Entrada em `data/cases/index.json`
2. Copiar `trifold.json` → `{slug}.json`
3. Mídia em `assets/cases/{slug}/`
4. `python3 build_cases.py`

---

## 8. Pendências conhecidas (não resolvidas no chat)

### Conteúdo

- Cases Yarden (e outros) sem copy no JSON
- Mockups Trifold ausentes no disco
- Galeria mockup no HTML original dependia de JS/assets removidos

### HTML / export YCode

- `index.html` tinha **80 `<div>` abertos e 79 fechados** (malformação reportada; não corrigido neste chat)
- Classes corrompidas pontuais (`rounded-&lt;svg...`) — parcialmente tratadas em scripts
- Re-export YCode pode reintroduzir Tailwind inline duplicado

### Deploy

- Push GitHub Pages e DNS do domínio não feitos (por pedido do usuário)
- `gh` não estava disponível no ambiente na fase inicial

### Formulários

- Redirecionam para WhatsApp; Formspree/Web3Forms não configurados

---

## 9. Scripts úteis — ordem sugerida

```bash
# Preview local
python3 -m http.server 8080

# Baixar mídia/fontes (se faltar)
python3 download_from_manifest.py
python3 download_fonts_from_manifest.py

# Limpar assets não usados (cuidado: irreversível)
python3 prune_unused_assets.py

# Correções globais pós-export
python3 fix_site.py

# Externalizar CSS/JS
python3 optimize_html.py

# Regenerar cases a partir do JSON
python3 build_cases.py
```

Após **re-export do YCode:** rodar `fix_site.py`, `optimize_html.py` e `build_cases.py`.

---

## 10. Arquivos de referência importantes

| Arquivo | Para quê |
|---------|-----------|
| `DESIGN-SYSTEM.md` | Identidade visual / prompts de IA |
| `data/cases/README.md` | Schema do CMS fake |
| `data/cases/trifold.json` | Exemplo completo de case |
| `cases/_template.html` | Layout de página de case |
| `build_cases.py` | Gerador de cases e listagens |
| `fix_site.py` | Correções pós-export |
| `optimize_html.py` | Dedupe CSS/JS |
| `README.md` | Visão geral do repo |

---

## 11. Decisões de arquitetura (resumo)

1. **Site 100% estático** — compatível com GitHub Pages, sem Node no deploy.
2. **JSON + build Python** para cases — SEO (HTML estático), URLs estáveis (`/cases/{slug}.html`), fácil de editar com IA.
3. **YCode** — útil para re-exportar **template** de layout; conteúdo do dia a dia fica no JSON.
4. **URLs `/assets/...`** — obrigatório para fundos quando CSS está em `assets/shared/`.
5. **Não commitar** até o usuário pedir — trabalho local contínuo.

---

*Documento gerado para transferência de contexto. Atualize datas e pendências conforme o projeto evoluir.*
