# -*- coding: utf-8 -*-
"""Test utility functions."""

import flask
import frost.exceptions
import frost.util
import pytest


def test_get_repos():
    repos = frost.util.get_repos('nickfrostatx')
    assert len(repos) == 4


def test_invalid_user():
    with pytest.raises(frost.exceptions.NoSuchUserException):
        frost.util.get_repos('fakeuser')


def test_get_repo():
    repo = frost.util.get_repo('nickfrostatx', 'frost')
    assert repo['status'] == 'passing'


def test_invalid_repos():
    with pytest.raises(frost.exceptions.NoSuchUserException):
        frost.util.get_repo('fakeuser', 'fakerepo')

    with pytest.raises(frost.exceptions.NoSuchRepoException):
        frost.util.get_repo('nickfrostatx', 'fakerepo')


def test_nocache():
    app = flask.Flask(__name__)

    @app.route('/')
    @frost.util.nocache
    def home():
        return 'Hello\n'

    with app.test_client() as client:
        rv = client.get('/')
        assert rv.data == b'Hello\n'
        assert rv.status_code == 200
        assert 'ETag' not in rv.headers
        assert 'Last-Modified' not in rv.headers
        assert rv.headers['Cache-Control'] == ('no-store, no-cache, '
                                               'must-revalidate')
        assert rv.headers['Pragma'] == 'no-cache'
