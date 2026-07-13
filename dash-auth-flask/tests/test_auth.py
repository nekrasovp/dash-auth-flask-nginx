from __future__ import annotations

from datetime import timedelta

import pytest
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models import PasswordResetToken, User, utcnow
from services.auth import (
    DuplicateEmailError,
    InvalidCredentialsError,
    InvalidResetTokenError,
    ValidationError,
    authenticate,
    change_password,
    create_reset_request,
    create_user,
    get_user_by_email,
    normalize_email,
    redeem_reset_token,
    update_profile,
)


def make_user():
    return create_user("Ada", "Lovelace", "ADA@Example.COM", "correct-horse-battery")


def test_email_normalization_and_validation(app_context):
    assert normalize_email("  ADA@Example.COM ") == "ada@example.com"
    with pytest.raises(ValidationError):
        normalize_email("not an email")


def test_create_authenticate_and_reject_duplicate(app_context):
    user = make_user()
    assert user.email == "ada@example.com"
    assert user.password_hash != "correct-horse-battery"
    assert authenticate("ada@example.com", "correct-horse-battery").id == user.id

    with pytest.raises(InvalidCredentialsError):
        authenticate("ada@example.com", "wrong password")
    with pytest.raises(DuplicateEmailError):
        make_user()


def test_password_and_profile_validation(app_context):
    user = make_user()
    with pytest.raises(ValidationError, match="12"):
        change_password(user, "correct-horse-battery", "short")
    with pytest.raises(InvalidCredentialsError):
        change_password(user, "wrong-current", "a-new-secure-password")

    change_password(user, "correct-horse-battery", "a-new-secure-password")
    assert authenticate(user.email, "a-new-secure-password").id == user.id

    update_profile(user, "  Grace ", " Hopper ")
    assert (user.first_name, user.last_name) == ("Grace", "Hopper")


def test_reset_unknown_email_is_indistinguishable(app_context):
    assert create_reset_request("unknown@example.com", 30) is None
    assert db.session.query(PasswordResetToken).count() == 0


def test_reset_request_does_not_change_password_and_is_single_use(app_context):
    user = make_user()
    request = create_reset_request(user.email, 30)
    assert request is not None
    assert user.check_password("correct-horse-battery")
    assert request.record.token_hash != request.raw_token

    redeemed = redeem_reset_token(request.raw_token, "replacement-password")
    assert redeemed.check_password("replacement-password")
    assert request.record.used_at is not None
    with pytest.raises(InvalidResetTokenError):
        redeem_reset_token(request.raw_token, "another-replacement")


def test_new_reset_request_revokes_previous_token(app_context):
    user = make_user()
    first = create_reset_request(user.email, 30)
    second = create_reset_request(user.email, 30)
    assert first is not None and second is not None
    assert first.record.used_at is not None
    with pytest.raises(InvalidResetTokenError):
        redeem_reset_token(first.raw_token, "replacement-password")
    redeem_reset_token(second.raw_token, "replacement-password")


def test_expired_reset_token_is_rejected(app_context):
    user = make_user()
    request = create_reset_request(user.email, 30)
    assert request is not None
    request.record.expires_at = utcnow() - timedelta(seconds=1)
    db.session.commit()
    with pytest.raises(InvalidResetTokenError):
        redeem_reset_token(request.raw_token, "replacement-password")


def test_database_commit_failure_rolls_back(app_context, monkeypatch):
    rolled_back = False

    def fail_commit():
        raise SQLAlchemyError("forced failure")

    def record_rollback():
        nonlocal rolled_back
        rolled_back = True

    monkeypatch.setattr(db.session, "commit", fail_commit)
    monkeypatch.setattr(db.session, "rollback", record_rollback)
    with pytest.raises(SQLAlchemyError):
        create_user("Ada", "Lovelace", "ada@example.com", "correct-horse-battery")
    assert rolled_back


def test_lookup_invalid_email_returns_none(app_context):
    make_user()
    assert get_user_by_email("invalid") is None
    assert db.session.scalar(db.select(User).where(User.email == "ada@example.com"))
