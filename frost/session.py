# -*- coding: utf-8 -*-
"""Server-side sessions."""

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
        self.new = new
        self.rotate = False
        self.modified_keys = set()

    def __setitem__(self, key, value):
        self.modified = True
        self.modified_keys.add(key)
        return super(RedisSession, self).__setitem__(key, value)


class RedisSessionInterface(SessionInterface):

    session_class = RedisSession

    def generate_sid(self):
        return random_string(64)

    def open_session(self, app, request):
        """Attempt to load the session from a cookie, or create one."""
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            try:
                data = get_session_data(sid)
                return self.session_class(initial=data, sid=sid)
            except LookupError:
                pass
        sid = self.generate_sid()
        session = self.session_class(sid=sid, new=True)
        session['csrf'] = random_string(64)
        return session

    def save_session(self, app, session, response):
        """Write the session to redis, and set the cookie."""
        domain = self.get_cookie_domain(app)
        if not session:
            delete_session(session.sid)
            if session.modified:
                response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        new_sid = None
        if session.rotate and not session.new:
            new_sid = self.generate_sid()
        redis_exp = app.permanent_session_lifetime
        cookie_exp = self.get_expiration_time(app, session)
        modified_data = {k: session.get(k) for k in session.modified_keys}
        store_session_data(session.sid, modified_data, redis_exp,
                           rename_to=new_sid)
        response.set_cookie(app.session_cookie_name, new_sid or session.sid,
                            expires=cookie_exp, httponly=True, domain=domain,
                            secure=(request.scheme == 'https'))
