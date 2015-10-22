
class TorrentoolException(Exception):
    """Base torrentool exception. All others are inherited from it."""


class BencodeError(TorrentoolException):
    """Base exception for bencode related errors."""


class BencodeDecodingError(BencodeError):
    """Raised when torrentool is unable to decode bencoded data."""


class BencodeEncodingError(BencodeError):
    """Raised when torrentool is unable to encode data into bencode."""


class TorrentError(TorrentoolException):
    """Base exception for Torrent object related errors."""
