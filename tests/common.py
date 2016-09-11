# -*- encoding: utf-8 -*-
from os.path import dirname, realpath, join
from collections import OrderedDict


CURRENT_DIR = dirname(realpath(__file__))

FPATH_TORRENT_WITH_DIR = join(CURRENT_DIR, 'test_dir.torrent')
FPATH_TORRENT_SIMPLE = join(CURRENT_DIR, 'test_file.torrent')

STRUCT_TORRENT_WITH_DIR = (
    OrderedDict([
        ('announce', 'udp://123.123.123.123'),
        ('comment', u'примечание'),
        ('created by', 'torrentool/0.3.0'),
        ('creation date', 1473889851),
        #('encoding', 'UTF-8'),
        ('info', OrderedDict([
            ('files', [
                OrderedDict([('length', 3), ('path', ['root.txt'])]),
                OrderedDict([('length', 5), ('path', ['sub1', 'sub11.txt'])]),
                OrderedDict([('length', 5), ('path', ['sub1', 'sub2', 'sub22.txt'])]),
                OrderedDict([('length', 11), ('path', ['sub1', 'sub2', u'\u043a\u0438\u0440\u0438\u043b\u043b\u0438\u0446\u0430.txt'])]),

            ]),
            ('name', 'torrtest'),
            ('piece length', 32768),
            ('pieces', b'\x00g\x9a\xf8$\x8eDq\r\x1c\x1f\xc0\x801\x93*:f&G'),
            ('private', 1)]))
    ])
)

STRUCT_TORRENT_SIMPLE = (
    OrderedDict([
        ('announce', 'udp://123.123.123.123'),
        ('created by', 'torrentool/0.3.0'),
        ('creation date', 1473886180),
        ('info', OrderedDict([
            ('length', 3),
            ('name', 'root.txt'),
            ('piece length', 32768),
            ('pieces', b'@\xbd\x00\x15c\x08_\xc3Qe2\x9e\xa1\xff\\^\xcb\xdb\xbe\xef'),
            ('private', 1)])
         )
    ])
)
