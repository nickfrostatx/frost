# -*- coding: utf-8 -*-
"""Flask application factory."""

from flask import Flask
from . import __name__ as package_name


def create_app():
    """Return an instance of the main Flask application."""
    app = Flask(package_name)

    app.config.from_envvar('CONFIG_PATH', silent=True)

    app.config.setdefault('GITHUB_CLIENT_ID', '')
    app.config.setdefault('GITHUB_CLIENT_SECRET', '')
    app.config.setdefault('GITHUB_WEBHOOKS_KEY', '')
    app.config.setdefault('REDIS_URL', '')

    from .error import register_error_handler, html_handler
    register_error_handler(app, html_handler)

    from .session import RedisSessionInterface
    app.session_interface = RedisSessionInterface()

    from .badge import badge
    app.register_blueprint(badge)

    from .views import views
    app.register_blueprint(views)

    from .hooks import hooks
    hooks.init_app(app)

    return app
