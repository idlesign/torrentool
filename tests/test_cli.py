from click.testing import CliRunner

from torrentool.cli import start


def test_torrent_info_color(torr_test_file):

    result = CliRunner().invoke(start, ["--color", "torrent", "info", torr_test_file], color=True)

    assert result.exit_code == 0
    assert "\x1b[" in result.output


def test_torrent_info_no_color(torr_test_file):

    result = CliRunner().invoke(start, ["--no-color", "torrent", "info", torr_test_file], color=True)

    assert result.exit_code == 0
    assert "\x1b[" not in result.output
