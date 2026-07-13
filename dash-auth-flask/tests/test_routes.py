from __future__ import annotations

import pytest
from flask_login import current_user

from app import logout, server
from extensions import db
from models import PasswordResetToken
from pages.auth_pages import forgot_password as forgot_page
from pages.auth_pages.login import sign_in
from pages.auth_pages.register import register
from services.auth import create_user
from services.mail import MailDeliveryError
from ui import safe_next_path


@pytest.fixture()
def integration_database():
    with server.app_context():
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        ("/analytics", "/analytics"),
        ("/profile?section=password", "/profile?section=password"),
        ("https://example.com/steal", "/"),
        ("//example.com/steal", "/"),
        ("profile", "/"),
        ("/login", "/"),
    ],
)
def test_safe_next_destination(candidate, expected):
    assert safe_next_path(candidate) == expected


@pytest.mark.parametrize(
    ("legacy_path", "current_path"),
    [
        ("/home", "/"),
        ("/page1", "/analytics"),
        ("/forgot", "/forgot-password"),
        ("/change", "/reset-password"),
    ],
)
def test_legacy_routes_redirect(legacy_path, current_path):
    response = server.test_client().get(legacy_path)
    assert response.status_code == 301
    assert response.headers["Location"].endswith(current_path)


def test_registration_signs_in_and_logout_is_button_driven(integration_database):
    with server.test_request_context("/register"):
        alert, redirect = register(
            1,
            "Ada",
            "Lovelace",
            "ADA@example.com",
            "correct-horse-battery",
            "correct-horse-battery",
        )
        assert alert is not None
        assert redirect == "/"
        assert current_user.is_authenticated

        assert logout([1, 0]) == "/login"
        assert not current_user.is_authenticated


def test_login_uses_sanitized_next_and_generic_failure(integration_database):
    create_user("Ada", "Lovelace", "ada@example.com", "correct-horse-battery")

    with server.test_request_context("/login"):
        alert, redirect = sign_in(
            1,
            None,
            "ada@example.com",
            "wrong-password",
            "https://example.com/steal",
        )
        assert "Invalid email or password" in alert.children
        assert redirect is not None
        assert not current_user.is_authenticated

    with server.test_request_context("/login?next=/analytics"):
        _alert, redirect = sign_in(
            1,
            None,
            "ada@example.com",
            "correct-horse-battery",
            "/analytics",
        )
        assert redirect == "/analytics"
        assert current_user.is_authenticated


def test_reset_delivery_failure_discards_live_token(
    integration_database,
    monkeypatch,
):
    create_user("Ada", "Lovelace", "ada@example.com", "correct-horse-battery")

    def fail_delivery(*_args, **_kwargs):
        raise MailDeliveryError("forced failure")

    monkeypatch.setattr(forgot_page, "send_password_reset", fail_delivery)
    with server.test_request_context("/forgot-password", base_url="http://localhost"):
        response = forgot_page.request_password_reset(1, "ada@example.com")
        assert forgot_page.GENERIC_MESSAGE in response.children
        assert db.session.query(PasswordResetToken).count() == 0
