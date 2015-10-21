# -*- encoding: utf-8 -*-
from os.path import dirname, realpath, join
from collections import OrderedDict
import unittest

from torrentool.api import Bencode
from torrentool.exceptions import BencodeDecodingError


CURRENT_DIR = dirname(realpath(__file__))


class BencodeDecodeTests(unittest.TestCase):

    def test_read_file_dir(self):
        expected = [
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
        ]
        decoded = Bencode.read_file(join(CURRENT_DIR, 'test_dir.torrent'))
        self.assertEqual(decoded, expected)

    def test_read_file(self):
        expected = [
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
        ]
        decoded = Bencode.read_file(join(CURRENT_DIR, 'test_file.torrent'))
        self.assertEqual(decoded, expected)

    def test_decode_simple(self):
        decode = Bencode.read_string

        self.assertEqual(decode('4:spam')[0], 'spam')
        self.assertEqual(decode('0:')[0], '')

        self.assertEqual(decode('i3e')[0], 3)
        self.assertEqual(decode('i-3e')[0], -3)
        self.assertEqual(decode('i04e')[0], 4)
        self.assertEqual(decode('i0e')[0], 0)

        self.assertEqual(decode('l4:spam4:eggse')[0], ['spam', 'eggs'])
        self.assertEqual(decode('le')[0], [])

        self.assertEqual(decode('d3:cow3:moo4:spam4:eggse')[0], OrderedDict([('cow', 'moo'), ('spam', 'eggs')]))
        self.assertEqual(decode('d4:spaml1:a1:bee')[0], OrderedDict([('spam', ['a', 'b'])]))
        self.assertEqual(
            decode('d9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee')[0],
            OrderedDict([
                ('publisher', 'bob'),
                ('publisher-webpage', 'www.example.com'),
                ('publisher.location', 'home'),
            ]))
        self.assertEqual(decode('de')[0], OrderedDict())

    def test_error(self):
        self.assertRaises(BencodeDecodingError, Bencode.read_string, 'u:some')


if __name__ == '__main__':
    unittest.main()
