"""popen_command.command_basename names a Popen `args`' command by its basename."""
import pathlib

from veri.popen_command import command_basename


def test_str_args():
    assert command_basename("/usr/bin/git") == "git"


def test_bytes_args():
    assert command_basename(b"/usr/bin/git") == "git"


def test_pathlike_args():
    assert command_basename(pathlib.PurePosixPath("/usr/bin/git")) == "git"


def test_list_args():
    assert command_basename(["/usr/bin/git", "status"]) == "git"
