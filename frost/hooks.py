# -*- coding: utf-8 -*-
"""GitHub web hooks."""

from hookserver import HookRoutes
from .error import errorhandler


hooks = HookRoutes()


@errorhandler(hooks)
def error(e):
    return 'hwhat\n', e.code


@hooks.hook('ping')
def ping(data, guid):
    return 'pong\n'
