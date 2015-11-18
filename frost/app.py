# -*- coding: utf-8 -*-
"""Flask application factory."""

from flask import Flask
from . import __name__ as package_name
import os
import redis


def create_app():
    """Return an instance of the main Flask application."""
    app = Flask(package_name)

    for var in ('GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET', 'REDIS_URL'):
        app.config.setdefault(var, os.environ.get(var))

    from .github import GitHub
    app.github = GitHub(app)

    from .error import register_error_handler, html_handler
    register_error_handler(app, html_handler)

    from .badge import badge
    app.register_blueprint(badge)

    from .views import views
    app.register_blueprint(views)

    from .hooks import hooks
    app.register_blueprint(hooks)

    return app
