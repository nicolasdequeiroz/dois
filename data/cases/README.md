# Cases — CMS fake (JSON)

Edite os JSON aqui e rode `python3 build_cases.py` na raiz do projeto.

## Arquivos

| Arquivo | Função |
|---------|--------|
| `index.json` | Lista de cases publicados (`slug`, `order`, `featured`) |
| `{slug}.json` | Conteúdo completo de cada case |
| `../cases/_template.html` | Layout HTML (não editar por case) |
| `../../build_cases.py` | Gera `cases/{slug}.html` + grids em `cases.html` e `index.html` |

## Campos (espelho do YCode)

### Metadados e hero
- `name`, `slug`
- `cardText` — texto do card na listagem
- `segment`, `duration`, `services[]`
- `headline` — headline principal
- `intro[]` — contexto inicial (parágrafos)
- `assets.heroImage` — imagem principal (arquivo em `assets/cases/{slug}/`)

### Corpo
- `challenge[]` — Desafio
- `strategicDecision[]` — Decisão Estratégica
- `appliedStrategy[]` — Processo / Estratégia aplicada
- `assets.logoBefore`, `assets.logoAfter` — slider antes/depois
- `assets.mainFilm` — filme principal (opcional)
- `mockups[]` — grid de mockups (nomes de arquivo)
- `verticalVideos[]` — conteúdos verticais (audiovisual)

### Resultados
- `results[]` — `{ "value": "87%", "label": "..." }` (vira big numbers)
- `testimonial` — `{ quote, name, role }` + `assets.clientPhoto`

### SEO e listagem
- `seo.title`, `seo.description`
- Em `index.json`: `featured: true` define o case em destaque na home

## Novo case

1. Adicionar entrada em `index.json`
2. Criar `{slug}.json` (copiar `trifold.json` como base)
3. Colocar mídia em `assets/cases/{slug}/`
4. `python3 build_cases.py`
