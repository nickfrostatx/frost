# -*- coding: utf-8 -*-
"""Test HTML views."""

from frost.views import views
import flask


def test_custom_handler():
    app = flask.Flask(__name__)
    app.register_blueprint(views)
    with app.test_client() as client:
        rv = client.get('/')
        assert rv.data == b'Home\n'
        assert rv.status_code == 200
