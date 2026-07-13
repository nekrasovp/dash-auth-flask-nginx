"""Authentication and account-management operations."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import timedelta

from email_validator import EmailNotValidError, validate_email
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from extensions import db
from models import PasswordResetToken, User, utcnow

MIN_PASSWORD_LENGTH = 12


class AuthError(Exception):
    """Base class for expected account errors."""


class ValidationError(AuthError):
    """Raised when user-provided data is invalid."""


class DuplicateEmailError(AuthError):
    """Raised when an account already owns an email address."""


class InvalidCredentialsError(AuthError):
    """Raised when a credential check fails."""


class InvalidResetTokenError(AuthError):
    """Raised when a reset token is invalid, expired, or already used."""


@dataclass(frozen=True)
class ResetRequest:
    user: User
    raw_token: str
    record: PasswordResetToken


def normalize_email(value: str | None) -> str:
    if not value:
        raise ValidationError("Enter a valid email address.")
    try:
        result = validate_email(value.strip(), check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValidationError("Enter a valid email address.") from exc
    return result.normalized.lower()


def normalize_name(value: str | None, label: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValidationError(f"{label} is required.")
    if len(cleaned) > 100:
        raise ValidationError(f"{label} must be 100 characters or fewer.")
    return cleaned


def validate_password(password: str | None) -> str:
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    return password


def get_user_by_email(email: str | None) -> User | None:
    try:
        normalized = normalize_email(email)
    except ValidationError:
        return None
    return db.session.scalar(select(User).where(User.email == normalized))


def create_user(
    first_name: str | None,
    last_name: str | None,
    email: str | None,
    password: str | None,
) -> User:
    user = User(
        first_name=normalize_name(first_name, "First name"),
        last_name=normalize_name(last_name, "Last name"),
        email=normalize_email(email),
        password_hash="",
    )
    user.set_password(validate_password(password))
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise DuplicateEmailError("An account already uses that email.") from exc
    except SQLAlchemyError:
        db.session.rollback()
        raise
    return user


def authenticate(email: str | None, password: str | None) -> User:
    user = get_user_by_email(email)
    if user is None or not password or not user.check_password(password):
        raise InvalidCredentialsError("Invalid email or password.")
    return user


def update_profile(user: User, first_name: str | None, last_name: str | None) -> User:
    user.first_name = normalize_name(first_name, "First name")
    user.last_name = normalize_name(last_name, "Last name")
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
    return user


def change_password(
    user: User,
    current_password: str | None,
    new_password: str | None,
) -> None:
    if not current_password or not user.check_password(current_password):
        raise InvalidCredentialsError("Current password is incorrect.")
    user.set_password(validate_password(new_password))
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise


def _token_hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_reset_request(
    email: str | None,
    ttl_minutes: int,
) -> ResetRequest | None:
    """Create a reset token, or return None without revealing account existence."""

    user = get_user_by_email(email)
    if user is None:
        return None

    now = utcnow()
    active_tokens = db.session.scalars(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
    )
    for token in active_tokens:
        token.used_at = now

    raw_token = secrets.token_urlsafe(32)
    record = PasswordResetToken(
        user=user,
        token_hash=_token_hash(raw_token),
        expires_at=now + timedelta(minutes=ttl_minutes),
    )
    db.session.add(record)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
    return ResetRequest(user=user, raw_token=raw_token, record=record)


def discard_reset_request(reset_request: ResetRequest) -> None:
    try:
        db.session.delete(reset_request.record)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise


def find_active_reset_token(raw_token: str | None) -> PasswordResetToken | None:
    if not raw_token:
        return None
    record = db.session.scalar(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == _token_hash(raw_token))
    )
    return record if record is not None and record.is_active else None


def redeem_reset_token(raw_token: str | None, new_password: str | None) -> User:
    record = find_active_reset_token(raw_token)
    if record is None:
        raise InvalidResetTokenError(
            "This reset link is invalid or has expired. Request a new one."
        )

    record.user.set_password(validate_password(new_password))
    record.used_at = utcnow()
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
    return record.user
