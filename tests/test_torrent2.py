# -*- encoding: utf-8 -*-
from __future__ import division
import os
import sys

# A user shouldnt have to install a package to run tests
sys.path.insert(0, os.path.abspath('..'))

import datetime
from collections import OrderedDict
from tempfile import mkdtemp
from uuid import uuid4

import pytest

from torrentool.torrent2 import Torrent
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


def test_str():
    """ Tests Torrent.__str__ method """
    t = Torrent().from_file(FPATH_TORRENT_SIMPLE)
    assert str(t) == 'Torrent: root.txt'

    t.name = 'Мой торрент'
    assert str(t) == 'Torrent: Мой торрент'


def test_setters():
    t = Torrent()

    assert t.info_hash is None
    assert t.comment is None
    assert t.created_by is None
    assert t.creation_date is None
    assert t.total_size == 0
    assert t.announce_urls == []
    assert t.files == []
    # new
    assert t.max_torrent_size is None
    assert t.webseeds == []
    assert t.httpseeds == []
    assert t.private is False
    assert t.name is None

    t.name = 'mytorrent'
    assert t.name == 'mytorrent'

    t.comment = 'mycomment'
    assert t.comment == 'mycomment'

    t.created_by = 'some/1.0'
    assert t.created_by == 'some/1.0'

    now = datetime.datetime.now()
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

    t.private = False
    assert t.private is False
    t.private = True
    assert t.private == 1
    t.private = False
    assert t.private is False


def test_stuff():
    with pytest.raises(ValueError):
        t = Torrent(webseeds='url')

    with pytest.raises(ValueError):
        t = Torrent(httpseeds='url')

    with pytest.raises(ValueError):
        t = Torrent(private=1)

    with pytest.raises(ValueError):
        t = Torrent(announce_list=['url'])

    # Options
    min_piece_number = 1337
    max_piece_number = 9999
    min_piece_size = 1
    max_piece_size = 16777216
    max_torrent_size = 200
    # end options

    webseeds = [['ws1']]
    httpseeds = [['hs1'], ['hs2'], ['hs3']]
    private = True
    announce_list = [['a1'], ['a2']]
    comment = 'Hello'
    creation_date = datetime.datetime(2016, 1, 1)
    created_by = 'abc'

    t = Torrent(min_piece_number=min_piece_number,
                max_piece_number=max_piece_number,
                min_piece_size=min_piece_size,
                max_piece_size=max_piece_size,
                max_torrent_size=max_torrent_size,
                webseeds=webseeds,
                httpseeds=httpseeds,
                private=private,
                announce_list=announce_list,
                comment=comment,
                creation_date=creation_date,
                created_by=created_by)

    assert t.webseeds == webseeds
    assert t.httpseeds == httpseeds
    assert t.comment == comment
    assert t.announce_urls == announce_list
    assert t.created_by == created_by
    assert str(t.creation_date) == '2016-01-01 00:00:00'
    assert t._struct['creation date'] == 1451606400
    assert t.private is True
    assert t.comment == comment
    assert t.created_by == created_by


def test_set_torrent_size():

    fpath = os.path.join(mkdtemp(), str(uuid4()))
    new_torrent_file = os.path.join(mkdtemp(), 'test.torrent')

    # filesize in mb, torrent size kb
    filesizes = [(1337, 1),
                 (1337, None)]  # Torrent size disabled

    try:
        for fs in filesizes:
            f = open(fpath, 'w+')
            f.seek((fs[0] * 1024 * 1024) - 1)
            f.write('\0')
            f.close()

            tt = Torrent(max_torrent_size=fs[1])
            tt.create_from(fpath)
            tt.to_file(new_torrent_file)

            if fs[1]:
                assert os.path.getsize(new_torrent_file) / 1024 < fs[1]
            else:
                assert os.path.getsize(new_torrent_file) == 26925

    except:
        raise

    finally:
        os.remove(fpath)
        os.remove(new_torrent_file)
        assert not os.path.isfile(fpath)
        assert not os.path.isfile(new_torrent_file)
