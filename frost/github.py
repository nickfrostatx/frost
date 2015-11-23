# -*- coding: utf-8 -*-
"""GitHub API."""

import requests


BASE_URL = 'https://github.com'
API_URL = 'https://api.github.com'

session = requests.session()


def _github_request(method, url, access_token=None, base=None, **kw):
    """Make the actual request, and handle any errors."""
    if base is None:
        base = API_URL

    kw.setdefault('headers', {})
    kw['headers'].setdefault('Accept', 'application/json')

    if access_token is not None:
        kw['headers'].setdefault('Authorization', 'token ' + access_token)

    try:
        response = session.request(method, base + url, **kw)
    except requests.exceptions.RequestException:
        raise Exception('Failed to communicate with GitHub')

    try:
        data = response.json()
    except ValueError:
        raise Exception('GitHub returned bad JSON')

    if not response.ok:
        try:
            msg = data['message']
        except (TypeError, KeyError):
            msg = '<no error message>'
        raise Exception('{0}: {1}'.format(response.status_code, msg))

    return data


def _get_string_from_json(data, key):
    """Attempt to load a key from a JSON-decoded response object."""
    try:
        val = data[key]
        assert hasattr(val, 'encode')  # Must be unicode
    except (TypeError, KeyError, AssertionError):
        raise Exception('GitHub response was missing "{0}"'.format(key))
    return val


def get_access_token(code, client_id, client_secret):
    """Request an access token with the given code."""
    url = '/login/oauth/access_token'
    params = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    data = _github_request('POST', url, base=BASE_URL, params=params)
    return _get_string_from_json(data, 'access_token')


def get_user(access_token):
    """Load a user."""
    data = _github_request('GET', '/user', access_token)
    return _get_string_from_json(data, 'login')
