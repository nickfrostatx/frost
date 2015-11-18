# -*- coding: utf-8 -*-
"""Test HTML views."""

from frost.views import views
from util import serving_app, db
import frost.github
import frost.model
import contextlib
import flask
import pytest


@pytest.fixture
def client():
    app = flask.Flask(__name__)
    app.config['GITHUB_CLIENT_ID'] = 'deadbeefcafe'
    app.config['GITHUB_CLIENT_SECRET'] = 'sekrit'
    app.config['DEBUG'] = True
    app.github = frost.github.GitHub(app)
    app.register_blueprint(views)
    return app.test_client()


def test_login(client, db):
    base = ('https://github.com/login/oauth/authorize?client_id=deadbeefcafe'
            '&scopes=write%3Arepo_hook%2Crepo%3Astatus%2Crepo_deployment%2C'
            'read%3Aorg&state=somecsrf'
            '&redirect_uri=http%3A%2F%2Flocalhost%2Foauth')

    client.set_cookie('localhost', 'session', 'noauth')
    url = '/login?state=somecsrf'

    rv = client.get(url)
    assert rv.headers.get('Location') == base

    rv = client.get(url, headers={'Referer': '/abc'})
    assert rv.headers.get('Location') == base

    rv = client.get(url, headers={'Referer': 'http://example.com/abc'})
    assert rv.headers.get('Location') == base

    rv = client.get(url, headers={'Referer': 'http://localhost:5000/ab'})
    assert rv.headers.get('Location') == base

    rv = client.get(url, headers={'Referer': 'http://localhost/abc'})
    assert rv.headers.get('Location') == base + '%3Fnext%3D%252Fabc'


def test_oauth_403(client, db):
    rv = client.get('/login?code=mycode')
    assert rv.status_code == 403

    rv = client.get('/login?state=&code=mycode')
    assert rv.status_code == 403

    rv = client.get('/login?state=fake&code=mycode')
    assert rv.status_code == 403


def test_oauth(client, db, serving_app):
    client.application.github.base_url = serving_app.url
    client.application.github.api_url = serving_app.url + '/api'

    @serving_app.route('/login/oauth/access_token', methods=['POST'])
    def access_token():
        return flask.jsonify({'access_token': flask.request.args['code']})

    @serving_app.route('/api/user')
    def user():
        return flask.jsonify({'login': 'someuser'})

    client.set_cookie('localhost', 'session', 'noauth')

    rv = client.get('/oauth?state=somecsrf&code=mycode')
    assert rv.headers.get('Location') == 'http://localhost/'

    rv = client.get('/oauth?state=somecsrf&code=mycode&next=/abc')
    assert rv.headers.get('Location') == 'http://localhost/abc'

    rv = client.get('/oauth?state=somecsrf&code=mycode&next=abc')
    assert rv.headers.get('Location') == 'http://localhost/'

    rv = client.get('/oauth?state=somecsrf&code=mycode&next='
                    'http%3A%2F%2Fabc')
    assert rv.headers.get('Location') == 'http://localhost/'

    rv = client.get('/oauth?state=somecsrf&code=mycode&next='
                    'http%3A%2F%2F%2Fabc')
    assert rv.headers.get('Location') == 'http://localhost/'

    rv = client.get('/oauth?state=somecsrf&code=mycode&next='
                    'http%3A%2F%2Flocalhost%2Fabc')
    assert rv.headers.get('Location') == 'http://localhost/'

    assert frost.model.get_session_data('noauth') == {
        'csrf': 'somecsrf',
        'user': 'someuser',
    }
    assert frost.model.user_exists('someuser')


def test_oauth_existing(client, db, serving_app):
    client.application.github.base_url = serving_app.url
    client.application.github.api_url = serving_app.url + '/api'

    @serving_app.route('/login/oauth/access_token', methods=['POST'])
    def access_token():
        return flask.jsonify({'access_token': flask.request.args['code']})

    @serving_app.route('/api/user')
    def user():
        return flask.jsonify({'login': 'nickfrostatx'})

    client.set_cookie('localhost', 'session', 'noauth')

    rv = client.get('/oauth?state=somecsrf&code=mycode')
    assert rv.headers.get('Location') == 'http://localhost/'

    assert frost.model.get_session_data('noauth') == {
        'csrf': 'somecsrf',
        'user': 'nickfrostatx',
    }


def test_oauth_403(client, db):
    rv = client.get('/oauth?code=mycode')
    assert rv.status_code == 403

    rv = client.get('/oauth?state=&code=mycode')
    assert rv.status_code == 403

    rv = client.get('/oauth?state=fake&code=mycode')
    assert rv.status_code == 403


def test_oauth_503(client, db, serving_app):
    client.application.github.base_url = 'http://0.0.0.0:1234'
    client.application.github.api_url = 'http://0.0.0.0:1234'

    @serving_app.route('/login/oauth/access_token', methods=['POST'])
    def access_token():
        return flask.jsonify({'access_token': flask.request.args['code']})

    client.set_cookie('localhost', 'session', 'noauth')

    rv = client.get('/oauth?state=somecsrf&code=mycode')
    assert rv.status_code == 503

    client.application.github.base_url = serving_app.url
    rv = client.get('/oauth?state=somecsrf&code=mycode')
    assert rv.status_code == 503


def test_home_unauthed(client, db):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'class="auth-btn"' in rv.data


def test_home_authed(client, db):
    client.set_cookie('localhost', 'session', 'auth')

    rv = client.get('/')
    assert rv.status_code == 200
    assert b'nickfrostatx/frost' in rv.data
    assert b'nickfrostatx/flask-hookserver' in rv.data


def test_repo_page(client, db):
    rv = client.get('/nickfrostatx/frost')
    assert b'/nickfrostatx/frost' in rv.data
    assert rv.status_code == 200


def test_invalid_repo_page(client, db):
    rv = client.get('/nickfrostatx/fakerepo')
    assert rv.status_code == 404

    rv = client.get('/fakeuser/fakerepo')
    assert rv.status_code == 404
