# -*- coding: utf-8 -*-
"""Badge blueprint."""

from flask import Blueprint
from flask.helpers import send_from_directory
from werkzeug.exceptions import NotFound, InternalServerError
from . import exceptions
from .error import errorhandler
from .model import get_repo_status


badge = Blueprint('badge', __name__, static_folder='badges')


def render_badge(status):
    """Render the static file for a given badge and HTTP status code."""
    if status in ('passing', 'failing', 'unknown', 'invalid'):
        badge_path = status + '.svg'
    else:
        badge_path = 'error.svg'

    return send_from_directory(badge.static_folder, badge_path,
                               add_etags=False, cache_timeout=-2)


@badge.after_request
def no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    del response.headers['Last-Modified']
    return response


@errorhandler(badge)
def error_badge(e):
    try:
        status = e.status
    except AttributeError:
        status = 'error'
    return render_badge(status), e.code


@badge.route('/<user>/<repo>.svg')
def view(user, repo):
    try:
        status = get_repo_status(user, repo)
        return render_badge(status)
    except (exceptions.NoSuchUserException, exceptions.NoSuchRepoException):
        exc = NotFound()
        exc.status = 'invalid'
        raise exc
    except KeyError:
        return render_badge('error'), 500
