# -*- encoding: utf-8 -*-
from os.path import normpath
import pytest
from uuid import uuid4
from tempfile import mkdtemp
from datetime import datetime

from torrentool.api import Torrent
from torrentool.exceptions import TorrentError

from common import *


def test_create():
    fp = join(CURRENT_DIR, 'torrtest', 'root.txt')
    t = Torrent.create_from(fp)
    t.private = True

    assert t._struct['info'] == STRUCT_TORRENT_SIMPLE['info']

    # Note that STRUCT_TORRENT_WITH_DIR will probably
    # differ from struct created during this test (due to different file ordering - Transmission-torrentool),
    # so all we do is checking all files are present.
    t = Torrent.create_from(join(CURRENT_DIR, 'torrtest'))
    info = t._struct['info']
    expected_info = STRUCT_TORRENT_WITH_DIR['info']

    def get_fpaths(info):
        return {'|'.join(f['path']) for f in info['files']}

    assert get_fpaths(info) == get_fpaths(expected_info)


def test_getters_simple():
    t = Torrent.from_file(FPATH_TORRENT_SIMPLE)

    assert t._filepath == FPATH_TORRENT_SIMPLE

    assert t.created_by == 'Transmission/2.84 (14307)'
    assert t.files == [('root.txt', 4)]
    assert t.total_size == 4
    assert t.name == u'root.txt'
    assert t.announce_urls == [['udp://123.123.123.123']]
    assert t.creation_date.isoformat() == '2015-10-21T17:40:05'
    assert t.comment is None

    hash_expected = '238967c8417cc6ccc378df16687d1958277f270b'
    assert t.info_hash == hash_expected

    magnet = t.magnet_link
    assert hash_expected in magnet
    assert 'btih' in magnet
    assert 'magnet:' in magnet


def test_getters_dir():
    t = Torrent.from_file(FPATH_TORRENT_WITH_DIR)

    assert t._filepath == FPATH_TORRENT_WITH_DIR

    assert t.created_by == 'Transmission/2.84 (14307)'
    assert t.files == [
        (normpath('torrtest/root.txt'), 4),
        (normpath('torrtest/sub1/sub11.txt'), 4),
        (normpath(u'torrtest/sub1/sub2/кириллица.txt'), 11),
        (normpath('torrtest/sub1/sub2/sub22.txt'), 4)
    ]
    assert t.total_size == 23
    assert t.announce_urls == [['http://track1.org/1/', 'http://track2.org/2/']]
    assert t.creation_date.isoformat() == '2015-10-25T09:42:04'
    assert t.comment == u'примечание'

    hash_expected = 'c815be93f20bf8b12fed14bee35c14b19b1d1984'
    assert t.info_hash == hash_expected

    magnet = t.magnet_link
    assert hash_expected in magnet
    assert 'btih' in magnet
    assert 'magnet:' in magnet

    magnet = t.get_magnet(detailed=True)
    assert (
        magnet == 'magnet:?xt=urn:btih:c815be93f20bf8b12fed14bee35c14b19b1d1984'
                  '&tr=http%3A%2F%2Ftrack1.org%2F1%2F&tr=http%3A%2F%2Ftrack2.org%2F2%2F'
    )


def test_setters():
    t = Torrent()

    assert t.info_hash is None
    assert t.comment is None
    assert t.created_by is None
    assert t.creation_date is None
    assert t.total_size == 0
    assert t.announce_urls == []
    assert t.files == []

    t.name = 'mytorrent'
    assert t.name == 'mytorrent'

    t.comment = 'mycomment'
    assert t.comment == 'mycomment'

    t.created_by = 'some/1.0'
    assert t.created_by == 'some/1.0'

    now = datetime.now()
    t.creation_date = now
    assert t.creation_date == now.replace(microsecond=0)

    t.announce_urls = 'some1'
    assert t.announce_urls == [['some1']]
    assert t._struct['announce'] == 'some1'
    assert 'announce-list' not in t._struct

    t.announce_urls = ['some3', 'some4']
    assert t.announce_urls == [['some3'], ['some4']]
    assert t._struct['announce'] == 'some3'

    t.announce_urls = ['some5']
    assert t.announce_urls == [['some5']]
    assert t._struct['announce'] == 'some5'
    assert 'announce-list' not in t._struct

    assert not t.private
    t.private = False
    assert not t.private
    t.private = True
    assert t.private
    t.private = False
    assert not t.private


def test_setters_webseed():
    t = Torrent()
    t.name = 'mytorrent'

    t.webseeds = None
    assert t.webseeds == []

    t.webseeds = 'http://host.some/file'
    assert t.webseeds == ['http://host.some/file']
    assert (
        t.get_magnet() == 'magnet:?xt=urn:btih:0f967b3f021421750069f93d256e319f13c404b1'
                          '&ws=http%3A%2F%2Fhost.some%2Ffile')

    seeds = ['seed1', 'seed2']
    t.webseeds = seeds
    assert t.webseeds == seeds
    assert t.get_magnet() == 'magnet:?xt=urn:btih:0f967b3f021421750069f93d256e319f13c404b1&ws=seed1&ws=seed2'

    t.webseeds = None
    assert t.webseeds == []
    assert 'url-list' not in t._struct


def test_setters_httpseed():
    t = Torrent()
    t.name = 'mytorrent'

    t.httpseeds = None
    assert t.httpseeds == []

    t.httpseeds = 'http://host.some/file'
    assert t.httpseeds == ['http://host.some/file']

    seeds = ['seed1', 'seed2']
    t.httpseeds = seeds
    assert t.httpseeds == seeds

    t.httpseeds = None
    assert t.httpseeds == []
    assert 'httpseeds' not in t._struct


def test_from_string():
    torrstr = '4:spam'
    t = Torrent.from_string(torrstr)
    assert t._struct == 'spam'


def test_to_file():
    t0 = Torrent({})

    with pytest.raises(TorrentError):
        t0.to_file()

    t1 = Torrent.from_file(FPATH_TORRENT_SIMPLE)
    fpath = join(mkdtemp(), str(uuid4()))
    t1.to_file(fpath)

    t2 = Torrent.from_file(fpath)
    assert t1._struct == t2._struct


def test_str():
    """ Tests Torrent.__str__ method """
    t = Torrent.from_file(FPATH_TORRENT_SIMPLE)
    assert str(t) == 'Torrent: root.txt'

    t.name = 'Мой торрент'
    assert str(t) == 'Torrent: Мой торрент'
