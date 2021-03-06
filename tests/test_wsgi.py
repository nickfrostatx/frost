# -*- coding: utf-8 -*-
"""Test the wsgi module."""

import flask
import os


def test_wsgi_app_config():
    os.environ['REDIS_URL'] = 'redis://user:pass@example.com/2'
    os.environ['GITHUB_CLIENT_ID'] = 'my client id'
    os.environ['GITHUB_CLIENT_SECRET'] = 'my client secret'
    from frost.wsgi import application
    assert isinstance(application, flask.Flask)
    assert application.config['REDIS_URL'] == 'redis://user:pass@example.com/2'
    assert application.config['GITHUB_CLIENT_ID'] == 'my client id'
    assert application.config['GITHUB_CLIENT_SECRET'] == 'my client secret'
