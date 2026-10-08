"""In-process cases for veri/tick_issue_criterion.py, the module tick-issue-criterion.sh is a shim over."""
import importlib
import json
import os
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.fixture
def tick_issue_criterion():
    return importlib.import_module("veri.tick_issue_criterion")


def test_main_returns_2_with_the_usage_line_and_no_subprocess_call_for_a_missing_or_empty_number(monkeypatch, capsys, tick_issue_criterion):
    def refuse(args, **kwargs):
        raise AssertionError("unexpected subprocess call: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    for argv in ([], [""]):
        code = tick_issue_criterion.main(argv)
        captured = capsys.readouterr()
        assert (code, captured.out, captured.err) == (2, "", "usage: tick-issue-criterion.sh <issue-number> <matcher>\n")


def test_main_returns_3_with_no_patch_and_names_the_matcher_and_issue_when_no_unchecked_criterion_matches(monkeypatch, capsys, tick_issue_criterion):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    real_run = subprocess.run
    patches = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] == ["gh", "issue", "view"]:
            return subprocess.CompletedProcess(args, 0, "- [ ] alpha\n", "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            patches.append(args)
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "gh":
            raise AssertionError("unexpected gh call: %r" % (args,))
        return real_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = tick_issue_criterion.main(["7", "zeta"])

    assert (code, capsys.readouterr().err, patches) == (3, "tick-issue-criterion: no unchecked criterion matched 'zeta' on #7\n", [])


def test_main_ticks_the_box_and_patches_the_stripped_body_through_gh_api_reading_either_route_with_tick_criterion_run_beside_it(monkeypatch, capsys, tick_issue_criterion):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    real_run = subprocess.run
    body = "- [ ] alpha\n- [ ] beta\n\n\n"

    def run_case(argv, view_ok):
        calls = []
        patched = []

        def fake_run(args, **kwargs):
            args = [str(arg) for arg in args]
            if args[:3] == ["gh", "issue", "view"]:
                calls.append(("view", args[3]))
                if view_ok:
                    return subprocess.CompletedProcess(args, 0, body, "")
                return subprocess.CompletedProcess(args, 1, "", "")
            if args[:4] == ["gh", "api", "-X", "PATCH"]:
                assert args[5] == "-F" and args[6].startswith("body=@")
                patched.append(args[6][len("body=@"):])
                with open(patched[-1]) as f:
                    calls.append(("patch", args[4], f.read()))
                return subprocess.CompletedProcess(args, 0, "", "")
            if args[:2] == ["gh", "api"] and len(args) == 3:
                calls.append(("api", args[2]))
                return subprocess.CompletedProcess(args, 0, json.dumps({"body": body}), "")
            if args[0] == "gh":
                raise AssertionError("unexpected gh call: %r" % (args,))
            calls.append(("tick", os.path.realpath(args[0]), kwargs.get("input")))
            return real_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = tick_issue_criterion.main(argv)
        return code, capsys.readouterr().out, calls, [p for p in patched if os.path.exists(p)]

    tick = os.path.realpath(SCRIPTS / "tick-criterion.sh")
    fed = body.rstrip("\n")
    assert run_case(["7", "alpha"], True) == (0, "", [
        ("view", "7"), ("tick", tick, fed),
        ("patch", "repos/{owner}/{repo}/issues/7", "- [x] alpha\n- [ ] beta")], [])
    assert run_case(["7", "alpha"], False) == (0, "", [
        ("view", "7"), ("api", "repos/{owner}/{repo}/issues/7"), ("tick", tick, fed),
        ("patch", "repos/{owner}/{repo}/issues/7", "- [x] alpha\n- [ ] beta")], [])
    assert run_case(["7"], True) == (0, "", [
        ("view", "7"), ("tick", tick, fed),
        ("patch", "repos/{owner}/{repo}/issues/7", "- [x] alpha\n- [ ] beta")], [])
    assert run_case(["abc", "alpha", "extra"], True) == (0, "", [
        ("view", "abc"), ("tick", tick, fed),
        ("patch", "repos/{owner}/{repo}/issues/abc", "- [x] alpha\n- [ ] beta")], [])


def test_main_keeps_every_failure_path_inside_0_to_3_and_lets_an_uncaught_exception_propagate(monkeypatch, capsys, tick_issue_criterion):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    real_run = subprocess.run

    def run_case(argv, view=(0, "- [ ] alpha\n"), api=(0, json.dumps({"body": "- [ ] alpha"})), patch=0, tick=None):
        patches = []

        def fake_run(args, **kwargs):
            args = [str(arg) for arg in args]
            if args[:3] == ["gh", "issue", "view"]:
                return subprocess.CompletedProcess(args, view[0], view[1], "")
            if args[:4] == ["gh", "api", "-X", "PATCH"]:
                patches.append(args)
                return subprocess.CompletedProcess(args, patch, "", "")
            if args[:2] == ["gh", "api"] and len(args) == 3:
                return subprocess.CompletedProcess(args, api[0], api[1], "")
            if args[0] == "gh":
                raise AssertionError("unexpected gh call: %r" % (args,))
            if tick is not None:
                return subprocess.CompletedProcess(args, tick, "", "")
            return real_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = tick_issue_criterion.main(argv)
        captured = capsys.readouterr()
        return code, captured.out, captured.err, len(patches)

    assert run_case(["7", "alpha"], view=(1, ""), api=(1, "")) == (
        2, "", "json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n", 0)
    assert run_case(["7", "alpha"], view=(1, ""), api=(0, "")) == (
        2, "", "json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n", 0)
    assert run_case(["7", "alpha"], patch=1) == (2, "", "", 1)
    assert run_case(["7", "alpha"], tick=1) == (1, "", "", 0)
    assert run_case(["7", "alpha"], tick=2) == (2, "", "", 0)
    assert run_case(["7", "alpha"], tick=5) == (2, "", "", 0)
    assert run_case(["7", "alpha"], tick=-9) == (2, "", "", 0)
    assert run_case(["7", ""], view=(0, "- [x] alpha\n")) == (
        3, "", "tick-issue-criterion: no unchecked criterion matched '' on #7\n", 0)

    def explode(args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(subprocess, "run", explode)
    with pytest.raises(RuntimeError, match="boom"):
        tick_issue_criterion.main(["7", "alpha"])
