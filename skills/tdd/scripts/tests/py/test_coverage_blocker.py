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


def test_main_returns_2_with_the_usage_line_and_no_gh_call_for_a_missing_or_empty_number_and_2_when_the_create_fails(tmpdir_env, monkeypatch, capsys, coverage_blocker):
    def refuse(args, **kwargs):
        raise AssertionError("unexpected subprocess call: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", refuse)
    for argv in ([], [""]):
        code = coverage_blocker.main(argv)
        captured = capsys.readouterr()
        assert (code, captured.out, captured.err) == (2, "", "usage: coverage-blocker.sh <refactor-issue-number>\n")

    def fail_create(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
            return subprocess.CompletedProcess(args, 1, "", "HTTP 422: Validation Failed\n")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fail_create)
    code = coverage_blocker.main(["60"])
    assert (code, capsys.readouterr().out) == (2, "")


def test_main_falls_back_to_rest_when_graphql_refuses_the_read_and_patches_a_null_body_as_one_newline(tmpdir_env, monkeypatch, capsys, coverage_blocker):
    def run_with_rest_answer(rest_answer):
        seen = {}

        def fake_run(args, **kwargs):
            args = [str(arg) for arg in args]
            if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
                return subprocess.CompletedProcess(args, 0, rest_answer, "")
            if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
                return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
            if args == ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"]:
                return subprocess.CompletedProcess(args, 1, "", "GraphQL refused\n")
            if args[:4] == ["gh", "api", "-X", "PATCH"]:
                path = args[args.index("-F") + 1].split("body=@", 1)[1]
                seen["body"] = pathlib.Path(path).read_text()
                return subprocess.CompletedProcess(args, 0, "{}", "")
            raise AssertionError("unexpected command: %r" % (args,))

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = coverage_blocker.main(["60"])
        return code, seen.get("body"), capsys.readouterr().err

    assert run_with_rest_answer('{"body": "## Blocked by\\n\\nNone\\n"}') == (0, "## Blocked by\n\n- #77\n", "")
    assert run_with_rest_answer('{"body": null}') == (0, "\n", "")


def test_main_files_the_issue_blocks_the_refactor_issue_on_it_prints_the_url_and_returns_0(tmpdir_env, monkeypatch, capsys, coverage_blocker):
    calls = []
    seen = {}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            flag = args.index("-F") + 1
            seen["body"] = pathlib.Path(args[flag].split("body=@", 1)[1]).read_text()
            calls.append(args[:flag] + ["body=@<file>"] + args[flag + 1:])
            return subprocess.CompletedProcess(args, 0, "", "")
        calls.append(args)
        if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
            return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
        if args[:3] == ["gh", "issue", "view"]:
            return subprocess.CompletedProcess(args, 0, "## Blocked by\n\nNone\n", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = coverage_blocker.main(["60"])
    captured = capsys.readouterr()

    assert calls == [
        ["gh", "api", "repos/{owner}/{repo}/issues",
         "-f", "title=Cover the behaviour #60 refactors",
         "-f", "body=Refactor #60 refused: its Cover probe found the code it would move uncovered (`COVERED: no`). Find a seam and surround the behaviour with tests, then #60 can be retaken.",
         "-q", ".html_url"],
        ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"],
        ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/60", "-F", "body=@<file>"],
    ]
    assert seen["body"] == "## Blocked by\n\n- #77\n"
    assert (code, captured.out, captured.err) == (0, "https://github.com/owner/name/issues/77\n", "")


def test_main_rewrites_every_blocked_by_section_replacing_none_lines_and_inserting_after_the_last_blocker(tmpdir_env, monkeypatch, capsys, coverage_blocker):
    def run_with_body(body):
        seen = {}

        def fake_run(args, **kwargs):
            args = [str(arg) for arg in args]
            if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
                return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
            if args == ["gh", "issue", "view", "60", "--json", "body", "-q", ".body"]:
                return subprocess.CompletedProcess(args, 0, body, "")
            if args[:4] == ["gh", "api", "-X", "PATCH"]:
                path = args[args.index("-F") + 1].split("body=@", 1)[1]
                seen["body"] = pathlib.Path(path).read_bytes()
                return subprocess.CompletedProcess(args, 0, "", "")
            raise AssertionError("unexpected command: %r" % (args,))

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = coverage_blocker.main(["60"])
        return code, capsys.readouterr().out, seen.get("body")

    url = "https://github.com/owner/name/issues/77\n"
    assert run_with_body(
        "## Blocked by\n\n- #12\nNone yet\nNonetheless\n\n## Blocked byproduct\n\n- #13\n\n\n"
    ) == (0, url, b"## Blocked by\n\n- #12\n- #77\n- #77\n\n## Blocked byproduct\n\n- #13\n- #77\n")
    assert run_with_body("## Blocked by\r\n\r\n- #12\r\n") == (0, url, b"## Blocked by\r\n\r\n- #12\r\n- #77\n")
    assert run_with_body("## Parent\n\n#1\n\n\n") == (0, url, b"## Parent\n\n#1\n")


def test_main_blocks_on_whatever_the_create_answers_ignores_extra_arguments_and_passes_a_failed_create_stderr_through(tmpdir_env, monkeypatch, capfd, coverage_blocker):
    def run(argv, create_answer, create_code=0):
        calls = []
        seen = {}

        def fake_run(args, **kwargs):
            args = [str(arg) for arg in args]
            if args[:4] == ["gh", "api", "-X", "PATCH"]:
                path = args[args.index("-F") + 1].split("body=@", 1)[1]
                seen["body"] = pathlib.Path(path).read_text()
                calls.append(args[:5])
                return subprocess.CompletedProcess(args, 0, "", "")
            calls.append(args)
            if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
                err = "HTTP 422: Validation Failed\n" if create_code else ""
                stream = kwargs.get("stderr")
                if stream is None:
                    os.write(2, err.encode())
                    err = None
                elif stream != subprocess.PIPE:
                    err = None
                return subprocess.CompletedProcess(args, create_code, create_answer, err)
            if args[:3] == ["gh", "issue", "view"]:
                return subprocess.CompletedProcess(args, 0, "## Blocked by\n\nNone\n", "")
            raise AssertionError("unexpected command: %r" % (args,))

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = coverage_blocker.main(argv)
        captured = capfd.readouterr()
        return code, captured.out, captured.err, seen.get("body"), calls

    code, out, err, body, _ = run(["60"], "")
    assert (code, out, err, body) == (0, "\n", "", "## Blocked by\n\n- #\n")

    code, out, err, body, _ = run(["60"], "no-slash-here\n")
    assert (code, out, err, body) == (0, "no-slash-here\n", "", "## Blocked by\n\n- #no-slash-here\n")

    code, out, err, body, calls = run(["abc", "extra"], "https://github.com/owner/name/issues/77\n")
    assert (code, out, err, body) == (0, "https://github.com/owner/name/issues/77\n", "", "## Blocked by\n\n- #77\n")
    assert calls[0][:5] == ["gh", "api", "repos/{owner}/{repo}/issues", "-f", "title=Cover the behaviour #abc refactors"]
    assert calls[1] == ["gh", "issue", "view", "abc", "--json", "body", "-q", ".body"]
    assert calls[2] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/abc"]
    assert not any("extra" in arg for call in calls for arg in call)

    code, out, err, body, calls = run(["60"], "", create_code=1)
    assert (code, out, body, len(calls)) == (2, "", None, 1)
    assert "HTTP 422: Validation Failed" in err
