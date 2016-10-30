import math
from os import path

from .exceptions import RemoteUploadError, RemoteDownloadError


OPEN_TRACKERS_FILENAME = 'open_trackers.ini'
REMOTE_TIMEOUT = 4


def get_app_version():
    """Returns full version string including application name
    suitable for putting into Torrent.created_by.

    """
    from torrentool import VERSION
    return 'torrentool/%s' % '.'.join(map(str, VERSION))


def humanize_filesize(bytes_size):
    """Returns human readable filesize.

    :param int bytes_size:
    :rtype: str
    """
    if not bytes_size:
        return '0 B'
    
    names = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

    name_idx = int(math.floor(math.log(bytes_size, 1024)))
    size = round(bytes_size / math.pow(1024, name_idx), 2)

    return '%s %s' % (size, names[name_idx])


def upload_to_cache_server(fpath):
    """Uploads .torrent file to a cache server.

    Returns upload file URL.

    :rtype: str
    """
    url_base = 'http://torrage.info'
    url_upload = '%s/autoupload.php' % url_base
    url_download = '%s/torrent.php?h=' % url_base
    file_field = 'torrent'

    try:
        import requests

        response = requests.post(url_upload, files={file_field: open(fpath, 'rb')}, timeout=REMOTE_TIMEOUT)
        response.raise_for_status()

        info_cache = response.text
        return url_download + info_cache

    except (ImportError, requests.RequestException) as e:

        # Now trace is lost. `raise from` to consider.
        raise RemoteUploadError('Unable to upload to %s: %s' % (url_upload, e))


def get_open_trackers_from_remote():
    """Returns open trackers announce URLs list from remote repo."""

    url_base = 'https://raw.githubusercontent.com/idlesign/torrentool/master/torrentool/repo'
    url = '%s/%s' % (url_base, OPEN_TRACKERS_FILENAME)

    try:
        import requests

        response = requests.get(url, timeout=REMOTE_TIMEOUT)
        response.raise_for_status()

        open_trackers = response.text.splitlines()

    except (ImportError, requests.RequestException) as e:

        # Now trace is lost. `raise from` to consider.
        raise RemoteDownloadError('Unable to download from %s: %s' % (url, e))

    return open_trackers


def get_open_trackers_from_local():
    """Returns open trackers announce URLs list from local backup."""
    with open(path.join(path.dirname(__file__), 'repo', OPEN_TRACKERS_FILENAME)) as f:
        open_trackers = map(str.strip, f.readlines())

    return list(open_trackers)
