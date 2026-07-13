from __future__ import annotations

import uuid

import pytest

from app import app, server
from extensions import db


@pytest.fixture(autouse=True)
def dispose_database_connections():
    yield
    with server.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.mark.browser
def test_registration_dashboard_theme_and_mobile_navigation(dash_duo):
    with server.app_context():
        db.create_all()

    dash_duo.start_server(app)
    dash_duo.driver.get(f"{dash_duo.server_url}/register")
    dash_duo.wait_for_text_to_equal(".auth-title", "Create your account")

    email = f"browser-{uuid.uuid4().hex[:8]}@example.com"
    dash_duo.find_element("#register-first-name").send_keys("Browser")
    dash_duo.find_element("#register-last-name").send_keys("Test")
    dash_duo.find_element("#register-email").send_keys(email)
    dash_duo.find_element("#register-password").send_keys("browser-test-password")
    dash_duo.find_element("#register-confirm").send_keys("browser-test-password")
    dash_duo.find_element("#register-submit").click()

    dash_duo.wait_for_text_to_equal(".page-eyebrow", "OVERVIEW")
    assert "Welcome back, Browser" in dash_duo.find_element(".page-title").text
    dash_duo.wait_for_element("#overview-trend .js-plotly-plot")

    theme_toggle = dash_duo.find_element("#theme-toggle")
    theme_toggle.click()
    dash_duo.wait_for_condition(
        lambda: dash_duo.find_element("#app-root").get_attribute("data-theme") == "dark"
    )
    dash_duo.driver.refresh()
    dash_duo.wait_for_condition(
        lambda: dash_duo.find_element("#app-root").get_attribute("data-theme") == "dark"
    )

    dash_duo.driver.set_window_size(390, 844)
    dash_duo.wait_for_element(".mobile-header")
    dash_duo.find_element("#mobile-menu-open").click()
    dash_duo.wait_for_element("#mobile-menu.show")
    assert dash_duo.get_logs() == []
