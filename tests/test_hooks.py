# -*- coding: utf-8 -*-
"""Test GitHub webhooks."""

from frost.hooks import hooks
import flask
import json
import pytest


def hook_client(hooks):
    server = flask.Flask(__name__)
    server.register_blueprint(hooks)
    server.config['DEBUG'] = True
    server.config['VALIDATE_IP'] = False
    server.config['VALIDATE_SIGNATURE'] = False
    return server.test_client()


def post(client, hook, data, guid='abc'):
    headers = {
        'X-GitHub-Event': hook,
        'X-GitHub-Delivery': guid,
    }
    return client.post('/hooks', content_type='application/json',
                       data=json.dumps(data), headers=headers)


def test_ping():
    with hook_client(hooks) as client:
        rv = post(client, 'ping', {})
        assert rv.data == b'pong\n'
        assert rv.status_code == 200


def test_unused():
    with hook_client(hooks) as client:
        rv = post(client, 'push', {})
        assert rv.data == b'Hook not used\n'
        assert rv.status_code == 200


def test_bad_request():
    with hook_client(hooks) as client:
        rv = client.post('/hooks')
        assert rv.data == b'hwhat\n'
        assert rv.status_code == 400
