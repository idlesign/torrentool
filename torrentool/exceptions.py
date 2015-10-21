
class TorrentoolException(Exception):
    pass


class BencodeError(TorrentoolException):
    pass


class BencodeDecodingError(BencodeError):
    pass
