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

.. image:: https://landscape.io/github/idlesign/torrentool/master/landscape.svg?style=flat
   :target: https://landscape.io/github/idlesign/torrentool/master

.. image:: https://img.shields.io/travis/idlesign/torrentool/master.svg
    :target: https://travis-ci.org/idlesign/torrentool

.. image:: https://img.shields.io/codeclimate/github/idlesign/torrentool.svg
   :target: https://codeclimate.com/github/idlesign/torrentool


Description
-----------

*The tool to work with torrent files.*

Works on Python 2.7+ and 3.3+.

Includes:

* Torrent utils (file read and modification)
* Bencoding utils (decoder, encoder)


.. code-block:: python

    from torrentool.api import Torrent


    my_torrent = Torrent.from_file('/home/idle/some.torrent')

    my_torrent.announce_urls  # Torrent trackers announce URLs.
    my_torrent.total_size  # Total files size in bytes.
    my_torrent.magnet_link  # Magnet link for you.

    # Etc.

    my_torrent.comment = 'Your torrents are mine.'  # Set a comment.

    my_torrent.to_file()  # Save changes to file

