# Contributing

## Working on the docs

The documentation site is built with [MkDocs](https://www.mkdocs.org/) and the
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme,
configured in `mkdocs.yml`. Content lives under `docs/`.

```bash
just sync         # install runtime + docs dependencies (uv)
just docs-serve   # http://localhost:8000 with live reload
just docs-build   # mkdocs build --strict
```

Before opening a pull request that touches the docs, run `just docs-build`.
For Compose changes, also run `just config`. CI runs both checks.

## CI and publishing

- **`.github/workflows/ci.yml`** — on pushes and pull requests: strict MkDocs
  build + `docker compose config` against `env.sample`.
- **`.github/workflows/docs.yml`** — on push to `main`: build and deploy to
  GitHub Pages (`upload-pages-artifact` + `deploy-pages`).

Merged docs changes go live at the URL in `site_url` inside `mkdocs.yml`.

**One-time repo setup:** GitHub → Settings → Pages → Build and deployment →
Source = **GitHub Actions**. Until that is set, the workflow builds but does not
publish.

## Pull request expectations

- Keep [Roadmap](roadmap.md) / `refactor-plan.md` in sync with what you finish.
- Treat `refactor.md` as the full architecture decision record and
  [Decisions](developer/decisions.md) as its concise published summary.
- Match existing page tone: task-oriented User Guide, implementation-detail
  Developer Guide.
- Prefer updating an existing page over adding a new one unless the topic is
  distinct.
