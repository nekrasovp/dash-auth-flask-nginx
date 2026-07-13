"""Account registration page."""

from __future__ import annotations

import logging

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, no_update
from flask_login import current_user, login_user
from sqlalchemy.exc import SQLAlchemyError

from services.auth import AuthError, create_user
from ui import auth_card, feedback_alert, form_field

LOGGER = logging.getLogger(__name__)

dash.register_page(
    __name__,
    path="/register",
    name="Register",
    title="Create account · Dash Starter",
)


def layout(**_kwargs):
    if current_user.is_authenticated:
        return dcc.Location(id="register-authenticated", href="/", refresh=True)
    form = dbc.Form(
        [
            dcc.Location(id="register-redirect", refresh=True),
            html.Div(id="register-alert"),
            dbc.Row(
                [
                    dbc.Col(
                        form_field(
                            "First name",
                            "register-first-name",
                            placeholder="Ada",
                            auto_focus=True,
                        ),
                        sm=6,
                    ),
                    dbc.Col(
                        form_field(
                            "Last name",
                            "register-last-name",
                            placeholder="Lovelace",
                        ),
                        sm=6,
                    ),
                ],
                className="g-3",
            ),
            form_field(
                "Email address",
                "register-email",
                input_type="email",
                placeholder="you@example.com",
            ),
            form_field(
                "Password",
                "register-password",
                input_type="password",
                placeholder="At least 12 characters",
                help_text="Use 12 or more characters.",
            ),
            form_field(
                "Confirm password",
                "register-confirm",
                input_type="password",
                placeholder="Repeat your password",
            ),
            dbc.Button(
                "Create account",
                id="register-submit",
                color="primary",
                className="auth-submit",
            ),
        ]
    )
    footer = html.P(
        ["Already registered? ", dcc.Link("Sign in", href="/login")],
        className="auth-footer",
    )
    return auth_card(
        "Create your account",
        "Start with a secure, modern Dash workspace.",
        form,
        footer,
    )


@callback(
    Output("register-alert", "children"),
    Output("register-redirect", "href"),
    Input("register-submit", "n_clicks"),
    State("register-first-name", "value"),
    State("register-last-name", "value"),
    State("register-email", "value"),
    State("register-password", "value"),
    State("register-confirm", "value"),
    prevent_initial_call=True,
)
def register(n_clicks, first_name, last_name, email, password, confirm):
    if not n_clicks:
        return no_update, no_update
    if password != confirm:
        return feedback_alert("Passwords do not match."), no_update
    try:
        user = create_user(first_name, last_name, email, password)
    except AuthError as exc:
        return feedback_alert(str(exc)), no_update
    except SQLAlchemyError:
        LOGGER.exception("Registration database failure")
        return feedback_alert("Unable to create your account right now."), no_update
    login_user(user)
    return no_update, "/"
