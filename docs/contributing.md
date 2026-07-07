# Contributing

## Working on the docs

The documentation site is built with [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme, configured in `mkdocs.yml` at the repo root. All content lives under `docs/`.

```bash
make install      # one-time: install uv (https://docs.astral.sh/uv/)
make sync         # install runtime + docs dependencies
make docs-serve   # serve locally at http://localhost:8000 with live reload
```

Before opening a pull request that touches the docs, run:

```bash
make docs-build   # builds with mkdocs build --strict, failing on broken links/refs
```

Every page has an "Edit this page" link (via `edit_uri` in `mkdocs.yml`) that takes you straight to the source file on GitHub.

## Publishing

Pushing to `main` triggers `.github/workflows/docs.yml`, which builds the site and deploys it to GitHub Pages via the official Pages Actions pipeline (`upload-pages-artifact` + `deploy-pages`). Merged docs changes go live automatically at the URL in `site_url` inside `mkdocs.yml`.

**One-time repo setup:** in GitHub → Settings → Pages, set **Build and deployment → Source** to **GitHub Actions** (not the `gh-pages` branch). Until that is set, the workflow builds successfully but nothing is published.

`make docs-deploy` still exists for a manual deploy to the legacy `gh-pages` branch if you ever need to publish outside of CI.

## Pull request expectations

- Keep the [Roadmap](roadmap.md) up to date: if you fix a known issue listed there, remove it (or move it to done); if you find a new one, add it.
- Match the tone and structure of the existing pages — task-oriented for the User Guide, implementation-detail-oriented for the Developer Guide.
- Prefer updating an existing page over adding a new one unless the topic is genuinely distinct.
