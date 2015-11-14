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


def test_repo_page(client):
    rv = client.get('/nickfrostatx/frost')
    assert b'nickfrostatx' in rv.data
    assert b'frost' in rv.data
    assert rv.status_code == 200


def test_invalid_repo_page(client):
    rv = client.get('/nickfrostatx/fakerepo')
    assert rv.status_code == 404

    rv = client.get('/fakeuser/fakerepo')
    assert rv.status_code == 404


def test_valid_badges(client):
    rv = client.get('/nickfrostatx/frost.svg')
    assert b'build' in rv.data
    assert b'passing' in rv.data
    assert rv.status_code == 200

    rv = client.get('/nickfrostatx/flask-hookserver.svg')
    assert b'build' in rv.data
    assert b'error' in rv.data
    assert rv.status_code == 200

    rv = client.get('/nickfrostatx/nass.svg')
    assert b'build' in rv.data
    assert b'failing' in rv.data
    assert rv.status_code == 200

    rv = client.get('/nickfrostatx/corral.svg')
    assert b'build' in rv.data
    assert b'unknown' in rv.data
    assert rv.status_code == 200


def test_404_badge(client):
    rv = client.get('/nickfrostatx/fakerepo.svg')
    assert b'build' in rv.data
    assert b'invalid' in rv.data
    assert rv.status_code == 404

    rv = client.get('/fakeuser/fakerepo.svg')
    assert b'build' in rv.data
    assert b'invalid' in rv.data
    assert rv.status_code == 404


def test_500_badge(client):
    rv = client.get('/error/error.svg')
    assert b'build' in rv.data
    assert b'error' in rv.data
    assert rv.status_code == 500
