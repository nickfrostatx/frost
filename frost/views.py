# -*- coding: utf-8 -*-
"""Main HTML views."""

from flask import Blueprint, abort, current_app, g, render_template
from werkzeug.exceptions import InternalServerError
from . import exceptions
from .model import get_repo, get_repos
from .util import nocache


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


@views.route('/<user>/<repo>')
def repo_page(user, repo):
    try:
        r = get_repo(user, repo)
    except (exceptions.NoSuchUserException, exceptions.NoSuchRepoException):
        abort(404)
    return render_template('views/repo.html', repo=r)


@views.route('/<user>/<repo>.svg')
@nocache
def badge(user, repo):
    try:
        status = get_repo(user, repo)['build_status']
        status_code = 200
    except (exceptions.NoSuchUserException, exceptions.NoSuchRepoException):
        status = 'invalid'
        status_code = 404
    except Exception:
        status = 'error'
        status_code = 500

    if status == 'passing':
        badge_path = 'badges/passing.svg'
    elif status == 'failing':
        badge_path = 'badges/failing.svg'
    elif status == 'unknown':
        badge_path = 'badges/unknown.svg'
    elif status == 'invalid':
        badge_path = 'badges/invalid.svg'
    else:
        badge_path = 'badges/error.svg'

    return current_app.send_static_file(badge_path), status_code
