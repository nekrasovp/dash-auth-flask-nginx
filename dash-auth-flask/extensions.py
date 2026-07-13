"""Shared Flask extensions."""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
