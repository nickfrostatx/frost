# -*- coding: utf-8 -*-
"""The model."""

from datetime import datetime
from . import exceptions


_repos = {
    'nickfrostatx': {
        'frost': {
            'user': 'nickfrostatx',
            'name': 'frost',
            'status': 'passing',
            'build_status': 'passing',
            'last_update': datetime(2015, 11, 14, 11, 30, 43),
        },
        'flask-hookserver': {
            'user': 'nickfrostatx',
            'name': 'flask-hookserver',
            'status': 'progress',
            'build_status': 'error',
            'last_update': datetime(2015, 11, 14, 11, 20, 15),
        },
        'nass': {
            'user': 'nickfrostatx',
            'name': 'nass',
            'status': 'failing',
            'build_status': 'failing',
            'last_update': datetime(2015, 11, 14, 11, 10, 27),
        },
        'corral': {
            'user': 'nickfrostatx',
            'name': 'corral',
            'status': 'inactive',
            'build_status': 'unknown',
            'last_update': datetime(2015, 11, 14, 11, 0, 5),
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
    """Return all the repos for a given user, sorted by last_update."""
    if user not in _repos:
        raise exceptions.NoSuchUserException()
    return sorted(_repos[user].values(),
                  key=lambda r: r['last_update'], reverse=True)


def get_repo(user, repo):
    """Return the repo owned by user with the name repo."""
    if user not in _repos:
        raise exceptions.NoSuchUserException()
    if repo not in _repos[user]:
        raise exceptions.NoSuchRepoException()
    return _repos[user][repo]
