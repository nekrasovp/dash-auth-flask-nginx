"""Custom Dash Pages 404."""

import dash
import dash_bootstrap_components as dbc
from dash import html
from flask_login import current_user

from ui import auth_card

dash.register_page(__name__, title="Page not found · Dash Starter")


def layout(**_kwargs):
    if current_user.is_authenticated:
        return html.Div(
            [
                html.P("404", className="error-code"),
                html.H1("Page not found", className="error-title"),
                html.P(
                    "The page you’re looking for may have moved or no longer exists.",
                    className="error-description",
                ),
                dbc.Button(
                    "Return to overview",
                    href="/",
                    color="primary",
                    className="primary-action",
                ),
            ],
            className="error-page",
        )

    public_content = html.Div(
        [
            html.P("404", className="error-code"),
            html.P(
                "The page you’re looking for may have moved or no longer exists.",
                className="error-description",
            ),
            dbc.Button(
                "Return to sign in",
                href="/login",
                color="primary",
                className="primary-action",
            ),
        ],
        className="error-page",
    )
    return auth_card("Page not found", "That address does not exist.", public_content)
