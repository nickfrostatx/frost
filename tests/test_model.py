# -*- coding: utf-8 -*-
"""Test model functions."""

import frost.exceptions
import frost.model
import pytest


def test_get_repos():
    repos = frost.model.get_repos('nickfrostatx')
    assert type(repos) == list
    assert len(repos) == 4


def test_invalid_user():
    with pytest.raises(frost.exceptions.NoSuchUserException):
        frost.model.get_repos('fakeuser')


def test_get_repo():
    repo = frost.model.get_repo('nickfrostatx', 'frost')
    assert repo['name'] == 'frost'
    assert repo['status'] == 'passing'


def test_invalid_repos():
    with pytest.raises(frost.exceptions.NoSuchUserException):
        frost.model.get_repo('fakeuser', 'fakerepo')

    with pytest.raises(frost.exceptions.NoSuchRepoException):
        frost.model.get_repo('nickfrostatx', 'fakerepo')
