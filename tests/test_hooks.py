# -*- coding: utf-8 -*-
"""Test GitHub webhooks."""

from frost.hooks import hooks
import flask
import json
import pytest


@pytest.fixture
def client():
    app = flask.Flask(__name__)
    app.register_blueprint(hooks)
    app.config['DEBUG'] = True
    app.config['VALIDATE_IP'] = False
    app.config['VALIDATE_SIGNATURE'] = False
    return app.test_client()


def post(client, hook, data, guid='abc'):
    headers = {
        'X-GitHub-Event': hook,
        'X-GitHub-Delivery': guid,
    }
    return client.post('/hooks', content_type='application/json',
                       data=json.dumps(data), headers=headers)


def test_ping(client):
    rv = post(client, 'ping', {})
    assert rv.data == b'pong\n'
    assert rv.status_code == 200


def test_unused(client):
    rv = post(client, 'push', {})
    assert rv.data == b'Hook not used\n'
    assert rv.status_code == 200


def test_bad_request(client):
    rv = client.post('/hooks')
    assert rv.data == b'hwhat\n'
    assert rv.status_code == 400
