# -*- coding: utf-8 -*-
"""Test utility functions."""

import frost.exceptions
import frost.util
import pytest


def test_get_repos():
    repos = frost.util.get_repos('nickfrostatx')
    assert len(repos) == 4


def test_invalid_user():
    with pytest.raises(frost.exceptions.NoSuchUserException):
        frost.util.get_repos('fakeuser')
