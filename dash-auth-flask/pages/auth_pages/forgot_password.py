"""Password-reset request page."""

from __future__ import annotations

import logging

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, no_update
from flask import current_app, request
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from services.auth import create_reset_request, discard_reset_request
from services.mail import MailDeliveryError, send_password_reset
from ui import auth_card, feedback_alert, form_field

LOGGER = logging.getLogger(__name__)
GENERIC_MESSAGE = "If an account matches that email, a password-reset link is on its way."

dash.register_page(
    __name__,
    path="/forgot-password",
    name="Forgot password",
    title="Reset password · Dash Starter",
    redirect_from=["/forgot"],
)


def layout(**_kwargs):
    if current_user.is_authenticated:
        return dcc.Location(id="forgot-authenticated", href="/profile", refresh=True)
    form = dbc.Form(
        [
            html.Div(id="forgot-alert"),
            form_field(
                "Email address",
                "forgot-email",
                input_type="email",
                placeholder="you@example.com",
                auto_focus=True,
            ),
            dbc.Button(
                "Send reset link",
                id="forgot-submit",
                color="primary",
                className="auth-submit",
            ),
        ]
    )
    footer = html.P(
        dcc.Link("Back to sign in", href="/login"),
        className="auth-footer",
    )
    return auth_card(
        "Reset your password",
        "Enter your account email and we’ll send a secure link.",
        form,
        footer,
    )


@callback(
    Output("forgot-alert", "children"),
    Input("forgot-submit", "n_clicks"),
    State("forgot-email", "value"),
    prevent_initial_call=True,
)
def request_password_reset(n_clicks, email):
    if not n_clicks:
        return no_update
    reset_request = None
    try:
        reset_request = create_reset_request(
            email,
            current_app.config["RESET_TOKEN_TTL_MINUTES"],
        )
        if reset_request is not None:
            reset_url = (
                f"{request.host_url.rstrip('/')}/reset-password?token={reset_request.raw_token}"
            )
            send_password_reset(reset_request.user, reset_url)
    except MailDeliveryError:
        LOGGER.exception("Password-reset email delivery failed")
        if reset_request is not None:
            try:
                discard_reset_request(reset_request)
            except SQLAlchemyError:
                LOGGER.exception("Unable to discard undelivered reset token")
    except SQLAlchemyError:
        LOGGER.exception("Password-reset request failed")
    return feedback_alert(GENERIC_MESSAGE, "success")
