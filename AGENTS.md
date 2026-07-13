# Repository agent guide

## Mission

Maintain this repository as a small, polished starter for authenticated Dash applications. Preserve the intentionally narrow stack: Dash Pages on Flask, Flask-Login, Flask-SQLAlchemy, SQLite, Gunicorn, Docker Compose, and Nginx.

This file is the primary operating contract for coding agents. `.github/copilot-instructions.md` and the path-specific files under `.github/instructions/` add GitHub Copilot context but must not contradict this guide.

## Start here

1. Read `README.md` for the product and runtime contract.
2. Read `CONTRIBUTING.md` for the delivery workflow.
3. Run `git status -sb` and preserve unrelated work.
4. Inspect the nearest relevant source and tests before editing.
5. Use the root `Makefile` as the canonical command interface.

## Repository map

| Path | Responsibility |
| --- | --- |
| `dash-auth-flask/server.py` | Flask configuration, extensions, health endpoint, and CLI commands |
| `dash-auth-flask/app.py` | Dash application shell and global callbacks |
| `dash-auth-flask/pages/` | Dash Pages layouts and page-level callbacks |
| `dash-auth-flask/services/` | Authentication and mail use cases |
| `dash-auth-flask/models.py` | SQLAlchemy models and password hashing |
| `dash-auth-flask/config.py` | Environment parsing and production validation |
| `dash-auth-flask/assets/` | Responsive CSS and visual tokens |
| `dash-auth-flask/tests/` | Unit, integration, and browser tests |
| `docker-compose*.yml` | Production-like and development orchestration |
| `nginx/` | Reverse proxy image and configuration |
| `.github/` | CI, dependency updates, templates, and agent instructions |

## Invariants

- Keep public routes limited to `/login`, `/register`, `/forgot-password`, and `/reset-password` plus the custom 404.
- Keep `/`, `/analytics`, and `/profile` protected and preserve sanitized local `next` redirects.
- Logout must remain a user-triggered POST-style Dash callback, never a GET side effect.
- Passwords require at least 12 characters and use Werkzeug `scrypt` hashes.
- Reset tokens remain random, hashed, single-use, revocable, and expiring. Reset requests must not reveal whether an email exists.
- Require the current password before an authenticated password change.
- Use SQLAlchemy 2 style APIs, explicit commits, and rollbacks on write failures.
- Never commit runtime databases, `.env`, credentials, reset tokens, or fixed production secrets.
- Demo seeding stays explicit, development-only, and disabled by default.
- SQLite and `db.create_all()` are deliberate starter constraints. Do not introduce PostgreSQL, Alembic, Redis, or external services without an explicit scope change.
- Keep Gunicorn at one worker with threads while SQLite is the default.
- Trust exactly one proxy hop and preserve production cookie/security settings.

## Canonical commands

Run these from the repository root:

```bash
make setup            # create .env if missing and install development dependencies
make lint             # Ruff rules and formatting check
make test             # non-browser pytest suite
make test-browser     # Chrome/Chromium Dash smoke test
make compose-config   # validate production and development Compose models
make check            # lint, tests, and Compose validation
make up               # production-like stack on :8000
make dev              # hot reload on :8050 plus Nginx on :8000
make down             # stop containers without deleting SQLite data
```

Do not hand-edit generated caches or runtime database files. Use `apply_patch` for source edits and let formatters perform only mechanical rewrites.

## Validation matrix

| Change | Minimum validation |
| --- | --- |
| Python logic or models | `make lint test` |
| Authentication or reset flow | `make lint test` plus focused browser verification |
| Dash layout, callbacks, or CSS | `make lint test` and `make test-browser`; inspect desktop/mobile and light/dark |
| Docker, Compose, or Nginx | `make compose-config`, image build, and `/healthz` through Nginx |
| Dependencies | `make check` and rebuild affected images |
| Documentation/templates only | Markdown/YAML review and `make compose-config` when runtime examples change |

Treat warnings as errors. A missing callback ID, browser console error, broken legacy redirect, duplicate heading, or inaccessible form label is a release blocker.

## Change discipline

- Keep changes cohesive and avoid unrelated refactors.
- Add or update tests for behavior changes and regression fixes.
- Update `README.md`, `.env.example`, templates, and screenshots when their contract changes.
- Preserve deterministic sample analytics data unless the task explicitly introduces a backend.
- Prefer typed domain errors and structured logging; avoid bare exception handlers.
- Keep user-facing authentication failures generic.
- For UI work, verify at 1440×900 and 390×844, in light and dark themes.

## Pull request handoff

Before handing off:

1. Run the validation required by the matrix.
2. Review `git diff --check` and the full staged diff.
3. Confirm no secrets or runtime data are staged.
4. Fill in the PR template with impact, security notes, and exact checks.
5. Use labels that describe type and area; do not use labels as a substitute for a clear title.
6. Default to a draft PR until CI is green and the visual/security review is complete.
