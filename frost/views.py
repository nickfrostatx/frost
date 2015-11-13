# -*- coding: utf-8 -*-
"""Main HTML views."""

from flask import Blueprint, current_app, render_template


views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('views/home.html')


@views.route('/<user>/<repo>.svg')
def badge(user, repo):
    return current_app.send_static_file('passing.svg')
