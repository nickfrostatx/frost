# -*- coding: utf-8 -*-
"""Test the badge."""

from frost.badge import badge
import flask
import werkzeug
import pytest


@pytest.fixture
def client():
    app = flask.Flask(__name__)
    app.config['DEBUG'] = True
    app.register_blueprint(badge)
    return app.test_client()


def validate_headers(rv):
    assert 'ETag' not in rv.headers
    assert 'Last-Modified' not in rv.headers
    assert rv.headers['Cache-Control'] == 'no-store, no-cache, must-revalidate'
    assert rv.headers['Pragma'] == 'no-cache'


def test_valid_badges(client):
    rv = client.get('/nickfrostatx/frost.svg')
    validate_headers(rv)
    assert b'build' in rv.data
    assert b'passing' in rv.data
    assert rv.status_code == 200

    rv = client.get('/nickfrostatx/flask-hookserver.svg')
    validate_headers(rv)
    assert b'build' in rv.data
    assert b'error' in rv.data
    assert rv.status_code == 200

    rv = client.get('/nickfrostatx/nass.svg')
    validate_headers(rv)
    assert b'build' in rv.data
    assert b'failing' in rv.data
    assert rv.status_code == 200

    rv = client.get('/nickfrostatx/corral.svg')
    validate_headers(rv)
    assert b'build' in rv.data
    assert b'unknown' in rv.data
    assert rv.status_code == 200


def test_custom_badge_error(client):
    def do400():
        exc = werkzeug.exceptions.BadRequest()
        raise exc

    # Doesn't touch the module-level badge object \m/
    client.application.add_url_rule('/400', 'badge.do400', do400)

    rv = client.get('/400')
    validate_headers(rv)
    assert b'build' in rv.data
    assert b'error' in rv.data
    assert rv.status_code == 400


def test_404_badge(client):
    rv = client.get('/nickfrostatx/fakerepo.svg')
    validate_headers(rv)
    assert b'build' in rv.data
    assert b'invalid' in rv.data
    assert rv.status_code == 404

    rv = client.get('/fakeuser/fakerepo.svg')
    validate_headers(rv)
    assert b'build' in rv.data
    assert b'invalid' in rv.data
    assert rv.status_code == 404


def test_500_badge(client):
    rv = client.get('/error/error.svg')
    validate_headers(rv)
    assert b'build' in rv.data
    assert b'error' in rv.data
    assert rv.status_code == 500
