"""In-process cases for veri/tick_issue_criterion.py, the module tick-issue-criterion.sh is a shim over."""
import importlib
import json
import os
import pathlib

import pytest

AC = "## Acceptance criteria\n\n"


@pytest.fixture
def tick_issue_criterion():
    return importlib.import_module("veri.tick_issue_criterion")


def test_main_returns_2_with_the_usage_line_and_no_subprocess_call_for_a_missing_or_empty_number(fake_processes, monkeypatch, capsys, tick_issue_criterion):
    fake = fake_processes.answers({})
    for argv in ([], [""]):
        code = tick_issue_criterion.main(argv)
        captured = capsys.readouterr()
        assert (code, captured.out, captured.err, fake.argvs) == (2, "", "usage: tick-issue-criterion.sh <issue-number> <matcher>\n", [])


def test_main_returns_3_with_no_patch_and_names_the_matcher_and_issue_when_no_unchecked_criterion_matches(fake_processes, monkeypatch, capsys, tick_issue_criterion, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    patches = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args[:3] == ["gh", "issue", "view"]:
            return (0, AC + "- [ ] alpha\n", "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            patches.append(args)
            return (0, "", "")
        if args[0] == "gh":
            raise AssertionError("unexpected gh call: %r" % (args,))
        raise AssertionError("unexpected process: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = tick_issue_criterion.main(["7", "zeta"])

    assert (code, capsys.readouterr().err, patches) == (3, "tick-issue-criterion: no unchecked criterion matched 'zeta' on #7\n", [])


def test_main_ticks_the_box_and_patches_the_stripped_body_through_gh_api_reading_either_route(fake_processes, monkeypatch, capsys, tick_issue_criterion):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    body = AC + "- [ ] alpha\n- [ ] beta\n\n\n"

    def run_case(argv, view_ok):
        calls = []
        patched = []

        def fake_run(line, **kwargs):
            args = fake.argvs[-1]
            args = [str(arg) for arg in args]
            if args[:3] == ["gh", "issue", "view"]:
                calls.append(("view", args[3]))
                if view_ok:
                    return (0, body, "")
                return (1, "", "")
            if args[:4] == ["gh", "api", "-X", "PATCH"]:
                assert args[5] == "-F" and args[6].startswith("body=@")
                patched.append(args[6][len("body=@"):])
                with open(patched[-1]) as f:
                    calls.append(("patch", args[4], f.read()))
                return (0, "", "")
            if args[:2] == ["gh", "api"] and len(args) == 3:
                calls.append(("api", args[2]))
                return (0, json.dumps({"body": body}), "")
            if args[0] == "gh":
                raise AssertionError("unexpected gh call: %r" % (args,))
            raise AssertionError("unexpected process: %r" % (args,))

        fake = fake_processes.answers({}, default=fake_run)
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


def test_main_keeps_every_failure_path_inside_0_to_3_and_lets_an_uncaught_exception_propagate(fake_processes, monkeypatch, capsys, tick_issue_criterion, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")

    def run_case(argv, view=(0, AC + "- [ ] alpha\n"), api=None, patch=0):
        if api is None:
            api = (0, json.dumps({"body": AC + "- [ ] alpha"}))
        patches = []

        def fake_run(line, **kwargs):
            args = fake.argvs[-1]
            args = [str(arg) for arg in args]
            if args[:3] == ["gh", "issue", "view"]:
                return (view[0], view[1], "")
            if args[:4] == ["gh", "api", "-X", "PATCH"]:
                patches.append(args)
                return (patch, "", "")
            if args[:2] == ["gh", "api"] and len(args) == 3:
                return (api[0], api[1], "")
            if args[0] == "gh":
                raise AssertionError("unexpected gh call: %r" % (args,))
            raise AssertionError("unexpected process: %r" % (args,))

        fake = fake_processes.answers({}, default=fake_run)
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

    fake_processes.answers({}, default=RuntimeError("boom"))
    with pytest.raises(RuntimeError, match="boom"):
        tick_issue_criterion.main(["7", "alpha"])


def test_main_gives_its_full_answer_when_every_process_start_but_gh_is_refused(fake_processes, monkeypatch, capsys, tick_issue_criterion, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")

    def run_case(matcher):
        patched = []

        def fake_run(line, **kwargs):
            args = fake.argvs[-1]
            args = [str(arg) for arg in args]
            if args[:3] == ["gh", "issue", "view"]:
                return (0, AC + "- [ ] alpha\n- [ ] beta\n", "")
            if args[:4] == ["gh", "api", "-X", "PATCH"]:
                with open(args[6][len("body=@"):]) as f:
                    patched.append(f.read())
                return (0, "", "")
            raise AssertionError("refused process start: %r" % (args,))

        fake = fake_processes.answers({}, default=fake_run)
        code = tick_issue_criterion.main(["7", matcher])
        captured = capsys.readouterr()
        return code, captured.out, captured.err, patched

    assert run_case("beta") == (0, "", "", [AC + "- [ ] alpha\n- [x] beta"])
    assert run_case("zeta") == (3, "", "tick-issue-criterion: no unchecked criterion matched 'zeta' on #7\n", [])


def test_main_returns_2_after_reaching_the_body_patch_when_graphql_is_refused_and_the_rest_read_answers_but_the_patch_fails_with_a_5xx(fake_processes, monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    refusal = "HTTP 403: GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)\n"
    calls = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args[:2] == ["gh", "issue"]:
            return (1, "", refusal)
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            calls.append("patch")
            return (1, "", "HTTP 502: Bad Gateway\n")
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"number": 7, "labels": [], "body": AC + "- [ ] the criterion\n\n## Blocked by\n\nNone\n"}), "")
        if args[0] == "gh":
            raise AssertionError("unexpected gh call: %r" % (args,))
        raise AssertionError("unexpected process: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code, out, _ = run_cli(tick_issue_criterion, ["7", "criterion"])

    assert (code, out, calls) == (2, "", ["patch"])


def _rest_only_gh(fake_processes, patch_status=0):
    calls = []
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        calls.append(args)
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": AC + "- [ ] alpha\n- [ ] beta\n"}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (patch_status, "", "")
        if args[:3] == ["gh", "issue", "view"]:
            return (0, AC + "- [ ] read over graphql\n", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)
    return calls, patched


def test_cli_ticks_over_rest_only_with_no_issue_view_call_when_veri_gh_driver_is_unset(fake_processes, monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    calls, patched = _rest_only_gh(fake_processes)

    result = run_cli(tick_issue_criterion, ["7", "beta"])

    assert [call for call in calls if call[:2] != ["gh", "api"]] == []
    assert (result, patched) == ((0, "", ""), [AC + "- [ ] alpha\n- [x] beta"])


def test_cli_ticks_with_the_same_gh_calls_exit_and_patched_body_when_gh_repo_is_set(fake_processes, monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    answers = []
    for repo in (None, "owner/name"):
        if repo is None:
            monkeypatch.delenv("GH_REPO", raising=False)
        else:
            monkeypatch.setenv("GH_REPO", repo)
        calls, patched = _rest_only_gh(fake_processes)
        answers.append((run_cli(tick_issue_criterion, ["7", "alpha"]), patched, [call[:5] for call in calls]))

    assert answers[0] == ((0, "", ""), [AC + "- [x] alpha\n- [ ] beta"], [
        ["gh", "api", "repos/{owner}/{repo}/issues/7"],
        ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]])
    assert answers[1] == answers[0]


@pytest.mark.parametrize("status", [1, 3, 5])
def test_cli_exits_2_with_nothing_on_stdout_when_the_body_patch_exits_with_status(fake_processes, monkeypatch, run_cli, tick_issue_criterion, status):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    calls, patched = _rest_only_gh(fake_processes, patch_status=status)

    code, out, _ = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (code, out, patched) == (2, "", [AC + "- [x] alpha\n- [ ] beta"])


def test_cli_1979_exits_3_and_patches_nothing_when_the_only_matching_unchecked_box_is_outside_acceptance_criteria(fake_processes, monkeypatch, run_cli, tick_issue_criterion, tmp_path):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Problem\n\n- [ ] alpha in the problem\n\n## Acceptance criteria\n\n- [ ] beta\n\n## Blocked by\n\n- [ ] alpha blocker\n"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"], cwd=tmp_path)

    assert (result, patched) == ((3, "", "tick-issue-criterion: no unchecked criterion matched 'alpha' on #7\n"), [])


def test_cli_1979_exits_3_and_patches_nothing_when_the_body_has_no_acceptance_criteria_heading_but_a_matching_unchecked_box_sits_elsewhere(fake_processes, monkeypatch, run_cli, tick_issue_criterion, tmp_path):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Problem\n\n- [ ] alpha in the problem\n\n## Blocked by\n\n- [ ] alpha blocker\n"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"], cwd=tmp_path)

    assert (result, patched) == ((3, "", "tick-issue-criterion: no unchecked criterion matched 'alpha' on #7\n"), [])


def test_cli_1979_ticks_only_the_matching_box_under_acceptance_criteria_and_leaves_the_one_under_problem_unchecked(fake_processes, monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Problem\n\n- [ ] alpha in the problem\n\n## Acceptance criteria\n\n- [ ] alpha criterion\n- [ ] beta\n"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (result, patched) == ((0, "", ""), [
        "## Problem\n\n- [ ] alpha in the problem\n\n## Acceptance criteria\n\n- [x] alpha criterion\n- [ ] beta"])


def test_1979_tick_criterion_script_and_module_no_longer_exist_in_the_scripts_directory():
    scripts = pathlib.Path(__file__).resolve().parents[3]
    assert [p for p in (scripts / "tick-criterion.sh", scripts / "veri" / "tick_criterion.py") if p.exists()] == []


def test_cli_1979_ticks_only_the_real_acceptance_criteria_box_and_leaves_the_one_after_a_fenced_heading_unchecked(fake_processes, monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Problem\n\n```\n## Acceptance criteria\n- [ ] alpha fenced\n```\n\n## Acceptance criteria\n\n- [ ] alpha real\n"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (result, patched) == ((0, "", ""), [
        "## Problem\n\n```\n## Acceptance criteria\n- [ ] alpha fenced\n```\n\n## Acceptance criteria\n\n- [x] alpha real"])


def test_cli_1979_ticks_only_the_real_acceptance_criteria_box_and_leaves_the_one_after_a_tilde_fenced_heading_unchecked(fake_processes, monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Problem\n\n~~~~md\n## Acceptance criteria\n- [ ] alpha fenced\n~~~~\n\n## Acceptance criteria\n\n- [ ] alpha real\n"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (result, patched) == ((0, "", ""), [
        "## Problem\n\n~~~~md\n## Acceptance criteria\n- [ ] alpha fenced\n~~~~\n\n## Acceptance criteria\n\n- [x] alpha real"])


def test_cli_1979_exits_3_and_patches_nothing_when_the_only_acceptance_criteria_line_sits_inside_a_fenced_code_block(fake_processes, monkeypatch, run_cli, tick_issue_criterion, tmp_path):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Problem\n\n```\n## Acceptance criteria\n- [ ] alpha fenced\n```\n"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"], cwd=tmp_path)

    assert (result, patched) == ((3, "", "tick-issue-criterion: no unchecked criterion matched 'alpha' on #7\n"), [])


def test_cli_1979_exits_3_and_patches_nothing_when_the_only_matching_box_sits_under_a_level_one_notes_heading_after_the_section(fake_processes, monkeypatch, run_cli, tick_issue_criterion, tmp_path):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Acceptance criteria\n\n- [ ] beta\n\n# Notes\n\n- [ ] alpha in the notes\n"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"], cwd=tmp_path)

    assert (result, patched) == ((3, "", "tick-issue-criterion: no unchecked criterion matched 'alpha' on #7\n"), [])


def test_cli_1979_ticks_the_matching_box_under_a_level_three_subheading_inside_acceptance_criteria(fake_processes, monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Acceptance criteria\n\n- [ ] beta\n\n### Edge cases\n\n- [ ] alpha under the subheading\n"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (result, patched) == ((0, "", ""), [
        "## Acceptance criteria\n\n- [ ] beta\n\n### Edge cases\n\n- [x] alpha under the subheading"])


def test_cli_1979_patches_back_the_whole_body_with_every_section_after_acceptance_criteria_unchanged_but_the_one_ticked_box(fake_processes, monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    tail = "\n\n## Blocked by\n\n- [ ] alpha blocker\n\n## Notes\n\nSome notes, with `code` and a [link](http://x).\n\n- [ ] alpha note"
    head = "## Problem\n\nWhy.\n\n## Acceptance criteria\n\n"
    body = head + "- [ ] alpha criterion\n- [ ] beta" + tail + "\n"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (result, patched) == ((0, "", ""), [head + "- [x] alpha criterion\n- [ ] beta" + tail])


def test_cli_2027_ticks_the_box_after_a_fenced_block_holding_a_hash_and_a_double_hash_line_inside_acceptance_criteria(fake_processes, monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Acceptance criteria\n\n```sh\n# shell comment\n## another\n```\n\n- [ ] alpha after fence\n"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (result, patched) == ((0, "", ""), [
        "## Acceptance criteria\n\n```sh\n# shell comment\n## another\n```\n\n- [x] alpha after fence"])


def test_cli_2027_ticks_the_box_after_a_tilde_fenced_and_an_indented_fenced_block_holding_hash_lines_inside_acceptance_criteria(fake_processes, monkeypatch, run_cli, tick_issue_criterion):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    body = "## Acceptance criteria\n\n~~~sh\n# tilde comment\n~~~\n\n   ```sh\n## indented\n   ```\n\n- [ ] alpha after fences\n"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        if args[:5] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/7"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    result = run_cli(tick_issue_criterion, ["7", "alpha"])

    assert (result[0], patched) == (0, [
        "## Acceptance criteria\n\n~~~sh\n# tilde comment\n~~~\n\n   ```sh\n## indented\n   ```\n\n- [x] alpha after fences"])


def test_cli_2027_writes_a_run_log_event_naming_the_matcher_when_no_unchecked_criterion_matched(fake_processes, monkeypatch, run_cli, tick_issue_criterion, tmp_path):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    (tmp_path / ".git").mkdir()
    body = AC + "- [ ] alpha\n"

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code, _, _ = run_cli(tick_issue_criterion, ["7", "zeta-matcher"], cwd=tmp_path)

    log = tmp_path / ".tdd" / "events.jsonl"
    lines = log.read_text().splitlines() if log.exists() else []
    events = [json.loads(line) for line in lines if "zeta-matcher" in line]
    assert (code, [(e["event"], e["matcher"]) for e in events]) == (3, [("criterion-unticked", "zeta-matcher")])


def test_cli_2027_criterion_unticked_event_carries_the_issue_number_when_veri_issue_is_unset(fake_processes, monkeypatch, run_cli, tick_issue_criterion, tmp_path):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    monkeypatch.delenv("VERI_ISSUE", raising=False)
    (tmp_path / ".git").mkdir()
    body = AC + "- [ ] alpha\n"

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/7"]:
            return (0, json.dumps({"body": body}), "")
        raise AssertionError("unexpected command: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code, _, _ = run_cli(tick_issue_criterion, ["7", "zeta-matcher"], cwd=tmp_path)

    lines = (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()
    events = [json.loads(line) for line in lines if "zeta-matcher" in line]
    assert (code, [(e["event"], e["issue"]) for e in events]) == (3, [("criterion-unticked", "7")])


def test_main_2630_ticks_under_the_last_of_two_acceptance_criteria_headings_and_exits_3_for_a_matcher_held_only_above(fake_processes, monkeypatch, capsys, tick_issue_criterion, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    body = AC + "- [ ] superseded one\n- [ ] superseded two\n\n" + AC + "- [ ] replacement one\n- [ ] replacement two\n"

    def run_case(matcher):
        patched = []

        def fake_run(line, **kwargs):
            args = fake.argvs[-1]
            args = [str(arg) for arg in args]
            if args[:3] == ["gh", "issue", "view"]:
                return (0, body, "")
            if args[:4] == ["gh", "api", "-X", "PATCH"]:
                with open(args[6][len("body=@"):]) as f:
                    patched.append(f.read())
                return (0, "", "")
            if args[0] == "gh":
                raise AssertionError("unexpected gh call: %r" % (args,))
            raise AssertionError("unexpected process: %r" % (args,))

        fake = fake_processes.answers({}, default=fake_run)
        code = tick_issue_criterion.main(["7", matcher])
        capsys.readouterr()
        return code, patched

    assert run_case("replacement two") == (0, [
        AC + "- [ ] superseded one\n- [ ] superseded two\n\n" + AC + "- [ ] replacement one\n- [x] replacement two"])
    assert run_case("superseded two") == (3, [])


def test_main_2630_ticks_a_three_line_wrapped_criterion_by_a_matcher_in_its_second_line_and_rewrites_only_the_checkbox_line(fake_processes, monkeypatch, capsys, tick_issue_criterion, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    before = AC + "- [ ] first criterion\n- [ ] wrapped criterion starts here\n  and carries the wrap-matcher here\n  and ends on the third line\n- [ ] last criterion"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args[:3] == ["gh", "issue", "view"]:
            return (0, before, "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        if args[0] == "gh":
            raise AssertionError("unexpected gh call: %r" % (args,))
        raise AssertionError("unexpected process: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = tick_issue_criterion.main(["7", "wrap-matcher"])
    capsys.readouterr()

    assert (code, patched) == (0, [before.replace("- [ ] wrapped", "- [x] wrapped")])


def test_main_2630_exits_3_and_patches_nothing_when_the_only_criterion_holding_the_matcher_is_already_ticked(fake_processes, monkeypatch, capsys, tick_issue_criterion, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    body = AC + "- [ ] first criterion\n- [x] done-matcher criterion\n- [ ] last criterion"
    patched = []

    def fake_run(line, **kwargs):
        args = fake.argvs[-1]
        args = [str(arg) for arg in args]
        if args[:3] == ["gh", "issue", "view"]:
            return (0, body, "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            with open(args[6][len("body=@"):]) as f:
                patched.append(f.read())
            return (0, "", "")
        if args[0] == "gh":
            raise AssertionError("unexpected gh call: %r" % (args,))
        raise AssertionError("unexpected process: %r" % (args,))

    fake = fake_processes.answers({}, default=fake_run)

    code = tick_issue_criterion.main(["7", "done-matcher"])
    capsys.readouterr()

    assert (code, patched) == (3, [])
