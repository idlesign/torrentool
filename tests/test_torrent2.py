import sys
import os
import pytest

# A user shouldnt have to install a package to run tests
sys.path.insert(0, os.path.abspath('..'))


from uuid import uuid4
from tempfile import mkdtemp, NamedTemporaryFile
from datetime import datetime
import math

from torrentool.torrent2 import Torrent
from torrentool.exceptions import TorrentError


from common import CURRENT_DIR, FPATH_TORRENT_SIMPLE, FPATH_TORRENT_WITH_DIR
from collections import OrderedDict

# remove me
from pprint import pprint as pp


def convert_size(size):
    if (size == 0):
        return '0B'
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return '%s %s' % (s, size_name[i])

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
    assert t.webseed == []
    assert t.httpseed == []
    assert t.private is False
    assert t.name is None

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

def test_instance():
    t = Torrent(max_torrent_size=100)

    #print t
    # make a torrent
    s = os.path.join(CURRENT_DIR, 'torrtest', 'root')


    x = t.from_file(FPATH_TORRENT_SIMPLE)
    #print pp(x._struct)

    struct = OrderedDict([(u'announce', u'udp://123.123.123.123'),
                        (u'created by', u'Transmission/2.84 (14307)'),
                        (u'creation date', 1445449205),
                        (u'encoding', u'UTF-8'),
                        (u'info', OrderedDict([(u'length', 4),
                                                (u'name', u'root.txt'),
                                                (u'piece length', 32768),
                                                (u'pieces', '\xa8\xfd\xc2\x05\xa9\xf1\x9c\xc1\xc7Pz`\xc4\xf0\x1b\x13\xd1\x1d\x7f\xd0'),
                                                (u'private', 1)]))])

    new_torrent = t.to_file('test222.torrent')


    fpath = os.path.join(mkdtemp(), str(uuid4()))
    new_torrent_file = os.path.join(os.getcwd(), 'dipshit.torrent')


    filesizes = [
                # filesize, torrent size
                 (1337, 3),
                 (5120, 50),
                 (11331, 100),
                 (11331, 250),
                 (11331, 30),
                ]

    try:
        for fs in filesizes:

            f = open(fpath, 'w+')
            f.seek((fs[0] * 1024 * 1024) - 1)
            f.write('\0')
            f.close()

            tt = Torrent(max_torrent_size=fs[1])
            print(convert_size(os.path.getsize(fpath)))

            tt.create_from(fpath)

            tt.to_file(new_torrent_file)
            print 'p', convert_size(tt._struct['piece length'])
            print ('Torrent file is %s size' % convert_size(os.path.getsize(new_torrent_file)))
            assert os.path.getsize(new_torrent_file) / 1024 < fs[1]

    except:
        raise
    finally:
        os.remove(fpath)
        os.remove(new_torrent_file)
        assert not os.path.isfile(fpath)
        assert not os.path.isfile(new_torrent_file)







if __name__ == '__main__':
    test_instance()
    pass
    #test_setters()