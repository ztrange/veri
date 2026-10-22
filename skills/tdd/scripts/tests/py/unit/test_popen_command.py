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


def test_guards_and_helper_test_share_one_popen_command_module_2012():
    import network_guard
    import small_case_guard
    from veri import popen_command

    for guard in (network_guard, small_case_guard):
        assert guard.command_basename is popen_command.command_basename
        assert guard.command_words is popen_command.command_words
