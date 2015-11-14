# -*- coding: utf-8 -*-
"""Test utility functions."""

import frost.exceptions
import frost.util
import pytest


def test_get_repos():
    repos = frost.util.get_repos('nickfrostatx')
    assert len(repos) == 5


def test_invalid_user():
    with pytest.raises(frost.exceptions.NoSuchUserException):
        frost.util.get_repos('fakeuser')


def test_get_repo():
    repo = frost.util.get_repo('nickfrostatx', 'frost')
    assert repo['status'] == 'passing'


def test_invalid_repos():
    with pytest.raises(frost.exceptions.NoSuchUserException):
        frost.util.get_repo('fakeuser', 'fakerepo')

    with pytest.raises(frost.exceptions.NoSuchRepoException):
        frost.util.get_repo('nickfrostatx', 'fakerepo')
