"""Interactive analytics example page."""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from sample_data import CHANNELS, DAILY_SERIES
from ui import page_heading, protected_page

dash.register_page(
    __name__,
    path="/analytics",
    name="Analytics",
    title="Analytics · Dash Starter",
    redirect_from=["/page1"],
)


def channel_table():
    return dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Channel"), html.Th("Visitors"), html.Th("Share")])),
            html.Tbody(
                [
                    html.Tr([html.Td(name), html.Td(f"{visitors:,}"), html.Td(share)])
                    for name, visitors, share in CHANNELS
                ]
            ),
        ],
        hover=True,
        responsive=True,
        className="data-table",
    )


def layout(**_kwargs):
    content = html.Div(
        [
            page_heading(
                "ANALYTICS",
                "Explore your audience",
                "Use these controls as a starting point for your own Dash callbacks.",
            ),
            dbc.Card(
                dbc.CardBody(
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Time range", html_for="analytics-period"),
                                    dcc.Dropdown(
                                        id="analytics-period",
                                        options=[
                                            {"label": "Last 30 days", "value": 30},
                                            {"label": "Last 60 days", "value": 60},
                                            {"label": "Last 90 days", "value": 90},
                                        ],
                                        value=30,
                                        clearable=False,
                                    ),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Metric"),
                                    dbc.RadioItems(
                                        id="analytics-metric",
                                        options=[
                                            {"label": "Visitors", "value": "visitors"},
                                            {"label": "Conversions", "value": "conversions"},
                                        ],
                                        value="visitors",
                                        inline=True,
                                        className="metric-selector",
                                    ),
                                ],
                                md=8,
                            ),
                        ],
                        className="g-3 align-items-end",
                    )
                ),
                className="filter-card",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H2("Performance trend", className="card-title"),
                                    dcc.Loading(
                                        dcc.Graph(
                                            id="analytics-chart",
                                            config={
                                                "displayModeBar": False,
                                                "responsive": True,
                                            },
                                            className="analytics-chart",
                                        ),
                                        type="circle",
                                        color="#6366f1",
                                    ),
                                ]
                            ),
                            className="content-card h-100",
                        ),
                        lg=8,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H2("Acquisition", className="card-title"),
                                    html.P("Visitors by channel", className="card-subtitle"),
                                    channel_table(),
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
    return protected_page("/analytics", content)


@callback(
    Output("analytics-chart", "figure"),
    Input("analytics-period", "value"),
    Input("analytics-metric", "value"),
    Input("theme-store", "data"),
)
def analytics_figure(period, metric, theme):
    rows = DAILY_SERIES[-int(period or 30) :]
    color = "#6366f1" if metric == "visitors" else "#14b8a6"
    label = "Visitors" if metric == "visitors" else "Conversions"
    figure = go.Figure(
        go.Bar(
            x=[row["date"] for row in rows],
            y=[row[metric] for row in rows],
            marker={"color": color, "cornerradius": 4},
            hovertemplate=f"%{{x|%b %d}}<br><b>%{{y:,}}</b> {label.lower()}<extra></extra>",
        )
    )
    figure.update_layout(
        template="plotly_dark" if theme == "dark" else "plotly_white",
        margin={"l": 10, "r": 10, "t": 28, "b": 10},
        height=390,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis={"showgrid": False, "title": None},
        yaxis={"gridcolor": "rgba(148,163,184,0.15)", "title": label},
        font={"family": "Inter, ui-sans-serif, system-ui", "color": "#94a3b8"},
    )
    return figure
