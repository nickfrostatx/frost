# -*- coding: utf-8 -*-
"""Main HTML views."""

from flask import Blueprint, current_app, g, render_template
from werkzeug.exceptions import InternalServerError
from . import exceptions
from .util import get_repos


views = Blueprint('views', __name__)


@views.before_request
def check_auth():
    if getattr(g, 'user', None) is None:
        g.user = 'nickfrostatx'


@views.route('/')
def home():
    try:
        repos = get_repos(g.user)
    except exceptions.NoSuchUserException:
        # This shouldn't happen
        raise InternalServerError()
    return render_template('views/home.html', repos=repos)


@views.route('/<user>/<repo>.svg')
def badge(user, repo):
    return current_app.send_static_file('badges/passing.svg')
