# -*- coding: utf-8 -*-
"""Test utility functions."""

import flask
import frost.util
import json
try:
    from urllib.parse import quote
except ImportError:
    from urlparse import quote


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


def test_is_safe_url_absolute():
    app = flask.Flask(__name__)

    @app.route('/url')
    def home():
        safe = False
        if flask.request.referrer:
            safe = frost.util.is_safe_url(flask.request.referrer, False)
        return flask.jsonify({'safe': safe})

    with app.test_client() as client:
        def is_safe(referrer=None):
            headers = None
            if referrer:
                headers = {'Referer': referrer}
            rv = client.get('/url', headers=headers)
            return json.loads(rv.data.decode('utf-8'))['safe']

        assert is_safe() == False
        assert is_safe('') == False
        assert is_safe('/') == False
        assert is_safe('abc') == False
        assert is_safe('/abc') == False
        assert is_safe('/url') == False
        assert is_safe('http://example.com') == False
        assert is_safe('http://example.com/abc') == False
        assert is_safe('http://localhost:1234/abc') == False
        assert is_safe('http://localhost/') == True
        assert is_safe('http://localhost') == False
        assert is_safe('ftp://localhost/abc') == False
        assert is_safe('http://localhost/abc') == True
        assert is_safe('http://localhost/url') == False


def test_is_safe_url_relative():
    app = flask.Flask(__name__)
    app.debug = True

    @app.route('/url')
    def home():
        safe = False
        next = flask.request.args.get('next')
        if next:
            safe = frost.util.is_safe_url(next, True)
        return flask.jsonify({'safe': safe})

    with app.test_client() as client:
        def is_safe(next=None):
            url = '/url'
            if next:
                url += '?next=' + quote(next, safe='')
            rv = client.get(url)
            return json.loads(rv.data.decode('utf-8'))['safe']

        assert is_safe() == False
        assert is_safe('') == False
        assert is_safe('/') == True
        assert is_safe('abc') == False
        assert is_safe('/abc') == True
        assert is_safe('/url') == False
        assert is_safe('http://abc') == False
        assert is_safe('http://example.com') == False
        assert is_safe('http://example.com/abc') == False
        assert is_safe('http://localhost:1234/abc') == False
        assert is_safe('http://localhost/') == False
        assert is_safe('http://localhost') == False
        assert is_safe('ftp://localhost/abc') == False
        assert is_safe('http://localhost/abc') == False
