torrentool
==========
https://github.com/idlesign/torrentool

.. image:: https://img.shields.io/pypi/v/torrentool.svg
    :target: https://pypi.python.org/pypi/torrentool

.. image:: https://img.shields.io/pypi/dm/torrentool.svg
    :target: https://pypi.python.org/pypi/torrentool

.. image:: https://img.shields.io/pypi/l/torrentool.svg
    :target: https://pypi.python.org/pypi/torrentool

.. image:: https://img.shields.io/coveralls/idlesign/torrentool/master.svg
    :target: https://coveralls.io/r/idlesign/torrentool

.. image:: https://img.shields.io/travis/idlesign/torrentool/master.svg
    :target: https://travis-ci.org/idlesign/torrentool

.. image:: https://landscape.io/github/idlesign/torrentool/master/landscape.svg?style=flat
   :target: https://landscape.io/github/idlesign/torrentool/master


Description
-----------

*The tool to work with torrent files.*

Works on Python 2.7+ and 3.3+.

Includes:

* Command line interface (requires ``click`` package to be installed)
* Torrent utils (file creation, read and modification)
* Bencoding utils (decoder, encoder)


Using CLI
~~~~~~~~~

.. code-block:: bash

    ; Make .torrent out of `video.mkv`
    $ torrentool torrent create /home/my/files_here/video.mkv

    ; Make .torrent out of entire `/home/my/files_here` dir,
    ; and put some open trackers announce URLs into it,
    ; and publish file on torrent caching service, so it is ready to share.
    $ torrentool torrent create /home/my/files_here --open_trackers --cache

    ; Print out existing file info.
    $ torrentool torrent info /home/my/some.torrent


Use command line ``--help`` switch to know more.

.. note:: Some commands require ``requests`` package to be installed.


From your Python code
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from torrentool.api import Torrent

    # Reading and modifying an existing file.
    my_torrent = Torrent.from_file('/home/idle/some.torrent')
    my_torrent.total_size  # Total files size in bytes.
    my_torrent.magnet_link  # Magnet link for you.
    my_torrent.comment = 'Your torrents are mine.'  # Set a comment.
    my_torrent.to_file()  # Save changes.

    # Or we can create a new torrent from a directory.
    new_torrent = Torrent.create_from('/home/idle/my_stuff/')  # or it could have been a single file
    new_torrent.announce_urls = 'udp://tracker.openbittorrent.com:80'
    new_torrent.to_file('/home/idle/another.torrent')

