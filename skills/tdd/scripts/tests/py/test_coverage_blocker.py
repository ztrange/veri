"""In-process cases for veri/coverage_blocker.py, the module coverage-blocker.sh is a shim over."""
import importlib
import json
import os
import pathlib
import subprocess
import tempfile

import pytest


@pytest.fixture
def coverage_blocker():
    return importlib.import_module("veri.coverage_blocker")


@pytest.fixture(autouse=True)
def default_driver(monkeypatch):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)


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
        if args[2].startswith("repos/{owner}/{repo}/issues?"):
            return subprocess.CompletedProcess(args, 0, "[]", "")
        if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
            return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
            return subprocess.CompletedProcess(args, 0, '{"body": "## Blocked by\\n\\nNone\\n"}', "")
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
        if args[2].startswith("repos/{owner}/{repo}/issues?"):
            calls.append("lookup")
            return subprocess.CompletedProcess(args, 0, "[]", "")
        if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
            calls.append("create")
            return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
            calls.append("view")
            return subprocess.CompletedProcess(args, 0, json.dumps({"body": "## Parent\n\n#1\n\n\n"}), "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            calls.append("patch")
            path = args[args.index("-F") + 1].split("body=@", 1)[1]
            seen["body"] = pathlib.Path(path).read_text()
            return subprocess.CompletedProcess(args, 5, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    coverage_blocker.main(["60"])

    assert calls == ["lookup", "create", "view", "patch"]
    assert seen["body"] == "## Parent\n\n#1\n"


def test_main_leaves_no_temp_file_when_the_patch_raises(tmpdir_env, monkeypatch, coverage_blocker):
    class PatchDied(Exception):
        pass

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[2].startswith("repos/{owner}/{repo}/issues?"):
            return subprocess.CompletedProcess(args, 0, "[]", "")
        if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
            return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
            return subprocess.CompletedProcess(args, 0, '{"body": "## Blocked by\\n\\nNone\\n"}', "")
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
        if args[2].startswith("repos/{owner}/{repo}/issues?"):
            return subprocess.CompletedProcess(args, 0, "[]", "")
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
            if args[2].startswith("repos/{owner}/{repo}/issues?"):
                return subprocess.CompletedProcess(args, 0, "[]", "")
            if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
                return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
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
        if args[2].startswith("repos/{owner}/{repo}/issues?"):
            return subprocess.CompletedProcess(args, 0, "[]", "")
        if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
            return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
            return subprocess.CompletedProcess(args, 0, '{"body": "## Blocked by\\n\\nNone\\n"}', "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = coverage_blocker.main(["60"])
    captured = capsys.readouterr()

    assert calls == [
        ["gh", "api", "repos/{owner}/{repo}/issues?state=open&per_page=100&page=1"],
        ["gh", "api", "repos/{owner}/{repo}/issues",
         "-f", "title=Cover the behaviour #60 refactors",
         "-f", "body=Refactor #60 refused: its Cover probe found the code it would move uncovered (`COVERED: no`). Find a seam and surround the behaviour with tests, then #60 can be retaken.",
         "-q", ".html_url"],
        ["gh", "api", "repos/{owner}/{repo}/issues/60"],
        ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/60", "-F", "body=@<file>"],
    ]
    assert seen["body"] == "## Blocked by\n\n- #77\n"
    assert (code, captured.out, captured.err) == (0, "https://github.com/owner/name/issues/77\n", "")


def test_main_rewrites_every_blocked_by_section_replacing_none_lines_and_inserting_after_the_last_blocker(tmpdir_env, monkeypatch, capsys, coverage_blocker):
    def run_with_body(body):
        seen = {}

        def fake_run(args, **kwargs):
            args = [str(arg) for arg in args]
            if args[2].startswith("repos/{owner}/{repo}/issues?"):
                return subprocess.CompletedProcess(args, 0, "[]", "")
            if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
                return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
            if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
                return subprocess.CompletedProcess(args, 0, json.dumps({"body": body}), "")
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
            if args[2].startswith("repos/{owner}/{repo}/issues?"):
                return subprocess.CompletedProcess(args, 0, "[]", "")
            if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
                err = "HTTP 422: Validation Failed\n" if create_code else ""
                stream = kwargs.get("stderr")
                if stream is None:
                    os.write(2, err.encode())
                    err = None
                elif stream != subprocess.PIPE:
                    err = None
                return subprocess.CompletedProcess(args, create_code, create_answer, err)
            if len(args) == 3 and args[2].startswith("repos/{owner}/{repo}/issues/"):
                return subprocess.CompletedProcess(args, 0, '{"body": "## Blocked by\\n\\nNone\\n"}', "")
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
    assert calls[1][:5] == ["gh", "api", "repos/{owner}/{repo}/issues", "-f", "title=Cover the behaviour #abc refactors"]
    assert calls[2] == ["gh", "api", "repos/{owner}/{repo}/issues/abc"]
    assert calls[3] == ["gh", "api", "-X", "PATCH", "repos/{owner}/{repo}/issues/abc"]
    assert not any("extra" in arg for call in calls for arg in call)

    code, out, err, body, calls = run(["60"], "", create_code=1)
    assert (code, out, body, len(calls)) == (2, "", None, 2)
    assert "HTTP 422: Validation Failed" in err


def test_main_reads_the_body_over_rest_when_the_view_fails_dropping_its_stderr_and_returns_2_with_the_json_error_when_both_fail(tmpdir_env, monkeypatch, capfd, coverage_blocker):
    def run(rest_code, rest_answer, rest_err):
        calls = []
        seen = {}

        def answer(args, kwargs, code, out, err):
            stream = kwargs.get("stderr")
            if stream is None:
                os.write(2, err.encode())
                err = None
            elif stream != subprocess.PIPE:
                err = None
            return subprocess.CompletedProcess(args, code, out, err)

        def fake_run(args, **kwargs):
            args = [str(arg) for arg in args]
            calls.append(args)
            if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
                return answer(args, kwargs, rest_code, rest_answer, rest_err)
            if args[2].startswith("repos/{owner}/{repo}/issues?"):
                return subprocess.CompletedProcess(args, 0, "[]", "")
            if args[:3] == ["gh", "api", "repos/{owner}/{repo}/issues"]:
                return answer(args, kwargs, 0, "https://github.com/owner/name/issues/77\n", "")
            if args[:4] == ["gh", "api", "-X", "PATCH"]:
                path = args[args.index("-F") + 1].split("body=@", 1)[1]
                seen["body"] = pathlib.Path(path).read_text()
                return answer(args, kwargs, 0, "", "")
            raise AssertionError("unexpected command: %r" % (args,))

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = coverage_blocker.main(["60"])
        captured = capfd.readouterr()
        return code, captured.out, captured.err, seen.get("body"), calls

    code, out, err, body, calls = run(0, '{"body": "## Blocked by\\n\\nNone\\n"}', "")
    assert (code, out, err, body) == (0, "https://github.com/owner/name/issues/77\n", "", "## Blocked by\n\n- #77\n")
    assert all(call[0] == "gh" and call[1:3] not in (["issue", "create"], ["issue", "edit"]) for call in calls)

    code, out, err, body, calls = run(1, "", "HTTP 404: Not Found (https://api.github.com/repos/owner/name/issues/60)\n")
    assert (code, out, body) == (2, "", None)
    assert calls[0] == ["gh", "api", "repos/{owner}/{repo}/issues?state=open&per_page=100&page=1"]
    assert not any(call[:4] == ["gh", "api", "-X", "PATCH"] for call in calls)
    assert "GraphQL: refused" not in err
    api_error = err.find("HTTP 404: Not Found")
    json_error = err.find("json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\n")
    assert 0 <= api_error < json_error
    assert all(call[0] == "gh" and call[1:3] not in (["issue", "create"], ["issue", "edit"]) for call in calls)


def test_main_rerun_after_a_first_run_that_filed_then_failed_files_no_second_issue_prints_the_first_url_and_blocks_on_it_777(tmpdir_env, monkeypatch, capsys, coverage_blocker):
    issues = {60: {"title": "Refactor something", "body": "## Blocked by\n\nNone\n", "state": "open"}}
    read_fails = {"on": True}
    seen = {}

    def url(number):
        return "https://github.com/owner/name/issues/%d" % number

    def listing():
        return [{"number": number, "title": issue["title"], "body": issue["body"], "state": issue["state"],
                 "url": url(number), "html_url": url(number)} for number, issue in sorted(issues.items())]

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] == ["gh", "issue", "list"]:
            return subprocess.CompletedProcess(args, 0, json.dumps(listing()), "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            path = args[args.index("-F") + 1].split("body=@", 1)[1]
            seen["body"] = pathlib.Path(path).read_text()
            issues[60]["body"] = seen["body"]
            return subprocess.CompletedProcess(args, 0, "{}", "")
        if args[:2] == ["gh", "api"] and args[2] == "repos/{owner}/{repo}/issues/60":
            if read_fails["on"]:
                return subprocess.CompletedProcess(args, 1, "", "HTTP 502: Bad Gateway\n")
            return subprocess.CompletedProcess(args, 0, json.dumps({"body": issues[60]["body"]}), "")
        if args[:2] == ["gh", "api"] and args[2].startswith("repos/{owner}/{repo}/issues"):
            fields = dict(arg.split("=", 1) for arg in args[3:] if "=" in arg)
            if "title" in fields:
                number = max(issues) + 1 if max(issues) >= 77 else 77
                issues[number] = {"title": fields["title"], "body": fields.get("body", ""), "state": "open"}
                return subprocess.CompletedProcess(args, 0, url(number) + "\n", "")
            if args[2].endswith("&page=1"):
                return subprocess.CompletedProcess(args, 0, json.dumps(listing()), "")
            return subprocess.CompletedProcess(args, 0, "[]", "")
        if args[:2] == ["gh", "api"] and args[2].startswith("search/issues"):
            return subprocess.CompletedProcess(args, 0, json.dumps({"items": listing()}), "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    first = coverage_blocker.main(["60"])
    capsys.readouterr()
    read_fails["on"] = False
    second = coverage_blocker.main(["60"])
    out = capsys.readouterr().out
    covers = [n for n, issue in issues.items() if issue["title"] == "Cover the behaviour #60 refactors"]

    assert first == 2
    assert (second, out, len(covers), seen.get("body")) == (
        0, "https://github.com/owner/name/issues/77\n", 1, "## Blocked by\n\n- #77\n")


def test_main_reads_the_body_over_rest_only_with_no_issue_view_call_when_veri_gh_driver_is_unset(tmpdir_env, monkeypatch, capsys, coverage_blocker):
    monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    calls = []
    seen = {}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        calls.append(args)
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
            return subprocess.CompletedProcess(args, 0, '{"body": "## Blocked by\\n\\nNone\\n"}', "")
        if args[:3] == ["gh", "issue", "view"]:
            return subprocess.CompletedProcess(args, 0, "## Read over GraphQL\n", "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            path = args[args.index("-F") + 1].split("body=@", 1)[1]
            seen["body"] = pathlib.Path(path).read_text()
            return subprocess.CompletedProcess(args, 0, "{}", "")
        if args[:2] == ["gh", "api"] and args[2].startswith("repos/{owner}/{repo}/issues"):
            if "-f" in args and any(arg.startswith("title=") for arg in args):
                return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
            return subprocess.CompletedProcess(args, 0, "[]", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = coverage_blocker.main(["60"])

    assert [call for call in calls if call[:3] == ["gh", "issue", "view"]] == []
    assert ["gh", "api", "repos/{owner}/{repo}/issues/60"] in calls
    assert (code, capsys.readouterr().out, seen.get("body")) == (
        0, "https://github.com/owner/name/issues/77\n", "## Blocked by\n\n- #77\n")


def test_main_falls_back_from_a_refused_issue_view_to_the_rest_read_and_patches_the_body_it_answers_under_veri_gh_driver_auto(tmpdir_env, monkeypatch, capsys, coverage_blocker):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    calls = []
    seen = {}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        calls.append(args)
        if args[:3] == ["gh", "issue", "view"]:
            return subprocess.CompletedProcess(args, 1, "", "GraphQL: refused\n")
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
            return subprocess.CompletedProcess(args, 0, '{"body": "## Blocked by\\n\\n- #12\\n"}', "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            path = args[args.index("-F") + 1].split("body=@", 1)[1]
            seen["body"] = pathlib.Path(path).read_text()
            return subprocess.CompletedProcess(args, 0, "{}", "")
        if args[:2] == ["gh", "api"] and args[2].startswith("repos/{owner}/{repo}/issues"):
            if any(arg.startswith("title=") for arg in args):
                return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
            return subprocess.CompletedProcess(args, 0, "[]", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = coverage_blocker.main(["60"])

    reads = [call for call in calls if call[:3] == ["gh", "issue", "view"] or call == ["gh", "api", "repos/{owner}/{repo}/issues/60"]]
    assert reads == [["gh", "issue", "view", "60", "--json", "body", "-q", ".body"], ["gh", "api", "repos/{owner}/{repo}/issues/60"]]
    assert (code, capsys.readouterr().out, seen.get("body")) == (
        0, "https://github.com/owner/name/issues/77\n", "## Blocked by\n\n- #12\n- #77\n")


def test_main_returns_2_with_no_patch_and_no_traceback_when_the_rest_read_exits_nonzero_with_a_json_error_body_and_no_body_key(tmpdir_env, monkeypatch, capfd, coverage_blocker):
    calls = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        calls.append(args)
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
            return subprocess.CompletedProcess(args, 1, '{"message":"Not Found"}', "gh: Not Found (HTTP 404)\n")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            return subprocess.CompletedProcess(args, 0, "{}", "")
        if args[:2] == ["gh", "api"] and args[2].startswith("repos/{owner}/{repo}/issues"):
            if any(arg.startswith("title=") for arg in args):
                return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/77\n", "")
            return subprocess.CompletedProcess(args, 0, "[]", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = coverage_blocker.main(["60"])

    captured = capfd.readouterr()
    assert [call for call in calls if call[:4] == ["gh", "api", "-X", "PATCH"]] == []
    assert (code, captured.out, "Traceback" in captured.err) == (2, "", False)


def test_main_pages_the_open_issue_lookup_until_an_empty_page_and_blocks_on_a_coverage_issue_found_on_page_2_without_creating_one(tmpdir_env, monkeypatch, capsys, coverage_blocker):
    lookup = "repos/{owner}/{repo}/issues?state=open&per_page=100&page="
    pages = {
        "1": [{"number": 70, "title": "Something else", "html_url": "https://github.com/owner/name/issues/70"}],
        "2": [{"number": 88, "title": "Cover the behaviour #60 refactors", "html_url": "https://github.com/owner/name/issues/88"}],
    }
    lookups = []
    creates = []
    seen = {}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:2] == ["gh", "api"] and args[2].startswith(lookup):
            page = args[2][len(lookup):]
            lookups.append(args)
            return subprocess.CompletedProcess(args, 0, json.dumps(pages.get(page, [])), "")
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
            return subprocess.CompletedProcess(args, 0, '{"body": "## Blocked by\\n\\nNone\\n"}', "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            path = args[args.index("-F") + 1].split("body=@", 1)[1]
            seen["body"] = pathlib.Path(path).read_text()
            return subprocess.CompletedProcess(args, 0, "{}", "")
        if any(arg.startswith("title=") for arg in args):
            creates.append(args)
            return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/99\n", "")
        return subprocess.CompletedProcess(args, 1, "", "unexpected\n")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = coverage_blocker.main(["60"])

    assert (lookups, creates) == ([
        ["gh", "api", lookup + "1"],
        ["gh", "api", lookup + "2"],
        ["gh", "api", lookup + "3"],
    ], [])
    assert (code, capsys.readouterr().out, seen.get("body")) == (
        0, "https://github.com/owner/name/issues/88\n", "## Blocked by\n\n- #88\n")


def test_main_files_the_issue_as_when_no_match_is_found_when_a_later_lookup_page_fails_ignoring_a_match_on_the_pages_before_it(tmpdir_env, monkeypatch, capsys, coverage_blocker):
    lookup = "repos/{owner}/{repo}/issues?state=open&per_page=100&page="
    page_1 = [{"number": 88, "title": "Cover the behaviour #60 refactors", "html_url": "https://github.com/owner/name/issues/88"}]
    lookups = []
    creates = []
    seen = {}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:2] == ["gh", "api"] and args[2].startswith(lookup):
            lookups.append(args)
            if args[2] == lookup + "1":
                return subprocess.CompletedProcess(args, 0, json.dumps(page_1), "")
            return subprocess.CompletedProcess(args, 1, "", "HTTP 502\n")
        if args == ["gh", "api", "repos/{owner}/{repo}/issues/60"]:
            return subprocess.CompletedProcess(args, 0, '{"body": "## Blocked by\\n\\nNone\\n"}', "")
        if args[:4] == ["gh", "api", "-X", "PATCH"]:
            path = args[args.index("-F") + 1].split("body=@", 1)[1]
            seen["body"] = pathlib.Path(path).read_text()
            return subprocess.CompletedProcess(args, 0, "{}", "")
        if any(arg.startswith("title=") for arg in args):
            creates.append(args)
            return subprocess.CompletedProcess(args, 0, "https://github.com/owner/name/issues/99\n", "")
        return subprocess.CompletedProcess(args, 1, "", "unexpected\n")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = coverage_blocker.main(["60"])

    assert (lookups, len(creates)) == ([["gh", "api", lookup + "1"], ["gh", "api", lookup + "2"]], 1)
    assert (code, capsys.readouterr().out, seen.get("body")) == (
        0, "https://github.com/owner/name/issues/99\n", "## Blocked by\n\n- #99\n")
