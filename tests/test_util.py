# -*- coding: utf-8 -*-
"""Test utility functions."""

import flask
import frost.util


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
