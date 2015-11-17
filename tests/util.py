# -*- coding: utf-8 -*-
"""Shared utility functions."""

from werkzeug.serving import ThreadedWSGIServer
import flask
import pytest
import random
import threading


@pytest.fixture
def serving_app(request):
    """Create a Flask app and serve it over some port 8xxx.

    This will be used to pretend to be GitHub, so we can see test what
    happens when GitHub returns unexpected responses. When the test
    ends, the server is destroyed.
    """
    host = '127.0.0.1'
    port = random.randint(8000, 8999)
    app = flask.Flask(__name__)
    app.debug = True

    app.url = 'http://{0}:{1}'.format(host, port)
    server = ThreadedWSGIServer(host, port, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    request.addfinalizer(server.shutdown)
    return app
