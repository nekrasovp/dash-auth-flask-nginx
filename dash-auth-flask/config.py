"""Environment-backed application configuration."""

from __future__ import annotations

import logging
import os
import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

LOGGER = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE_URL = f"sqlite:///{BASE_DIR / 'instance' / 'users.db'}"
VALID_ENVIRONMENTS = {"development", "test", "production"}
VALID_MAIL_BACKENDS = {"console", "mailjet"}


@dataclass(frozen=True)
class Settings:
    """Validated runtime settings."""

    app_env: str
    secret_key: str
    database_url: str
    mail_backend: str
    mailjet_api_key: str
    mailjet_api_secret: str
    mail_from: str
    reset_token_ttl_minutes: int
    demo_user_email: str
    demo_user_password: str
    demo_user_first_name: str
    demo_user_last_name: str
    seed_demo_user: bool

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def flask_config(self) -> dict[str, object]:
        return {
            "SECRET_KEY": self.secret_key,
            "SQLALCHEMY_DATABASE_URI": self.database_url,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SESSION_COOKIE_HTTPONLY": True,
            "SESSION_COOKIE_SAMESITE": "Lax",
            "SESSION_COOKIE_SECURE": self.is_production,
            "REMEMBER_COOKIE_HTTPONLY": True,
            "REMEMBER_COOKIE_SAMESITE": "Lax",
            "REMEMBER_COOKIE_SECURE": self.is_production,
            "MAIL_BACKEND": self.mail_backend,
            "MAILJET_API_KEY": self.mailjet_api_key,
            "MAILJET_API_SECRET": self.mailjet_api_secret,
            "MAIL_FROM": self.mail_from,
            "RESET_TOKEN_TTL_MINUTES": self.reset_token_ttl_minutes,
        }


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _positive_int(value: str, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if parsed <= 0:
        raise RuntimeError(f"{name} must be greater than zero")
    return parsed


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Load settings and reject unsafe production configuration."""

    env = environ if environ is not None else os.environ
    app_env = env.get("APP_ENV", "development").strip().lower()
    if app_env not in VALID_ENVIRONMENTS:
        raise RuntimeError(f"APP_ENV must be one of {', '.join(sorted(VALID_ENVIRONMENTS))}")

    secret_key = env.get("SECRET_KEY", "").strip()
    if app_env == "production" and not secret_key:
        raise RuntimeError("SECRET_KEY is required when APP_ENV=production")
    if not secret_key:
        secret_key = secrets.token_hex(32)
        LOGGER.warning(
            "SECRET_KEY is unset; using an ephemeral development key. "
            "Sessions will reset when the process restarts."
        )

    mail_backend = env.get("MAIL_BACKEND", "console").strip().lower()
    if mail_backend not in VALID_MAIL_BACKENDS:
        raise RuntimeError(f"MAIL_BACKEND must be one of {', '.join(sorted(VALID_MAIL_BACKENDS))}")

    mailjet_api_key = env.get("MAILJET_API_KEY", "").strip()
    mailjet_api_secret = env.get("MAILJET_API_SECRET", "").strip()
    mail_from = env.get(
        "MAIL_FROM", "" if app_env == "production" else "no-reply@example.com"
    ).strip()
    if app_env == "production":
        if mail_backend != "mailjet":
            raise RuntimeError("MAIL_BACKEND must be mailjet in production")
        missing = [
            name
            for name, value in (
                ("MAILJET_API_KEY", mailjet_api_key),
                ("MAILJET_API_SECRET", mailjet_api_secret),
                ("MAIL_FROM", mail_from),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(f"Missing production mail settings: {', '.join(missing)}")

    return Settings(
        app_env=app_env,
        secret_key=secret_key,
        database_url=env.get("DATABASE_URL", DEFAULT_DATABASE_URL).strip(),
        mail_backend=mail_backend,
        mailjet_api_key=mailjet_api_key,
        mailjet_api_secret=mailjet_api_secret,
        mail_from=mail_from,
        reset_token_ttl_minutes=_positive_int(
            env.get("RESET_TOKEN_TTL_MINUTES", "30"),
            "RESET_TOKEN_TTL_MINUTES",
        ),
        demo_user_email=env.get("DEMO_USER_EMAIL", "demo@example.com").strip(),
        demo_user_password=env.get("DEMO_USER_PASSWORD", "dash-demo-password"),
        demo_user_first_name=env.get("DEMO_USER_FIRST_NAME", "Demo").strip(),
        demo_user_last_name=env.get("DEMO_USER_LAST_NAME", "User").strip(),
        seed_demo_user=_as_bool(env.get("SEED_DEMO_USER")),
    )
