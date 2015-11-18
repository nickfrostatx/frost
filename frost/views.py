# -*- coding: utf-8 -*-
"""Main HTML views."""

from flask import Blueprint, abort, current_app, g, request, render_template, \
                  redirect
from werkzeug.exceptions import InternalServerError
from . import exceptions
from .model import get_repos, get_repo
from .util import is_safe_url
import requests
try:
    from urllib.parse import quote, urlencode
except ImportError:
    from urllib import quote, urlencode


views = Blueprint('views', __name__, template_folder='templates')


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
    redirect_uri = request.host_url + 'oauth'
    if request.referrer and is_safe_url(request.referrer, False):
        next = request.referrer[len(request.host_url) - 1:]
        redirect_uri += '?next=' + quote(next, safe='')
    query = [
        ('client_id', current_app.config['GITHUB_CLIENT_ID']),
        ('scopes', ','.join(['write:repo_hook', 'repo:status',
                             'repo_deployment', 'read:org'])),
        ('state', 'my unique  state str'),
        ('redirect_uri', redirect_uri),
    ]
    qs = urlencode(query)
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

    next = request.args.get('next', '/')
    if not next or not is_safe_url(next, True):
        next = request.host_url
    return redirect(next, code=302)


@views.route('/<user>/<repo>')
def repo_page(user, repo):
    try:
        r = get_repo(user, repo)
    except exceptions.NoSuchRepoException:
        abort(404)
    return render_template('views/repo.html', user=user, name=repo, repo=r)
