from __future__ import division
import click
from os import path, getcwd

from . import VERSION
from .api import Torrent
from .utils import humanize_filesize, upload_to_cache_server, get_open_trackers_from_remote, \
    get_open_trackers_from_local
from .exceptions import RemoteUploadError, RemoteDownloadError


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
        click.secho('Fetching an up-to-date open tracker list ...')
        try:
            urls.extend(get_open_trackers_from_remote())
        except RemoteDownloadError:
            click.secho('Failed. Using built-in open tracker list.', fg='red', err=True)
            urls.extend(get_open_trackers_from_local())

    if urls:
        my_torrent.announce_urls = urls

    my_torrent.to_file(dest)

    click.secho('Torrent file created: %s' % dest, fg='green')
    click.secho('Torrent info hash: %s' % my_torrent.info_hash, fg='blue')

    if cache:
        click.secho('Uploading to %s torrent cache service ...')
        try:
            result = upload_to_cache_server(dest)
            click.secho('Cached torrent URL: %s' % result, fg='yellow')

        except RemoteUploadError as e:
            click.secho('Failed: %s' % e, fg='red', err=True)


def main():
    start(obj={})
