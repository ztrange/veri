"""In-process cases for veri/coverage_blocker.py, the module coverage-blocker.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys
import tempfile

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def coverage_blocker():
    return importlib.import_module("veri.coverage_blocker")


@pytest.fixture
def tmpdir_env(tmp_path, monkeypatch):
    """TMPDIR pointed at an empty directory under tmp_path."""
    scratch = tmp_path / "tmpdir"
    scratch.mkdir()
    monkeypatch.setenv("TMPDIR", str(scratch))
    monkeypatch.setattr(tempfile, "tempdir", None)
    return scratch


def test_main_returns_2_and_leaves_no_temp_file_when_the_patch_dies_with_5(tmpdir_env, monkeypatch, capsys, coverage_blocker):
    seen = {}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
            return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
        if args[:3] == ["gh", "issue", "view"]:
            return subprocess.CompletedProcess(args, 0, "## Blocked by\n\nNone\n", "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            path = args[args.index("-F") + 1].split("body=@", 1)[1]
            seen["path"] = path
            seen["existed"] = os.path.isfile(path)
            return subprocess.CompletedProcess(args, 5, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = coverage_blocker.main(["60"])

    assert (code, capsys.readouterr().out) == (2, "")
    assert seen.get("existed") is True
    assert pathlib.Path(seen["path"]).resolve().parent == tmpdir_env.resolve()
    assert list(tmpdir_env.iterdir()) == []


def test_main_patches_the_body_it_read_after_the_create_with_trailing_newlines_collapsed_to_one(tmpdir_env, monkeypatch, coverage_blocker):
    calls = []
    seen = {}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
            calls.append("create")
            return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
        if args == ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"]:
            calls.append("view")
            return subprocess.CompletedProcess(args, 0, "## Parent\n\n#1\n\n\n", "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            calls.append("patch")
            path = args[args.index("-F") + 1].split("body=@", 1)[1]
            seen["body"] = pathlib.Path(path).read_text()
            return subprocess.CompletedProcess(args, 5, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    coverage_blocker.main(["60"])

    assert calls == ["create", "view", "patch"]
    assert seen["body"] == "## Parent\n\n#1\n"


def test_main_leaves_no_temp_file_when_the_patch_raises(tmpdir_env, monkeypatch, coverage_blocker):
    class PatchDied(Exception):
        pass

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
            return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
        if args[:3] == ["gh", "issue", "view"]:
            return subprocess.CompletedProcess(args, 0, "## Blocked by\n\nNone\n", "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            raise PatchDied()
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    try:
        coverage_blocker.main(["60"])
    except PatchDied:
        pass

    assert list(tmpdir_env.iterdir()) == []
