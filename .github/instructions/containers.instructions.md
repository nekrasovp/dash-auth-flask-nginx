---
applyTo: "**/Dockerfile,docker-compose*.yml,nginx/**/*.conf"
---

- Keep the application image on Python 3.13 slim and the runtime user non-root.
- Keep one Gunicorn worker with threads while SQLite is the default.
- Preserve health checks, the named SQLite volume, and Nginx-only production exposure.
- Trust one proxy hop and forward host, client IP, protocol, and port headers consistently.
- Validate both Compose models and rebuild the affected image after changes.
