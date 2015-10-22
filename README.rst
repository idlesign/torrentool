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
    :target: https://travis-ci.org/idlesign/django-sitegate

.. image:: https://img.shields.io/codeclimate/github/idlesign/torrentool.svg
   :target: https://codeclimate.com/github/idlesign/torrentool


Description
-----------

*The tool to work with torrent files.*

Includes:

* Torrent utils (to create and modify files)
* Bencoding utils (decoder, encoder)

Can be used both as python module and console application.

.. code-block:: python

    from torrentool.api import Torrent

    my_torrent = Torrent.from_file('/home/idle/some.torrent')

    print(my_torrent.announce_urls)  # Get torrent trackers announce URLs.
    my_torrent.comment = 'Your torrents are mine.'  # Set a comment.



Documentation
-------------

Will be available at http://torrentool.readthedocs.org/
