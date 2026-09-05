# AGENTS.md - Synkra AIOX (Codex CLI)

Este arquivo define as instruções do projeto para o Codex CLI. Equivalente ao `.claude/CLAUDE.md`, usado pelo Codex.

<!-- AIOX-MANAGED-START: core -->
## Core Rules

1. Siga a Constitution em `.aiox-core/constitution.md`
2. Trabalhe por stories em `docs/stories/` quando houver trabalho de desenvolvimento estruturado
3. Não invente requisitos fora dos artefatos existentes
4. Este é um site estático (sem build step de aplicação) — mudanças em HTML/CSS/JS são diretas, sem compilação
<!-- AIOX-MANAGED-END: core -->

<!-- AIOX-MANAGED-START: quality -->
## Quality Gates

Projeto sem `package.json` na raiz (sem lint/typecheck/test via npm). Antes de concluir uma tarefa:

- Rode `python3 fix_site.py` após editar/gerar HTML (corrige artefatos do export YCode, links, SEO, WhatsApp floater)
- Rode `python3 build_cases.py` se alterou conteúdo em `data/cases/`
- Valide manualmente no browser: `python3 -m http.server 8080`
- Atualize checklist e File List da story antes de concluir (quando houver story ativa)
<!-- AIOX-MANAGED-END: quality -->

<!-- AIOX-MANAGED-START: codebase -->
## Project Map

- Core framework: `.aiox-core/`
- Site estático: raiz do repo (`index.html`, `cases/`, `contato/`, `metodologia/`, `blog/`, `obrigado/`)
- Assets: `assets/`, `fonts/`
- Conteúdo de cases (CMS fake em JSON): `data/cases/`
- Scripts de manutenção: `build_cases.py`, `fix_site.py`, `optimize_html.py`, `prune_unused_assets.py`, `download_from_manifest.py`, `download_fonts_from_manifest.py`
- Stories (quando existirem): `docs/stories/`
- Deploy: GitHub Pages, branch `main`, domínio custom via `CNAME` (`doisintelligence.com`)
<!-- AIOX-MANAGED-END: codebase -->

<!-- AIOX-MANAGED-START: commands -->
## Common Commands

- `python3 -m http.server 8080` — preview local
- `python3 build_cases.py && python3 fix_site.py` — regenerar páginas de cases + aplicar correções
- `python3 optimize_html.py` — extrair CSS/JS compartilhado para `assets/shared/` após re-export do YCode
- `python3 prune_unused_assets.py` — remover assets não usados e atualizar manifest
<!-- AIOX-MANAGED-END: commands -->

<!-- AIOX-MANAGED-START: shortcuts -->
## Agent Shortcuts

Preferência de ativação no Codex CLI:

1. Use `/skills` e selecione `aiox-<agent-id>` vindo de `.codex/skills` (ex.: `aiox-architect`)
2. Se preferir, use os atalhos abaixo (`@architect`, `/architect`, etc.)

Interprete os atalhos abaixo carregando o arquivo correspondente em `.aiox-core/development/agents/` (fallback: `.codex/agents/`), renderize o greeting via `generate-greeting.js` e assuma a persona até `*exit`:

- `@architect`, `/architect`, `/architect.md` -> `.aiox-core/development/agents/architect.md`
- `@dev`, `/dev`, `/dev.md` -> `.aiox-core/development/agents/dev.md`
- `@qa`, `/qa`, `/qa.md` -> `.aiox-core/development/agents/qa.md`
- `@pm`, `/pm`, `/pm.md` -> `.aiox-core/development/agents/pm.md`
- `@po`, `/po`, `/po.md` -> `.aiox-core/development/agents/po.md`
- `@sm`, `/sm`, `/sm.md` -> `.aiox-core/development/agents/sm.md`
- `@analyst`, `/analyst`, `/analyst.md` -> `.aiox-core/development/agents/analyst.md`
- `@devops`, `/devops`, `/devops.md` -> `.aiox-core/development/agents/devops.md`
- `@data-engineer`, `/data-engineer`, `/data-engineer.md` -> `.aiox-core/development/agents/data-engineer.md`
- `@ux-design-expert`, `/ux-design-expert`, `/ux-design-expert.md` -> `.aiox-core/development/agents/ux-design-expert.md`
- `@squad-creator`, `/squad-creator`, `/squad-creator.md` -> `.aiox-core/development/agents/squad-creator.md`
- `@aiox-master`, `/aiox-master`, `/aiox-master.md` -> `.aiox-core/development/agents/aiox-master.md`
<!-- AIOX-MANAGED-END: shortcuts -->
