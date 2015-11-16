# -*- coding: utf-8 -*-
"""GitHub API."""

import requests
from . import exceptions


class GitHub(object):

    """GitHub API implementation."""

    def __init__(self, app, base_url='https://github.com'):
        self.app = app
        self.base_url = base_url

    def get_access_token(self, code):
        url = '/login/oauth/access_token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
        }
        data = self.make_request('GET', url, params=params)

        try:
            access_token = data['access_token']
            assert isinstance(access_token, basestring)
        except (TypeError, KeyError, AssertionError):
            raise exceptions.GitHubError()

        return access_token

    def make_request(self, method, url, *a, **kw):
        """Make the actual request, and handle any errors."""
        url = self.base_url + url

        if 'headers' not in kw:
            kw['headers'] = {}
        kw['headers']['Accept'] = 'application/json'

        try:
            response = self.session.request(method, url, *a, **kw)
        except requests.exceptions.RequestException as e:
            raise exceptions.GitHubError()

        if not response.ok:
            raise exceptions.GitHubError(response)

        try:
            return response.json()
        except ValueError:
            raise exceptions.GitHubError()

    @property
    def client_id(self):
        return self.app.config['GITHUB_CLIENT_ID']

    @property
    def client_secret(self):
        return self.app.config['GITHUB_CLIENT_SECRET']

    @property
    def session(self):
        if not hasattr(self, '_session'):
            self._session = requests.session()
        return self._session
