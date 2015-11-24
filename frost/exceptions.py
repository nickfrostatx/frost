# -*- coding: utf-8 -*-
"""App-specific exceptions."""


class NoSuchUserException(Exception):

    """There is no user with the given username."""


class NoSuchRepoException(Exception):

    """The user has no repo with the given name."""
