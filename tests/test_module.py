# -*- encoding: utf-8 -*-
import sys
import unittest
from uuid import uuid4
from tempfile import mkdtemp
from os.path import dirname, realpath, join
from collections import OrderedDict
from datetime import datetime

from torrentool.api import Bencode, Torrent, get_app_version
from torrentool.exceptions import BencodeDecodingError, BencodeEncodingError, TorrentError


if sys.version_info >= (3, 0):
    enc = lambda v: v.encode()
else:
    enc = lambda v: v

decode = Bencode.read_string
encode = Bencode.encode

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


def read_file(filepath):
    with open(filepath, mode='rb') as f:
        contents = f.read()
    return contents


class TorrentTests(unittest.TestCase):

    def test_create(self):
        t = Torrent.create_from(join(CURRENT_DIR, 'torrtest', 'root.txt'))
        t.private = True
        self.assertEqual(t._struct['info'], STRUCT_TORRENT_SIMPLE['info'])

        # todo
        # t = Torrent.create_from(join(CURRENT_DIR, 'torrtest'))
        # expected = dict(STRUCT_TORRENT_WITH_DIR['info'])
        # del expected['private']
        # self.assertEqual(t._struct['info'], expected)

    def test_getters_simple(self):
        t = Torrent.from_file(FPATH_TORRENT_SIMPLE)

        self.assertEqual(t._filepath, FPATH_TORRENT_SIMPLE)

        self.assertEqual(t.created_by, 'Transmission/2.84 (14307)')
        self.assertEqual(t.files, [('root.txt', 4)])
        self.assertEqual(t.total_size, 4)
        self.assertEqual(t.announce_urls, [['udp://123.123.123.123']])
        self.assertEqual(t.creation_date.isoformat(), '2015-10-21T17:40:05')
        self.assertIsNone(t.comment)

        hash_expected = '238967c8417cc6ccc378df16687d1958277f270b'
        self.assertEqual(t.info_hash, hash_expected)

        magnet = t.magnet_link
        self.assertIn(hash_expected, magnet)
        self.assertIn('btih', magnet)
        self.assertIn('magnet:', magnet)

    def test_getters_dir(self):
        t = Torrent.from_file(FPATH_TORRENT_WITH_DIR)

        self.assertEqual(t._filepath, FPATH_TORRENT_WITH_DIR)

        self.assertEqual(t.created_by, 'Transmission/2.84 (14307)')
        self.assertEqual(t.files, [
            ('torrtest/root.txt', 4),
            ('torrtest/sub1/sub11.txt', 4),
            (u'torrtest/sub1/sub2/кириллица.txt', 11),
            ('torrtest/sub1/sub2/sub22.txt', 4)
        ])
        self.assertEqual(t.total_size, 23)
        self.assertEqual(t.announce_urls, [['http://track1.org/1/', 'http://track2.org/2/']])
        self.assertEqual(t.creation_date.isoformat(), '2015-10-25T09:42:04')
        self.assertEqual(t.comment, u'примечание')

        hash_expected = 'ae513c403120f6ae8a2d5c11ae969340a9af0ca1'
        self.assertEqual(t.info_hash, hash_expected)

        magnet = t.magnet_link
        self.assertIn(hash_expected, magnet)
        self.assertIn('btih', magnet)
        self.assertIn('magnet:', magnet)

    def test_setters(self):
        t = Torrent()

        self.assertIsNone(t.info_hash)
        self.assertIsNone(t.comment)
        self.assertIsNone(t.created_by)
        self.assertIsNone(t.creation_date)
        self.assertEqual(t.total_size, 0)
        self.assertEqual(t.announce_urls, [])
        self.assertEqual(t.files, [])

        t.comment = 'mycomment'
        self.assertEqual(t.comment, 'mycomment')

        t.created_by = 'some/1.0'
        self.assertEqual(t.created_by, 'some/1.0')

        now = datetime.now()
        t.creation_date = now
        self.assertEqual(t.creation_date, now.replace(microsecond=0))

        t.announce_urls = 'some1'
        self.assertEqual(t.announce_urls, [['some1']])
        self.assertEqual(t._struct['announce'], 'some1')
        self.assertNotIn('announce-list', t._struct)

        t.announce_urls = ['some3', 'some4']
        self.assertEqual(t.announce_urls, [['some3'], ['some4']])
        self.assertEqual(t._struct['announce'], 'some3')

        t.announce_urls = ['some5']
        self.assertEqual(t.announce_urls, [['some5']])
        self.assertEqual(t._struct['announce'], 'some5')
        self.assertNotIn('announce-list', t._struct)

        self.assertFalse(t.private)
        t.private = False
        self.assertFalse(t.private)
        t.private = True
        self.assertTrue(t.private)
        t.private = False
        self.assertFalse(t.private)


    def test_from_string(self):
        torrstr = '4:spam'
        t = Torrent.from_string(torrstr)
        self.assertEqual(t._struct, 'spam')

    def test_to_file(self):
        t0 = Torrent({})
        self.assertRaises(TorrentError, t0.to_file)

        t1 = Torrent.from_file(FPATH_TORRENT_SIMPLE)
        fpath = join(mkdtemp(), str(uuid4()))
        t1.to_file(fpath)

        t2 = Torrent.from_file(fpath)
        self.assertEqual(t1._struct, t2._struct)


class BencodeDecodeTests(unittest.TestCase):

    def test_read_file_dir(self):
        decoded = Bencode.read_file(FPATH_TORRENT_WITH_DIR)
        self.assertEqual(decoded, STRUCT_TORRENT_WITH_DIR)

    def test_read_file(self):
        decoded = Bencode.read_file(FPATH_TORRENT_SIMPLE)
        self.assertEqual(decoded, STRUCT_TORRENT_SIMPLE)

    def test_decode_simple(self):
        self.assertEqual(decode('4:spam'), 'spam')
        self.assertEqual(decode('0:'), '')

        self.assertEqual(decode('i3e'), 3)
        self.assertEqual(decode('i-3e'), -3)
        self.assertEqual(decode('i04e'), 4)
        self.assertEqual(decode('i0e'), 0)

        self.assertEqual(decode('l4:spam4:eggse'), ['spam', 'eggs'])
        self.assertEqual(decode('le'), [])

        self.assertEqual(decode('d3:cow3:moo4:spam4:eggse'), OrderedDict([('cow', 'moo'), ('spam', 'eggs')]))
        self.assertEqual(decode('d4:spaml1:a1:bee'), OrderedDict([('spam', ['a', 'b'])]))
        self.assertEqual(
            decode('d9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee'),
            OrderedDict([
                ('publisher', 'bob'),
                ('publisher-webpage', 'www.example.com'),
                ('publisher.location', 'home'),
            ]))
        self.assertEqual(decode('de'), OrderedDict())

    def test_errors(self):
        self.assertRaises(BencodeDecodingError, Bencode.read_string, 'u:some')


class BencodeEncodeTests(unittest.TestCase):

    def test_encode_simple(self):
        self.assertEqual(encode('spam'), enc('4:spam'))
        self.assertEqual(encode(''), enc('0:'))

        self.assertEqual(encode(3), enc('i3e'))
        self.assertEqual(encode(-3), enc('i-3e'))
        self.assertEqual(encode(0), enc('i0e'))

        self.assertEqual(encode(['spam', 'eggs']), enc('l4:spam4:eggse'))
        self.assertEqual(encode([]), enc('le'))

        self.assertEqual(encode(OrderedDict([('cow', 'moo'), ('spam', 'eggs')])), enc('d3:cow3:moo4:spam4:eggse'))
        self.assertEqual(encode(OrderedDict([('spam', ['a', 'b'])])), enc('d4:spaml1:a1:bee'))
        self.assertEqual(
            encode(OrderedDict([
                ('publisher', 'bob'),
                ('publisher-webpage', 'www.example.com'),
                ('publisher.location', 'home'),
            ])),
            enc('d9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee')
        )
        self.assertEqual(encode(OrderedDict()), enc('de'))

    def test_encode_complex(self):
        encoded = encode(STRUCT_TORRENT_SIMPLE)
        from_file = read_file(FPATH_TORRENT_SIMPLE)
        self.assertEqual(encoded, from_file)

    def test_errors(self):
        self.assertRaises(BencodeEncodingError, Bencode.encode, object())


class OtherTests(unittest.TestCase):

    def test_get_app_version(self):
        self.assertIn('torrentool', get_app_version())


if __name__ == '__main__':
    unittest.main()
