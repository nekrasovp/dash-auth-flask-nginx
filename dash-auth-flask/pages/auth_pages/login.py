"""Sign-in page."""

from __future__ import annotations

import logging

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, no_update
from flask_login import current_user, login_user
from sqlalchemy.exc import SQLAlchemyError

from services.auth import InvalidCredentialsError, authenticate
from ui import auth_card, feedback_alert, form_field, safe_next_path

LOGGER = logging.getLogger(__name__)

dash.register_page(
    __name__,
    path="/login",
    name="Sign in",
    title="Sign in · Dash Starter",
)


def layout(next=None, **_kwargs):
    if current_user.is_authenticated:
        return dcc.Location(id="login-authenticated", href="/", refresh=True)
    next_path = safe_next_path(next)
    form = dbc.Form(
        [
            dcc.Store(id="login-next", data=next_path),
            dcc.Location(id="login-redirect", refresh=True),
            html.Div(id="login-alert"),
            form_field(
                "Email address",
                "login-email",
                input_type="email",
                placeholder="you@example.com",
                auto_focus=True,
            ),
            form_field(
                "Password",
                "login-password",
                input_type="password",
                placeholder="Enter your password",
            ),
            html.Div(
                dcc.Link("Forgot password?", href="/forgot-password"),
                className="form-link-row",
            ),
            dbc.Button(
                "Sign in",
                id="login-submit",
                color="primary",
                className="auth-submit",
            ),
        ]
    )
    footer = html.P(
        ["New to the starter? ", dcc.Link("Create an account", href="/register")],
        className="auth-footer",
    )
    return auth_card(
        "Welcome back",
        "Sign in to continue to your analytics workspace.",
        form,
        footer,
    )


@callback(
    Output("login-alert", "children"),
    Output("login-redirect", "href"),
    Input("login-submit", "n_clicks"),
    Input("login-password", "n_submit"),
    State("login-email", "value"),
    State("login-password", "value"),
    State("login-next", "data"),
    prevent_initial_call=True,
)
def sign_in(n_clicks, n_submit, email, password, next_path):
    if not n_clicks and not n_submit:
        return no_update, no_update
    try:
        user = authenticate(email, password)
    except InvalidCredentialsError:
        return feedback_alert("Invalid email or password."), no_update
    except SQLAlchemyError:
        LOGGER.exception("Sign-in database failure")
        return feedback_alert("Unable to sign in right now."), no_update

    login_user(user)
    return no_update, safe_next_path(next_path)
