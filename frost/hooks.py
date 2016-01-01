# -*- coding: utf-8 -*-
"""GitHub web hooks."""

from flask.ext.hookserver import Hooks


hooks = Hooks()


@hooks.hook('ping')
def ping(data, guid):
    return 'pong\n'
