# -*- coding: utf-8 -*-
"""Test error handling."""

from frost.error import register_error_handler, html_handler
import flask
import werkzeug.exceptions


def test_custom_handler():
    app = flask.Flask(__name__)
    client = app.test_client()

    def handler(e):
        return e.name + '\n', e.code

    register_error_handler(app, handler, include_500=True)

    @app.route('/good')
    def good():
        return 'OK'

    @app.route('/418')
    def teapot():
        flask.abort(418)

    @app.route('/500')
    def internal():
        raise werkzeug.exceptions.InternalServerError()

    @app.route('/internal')
    def divide_by_zero():
        1/0

    rv = client.get('/good')
    assert rv.status_code == 200

    rv = client.get('/418')
    assert rv.data == b'I\'m a teapot\n'
    assert rv.status_code == 418

    rv = client.get('/500')
    assert rv.data == b'Internal Server Error\n'
    assert rv.status_code == 500

    rv = client.get('/internal')
    assert rv.data == b'Internal Server Error\n'
    assert rv.status_code == 500


def test_html_handler():
    app = flask.Flask(__name__, template_folder='../frost/templates')
    client = app.test_client()
    register_error_handler(app, html_handler, include_500=True)

    @app.route('/good')
    def good():
        return 'OK'

    @app.route('/418')
    def teapot():
        flask.abort(418)

    @app.route('/internal')
    def divide_by_zero():
        1/0

    rv = client.get('/good')
    assert rv.status_code == 200

    rv = client.get('/418')
    assert b'<title>Frost CI - I&#39;m a teapot</title>' in rv.data
    assert b'<h1>Error 418</h1>' in rv.data
    assert rv.status_code == 418

    rv = client.get('/internal')
    assert b'<title>Frost CI - Internal Server Error</title>' in rv.data
    assert b'<h1>Error 500</h1>' in rv.data
    assert rv.status_code == 500


def test_not_500():
    app = flask.Flask(__name__)
    client = app.test_client()

    def handler(e):
        return e.name + '\n', e.code
    register_error_handler(app, handler, include_500=False)

    @app.route('/internal')
    def divide_by_zero():
        1/0

    rv = client.get('/internal')
    assert b'<!DOCTYPE HTML PUBLIC' in rv.data
    assert rv.status_code == 500
