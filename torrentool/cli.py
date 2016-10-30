from __future__ import division
import click
from os import path, getcwd

from . import VERSION
from .api import Torrent
from .utils import humanize_filesize


@click.group()
@click.version_option(version='.'.join(map(str, VERSION)))
def start():
    """Torrentool command line utilities."""


@start.group()
def torrent():
    """Torrent-related commands."""


@torrent.command()
@click.argument('torrent_path', type=click.Path(exists=True, writable=False, dir_okay=False))
def info(torrent_path):
    """Print out information from .torrent file."""

    my_torrent = Torrent.from_file(torrent_path)

    size = my_torrent.total_size

    click.secho('Name: %s' % my_torrent.name, fg='blue')
    click.secho('Files:')
    for file_tuple in my_torrent.files:
        click.secho(file_tuple[0])

    click.secho('Hash: %s' % my_torrent.info_hash, fg='blue')
    click.secho('Size: %s (%s)' % (humanize_filesize(size), size), fg='blue')
    click.secho('Magnet: %s' % my_torrent.get_magnet(), fg='yellow')


@torrent.command()
@click.argument('source', type=click.Path(exists=True, writable=False))
@click.option('--dest', getcwd(), type=click.Path(file_okay=False), help='Destination path to put .torrent file into. Default: current directory.')
@click.option('--tracker', default=None, help='Tracker announce URL (multiple comma-separated values supported).')
@click.option('--open_trackers', default=False, is_flag=True, help='Add open trackers announce URLs.')
@click.option('--comment', default=None, help='Arbitrary comment.')
@click.option('--cache', default=False, is_flag=True, help='Upload file to torrent cache services.')
def create(source, dest, tracker, open_trackers, comment, cache):
    """Create torrent file from a single file or a directory."""

    source_title = path.basename(source).replace('.', '_').replace(' ', '_')
    dest = '%s.torrent' % path.join(dest, source_title)

    click.secho('Creating torrent from %s ...' % source)

    my_torrent = Torrent.create_from(source)

    if comment:
        my_torrent.comment = comment

    urls = []

    if tracker:
        urls = tracker.split(',')

    if open_trackers:
        urls.extend(get_open_trackers())

    if urls:
        my_torrent.announce_urls = urls

    my_torrent.to_file(dest)

    click.secho('Torrent file created: %s' % dest, fg='green')
    click.secho('Torrent info hash: %s' % my_torrent.info_hash, fg='blue')

    if cache:
        upload_cache(dest)


def upload_cache(fpath):
    """Uploads .torrent file to a cache server."""
    url_base = 'http://torrage.info'
    url_upload = '%s/autoupload.php' % url_base
    url_download = '%s/torrent.php?h=' % url_base
    file_field = 'torrent'

    click.secho('Uploading to %s torrent cache service ...')

    try:
        import requests

        response = requests.post(url_upload, files={file_field: open(fpath, 'rb')})
        response.raise_for_status()

        info_cache = response.text
        click.secho('Cached torrent URL: %s' % (url_download + info_cache), fg='yellow')

    except (ImportError, requests.RequestException) as e:

        if isinstance(e, ImportError):
            click.secho('`requests` package is unavailable.', fg='red', err=True)

        click.secho('Failed: %s' % e, fg='red', err=True)


def get_open_trackers():
    """Returns open trackers announce URLs list from remote repo or local backup."""

    ourl = 'https://raw.githubusercontent.com/idlesign/torrentool/master/torrentool/repo'
    ofile = 'open_trackers.ini'

    click.secho('Fetching an up-to-date open tracker list ...')

    try:
        import requests

        response = requests.get('%s/%s' % (ourl, ofile), timeout=3)
        response.raise_for_status()

        open_trackers = response.text.splitlines()

    except (ImportError, requests.RequestException) as e:

        if isinstance(e, ImportError):
            click.secho('`requests` package is unavailable.', fg='red', err=True)

        click.secho('Failed. Using built-in open tracker list.', fg='red', err=True)

        with open(path.join(path.dirname(__file__), 'repo', ofile)) as f:
            open_trackers = map(str.strip, f.readlines())

    return open_trackers


def main():
    start(obj={})
