"""popen_command.command_basename names a Popen `args`' command by its basename."""
import pathlib

import pytest

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


def test_each_guard_asks_the_helper_for_the_command_2012(monkeypatch, tmp_path_factory):
    import importlib
    import subprocess
    import network_guard
    import small_case_guard
    from veri import popen_command

    asked = []

    def spy(args):
        asked.append(args)
        return "git"

    monkeypatch.setattr(popen_command, "command_basename", spy)
    try:
        importlib.reload(small_case_guard)
        assert small_case_guard.refused(["anything"]) == "git"
        assert asked == [["anything"]]

        asked.clear()
        installed = {}

        class Recorder:
            def setattr(self, target, name, value):
                installed[name] = value

        monkeypatch.setattr(popen_command, "command_basename", lambda args: asked.append(args) or "gh")
        importlib.reload(network_guard)
        monkeypatch.setattr(subprocess.Popen, "__init__", lambda self, *a, **k: None)
        network_guard.network_refusal.__wrapped__(Recorder(), tmp_path_factory)
        with pytest.raises(AssertionError, match="a case started gh"):
            installed["__init__"](None, ["x"])
        assert asked == [["x"]]
    finally:
        monkeypatch.undo()
        importlib.reload(small_case_guard)
        importlib.reload(network_guard)


def test_network_guard_refuses_an_iterator_args_as_it_does_the_list_2012(monkeypatch, tmp_path_factory):
    import subprocess
    import network_guard

    installed = {}

    class Recorder:
        def setattr(self, target, name, value):
            installed[name] = value

    monkeypatch.setattr(subprocess.Popen, "__init__", lambda self, *a, **k: None)
    network_guard.network_refusal.__wrapped__(Recorder(), tmp_path_factory)
    with pytest.raises(AssertionError, match="a case started gh"):
        installed["__init__"](None, ["gh"])
    with pytest.raises(AssertionError, match="a case started gh"):
        installed["__init__"](None, iter(["gh"]))


def test_small_case_guard_allows_an_iterator_args_as_it_does_the_list_2012():
    import os
    import small_case_guard

    words = ["python3", os.path.join(small_case_guard.VERI, "status.py")]

    assert small_case_guard.refused(words) is None
    assert small_case_guard.refused(iter(words)) is None


def test_small_case_guard_raises_its_own_type_error_for_a_non_str_word_2012():
    import small_case_guard

    with pytest.raises(TypeError):
        small_case_guard.refused(["ls", 5])
