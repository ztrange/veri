"""In-process cases for veri/coverage_blocker.py: the body it writes names the new issue as a blocker."""
import importlib
import json
import pathlib
import subprocess

import pytest

from veri.blocked_by import blockers


@pytest.fixture
def coverage_blocker():
    return importlib.import_module("veri.coverage_blocker")


@pytest.fixture(autouse=True)
def default_driver(monkeypatch):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)


def test_main_1262_exits_0_with_the_new_issue_a_blocker_and_every_line_kept_when_the_body_has_no_blocked_by_heading(
        monkeypatch, coverage_blocker):
    original = "## Problem\n\nx"
    written = {}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[2].startswith("repos/{owner}/{repo}/issues?"):
            return subprocess.CompletedProcess(args, 0, "[]", "")
        if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
            return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"body": original}), "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            path = args[args.index("-F") + 1].split("body=@", 1)[1]
            written["body"] = pathlib.Path(path).read_text()
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = coverage_blocker.main(["60"])

    body = written.get("body", "")
    assert (code, blockers(body, ""), all(line in body.split("\n") for line in original.split("\n"))) == (0, [77], True)
