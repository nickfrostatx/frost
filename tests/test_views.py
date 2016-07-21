# -*- coding: utf-8 -*-
"""Test HTML views."""

from util import serving_app, db
import frost.github
import frost.model
import frost.session
import frost.views
import flask
import pytest


@pytest.fixture
def client():
    app = flask.Flask(__name__)
    app.config['GITHUB_CLIENT_ID'] = 'deadbeefcafe'
    app.config['GITHUB_CLIENT_SECRET'] = 'sekrit'
    app.config['DEBUG'] = True
    app.session_interface = frost.session.RedisSessionInterface()
    app.register_blueprint(frost.views.views)
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


def test_oauth(monkeypatch, client, db, serving_app):
    monkeypatch.setattr('frost.github.BASE_URL', serving_app.url)
    monkeypatch.setattr('frost.github.API_URL', serving_app.url + '/api')

    @serving_app.route('/login/oauth/access_token', methods=['POST'])
    def access_token():
        return flask.jsonify({'access_token': flask.request.args['code']})

    @serving_app.route('/api/user')
    def user():
        return flask.jsonify({'login': 'someuser'})

    sid = 'noauth'
    client.set_cookie('localhost', 'session', 'noauth')
    rv = client.get('/oauth?state=somecsrf&code=mycode&next=/abc')
    assert rv.headers.get('Location') == 'http://localhost/abc'
    sid = rv.headers['Set-Cookie'][8:72]

    for u in ('', 'abc', 'http://abc', 'http:///abc', 'http://localhost/abc'):
        csrf = db.hget('session:{0}'.format(sid), 'csrf').decode()
        url = '/oauth?state={0}&code=mycode'.format(csrf)
        if u:
            url += '&next=' + u
        client.set_cookie('localhost', 'session', sid)
        rv = client.get(url)
        sid = rv.headers['Set-Cookie'][8:72]
        assert rv.headers.get('Location') == 'http://localhost/'

    assert 'session=noauth' not in rv.headers['Set-Cookie']
    assert db.hget('session:{0}'.format(sid), 'user') == b'someuser'
    assert db.hget('session:{0}'.format(sid), 'csrf') != b'somecsrf'
    assert frost.model.user_exists('someuser')


def test_oauth_existing(monkeypatch, client, db, serving_app):
    monkeypatch.setattr('frost.github.BASE_URL', serving_app.url)
    monkeypatch.setattr('frost.github.API_URL', serving_app.url + '/api')

    @serving_app.route('/login/oauth/access_token', methods=['POST'])
    def access_token():
        return flask.jsonify({'access_token': flask.request.args['code']})

    @serving_app.route('/api/user')
    def user():
        return flask.jsonify({'login': 'nickfrostatx'})

    client.set_cookie('localhost', 'session', 'noauth')

    rv = client.get('/oauth?state=somecsrf&code=mycode')
    assert rv.headers.get('Location') == 'http://localhost/'

    sid = rv.headers['Set-Cookie'][8:72]
    assert db.hget('session:{0}'.format(sid), 'user') == b'nickfrostatx'
    assert db.hget('session:{0}'.format(sid), 'csrf') != b'somecsrf'


def test_oauth_403(client, db):
    rv = client.get('/oauth?code=mycode')
    assert rv.status_code == 403

    rv = client.get('/oauth?state=&code=mycode')
    assert rv.status_code == 403

    rv = client.get('/oauth?state=fake&code=mycode')
    assert rv.status_code == 403


def test_oauth_503(monkeypatch, client, db, serving_app):
    monkeypatch.setattr('frost.github.BASE_URL', 'http://0.0.0.0:1234')
    monkeypatch.setattr('frost.github.API_URL', 'http://0.0.0.0:1234')

    @serving_app.route('/login/oauth/access_token', methods=['POST'])
    def access_token():
        return flask.jsonify({'access_token': flask.request.args['code']})

    client.set_cookie('localhost', 'session', 'noauth')

    rv = client.get('/oauth?state=somecsrf&code=mycode')
    assert rv.status_code == 503

    monkeypatch.setattr('frost.github.BASE_URL', serving_app.url)
    rv = client.get('/oauth?state=somecsrf&code=mycode')
    assert rv.status_code == 503


def test_home_unauthed(client, db):
    rv = client.get('/')
    assert b'class="auth-btn"' in rv.data
    assert rv.status_code == 200


def test_home_authed(client, db):
    client.set_cookie('localhost', 'session', 'auth')

    rv = client.get('/')
    assert b'nickfrostatx/frost' in rv.data
    assert b'nickfrostatx/flask-hookserver' in rv.data
    assert rv.status_code == 200


def test_user_page(client, db):
    rv = client.get('/nickfrostatx')
    assert b'nickfrostatx/frost' in rv.data
    assert b'nickfrostatx/flask-hookserver' in rv.data
    assert rv.status_code == 200

    rv = client.get('/fakeuser')
    assert rv.status_code == 404


def test_repo_page(client, db):
    rv = client.get('/nickfrostatx/frost')
    assert b'/nickfrostatx/frost' in rv.data
    assert rv.status_code == 200


def test_invalid_repo_page(client, db):
    rv = client.get('/nickfrostatx/fakerepo')
    assert rv.status_code == 404

    rv = client.get('/fakeuser/fakerepo')
    assert rv.status_code == 404
