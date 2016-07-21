# -*- coding: utf-8 -*-
"""Badge blueprint."""

from flask import Blueprint, request, abort
from flask.helpers import send_from_directory
from .error import errorhandler
from .model import get_repo_status


badge = Blueprint('badge', __name__, static_folder='badges')


def render_badge(status):
    """Render the static file for a given badge status."""
    def send_file(path):
        return send_from_directory(badge.static_folder, path, add_etags=False,
                                   cache_timeout=-2)

    if status in ('passing', 'failing', 'unknown', 'invalid'):
        badge_path = status + '.svg'
    else:
        badge_path = 'error.svg'

    if 'gzip' in request.headers.get('Accept-Encoding', ''):
        # Send pre-compressed badge
        resp = send_file(badge_path + '.gz')
        resp.headers['Content-Encoding'] = 'gzip'
        return resp

    return send_file(badge_path)


@badge.after_request
def no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    del response.headers['Last-Modified']
    return response


@errorhandler(badge)
def error_badge(e):
    return render_badge('invalid'), e.code


@badge.route('/<user>/<repo>.svg')
def view(user, repo):
    try:
        status = get_repo_status(user, repo)
    except LookupError:
        abort(404)
    return render_badge(status)
