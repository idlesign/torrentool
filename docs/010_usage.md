# Usage

## Using CLI

Requires `click` package (can be installed with: `pip install torrentool[cli]`).

```shell
# Make .torrent out of `video.mkv`
$ torrentool torrent create /home/my/files_here/video.mkv

# Make .torrent out of entire `/home/my/files_here` dir,
# and put some open trackers announce URLs into it,
# and publish file on torrent caching service, so it is ready to share.
$ torrentool torrent create /home/my/files_here --open_trackers --cache

# Print out existing file info.
$ torrentool torrent info /home/my/some.torrent

# Force colored or plain output (the NO_COLOR environment variable is also respected).
$ torrentool --no-color torrent info /home/my/some.torrent
```

Use command line `--help` switch to know more.

!!! note

    Some commands require `requests` package to be installed.

## From your Python code

```python
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

# The piece size is deduced from the data size by default; set it explicitly if needed:
new_torrent = Torrent.create_from('/home/idle/my_stuff/', piece_size=524288)

# Basic data (info hash, name, trackers) can also be read from a magnet link:
another_torrent = Torrent.from_magnet('magnet:?xt=urn:btih=0123456789abcdef0123456789abcdef01234567&dn=Stuff')
```
