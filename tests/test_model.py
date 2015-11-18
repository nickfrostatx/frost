# -*- coding: utf-8 -*-
"""Test model functions."""

from datetime import datetime
from util import db
import frost.exceptions
import frost.model
import pytest


def test_get_repos(db):
    repos = frost.model.get_repos('nickfrostatx')
    assert type(repos) == list
    assert len(repos) == 4
    assert repos[0] == {
        u'name': u'frost',
        u'status': u'passing',
        u'build_status': u'passing',
        u'last_update': datetime(2015, 11, 14, 11, 30, 43),
    }


def test_invalid_user(db):
    with pytest.raises(frost.exceptions.NoSuchUserException):
        frost.model.get_repos('fakeuser')


def test_get_repo(db):
    repo = frost.model.get_repo('nickfrostatx', 'frost')
    assert repo[u'status'] == u'passing'


def test_invalid_repos(db):
    with pytest.raises(frost.exceptions.NoSuchRepoException):
        frost.model.get_repo('fakeuser', 'fakerepo')

    with pytest.raises(frost.exceptions.NoSuchRepoException):
        frost.model.get_repo('nickfrostatx', 'fakerepo')


def test_get_repo_status(db):
    status = frost.model.get_repo_status('nickfrostatx', 'frost')
    assert status == u'passing'


def test_invalid_repo_status(db):
    with pytest.raises(frost.exceptions.NoSuchRepoException):
        frost.model.get_repo_status('fakeuser', 'fakerepo')

    with pytest.raises(frost.exceptions.NoSuchRepoException):
        frost.model.get_repo_status('nickfrostatx', 'fakerepo')
