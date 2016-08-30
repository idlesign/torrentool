# -*- encoding: utf-8 -*-
from os.path import dirname, realpath, join
from collections import OrderedDict


CURRENT_DIR = dirname(realpath(__file__))

FPATH_TORRENT_WITH_DIR = join(CURRENT_DIR, 'test_dir.torrent')
FPATH_TORRENT_SIMPLE = join(CURRENT_DIR, 'test_file.torrent')

STRUCT_TORRENT_WITH_DIR = (
    OrderedDict([
        ('announce', 'http://track1.org/1/'),
        ('announce-list', [
            ['http://track1.org/1/', 'http://track2.org/2/']
        ]),
        ('comment', u'примечание'),
        ('created by', 'Transmission/2.84 (14307)'),
        ('creation date', 1445766124),
        ('encoding', 'UTF-8'),
        ('info', OrderedDict([
            ('files', [
                OrderedDict([('length', 4), ('path', ['root.txt'])]),
                OrderedDict([('length', 4), ('path', ['sub1', 'sub11.txt'])]),
                OrderedDict([('length', 11), ('path', ['sub1', 'sub2', u'кириллица.txt'])]),
                OrderedDict([('length', 4), ('path', ['sub1', 'sub2', 'sub22.txt'])])
            ]),
            ('name', 'torrtest'),
            ('piece length', 32768),
            ('pieces', b'?\x9ew\xc1A\x84\x8d\x8b\xb7\x91\x19\xe3(\x1e\x1ex\x1e\xde\xa8\xdc'),
            ('private', 0)]))
    ])
)

STRUCT_TORRENT_SIMPLE = (
    OrderedDict([
        ('announce', 'udp://123.123.123.123'),
        ('created by', 'Transmission/2.84 (14307)'),
        ('creation date', 1445449205),
        ('encoding', 'UTF-8'),
        ('info', OrderedDict([
            ('length', 4),
            ('name', 'root.txt'),
            ('piece length', 32768),
            ('pieces', b'\xa8\xfd\xc2\x05\xa9\xf1\x9c\xc1\xc7Pz`\xc4\xf0\x1b\x13\xd1\x1d\x7f\xd0'),
            ('private', 1)])
         )
    ])
)
