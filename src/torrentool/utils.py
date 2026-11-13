import math
from pathlib import Path
from typing import List

from .exceptions import RemoteUploadError, RemoteDownloadError


OPEN_TRACKERS_FILENAME = 'open_trackers.ini'
REMOTE_TIMEOUT = 4


def get_app_version() -> str:
    """Returns full version string including application name
    suitable for putting into Torrent.created_by.

    """
    from torrentool import VERSION
    return f'torrentool/{VERSION}'


def humanize_filesize(bytes_size: int) -> str:
    """Returns human readable filesize.

    :param bytes_size:

    """
    if not bytes_size:
        return '0 B'
    
    names = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

    name_idx = math.floor(math.log(bytes_size, 1024))
    size = round(bytes_size / math.pow(1024, name_idx), 2)

    return f'{size} {names[name_idx]}'


def upload_to_cache_server(fpath: str) -> str:
    """Uploads .torrent file to a cache server.
    Returns upload file URL.

    :param fpath: File to upload

    """
    url_base = 'http://torrage.info'
    url_upload = f'{url_base}/autoupload.php'
    url_download = f'{url_base}/torrent.php?h='
    file_field = 'torrent'

    try:
        import requests

        response = requests.post(url_upload, files={file_field: Path(fpath).open('rb')}, timeout=REMOTE_TIMEOUT)
        response.raise_for_status()

        info_cache = response.text
        return url_download + info_cache

    except (ImportError, requests.RequestException) as e:

        raise RemoteUploadError(f'Unable to upload to {url_upload}: {e}') from e


def get_open_trackers_from_remote() -> List[str]:
    """Returns open trackers announce URLs list from remote repo."""

    url = "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"

    try:
        import requests

        response = requests.get(url, timeout=REMOTE_TIMEOUT)
        response.raise_for_status()

        # Entries in the list are separated with blank lines.
        open_trackers = [stripped for line in response.text.splitlines() if (stripped := line.strip())]

    except (ImportError, requests.RequestException) as error:

        raise RemoteDownloadError(f"Unable to download from {url}: {error}") from error

    return open_trackers


def get_open_trackers_from_local() -> List[str]:
    """Returns open trackers announce URLs list from local backup."""

    with (Path(__file__).parent / 'repo' / OPEN_TRACKERS_FILENAME).open() as f:
        open_trackers = map(str.strip, f.readlines())

    return list(open_trackers)
