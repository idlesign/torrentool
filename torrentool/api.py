from sys import version_info
from os.path import join, isdir, getsize, normpath, basename
from os import walk, sep
from hashlib import sha1
from codecs import encode
from datetime import datetime
from calendar import timegm
from functools import reduce
from collections import OrderedDict

from .exceptions import BencodeDecodingError, BencodeEncodingError, TorrentError

PY3 = version_info >= (3, 0)

if PY3:
    str_type = str
    chr_ = chr
else:
    str_type = basestring
    chr_ = lambda ch: ch


def get_app_version():
    """Returns full version string including application name
    suitable for putting into Torrent.created_by.

    """
    from torrentool import VERSION
    return 'torrentool/%s' % '.'.join(map(str, VERSION))


class Bencode(object):
    """Exposes utilities for bencoding."""

    @classmethod
    def encode(cls, value, val_encoding='utf-8'):
        """Encodes a value into bencoded bytes.

        :param value: Python object to be encoded (str, int, list, dict).
        :param str val_encoding: Encoding used by strings in a given object.
        :rtype: bytes
        """
        def encode_str(v):
            prefix = encode('%s:' % len(v), val_encoding)
            try:
                v_enc = encode(v, val_encoding)

            except UnicodeDecodeError:
                if PY3:
                    raise
                else:
                    # Suppose bytestring
                    v_enc = v

            return prefix + v_enc

        def encode_(val):
            if isinstance(val, str_type):
                result = encode_str(val)

            elif isinstance(val, int):
                result = encode(('i%se' % val), val_encoding)

            elif isinstance(val, (list, set, tuple)):
                result = encode('l', val_encoding)
                for item in val:
                    result += encode_(item)
                result += encode('e', val_encoding)

            elif isinstance(val, dict):
                result = encode('d', val_encoding)
                for k, v in val.items():
                    result += (encode_str(k) + encode_(v))
                result += encode('e', val_encoding)

            elif isinstance(val, bytes):  # Py3
                result = encode('%s:' % len(val), val_encoding)
                result += val

            else:
                raise BencodeEncodingError('Unable to encode `%s` type.' % type(val))

            return result

        return encode_(value)

    @classmethod
    def decode(cls, encoded):
        """Decodes bencoded data introduced as bytes.

        Returns decoded structure(s).

        :param bytes encoded:
        """
        def create_dict(items):
            return OrderedDict(zip(*[iter(items)] * 2))

        def create_list(items):
            return list(items)

        stack_items = []
        stack_containers = []

        def compress_stack():
            target_container = stack_containers.pop()
            subitems = []

            while True:
                subitem = stack_items.pop()
                subitems.append(subitem)
                if subitem is target_container:
                    break

            container_creator = subitems.pop()
            container = container_creator(reversed(subitems))
            stack_items.append(container)

        def parse_forward(till_char, sequence):
            number = ''
            char_sub_idx = 0

            for char_sub_idx, char_sub in enumerate(sequence):
                char_sub = chr_(char_sub)
                if char_sub == till_char:
                    break

                number += char_sub

            number = int(number or 0)
            char_sub_idx += 1

            return number, char_sub_idx

        while encoded:
            char = encoded[0]
            char = chr_(char)

            if char == 'd':  # Dictionary
                stack_items.append(create_dict)
                stack_containers.append(create_dict)
                encoded = encoded[1:]

            elif char == 'l':  # List
                stack_items.append(create_list)
                stack_containers.append(create_list)
                encoded = encoded[1:]

            elif char == 'i':  # Integer
                number, char_sub_idx = parse_forward('e', encoded[1:])
                char_sub_idx += 1

                stack_items.append(number)
                encoded = encoded[char_sub_idx:]

            elif char.isdigit():  # String
                str_len, char_sub_idx = parse_forward(':', encoded)
                last_char_idx = char_sub_idx+str_len

                string = encoded[char_sub_idx:last_char_idx]
                try:
                    string = string.decode('utf-8')
                except UnicodeDecodeError:
                    # Considered bytestring (e.g. `pieces` hashes concatenation).
                    pass

                stack_items.append(string)
                encoded = encoded[last_char_idx:]

            elif char == 'e':  # End of a dictionary or a list.
                compress_stack()
                encoded = encoded[1:]

            else:
                raise BencodeDecodingError('Unable to interpret `%s` char.' % char)

        if len(stack_items) == 1:
            stack_items = stack_items.pop()

        return stack_items

    @classmethod
    def read_string(cls, string):
        """Decodes a given bencoded string.

        Returns decoded structure(s).

        :param str string:
        :rtype: list
        """
        string = string.encode()
        return cls.decode(string)

    @classmethod
    def read_file(cls, filepath):
        """Decodes bencoded data of a given file.

        Returns decoded structure(s).

        :param str filepath:
        :rtype: list
        """
        with open(filepath, mode='rb') as f:
            contents = f.read()
        return cls.decode(contents)


class Torrent(object):
    """Represents a torrent file, and exposes utilities to work with it."""

    _filepath = None

    def __init__(self, dict_struct=None):
        dict_struct = dict_struct or {'info': {}}
        self._struct = dict_struct

    @property
    def files(self):
        """Files in torrent. List of tuples (filepath, size)."""
        files = []
        info = self._struct.get('info')

        if not info:
            return files

        if 'files' in info:
            base = info['name']

            for f in info['files']:
                files.append((join(base, *f['path']), f['length']))

        else:
            files.append((info['name'], info['length']))

        return files

    @property
    def total_size(self):
        """Total size of all files in torrent."""
        return reduce(lambda prev, curr: prev + curr[1], self.files, 0)

    @property
    def info_hash(self):
        """Hash of torrent file info section. Also known as torrent hash."""
        info = self._struct.get('info')

        if not info:
            return None

        return sha1(Bencode.encode(info)).hexdigest()

    @property
    def magnet_link(self):
        """Magnet link using BTIH (BitTorrent Info Hash) URN."""
        return 'magnet:?xt=urn:btih:' + self.info_hash

    def _get_announce_urls(self):
        urls = self._struct.get('announce-list')

        if not urls:
            urls = self._struct.get('announce')
            if not urls:
                return []
            urls = [[urls]]

        return urls

    def _set_announce_urls(self, val):
        self._struct['announce'] = ''
        self._struct['announce-list'] = []

        def set_single(val):
            del self._struct['announce-list']
            self._struct['announce'] = val

        types = (list, tuple, set)

        if isinstance(val, types):
            length = len(val)

            if length:
                if length == 1:
                    set_single(val[0])
                else:
                    for item in val:
                        if not isinstance(item, types):
                            item = [item]
                        self._struct['announce-list'].append(item)
                    self._struct['announce'] = val[0]

        else:
            set_single(val)

    announce_urls = property(_get_announce_urls, _set_announce_urls)
    """List of lists of tracker announce URLs."""

    def _get_comment(self):
        return self._struct.get('comment')

    def _set_comment(self, val):
        self._struct['comment'] = val

    comment = property(_get_comment, _set_comment)
    """Optional. Free-form textual comments of the author."""

    def _get_creation_date(self):
        date = self._struct.get('creation date')
        if date is not None:
            date = datetime.utcfromtimestamp(int(date))
        return date

    def _set_creation_date(self, val):
        self._struct['creation date'] = timegm(val.timetuple())

    creation_date = property(_get_creation_date, _set_creation_date)
    """Optional. The creation time of the torrent, in standard UNIX epoch format. UTC."""

    def _get_created_by(self):
        return self._struct.get('created by')

    def _set_created_by(self, val):
        self._struct['created by'] = val

    created_by = property(_get_created_by, _set_created_by)
    """Optional. Name and version of the program used to create the .torrent"""

    def _get_private(self):
        return self._struct.get('info', {}).get('private', False)

    def _set_private(self, val):
        if not val:
            try:
                del self._struct['info']['private']
            except KeyError:
                pass
        else:
            self._struct['info']['private'] = 1

    private = property(_get_private, _set_private)
    """Optional. If True the client MUST publish its presence to get other peers
    ONLY via the trackers explicitly described in the metainfo file. If False or is not present,
    the client may obtain peer from other means, e.g. PEX peer exchange, dht.

    """

    def to_file(self, filepath=None, encoding='utf-8'):
        """Writes Torrent object into file, either

        :param filepath:
        :param str encoding: Encoding used by strings in Torrent object.
        """
        if filepath is None and self._filepath is None:
            raise TorrentError('Unable to save torrent to file: no filepath supplied.')

        if filepath is not None:
            self._filepath = filepath

        with open(self._filepath, mode='wb') as f:
            f.write(self.to_string(encoding))

    def to_string(self, encoding='utf-8'):
        """Returns bytes representing torrent file.

        :param str encoding: Encoding used by strings in Torrent object.
        :rtype: bytearray
        """
        return Bencode.encode(self._struct, val_encoding=encoding)

    @classmethod
    def _get_target_files_info(cls, src_path):
        is_dir = isdir(src_path)
        target_files = []

        if is_dir:
            for base, _, files in walk(src_path):
                target_files.extend([join(base, fname) for fname in sorted(files)])

        else:
            target_files.append(src_path)

        target_files_ = []
        total_size = 0
        for fpath in target_files:
            file_size = getsize(fpath)
            if not file_size:
                continue
            target_files_.append((fpath, file_size, normpath(fpath.replace(src_path, '')).strip(sep).split(sep)))
            total_size += file_size

        return target_files_, total_size

    @classmethod
    def create_from(cls, src_path):
        """Returns Torrent object created from a file or a directory.

        :param str src_path:
        :rtype: Torrent
        """
        is_dir = isdir(src_path)
        target_files, size_data = cls._get_target_files_info(src_path)

        SIZE_MIN = 32768  # 32 KiB
        SIZE_DEFAULT = 262144  # 256 KiB
        SIZE_MAX = 1048576  # 1 MiB

        CHUNKS_MIN = 1000  # todo use those limits as advised
        CHUNKS_MAX = 2200

        size_piece = SIZE_MIN
        if size_data > SIZE_MIN:
            size_piece = SIZE_DEFAULT

        if size_piece > SIZE_MAX:
            size_piece = SIZE_MAX

        def read(filepath):
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(size_piece-len(pieces_buffer))
                    chunk_size = len(chunk)
                    if chunk_size == 0:
                        break
                    yield chunk

        pieces = bytearray()
        pieces_buffer = bytearray()

        for fpath, _, _ in target_files:
            for chunk in read(fpath):
                pieces_buffer += chunk

                if len(pieces_buffer) == size_piece:
                    pieces += sha1(pieces_buffer).digest()[:20]
                    pieces_buffer = bytearray()

        if len(pieces_buffer):
            pieces += sha1(pieces_buffer).digest()[:20]
            pieces_buffer = bytearray()

        info = {
            'name': basename(src_path),
            'pieces': pieces,
            'piece length': size_piece,
        }

        if is_dir:
            files = []

            for _, length, path in target_files:
                files.append({'length': length, 'path': path})

            info['files'] = files

        else:
            info['length'] = target_files[0][1]

        torrent = cls({'info': info})
        torrent.created_by = get_app_version()
        torrent.creation_date = datetime.utcnow()

        return torrent

    @classmethod
    def from_string(cls, string):
        """Alternative constructor to get Torrent object from string.

        :param str string:
        :rtype: Torrent
        """
        return cls(Bencode.read_string(string))

    @classmethod
    def from_file(cls, filepath):
        """Alternative constructor to get Torrent object from file.

        :param str filepath:
        :rtype: Torrent
        """
        torrent = cls(Bencode.read_file(filepath))
        torrent._filepath = filepath
        return torrent
