from __future__ import annotations

import pytest

from config import load_settings


def test_development_defaults_are_safe_and_usable():
    settings = load_settings({})
    assert settings.app_env == "development"
    assert settings.secret_key
    assert settings.mail_backend == "console"
    assert settings.reset_token_ttl_minutes == 30


def test_production_requires_secret_and_mailjet():
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        load_settings({"APP_ENV": "production"})

    with pytest.raises(RuntimeError, match="MAIL_BACKEND"):
        load_settings({"APP_ENV": "production", "SECRET_KEY": "secret"})


def test_production_accepts_complete_configuration():
    settings = load_settings(
        {
            "APP_ENV": "production",
            "SECRET_KEY": "secret",
            "MAIL_BACKEND": "mailjet",
            "MAILJET_API_KEY": "key",
            "MAILJET_API_SECRET": "secret",
            "MAIL_FROM": "sender@example.com",
        }
    )
    assert settings.is_production
    assert settings.flask_config()["SESSION_COOKIE_SECURE"] is True


@pytest.mark.parametrize("value", ["0", "-1", "not-a-number"])
def test_reset_ttl_must_be_positive(value):
    with pytest.raises(RuntimeError, match="RESET_TOKEN_TTL_MINUTES"):
        load_settings({"RESET_TOKEN_TTL_MINUTES": value})
