# -*- encoding: utf-8 -*-
from __future__ import division
import os
import sys

# A user shouldnt have to install a package to run tests
sys.path.insert(0, os.path.abspath('..'))

import datetime
from tempfile import mkdtemp
from uuid import uuid4

import pytest

try:
    from unittest import mock
except ImportError:
    import mock

m_open = 'builtins.open' if sys.version_info >= (3, 0) else '__builtin__.open'

from torrentool.api import Torrent
from torrentool.exceptions import TorrentError

from common import *


def test_create():
    t = Torrent().create_from(os.path.join(CURRENT_DIR, 'torrtest', 'root.txt'))
    t.private = True
    t.announce_urls = 'udp://123.123.123.123'
    assert t._struct['info'] == STRUCT_TORRENT_SIMPLE['info']

    # Note that STRUCT_TORRENT_WITH_DIR will probably
    # differ from struct created during this test (due to different file ordering - Transmission-torrentool),
    # so all we do is checking all files are present.
    t = Torrent().create_from(join(CURRENT_DIR, 'torrtest'))
    info = t._struct['info']
    expected_info = STRUCT_TORRENT_WITH_DIR['info']

    def get_fpaths(info):
        return {'|'.join(f['path']) for f in info['files']}

    assert get_fpaths(info) == get_fpaths(expected_info)


def test_getters_simple():
    t = Torrent().from_file(FPATH_TORRENT_SIMPLE)

    assert t._filepath == FPATH_TORRENT_SIMPLE

    assert t.created_by == 'torrentool/0.3.0'
    assert t.files == [('root.txt', 3)]
    assert t.total_size == 3
    assert t.name == u'root.txt'
    assert t.announce_urls == [['udp://123.123.123.123']]
    assert t.creation_date.isoformat() == '2016-09-14T20:49:40'
    assert t.comment is None

    hash_expected = '13548e73f889bb6108dd61550c722693184093a5'
    assert t.info_hash == hash_expected

    magnet = t.magnet_link
    assert hash_expected in magnet
    assert 'btih' in magnet
    assert 'magnet:' in magnet


@mock.patch(m_open)
def test_mocked_to_file(m):
    t = Torrent().create_from(os.path.join(CURRENT_DIR, 'torrtest', 'root.txt'))
    f = t.to_file()
    assert t._filepath + '.torrent' == f


def test_getters_dir():
    t = Torrent().from_file(FPATH_TORRENT_WITH_DIR)

    assert t._filepath == FPATH_TORRENT_WITH_DIR

    assert t.created_by == 'torrentool/0.3.0'

    assert t.files == [
        (os.path.normpath('torrtest/root.txt'), 3),
        (os.path.normpath('torrtest/sub1/sub11.txt'), 5),
        (os.path.normpath('torrtest/sub1/sub2/sub22.txt'), 5),
        (os.path.normpath(u'torrtest/sub1/sub2/кириллица.txt'), 11)

    ]

    assert t.total_size == 24
    assert t.announce_urls == [[u'udp://123.123.123.123']]
    assert t.creation_date.isoformat() == '2016-09-14T21:50:51'
    assert t.comment == u'примечание'

    hash_expected = '7cc3a898e1f6c7c4342f023eafe77888ce979906'
    assert t.info_hash == hash_expected

    magnet = t.magnet_link
    assert hash_expected in magnet
    assert 'btih' in magnet
    assert 'magnet:' in magnet


def test_setters():
    t = Torrent()

    assert t.info_hash is None
    assert t.comment is None
    assert t.created_by is None
    assert t.creation_date is None
    assert t.total_size == 0
    assert t.announce_urls == []
    assert t.files == []

    #
    assert t.webseeds == []
    assert t.httpseeds == []
    assert t.private is False
    assert t.piece_size is None
    assert t.encoding is None

    t.name = 'mytorrent'
    assert t.name == 'mytorrent'

    t.comment = 'mycomment'
    assert t.comment == 'mycomment'

    t.created_by = 'some/1.0'
    assert t.created_by == 'some/1.0'

    now = datetime.datetime.now()
    t.creation_date = now
    assert t.creation_date == now.replace(microsecond=0)
    t.creation_date = 0
    assert str(t.creation_date) == '1970-01-01 00:00:00'

    with pytest.raises(ValueError):
        t.webseeds = 'i should be a list of lists'

    with pytest.raises(ValueError):
        t.httpseeds = 'i should be a list of lists'

    t.webseeds = [['url1']]
    assert t.webseeds == [['url1']]

    t.httpseeds = [['url2']]
    assert t.httpseeds == [['url2']]

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
    t = t1.to_file(fpath)

    t2 = Torrent.from_file(t)
    assert t1._struct == t2._struct


def test_str():
    """ Tests Torrent.__str__ method """
    t = Torrent.from_file(FPATH_TORRENT_SIMPLE)
    assert str(t) == 'Torrent: root.txt'

    t.name = 'Мой торрент'
    assert str(t) == 'Torrent: Мой торрент'


def test_calc_size_auto():

    sizes = [(0.001, 32768, 16384),
             (20, 32768, 16384),
             (64, 65536, 65536),
             (150, 131072, 131072),
             (350, 262144, 262144),
             (600, 524288, 524288),
             (1100, 1048576, 1048576),
             (5200, 2097152, 4194304),
             (11000, 4194304, 8388608),
             (22000, 8388608, 16777216),
             (50000, 16777216, 16777216),
             (133700, 16777216, 16777216)]

    for s in sizes:
        size = s[0] * 1024 * 1024
        ps_auto = Torrent()._calc_piece_size(size)
        ps_calc = Torrent()._calc_piece_size(size, mode='calc')
        assert ps_auto == s[1]
        assert ps_calc == s[2]
        assert ps_auto % 32768 == 0
        assert ps_calc % 16384 == 0

    x = Torrent()._calc_piece_size(131 * 1024 * 1024,
                                   mode='calc',
                                   min_piece_number=1788,
                                   max_piece_number=1800,
                                   max_piece_size=None)

    assert x % 16384 == 0


def test_set_torrent_size():
    fpath = os.path.join(mkdtemp(), str(uuid4()))
    new_torrent_file = os.path.join(mkdtemp(), 'test.torrent')

    # filesize in mb, torrent size kb
    filesizes = [(1337, 1, 'auto', 996),
                 (1337, None, 'auto', 26937),
                 (356, 1, 'calc', 994),
                 (356, None, 'calc', 28675)]  # Torrent size disabled

    try:
        for fs in filesizes:
            f = open(fpath, 'w+')
            f.seek((fs[0] * 1024 * 1024) - 1)
            f.write('\0')
            f.close()

            tt = Torrent()
            tt.private = True

            tt.create_from(fpath, max_torrent_size=fs[1], mode=fs[2])
            tt.to_file(new_torrent_file)

            if fs[1]:
                assert os.path.getsize(new_torrent_file) / 1024 <= fs[1]
            else:
                assert os.path.getsize(new_torrent_file) == fs[3]

    except:
        raise

    finally:
        try:
            os.remove(fpath)
            os.remove(new_torrent_file)
        except:
            raise
        finally:
            assert not os.path.isfile(fpath)
            assert not os.path.isfile(new_torrent_file)
