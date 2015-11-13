# -*- coding: utf-8 -*-
"""Utility functions."""

from . import exceptions


_repos = {
    'nickfrostatx': {
        'frost': {
            'user': 'nickfrostatx',
            'name': 'frost',
            'status': 'passing',
        },
        'flask-hookserver': {
            'user': 'nickfrostatx',
            'name': 'flask-hookserver',
            'status': 'progress',
        },
        'nass': {
            'user': 'nickfrostatx',
            'name': 'nass',
            'status': 'failing',
        },
        'corral': {
            'user': 'nickfrostatx',
            'name': 'corral',
            'status': 'inactive',
        },
    },
}


def get_repos(user):
    """Return all the repos for a given user."""
    if user not in _repos:
        raise exceptions.NoSuchUserException()
    return _repos[user]
