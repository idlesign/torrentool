# -*- encoding: utf-8 -*-
from torrentool.utils import get_app_version


def test_get_app_version():
    assert 'torrentool' in get_app_version()
