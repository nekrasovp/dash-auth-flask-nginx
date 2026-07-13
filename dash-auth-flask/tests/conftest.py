from __future__ import annotations

import pytest
from flask import Flask

from extensions import db


@pytest.fixture()
def flask_app(tmp_path):
    database_path = tmp_path / "test.db"
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAIL_BACKEND="console",
        RESET_TOKEN_TTL_MINUTES=30,
    )
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture()
def app_context(flask_app):
    with flask_app.app_context():
        yield flask_app
