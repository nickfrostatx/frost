# -*- coding: utf-8 -*-
"""Main HTML views."""


from flask import Blueprint


views = Blueprint('views', __name__)


@views.route('/')
def home():
    return 'Home\n'
