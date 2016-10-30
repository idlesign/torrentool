# -*- encoding: utf-8 -*-
from torrentool.utils import get_app_version, humanize_filesize


def test_get_app_version():
    assert 'torrentool' in get_app_version()


def test_filesize():
    assert humanize_filesize(0) == '0 B'
    assert humanize_filesize(1024) == '1.0 KB'
    assert humanize_filesize(1024 * 1024) == '1.0 MB'
