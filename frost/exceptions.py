# -*- coding: utf-8 -*-
"""App-specific exceptions."""


class NoSuchSessionException(Exception):

    """There is no session with the given key."""


class NoSuchUserException(Exception):

    """There is no user with the given username."""


class NoSuchRepoException(Exception):

    """The user has no repo with the given name."""
