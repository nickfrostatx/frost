# -*- coding: utf-8 -*-
"""Test utility functions."""

import flask
import frost.util
import json


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


def test_is_safe_url():
    app = flask.Flask(__name__)

    @app.route('/')
    def home():
        safe = False
        if flask.request.referrer:
            safe = frost.util.is_safe_url(flask.request.referrer)
        return flask.jsonify({'safe': safe})

    with app.test_client() as client:
        rv = client.get('/')
        assert json.loads(rv.data.decode('utf-8'))['safe'] == False

        rv = client.get('/', headers={'Referer': 'http://example.com/abc'})
        assert json.loads(rv.data.decode('utf-8'))['safe'] == False

        rv = client.get('/', headers={'Referer': 'http://localhost:1234/abc'})
        assert json.loads(rv.data.decode('utf-8'))['safe'] == False

        rv = client.get('/', headers={'Referer': 'http://localhost/'})
        assert json.loads(rv.data.decode('utf-8'))['safe'] == False

        rv = client.get('/', headers={'Referer': 'http://localhost'})
        assert json.loads(rv.data.decode('utf-8'))['safe'] == True

        rv = client.get('/', headers={'Referer': 'http://localhost/abc'})
        assert json.loads(rv.data.decode('utf-8'))['safe'] == True
