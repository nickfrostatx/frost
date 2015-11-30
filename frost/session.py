# -*- coding: utf-8 -*-
"""Server-side sessions."""

from datetime import datetime, timedelta
from flask import request
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
from .model import get_session_data, store_session_data, delete_session
from .util import random_string


class RedisSession(dict, SessionMixin):
    """The session object."""

    def __init__(self, initial=None, sid=None, new=None):
        if initial is None:
            initial = {}
        dict.__init__(self, initial)
        self.sid = sid
        self.old_sid = None
        self.new = new
        self.modified_keys = set()

    def init_data(self):
        """Create a random session key and CSRF token."""
        self.sid = random_string(64)
        self['csrf'] = random_string(64)

    def rotate(self):
        """Reset the session key and CSRF token."""
        if not self.new:
            self.old_sid = self.sid
        self.init_data()

    def __setitem__(self, key, value):
        """Change the value, and record the change."""
        self.modified = True
        self.modified_keys.add(key)
        return super(RedisSession, self).__setitem__(key, value)

    @property
    def authed(self):
        """Return whether the user is authenticated."""
        return 'user' in self

    @property
    def permanent(self):
        """Return whether the session should be stored long-term."""
        return self.authed


class RedisSessionInterface(SessionInterface):

    session_class = RedisSession

    def open_session(self, app, request):
        """Attempt to load the session from a cookie, or create one."""
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            try:
                data = get_session_data(sid)
                return self.session_class(initial=data, sid=sid)
            except LookupError:
                pass
        session = self.session_class(new=True)
        session.init_data()
        return session

    def get_session_lifetime(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def get_expiration_time(self, app, session):
        return datetime.utcnow() + self.get_session_lifetime(app, session)

    def save_session(self, app, session, response):
        """Write the session to redis, and set the cookie."""
        domain = self.get_cookie_domain(app)
        if not session:
            delete_session(session.sid)
            if session.modified:
                response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        redis_exp = self.get_session_lifetime(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        changed_data = dict((k, session.get(k)) for k in session.modified_keys)
        store_session_data(session.sid, changed_data, redis_exp,
                           session.old_sid)
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True, domain=domain,
                            secure=(request.scheme == 'https'))
