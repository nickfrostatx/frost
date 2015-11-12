# -*- coding: utf-8 -*-
"""Main HTML views."""

from flask import Blueprint, current_app


views = Blueprint('views', __name__)


@views.route('/')
def home():
    return 'Home\n'


@views.route('/<user>/<repo>.svg')
def badge(user, repo):
    return current_app.send_static_file('passing.svg')
