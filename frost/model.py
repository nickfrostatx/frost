# -*- coding: utf-8 -*-
"""The model."""

from datetime import datetime
import flask
import redis


redis_cls = redis.StrictRedis
_redis = None


def get_redis():
    """Cached redis instance that won't get created until first used."""
    global _redis
    if _redis is None:
        _redis = redis_cls.from_url(flask.current_app.config['REDIS_URL'])
    return _redis


def decode_dict(d, *keys):
    """Decode all keys and values."""
    decoded = {}
    for key in keys:
        if key in d:
            decoded[key.decode()] = d[key].decode()
    return decoded


def decode_repo(repo):
    """Decode repo, including last_update."""
    decoded = decode_dict(repo, b'name', b'status', b'build_status')
    last_update = datetime.strptime(repo[b'last_update'].decode(),
                                    '%Y-%m-%d %H:%M:%S')
    decoded['last_update'] = last_update
    return decoded


def get_session_data(key):
    """Load all the values of a session dictionary."""
    s = get_redis().hgetall('session:{0}'.format(key))
    if not s:
        raise LookupError()
    return decode_dict(s, b'csrf', b'user')


def store_session_data(key, data, expire, rename_to=None):
    """Store the changes in the session, update expire time."""
    expire_seconds = expire.days * 60 * 60 * 24 + expire.seconds
    pipe = get_redis().pipeline()
    if data:
        pipe.hmset('session:{0}'.format(key), data)
    pipe.expire('session:{0}'.format(key), expire_seconds)
    if rename_to is not None:
        pipe.rename('session:{0}'.format(key), 'session:{0}'.format(rename_to))
    pipe.execute()


def delete_session(key):
    """Remove a session."""
    get_redis().delete('session:{0}'.format(key))


def user_exists(user):
    """Return whether the given user exists."""
    return get_redis().exists('user:{0}'.format(user))


def create_user(user, access_token):
    """Create a user to the database."""
    get_redis().hmset('user:{0}'.format(user), {
        'access_token': access_token,
    })


def get_repos(user):
    """Return all the repos for a given user, sorted by last_update."""
    repos = get_redis().lrange('repos:{0}'.format(user), 0, -1)
    if not repos:
        raise LookupError()
    pipe = get_redis().pipeline()
    for repo in repos:
        pipe.hgetall('repo:{0}:{1}'.format(user, repo.decode()))
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
        raise LookupError()
    return decode_repo(r)


def get_repo_status(user, repo):
    """Return the build status of a repo."""
    s = get_redis().hget('repo:{0}:{1}'.format(user, repo), 'build_status')
    if not s:
        raise LookupError()
    return s.decode()
