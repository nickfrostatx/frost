# -*- coding: utf-8 -*-
"""GitHub API."""

import requests
from . import exceptions


class GitHub(object):

    """GitHub API implementation."""

    def __init__(self, client_id, client_secret, url='https://github.com'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = url

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
            assert isinstance(access_token, str)
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
            print(e)
            raise exceptions.GitHubError()

        if not response.ok:
            raise exceptions.GitHubError(response)

        try:
            return response.json()
        except ValueError:
            raise exceptions.GitHubError()


    @property
    def session(self):
        if not hasattr(self, '_session'):
            self._session = requests.session()
        return self._session
