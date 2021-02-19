import pytest

from torrentool.api import Bencode
from torrentool.exceptions import BencodeDecodingError, BencodeEncodingError

enc = lambda v: v.encode()

decode = Bencode.read_string
encode = Bencode.encode


def read_file(filepath):
    with open(filepath, mode='rb') as f:
        contents = f.read()
    return contents


def test_non_utf_string():
    bogus = b'32:J\xf3ban Rosszban [2005] Bor\xedt\xf3.jpg'

    assert decode(bogus) == bogus[3:]
    assert decode(bogus, byte_keys={'some'}) == 'J�ban Rosszban [2005] Bor�t�.jpg'


def test_read_file_dir(torr_test_dir, struct_torr_dir):
    decoded = Bencode.read_file(torr_test_dir)
    assert decoded == struct_torr_dir


def test_read_file(torr_test_file, struct_torr_file):
    decoded = Bencode.read_file(torr_test_file)
    assert decoded == struct_torr_file


def test_decode_simple():
    assert decode('4:spam') == 'spam'
    assert decode('0:') == ''

    assert decode('i3e') == 3
    assert decode('i-3e') == -3
    assert decode('i04e') == 4
    assert decode('i0e') == 0

    assert decode('l4:spam4:eggse') == ['spam', 'eggs']
    assert decode('le') == []

    assert decode('d3:cow3:moo4:spam4:eggse') == {'cow': 'moo', 'spam': 'eggs'}
    assert decode('d4:spaml1:a1:bee') == {'spam': ['a', 'b']}
    assert (
        decode('d9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee')  ==
        {
            'publisher': 'bob',
            'publisher-webpage': 'www.example.com',
            'publisher.location': 'home',
        })
    assert decode('de') == {}


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

    assert encode({'cow': 'moo', 'spam': 'eggs'}) == enc('d3:cow3:moo4:spam4:eggse')
    assert encode({'spam': ['a', 'b']}) == enc('d4:spaml1:a1:bee')
    assert (
        encode({
            'publisher': 'bob',
            'publisher-webpage': 'www.example.com',
            'publisher.location': 'home',
        }) ==
        enc('d9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee')
    )
    assert encode({}) == enc('de')


def test_encode_complex(struct_torr_file, struct_torr_dir, torr_test_file, torr_test_dir):
    encoded = encode(struct_torr_file)
    from_file = read_file(torr_test_file)
    assert encoded == from_file

    encoded = encode(struct_torr_dir)
    from_file = read_file(torr_test_dir)
    assert encoded == from_file


def test_encode_errors():
    with pytest.raises(BencodeEncodingError):
        Bencode.encode(object())
