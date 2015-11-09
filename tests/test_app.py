# -*- coding: utf-8 -*-
"""Test that everything gets tied together."""

from flask import Flask
import frost.app


def test_create_app():
    app = frost.app.create_app()
    assert isinstance(app, Flask)
