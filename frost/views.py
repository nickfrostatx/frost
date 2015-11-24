# -*- coding: utf-8 -*-
"""Main HTML views."""

from flask import Blueprint, abort, current_app, request, render_template, \
                  redirect, session
from werkzeug.exceptions import InternalServerError
from . import exceptions
from .github import get_access_token, get_user
from .model import user_exists, create_user, get_repos, get_repo
from .util import check_state, is_safe_url, random_string
import requests
try:
    from urllib.parse import quote, urlencode
except ImportError:
    from urllib import quote, urlencode


views = Blueprint('views', __name__, template_folder='templates')

@views.route('/')
def home():
    if 'user' not in g.session:
        return render_template('views/auth.html')
    repos = get_repos(g.session['user'])
    return render_template('views/repos.html', user=g.session['user'],
                           repos=repos)


@views.route('/login')
@check_state
def login():
    redirect_uri = request.host_url + 'oauth'
    if request.referrer and is_safe_url(request.referrer, False):
        next = request.referrer[len(request.host_url) - 1:]
        redirect_uri += '?next=' + quote(next, safe='')
    query = [
        ('client_id', current_app.config['GITHUB_CLIENT_ID']),
        ('scopes', ','.join(['write:repo_hook', 'repo:status',
                             'repo_deployment', 'read:org'])),
        ('state', request.args['state']),
        ('redirect_uri', redirect_uri),
    ]
    qs = urlencode(query)
    return redirect('https://github.com/login/oauth/authorize?' + qs, code=303)


@views.route('/oauth')
@check_state
def oauth():
    code = request.args.get('code')
    try:
        client_id = current_app.config['GITHUB_CLIENT_ID']
        client_secret = current_app.config['GITHUB_CLIENT_SECRET']
        access_token = get_access_token(code, client_id, client_secret)
        user = get_user(access_token)
    except:
        abort(503)

    if not user_exists(user):
        create_user(user, access_token)

    session['user'] = user
    session.rotate = True

    next = request.args.get('next', '/')
    if not next or not is_safe_url(next, True):
        next = request.host_url
    return redirect(next, code=302)


@views.route('/<user>')
def user_page(user):
    try:
        repos = get_repos(user)
    except exceptions.NoSuchUserException:
        abort(404)
    return render_template('views/repos.html', user=user, repos=repos)


@views.route('/<user>/<repo>')
def repo_page(user, repo):
    try:
        r = get_repo(user, repo)
    except exceptions.NoSuchRepoException:
        abort(404)
    return render_template('views/repo.html', user=user, name=repo, repo=r)
