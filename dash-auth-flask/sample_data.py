"""Deterministic sample data used by the starter dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Metric:
    label: str
    value: str
    change: str
    direction: str


METRICS = (
    Metric("Active users", "8,492", "+12.8%", "up"),
    Metric("Conversion", "6.42%", "+0.8%", "up"),
    Metric("Avg. session", "4m 18s", "+18s", "up"),
    Metric("Bounce rate", "31.6%", "-2.4%", "down"),
)

START_DATE = date(2026, 1, 1)
DAILY_SERIES = [
    {
        "date": START_DATE + timedelta(days=index),
        "visitors": 620 + ((index * 47) % 310) + (index % 7) * 22,
        "conversions": 34 + ((index * 13) % 42),
    }
    for index in range(90)
]

CHANNELS = (
    ("Organic search", 3820, "44.9%"),
    ("Direct", 2110, "24.8%"),
    ("Referrals", 1480, "17.4%"),
    ("Social", 1092, "12.9%"),
)

RECENT_ACTIVITY = (
    ("Workspace created", "Starter project", "2 minutes ago"),
    ("Report exported", "Weekly overview", "38 minutes ago"),
    ("Profile updated", "Demo account", "Yesterday"),
    ("New data source", "Product analytics", "2 days ago"),
)
