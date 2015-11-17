# -*- coding: utf-8 -*-
"""Test the GitHub API."""

from util import serving_app
import flask
import frost.exceptions
import frost.github
import pytest


@pytest.fixture
def github():
    """Create a GitHub client"""
    app = flask.Flask(__name__)
    app.config['GITHUB_CLIENT_ID'] = 'deadbeefcafe'
    app.config['GITHUB_CLIENT_SECRET'] = 'sekrit'

    return frost.github.GitHub(app)


def test_github_setup(github):
    assert github.client_id == 'deadbeefcafe'
    assert github.client_secret == 'sekrit'
    github.app.config['GITHUB_CLIENT_ID'] = 'abc'
    github.app.config['GITHUB_CLIENT_SECRET'] = 'seeecret'
    assert github.client_id == 'abc'
    assert github.client_secret == 'seeecret'


def test_make_request(github, serving_app):
    github.base_url = serving_app.url

    @serving_app.route('/')
    def home():
        data = {
            'accept': flask.request.headers.get('Accept'),
            'something': flask.request.headers.get('X-Something'),
        }
        return flask.jsonify(data)

    data = github.make_request('GET', '/')
    assert data == {'accept': 'application/json',
                    'something': None,
                    }

    headers = {'X-Something': 'abc'}
    data = github.make_request('GET', '/', headers=headers)
    assert data == {'accept': 'application/json',
                    'something': 'abc',
                    }

    headers = {
        'Accept': 'text/html',
        'X-Something': 'abc',
    }
    data = github.make_request('GET', '/', headers=headers)
    assert data == {'accept': 'application/json',
                    'something': 'abc',
                    }


def test_no_connection(github):
    with pytest.raises(frost.exceptions.GitHubError) as exc:
        github.base_url = 'http://0.0.0.0:1234'
        github.make_request('GET', '/')
    assert 'Failed to communicate with GitHub' in str(exc)


def test_bad_status(github, serving_app):
    github.base_url = serving_app.url

    @serving_app.route('/')
    def home():
        return flask.jsonify({'message': 'No sir.'}), 400

    @serving_app.route('/nomsg')
    def nomsg():
        return flask.jsonify({}), 400

    with pytest.raises(frost.exceptions.GitHubError) as exc:
        github.make_request('GET', '/')
    assert '400: No sir.' in str(exc)

    with pytest.raises(frost.exceptions.GitHubError) as exc:
        github.make_request('GET', '/nomsg')
    assert 'Failed to communicate with GitHub' in str(exc)


def test_invalid_json(github, serving_app):
    github.base_url = serving_app.url

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
        with pytest.raises(frost.exceptions.GitHubError) as exc:
            github.make_request('GET', url)
        assert 'Failed to communicate with GitHub' in str(exc)


def test_get_access_token(github, serving_app):
    github.base_url = serving_app.url

    @serving_app.route('/login/oauth/access_token', methods=['POST'])
    def missing():
        client_id = flask.request.args.get('client_id')
        client_secret = flask.request.args.get('client_secret')
        if client_id != 'deadbeefcafe' or client_secret != 'sekrit':
            return jsonify({}), 403

        code = flask.request.args.get('code', '')
        if code == 'bad_request':
            return flask.jsonify({}), 400
        elif code == 'missing':
            return flask.jsonify({})
        elif code == 'bad_type':
            return flask.jsonify({'access_token': 123})
        elif code == 'bad_type2':
            return flask.jsonify({'access_token': ['ab', 'cd']})
        else:
            return flask.jsonify({'access_token': code + code})

    for t in ('bad_request', 'missing', 'bad_type', 'bad_type2'):
        with pytest.raises(frost.exceptions.GitHubError) as exc:
            github.get_access_token(t)
        assert 'Failed to communicate with GitHub' in str(exc)

    access_token = github.get_access_token('mycode')
    assert access_token == 'mycodemycode'
