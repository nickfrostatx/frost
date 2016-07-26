# -*- coding: utf-8 -*-
"""Test that everything gets tied together."""

import flask
import frost.app
import os


def test_create_app():
    os.environ.clear()
    app = frost.app.create_app()
    assert isinstance(app, flask.Flask)
    assert app.config['REDIS_URL'] == ''
    assert app.config['GITHUB_CLIENT_ID'] == ''
    assert app.config['GITHUB_CLIENT_SECRET'] == ''


def test_app_config(tmpdir):
    f = tmpdir.join('config.py')
    f.write('''
REDIS_URL = 'redis://user:pass@example.com/2'
GITHUB_CLIENT_ID = 'my client id'
GITHUB_CLIENT_SECRET = 'my client secret'
''')
    os.environ.clear()
    os.environ['CONFIG_PATH'] = str(f)

    app = frost.app.create_app()
    assert isinstance(app, flask.Flask)
    assert app.config['REDIS_URL'] == 'redis://user:pass@example.com/2'
    assert app.config['GITHUB_CLIENT_ID'] == 'my client id'
    assert app.config['GITHUB_CLIENT_SECRET'] == 'my client secret'
    assert app.config['GITHUB_WEBHOOKS_KEY'] == ''
