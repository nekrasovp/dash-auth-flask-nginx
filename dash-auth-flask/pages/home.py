"""Authenticated overview dashboard."""

from __future__ import annotations

import csv
import io

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html, no_update
from flask_login import current_user

from sample_data import DAILY_SERIES, METRICS, RECENT_ACTIVITY
from ui import page_heading, protected_page

dash.register_page(
    __name__,
    path="/",
    name="Overview",
    title="Overview · Dash Starter",
    redirect_from=["/home"],
)


def metric_card(metric):
    trend_class = f"metric-change metric-change-{metric.direction}"
    arrow = "↑" if metric.direction == "up" else "↓"
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.P(metric.label, className="metric-label"),
                    html.Div(
                        [
                            html.Strong(metric.value, className="metric-value"),
                            html.Span(f"{arrow} {metric.change}", className=trend_class),
                        ],
                        className="metric-row",
                    ),
                    html.P("vs. previous period", className="metric-caption"),
                ]
            ),
            className="metric-card",
        ),
        xs=12,
        sm=6,
        xl=3,
    )


def activity_table():
    return dbc.Table(
        [
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(html.Span("•", className="activity-dot")),
                            html.Td(
                                [
                                    html.Strong(action, className="activity-title"),
                                    html.Span(detail, className="activity-detail"),
                                ]
                            ),
                            html.Td(when, className="activity-time"),
                        ]
                    )
                    for action, detail, when in RECENT_ACTIVITY
                ]
            )
        ],
        borderless=True,
        responsive=True,
        className="activity-table",
    )


def layout(**_kwargs):
    content = html.Div(
        [
            html.Div(
                [
                    page_heading(
                        "OVERVIEW",
                        f"Welcome back, {current_user.first_name}",
                        "A clear snapshot of your workspace performance.",
                    ),
                    html.Div(
                        [
                            dbc.Button(
                                "Download report",
                                id="overview-download-button",
                                color="primary",
                                className="primary-action",
                            ),
                            dcc.Download(id="overview-download"),
                        ]
                    ),
                ],
                className="heading-row",
            ),
            dbc.Row([metric_card(metric) for metric in METRICS], className="g-3 metric-grid"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H2(
                                                        "Audience growth", className="card-title"
                                                    ),
                                                    html.P(
                                                        "Daily visitors over the last 90 days",
                                                        className="card-subtitle",
                                                    ),
                                                ]
                                            ),
                                            html.Span("Last 90 days", className="period-pill"),
                                        ],
                                        className="card-heading-row",
                                    ),
                                    dcc.Loading(
                                        dcc.Graph(
                                            id="overview-trend",
                                            config={
                                                "displayModeBar": False,
                                                "responsive": True,
                                            },
                                            className="dashboard-chart",
                                        ),
                                        type="circle",
                                        color="#6366f1",
                                    ),
                                ]
                            ),
                            className="content-card",
                        ),
                        lg=8,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H2("Recent activity", className="card-title"),
                                    html.P(
                                        "Latest workspace events",
                                        className="card-subtitle",
                                    ),
                                    activity_table(),
                                ]
                            ),
                            className="content-card h-100",
                        ),
                        lg=4,
                    ),
                ],
                className="g-3 dashboard-row",
            ),
        ],
        className="page-container",
    )
    return protected_page("/", content)


@callback(Output("overview-trend", "figure"), Input("theme-store", "data"))
def overview_figure(theme):
    is_dark = theme == "dark"
    dates = [row["date"] for row in DAILY_SERIES]
    visitors = [row["visitors"] for row in DAILY_SERIES]
    figure = go.Figure(
        go.Scatter(
            x=dates,
            y=visitors,
            mode="lines",
            line={"color": "#6366f1", "width": 3, "shape": "spline"},
            fill="tozeroy",
            fillcolor="rgba(99, 102, 241, 0.12)",
            hovertemplate="%{x|%b %d}<br><b>%{y:,}</b> visitors<extra></extra>",
        )
    )
    figure.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        margin={"l": 10, "r": 10, "t": 24, "b": 10},
        height=330,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        showlegend=False,
        xaxis={"showgrid": False, "title": None},
        yaxis={"gridcolor": "rgba(148,163,184,0.15)", "title": None},
        font={"family": "Inter, ui-sans-serif, system-ui", "color": "#94a3b8"},
    )
    return figure


@callback(
    Output("overview-download", "data"),
    Input("overview-download-button", "n_clicks"),
    prevent_initial_call=True,
)
def download_report(n_clicks):
    if not n_clicks:
        return no_update

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=("date", "visitors", "conversions"))
    writer.writeheader()
    writer.writerows(DAILY_SERIES)
    return {
        "content": output.getvalue(),
        "filename": "dash-starter-report.csv",
        "type": "text/csv",
    }
