# -*- coding: utf-8 -*-
"""Utility functions."""

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
        'error': {
            'user': 'nickfrostatx',
            'name': 'error',
        }
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
