# -*- coding: utf-8 -*-
"""Test HTML views."""

from frost.views import views
import contextlib
import flask
import pytest


@pytest.fixture
def client():
    app = flask.Flask(__name__, template_folder='../frost/templates',
                      static_folder='../frost/static')
    app.register_blueprint(views)
    return app.test_client()


@contextlib.contextmanager
def user_set(app, user):
    """Manually set g.user."""
    def handler(sender, **kwargs):
        flask.g.user = user
    with flask.appcontext_pushed.connected_to(handler, app):
        yield


def test_home(client):
    rv = client.get('/')
    assert rv.status_code == 200


def test_home_invalid_user(client):
    with user_set(client.application, 'fakeuser'):
        rv = client.get('/')
        assert rv.status_code == 500


def test_badge(client):
    rv = client.get('/nick/repo.svg')
    assert b'build' in rv.data
    assert b'passing' in rv.data
    assert rv.status_code == 200
