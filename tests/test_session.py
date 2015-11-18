# -*- coding: utf-8 -*-
"""Test session."""

import flask
import frost.session
import json
import pytest
from util import db


@pytest.fixture
def client():
    app = flask.Flask(__name__)

    app.before_request(frost.session.init_session)
    app.after_request(frost.session.save_session)

    @app.route('/')
    def home():
        return flask.jsonify(flask.g.session)

    return app.test_client()


def test_default_session(client, db):
    rv = client.get('/')
    data = json.loads(rv.data.decode())
    assert len(data) == 1
    csrf = data['csrf']
    assert len(csrf) == 64
    assert rv.status_code == 200

    rv = client.get()
    data = json.loads(rv.data.decode())
    assert len(data) == 1
    assert data['csrf'] == csrf
    assert rv.status_code == 200


def test_unauthed_session(client, db):
    rv = client.get('/', headers={'Cookie': 'session=noauth'})
    data = json.loads(rv.data.decode())
    assert data == {
        'csrf': 'somecsrf',
    }
    assert rv.status_code == 200


def test_authed_session(client, db):
    rv = client.get('/', headers={'Cookie': 'session=auth'})
    data = json.loads(rv.data.decode())
    assert data == {
        'csrf': 'coolcsrf',
        'user': 'nickfrostatx',
    }
    assert rv.status_code == 200


def test_invalid_session(client, db):
    rv = client.get('/', headers={'Cookie': 'session=fake'})
    data = json.loads(rv.data.decode())
    assert len(data['csrf']) == 64
    assert rv.status_code == 200
