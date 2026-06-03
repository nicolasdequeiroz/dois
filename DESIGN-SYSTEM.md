# Dois Intelligence — Design System (referência para IA)

Documento derivado do site estático em produção (`index.html`, `cases/`, `metodologia.html`, `contato.html` e CSS em `assets/shared/`). Use este arquivo como **fonte única de verdade** ao criar novas seções, páginas ou componentes — mantenha consistência visual, tipográfica e técnica com o que já existe.

**Como usar com IA:** inclua este arquivo no contexto (ex.: `@DESIGN-SYSTEM.md` no Cursor) ou cole trechos relevantes no prompt. Ao pedir uma nova seção, cite o tipo de seção (hero escura, bloco claro, card de case, etc.).

---

## 1. Marca e personalidade visual

| Aspecto | Diretriz |
|--------|----------|
| **Setor** | Branding e marketing para **negócios imobiliários** (construtoras, incorporadoras, imobiliárias). |
| **Tom** | Consultoria premium, estratégica, confiante — sem exagero “startup colorida”. |
| **Estética** | Monocromática com **fotografia arquitetônica** em alto contraste (preto e branco / tons neutros). Superfícies escuras com texto branco; seções claras com texto `#171717`. |
| **Sensação** | Arquitetura, solidez, inteligência de mercado — “marca à altura da engenharia”. |
| **Logo** | Wordmark **DOIS** em SVG branco no header (`assets/shared/navigation--logo.svg`); versão escura em `assets/library/dois-black-1.svg` (favicon). |
| **Idioma** | **pt-BR**. Títulos em sentence case ou frases completas; UI e navegação frequentemente em **MAIÚSCULAS** com tracking largo. |

---

## 2. Paleta de cores

### Cores sólidas principais

| Nome | Hex | Uso |
|------|-----|-----|
| Texto corpo (claro) | `#333333` | Wrapper padrão do `<body>` em páginas claras. |
| Preto editorial | `#171717` | Títulos e texto em fundos brancos; botão primário de formulário; cards de dor. |
| Cinza seção escura | `#1e1e1e` | Bloco “Metodologia Intelligence” (3 pilares). |
| Cinza footer / nav | `#333333` | Footer e fundo translúcido da navbar (`#333333` com opacidade). |
| Branco | `#ffffff` | Texto sobre fotos/escuro; fundos de card interno; intro overlay. |
| Preto puro | `#000000` | Overlay em heroes de case (`/60`); botão flutuante WhatsApp. |

### Branco e preto com opacidade (padrão Tailwind no HTML)

Sobre **fundos escuros ou fotos**:
- Texto principal: `#ffffff`
- Subtítulo / apoio: `#ffffff/60`, `#ffffff/80`, `#ffffff/75`
- Eyebrow (STIX): `#ffffff/40` ou `opacity-[40%]` no elemento
- Vidro / painéis: `bg-[#ffffff]/5`, `/10`, `/20` + `backdrop-blur-[8px]` ou `[10px]`

Sobre **fundos claros**:
- Texto secundário: `#171717/60`
- Fundos suaves: `#171717/5` (blocos, ícones)
- Bordas: `border-[#000000]/10` com `border-[1.5px]`

### Formulários (seções claras)

| Elemento | Valor |
|----------|--------|
| Label | `#404040`, 14px, `font-medium` |
| Input texto | `#171717`, 14px |
| Fundo input | `bg-[#d4d4d4]/10` |
| Borda | `border-[#737373]/[0.15]`, focus `border-[#737373]/20` |
| Placeholder | `#a8a8a8` |
| Botão enviar | `bg-[#171717]`, texto `#FFFFFF`, `rounded-[999px]`, uppercase, `tracking-[0.05em]`, altura ~42px |

### Feedback (formulário)

- Erro: fundo `#fee2e2`, texto `#991b1b`
- Sucesso: fundo `#d1fae5`, texto `#065f46`

### Variáveis Ycode (legado — preferir hex explícito em código novo)

O export do Ycode referencia tokens sem definição no CSS atual:
- `--f53a5a83-1585-4ee8-9cad-d1da78881835` → tratar como **texto branco** (`#ffffff`) no botão “Contato” da nav.
- `--9187beaa-0cd5-40b8-8d66-8527181f7d22` → tratar como **acento escuro** (`#333333` ou `#171717`) nos bullets do marquee.

Em HTML/CSS novo, **não criar** novos UUIDs de cor; use hex direto como no restante do site.

---

## 3. Tipografia

### Famílias (arquivos em `/fonts/`, carregadas em `assets/shared/fonts.css`)

| Família | Classe utilitária | Papel |
|---------|-------------------|--------|
| **DM Sans 9pt Regular** | `font-dm-sans-9pt-regular` / `font-[DM_Sans_9pt_Regular]` | Títulos, corpo, UI, botões, navegação. Pesos no HTML: 400 (normal), 600, 700 (bold). |
| **STIX Two Text Italic** | `font-stix-two-text-italic` / `font-[STIX_Two_Text_Italic]` | *Eyebrows*, legendas editoriais, títulos de seção em cases, frases de destaque em cards escuros. |
| **Inter** | (reservado / formulários) | Disponível no projeto; labels de form usam sobretudo DM Sans medium via utilitários. |

### Hierarquia de tamanhos (desktop → mobile `max-md`)

| Elemento | Desktop | Mobile |
|----------|---------|--------|
| Intro animada | 60px | 48px |
| Hero H1 | 64px, `leading-[1.15]` | 42px |
| Hero eyebrow (STIX) | 24px | 20px |
| Hero parágrafo | 20px, max-width ~400px | 16px, largura total |
| H2 seção principal | 48px, `tracking-[-0.025em]`, `leading-[1.1]` | 32px |
| H2 bloco “Fale com a…” | 42px, palavras separadas em `<h2>` | igual / wrap |
| Eyebrow de seção | 18px STIX, `opacity-[40%]`, `mb-[12px]` | igual |
| Corpo claro | 16px, `leading-[1.5]` | 14px em alguns blocos de metodologia |
| Corpo escuro (card) | 18px STIX + 14px apoio | — |
| Nav links | 12px, **uppercase**, `tracking-[0.1em]` | igual |
| Marquee | 30px, **bold**, uppercase, `opacity-[40%]` | — |
| Título card case | 24px | — |
| H2 página de case | 24px STIX italic | — |
| Footer copyright | 14px, `#ffffff/60` | — |

### Regras tipográficas

1. **Eyebrow antes do título:** sempre `<span>` com STIX Two Text Italic, 18px, opacidade reduzida, margem inferior 12px. Ex.: “Dois Intelligence”, “Nossos Cases”, “Metodologia Intelligence”, “Para quem é?”.
2. **Títulos grandes:** DM Sans, peso normal (400), tracking negativo leve (`-0.025em` ou `-0.01em`).
3. **Ênfase editorial:** STIX italic em frases curtas dentro de cards escuros — não substituir o H2 principal.
4. **Botões e CTAs:** DM Sans, **uppercase**, sem serif.

---

## 4. Espaçamento, grid e layout

### Container

```html
<div class="mr-auto ml-auto w-full flex flex-col w-[100%] max-w-[1280px] mr-[auto] ml-[auto] pr-[32px] pl-[32px]">
```

- Largura máxima conteúdo: **1280px**
- Padding interno horizontal: **32px** (`max-md:pl-[0px] max-md:pr-[0px]` quando a seção já tem padding lateral)
- Seções usam padding lateral de viewport: **`pl-[5%] pr-[5%]`**

### Ritmo vertical de seções

| Padrão | Valores típicos |
|--------|-----------------|
| Seção padrão | `pt-[120px] pb-[120px]` ou `pt-[140px] pb-[140px]` |
| Seção menor / footer | `pt-[80px] pb-[80px]` |
| Hero | `h-[100vh]`, `pt-[80px] pb-[80px]` |
| Metodologia (fullscreen) | `h-[100vh]` por etapa |
| Gap entre blocos internos | 16px, 24px, 48px |
| Grid 2 colunas | `grid-cols-[repeat(2,_1fr)] gap-[24px]` → coluna única no mobile |

### Navbar

- `fixed`, `z-[100]`, `pt-[16px] pb-[16px]`
- Capsule: `max-w-[1000px]`, `rounded-[9999px]`, `backdrop-blur-[10px]`, `bg-[#333333]/30`, padding `pl-[24px] pr-[8px] py-[8px]`
- Logo: largura **100px**
- Links: gap **32px**, opacidade 60% → 100% no hover
- Botão Contato: pill branco translúcido `bg-[#ffffff]/20`, texto 12px bold uppercase

### Footer

- Fundo `#333333`, mesma estrutura de container 1280px
- Links nav: iguais ao header (12px uppercase branco 60%)
- `hr`: `border-[#d1d5db] opacity-[10%]`

### WhatsApp flutuante

- `fixed`, `z-[999]`, `bottom-[64px]`, `right-[24px]`
- Círculo **80×80px**, `bg-[#000000]`, `rounded-[999px]`
- Ícone: `assets/shared/zap.svg`

---

## 5. Componentes

### 5.1 Botão primário CTA (`#bttn`)

Padrão usado na hero e seções escuras:

- Formato **pill**: `rounded-[9999px]`
- `bg-[#ffffff]/10`, `text-[#ffffff]`, `backdrop-blur-[8px]`
- Texto: uppercase, 16px, semibold
- Padding: `pl-[20px] pr-[8px] py-[8px]`, gap 10px
- **Bloco seta:** círculo 36px `bg-[#ffffff]/10` com ícone SVG (`assets/home/hero-text-bttn-arrow-block-image.svg`)
- Efeitos extras em `assets/shared/index-extra.css`: glare no hover, rotação -45° da seta

### 5.2 Botão nav “Contato”

- Pill menor, `w-[100px]`, `bg-[#ffffff]/20`, 12px bold uppercase
- Cor do texto: branco (`#ffffff`)

### 5.3 Botão submit (formulário)

- `bg-[#171717]`, texto branco, `rounded-[999px]`, `h-[42px]`, `pl-[32px] pr-[32px]`, uppercase tracking 0.05em

### 5.4 Botão secundário (cases)

- `bg-[#e5e5e5]`, texto `#171717`, 14px, pill

### 5.5 Card de case (listagem)

- Altura **400px**, `rounded-[12px]`, `bg-cover bg-center`
- Borda `1.5px solid #000000/10`
- Imagem de fundo: `style="background-image:url(/assets/cases/...)"` (sempre caminho **absoluto desde a raiz** `/assets/...`)
- Texto sobre imagem: branco; título 24px; descrição 12px `#ffffff/60`
- Overlay opcional: div absoluta full-bleed com `bg-[image:var(--bg-img)]` herdado

### 5.6 Card “Em destaque” (hero)

- `rounded-[12px]`, `backdrop-blur-[10px]`, `bg-[#ffffff]/5`
- Thumb 120×80px, `rounded-[8px]`, `object-cover`
- Label “Em destaque”: STIX 16px `#ffffff/40`

### 5.7 Lista de dores / benefícios (fundo claro)

- Container externo: `bg-[#171717]/5`, `rounded-[24px]`, padding 24px (16px mobile)
- Linha: ícone em quadrado `bg-[#171717]/5` `rounded-[8px]` + cartão branco `rounded-[8px]` com texto 18px weight 600

### 5.8 Cards “3 pilares” (fundo `#1e1e1e`)

- Grid 3 colunas (`max-lg:2`, `max-md:1`)
- Card: `rounded-[12px]`, `backdrop-blur-[10px]`, `bg-[#ffffff]/5`, altura ~450px (380px mobile)
- Label do pilar: uppercase 18px extrabold branco
- Texto: STIX 18px `/80` + apoio 14px `/60`

### 5.9 Marquee (`#marquee`)

- Faixa horizontal, uppercase bold 30px, opacidade 40%
- Separadores: bolinhas 8px entre palavras-chave (marketing, branding, leads…)

### 5.10 Hero de página de case

- `pt-[200px]`, imagem de fundo fixa `bg-fixed bg-cover`
- Overlay: `bg-[#000000]/60` em tela cheia
- Metadados: STIX para rótulos (`Segmento`, `Duração`), valores em DM Sans 16px branco

### 5.11 Inputs

- Altura 38px, `rounded-[12px]`, padding horizontal 16px
- Sem sombra; focus apenas borda levemente mais escura

---

## 6. Modos de seção (templates)

Use um destes “modos” ao pedir novas seções à IA:

### A — Hero fotográfica (escura)

- `h-[100vh]`, foto full-bleed, texto branco alinhado à esquerda
- `--bg-img: url(/assets/...)` + classes `bg-cover bg-[image:var(--bg-img)]`
- Navbar e CTA `#bttn` por cima (`z-index` adequado)

### B — Seção clara editorial

- Fundo branco implícito, texto `#171717`
- Grid 2 colunas: copy à esquerda (~90% ou 60% largura), componente à direita
- Eyebrow STIX + H2 DM Sans 42–48px

### C — Seção escura estrutural

- `bg-[#1e1e1e]`, texto branco, cards vidro `/5`

### D — Fullscreen storytelling (metodologia)

- `h-[100vh]`, imagem de fundo, conteúdo ancorado **embaixo** (`items-end`)
- Largura do texto ~60% desktop
- Variante mobile: `--bg-img-mobile` com `max-md:bg-[image:var(--bg-img-mobile)]`

### E — Página de case (longform)

- Hero com overlay escuro
- Corpo branco, H2 de seção em STIX italic 24px `#171717`
- Separadores `hr` com `border-[#000000]/20`
- Mídia com bordas `1.5px`, cantos `rounded-[4px]` ou `[12px]`

### F — Contato / formulário

- Mesmo padrão “Fale com a…” (palavras + logo inline `contato.svg`)
- Form em coluna, `gap-[24px]`, largura total dos campos

---

## 7. Imagens e mídia

| Regra | Detalhe |
|-------|---------|
| **Estilo** | Arquitetura contemporânea, céu dramático, PB ou dessaturado; sensação “premium imobiliário”. |
| **Formato** | `.webp` para fotos; `.svg` para ícones e logo. |
| **Hero / fundos** | `background-size: cover`, `background-position: center` (ou `right-top` no mobile quando necessário). |
| **URLs em CSS** | Sempre **`/assets/...`** (raiz do site). Nunca `url(assets/...)` sem barra inicial — quebra quando o CSS está em `assets/shared/`. |
| **Variável** | `--bg-img: url(/assets/caminho/arquivo.webp)` no `style` do elemento. |
| **Lazy load** | `loading="lazy"` em imagens abaixo da dobra. |
| **Logo** | Não distorcer; larguras fixas (100px nav, 24px footer). |

---

## 8. Motion e interação

| Recurso | Uso |
|---------|-----|
| **GSAP** | Intro da home (`assets/shared/hero-intro.js`): overlay branco, texto “Marcas fortes são” → buraco com mesma foto da hero → revela conteúdo. |
| **Lenis** | Scroll suave global (`lenis-init.js`). |
| **Hover nav** | Opacidade 60% → 100%. |
| **CTA `#bttn`** | Glare + leve `translateY` + rotação da seta (CSS). |
| **Imagens flutuantes** | Classes `.concrete-img.is-1` / `.is-2` com keyframes em `index-extra.css` (se usar elementos decorativos). |
| **Scroll navbar** | Script inline reduz border-radius da capsule no scroll (ver `index.html`). |

Novas páginas **fora da home** normalmente **não** repetem a intro GSAP — apenas hero estática ou sem overlay.

---

## 9. Stack técnico e convenções

| Item | Padrão do projeto |
|------|-------------------|
| HTML | Estático, sem build; Tailwind **v4** pré-compilado em `assets/shared/tailwind.css` |
| CSS global | `fonts.css` → `tailwind.css` → `base.css` → `index-extra.css` / `case-extra.css` conforme a página |
| JS | `hero-intro.js`, `lenis-init.js`, `mobile-menu.js`, `slider.js`; GSAP via CDN no `<head>` apenas onde necessário |
| Breakpoints | `max-md:` (<768px), `max-lg:` — seguir padrões já usados no HTML vizinho |
| Links | `no-underline` em botões e cards clicáveis; `focus:outline-none` nos links de nav |
| Acessibilidade | `alt` em logos; `aria-label="WhatsApp"` no FAB |
| Domínio | `doisintelligence.com.br` (referência SEO em canonicals) |

### Checklist rápido — nova página

- [ ] `<html lang="pt-BR">` + meta title/description
- [ ] CSS shared linkado na ordem correta
- [ ] Navbar id `#site-navbar` idêntica às outras páginas (ajustar `href` relativos em `cases/`)
- [ ] Container `max-w-[1280px]` + padding 32px
- [ ] Eyebrow STIX + título DM Sans
- [ ] Cores conforme modo de seção (claro vs escuro)
- [ ] Fundos com `/assets/...`
- [ ] Footer `#333333` + FAB WhatsApp
- [ ] Formulários apontando para WhatsApp se for CTA de contato (padrão atual)

---

## 10. Copy e nomenclatura recorrentes

- Marca: **Dois Intelligence**
- Metodologia: **Metodologia Intelligence**
- Pilares: **Branding**, **Marketing**, **Audiovisual**
- CTA principal: **Fale conosco** / **enviar**
- Nav: **Cases**, **Metodologia**, **Contato**, **Home**, **Blog**
- Público: construtoras, incorporadoras, incorporadores, mercado imobiliário

---

## 11. Arquivos de referência no repositório

| Arquivo | Conteúdo |
|---------|----------|
| `index.html` | Referência completa: hero, marquee, cases, dores, pilares, contato, footer |
| `metodologia.html` | Seções fullscreen com foto |
| `cases/trifold.html` | Estrutura longform de case |
| `assets/shared/index-extra.css` | Hover do CTA e animações decorativas |
| `assets/shared/fonts.css` | @font-face |
| `fix_site.py` | Correções pós-export (links, SEO, URLs de fundo) |

---

*Última atualização: junho de 2026 — alinhado ao site estático pós-otimização (GitHub Pages).*
