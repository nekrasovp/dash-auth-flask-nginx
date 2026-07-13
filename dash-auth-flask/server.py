"""Flask server and Dash application initialization."""

from __future__ import annotations

import logging
from pathlib import Path

import click
import dash
import dash_bootstrap_components as dbc
from flask import Flask, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Settings, load_settings
from extensions import db, login_manager
from models import User
from services.auth import DuplicateEmailError, ValidationError, create_user

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
LOGGER = logging.getLogger(__name__)

settings: Settings = load_settings()

if settings.database_url.startswith("sqlite:///"):
    database_path = Path(settings.database_url.removeprefix("sqlite:///"))
    database_path.parent.mkdir(parents=True, exist_ok=True)

server = Flask(__name__)
server.config.update(settings.flask_config())
server.debug = settings.app_env == "development"
server.wsgi_app = ProxyFix(
    server.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_port=1,
)

db.init_app(server)
login_manager.init_app(server)
login_manager.login_view = "/login"
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


@server.get("/healthz")
def healthcheck():
    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        LOGGER.exception("Database health check failed")
        return jsonify(status="unhealthy"), 503
    return jsonify(status="ok"), 200


@server.after_request
def set_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    return response


@server.cli.command("init-db")
def init_db_command() -> None:
    """Create the starter database tables."""

    db.create_all()
    click.echo("Database tables are ready.")


@server.cli.command("seed-demo")
def seed_demo_command() -> None:
    """Create the explicitly configured development demo account."""

    if settings.is_production:
        raise click.ClickException("Demo seeding is disabled in production.")
    if not settings.seed_demo_user:
        click.echo("SEED_DEMO_USER is not enabled; skipping demo account.")
        return
    try:
        user = create_user(
            settings.demo_user_first_name,
            settings.demo_user_last_name,
            settings.demo_user_email,
            settings.demo_user_password,
        )
    except DuplicateEmailError:
        click.echo("Demo account already exists.")
    except ValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    else:
        click.echo(f"Created demo account {user.email}.")


app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    pages_folder="pages",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Dash Starter",
    update_title="Updating…",
)
