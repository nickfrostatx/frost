# -*- coding: utf-8 -*-
"""Expose an app instance on import."""

from .app import create_app


application = create_app()
