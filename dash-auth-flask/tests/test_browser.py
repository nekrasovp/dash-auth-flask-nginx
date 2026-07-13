from __future__ import annotations

import threading
import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server

from app import server
from extensions import db


@pytest.fixture(scope="module")
def live_server():
    with server.app_context():
        db.drop_all()
        db.create_all()

    http_server = make_server("127.0.0.1", 0, server, threaded=True)
    thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    thread.start()

    yield f"http://127.0.0.1:{http_server.server_port}"

    http_server.shutdown()
    http_server.server_close()
    thread.join(timeout=5)
    with server.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture()
def browser():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,900")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.mark.browser
def test_registration_dashboard_theme_and_mobile_navigation(live_server, browser):
    wait = WebDriverWait(browser, 15)
    browser.get(f"{live_server}/register")
    wait.until(
        expected.text_to_be_present_in_element(
            (By.CSS_SELECTOR, ".auth-title"),
            "Create your account",
        )
    )

    email = f"browser-{uuid.uuid4().hex[:8]}@example.com"
    browser.find_element(By.ID, "register-first-name").send_keys("Browser")
    browser.find_element(By.ID, "register-last-name").send_keys("Test")
    browser.find_element(By.ID, "register-email").send_keys(email)
    browser.find_element(By.ID, "register-password").send_keys("browser-test-password")
    browser.find_element(By.ID, "register-confirm").send_keys("browser-test-password")
    browser.find_element(By.ID, "register-submit").click()

    wait.until(
        expected.text_to_be_present_in_element(
            (By.CSS_SELECTOR, ".page-eyebrow"),
            "OVERVIEW",
        )
    )
    assert "Welcome back, Browser" in browser.find_element(By.CSS_SELECTOR, ".page-title").text
    wait.until(
        expected.presence_of_element_located((By.CSS_SELECTOR, "#overview-trend .js-plotly-plot"))
    )
    assert (
        browser.find_element(By.CSS_SELECTOR, '.app-nav a[href="/"]')
        .get_attribute("class")
        .endswith("active")
    )

    browser.find_element(By.ID, "theme-toggle").click()
    wait.until(
        lambda driver: driver.find_element(By.ID, "app-root").get_attribute("data-theme") == "dark"
    )
    browser.refresh()
    wait.until(
        lambda driver: driver.find_element(By.ID, "app-root").get_attribute("data-theme") == "dark"
    )

    browser.set_window_size(390, 844)
    wait.until(expected.visibility_of_element_located((By.CSS_SELECTOR, ".mobile-header")))
    browser.find_element(By.ID, "mobile-menu-open").click()
    wait.until(
        lambda driver: "show"
        in driver.find_element(By.ID, "mobile-menu").get_attribute("class").split()
    )

    severe_logs = [entry for entry in browser.get_log("browser") if entry["level"] == "SEVERE"]
    assert severe_logs == []
