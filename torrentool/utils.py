
def get_app_version():
    """Returns full version string including application name
    suitable for putting into Torrent.created_by.

    """
    from torrentool import VERSION
    return 'torrentool/%s' % '.'.join(map(str, VERSION))
