# -*- coding: utf-8 -*-
"""GitHub web hooks."""

from flask_hookserver import Hooks


hooks = Hooks()


@hooks.hook('ping')
def ping(data, guid):
    return 'pong\n'
