"""A pytest plugin the launcher loads: an unmarked (small) case may not start git, or python3 on anything but a veri/ module."""
import os
import subprocess

import pytest

VERI = os.path.dirname(os.path.abspath(__file__))


def refused(args):
    words = [args] if isinstance(args, (str, bytes, os.PathLike)) else list(args)
    words = [os.fsdecode(word) for word in words]
    if not words:
        return None
    command = os.path.basename(words[0])
    if command == "git":
        return command
    if command == "python3":
        target = os.path.abspath(words[1]) if len(words) > 1 else ""
        if not target.startswith(VERI + os.sep):
            return command
    return None


@pytest.fixture(autouse=True)
def small_case_process_refusal(request, monkeypatch):
    if request.node.get_closest_marker("process") is not None:
        return
    real = subprocess.Popen.__init__

    def checked(self, args, *rest, **kwargs):
        command = refused(args)
        if command is not None:
            raise AssertionError("a small case started %s; mark it process(...) or fake the call" % command)
        return real(self, args, *rest, **kwargs)

    monkeypatch.setattr(subprocess.Popen, "__init__", checked)
