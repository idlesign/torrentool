# -*- encoding: utf-8 -*-
import pytest

from torrentool.utils import get_app_version, humanize_filesize, get_open_trackers_from_local, \
    get_open_trackers_from_remote, upload_to_cache_server
from torrentool.exceptions import RemoteUploadError, RemoteDownloadError

from common import FPATH_TORRENT_SIMPLE
from requests import ResponseMock


def test_get_app_version():
    assert 'torrentool' in get_app_version()


def test_filesize():
    assert humanize_filesize(0) == '0 B'
    assert humanize_filesize(1024) == '1.0 KB'
    assert humanize_filesize(1024 * 1024) == '1.0 MB'


def test_get_opentrackers(monkeypatch):
    assert isinstance(get_open_trackers_from_local(), list)

    monkeypatch.setattr('requests.get', lambda *args, **kwargs: ResponseMock('1\n2\n'), raising=False)
    assert get_open_trackers_from_remote() == ['1', '2']

    monkeypatch.setattr('requests.get', lambda *args, **kwargs: ResponseMock(None), raising=False)
    with pytest.raises(RemoteDownloadError):
        get_open_trackers_from_remote()


def test_cache_upload(monkeypatch):

    monkeypatch.setattr('requests.post', lambda *args, **kwargs: ResponseMock('somehash'), raising=False)
    assert upload_to_cache_server(FPATH_TORRENT_SIMPLE) == 'http://torrage.info/torrent.php?h=somehash'

    monkeypatch.setattr('requests.post', lambda *args, **kwargs: ResponseMock(None), raising=False)
    with pytest.raises(RemoteUploadError):
        upload_to_cache_server(FPATH_TORRENT_SIMPLE)
