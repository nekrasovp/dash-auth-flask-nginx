"""Reusable UI helpers shared by Dash pages."""

from __future__ import annotations

from urllib.parse import quote, urlparse

import dash_bootstrap_components as dbc
from dash import dcc, html
from flask_login import current_user

PUBLIC_PATHS = {
    "/login",
    "/register",
    "/forgot-password",
    "/reset-password",
    "/forgot",
    "/change",
}


def safe_next_path(value: str | None, default: str = "/") -> str:
    """Allow local paths only, preventing open redirects."""

    if not value:
        return default
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
        return default
    if parsed.path in PUBLIC_PATHS:
        return default
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{parsed.path}{query}"


def protected_page(path: str, content):
    if current_user.is_authenticated:
        return content
    target = quote(path, safe="/")
    return dcc.Location(
        id={"type": "auth-redirect", "path": path},
        href=f"/login?next={target}",
        refresh=True,
    )


def page_heading(eyebrow: str, title: str, description: str):
    return html.Div(
        [
            html.P(eyebrow, className="page-eyebrow"),
            html.H1(title, className="page-title"),
            html.P(description, className="page-description"),
        ],
        className="page-heading",
    )


def auth_card(title: str, description: str, children, footer=None):
    return html.Div(
        [
            html.Div(
                [
                    html.Div("D", className="brand-mark"),
                    html.Span("Dash Starter", className="brand-name"),
                ],
                className="auth-brand",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H1(title, className="auth-title"),
                        html.P(description, className="auth-description"),
                        children,
                        footer,
                    ]
                ),
                className="auth-card",
            ),
            html.P(
                "Dash · Flask · SQLite · Nginx",
                className="auth-stack-note",
            ),
        ],
        className="auth-wrap",
    )


def form_field(
    label: str,
    component_id: str,
    *,
    input_type: str = "text",
    placeholder: str = "",
    value: str | None = None,
    help_text: str | None = None,
    auto_focus: bool = False,
    disabled: bool = False,
):
    return html.Div(
        [
            dbc.Label(label, html_for=component_id, className="form-label"),
            dbc.Input(
                id=component_id,
                type=input_type,
                placeholder=placeholder,
                value=value,
                autoFocus=auto_focus,
                disabled=disabled,
                className="form-control-modern",
            ),
            dbc.FormText(help_text, className="form-help") if help_text else None,
        ],
        className="form-field",
    )


def feedback_alert(message: str, color: str = "danger"):
    return dbc.Alert(message, color=color, className="form-alert", dismissable=True)
