# -*- coding: utf-8 -*-
"""The model."""

from datetime import datetime
from . import exceptions
import flask
import redis


_redis = None


def get_redis():
    """Cached redis instance that won't get created until first used."""
    global _redis
    if _redis is None:
        redis_cls = flask.current_app.config['REDIS_CLS']
        url = flask.current_app.config['REDIS_URL']
        _redis = redis_cls(url)
    return _redis


def decode_repo(repo):
    """Decode all keys and values to UTF-8."""
    decoded = {}
    for key in (b'name', b'status', b'build_status'):
        if key in repo:
            decoded[key.decode('utf-8')] = repo[key].decode('utf-8')
    last_update = datetime.strptime(repo[b'last_update'].decode('utf-8'),
                                    '%Y-%m-%d %H:%M:%S')
    decoded['last_update'] = last_update
    return decoded


def get_repos(user):
    """Return all the repos for a given user, sorted by last_update."""
    repos = get_redis().lrange('repos:{0}'.format(user), 0, -1)
    if not repos:
        raise exceptions.NoSuchUserException()
    pipe = get_redis().pipeline()
    for repo in repos:
        pipe.hgetall('repo:{0}:{1}'.format(user, repo.decode('utf-8')))
    result = pipe.execute()
    decoded = []
    for i, r in enumerate(result):
        r[b'name'] = repos[i]
        decoded.append(decode_repo(r))
    return decoded


def get_repo(user, repo):
    """Return the repo owned by user with the name repo."""
    r = get_redis().hgetall('repo:{0}:{1}'.format(user, repo))
    if not r:
        raise exceptions.NoSuchRepoException()
    return decode_repo(r)


def get_repo_status(user, repo):
    """Return the build status of a repo."""
    s = get_redis().hget('repo:{0}:{1}'.format(user, repo), 'build_status')
    if not s:
        raise exceptions.NoSuchRepoException()
    return s.decode('utf-8')
