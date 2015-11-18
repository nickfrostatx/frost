# -*- coding: utf-8 -*-
"""Shared utility functions."""

from datetime import datetime
from werkzeug.serving import ThreadedWSGIServer
import fakeredis
import flask
import frost.model
import pytest
import random
import threading


@pytest.fixture
def db(request):
    """Inject our fake database."""
    r = fakeredis.FakeRedis()
    frost.model._redis = r

    def fin():
        frost.model._redis = None
        r.flushdb()
    request.addfinalizer(fin)

    r.hmset('repo:nickfrostatx:frost', {
        'status': 'passing',
        'build_status': 'passing',
        'last_update': datetime(2015, 11, 14, 11, 30, 43),
    })
    r.hmset('repo:nickfrostatx:flask-hookserver', {
        'status': 'progress',
        'build_status': 'error',
        'last_update': datetime(2015, 11, 14, 11, 30, 43),
    })
    r.hmset('repo:nickfrostatx:nass', {
        'status': 'failing',
        'build_status': 'failing',
        'last_update': datetime(2015, 11, 14, 11, 10, 27),
    })
    r.hmset('repo:nickfrostatx:corral', {
        'status': 'inactive',
        'build_status': 'unknown',
        'last_update': datetime(2015, 11, 14, 11, 0, 5),
    })
    r.rpush('repos:nickfrostatx', 'frost', 'flask-hookserver', 'nass',
            'corral')
    return r


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
