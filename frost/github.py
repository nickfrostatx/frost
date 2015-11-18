# -*- coding: utf-8 -*-
"""GitHub API."""

import requests
from . import exceptions


class GitHub(object):

    """GitHub API implementation."""

    def __init__(self, app, base_url='https://github.com',
                 api_url='https://api.github.com'):
        """Construct the API object."""
        self.app = app
        self.base_url = base_url
        self.api_url = api_url

    def get_access_token(self, code):
        """Request an access token with the given code."""
        url = '/login/oauth/access_token'
        params = {'code': code}
        data = self.make_request('POST', url, base_url=self.base_url,
                                 params=params)

        try:
            access_token = data['access_token']
            assert hasattr(access_token, 'encode')  # Must be unicode
        except (TypeError, KeyError, AssertionError):
            raise exceptions.GitHubError()

        return access_token

    def get_user(self, access_token):
        """Load a user."""
        params = {'access_token': access_token}
        data = self.make_request('GET', '/user', params=params)

        try:
            name = data['login']
            assert hasattr(name, 'encode')  # Must be unicode
        except (TypeError, KeyError, AssertionError):
            raise exceptions.GitHubError()

        return name

    def make_request(self, method, url, base_url=None, **kw):
        """Make the actual request, and handle any errors."""
        if not base_url:
            base_url = self.api_url
        url = base_url + url

        kw.setdefault('headers', {})
        kw['headers'].setdefault('Accept', 'application/json')

        kw.setdefault('params', {})
        kw['params'].setdefault('client_id', self.client_id)
        kw['params'].setdefault('client_secret', self.client_secret)

        try:
            response = self.session.request(method, url, **kw)
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
