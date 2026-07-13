"""Dash application shell and global callbacks."""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, clientside_callback, dcc, html, no_update
from flask_login import current_user, logout_user

from server import app, server
from ui import PUBLIC_PATHS


def brand():
    return html.Div(
        [
            html.Div("D", className="brand-mark"),
            html.Div(
                [
                    html.Span("Dash Starter", className="brand-name"),
                    html.Span("Analytics workspace", className="brand-subtitle"),
                ],
            ),
        ],
        className="app-brand",
    )


def nav_links():
    return dbc.Nav(
        [
            dbc.NavLink(
                [html.Span("⌂", className="nav-icon"), "Overview"],
                href="/",
                active="exact",
            ),
            dbc.NavLink(
                [html.Span("↗", className="nav-icon"), "Analytics"],
                href="/analytics",
                active="exact",
            ),
            dbc.NavLink(
                [html.Span("○", className="nav-icon"), "Profile"],
                href="/profile",
                active="exact",
            ),
        ],
        vertical=True,
        pills=True,
        className="app-nav",
    )


def account_block(place: str):
    if not current_user.is_authenticated:
        return html.Div()
    initials = f"{current_user.first_name[:1]}{current_user.last_name[:1]}".upper()
    return html.Div(
        [
            html.Div(initials, className="user-avatar"),
            html.Div(
                [
                    html.Strong(
                        f"{current_user.first_name} {current_user.last_name}",
                        className="user-name",
                    ),
                    html.Span(current_user.email, className="user-email"),
                ],
                className="user-meta",
            ),
            dbc.Button(
                "Sign out",
                id={"type": "logout-button", "place": place},
                color="link",
                className="logout-button",
                n_clicks=0,
            ),
        ],
        className="account-block",
    )


def desktop_sidebar():
    return html.Aside(
        [
            brand(),
            html.Div("Workspace", className="nav-section-label"),
            nav_links(),
            account_block("desktop"),
        ],
        className="app-sidebar",
    )


def mobile_header():
    return html.Header(
        [
            html.Button(
                "☰",
                id="mobile-menu-open",
                className="menu-button",
                title="Open navigation",
                **{"aria-label": "Open navigation"},
            ),
            brand(),
        ],
        className="mobile-header",
    )


def serve_layout():
    return html.Div(
        [
            dcc.Location(id="app-url", refresh=True),
            dcc.Store(id="theme-store", storage_type="local"),
            html.Div(
                [
                    mobile_header(),
                    desktop_sidebar(),
                    dbc.Offcanvas(
                        [brand(), nav_links(), account_block("mobile")],
                        id="mobile-menu",
                        title=None,
                        is_open=False,
                        placement="start",
                        className="mobile-menu",
                    ),
                    html.Main(dash.page_container, className="app-main"),
                ],
                id="app-shell",
                className="app-shell",
            ),
            html.Button(
                "◐",
                id="theme-toggle",
                className="theme-toggle",
                title="Toggle color theme",
                **{"aria-label": "Toggle color theme"},
            ),
        ],
        id="app-root",
        **{"data-theme": "light"},
    )


app.layout = serve_layout


@app.callback(
    Output("app-shell", "className"),
    Input("app-url", "pathname"),
)
def update_shell(pathname: str | None):
    is_public = pathname in PUBLIC_PATHS or not current_user.is_authenticated
    return "app-shell auth-shell" if is_public else "app-shell"


@app.callback(
    Output("mobile-menu", "is_open"),
    Input("mobile-menu-open", "n_clicks"),
    Input("app-url", "pathname"),
    State("mobile-menu", "is_open"),
    prevent_initial_call=True,
)
def toggle_mobile_menu(n_clicks, _pathname, is_open):
    triggered = dash.ctx.triggered_id
    if triggered == "mobile-menu-open" and n_clicks:
        return not is_open
    return False


@app.callback(
    Output("app-url", "href"),
    Input({"type": "logout-button", "place": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def logout(n_clicks):
    if not any(n_clicks or []):
        return no_update
    logout_user()
    return "/login"


clientside_callback(
    """
    function(nClicks, storedTheme) {
        let theme = storedTheme || 'light';
        if (nClicks) {
            theme = theme === 'dark' ? 'light' : 'dark';
        }
        return [theme, theme, theme === 'dark' ? '☀' : '◐'];
    }
    """,
    Output("theme-store", "data"),
    Output("app-root", "data-theme"),
    Output("theme-toggle", "children"),
    Input("theme-toggle", "n_clicks"),
    State("theme-store", "data"),
)


if __name__ == "__main__":
    with server.app_context():
        from extensions import db

        db.create_all()
    app.run(host="0.0.0.0", port=8000, debug=True)
