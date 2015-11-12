# -*- coding: utf-8 -*-
"""Test HTML views."""

from frost.views import views
import flask
import pytest


@pytest.fixture
def client():
    app = flask.Flask(__name__, static_folder='../frost/static')
    app.register_blueprint(views)
    return app.test_client()


def test_home(client):
    rv = client.get('/')
    assert rv.data == b'Home\n'
    assert rv.status_code == 200


def test_badge(client):
    rv = client.get('/nick/repo.svg')
    assert b'build' in rv.data
    assert b'passing' in rv.data
    assert rv.status_code == 200
