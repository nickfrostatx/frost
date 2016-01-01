# -*- coding: utf-8 -*-
"""GitHub web hooks."""

from flask.ext.hookserver import Hooks
from .error import errorhandler


hooks = Hooks()


@errorhandler(hooks)
def error(e):
    return 'hwhat\n', e.code


@hooks.hook('ping')
def ping(data, guid):
    return 'pong\n'
