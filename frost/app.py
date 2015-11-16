# -*- coding: utf-8 -*-
"""Flask application factory."""

from flask import Flask
from . import __name__ as package_name
import os


def create_app():
    """Return an instance of the main Flask application."""
    app = Flask(package_name)

    client_id = os.environ.get('GITHUB_CLIENT_ID')
    client_secret = os.environ.get('GITHUB_CLIENT_SECRET')
    app.config['GITHUB_CLIENT_ID'] = client_id
    from .github import GitHub
    app.github = GitHub(client_id, client_secret)

    from .error import register_error_handler, html_handler
    register_error_handler(app, html_handler)

    from .views import views
    app.register_blueprint(views)

    from .hooks import hooks
    app.register_blueprint(hooks)

    return app
