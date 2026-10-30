"""In-process cases for veri/workqueue.py, the module workqueue.sh is a shim over."""
import importlib
import json
import os
import re
import subprocess
import sys
import time

import pytest

USAGE = """workqueue.sh: usage: workqueue.sh assign <worker> <issue>...
                     workqueue.sh next <worker>
                     workqueue.sh start <worker> <issue>
                     workqueue.sh done <worker> <issue> <merge-sha>
                     workqueue.sh park <worker> <issue> <reason>
                     workqueue.sh show [<worker>]
"""


@pytest.fixture(autouse=True)
def no_ambient_tunables(monkeypatch):
    for name in ("VERI_GH_JSON", "VERI_WORKQUEUE_LOCK_WAIT"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def workqueue():
    return importlib.import_module("veri.workqueue")


def fake_git(monkeypatch, main_tree, origin=None, gh_api=None):
    """subprocess.run answering `git worktree list` with <main_tree> and `git remote get-url origin` with <origin>, or no origin; `gh api` goes to <gh_api>(args) when given."""
    def fake_run(args, **kwargs):
        if gh_api is not None and list(args[:2]) == ["gh", "api"]:
            return gh_api(args)
        if list(args[:3]) == ["git", "worktree", "list"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\nHEAD abc\nbranch refs/heads/main\n\n" % main_tree, "")
        if list(args[:3]) == ["git", "remote", "get-url"]:
            if origin is not None:
                return subprocess.CompletedProcess(args, 0, origin + "\n", "")
            return subprocess.CompletedProcess(args, 2, "", "error: No such remote 'origin'\n")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_main_refuses_bad_arguments_with_2_and_the_usage_text_and_answers_next_with_nothing_launchable_as_3(tmp_path, monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    queue.write_bytes(b"alpha\t12\tqueued\t\n")
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text('[{"number": 12, "state": "OPEN", "body": ""}]')

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    assert run([]) == (2, "", "workqueue.sh: unknown subcommand: \n" + USAGE)
    assert run(["done", "alpha", "12"]) == (2, "", USAGE)
    assert run(["assign", "alpha", "12", "12"]) == (2, "", "workqueue.sh: issue 12 is named twice\n" + USAGE)
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))
    code, out, _ = run(["next", "beta"])
    assert (code, out) == (3, "")


def test_start_naming_no_queued_item_of_the_worker_returns_1_and_leaves_the_main_working_tree_queue_unchanged(tmp_path, monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    before = b"alpha\t12\tqueued\t\nalpha\t13\trunning\t\n"
    queue.write_bytes(before)

    code = workqueue.main(["start", "beta", "12"])
    _, err = capsys.readouterr()

    assert (code, err) == (1, "workqueue.sh: beta holds no queued item for issue 12\n")
    assert queue.read_bytes() == before


@pytest.mark.parametrize("answer", [
    subprocess.CompletedProcess([], 128, "", "fatal: not a git repository (or any of the parent directories): .git\n"),
    subprocess.CompletedProcess([], 0, "", ""),
], ids=["git-refused", "git-printed-nothing"])
def test_main_refuses_an_unknown_subcommand_with_2_and_writes_nothing_when_git_names_no_main_working_tree_and_ignores_extra_arguments(answer, tmp_path, monkeypatch, capsys, workqueue):
    def failing_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            if not kwargs.get("capture_output") and kwargs.get("stderr") is None:
                sys.stderr.write(answer.stderr)
            return subprocess.CompletedProcess(args, answer.returncode, answer.stdout, answer.stderr)
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", failing_run)
    monkeypatch.chdir(tmp_path)

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    assert run([]) == (2, "", "workqueue.sh: unknown subcommand: \n" + USAGE)
    assert run(["bogus"]) == (2, "", "workqueue.sh: unknown subcommand: bogus\n" + USAGE)
    assert run(["bogus", "next", "beta"]) == (2, "", "workqueue.sh: unknown subcommand: bogus\n" + USAGE)
    assert run(["alpha", "start", "12"]) == (2, "", "workqueue.sh: unknown subcommand: alpha\n" + USAGE)
    assert list(tmp_path.iterdir()) == []

    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    before = b"alpha\t12\tqueued\t\n"
    queue.write_bytes(before)
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))

    assert run(["start", "beta", "12", "extra"]) == (1, "", "workqueue.sh: beta holds no queued item for issue 12\n")
    assert run(["next", "beta", "extra"])[:2] == (3, "")
    assert queue.read_bytes() == before


def test_next_prints_the_workers_first_queued_item_with_no_open_blocker_reading_blockers_against_the_origin_slug(tmp_path, monkeypatch, capsys, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    before = (b"beta\t1\tqueued\t\nalpha\t2\trunning\t\nalpha\t012\tqueued\t\nalpha\t14\tqueued\t\n"
              b"alpha\t13\tqueued\t\nalpha\t99\tqueued\t\ngamma\t12\tqueued\t\n")
    queue.write_bytes(before)
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text(json.dumps([
        {"number": 1, "state": "OPEN", "body": ""},
        {"number": 2, "state": "OPEN", "body": ""},
        {"number": 5, "state": "open", "body": ""},
        {"number": 6, "state": "CLOSED", "body": ""},
        {"number": 7, "state": "Open", "body": None},
        {"number": 12, "state": "OPEN", "body": "Work.\n\n## Blocked by\n\n- #5\n- #6\n"},
        {"number": 14, "state": "OPEN", "body": "Work.\n\n## Blocked by\n\n- https://github.com/ztrange/veri/issues/7\n"},
        {"number": 13, "state": "OPEN", "body": "Work.\n\n## Blocked by\n\n- https://github.com/other/repo/issues/7\n- #6\n"},
    ]))
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    fake_git(monkeypatch, tmp_path, origin="https://github.com/ztrange/veri.git")
    assert run(["next", "alpha"]) == (0, "13\n", "")
    fake_git(monkeypatch, tmp_path, origin="git@github.com:ztrange/veri.git")
    assert run(["next", "alpha"]) == (0, "13\n", "")
    assert run(["next", "gamma"]) == (3, "", "")
    assert run(["next", "delta"]) == (3, "", "")
    fake_git(monkeypatch, tmp_path)
    assert run(["next", "alpha"]) == (0, "99\n", "")
    assert queue.read_bytes() == before


def test_next_reads_a_queue_line_of_three_tab_fields_and_a_queued_issue_whose_body_is_null(tmp_path, monkeypatch, capsys, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    before = b"alpha\t7\tqueued\n"
    queue.write_bytes(before)
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text(json.dumps([{"number": 7, "state": "OPEN", "body": None}]))
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))
    fake_git(monkeypatch, tmp_path)

    code = workqueue.main(["next", "alpha"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "7\n", "")
    assert queue.read_bytes() == before


def test_next_fetches_the_listing_first_from_the_fixture_or_gh_pages_returning_2_on_a_failed_page_and_dying_uncaught_on_a_bad_queue_or_listing(tmp_path, monkeypatch, capsys, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    queue.write_bytes(b"alpha\t12\tqueued\t\n")
    fixture = tmp_path / "gh"
    fixture.mkdir()
    listing = "repos/{owner}/{repo}/issues?state=all&per_page=100&page=%d"
    pages = {}
    requests = []

    def fake_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\n" % tmp_path, "")
        if list(args[:3]) == ["git", "remote", "get-url"]:
            return subprocess.CompletedProcess(args, 2, "", "error: No such remote 'origin'\n")
        if list(args[:2]) == ["gh", "api"]:
            requests.append(args[2])
            returncode, stdout, stderr = pages[args[2]]
            if kwargs.get("stderr") is None:
                sys.stderr.write(stderr)
            return subprocess.CompletedProcess(args, returncode, stdout, None)
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    def run(argv):
        requests.clear()
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    def dies(argv):
        requests.clear()
        with pytest.raises(Exception):
            workqueue.main(argv)
        capsys.readouterr()
        return list(requests)

    monkeypatch.setenv("VERI_GH_JSON", str(fixture))
    assert dies(["next", "alpha"]) == []
    (fixture / "issues.json").write_text("not json")
    assert dies(["next", "alpha"]) == []

    monkeypatch.delenv("VERI_GH_JSON")
    pages.update({listing % 1: (0, '[{"number": 12, "state": "OPEN", "body": ""}]\n', ""),
                  listing % 2: (0, "[]\n", "")})
    assert run(["next", "alpha"]) == (0, "12\n", "")
    assert requests == [listing % 1, listing % 2]

    pages[listing % 2] = (1, "", "gh: Server Error (HTTP 502)\n")
    assert run(["next", "alpha"]) == (2, "", "gh: Server Error (HTTP 502)\n")
    assert requests == [listing % 1, listing % 2]

    pages[listing % 2] = (0, "[]\n", "")
    assert dies(["next"]) == [listing % 1, listing % 2]
    for line in (b"alpha\t12\n", b"alpha\ttwelve\tqueued\t\n"):
        queue.write_bytes(line)
        assert dies(["next", "alpha"]) == [listing % 1, listing % 2]
    queue.unlink()
    assert dies(["next", "alpha"]) == [listing % 1, listing % 2]


def test_start_done_park_and_assign_take_the_lock_directory_polling_it_for_the_wait_times_20_reading_leading_zeros_as_decimal_and_release_it_on_every_path_issue_776(tmp_path, monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    lock = tmp_path / ".tdd" / "workqueue.lock"
    queue.parent.mkdir()
    before = b"alpha\t12\tqueued\t\nalpha\t13\trunning\t\n"
    queue.write_bytes(before)
    sleeps = []
    monkeypatch.setattr(time, "sleep", sleeps.append)

    def run(argv, wait=None):
        if wait is None:
            monkeypatch.delenv("VERI_WORKQUEUE_LOCK_WAIT", raising=False)
        else:
            monkeypatch.setenv("VERI_WORKQUEUE_LOCK_WAIT", wait)
        sleeps.clear()
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    lock.mkdir()
    held = (2, "", "workqueue.sh: could not take the lock %s\n" % lock)
    assert run(["start", "alpha", "12"], "1") == held
    assert sleeps == [0.05] * 20
    assert run(["done", "alpha", "13", "abc123"], "010") == held
    assert sleeps == [0.05] * 200
    assert run(["start", "alpha", "12"], "08") == held
    assert sleeps == [0.05] * 160
    assert run(["park", "alpha", "13", "flaky"]) == held
    assert sleeps == [0.05] * 600
    assert run(["assign", "beta", "14"], "2") == held
    assert sleeps == [0.05] * 40
    assert queue.read_bytes() == before
    assert lock.is_dir()

    for wait in ("abc", "0.5"):
        for argv in (["start", "alpha", "12"], ["done", "alpha", "13", "abc123"], ["park", "alpha", "13", "flaky"], ["assign", "beta", "14"]):
            code, out, err = run(argv, wait)
            assert (code, out) == (2, ""), (wait, argv, code, out, err)
            assert "VERI_WORKQUEUE_LOCK_WAIT" in err, (wait, argv, err)
            assert "unknown subcommand" not in err, (wait, argv, err)
            assert queue.read_bytes() == before
    assert lock.is_dir()

    lock.rmdir()
    queue.write_bytes(before)
    assert run(["start", "beta", "12"]) == (1, "", "workqueue.sh: beta holds no queued item for issue 12\n")
    assert not lock.exists()
    assert run(["assign", "beta", "14"]) == (0, "", "")
    assert queue.read_bytes() == before + b"beta\t14\tqueued\t\n"
    assert not lock.exists()
    assert sleeps == []


def test_start_done_park_rewrite_every_matching_line_in_place_as_four_tab_fields_and_rename_the_temp_file_with_mv(tmp_path, monkeypatch, capsys, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    tmp = tmp_path / ".tdd" / ("workqueue.tmp.%d" % os.getpid())
    queue.parent.mkdir()
    moves = []
    mv_status = [0]

    def fake_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\n" % tmp_path, "")
        if list(args[:1]) == ["mv"]:
            moves.append(list(args))
            if mv_status[0] == 0:
                os.replace(args[1], args[2])
            return subprocess.CompletedProcess(args, mv_status[0], "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    def run(argv):
        moves.clear()
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    queue.write_bytes(b"alpha\t12\tqueued\t\nbeta\t12\tqueued\t\nalpha\t12\tqueued\told\n\n"
                      b"alpha\t13\trunning\t\nalpha\t14\trunning\tx\ty\tz\nalpha\t15\tqueued\t")
    assert run(["start", "alpha", "12", "junk"]) == (0, "", "")
    assert moves == [["mv", str(tmp), str(queue)]]
    assert queue.read_bytes() == (b"alpha\t12\trunning\t\nbeta\t12\tqueued\t\nalpha\t12\trunning\t\n\t\t\t\n"
                                  b"alpha\t13\trunning\t\nalpha\t14\trunning\tx\ty\tz\nalpha\t15\tqueued\t\n")
    assert run(["done", "alpha", "13", "abc123"]) == (0, "", "")
    assert run(["park", "alpha", "14", "flaky ci"]) == (0, "", "")
    after = (b"alpha\t12\trunning\t\nbeta\t12\tqueued\t\nalpha\t12\trunning\t\n\t\t\t\n"
             b"alpha\t13\tmerged\tabc123\nalpha\t14\tparked\tflaky ci\nalpha\t15\tqueued\t\n")
    assert queue.read_bytes() == after
    assert not tmp.exists()

    assert run(["park", "beta", "12", "flaky"]) == (1, "", "workqueue.sh: beta holds no running item for issue 12\n")
    assert moves == []
    assert not tmp.exists()
    assert queue.read_bytes() == after

    for status, code in ((5, 2), (1, 1)):
        mv_status[0] = status
        assert run(["done", "alpha", "12", "def456"]) == (code, "", "")
        assert moves == [["mv", str(tmp), str(queue)]]
        assert queue.read_bytes() == after
        assert tmp.read_bytes() == after.replace(b"alpha\t12\trunning\t\n", b"alpha\t12\tmerged\tdef456\n")
        tmp.unlink()


def test_the_rewrite_reads_fields_as_bash_read_does_and_a_signalled_mv_returns_2(tmp_path, monkeypatch, capsys, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    tmp = tmp_path / ".tdd" / ("workqueue.tmp.%d" % os.getpid())
    queue.parent.mkdir()
    mv_status = [0]

    def fake_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\n" % tmp_path, "")
        if list(args[:1]) == ["mv"]:
            if mv_status[0] == 0:
                os.replace(args[1], args[2])
            return subprocess.CompletedProcess(args, mv_status[0], "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    queue.write_bytes(b"\talpha\t12\tqueued\tn\t\nalpha\t\t13\tqueued\tx\t\ty\t\nalpha\t14\tqueued\tc\rd\r\n")
    assert workqueue.main(["start", "alpha", "12"]) == 0
    assert queue.read_bytes() == b"alpha\t12\trunning\t\nalpha\t13\tqueued\tx\t\ty\nalpha\t14\tqueued\tc\rd\r\n"
    mv_status[0] = -15
    assert workqueue.main(["start", "alpha", "13"]) == 2
    assert tmp.read_bytes() == b"alpha\t12\trunning\t\nalpha\t13\trunning\t\nalpha\t14\tqueued\tc\rd\r\n"
    assert capsys.readouterr() == ("", "")


def test_start_done_park_refuse_a_tabbed_park_reason_before_the_lock_and_return_1_on_a_missing_argument_or_queue_file(tmp_path, monkeypatch, capsys, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    lock = tmp_path / ".tdd" / "workqueue.lock"
    tmp = tmp_path / ".tdd" / ("workqueue.tmp.%d" % os.getpid())
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    def fake_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\n" % tmp_path, "")
        if list(args[:1]) == ["mv"]:
            os.replace(args[1], args[2])
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    assert run(["start", "alpha", "12"])[:2] == (1, "")
    assert (tmp_path / ".tdd").is_dir()
    assert not queue.exists()
    assert not lock.exists()

    before = b"alpha\t12\tqueued\t\nalpha\t13\trunning\t\n"
    queue.write_bytes(before)
    lock.mkdir()
    refused = (2, "", "workqueue.sh: a park reason may not hold a tab or a newline\n" + USAGE)
    assert run(["park", "alpha", "13", "a\tb"]) == refused
    assert run(["park", "alpha", "13", "a\nb"]) == refused
    assert run(["park", "alpha", "13"])[:2] == (2, "")
    assert queue.read_bytes() == before
    assert not tmp.exists()
    lock.rmdir()

    assert run(["start"])[:2] == (2, "")
    assert not tmp.exists()
    assert run(["start", "alpha"])[:2] == (2, "")
    assert not tmp.exists()
    assert run(["start", "beta"]) == (2, "", USAGE)
    assert not tmp.exists()
    assert queue.read_bytes() == before
    assert not lock.exists()
    queue.write_bytes(b"")
    assert run(["start"]) == (2, "", USAGE)
    assert not tmp.exists()
    queue.write_bytes(before)

    assert run(["done", "alpha", "13", "a\tb\nc"]) == (0, "", "")
    assert queue.read_bytes() == b"alpha\t12\tqueued\t\nalpha\t13\tmerged\ta\tb\nc\n"
    queue.write_bytes(before)
    assert run(["start", "alpha", "12"]) == (0, "", "")
    assert run(["park", "alpha", "12", ""]) == (0, "", "")
    assert queue.read_bytes() == b"alpha\t12\tparked\t\nalpha\t13\trunning\t\n"
    assert not tmp.exists()
    assert not lock.exists()


def test_show_groups_items_by_worker_in_first_appearance_order_reading_the_worker_with_awks_backslash_escapes(tmp_path, monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    assert run(["show"])[:2] == (2, "")

    before = (b"alpha\t12\trunning\t\nbeta\t4\tqueued\t\nalpha\t7\tqueued\tx\n"
              b"a\\tb\t5\tqueued\t\na\\b\t6\tqueued\t\n")
    queue.write_bytes(before)
    grouped = "alpha\n\t12\trunning\n\t7\tqueued\nbeta\n\t4\tqueued\na\\tb\n\t5\tqueued\na\\b\n\t6\tqueued\n"
    assert run(["show"]) == (0, grouped, "")
    assert run(["show", ""]) == (0, grouped, "")
    assert run(["show", "alpha", "extra"]) == (0, "alpha\n\t12\trunning\n\t7\tqueued\n", "")
    assert run(["show", "delta"]) == (0, "", "")
    assert run(["show", "a\\tb"]) == (0, "", "")
    assert run(["show", "a\\\\b"]) == (0, "a\\b\n\t6\tqueued\n", "")
    assert queue.read_bytes() == before


def test_show_reads_short_lines_an_empty_queue_and_every_escape_as_macos_awk_does(tmp_path, monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    assert run(["show"]) == (2, "", "awk: can't open file %s\n source line number 1\n" % queue)

    queue.write_bytes(b"")
    assert run(["show"]) == (0, "", "")

    queue.write_bytes(b"alpha\n\nbeta\t4\n")
    assert run(["show"]) == (0, "alpha\n\t\t\n\n\t\t\nbeta\n\t4\t\n", "")

    queue.write_bytes(b"alpha\r\t3\tqueued\n")
    assert run(["show"]) == (0, "alpha\r\n\t3\tqueued\n", "")

    letters = "abfnrtvq"
    queue.write_bytes(b"".join(b"%s\t%d\tqueued\n" % (c.encode(), i) for i, c in enumerate(letters))
                      + b"AB\t20\tqueued\n\x08\t21\tqueued\n\x01\t22\tqueued\n")
    for letter in "afnrtv":
        assert run(["show", "\\" + letter]) == (0, "", ""), letter
    assert run(["show", "\\b"]) == (0, "\x08\n\t21\tqueued\n", "")
    assert run(["show", "\\q"]) == (0, "q\n\t7\tqueued\n", "")
    assert run(["show", "\\101B"]) == (0, "AB\n\t20\tqueued\n", "")
    assert run(["show", "\\8"]) == (0, "\x08\n\t21\tqueued\n", "")
    assert run(["show", "\\010"]) == (0, "\x08\n\t21\tqueued\n", "")
    assert run(["show", "\\401"]) == (0, "\x01\n\t22\tqueued\n", "")
    everything = run(["show"])
    assert run(["show", "\\0"]) == everything
    assert run(["show", "\\400"]) == everything


def test_assign_refuses_short_empty_repeated_or_held_issues_appends_one_queued_line_per_issue_unvalidated_and_fails_outside_a_repository(tmp_path, monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    lock = tmp_path / ".tdd" / "workqueue.lock"
    queue.parent.mkdir()
    before = b"alpha\t12\tqueued\t\nalpha\t13\trunning\t\nalpha\t14\tmerged\tabc\n\t15\tqueued\t\n"
    queue.write_bytes(before)
    monkeypatch.setenv("VERI_WORKQUEUE_LOCK_WAIT", "0")

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    assert run(["assign"]) == (2, "", USAGE)
    assert run(["assign", "beta"]) == (2, "", USAGE)
    assert queue.read_bytes() == before

    lock.mkdir()
    assert run(["assign", "beta", "16", ""]) == (2, "", "workqueue.sh: an issue argument is empty\n" + USAGE)
    assert run(["assign", "beta", "16", "16"]) == (2, "", "workqueue.sh: issue 16 is named twice\n" + USAGE)
    assert lock.is_dir()
    lock.rmdir()

    assert run(["assign", "beta", "16", "12"]) == (2, "", "workqueue.sh: issue 12 is already queued\n")
    assert run(["assign", "beta", "13"]) == (2, "", "workqueue.sh: issue 13 is already running\n")
    assert queue.read_bytes() == before
    assert not lock.exists()

    assert run(["assign", "beta", "012", "14", "15", "foo"]) == (0, "", "")
    assert run(["assign", "", "5"]) == (0, "", "")
    assert queue.read_bytes() == before + (b"beta\t012\tqueued\t\nbeta\t14\tqueued\t\nbeta\t15\tqueued\t\n"
                                           b"beta\tfoo\tqueued\t\n\t5\tqueued\t\n")
    queue.write_bytes(b"alpha\t12\tmerged\tabc")
    assert run(["assign", "beta", "7", "8"]) == (0, "", "")
    assert queue.read_bytes() == b"alpha\t12\tmerged\tabc\nbeta\t7\tqueued\t\nbeta\t8\tqueued\t\n"
    assert not lock.exists()
    queue.write_bytes(b"alpha\t12\tqueued\t")
    assert run(["assign", "beta", "12"]) == (0, "", "")
    assert queue.read_bytes() == b"alpha\t12\tqueued\t\nbeta\t12\tqueued\t\n"
    queue.write_bytes(b"alpha\t12\tqueued\r\n")
    assert run(["assign", "beta", "12"]) == (0, "", "")
    assert queue.read_bytes() == b"alpha\t12\tqueued\r\nbeta\t12\tqueued\t\n"
    queue.unlink()
    assert run(["assign", "beta", "7"]) == (0, "", "")
    assert queue.read_bytes() == b"beta\t7\tqueued\t\n"
    assert not lock.exists()

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / ".tdd").write_bytes(b"")
    fake_git(monkeypatch, outside)
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))
    code, out, err = run(["assign", "beta", "7"])
    assert (code, out, err.startswith("mkdir: %s/.tdd: " % outside)) == (1, "", True)
    code, out, err = run(["start", "beta", "7"])
    assert (code, out, err.startswith("mkdir: %s/.tdd: " % outside)) == (1, "", True)
    fake_git(monkeypatch, "")
    assert run(["show"])[:2] == (2, "")
    assert run(["next", "beta"])[:2] == (2, "")


def test_show_next_and_assign_with_an_empty_toplevel_exit_2_and_read_lock_and_write_nothing_under_the_filesystem_root_issue_898(tmp_path, monkeypatch, capsys, workqueue):
    root = tmp_path / "root"
    (root / ".tdd").mkdir(parents=True)
    planted = root / ".tdd" / "workqueue"
    planted.write_bytes(b"beta\t7\tqueued\t\n")
    touched = []

    def rooted(path):
        if isinstance(path, str) and path.startswith(os.sep + ".tdd"):
            touched.append(path)
            return str(root) + path
        return path

    real_open, real_mkdir, real_makedirs, real_rmdir, real_isfile = open, os.mkdir, os.makedirs, os.rmdir, os.path.isfile
    monkeypatch.setattr(workqueue, "open", lambda path, *a, **k: real_open(rooted(path), *a, **k), raising=False)
    monkeypatch.setattr(os, "mkdir", lambda path, *a, **k: real_mkdir(rooted(path), *a, **k))
    monkeypatch.setattr(os, "makedirs", lambda path, *a, **k: real_makedirs(rooted(path), *a, **k))
    monkeypatch.setattr(os, "rmdir", lambda path, *a, **k: real_rmdir(rooted(path), *a, **k))
    monkeypatch.setattr(os.path, "isfile", lambda path: real_isfile(rooted(path)))
    fake_git(monkeypatch, "")
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text('[{"number": 7, "state": "OPEN", "body": ""}]')
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    assert run(["show"])[:2] == (2, "")
    assert run(["next", "beta"])[:2] == (2, "")
    assert run(["assign", "beta", "8"])[:2] == (2, "")
    assert touched == []
    assert planted.read_bytes() == b"beta\t7\tqueued\t\n"
    assert sorted(p.name for p in (root / ".tdd").iterdir()) == ["workqueue"]


def test_the_outside_a_repository_part_of_the_assign_case_reads_and_writes_nothing_outside_tmp_path_whatever_exists_at_the_root_issue_898(tmp_path, monkeypatch, capsys, workqueue):
    root = tmp_path / "root"
    (root / ".tdd").mkdir(parents=True)
    planted = root / ".tdd" / "workqueue"
    planted.write_bytes(b"beta\t7\tqueued\t\n")
    touched = []

    def rooted(path):
        path = os.fspath(path)
        touched.append(path)
        return str(root) + path if path.startswith(os.sep + ".tdd") else path

    real_open, real_mkdir, real_makedirs, real_rmdir, real_remove, real_isfile = (
        open, os.mkdir, os.makedirs, os.rmdir, os.remove, os.path.isfile)
    monkeypatch.setattr(workqueue, "open", lambda path, *a, **k: real_open(rooted(path), *a, **k), raising=False)
    monkeypatch.setattr(os, "mkdir", lambda path, *a, **k: real_mkdir(rooted(path), *a, **k))
    monkeypatch.setattr(os, "makedirs", lambda path, *a, **k: real_makedirs(rooted(path), *a, **k))
    monkeypatch.setattr(os, "rmdir", lambda path, *a, **k: real_rmdir(rooted(path), *a, **k))
    monkeypatch.setattr(os, "remove", lambda path, *a, **k: real_remove(rooted(path), *a, **k))
    monkeypatch.setattr(os.path, "isfile", lambda path: real_isfile(rooted(path)))
    monkeypatch.setenv("VERI_WORKQUEUE_LOCK_WAIT", "0")

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / ".tdd").write_bytes(b"")
    fake_git(monkeypatch, outside)
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text('[{"number": 7, "state": "OPEN", "body": ""}]')
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))
    code, out, err = run(["assign", "beta", "7"])
    assert (code, out, err.startswith("mkdir: %s/.tdd: " % outside)) == (1, "", True)
    code, out, err = run(["start", "beta", "7"])
    assert (code, out, err.startswith("mkdir: %s/.tdd: " % outside)) == (1, "", True)
    fake_git(monkeypatch, "")
    assert run(["show"])[:2] == (2, "")
    assert run(["next", "beta"])[:2] == (2, "")
    assert [path for path in touched if not path.startswith(str(tmp_path) + "/")] == []
    assert planted.read_bytes() == b"beta\t7\tqueued\t\n"
    assert sorted(p.name for p in (root / ".tdd").iterdir()) == ["workqueue"]


def test_show_with_an_empty_toplevel_exits_2_with_empty_stdout_saying_it_is_outside_a_repository_issue_898(monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, "")
    code = workqueue.main(["show"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (2, "", "workqueue.sh: outside a repository\n")


def test_next_with_an_empty_toplevel_exits_2_with_empty_stdout_saying_it_is_outside_a_repository_issue_898(tmp_path, monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, "")
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text('[{"number": 7, "state": "OPEN", "body": ""}]')
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))
    code = workqueue.main(["next", "beta"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (2, "", "workqueue.sh: outside a repository\n")


def test_assign_with_an_empty_toplevel_exits_2_with_empty_stdout_saying_it_is_outside_a_repository_issue_898(monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, "")
    code = workqueue.main(["assign", "beta", "8"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (2, "", "workqueue.sh: outside a repository\n")


def test_start_done_and_park_with_an_empty_toplevel_exit_2_with_empty_stdout_saying_it_is_outside_a_repository_taking_no_lock_issue_898(monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, "")
    locks = []
    monkeypatch.setattr(workqueue, "take_lock", locks.append)
    answers = []
    for argv in (["start", "beta", "7"], ["done", "beta", "7", "abc1234"], ["park", "beta", "7", "stuck"]):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        answers.append((argv[0], code, out, err))
    assert answers == [(command, 2, "", "workqueue.sh: outside a repository\n") for command in ("start", "done", "park")]
    assert locks == []


def test_show_when_git_worktree_list_fails_with_no_output_exits_2_with_empty_stdout_saying_it_is_outside_a_repository_issue_898(monkeypatch, capsys, workqueue):
    def fake_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            return subprocess.CompletedProcess(args, 128, "", "fatal: not a git repository (or any of the parent directories): .git\n")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    code = workqueue.main(["show"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (2, "", "workqueue.sh: outside a repository\n")


def test_start_done_park_keep_a_last_queue_line_that_has_no_trailing_newline_issue_777(tmp_path, monkeypatch, capsys, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()

    def fake_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\n" % tmp_path, "")
        if list(args[:1]) == ["mv"]:
            os.replace(args[1], args[2])
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    queue.write_bytes(b"alpha\t13\trunning\t\nalpha\t12\tqueued\t")
    assert run(["start", "alpha", "12"]) == (0, "", "")
    assert queue.read_bytes().splitlines() == [b"alpha\t13\trunning\t", b"alpha\t12\trunning\t"]

    queue.write_bytes(b"alpha\t12\tqueued\t\nalpha\t13\trunning\t")
    assert run(["done", "alpha", "13", "abc123"]) == (0, "", "")
    assert queue.read_bytes().splitlines() == [b"alpha\t12\tqueued\t", b"alpha\t13\tmerged\tabc123"]

    queue.write_bytes(b"alpha\t13\trunning\t\nbeta\t14\tqueued\t")
    assert run(["park", "alpha", "13", "flaky"]) == (0, "", "")
    assert queue.read_bytes().splitlines() == [b"alpha\t13\tparked\tflaky", b"beta\t14\tqueued\t"]


def test_assign_keeps_a_last_queue_line_that_has_no_trailing_newline_issue_777(tmp_path, monkeypatch, capsys, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()

    def fake_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\n" % tmp_path, "")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)

    queue.write_bytes(b"alpha\t12\tqueued\t")
    assert workqueue.main(["assign", "alpha", "13", "14"]) == 0
    assert capsys.readouterr() == ("", "")
    assert queue.read_bytes().splitlines() == [b"alpha\t12\tqueued\t", b"alpha\t13\tqueued\t", b"alpha\t14\tqueued\t"]


def test_every_argument_refusal_through_the_cli_exits_2_with_its_usage_text_and_leaves_the_queue_byte_identical_creating_no_queue_file_or_temp_file(tmp_path, monkeypatch, run_cli, workqueue):
    refusals = [
        ([], "workqueue.sh: unknown subcommand: \n" + USAGE),
        (["bogus"], "workqueue.sh: unknown subcommand: bogus\n" + USAGE),
        (["assign"], USAGE),
        (["assign", "alpha"], USAGE),
        (["assign", "alpha", ""], "workqueue.sh: an issue argument is empty\n" + USAGE),
        (["assign", "alpha", "12", "12"], "workqueue.sh: issue 12 is named twice\n" + USAGE),
        (["start"], USAGE),
        (["start", "alpha"], USAGE),
        (["done", "alpha"], USAGE),
        (["done", "alpha", "12"], USAGE),
        (["done", "alpha", "12", ""], USAGE),
        (["park", "alpha"], USAGE),
        (["park", "alpha", "12"], USAGE),
        (["park", "alpha", "12", "a\tb"], "workqueue.sh: a park reason may not hold a tab or a newline\n" + USAGE),
        (["park", "alpha", "12", "a\nb"], "workqueue.sh: a park reason may not hold a tab or a newline\n" + USAGE),
    ]
    queued, bare = tmp_path / "queued", tmp_path / "bare"
    (queued / ".tdd").mkdir(parents=True)
    (bare / ".tdd").mkdir(parents=True)
    queue = queued / ".tdd" / "workqueue"
    before = b"alpha\t12\trunning\t\nbeta\t4\tqueued\t\n"
    queue.write_bytes(before)

    for tree in (queued, bare):
        fake_git(monkeypatch, tree)
        for argv, usage in refusals:
            assert run_cli(workqueue, argv) == (2, "", usage), argv

    assert queue.read_bytes() == before
    assert sorted(path.name for path in (queued / ".tdd").iterdir()) == ["workqueue"]
    assert list((bare / ".tdd").iterdir()) == []


def test_next_against_a_gh_that_serves_issues_over_three_pages_and_refuses_repositories_id_with_the_proxys_403_prints_the_same_issue_as_a_single_page(tmp_path, monkeypatch, run_cli, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    queue.write_bytes(b"alpha\t71\tqueued\t\nalpha\t73\tqueued\t\n")
    issues = [
        {"number": 70, "state": "closed", "body": ""},
        {"number": 71, "state": "open", "body": "Work.\n\n## Blocked by\n\n- #74\n"},
        {"number": 72, "state": "closed", "body": ""},
        {"number": 73, "state": "open", "body": "Work.\n\n## Blocked by\n\n- #72\n"},
        {"number": 74, "state": "open", "body": ""},
        {"number": 75, "state": "closed", "body": ""},
    ]
    proxy = "gh: Numeric-ID repository paths (repositories/{id}/...) are not supported through this proxy. (HTTP 403)\n"

    def serve(per_page):
        def gh_api(args):
            path = args[2]
            if "repositories/" in path:
                sys.stderr.write(proxy)
                return subprocess.CompletedProcess(args, 1, "", None)
            assert path.startswith("repos/{owner}/{repo}/issues"), path
            page = int(path.rsplit("page=", 1)[1])
            chunk = issues[(page - 1) * per_page:page * per_page]
            return subprocess.CompletedProcess(args, 0, json.dumps(chunk) + "\n", None)

        fake_git(monkeypatch, tmp_path, gh_api=gh_api)

    serve(len(issues))
    one = run_cli(workqueue, ["next", "alpha"])
    serve(2)
    three = run_cli(workqueue, ["next", "alpha"])
    assert one == (0, "73\n", "")
    assert three == one


def test_next_against_a_gh_that_refuses_graphql_with_the_403_and_answers_rest_a_page_at_a_time_prints_the_same_issue_stderr_and_exit_code_as_against_a_working_gh_across_more_than_one_page_of_issues(tmp_path, monkeypatch, run_cli, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    queue.write_bytes(b"alpha\t20\tqueued\t\nalpha\t22\tqueued\t\n")
    filler = [{"number": 100 + k, "state": "closed", "body": None} for k in range(110)]
    issues = filler + [
        {"number": 5, "state": "open", "body": None},
        {"number": 6, "state": "closed", "body": None},
        {"number": 20, "state": "open", "body": "Work.\n\n## Blocked by\n\n- #5\n"},
        {"number": 22, "state": "open", "body": "Work.\n\n## Blocked by\n\n- #6\n"},
    ]
    refusal = "HTTP 403: GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)\n"

    def serve(graphql):
        def gh_api(args):
            if args[2] == "graphql":
                assert graphql == "working"
                return subprocess.CompletedProcess(args, 0, "{}\n", None)
            page = int(args[2].rsplit("page=", 1)[1])
            return subprocess.CompletedProcess(args, 0, json.dumps(issues[(page - 1) * 100:page * 100]) + "\n", None)

        fake_git(monkeypatch, tmp_path, origin="https://github.com/ztrange/veri.git", gh_api=gh_api)
        fake = subprocess.run

        def routed(args, **kwargs):
            if list(args[:2]) not in (["gh", "issue"], ["gh", "pr"], ["gh", "repo"]):
                return fake(args, **kwargs)
            if graphql == "refused":
                sys.stderr.write(refusal)
                return subprocess.CompletedProcess(args, 1, "", None)
            return subprocess.CompletedProcess(args, 0, "[]\n", None)

        monkeypatch.setattr(subprocess, "run", routed)

    serve("working")
    working = run_cli(workqueue, ["next", "alpha"])
    serve("refused")
    refused = run_cli(workqueue, ["next", "alpha"])
    assert working == (0, "22\n", "")
    assert refused == working


def test_assign_through_the_cli_takes_an_issue_held_only_as_merged_parked_or_skipped(tmp_path, monkeypatch, run_cli, workqueue):
    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    before = b"beta\t4\tmerged\tabc1234\ngamma\t9\tparked\tsecond bail\nbeta\t11\tskipped\t\n"
    queue.write_bytes(before)

    assert run_cli(workqueue, ["assign", "alpha", "4", "9", "11"]) == (0, "", "")
    assert queue.read_bytes() == before + b"alpha\t4\tqueued\t\nalpha\t9\tqueued\t\nalpha\t11\tqueued\t\n"


def test_next_through_the_cli_reads_an_issues_document_over_256_kib_as_it_reads_a_small_one(tmp_path, monkeypatch, run_cli, workqueue):
    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    queue.write_bytes(b"alpha\t2\tqueued\t\nalpha\t3\tqueued\t\n")

    def fixture(name, pad):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "issues.json").write_text(json.dumps([
            {"number": n, "title": "issue %d" % n, "labels": [], "state": "OPEN",
             "body": "## What to build\n\n" + pad + "\n\n## Blocked by\n\n" + ("- #1\n" if n == 2 else "None.\n")}
            for n in range(1, 41)]))
        return directory

    short, long = fixture("short", "short"), fixture("long", "x" * 8192)
    assert (long / "issues.json").stat().st_size > 262144

    small = run_cli(workqueue, ["next", "alpha"], env={"VERI_GH_JSON": str(short)})
    large = run_cli(workqueue, ["next", "alpha"], env={"VERI_GH_JSON": str(long)})
    assert small == (0, "3\n", "")
    assert large == small


def queue_tree(tmp_path, fake_processes, mv_status=0):
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()

    def answer(line, **kwargs):
        if line.startswith("git worktree list"):
            return 0, "worktree %s\n" % tmp_path, ""
        if line.startswith("mv "):
            _, source, target = line.split(" ")
            if mv_status == 0:
                os.replace(source, target)
            return mv_status, "", ""
        raise AssertionError("unexpected command: %s" % line)

    fake_processes(answer)
    return queue


def test_start_done_and_park_through_the_cli_rewrite_only_that_workers_line_moving_it_to_running_merged_or_parked(tmp_path, fake_processes, run_cli, workqueue):
    queue = queue_tree(tmp_path, fake_processes)
    queue.write_bytes(b"alpha\t12\tparked\tsecond bail\nbeta\t4\tqueued\t\nbeta\t12\tqueued\t\nalpha\t12\tqueued\t\nalpha\t7\tqueued\t\n")
    assert run_cli(workqueue, ["start", "alpha", "12"]) == (0, "", "")
    assert queue.read_bytes() == b"alpha\t12\tparked\tsecond bail\nbeta\t4\tqueued\t\nbeta\t12\tqueued\t\nalpha\t12\trunning\t\nalpha\t7\tqueued\t\n"

    queue.write_bytes(b"beta\t4\trunning\t\nbeta\t12\trunning\t\nalpha\t12\trunning\t\nalpha\t7\tqueued\t\n")
    assert run_cli(workqueue, ["done", "alpha", "12", "abc1234"]) == (0, "", "")
    assert queue.read_bytes() == b"beta\t4\trunning\t\nbeta\t12\trunning\t\nalpha\t12\tmerged\tabc1234\nalpha\t7\tqueued\t\n"

    queue.write_bytes(b"beta\t4\trunning\t\nbeta\t12\trunning\t\nalpha\t12\trunning\t\nalpha\t7\tqueued\t\n")
    assert run_cli(workqueue, ["park", "alpha", "12", "second bail"]) == (0, "", "")
    assert queue.read_bytes() == b"beta\t4\trunning\t\nbeta\t12\trunning\t\nalpha\t12\tparked\tsecond bail\nalpha\t7\tqueued\t\n"


@pytest.mark.parametrize("argv, stderr", [
    (["start", "beta", "12"], "workqueue.sh: beta holds no queued item for issue 12\n"),
    (["done", "beta", "13", "abc1234"], "workqueue.sh: beta holds no running item for issue 13\n"),
    (["park", "beta", "13", "second bail"], "workqueue.sh: beta holds no running item for issue 13\n"),
    (["start", "alpha", "13"], "workqueue.sh: alpha holds no queued item for issue 13\n"),
    (["done", "alpha", "12", "abc1234"], "workqueue.sh: alpha holds no running item for issue 12\n"),
    (["park", "alpha", "12", "second bail"], "workqueue.sh: alpha holds no running item for issue 12\n"),
])
def test_start_done_and_park_through_the_cli_naming_another_workers_item_or_an_item_in_the_wrong_state_exit_1_and_leave_the_queue_byte_identical(argv, stderr, tmp_path, fake_processes, run_cli, workqueue):
    queue = queue_tree(tmp_path, fake_processes)
    before = b"alpha\t12\tqueued\t\nalpha\t13\trunning\t\n"
    queue.write_bytes(before)
    assert run_cli(workqueue, argv) == (1, "", stderr)
    assert queue.read_bytes() == before
    assert sorted(path.name for path in queue.parent.iterdir()) == ["workqueue"]


def test_after_assign_start_done_park_and_refused_calls_through_the_cli_every_issue_ever_assigned_is_still_a_line(tmp_path, fake_processes, run_cli, workqueue):
    queue = queue_tree(tmp_path, fake_processes)
    for call in ("assign alpha 12 7", "assign beta 30", "assign beta 12", "start alpha 12",
                 "start beta 7", "done alpha 12 abc1234", "start alpha 7", "done alpha 7",
                 "park alpha 7 why", "park alpha 30 why", "start beta 30", "frobnicate beta 30"):
        run_cli(workqueue, call.split(" "))
    held = {line.split("\t")[1] for line in queue.read_text().splitlines()}
    assert {"12", "7", "30"} <= held


def test_a_write_through_the_cli_that_cannot_take_the_lock_exits_2_without_touching_the_queue(tmp_path, fake_processes, run_cli, workqueue):
    queue = queue_tree(tmp_path, fake_processes)
    lock = tmp_path / ".tdd" / "workqueue.lock"
    before = b"alpha\t12\tqueued\t\n"
    queue.write_bytes(before)
    lock.mkdir()
    assert run_cli(workqueue, ["assign", "beta", "7"], env={"VERI_WORKQUEUE_LOCK_WAIT": "0"}) == (
        2, "", "workqueue.sh: could not take the lock %s\n" % lock)
    assert queue.read_bytes() == before
    assert lock.is_dir()


def test_a_failure_through_the_cli_after_the_lock_is_taken_exits_2_and_releases_the_lock(tmp_path, fake_processes, run_cli, workqueue):
    queue = queue_tree(tmp_path, fake_processes, mv_status=5)
    before = b"alpha\t12\tqueued\t\n"
    queue.write_bytes(before)
    assert run_cli(workqueue, ["start", "alpha", "12"])[0] == 2
    assert queue.read_bytes() == before
    assert not (tmp_path / ".tdd" / "workqueue.lock").exists()


@pytest.mark.process("parallel workqueue.sh processes writing one queue under a real git repository")
def test_assign_and_start_run_as_parallel_processes_leave_a_well_formed_queue_holding_every_write(tmp_path):
    script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "workqueue.sh")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    queue.write_text("".join("alpha\t%d\tqueued\t\n" % (100 + i) for i in range(1, 21)))
    writers = []
    for i in range(1, 21):
        for argv in (["assign", "w%d" % i, str(i)], ["start", "alpha", str(100 + i)]):
            writers.append(subprocess.Popen([script] + argv, cwd=tmp_path, stdin=subprocess.DEVNULL,
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    for writer in writers:
        writer.wait(timeout=25)
    lines = queue.read_text().split("\n")
    assert lines.pop() == ""
    torn = [line for line in lines if not re.fullmatch(r"[^\t]+\t[0-9]+\t(queued|running|merged|parked|skipped)\t[^\t]*", line)]
    assert torn == []
    want = {"w%d\t%d\tqueued\t" % (i, i) for i in range(1, 21)} | {"alpha\t%d\trunning\t" % (100 + i) for i in range(1, 21)}
    assert want - set(lines) == set()


def git_repo_with_queue(path):
    git = ["git", "-c", "user.name=veri", "-c", "user.email=veri@example.test"]
    subprocess.run(git + ["init", "-q", "-b", "main", str(path)], check=True)
    subprocess.run(git + ["-C", str(path), "commit", "-q", "--allow-empty", "-m", "initial"], check=True)
    (path / ".tdd").mkdir()
    (path / ".tdd" / "workqueue").write_bytes(b"beta\t4\tqueued\t\n")
    return path


@pytest.mark.process("a real linked git worktree whose `git worktree list` names the main working tree")
def test_called_from_a_linked_worktree_through_the_cli_assign_and_show_act_on_the_main_working_tree_queue(tmp_path, run_cli, workqueue):
    main = git_repo_with_queue(tmp_path / "main")
    linked = tmp_path / "linked"
    subprocess.run(["git", "-C", str(main), "worktree", "add", "-q", "-b", "side", str(linked)], check=True)

    assert run_cli(workqueue, ["assign", "alpha", "7"], cwd=str(linked)) == (0, "", "")
    assert run_cli(workqueue, ["show"], cwd=str(linked)) == (0, "beta\n\t4\tqueued\nalpha\n\t7\tqueued\n", "")
    assert (main / ".tdd" / "workqueue").read_bytes() == b"beta\t4\tqueued\t\nalpha\t7\tqueued\t\n"
    assert not (linked / ".tdd" / "workqueue").exists()


def test_show_through_the_cli_groups_every_item_by_worker_and_show_worker_prints_one_group_or_nothing_with_exit_0(tmp_path, fake_processes, run_cli, workqueue):
    queue = queue_tree(tmp_path, fake_processes)
    before = b"alpha\t12\trunning\t\nbeta\t4\tqueued\t\nalpha\t7\tqueued\t\n"
    queue.write_bytes(before)
    assert run_cli(workqueue, ["show"]) == (0, "alpha\n\t12\trunning\n\t7\tqueued\nbeta\n\t4\tqueued\n", "")
    assert run_cli(workqueue, ["show", "alpha"]) == (0, "alpha\n\t12\trunning\n\t7\tqueued\n", "")
    assert run_cli(workqueue, ["show", "beta"]) == (0, "beta\n\t4\tqueued\n", "")
    assert run_cli(workqueue, ["show", "gamma"]) == (0, "", "")
    assert queue.read_bytes() == before


SKILL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@pytest.mark.process("workqueue.sh run through a symlink to the skill directory from a subdirectory of a real linked git worktree")
def test_run_through_a_symlinked_skill_from_a_linked_worktree_subdirectory_assign_start_and_show_act_as_in_place_on_the_main_working_tree_queue(tmp_path):
    in_place, main, linked = git_repo_with_queue(tmp_path / "in-place"), git_repo_with_queue(tmp_path / "main"), tmp_path / "linked"
    subprocess.run(["git", "-C", str(main), "worktree", "add", "-q", "-b", "side", str(linked)], check=True)
    (linked / "sub" / "dir").mkdir(parents=True)
    (tmp_path / "skill-link").symlink_to(SKILL_DIR, target_is_directory=True)

    def sequence(script, cwd):
        out = []
        for argv in (["assign", "alpha", "7", "8"], ["start", "alpha", "7"], ["show"]):
            done = subprocess.run([script] + argv, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
            out.append((done.returncode, done.stdout, done.stderr))
        return out

    want = [(0, "", ""), (0, "", ""), (0, "beta\n\t4\tqueued\nalpha\n\t7\trunning\n\t8\tqueued\n", "")]
    assert sequence(os.path.join(SKILL_DIR, "scripts", "workqueue.sh"), in_place) == want
    assert sequence(str(tmp_path / "skill-link" / "scripts" / "workqueue.sh"), linked / "sub" / "dir") == want
    queue = b"beta\t4\tqueued\t\nalpha\t7\trunning\t\nalpha\t8\tqueued\t\n"
    assert (in_place / ".tdd" / "workqueue").read_bytes() == queue
    assert (main / ".tdd" / "workqueue").read_bytes() == queue
    assert not (linked / ".tdd" / "workqueue").exists()
    assert not (linked / "sub" / "dir" / ".tdd" / "workqueue").exists()
