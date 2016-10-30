# -*- encoding: utf-8 -*-
import sys
import pytest

from torrentool.api import Bencode
from torrentool.exceptions import BencodeDecodingError, BencodeEncodingError

from common import *


PY3 = sys.version_info >= (3, 0)

if PY3:
    enc = lambda v: v.encode()
else:
    enc = lambda v: v

decode = Bencode.read_string
encode = Bencode.encode


def read_file(filepath):
    with open(filepath, mode='rb') as f:
        contents = f.read()
    return contents


def test_read_file_dir():
    decoded = Bencode.read_file(FPATH_TORRENT_WITH_DIR)
    assert decoded == STRUCT_TORRENT_WITH_DIR


def test_read_file():
    decoded = Bencode.read_file(FPATH_TORRENT_SIMPLE)
    assert decoded == STRUCT_TORRENT_SIMPLE


def test_decode_simple():
    assert decode('4:spam') == 'spam'
    assert decode('0:') == ''

    assert decode('i3e') == 3
    assert decode('i-3e') == -3
    assert decode('i04e') == 4
    assert decode('i0e') == 0

    assert decode('l4:spam4:eggse') == ['spam', 'eggs']
    assert decode('le') == []

    assert decode('d3:cow3:moo4:spam4:eggse'), OrderedDict([('cow', 'moo') == ('spam', 'eggs')])
    assert decode('d4:spaml1:a1:bee') == OrderedDict([('spam', ['a', 'b'])])
    assert (
        decode('d9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee')  ==
        OrderedDict([
            ('publisher', 'bob'),
            ('publisher-webpage', 'www.example.com'),
            ('publisher.location', 'home'),
        ]))
    assert decode('de') == OrderedDict()


def test_decode_errors():
    with pytest.raises(BencodeDecodingError):
        Bencode.read_string('u:some')


def test_encode_simple():
    assert encode('spam') == enc('4:spam')
    assert encode('') == enc('0:')

    assert encode(b'spam') == enc('4:spam')
    assert encode(b'\xd0\xb9') == b'2:\xd0\xb9'

    assert encode(3) == enc('i3e')
    assert encode(-3) == enc('i-3e')
    assert encode(0) == enc('i0e')

    assert encode(['spam', 'eggs']) == enc('l4:spam4:eggse')
    assert encode([]) == enc('le')

    assert encode(OrderedDict([('cow', 'moo'), ('spam', 'eggs')])) == enc('d3:cow3:moo4:spam4:eggse')
    assert encode(OrderedDict([('spam', ['a', 'b'])])) == enc('d4:spaml1:a1:bee')
    assert (
        encode(OrderedDict([
            ('publisher', 'bob'),
            ('publisher-webpage', 'www.example.com'),
            ('publisher.location', 'home'),
        ])) ==
        enc('d9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee')
    )
    assert encode(OrderedDict()) == enc('de')


def test_encode_complex():
    encoded = encode(STRUCT_TORRENT_SIMPLE)
    from_file = read_file(FPATH_TORRENT_SIMPLE)
    assert encoded == from_file

    encoded = encode(STRUCT_TORRENT_WITH_DIR)
    from_file = read_file(FPATH_TORRENT_WITH_DIR)
    assert encoded == from_file


def test_encode_errors():
    with pytest.raises(BencodeEncodingError):
        Bencode.encode(object())


@pytest.mark.xfail(PY3, reason='py3 has no long')
def test_encode_error_long():
    # os.path.getsize() can be longs on py2
    a_long = long(741634835)
    Bencode.encode(a_long)
