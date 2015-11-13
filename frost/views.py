# -*- coding: utf-8 -*-
"""Main HTML views."""

from flask import Blueprint, current_app, render_template


views = Blueprint('views', __name__)


@views.route('/')
def home():
    repos = [
        {
            'user': 'nickfrostatx',
            'name': 'frost',
            'status': 'passing',
        },
        {
            'user': 'nickfrostatx',
            'name': 'flask-hookserver',
            'status': 'progress',
        },
        {
            'user': 'nickfrostatx',
            'name': 'nass',
            'status': 'failing',
        },
        {
            'user': 'nickfrostatx',
            'name': 'corral',
            'status': 'inactive',
        },
    ]
    return render_template('views/home.html', repos=repos)


@views.route('/<user>/<repo>.svg')
def badge(user, repo):
    return current_app.send_static_file('passing.svg')
