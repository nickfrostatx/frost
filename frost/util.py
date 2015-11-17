# -*- coding: utf-8 -*-
"""Utility functions."""

from datetime import datetime, timedelta
from flask import make_response, request
from functools import wraps
from werkzeug.http import http_date
try:
    from urllib.parse import urlparse, urljoin
except ImportError:
    from urllib import urlparse, urljoin


def is_safe_url(url, relative):
    """Return whether the url is safe for redirection."""
    if relative:
        ref_url = urlparse('')
    else:
        ref_url = urlparse(request.host_url)
    test_url = urlparse(url)
    return test_url.scheme == ref_url.scheme and \
        test_url.netloc == ref_url.netloc and \
        test_url.path != request.path and \
        test_url.path.startswith('/')


def nocache(fn):
    """Decorate the view fn to override Cache-Control header."""
    @wraps(fn)
    def wrapped(*a, **kw):
        resp = make_response(fn(*a, **kw))
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = http_date(datetime.now() - timedelta(0, 2))
        del resp.headers['ETag']
        del resp.headers['Last-Modified']
        return resp
    return wrapped
