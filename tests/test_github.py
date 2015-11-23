# -*- coding: utf-8 -*-
"""Test the GitHub API."""

from frost.github import _github_request, _get_string_from_json, \
                         get_access_token, get_user
from util import serving_app
import flask
import pytest


def test_make_request(monkeypatch, serving_app):
    monkeypatch.setattr('frost.github.BASE_URL', serving_app.url)
    monkeypatch.setattr('frost.github.API_URL', serving_app.url + '/api')

    @serving_app.route('/')
    def home():
        return flask.jsonify({'msg': 'The base domain.'})

    @serving_app.route('/api/')
    def api():
        data = {
            'accept': flask.request.headers.get('Accept'),
            'something': flask.request.headers.get('X-Something'),
        }
        return flask.jsonify(data)

    data = _github_request('GET', '/', base=serving_app.url)
    assert data == {
        'msg': 'The base domain.',
    }

    data = _github_request('GET', '/')
    assert data == {
        'accept': 'application/json',
        'something': None,
    }

    headers = {'X-Something': 'abc'}
    data = _github_request('GET', '/', headers=headers)
    assert data == {
        'accept': 'application/json',
        'something': 'abc',
    }

    headers = {
        'Accept': 'text/html',
        'X-Something': 'abc',
    }
    data = _github_request('GET', '/', headers=headers)
    assert data == {
        'accept': 'text/html',
        'something': 'abc',
    }


def test_no_connection(monkeypatch):
    with pytest.raises(Exception) as exc:
        monkeypatch.setattr('frost.github.API_URL', 'http://0.0.0.0:1234')
        _github_request('GET', '/')
    assert 'Failed to communicate with GitHub' in str(exc)


def test_bad_status(monkeypatch, serving_app):
    monkeypatch.setattr('frost.github.API_URL', serving_app.url)

    @serving_app.route('/')
    def home():
        return flask.jsonify({'message': 'I\'m a teapot.'}), 418

    @serving_app.route('/badtype')
    def badtype():
        headers = {
            'Content-Type': 'application/json',
        }
        return '""', 418, headers

    @serving_app.route('/nomsg')
    def nomsg():
        return flask.jsonify({}), 418

    with pytest.raises(Exception) as exc:
        _github_request('GET', '/')
    assert '418: I\'m a teapot.' in str(exc)

    with pytest.raises(Exception) as exc:
        _github_request('GET', '/badtype')
    assert '418: <no error message>' in str(exc)

    with pytest.raises(Exception) as exc:
        _github_request('GET', '/nomsg')
    assert '418: <no error message>' in str(exc)


def test_invalid_json(monkeypatch, serving_app):
    monkeypatch.setattr('frost.github.API_URL', serving_app.url)

    @serving_app.route('/text')
    def home():
        return 'Home\n'

    @serving_app.route('/invalid')
    def fake_content_type():
        headers = {
            'Content-Type': 'application/json',
        }
        return 'Home\n', headers

    for url in ('/text', '/invalid'):
        with pytest.raises(Exception) as exc:
            _github_request('GET', url)
        assert 'GitHub returned bad JSON' in str(exc)


def test_get_string_from_json():
    assert _get_string_from_json({'msg': 'Something'}, 'msg') == 'Something'

    for data in ({}, '', {'msg': 123}, {'msg': ['ab', 'cd']}):
        with pytest.raises(Exception) as exc:
            _get_string_from_json(data, 'msg')
        assert 'GitHub response was missing "msg"' in str(exc)


def test_get_access_token(monkeypatch, serving_app):
    monkeypatch.setattr('frost.github.BASE_URL', serving_app.url)

    @serving_app.route('/login/oauth/access_token', methods=['POST'])
    def missing():
        client_id = flask.request.args.get('client_id')
        client_secret = flask.request.args.get('client_secret')
        if client_id != 'deadbeefcafe' or client_secret != 'sekrit':
            return flask.jsonify({'message': 'Bad credentials'}), 401

        code = flask.request.args.get('code', '')
        if code == 'teapot':
            return flask.jsonify({}), 418
        elif code == 'missing':
            return flask.jsonify({})
        else:
            return flask.jsonify({'access_token': code + code})

    with pytest.raises(Exception) as exc:
        get_access_token('teapot', 'fake', 'fake')
    assert '401: Bad credentials' in str(exc)

    with pytest.raises(Exception) as exc:
        get_access_token('teapot', 'deadbeefcafe', 'sekrit')
    assert '418: <no error message>' in str(exc)

    with pytest.raises(Exception) as exc:
        get_access_token('missing', 'deadbeefcafe', 'sekrit')
    assert 'GitHub response was missing "access_token"' in str(exc)

    access_token = get_access_token('mycode', 'deadbeefcafe', 'sekrit')
    assert access_token == 'mycodemycode'


def test_get_user(monkeypatch, serving_app):
    monkeypatch.setattr('frost.github.API_URL', serving_app.url)

    @serving_app.route('/user')
    def user():
        authorization = flask.request.headers.get('authorization', '')
        assert authorization.startswith('token ')
        code = authorization[6:]

        if code == 'teapot':
            return flask.jsonify({}), 418
        elif code == 'missing':
            return flask.jsonify({})
        else:
            return flask.jsonify({'login': code + code})

    with pytest.raises(Exception) as exc:
        get_user('teapot')
    assert '418: <no error message>' in str(exc)

    with pytest.raises(Exception) as exc:
        get_user('missing')
    assert 'GitHub response was missing "login"' in str(exc)

    user = get_user('mycode')
    assert user == 'mycodemycode'
