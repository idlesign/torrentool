import math


def get_app_version():
    """Returns full version string including application name
    suitable for putting into Torrent.created_by.

    """
    from torrentool import VERSION
    return 'torrentool/%s' % '.'.join(map(str, VERSION))


def humanize_filesize(bytes_size):
    """Returns human readable filesize.

    :param int bytes_size:
    :rtype: str
    """
    if not bytes_size:
        return '0 B'
    
    names = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

    name_idx = int(math.floor(math.log(bytes_size, 1024)))
    size = round(bytes_size / math.pow(1024, name_idx), 2)

    return '%s %s' % (size, names[name_idx])
