import pytest

from torrentool.exceptions import RemoteUploadError, RemoteDownloadError
from torrentool.utils import get_app_version, humanize_filesize, get_open_trackers_from_local, \
    get_open_trackers_from_remote, upload_to_cache_server


def test_get_app_version():
    assert 'torrentool' in get_app_version()


def test_filesize():
    assert humanize_filesize(0) == '0 B'
    assert humanize_filesize(1024) == '1.0 KB'
    assert humanize_filesize(1024 * 1024) == '1.0 MB'


def test_get_opentrackers(monkeypatch, response_mock):

    assert isinstance(get_open_trackers_from_local(), list)

    url = 'https://raw.githubusercontent.com/idlesign/torrentool/master/torrentool/repo/open_trackers.ini'

    with response_mock(f'GET  {url} -> 200:1\n2\n'):
        assert get_open_trackers_from_remote() == ['1', '2']

    with response_mock(f'GET  {url} -> 500:'):
        with pytest.raises(RemoteDownloadError):
            get_open_trackers_from_remote()


def test_cache_upload(monkeypatch, torr_test_file, response_mock):

    url = 'http://torrage.info/autoupload.php'

    with response_mock(f'POST {url} -> 200:somehash'):
        assert upload_to_cache_server(torr_test_file) == 'http://torrage.info/torrent.php?h=somehash'

    with response_mock(f'POST {url} -> 500:'):
        with pytest.raises(RemoteUploadError):
            upload_to_cache_server(torr_test_file)
