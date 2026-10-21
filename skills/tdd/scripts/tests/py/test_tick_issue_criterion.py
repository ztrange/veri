"""In-process cases for veri/tick_issue_criterion.py, the module tick-issue-criterion.sh is a shim over."""
import importlib
import json
import os
import pathlib
import subprocess

import pytest

AC = "## Acceptance criteria\n\n"


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
            return subprocess.CompletedProcess(args, 0, AC + "- [ ] alpha\n", "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            patches.append(args)
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "gh":
            raise AssertionError("unexpected gh call: %r" % (args,))
        return real_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = tick_issue_criterion.main(["7", "zeta"])

    assert (code, capsys.readouterr().err, patches) == (3, "tick-issue-criterion: no unchecked criterion matched 'zeta' on #7\n", [])


def test_main_ticks_the_box_and_patches_the_stripped_body_through_gh_api_reading_either_route(monkeypatch, capsys, tick_issue_criterion):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    real_run = subprocess.run
    body = AC + "- [ ] alpha\n- [ ] beta\n\n\n"

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
            return real_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = tick_issue_criterion.main(argv)
        return code, capsys.readouterr().out, calls, [p for p in patched if os.path.exists(p)]

    assert run_case(["7", "alpha"], True) == (0, "", [
        ("view", "7"),
        ("patch", "repos/{owner}/{repo}/issues/7", AC + "- [x] alpha\n- [ ] beta")], [])
    assert run_case(["7", "alpha"], False) == (0, "", [
        ("view", "7"), ("api", "repos/{owner}/{repo}/issues/7"),
        ("patch", "repos/{owner}/{repo}/issues/7", AC + "- [x] alpha\n- [ ] beta")], [])
    assert run_case(["7"], True) == (0, "", [
        ("view", "7"),
        ("patch", "repos/{owner}/{repo}/issues/7", AC + "- [x] alpha\n- [ ] beta")], [])
    assert run_case(["abc", "alpha", "extra"], True) == (0, "", [
        ("view", "abc"),
        ("patch", "repos/{owner}/{repo}/issues/abc", AC + "- [x] alpha\n- [ ] beta")], [])


def test_main_keeps_every_failure_path_inside_0_to_3_and_lets_an_uncaught_exception_propagate(monkeypatch, capsys, tick_issue_criterion):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    real_run = subprocess.run

    def run_case(argv, view=(0, AC + "- [ ] alpha\n"), api=(0, json.dumps({"body": AC + "- [ ] alpha"})), patch=0):
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
    assert run_case(["7", ""], view=(0, AC + "- [x] alpha\n")) == (
        3, "", "tick-issue-criterion: no unchecked criterion matched '' on #7\n", 0)

    def explode(args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(subprocess, "run", explode)
    with pytest.raises(RuntimeError, match="boom"):
        tick_issue_criterion.main(["7", "alpha"])


def test_main_gives_its_full_answer_when_every_process_start_but_gh_is_refused(monkeypatch, capsys, tick_issue_criterion):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")

    def run_case(matcher):
        patched = []

        def fake_run(args, **kwargs):
            args = [str(arg) for arg in args]
            if args[:3] == ["gh", "issue", "view"]:
                return subprocess.CompletedProcess(args, 0, AC + "- [ ] alpha\n- [ ] beta\n", "")
            if args[:4] == ["gh", "api", "-X", "PATCH"]:
                with open(args[6][len("body=@"):]) as f:
                    patched.append(f.read())
                return subprocess.CompletedProcess(args, 0, "", "")
            raise AssertionError("refused process start: %r" % (args,))

        def refuse_popen(args, **kwargs):
            raise AssertionError("refused process start: %r" % (args,))

        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(subprocess, "Popen", refuse_popen)
        code = tick_issue_criterion.main(["7", matcher])
        captured = capsys.readouterr()
        return code, captured.out, captured.err, patched

    assert run_case("beta") == (0, "", "", [AC + "- [ ] alpha\n- [x] beta"])
    assert run_case("zeta") == (3, "", "tick-issue-criterion: no unchecked criterion matched 'zeta' on #7\n", [])


def test_main_returns_2_after_reaching_the_body_patch_when_graphql_is_refused_and_the_rest_read_answers_but_the_patch_fails_with_a_5xx(monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    real_run = subprocess.run
    refusal = "HTTP 403: GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)\n"
    calls = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:2] == ["gh", "issue"]:
            return subprocess.CompletedProcess(args, 1, "", refusal)
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            calls.append("patch")
            return subprocess.CompletedProcess(args, 1, "", "HTTP 502: Bad Gateway\n")
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"number": 7, "labels": [], "body": AC + "- [ ] the criterion\n\n## Blocked by\n\nNone\n"}), "")
        if args[0] == "gh":
            raise AssertionError("unexpected gh call: %r" % (args,))
        return real_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, _ = run_cli(tick_issue_criterion, ["7", "criterion"])

    assert (code, out, calls) == (2, "", ["patch"])


@pytest.mark.process("a symlink to the skill directory, and the tick-issue-criterion.sh shim run from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_directory_ticks_and_patches_the_same_body_as_in_place(tmp_path):
    scripts = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".."))
    stub = tmp_path / "stub"
    stub.mkdir()
    (stub / "gh").write_text(
        '#!/bin/sh\n'
        'if [ "$1" = "issue" ] && [ "$2" = "view" ]; then\n'
        '  printf \'%s\' "$FAKE_BODY"\n'
        'elif [ "$1" = "api" ]; then\n'
        '  for a in "$@"; do case "$a" in body=@*) cp "${a#body=@}" "$FAKE_OUT" ;; esac; done\n'
        'fi\n')
    (stub / "gh").chmod(0o755)
    (tmp_path / "linked-skill").symlink_to(os.path.dirname(scripts))
    (tmp_path / "elsewhere").mkdir()
    body = AC + "- [ ] alpha criterion\n- [ ] beta criterion"

    def run(script, cwd, out):
        env = dict(os.environ, VERI_GH_DRIVER="auto", FAKE_BODY=body, FAKE_OUT=str(out),
                   PATH=str(stub) + os.pathsep + os.environ["PATH"])
        done = subprocess.run([script, "7", "alpha"], cwd=cwd, env=env, capture_output=True, text=True)
        return done.returncode, done.stdout, done.stderr, out.read_text() if out.exists() else None

    in_place = run(os.path.join(scripts, "tick-issue-criterion.sh"), tmp_path, tmp_path / "in-place-edit")
    linked = run(str(tmp_path / "linked-skill" / "scripts" / "tick-issue-criterion.sh"),
                 tmp_path / "elsewhere", tmp_path / "linked-edit")

    assert in_place == (0, "", "", AC + "- [x] alpha criterion\n- [ ] beta criterion")
    assert linked == in_place


def _rest_only_gh(monkeypatch, patch_status=0):
    calls = []
    patched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        calls.append(args)
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"body": AC + "- [ ] alpha\n- [ ] beta\n"}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return subprocess.CompletedProcess(args, patch_status, "", "")
        if args[:3] == ["gh", "issue", "view"]:
            return subprocess.CompletedProcess(args, 0, AC + "- [ ] read over graphql\n", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls, patched


def test_cli_ticks_over_rest_only_with_no_issue_view_call_when_veri_gh_driver_is_unset(monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    calls, patched = _rest_only_gh(monkeypatch)

    result = run_cli(tick_issue_criterion, ["7", "beta"])

    assert [call for call in calls if call[:2] != ["gh", "api"]] == []
    assert (result, patched) == ((0, "", ""), [AC + "- [ ] alpha\n- [x] beta"])


def test_cli_ticks_with_the_same_gh_calls_exit_and_patched_body_when_gh_repo_is_set(monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    answers = []
    for repo in (None, "owner/name"):
        if repo is None:
            monkeypatch.delenv("GH_REPO", raising=False)
        else:
            monkeypatch.setenv("GH_REPO", repo)
        calls, patched = _rest_only_gh(monkeypatch)
        answers.append((run_cli(tick_issue_criterion, ["7", "alpha"]), patched, [call[:5] for call in calls]))

    assert answers[0] == ((0, "", ""), [AC + "- [x] alpha\n- [ ] beta"], [
        ["gh", "api", "repos/{owner}/{repo}/issues/7"],
        ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]])
    assert answers[1] == answers[0]


@pytest.mark.parametrize("status", [1, 3, 5])
def test_cli_exits_2_with_nothing_on_stdout_when_the_body_patch_exits_with_status(monkeypatch, run_cli, tick_issue_criterion, status):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    calls, patched = _rest_only_gh(monkeypatch, patch_status=status)

    code, out, _ = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (code, out, patched) == (2, "", [AC + "- [x] alpha\n- [ ] beta"])


def test_cli_1979_exits_3_and_patches_nothing_when_the_only_matching_unchecked_box_is_outside_acceptance_criteria(monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Problem\n\n- [ ] alpha in the problem\n\n## Acceptance criteria\n\n- [ ] beta\n\n## Blocked by\n\n- [ ] alpha blocker\n"
    patched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (result, patched) == ((3, "", "tick-issue-criterion: no unchecked criterion matched 'alpha' on #7\n"), [])


def test_cli_1979_exits_3_and_patches_nothing_when_the_body_has_no_acceptance_criteria_heading_but_a_matching_unchecked_box_sits_elsewhere(monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Problem\n\n- [ ] alpha in the problem\n\n## Blocked by\n\n- [ ] alpha blocker\n"
    patched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (result, patched) == ((3, "", "tick-issue-criterion: no unchecked criterion matched 'alpha' on #7\n"), [])


def test_cli_1979_ticks_only_the_matching_box_under_acceptance_criteria_and_leaves_the_one_under_problem_unchecked(monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Problem\n\n- [ ] alpha in the problem\n\n## Acceptance criteria\n\n- [ ] alpha criterion\n- [ ] beta\n"
    patched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (result, patched) == ((0, "", ""), [
        "## Problem\n\n- [ ] alpha in the problem\n\n## Acceptance criteria\n\n- [x] alpha criterion\n- [ ] beta"])


def test_1979_tick_criterion_script_and_module_no_longer_exist_in_the_scripts_directory():
    scripts = pathlib.Path(__file__).resolve().parents[2]
    assert [p for p in (scripts / "tick-criterion.sh", scripts / "veri" / "tick_criterion.py") if p.exists()] == []


def test_cli_1979_ticks_only_the_real_acceptance_criteria_box_and_leaves_the_one_after_a_fenced_heading_unchecked(monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Problem\n\n```\n## Acceptance criteria\n- [ ] alpha fenced\n```\n\n## Acceptance criteria\n\n- [ ] alpha real\n"
    patched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (result, patched) == ((0, "", ""), [
        "## Problem\n\n```\n## Acceptance criteria\n- [ ] alpha fenced\n```\n\n## Acceptance criteria\n\n- [x] alpha real"])
