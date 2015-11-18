# -*- coding: utf-8 -*-
"""App-specific exceptions."""


class NoSuchSessionException(Exception):

    """There is no session with the given key."""


class NoSuchUserException(Exception):

    """There is no user with the given username."""


class NoSuchRepoException(Exception):

    """The user has no repo with the given name."""


class GitHubError(Exception):

    """Communication with the GitHub API has failed."""

    def __str__(self):
        """Return the error message, or a generic message."""
        try:
            message = '{0}: {1}'.format(self.response.status_code,
                                        self.response.json()['message'])
        except Exception:
            message = 'Failed to communicate with GitHub'
        return message

    @property
    def response(self):
        """The :class:`~requests.Response` object for the request."""
        if len(self.args) < 1:
            return None
        return self.args[0]
