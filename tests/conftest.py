import pytest


@pytest.fixture
def torr_test_file(datafix_dir):
    return str(datafix_dir / 'test_file.torrent')


@pytest.fixture
def torr_test_dir(datafix_dir):
    return str(datafix_dir / 'test_dir.torrent')


@pytest.fixture(scope='session')
def struct_torr_dir():
    return {
        'announce': 'http://track1.org/1/',
        'announce-list': [
            ['http://track1.org/1/', 'http://track2.org/2/']
        ],
        'comment': 'примечание',
        'created by': 'Transmission/2.84 (14307)',
        'creation date': 1445766124,
        'encoding': 'UTF-8',
        'info': {
            'files': [
                {'length': 4, 'path': ['root.txt']},
                {'length': 4, 'path': ['sub1', 'sub11.txt']},
                {'length': 11, 'path': ['sub1', 'sub2', 'кириллица.txt']},
                {'length': 4, 'path': ['sub1', 'sub2', 'sub22.txt']}
            ],
            'name': 'torrtest',
            'piece length': 32768,
            'pieces': b'?\x9ew\xc1A\x84\x8d\x8b\xb7\x91\x19\xe3(\x1e\x1ex\x1e\xde\xa8\xdc',
            'private': 0,
        }
    }


@pytest.fixture(scope='session')
def struct_torr_file():
    return {
        'announce': 'udp://123.123.123.123',
        'created by': 'Transmission/2.84 (14307)',
        'creation date': 1445449205,
        'encoding': 'UTF-8',
        'info': {
            'length': 4,
            'name': 'root.txt',
            'piece length': 32768,
            'pieces': b'\xa8\xfd\xc2\x05\xa9\xf1\x9c\xc1\xc7Pz`\xc4\xf0\x1b\x13\xd1\x1d\x7f\xd0',
            'private': 1,
        }
    }
