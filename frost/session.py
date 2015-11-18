# -*- coding: utf-8 -*-
"""Server-side sessions."""

from flask import request, g
from . import exceptions
from .model import get_session_data, store_session_data
from .util import random_string


def get_session(key):
    """Attempt to load the session from the cookie."""
    if key is None:
        return None
    try:
        return get_session_data(key)
    except exceptions.NoSuchSessionException:
        return None


def init_session():
    """Load a session, or create a new one.

    This will also create a CSRF token.
    """
    key = request.cookies.get('session')
    session = get_session(key)
    if not session:
        key = random_string(64)
        session = {
            'csrf': random_string(64),
        }
    g.session_key = key
    g.session = session


def save_session(response):
    """Store the session in the database."""
    secure = request.headers.get('X-Scheme', 'http') == 'https'
    response.set_cookie('session', g.session_key, max_age=60*60*24*30,
                        secure=secure, httponly=True)
    from flask import make_response
    store_session_data(g.session_key, g.session)
    return response
