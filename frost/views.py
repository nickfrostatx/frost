# -*- coding: utf-8 -*-
"""Main HTML views."""

from flask import Blueprint, abort, current_app, g, request, render_template, \
                  redirect
from werkzeug.exceptions import InternalServerError
from . import exceptions
from .model import get_repos, get_repo, get_repo_status
from .util import is_safe_url, nocache
import requests
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


views = Blueprint('views', __name__)


@views.before_request
def check_auth():
    if getattr(g, 'authed', None) is None:
        g.authed = False
    if getattr(g, 'user', None) is None:
        g.user = 'nickfrostatx'


@views.route('/')
def home():
    if not g.authed:
        return render_template('views/auth.html')
    try:
        repos = get_repos(g.user)
    except exceptions.NoSuchUserException:
        # This shouldn't happen
        raise InternalServerError()
    return render_template('views/home.html', repos=repos)


@views.route('/login', methods=['POST'])
def login():
    client_id = current_app.config['GITHUB_CLIENT_ID']
    scopes = ','.join(['write:repo_hook', 'repo:status', 'repo_deployment',
                       'read:org'])
    state = 'my unique  state str'

    redirect_uri = 'http://localhost:5000/oauth'

    qs = ('client_id={0}&scope={1}&state={2}&redirect_uri={3}'
          .format(client_id, scopes, state, redirect_uri))
    return redirect('https://github.com/login/oauth/authorize?' + qs, code=303)


@views.route('/oauth')
def oauth():
    if request.args.get('state') != 'my unique  state str':
        abort(400)

    code = request.args.get('code')
    try:
        access_token = current_app.github.get_access_token(code)
    except exceptions.GitHubError as e:
        abort(503)

    next = request.referrer
    if not next or not is_safe_url(next):
        next = request.host_url
    return redirect(next, code=302)


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
        status = get_repo_status(user, repo)
        status_code = 200
    except (exceptions.NoSuchUserException, exceptions.NoSuchRepoException):
        status = 'invalid'
        status_code = 404
    except KeyError:
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
