"""In-process cases for veri/stop_settle.py, the module stop-settle.sh is a shim over (PRD 038.5, #4388)."""
import importlib
import json
import os

import pytest

LEDGER = "# Plan for #12\n\n- [ ] one ⟦criterion 1⟧\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout, stderr)."""

    def __init__(self, answers=None, porcelain="", ledger=LEDGER, merging=False):
        self.answers, self.calls, self.porcelain, self.ledger = dict(answers or {}), [], porcelain, ledger
        self.merging = merging

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), answer in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return answer
        if base == "git" and args[:1] == ("status",):
            return 0, self.porcelain, ""
        if base == "git" and args[:2] == ("rev-parse", "--git-path"):
            return 0, ".git/" + args[2] + "\n", ""
        if base == "git" and args[:2] == ("rev-parse", "-q"):
            return (0, "abc1234\n", "") if self.merging else (1, "", "")
        if base == "git" and args[:1] == ("show",):
            return (0, self.ledger, "") if self.ledger is not None else (128, "", "fatal: no such path\n")
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def stop(monkeypatch, run_cli, tmp_path):
    """stop(answers=None, fake=None, argv=None, preflight=True) runs stop-settle for issue 12 from the main tree, the
    run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    stop_settle = importlib.import_module("veri.stop_settle")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, argv=None, preflight=True):
        if preflight:
            (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(stop_settle, list(argv if argv is not None else ("12", "at-ledger")),
                                 cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


@pytest.mark.parametrize("argv", [(), ("12",), ("x", "now"), ("12", "later"), ("12", "now", "--force"),
                                  ("12", "now", "--drop", "--drop")])
def test_4388_bad_arguments_print_the_usage_and_exit_2_with_no_call(stop, argv):
    code, out, err, fake = stop(argv=argv)

    assert (code, "stop-settle.sh <n> <mode> [--drop]" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.stop_settle").__file__)
    assert os.path.exists(os.path.join(here, "..", "stop-settle.sh"))


def test_4388_a_missing_preflight_file_is_exit_2_before_any_call_named_on_stderr(stop):
    code, out, err, fake = stop(preflight=False)

    assert (code, fake.calls) == (2, [])
    assert ".tdd/issue-12-preflight" in err


def _seq(fake):
    return [(c[0],) + c[1] for c in fake.calls]


def test_4388_on_a_clean_tree_it_settles_resets_pushes_marks_comments_and_clears_in_order(stop):
    code, out, err, fake = stop(argv=("12", "now"))

    assert code == 0, err
    assert _seq(fake) == [
        ("git", "rev-parse", "--git-path", "rebase-merge"), ("git", "rev-parse", "--git-path", "rebase-apply"),
        ("git", "rev-parse", "-q", "--verify", "MERGE_HEAD"), ("git", "status", "--porcelain"),
        ("git", "reset", "--hard", "HEAD"), ("push-branch.sh",), ("git", "show", "HEAD:.tdd/issue-12.md"),
        ("event.sh", "stop", "mode=now", "at=planned"), ("comment.sh", "12", "stopped"),
        ("stop-requested.sh", "--clear")]
    mark = fake.call("event.sh")
    assert (mark[3]["VERI_ISSUE"], mark[3]["VERI_ACTOR"], mark[3]["VERI_STEP"]) == ("12", "conductor",
                                                                                   "one ⟦criterion 1⟧")
    assert {c[2] for c in fake.calls} == {str(stop.wt)}


def _leaves(stop, monkeypatch, live):
    """Seed .tdd/<name>.pid files, pid 100 + i each; <live> the names whose process still runs supervise.sh <name>."""
    names = ["develop-red", "verdict-red", "conductor"]
    for i, name in enumerate(names):
        (stop.wt / ".tdd" / (name + ".pid")).write_text("%d\n" % (100 + i))
    pid_file = importlib.import_module("veri.pid_file")
    monkeypatch.setattr(pid_file, "supervising", lambda pid, name: name in live and pid == str(100 + names.index(name)))


@pytest.mark.parametrize("leaf", [0, 1, 2])
def test_4388_it_waits_on_each_leaf_still_supervised_before_the_tree_check_and_on_no_other(stop, monkeypatch, leaf):
    _leaves(stop, monkeypatch, live=("develop-red", "conductor"))
    code, out, err, fake = stop(answers={("wait-leaf.sh", None): (leaf, "", "")})

    assert code == 0, err
    assert _seq(fake)[:2] == [("wait-leaf.sh", "develop-red"), ("git", "rev-parse", "--git-path", "rebase-merge")]
    assert [c for c in fake.calls if c[0] == "wait-leaf.sh"] == [fake.calls[0]]


@pytest.mark.parametrize("ledger, at", [
    (None, "unplanned"), (LEDGER, "planned"),
    ("# Plan\n\n- [x] one ⟦criterion 1⟧ ⟂ refactor pending\n- [ ] two ⟦criterion 2⟧\n", "green"),
    ("# Plan\n\n- [x] one ⟦criterion 1⟧\n- [ ] two ⟦criterion 2⟧\n", "step-done")])
def test_4388_at_is_read_off_the_committed_ledger(stop, ledger, at):
    fake = Fake(ledger=ledger)
    code, out, err, fake = stop(fake=fake)

    assert code == 0, err
    assert fake.call("event.sh")[1] == ("stop", "mode=at-ledger", "at=" + at)


@pytest.mark.parametrize("where, finish", [("rebase-merge", "git rebase --continue"),
                                           ("rebase-apply", "git rebase --continue"),
                                           ("MERGE_HEAD", "git merge --abort")])
def test_4388_an_interrupted_rebase_or_merge_is_unsettled_and_neither_reset_nor_pushed(stop, where, finish):
    fake = Fake(ledger="# Plan\n\n- [x] one ⟦criterion 1⟧\n", merging=where == "MERGE_HEAD")
    if where != "MERGE_HEAD":
        (stop.wt / ".git" / where).mkdir(parents=True)
    code, out, err, fake = stop(fake=fake)

    assert code == 0, err
    names = [c[:2] for c in _seq(fake)]
    assert not {("git", "status"), ("git", "reset"), ("push-branch.sh",)} & set(names)
    assert fake.call("event.sh")[1] == ("stop", "mode=at-ledger", "at=unsettled")
    comment = fake.call("comment.sh")
    assert comment[1] == ("12", "stopped", "--note-file", ".tdd/stop-settle-note.md")
    assert finish in (stop.wt / ".tdd" / "stop-settle-note.md").read_text()


DIRTY = " M src/a.py\n?? src/b.py\n"


def test_4388_a_dirty_tree_without_drop_stops_at_2_tree_check_with_exit_1_before_any_reset(stop):
    code, out, err, fake = stop(fake=Fake(porcelain=DIRTY))

    assert (code, out.splitlines()[-1]) == (1, "stopped at 2 tree-check")
    assert _seq(fake)[-1] == ("git", "status", "--porcelain")


def test_4388_with_drop_a_dirty_tree_is_reset_and_what_was_dropped_is_named_in_the_comment(stop):
    code, out, err, fake = stop(fake=Fake(porcelain=DIRTY), argv=("12", "at-leaf", "--drop"))

    assert code == 0, err
    names = [c[:2] for c in _seq(fake)]
    assert names.index(("git", "status")) < names.index(("git", "reset")) < names.index(("push-branch.sh",))
    assert fake.call("comment.sh")[1] == ("12", "stopped", "--note-file", ".tdd/stop-settle-note.md")
    note = (stop.wt / ".tdd" / "stop-settle-note.md").read_text()
    assert "src/a.py" in note and "src/b.py" in note


@pytest.mark.parametrize("live", [True, False])
def test_4388_a_live_restart_pending_pid_makes_the_comment_the_restart_variant_and_it_relaunches_nothing(
        stop, monkeypatch, live):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/12#issuecomment-9")
    monkeypatch.setattr(importlib.import_module("metrics"), "rendered", lambda issue: (0, "### 📊 Metrics\n", ""))
    (stop.wt / ".git").mkdir()
    (stop.wt / ".git" / "HEAD").write_text("ref: refs/heads/tdd/12-x\n")
    (stop.wt / ".tdd" / "restart-pending").write_text("%d\n" % (os.getpid() if live else 2147483646))
    fake = Fake(porcelain=" M src/a.py\n")
    real = Fake.__call__

    def answer(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        if base == "event.sh":
            with open(os.path.join(cwd, ".tdd", "events.jsonl"), "a") as f:
                f.write(json.dumps({"event": args[0], **dict(a.split("=", 1) for a in args[1:])}) + "\n")
        if base == "comment.sh":
            monkeypatch.chdir(cwd)
            self.calls.append((base, args, cwd, env, kw))
            return comment.main(list(args)), "", ""
        return real(self, name, *args, cwd=cwd, env=env, **kw)
    monkeypatch.setattr(Fake, "__call__", answer)
    code, out, err, fake = stop(fake=fake, argv=("12", "at-ledger", "--drop"))

    assert code == 0, err
    body = posted[0]
    assert body.splitlines()[0] == "### ⏹️ Stopped — at-ledger"
    assert ("context growth" in body, "run-conductor.sh" in body, "operator" in body) == (live, not live, False)
    assert not {"run-conductor.sh", "restart-conductor.sh", "detach-leaf.sh", "supervise.sh"} & set(fake.names())


@pytest.mark.parametrize("pushed, said, sha", [
    (1, "push rejected (non-fast-forward): origin/tdd/12-x is at abc1234def\n", "abc1234def"),
    (2, "push-branch.sh: push failed after 4 attempts; the branch is not on the remote\n", "unknown")])
def test_4388_a_push_exit_1_or_2_is_carried_into_the_comment_and_it_goes_on_to_exit_0(stop, pushed, said, sha):
    code, out, err, fake = stop(answers={("push-branch.sh", None): (pushed, "", said)})

    assert code == 0, err
    assert fake.names()[-2:] == ["comment.sh", "stop-requested.sh"]
    assert fake.call("comment.sh")[1] == ("12", "stopped", "--note-file", ".tdd/stop-settle-note.md")
    assert "push=rejected sha=" + sha in (stop.wt / ".tdd" / "stop-settle-note.md").read_text().splitlines()


def test_4388_it_writes_no_bail_classifies_nothing_writes_no_metrics_file_commits_nothing_and_keeps_the_pid_file(stop):
    (stop.wt / ".tdd" / "conductor.pid").write_text("4242\nThu Nov 18 10:00:00 2026\n")
    code, out, err, fake = stop(fake=Fake(porcelain=DIRTY), argv=("12", "now", "--drop"))

    assert code == 0, err
    assert [c[1][0] for c in fake.calls if c[0] == "event.sh"] == ["stop"]
    assert "classify-bail.sh" not in fake.names()
    assert not [p for p in (stop.wt / ".tdd").iterdir() if "metrics" in p.name]
    assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] in (("commit",), ("add",))]
    assert (stop.wt / ".tdd" / "conductor.pid").read_text() == "4242\nThu Nov 18 10:00:00 2026\n"


def test_4388_it_prints_one_line_per_call_with_its_exit_code_and_never_a_leaf_or_suite_output_file(stop, monkeypatch):
    _leaves(stop, monkeypatch, live=("develop-red",))
    (stop.wt / ".tdd" / "develop-red.out").write_text("LEAF-OUT-MARKER\n")
    (stop.wt / ".tdd" / "test-runs").mkdir()
    (stop.wt / ".tdd" / "test-runs" / "run.txt").write_text("SUITE-OUT-MARKER\n")
    code, out, err, fake = stop(fake=Fake(ledger=LEDGER + "LEDGER-MARKER\n"))

    assert code == 0, err
    named = [line for line in out.splitlines() if " exit " in line]
    assert len(named) == len(fake.calls)
    assert [line.split(" ")[0] for line in named] == fake.names()
    assert all(line.rsplit(" exit ", 1)[1].isdigit() for line in named)
    assert not {"LEAF-OUT-MARKER", "SUITE-OUT-MARKER", "LEDGER-MARKER"} & (set(out.split()) | set(err.split()))
