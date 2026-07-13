---
applyTo: "dash-auth-flask/**/*.py"
---

- Target Python 3.13 and follow the Ruff configuration in `dash-auth-flask/pyproject.toml`.
- Prefer small typed service functions, SQLAlchemy 2 style queries, explicit commits, and rollbacks on write failures.
- Keep Flask request/session concerns at page or server boundaries; keep reusable authentication behavior in `services/`.
- Use domain exceptions for expected failures and structured logging for operational failures.
- Add pytest coverage for validation, persistence, security boundaries, and regressions.
