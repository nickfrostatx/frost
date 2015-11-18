# -*- coding: utf-8 -*-
"""Utility functions."""

from base64 import urlsafe_b64encode
from flask import request
from math import ceil
import os
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


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


def random_string(size):
    """Generate a random base64 string from urandom."""
    if size % 4 != 0:
        raise AssertionError('random_string expects a multiple of 4')
    n_bytes = size * 3 // 4
    return urlsafe_b64encode(os.urandom(n_bytes)).decode('utf-8')
