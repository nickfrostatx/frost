# -*- coding: utf-8 -*-
"""Test HTML views."""

from frost.views import views
from util import serving_app, db
import frost.github
import contextlib
import flask
import pytest


@pytest.fixture
def client():
    app = flask.Flask(__name__)
    app.config['GITHUB_CLIENT_ID'] = 'deadbeefcafe'
    app.config['GITHUB_CLIENT_SECRET'] = 'sekrit'
    app.github = frost.github.GitHub(app)
    app.register_blueprint(views)
    return app.test_client()


@contextlib.contextmanager
def user_set(app, user):
    """Manually set g.user."""
    def handler(sender, **kwargs):
        flask.g.user = user
    with flask.appcontext_pushed.connected_to(handler, app):
        yield


def test_home(client, db):
    rv = client.get('/')
    assert rv.status_code == 200


def test_login(client, db):
    base = ('https://github.com/login/oauth/authorize?client_id=deadbeefcafe'
            '&scopes=write%3Arepo_hook%2Crepo%3Astatus%2Crepo_deployment%2C'
            'read%3Aorg&state=my+unique++state+str'
            '&redirect_uri=http%3A%2F%2Flocalhost%2Foauth')

    rv = client.post('/login')
    assert rv.headers.get('Location') == base

    rv = client.post('/login', headers={'Referer': '/abc'})
    assert rv.headers.get('Location') == base

    rv = client.post('/login', headers={'Referer': 'http://example.com/abc'})
    assert rv.headers.get('Location') == base

    rv = client.post('/login', headers={'Referer': 'http://localhost:5000/ab'})
    assert rv.headers.get('Location') == base

    rv = client.post('/login', headers={'Referer': 'http://localhost/abc'})
    assert rv.headers.get('Location') == base + '%3Fnext%3D%252Fabc'


def test_oauth(client, db, serving_app):
    client.application.github.base_url = serving_app.url

    @serving_app.route('/login/oauth/access_token', methods=['POST'])
    def access_token():
        return flask.jsonify({'access_token': flask.request.args['code']})

    client.application.github.get_access_token('mycode')

    rv = client.get('/oauth?state=my+unique++state+str&code=mycode')
    assert rv.headers.get('Location') == 'http://localhost/'

    rv = client.get('/oauth?state=my+unique++state+str&code=mycode&next=/abc')
    assert rv.headers.get('Location') == 'http://localhost/abc'

    rv = client.get('/oauth?state=my+unique++state+str&code=mycode&next=abc')
    assert rv.headers.get('Location') == 'http://localhost/'

    rv = client.get('/oauth?state=my+unique++state+str&code=mycode&next='
                    'http%3A%2F%2Fabc')
    assert rv.headers.get('Location') == 'http://localhost/'

    rv = client.get('/oauth?state=my+unique++state+str&code=mycode&next='
                    'http%3A%2F%2F%2Fabc')
    assert rv.headers.get('Location') == 'http://localhost/'

    rv = client.get('/oauth?state=my+unique++state+str&code=mycode&next='
                    'http%3A%2F%2Flocalhost%2Fabc')
    assert rv.headers.get('Location') == 'http://localhost/'


def test_oauth_400(client, db):
    rv = client.get('/oauth?code=mycode')
    assert rv.status_code == 400

    rv = client.get('/oauth?state=&code=mycode')
    assert rv.status_code == 400

    rv = client.get('/oauth?state=fake&code=mycode')
    assert rv.status_code == 400


def test_oauth_503(client, db):
    client.application.github.base_url = 'http://0.0.0.0:1234'
    rv = client.get('/oauth?state=my+unique++state+str&code=mycode')
    assert rv.status_code == 503


def test_home_invalid_user(client, db):
    with user_set(client.application, 'fakeuser'):
        rv = client.get('/')
        # assert rv.status_code == 500


def test_repo_page(client, db):
    rv = client.get('/nickfrostatx/frost')
    assert b'nickfrostatx' in rv.data
    assert b'frost' in rv.data
    assert rv.status_code == 200


def test_invalid_repo_page(client, db):
    rv = client.get('/nickfrostatx/fakerepo')
    assert rv.status_code == 404

    rv = client.get('/fakeuser/fakerepo')
    assert rv.status_code == 404
