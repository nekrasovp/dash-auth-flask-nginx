# Contributing

Thanks for improving the Dash authentication starter. Changes should keep the project understandable enough to learn from while maintaining secure defaults.

## Development workflow

1. Create a branch from `main` using `agent/<description>`, `feature/<description>`, or `fix/<description>`.
2. Run `make setup` once to create the local environment.
3. Make a focused change and add tests alongside it.
4. Run `make check`. Run `make test-browser` for UI, routing, or authentication changes.
5. Update documentation, screenshots, and `.env.example` when the public contract changes.
6. Open a draft pull request and complete the repository template.

The complete repository contract and validation matrix live in [AGENTS.md](AGENTS.md). These instructions apply equally to human contributors and coding agents.

## Useful commands

```bash
make help
make setup
make lint
make test
make test-browser
make compose-config
make up
make dev
make down
```

`make down` keeps the named SQLite volume. Use `make clean-data` only when you intentionally want to delete local user data.

## Pull requests

- Keep the title outcome-focused and the diff cohesive.
- Explain user/developer impact, security implications, and any migration steps.
- Include screenshots for visible changes.
- Link issues with `Closes #…` when the change fully resolves them.
- Do not commit `.env`, SQLite databases, credentials, live reset tokens, or generated caches.

Pull requests start as drafts. They are ready for review when CI is green, the checklist is complete, and any UI change has been checked on desktop and mobile in both themes.

## Issue and label conventions

Use the issue forms for reproducible bugs and scoped feature requests. Apply one type label (`bug`, `enhancement`, `documentation`, `maintenance`, or `security`) and relevant area labels (`area: ui`, `area: auth`, `area: infrastructure`, or `area: developer-experience`). Dependency automation uses `dependencies` plus an ecosystem label.

## Security reports

Do not disclose vulnerabilities in a public issue. Follow [SECURITY.md](SECURITY.md).
