# -*- coding: utf-8 -*-
"""Flask application factory."""

from flask import Flask
from . import __name__ as package_name


def create_app():
    """Return an instance of the main Flask application."""
    app = Flask(package_name)

    from .error import register_error_handler, html_handler
    register_error_handler(app, html_handler)

    return app
