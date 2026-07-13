from __future__ import annotations

import pytest

from app import server
from extensions import db
from pages.home import download_report


@pytest.fixture(autouse=True)
def dispose_database_connections():
    yield
    with server.app_context():
        db.session.remove()
        db.engine.dispose()


def test_healthcheck_reaches_database():
    with server.app_context():
        db.create_all()
    response = server.test_client().get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_security_headers_are_present():
    response = server.test_client().get("/healthz")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"


def test_overview_report_download_is_deterministic():
    report = download_report(1)
    lines = report["content"].splitlines()
    assert report["filename"] == "dash-starter-report.csv"
    assert lines[0] == "date,visitors,conversions"
    assert len(lines) == 91
