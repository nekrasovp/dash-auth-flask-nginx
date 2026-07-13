"""Authenticated profile and password settings."""

from __future__ import annotations

import logging

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, no_update
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from services.auth import (
    AuthError,
    change_password,
    update_profile,
    validate_password,
)
from ui import feedback_alert, form_field, page_heading, protected_page

LOGGER = logging.getLogger(__name__)

dash.register_page(
    __name__,
    path="/profile",
    name="Profile",
    title="Profile · Dash Starter",
)


def layout(**_kwargs):
    if not current_user.is_authenticated:
        return protected_page("/profile", html.Div())

    content = html.Div(
        [
            dcc.Location(id="profile-redirect", refresh=True),
            page_heading(
                "ACCOUNT",
                "Profile settings",
                "Keep your personal details and password up to date.",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H2("Personal details", className="card-title"),
                                    html.P(
                                        "This information appears in your workspace.",
                                        className="card-subtitle",
                                    ),
                                    html.Div(id="profile-details-alert"),
                                    dbc.Form(
                                        [
                                            form_field(
                                                "First name",
                                                "profile-first-name",
                                                value=current_user.first_name,
                                            ),
                                            form_field(
                                                "Last name",
                                                "profile-last-name",
                                                value=current_user.last_name,
                                            ),
                                            form_field(
                                                "Email address",
                                                "profile-email",
                                                input_type="email",
                                                value=current_user.email,
                                                help_text="Email changes are disabled in this starter.",
                                                disabled=True,
                                            ),
                                            dbc.Button(
                                                "Save details",
                                                id="profile-save-details",
                                                color="primary",
                                                className="primary-action",
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            className="content-card",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H2("Change password", className="card-title"),
                                    html.P(
                                        "Confirm your current password before choosing a new one.",
                                        className="card-subtitle",
                                    ),
                                    html.Div(id="profile-password-alert"),
                                    dbc.Form(
                                        [
                                            form_field(
                                                "Current password",
                                                "profile-current-password",
                                                input_type="password",
                                            ),
                                            form_field(
                                                "New password",
                                                "profile-new-password",
                                                input_type="password",
                                                help_text="Use at least 12 characters.",
                                            ),
                                            form_field(
                                                "Confirm new password",
                                                "profile-confirm-password",
                                                input_type="password",
                                            ),
                                            dbc.Button(
                                                "Update password",
                                                id="profile-save-password",
                                                color="primary",
                                                className="primary-action",
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            className="content-card",
                        ),
                        lg=6,
                    ),
                ],
                className="g-3",
            ),
        ],
        className="page-container profile-page",
    )
    return protected_page("/profile", content)


@callback(
    Output("profile-details-alert", "children"),
    Output("profile-redirect", "href"),
    Input("profile-save-details", "n_clicks"),
    State("profile-first-name", "value"),
    State("profile-last-name", "value"),
    prevent_initial_call=True,
)
def save_details(n_clicks, first_name, last_name):
    if not n_clicks or not current_user.is_authenticated:
        return no_update, no_update
    try:
        update_profile(current_user, first_name, last_name)
    except AuthError as exc:
        return feedback_alert(str(exc)), no_update
    except SQLAlchemyError:
        LOGGER.exception("Profile update failed")
        return feedback_alert("Unable to save your profile right now."), no_update
    return feedback_alert("Profile updated.", "success"), "/profile"


@callback(
    Output("profile-password-alert", "children"),
    Output("profile-current-password", "value"),
    Output("profile-new-password", "value"),
    Output("profile-confirm-password", "value"),
    Input("profile-save-password", "n_clicks"),
    State("profile-current-password", "value"),
    State("profile-new-password", "value"),
    State("profile-confirm-password", "value"),
    prevent_initial_call=True,
)
def save_password(n_clicks, current_password, new_password, confirm_password):
    if not n_clicks or not current_user.is_authenticated:
        return no_update, no_update, no_update, no_update
    if new_password != confirm_password:
        return feedback_alert("New passwords do not match."), no_update, no_update, no_update
    try:
        validate_password(new_password)
        change_password(current_user, current_password, new_password)
    except AuthError as exc:
        return feedback_alert(str(exc)), no_update, no_update, no_update
    except SQLAlchemyError:
        LOGGER.exception("Password update failed")
        return (
            feedback_alert("Unable to change your password right now."),
            no_update,
            no_update,
            no_update,
        )
    return feedback_alert("Password updated.", "success"), "", "", ""
