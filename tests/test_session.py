# -*- coding: utf-8 -*-
"""Test session."""

from util import db
import flask
import frost.session
import json
import pytest


@pytest.fixture
def client():
    app = flask.Flask(__name__)
    app.debug = True
    app.session_interface = frost.session.RedisSessionInterface()

    @app.route('/')
    def home():
        return flask.jsonify({
            'data': dict(flask.session),
            'sid': flask.session.sid,
        })

    @app.route('/update', methods=['PUT'])
    def update():
        for k, v in flask.request.get_json().items():
            flask.session[k] = v
        return home()

    @app.route('/logout', methods=['POST'])
    def logout():
        flask.session.clear()
        return home()

    @app.route('/rotate', methods=['PUT'])
    def rotate():
        for k, v in flask.request.get_json().items():
            flask.session[k] = v
        flask.session.rotate = True
        return home()

    return app.test_client()


def test_default_session(client, db):
    rv = client.get('/')
    data = json.loads(rv.data.decode())
    sid = data['sid']
    assert len(sid) == 64
    assert len(data['data']) == 1
    csrf = data['data']['csrf']
    assert len(csrf) == 64
    assert rv.status_code == 200

    rv = client.get('/')
    data = json.loads(rv.data.decode())
    assert data['sid'] == sid
    assert len(data['data']) == 1
    assert data['data']['csrf'] == csrf
    assert rv.status_code == 200


def test_unauthed_session(client, db):
    rv = client.get('/', headers={'Cookie': 'session=noauth'})
    data = json.loads(rv.data.decode())
    assert data['sid'] == 'noauth'
    assert data['data'] == {
        'csrf': 'somecsrf',
    }
    assert rv.status_code == 200


def test_authed_session(client, db):
    rv = client.get('/', headers={'Cookie': 'session=auth'})
    data = json.loads(rv.data.decode())
    assert data['sid'] == 'auth'
    assert data['data'] == {
        'csrf': 'coolcsrf',
        'user': 'nickfrostatx',
    }
    assert rv.status_code == 200


def test_invalid_session(client, db):
    rv = client.get('/', headers={'Cookie': 'session=fake'})
    data = json.loads(rv.data.decode())
    assert data['sid'] != 'fake'
    assert len(data['sid']) == 64
    assert len(data['data']['csrf']) == 64
    assert 'session=' in rv.headers['Set-Cookie']
    assert rv.status_code == 200


def test_change_session(client, db):
    headers = {
        'Cookie': 'session=auth',
        'Content-Type': 'application/json',
    }
    rv = client.put('/update', headers=headers, data='{"csrf":"abc","a":"b"}')
    data = json.loads(rv.data.decode())
    assert data['sid'] == 'auth'
    assert data['data'] == {
        'csrf': 'abc',
        'user': 'nickfrostatx',
        'a': 'b',
    }
    assert db.hgetall('session:auth') == {
        b'csrf': b'abc',
        b'user': b'nickfrostatx',
        b'a': b'b',
    }


def test_delete_session(client, db):
    rv = client.post('/logout', headers={'Cookie': 'session=auth'})
    data = json.loads(rv.data.decode())
    assert data['sid'] == 'auth'
    assert data['data'] == {}
    assert db.hgetall('session:auth') == {}
    assert 'Expires=Thu, 01-Jan-1970 00:00:00 GMT' in rv.headers['Set-Cookie']


def test_rotate_session(client, db):
    headers = {
        'Cookie': 'session=auth',
        'Content-Type': 'application/json',
    }
    rv = client.put('/rotate', headers=headers, data='{"csrf":"abc","a":"b"}')
    data = json.loads(rv.data.decode())
    assert 'session=auth' not in rv.headers['Set-Cookie']
    assert data['data'] == {
        'csrf': 'abc',
        'user': 'nickfrostatx',
        'a': 'b',
    }
    assert db.exists('session:auth') == False
    sid = rv.headers['Set-Cookie'][8:72]
    assert db.hgetall('session:{0}'.format(sid)) == {
        b'csrf': b'abc',
        b'user': b'nickfrostatx',
        b'a': b'b',
    }


def test_rotate_new_session(client, db):
    headers = {
        'Content-Type': 'application/json',
    }
    rv = client.put('/rotate', headers=headers, data='{"csrf":"abc","a":"b"}')
    data = json.loads(rv.data.decode())
    assert len(data['sid']) == 64
    assert 'session={0}'.format(data['sid']) in rv.headers['Set-Cookie']
    assert data['data'] == {
        'csrf': 'abc',
        'a': 'b',
    }
    assert db.hgetall('session:{0}'.format(data['sid'])) == {
        b'csrf': b'abc',
        b'a': b'b',
    }
