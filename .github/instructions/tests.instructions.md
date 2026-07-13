---
applyTo: "dash-auth-flask/tests/**/*.py,.github/workflows/**/*.yml"
---

- Keep warnings treated as errors.
- Use deterministic data and isolated temporary SQLite databases.
- Dispose SQLAlchemy engines in tests to avoid Python 3.13 resource warnings.
- Cover successful behavior and security-sensitive failure paths without relying on external mail or data services.
- Browser tests must check console logs and use stable IDs or accessible labels.
