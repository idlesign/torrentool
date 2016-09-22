from __future__ import division

from calendar import timegm
import datetime
from functools import reduce
from hashlib import sha1
import math
from os import walk, sep
from os.path import join, isdir, getsize, normpath, basename
import time

from .bencode import Bencode
from .exceptions import TorrentError
from .utils import get_app_version


class Torrent(object):
    """Represents a torrent file, and exposes utilities to work with it."""

    _filepath = None

    def __init__(self,
                 dict_struct=None,
                 filepath=None,
                 min_piece_number=1000,
                 max_piece_number=1800,
                 min_piece_size=None,
                 max_piece_size=16777216,
                 max_torrent_size=None,
                 webseeds=None,
                 httpseeds=None,
                 private=None,
                 announce_list=None,
                 comment=None,
                 creation_date=None,
                 created_by=None
                 ):
        """

        Args:
            filepath(str): ''
            min_piece_number(int): xxx1000,
            max_piece_number(int): 1800,
            min_piece_size(None, int): ''
            max_piece_size(int): Max piece size in bytes.
            max_torrent_size(int, None): Set a max torrent size in kbits,
            webseeds(list): List of lists
            httpseeds(list): List of list=None,
            private(int): Make this torrent private, 1 or 0
            announce_list(list): List of lists,
            comment(str): Add  a comment to the meta data,
            creation_date(str): Date of torrent creation
            created_by(str): Torrentool or user defined
            add_md5(bool): md5 the files

        """
        self._struct = dict_struct or {'announce': '',
                                       'creation date': None,
                                       'info': {}
                                       }
        self._filepath = filepath
        self._files = []

        self._min_piece_number = min_piece_number
        self._max_piece_number = max_piece_number
        self._min_piece_size = min_piece_size
        self._max_piece_size = max_piece_size
        self._max_torrent_size = max_torrent_size

        if httpseeds:
            if not all(isinstance(i, list) for i in httpseeds):
                raise ValueError('httpseeds needs to be a list of lists')
            else:
                self._struct['httpseeds'] = httpseeds

        if webseeds:
            if not all(isinstance(i, list) for i in webseeds):
                raise ValueError('webseeds needs to be a list of lists')
            else:
                self._struct['url-list'] = webseeds

        if announce_list:
            if not all(isinstance(i, list) for i in announce_list):
                raise ValueError('announce list needs to be a list of lists')
            else:
                self._struct['announce-list'] = announce_list

        if comment:
            self._struct['comment'] = comment

        if private:
            if not isinstance(private, bool):
                raise ValueError('private must be bool')
            self._struct['info']['private'] = int(private)

        if created_by:
            self._struct['created by'] = created_by

        if creation_date:
            self.creation_date = creation_date

    def __str__(self):
        return 'Torrent: %s' % self.name

    @property
    def max_torrent_size(self):
        return self._max_torrent_size

    @max_torrent_size.setter
    def max_torrent_size(self, val):
        self._max_torrent_size = val

    @property
    def files(self):
        """Files in torrent. List of tuples (filepath, size)."""
        files = []
        info = self._struct.get('info')

        if 'files' in info:
            base = info['name']

            for f in info['files']:
                files.append((join(base, *f['path']), f['length']))

        else:
            if info.get('name') and info.get('length'):
                files.append((info['name'], info['length']))

        return files

    @property
    def total_size(self):
        """Total size of all files in torrent."""
        try:
            return reduce(lambda prev, curr: prev + curr[1], self.files, 0)
        except KeyError:
            return 0

    @property
    def info_hash(self):
        """Hash of torrent file info section. Also known as torrent hash."""
        info = self._struct.get('info')
        if 'name' in info:
            return sha1(Bencode.encode(info)).hexdigest()

    @property
    def magnet_link(self):
        """Magnet link using BTIH (BitTorrent Info Hash) URN."""
        return 'magnet:?xt=urn:btih:' + self.info_hash

    @property
    def webseeds(self):
        return self._struct.get('url-list', [])

    @webseeds.setter
    def webseeds(self, val):
        self._struct['url-list'] = val  # add valiation?

    @property
    def httpseeds(self):
        return self._struct.get('httpseeds', [])

    @httpseeds.setter
    def httpseeds(self, val):
        self._struct['httpseeds'] = val

    @property
    def announce_urls(self):
        """List of lists of tracker announce URLs."""
        urls = self._struct.get('announce-list')

        if not urls:
            urls = self._struct.get('announce')
            if not urls:
                return []
            urls = [[urls]]

        return urls

    @announce_urls.setter
    def announce_urls(self, val):
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

    @property
    def comment(self):
        """Optional. Free-form textual comments of the author."""
        return self._struct.get('comment')

    @comment.setter
    def comment(self, val):
        self._struct['comment'] = val

    @property
    def creation_date(self):
        """Optional. The creation time of the torrent, in standard UNIX epoch format. UTC."""
        date = self._struct.get('creation date')
        if date is not None:
            date = datetime.datetime.utcfromtimestamp(int(date))
        return date

    @creation_date.setter
    def creation_date(self, val):
        if isinstance(val, datetime.date):
            self._struct['creation date'] = timegm(val.timetuple())
        else:
            self._struct['creation date'] = val

    @property
    def created_by(self):
        """Optional. Name and version of the program used to create the .torrent"""
        return self._struct.get('created by')

    @created_by.setter
    def created_by(self, val):
        self._struct['created by'] = val

    @property
    def private(self):
        """Optional. If True the client MUST publish its presence to get other peers
        ONLY via the trackers explicitly described in the metainfo file. If False or is not present,
        the client may obtain peer from other means, e.g. PEX peer exchange, dht.
        """
        return bool(self._struct.get('info', {}).get('private', False))

    @private.setter
    def private(self, val):
        if not val:
            try:
                del self._struct['info']['private']
            except KeyError:
                pass
        else:
            self._struct['info']['private'] = 1

    @property
    def piece_size(self):
        return self._struct.get('info', {}).get('piece length')

    @property
    def name(self):
        """Torrent's name"""
        return self._struct.get('info', {}).get('name')

    @property
    def encoding(self):
        return self._struct.get('info', {}).get('encoding')

    @name.setter
    def name(self, val):
        self._struct['info']['name'] = val

    def to_file(self, filepath=None):
        """Writes Torrent object into file, either

        :param filepath:
        """
        if filepath is None and self._filepath is None:
            raise TorrentError(
                'Unable to save torrent to file: no filepath supplied.')

        if filepath is None:
            filepath = '%s.torrent' % self._filepath

        with open(filepath, mode='wb') as f:
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
                target_files.extend([join(base, fname)
                                     for fname in sorted(files)])

        else:
            target_files.append(src_path)

        target_files_ = []
        total_size = 0
        for fpath in target_files:
            file_size = getsize(fpath)
            if not file_size:
                continue
            target_files_.append((fpath, file_size, normpath(
                fpath.replace(src_path, '')).strip(sep).split(sep)))
            total_size += file_size

        return target_files_, total_size

    def _calc_size(self, size):
        block = 16384  # 16kb

        if self._max_torrent_size:
            # to kb
            self._max_torrent_size *= 1024
            # This only has to be close enough..
            t = self._max_torrent_size - len(self.to_string())
            # Set max to get the torrent as close to the limit as possible..
            self._max_piece_number = (t / 20) - 2
            self._min_piece_size = int(math.ceil(size / self._max_piece_number))

            while (self._min_piece_size % block):
                self._min_piece_size += 1

        if self._min_piece_size:
            piece_size = self._min_piece_size
        else:
            piece_size = 16384

        while True:
            n_pieces = int(math.ceil(size / piece_size))
            if n_pieces <= 1:
                piece_size *= 2
                break
            # Stop at optimal size or there isnt any enough pieces
            elif n_pieces >= self._min_piece_number and n_pieces <= self._max_piece_number:
                break
            elif self._min_piece_size and self._min_piece_size <= piece_size:
                break
            # User is da boss^^
            elif self._max_piece_size and self._max_piece_size <= piece_size:
                break
            else:
                # Larger faster plx
                if (size / (piece_size * 2) > self._min_piece_number):
                    piece_size *= 2
                else:
                    piece_size += block

        # Make sure we cover them all..
        num_pieces = size / piece_size
        if size % piece_size:
            num_pieces += 1

        if piece_size >= 16777216:
            print('Warning: This torrent can be hard to seed')

        assert piece_size % block == 0

        return piece_size, int(num_pieces)

    def create_from(self, src_path):
        """Returns Torrent object created from a file or a directory.

        :param str src_path:
        :rtype: Torrent
        """
        is_dir = isdir(src_path)
        target_files, size_data = self._get_target_files_info(src_path)

        info = {
            'name': basename(src_path),
            'pieces': '',
            'piece length': ''
        }

        # lets add some more incase this was called
        # before the torrent is created
        if not self.creation_date:
            self.creation_date = int(time.time())
        if not self.created_by:
            self.created_by = get_app_version()
        if self.private:
            info['private'] = 1

        if is_dir:
            files = []

            for _, length, path in target_files:
                files.append({'length': length, 'path': path})

            info['files'] = files

        else:
            info['length'] = target_files[0][1]

        self._struct['info'].update(info)
        size_piece, _ = self._calc_size(size_data)

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

        self._struct['info']['pieces'] = bytes(pieces)
        self._struct['info']['piece length'] = size_piece
        return self

    def from_string(self, string):
        """Alternative constructor to get Torrent object from string.

        :param str string:
        :rtype: Torrent
        """
        self._struct = Bencode.read_string(string)
        return self

    def from_file(self, filepath):
        """Alternative constructor to get Torrent object from file.

        :param str filepath:
        :rtype: Torrent
        """
        self._struct = Bencode.read_file(filepath)
        self._filepath = filepath
        return self
