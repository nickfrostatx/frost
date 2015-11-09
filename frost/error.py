# -*- coding: utf-8 -*-
"""Catch-all error handling."""

from flask import render_template
from functools import wraps
import werkzeug.exceptions


ERROR_CODES = (400, 401, 403, 404, 405, 406, 408, 409, 410, 411, 412, 413, 414,
               415, 416, 417, 418, 422, 423, 424, 426, 428, 429, 431, 501, 502,
               503, 504, 505)


def register_error_handler(app, fn, include_500=False):
    """Register a catch-all handler to an app or blueprint."""
    for status in ERROR_CODES:
        app.register_error_handler(status, fn)

    if include_500:
        @wraps(fn)
        def handle_500(e):
            if not isinstance(e, werkzeug.exceptions.HTTPException):
                e = werkzeug.exceptions.InternalServerError()
            return fn(e)
        app.register_error_handler(500, handle_500)

    return fn


def html_handler(e):
    """Render the HTML error page for a given HTTPException."""
    return render_template('error.html', e=e), e.code
