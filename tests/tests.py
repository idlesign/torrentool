# -*- encoding: utf-8 -*-
import sys
from os.path import dirname, realpath, join
from collections import OrderedDict
import unittest

from torrentool.api import Bencode
from torrentool.exceptions import BencodeDecodingError, BencodeEncodingError


if sys.version_info >= (3, 0):
    enc = lambda v: v.encode()
else:
    enc = lambda v: v

decode = Bencode.read_string
encode = Bencode.encode

CURRENT_DIR = dirname(realpath(__file__))

FPATH_TORRENT_WITH_DIR = join(CURRENT_DIR, 'test_dir.torrent')
FPATH_TORRENT_SIMPLE = join(CURRENT_DIR, 'test_file.torrent')


def read_file(filepath):
    with open(filepath, mode='rb') as f:
        contents = f.read()
    return contents


class BencodeDecodeTests(unittest.TestCase):

    torrent_with_dirs = (
        OrderedDict([
            ('announce', 'http://track1.org/1/'),
            ('announce-list', [
                ['http://track1.org/1/', 'http://track2.org/2/']
            ]),
            ('comment', 'примечание'),
            ('created by', 'Transmission/2.84 (14307)'),
            ('creation date', 1445435220),
            ('encoding', 'UTF-8'),
            ('info', OrderedDict([
                ('files', [
                    OrderedDict([('length', 4), ('path', ['root.txt'])]),
                    OrderedDict([('length', 4), ('path', ['sub1', 'sub11.txt'])]),
                    OrderedDict([('length', 4), ('path', ['sub1', 'sub2', 'sub22.txt'])])
                ]),
                ('name', 'torrtest'),
                ('piece length', 32768),
                ('pieces', b'\x12\x16\x97N\xea\x14BV6\x02O\xcf\xac+\xcc\xf2\xed\x1f3\x81'),
                ('private', 0)]))
        ])
    )

    torrent_simple = (
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

    def test_read_file_dir(self):
        decoded = Bencode.read_file(FPATH_TORRENT_WITH_DIR)
        self.assertEqual(decoded, self.torrent_with_dirs)

    def test_read_file(self):
        decoded = Bencode.read_file(FPATH_TORRENT_SIMPLE)
        self.assertEqual(decoded, self.torrent_simple)

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
        self.assertRaises(BencodeEncodingError, Bencode.encode, object())

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
        encoded = encode(self.torrent_simple)
        from_file = read_file(FPATH_TORRENT_SIMPLE)
        self.assertEqual(encoded, from_file)


if __name__ == '__main__':
    unittest.main()
