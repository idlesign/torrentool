from os.path import join, isdir, getsize, normpath, basename
from os import walk, sep
from hashlib import sha1
from datetime import datetime
from calendar import timegm
from functools import reduce

from .bencode import Bencode
from .exceptions import TorrentError
from .utils import get_app_version


class Torrent(object):
    """Represents a torrent file, and exposes utilities to work with it."""

    _filepath = None

    def __init__(self, dict_struct=None):
        dict_struct = dict_struct or {'info': {}}
        self._struct = dict_struct

    def __str__(self):
        return 'Torrent: %s' % self.name

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

    def _get_name(self):
        return self._struct.get('info', {}).get('name', None)

    def _set_name(self, val):
        self._struct['info']['name'] = val

    name = property(_get_name, _set_name)
    """ Torrent's name """

    def to_file(self, filepath=None):
        """Writes Torrent object into file, either

        :param filepath:
        """
        if filepath is None and self._filepath is None:
            raise TorrentError('Unable to save torrent to file: no filepath supplied.')

        if filepath is not None:
            self._filepath = filepath

        with open(self._filepath, mode='wb') as f:
            f.write(self.to_string())

    def to_string(self):
        """Returns bytes representing torrent file.

        :param str encoding: Encoding used by strings in Torrent object.
        :rtype: bytearray
        """
        return Bencode.encode(self._struct)

    @classmethod
    def _get_target_files_info(cls, src_path):
        src_path = u'%s' % src_path  # Force walk() to return unicode names.

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
                    chunk = f.read(size_piece - len(pieces_buffer))
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
            'pieces': bytes(pieces),
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
