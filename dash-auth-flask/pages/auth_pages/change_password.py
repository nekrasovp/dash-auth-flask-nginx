"""Password reset redemption page."""

from __future__ import annotations

import logging

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, no_update
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from services.auth import AuthError, redeem_reset_token
from ui import auth_card, feedback_alert, form_field

LOGGER = logging.getLogger(__name__)

dash.register_page(
    __name__,
    path="/reset-password",
    name="Reset password",
    title="Choose a new password · Dash Starter",
    redirect_from=["/change"],
)


def layout(token=None, **_kwargs):
    if current_user.is_authenticated:
        return dcc.Location(id="reset-authenticated", href="/profile", refresh=True)
    form = dbc.Form(
        [
            dcc.Store(id="reset-token", data=token or ""),
            dcc.Location(id="reset-redirect", refresh=True),
            html.Div(id="reset-alert"),
            form_field(
                "New password",
                "reset-password",
                input_type="password",
                placeholder="At least 12 characters",
                help_text="Use 12 or more characters.",
                auto_focus=True,
            ),
            form_field(
                "Confirm new password",
                "reset-confirm",
                input_type="password",
                placeholder="Repeat your password",
            ),
            dbc.Button(
                "Update password",
                id="reset-submit",
                color="primary",
                className="auth-submit",
            ),
        ]
    )
    footer = html.P(
        [
            dcc.Link("Request a new link", href="/forgot-password"),
            " · ",
            dcc.Link("Back to sign in", href="/login"),
        ],
        className="auth-footer",
    )
    return auth_card(
        "Choose a new password",
        "This secure link can be used once and expires after 30 minutes.",
        form,
        footer,
    )


@callback(
    Output("reset-alert", "children"),
    Output("reset-redirect", "href"),
    Input("reset-submit", "n_clicks"),
    State("reset-token", "data"),
    State("reset-password", "value"),
    State("reset-confirm", "value"),
    prevent_initial_call=True,
)
def reset_password(n_clicks, token, password, confirm):
    if not n_clicks:
        return no_update, no_update
    if password != confirm:
        return feedback_alert("Passwords do not match."), no_update
    try:
        redeem_reset_token(token, password)
    except AuthError as exc:
        return feedback_alert(str(exc)), no_update
    except SQLAlchemyError:
        LOGGER.exception("Password reset failed")
        return feedback_alert("Unable to update your password right now."), no_update
    return feedback_alert("Password updated. Redirecting to sign in…", "success"), "/login"
