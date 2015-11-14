# -*- coding: utf-8 -*-
"""Utility functions."""

from datetime import datetime, timedelta
from flask import make_response
from functools import wraps
from werkzeug.http import http_date
from . import exceptions


_repos = {
    'nickfrostatx': {
        'frost': {
            'user': 'nickfrostatx',
            'name': 'frost',
            'status': 'passing',
            'build_status': 'passing',
        },
        'flask-hookserver': {
            'user': 'nickfrostatx',
            'name': 'flask-hookserver',
            'status': 'progress',
            'build_status': 'error',
        },
        'nass': {
            'user': 'nickfrostatx',
            'name': 'nass',
            'status': 'failing',
            'build_status': 'failing',
        },
        'corral': {
            'user': 'nickfrostatx',
            'name': 'corral',
            'status': 'inactive',
            'build_status': 'unknown',
        },
    },
    'error': {
        'error': {
            'user': 'error',
            'name': 'error',
        },
    },
}


def get_repos(user):
    """Return all the repos for a given user."""
    if user not in _repos:
        raise exceptions.NoSuchUserException()
    return _repos[user]


def get_repo(user, repo):
    """Return the repo owned by user with the name repo."""
    if user not in _repos:
        raise exceptions.NoSuchUserException()
    if repo not in _repos[user]:
        raise exceptions.NoSuchRepoException()
    return _repos[user][repo]


def nocache(fn):
    """Decorate the view fn to override Cache-Control header."""
    @wraps(fn)
    def wrapped(*a, **kw):
        resp = make_response(fn(*a, **kw))
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = http_date(datetime.now() - timedelta(0, 2))
        del resp.headers['ETag']
        del resp.headers['Last-Modified']
        return resp
    return wrapped
