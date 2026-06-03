# Dois Intelligence — site estático

Site marketing exportado do YCode, publicado via **GitHub Pages** com domínio customizado.

## Preview local

```bash
python3 -m http.server 8080
```

Abra [http://localhost:8080](http://localhost:8080).

## Baixar mídia e fontes

Se faltar imagem ou fonte:

```bash
python3 download_from_manifest.py
python3 download_fonts_from_manifest.py
```

## Remover lixo do export YCode

Remove assets não usados no HTML, páginas 401/500 e atualiza o manifest:

```bash
python3 prune_unused_assets.py
```

## Otimizar HTML (CSS/JS compartilhados)

Extrai Tailwind, fontes e scripts repetidos para `assets/shared/`, e deixa `blog.html` / `404.html` leves:

```bash
python3 optimize_html.py
```

Depois de re-exportar do YCode, rode de novo `optimize_html.py` (e `fix_site.py` se precisar das correções de links).

## Cases (CMS fake em JSON)

Conteúdo dos cases em `data/cases/`. Edite o JSON e regenere as páginas:

```bash
python3 build_cases.py
```

Isso gera `cases/{slug}.html` (páginas irmãs) e atualiza os grids em `cases.html` e `index.html`. Ver [`data/cases/README.md`](data/cases/README.md).

## Aplicar correções no HTML

Remove artefatos do export YCode (classes inválidas, SVG de seta corrompido, IDs duplicados, links quebrados, SEO, WhatsApp, etc.):

```bash
python3 fix_site.py
```

Fluxo recomendado após editar cases ou re-exportar:

```bash
python3 build_cases.py && python3 fix_site.py
```

## GitHub Pages

1. Push deste repositório para o GitHub (branch `main`, raiz do repo).
2. **Settings → Pages →** Deploy from branch `main`, pasta `/ (root)`.
3. Domínio: o arquivo [`CNAME`](CNAME) aponta para `doisintelligence.com.br`.
4. No registrador do domínio, configure os registros DNS conforme a [documentação do GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site).
5. Ative **Enforce HTTPS** após a propagação do DNS.

## Formulários

Enquanto não houver backend, os formulários redirecionam para o WhatsApp. Para usar Formspree ou Web3Forms, altere o `action` dos `<form>` em `index.html` e `contato.html`.
