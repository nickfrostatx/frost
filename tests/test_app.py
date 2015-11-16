# -*- coding: utf-8 -*-
"""Test that everything gets tied together."""

from flask import Flask
import frost.app
import os


def test_create_app():
    app = frost.app.create_app()
    assert isinstance(app, Flask)


def test_app_config():
    os.environ['GITHUB_CLIENT_ID'] = 'my client id'
    os.environ['GITHUB_CLIENT_SECRET'] = 'my client secret'
    app = frost.app.create_app()
    assert isinstance(app, Flask)
    assert app.config['GITHUB_CLIENT_ID'] == 'my client id'
    assert app.config['GITHUB_CLIENT_SECRET'] == 'my client secret'
