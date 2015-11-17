# -*- coding: utf-8 -*-
"""Utility functions."""

from datetime import datetime, timedelta
from flask import make_response, request
from functools import wraps
from werkzeug.http import http_date
try:
    from urllib.parse import urlparse, urljoin
except ImportError:
    from urlparse import urlparse, urljoin


def is_safe_url(url):
    """Return whether the url is on the app's host."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, url))
    return (test_url.scheme == ref_url.scheme and
            ref_url.netloc == test_url.netloc and
            test_url.path != request.path)


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
