"""Password-reset mail delivery adapters."""

from __future__ import annotations

import logging
from html import escape

from flask import current_app
from mailjet_rest import Client

from models import User

LOGGER = logging.getLogger(__name__)


class MailDeliveryError(RuntimeError):
    """Raised when an email provider rejects a message."""


def send_password_reset(user: User, reset_url: str) -> None:
    backend = current_app.config["MAIL_BACKEND"]
    ttl_minutes = current_app.config["RESET_TOKEN_TTL_MINUTES"]
    if backend == "console":
        if current_app.debug or current_app.config.get("TESTING"):
            LOGGER.info("Development password reset for %s: %s", user.email, reset_url)
        else:
            LOGGER.info("Development password reset requested for %s", user.email)
        return

    client = Client(
        auth=(
            current_app.config["MAILJET_API_KEY"],
            current_app.config["MAILJET_API_SECRET"],
        ),
        version="v3.1",
    )
    data = {
        "Messages": [
            {
                "From": {
                    "Email": current_app.config["MAIL_FROM"],
                    "Name": "Dash Starter",
                },
                "To": [{"Email": user.email, "Name": user.first_name}],
                "Subject": "Reset your Dash Starter password",
                "TextPart": f"Reset your password: {reset_url}",
                "HTMLPart": (
                    f"<p>Hello {escape(user.first_name)},</p>"
                    "<p>Use the link below to reset your password. "
                    f"It expires in {ttl_minutes} minutes.</p>"
                    f'<p><a href="{escape(reset_url, quote=True)}">Reset password</a></p>'
                ),
            }
        ]
    }
    try:
        response = client.send.create(data=data)
    except Exception as exc:  # Mailjet wraps transport errors inconsistently.
        raise MailDeliveryError("Mailjet request failed") from exc
    if not 200 <= int(response.status_code) < 300:
        raise MailDeliveryError(f"Mailjet rejected reset email with status {response.status_code}")
