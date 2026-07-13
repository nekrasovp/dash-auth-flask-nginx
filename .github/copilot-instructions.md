# Repository instructions

- Read and follow the root `AGENTS.md` before changing code. It is the primary repository contract.
- Use the root `Makefile` commands instead of inventing setup or validation commands.
- Preserve the Dash Pages + Flask-Login + Flask-SQLAlchemy + SQLite + Gunicorn + Nginx architecture unless the issue explicitly changes scope.
- Keep authentication failures generic, reset tokens hashed and single-use, writes transactional, and secrets/runtime databases out of Git.
- Add or update tests for behavior changes. Treat warnings, missing callback IDs, browser console errors, inaccessible labels, and broken mobile layouts as failures.
- Run `make check` before handoff. Run `make test-browser` and verify both themes and responsive navigation for UI, routing, or authentication changes.
- Keep PRs focused, document user/developer impact, and update README/configuration examples when the public contract changes.
