"""In-process cases for veri/pr_ready_wait.py, the module pr-ready-wait.sh is a shim over (PRD 027.10, #4032)."""
import importlib
import os

import pytest

URL = "https://github.com/o/r/pull/42"
HEAD = "a" * 40
PLAN = "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n"
TICKED = PLAN + "- [x] the full suite is green ⟦full-suite⟧ ⟦criterion 2⟧\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout) or (code, stdout, {redirected path: its text})."""

    def __init__(self, answers=None):
        self.answers, self.calls = dict(answers or {}), []

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), answer in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                for path, text in (answer[2] if len(answer) > 2 else {}).items():
                    with open(os.path.join(cwd, path), "w") as f:
                        f.write(text)
                return answer[0], answer[1], ""
        if base == "gh":
            return 0, URL + "\n", ""
        if base == "git" and args[:1] == ("branch",):
            return 0, "tdd/12-thing\n", ""
        if base == "git" and args[:1] == ("rev-parse",):
            return 0, HEAD + "\n", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def made(self, base):
        return [c for c in self.calls if c[0] == base]


@pytest.fixture
def ready(monkeypatch, run_cli, tmp_path):
    """ready(answers=None, fake=None, missing=(), argv=None, ledger=PLAN) runs pr-ready-wait for issue 12 from the main
    tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    pr_ready_wait = importlib.import_module("veri.pr_ready_wait")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), argv=None, ledger=None):
        if "preflight" not in missing:
            (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
        (wt / ".tdd" / "issue-12.md").write_text(PLAN if ledger is None else ledger)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(pr_ready_wait, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4032_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(ready):
    code, out, err, fake = ready(argv=())

    assert (code, "pr-ready-wait.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.pr_ready_wait").__file__)
    assert os.path.exists(os.path.join(here, "..", "pr-ready-wait.sh"))


def test_4032_a_missing_preflight_is_exit_2_before_any_inner_call_named_on_stderr(ready):
    code, out, err, fake = ready(missing=("preflight",))

    assert (code, fake.calls) == (2, [])
    assert ".tdd/issue-12-preflight" in err


def test_4032_a_stacked_run_is_refused_with_exit_2_before_any_inner_call(ready):
    (ready.wt / ".tdd" / "issue-12-base").write_text("tdd/11-below\n")
    code, out, err, fake = ready()

    assert (code, fake.calls) == (2, [])
    assert "stacked" in err and ".tdd/issue-12-base" in err


class Failing(Fake):
    """Fake, but the first call <hit> takes (base, args) to exits <code>."""

    def __init__(self, hit, code):
        super().__init__()
        self.hit, self.code = hit, code

    def __call__(self, name, *args, **kw):
        if self.hit(os.path.basename(name), args):
            self.hit = lambda *_: False
            self.calls.append((os.path.basename(name), args, kw.get("cwd"), kw.get("env"), kw))
            return self.code, "", "boom\n"
        return super().__call__(name, *args, **kw)


@pytest.mark.parametrize("hit, code", [
    (lambda b, a: b == "git" and a[:1] == ("branch",), 128), (lambda b, a: b == "gh", 1),
    (lambda b, a: b == "gh", 4), (lambda b, a: b == "git" and a[:1] == ("status",), 128),
    (lambda b, a: b == "git" and a[:1] == ("rev-parse",), 128)],
    ids=["git branch", "gh url read exit 1", "gh url read exit 4", "git status", "git rev-parse"])
def test_4032_a_git_or_gh_call_that_fails_is_no_answer_exit_2(ready, hit, code):
    out_code, out, err, fake = ready(fake=Failing(hit, code))

    assert (out_code, out.splitlines()[-1].startswith("stopped at 2 ")) == (2, True)
    assert "pr-ready.sh" not in fake.names()


def test_4032_the_wait_s_head_read_failing_is_no_answer_exit_2(ready):
    seen = []
    code, out, err, fake = ready(fake=Failing(lambda b, a: b == "git" and a[:1] == ("rev-parse",) and seen.append(1)
                                              is None and len(seen) == 2, 128))

    assert (code, fake.names()[-1], "wait-ci.sh" in fake.names()) == (2, "git", False)


def _flow(fake):
    return [(c[0], c[1]) for c in fake.calls if c[0] != "gh"]


def test_4032_it_reads_the_pr_url_readies_the_pr_waits_on_ci_and_settles_green(ready):
    code, out, err, fake = ready()

    assert (code, out.splitlines()[-3:]) == (0, ["pr_url=" + URL, "pr_number=42", "ci=green"])
    assert (ready.wt / ".tdd" / "issue-12-pr-ready-wait").read_text() == "pr_url=%s\npr_number=42\nci=green\n" % URL
    assert [c[1] for c in fake.made("gh")] == [("api", "repos/{owner}/{repo}/pulls?head={owner}:tdd/12-thing", "-q",
                                               ".[0].html_url // empty")]
    assert _flow(fake) == [("git", ("branch", "--show-current")), ("branch-suite.sh", ()),
                           ("event.sh", ("done", "pr=" + URL)), ("metrics.sh", ("12",)),
                           ("git", ("add", ".tdd/issue-12-metrics.md")),
                           ("git", ("commit", "-m", "metrics: what solving #12 cost (#12)")),
                           ("git", ("status", "--porcelain", "--untracked-files=all")), ("push-branch.sh", ()),
                           ("git", ("rev-parse", "HEAD")), ("pr-ready.sh", ("42", HEAD)),
                           ("git", ("rev-parse", "HEAD")), ("wait-ci.sh", (URL, "540", "", HEAD))]
    done = fake.made("event.sh")[0][3]
    assert (done["VERI_ISSUE"], done["VERI_ACTOR"]) == ("12", "conductor")
    assert fake.made("metrics.sh")[0][4]["out"] == ".tdd/issue-12-metrics.md"
    assert fake.made("pr-ready.sh")[0][4]["err"] == ".tdd/pr-ready.err"
    waited = fake.made("wait-ci.sh")[0][4]
    assert (waited["out"], waited["err"]) == (".tdd/wait-ci.out", ".tdd/wait-ci.err")
    assert all(c[2] == str(ready.wt) for c in fake.calls)


def test_4032_a_pr_with_no_checks_is_settled_with_no_checks_1(ready):
    code, out, err, fake = ready(answers={("wait-ci.sh", None): (0, "", {".tdd/wait-ci.err": "PR 42 has no checks\n"})})

    assert (code, out.splitlines()[-1]) == (0, "no_checks=1")


class Ticking(Fake):
    """Fake under `ci`: tick-ledger.sh exits 0 once, then 3."""

    def __init__(self, answers=None):
        super().__init__({("branch-suite.sh", None): (0, "ci\n"), **dict(answers or {})})
        self.ticks = 1

    def __call__(self, name, *args, **kw):
        if os.path.basename(name) == "tick-ledger.sh":
            self.calls.append(("tick-ledger.sh", args, kw.get("cwd"), kw.get("env"), kw))
            self.ticks -= 1
            return (0 if self.ticks >= 0 else 3), "", ""
        return super().__call__(name, *args, **kw)


def test_4332_a_has_no_checks_wait_after_the_pre_readying_ticks_still_settles_no_checks_1(ready):
    fake = Ticking({("wait-ci.sh", None): (0, "", {".tdd/wait-ci.err": "PR 42 has no checks\n"})})
    code, out, err, fake = ready(fake=fake, ledger=PLAN + "- [ ] the full suite is green ⟦full-suite⟧ ⟦criterion 2⟧\n")

    commits = [c[1][2] for c in fake.made("git") if c[1][:1] == ("commit",)]
    assert (code, out.splitlines()[-1], commits[0]) == (0, "no_checks=1", "plan: the full suite is owed to CI (#12)")
    assert fake.names().index("tick-ledger.sh") < fake.names().index("pr-ready.sh")


def test_4032_no_pr_for_the_branch_exits_2_before_readying(ready):
    code, out, err, fake = ready(answers={("gh", None): (0, "\n")})

    assert (code, out.splitlines()[-1]) == (2, "stopped at 2 no PR for tdd/12-thing")
    assert "pr-ready.sh" not in fake.names()


def test_4032_a_dirty_tree_just_before_readying_stops_it_with_exit_1(ready):
    code, out, err, fake = ready(answers={("git", "status"): (0, "?? stray.txt\n")})

    assert (code, out.splitlines()[-1]) == (1, "stopped at 2 tree-check")
    assert "pr-ready.sh" not in fake.names()


def test_4032_pr_ready_failing_stops_it_with_its_code_and_no_event_adjudication_or_wait(ready):
    code, out, err, fake = ready(answers={("pr-ready.sh", None): (2, "")})

    assert (code, out.splitlines()[-1]) == (2, "stopped at 2 pr-ready.sh 42 %s 2> .tdd/pr-ready.err exit 2" % HEAD)
    assert fake.names()[-1] == "pr-ready.sh"
    assert not (ready.wt / ".tdd" / "issue-12-pr-ready-wait").exists()


@pytest.mark.parametrize("inner", [1, 2])
def test_4032_a_red_or_unanswered_wait_stops_it_with_its_code_before_any_run_view_rebase_adjudication_or_step(
        ready, inner):
    code, out, err, fake = ready(answers={("wait-ci.sh", None): (inner, "test\n")})

    assert (code, out.splitlines()[-1]) == (inner, "stopped at 2 wait-ci.sh %s 540  %s > .tdd/wait-ci.out 2> "
                                            ".tdd/wait-ci.err exit %d" % (URL, HEAD, inner))
    assert fake.names()[-1] == "wait-ci.sh" and len(fake.made("gh")) == 1
    assert not (ready.wt / ".tdd" / "issue-12-pr-ready-wait").exists()


def test_4032_a_green_wait_after_a_flake_re_run_stops_it_so_the_block_writes_the_ci_flake_event(ready):
    (ready.wt / ".tdd" / "ci-flake.out").write_text("tests/test_x.py\n")
    code, out, err, fake = ready()

    assert (code, out.splitlines()[-1]) == (1, "stopped at 2 wait-ci.sh exit 0 with .tdd/ci-flake.out non-empty")
    assert not (ready.wt / ".tdd" / "issue-12-pr-ready-wait").exists()


def test_4032_it_writes_only_the_done_event_commits_only_the_metrics_and_handles_no_refusal(ready):
    ready(answers={("pr-ready.sh", None): (2, "")})
    code, out, err, fake = ready()

    assert code == 0
    assert not {"classify-bail.sh", "preflight-refused.sh", "adjudicate.sh", "comment.sh", "detach-leaf.sh",
                "add-ledger-step.sh", "rebase-onto-default.sh"} & set(fake.names())
    assert [c[1][0] for c in fake.made("event.sh")] == ["done"]
    assert [c[1][2] for c in fake.made("git") if c[1][:1] == ("commit",)] == ["metrics: what solving #12 cost (#12)"]
    assert not [c for c in fake.made("git") if c[1][:1] in (("push",), ("reset",))]


def first_block():
    """DRAFT-PR.md sub-step 2's opening and its first block, up to that block's closing fence."""
    from pathlib import Path
    module = importlib.import_module("veri.pr_ready_wait")
    draft = (Path(module.__file__).resolve().parents[2] / "DRAFT-PR.md").read_text()
    start = draft.index("\n2. **Mark the PR ready for review")
    opened = draft.index("   ```\n", start) + len("   ```\n")
    return draft[start:draft.index("   ```\n", opened)]


def test_4032_every_inner_call_in_the_ordered_list_is_a_script_sub_step_2s_first_block_names():
    pr_ready_wait = importlib.import_module("veri.pr_ready_wait")

    assert [name for name in pr_ready_wait.CALLS if "$S/" + name not in first_block()] == []


def _pid(ready, text):
    (ready.wt / ".tdd" / "conductor.pid").write_text(text)


def test_4032_a_wait_whose_slice_ran_out_exits_3_on_a_waiting_on_line(ready):
    code, out, err, fake = ready(answers={("wait-ci.sh", None): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on wait-ci.sh")
    assert not (ready.wt / ".tdd" / "issue-12-pr-ready-wait").exists()


def test_4032_called_again_after_an_exit_3_it_only_waits_again_and_never_readies_twice(ready):
    _pid(ready, "111\nTue Nov 17 07:00:00 2026\n")
    first = ready(answers={("wait-ci.sh", None): (3, "")})[0]
    code, out, err, fake = ready()

    assert (first, code) == (3, 0)
    assert [(c[0], c[1]) for c in fake.calls] == [("git", ("rev-parse", "HEAD")),
                                                  ("wait-ci.sh", (URL, "540", "", HEAD))]
    assert out.splitlines()[-3:] == ["pr_url=" + URL, "pr_number=42", "ci=green"]
    assert not (ready.wt / ".tdd" / "issue-12-pr-ready-wait-wait").exists()


def test_4332_a_resumed_call_with_every_full_suite_line_ticked_still_waits_on_the_head_and_closes_nothing_again(ready):
    _pid(ready, "111\nTue Nov 17 07:00:00 2026\n")
    ci = {("branch-suite.sh", None): (0, "ci\n")}
    first = ready(answers={**ci, ("wait-ci.sh", None): (3, "")}, ledger=TICKED)[0]
    assert (ready.wt / ".tdd" / "issue-12-pr-ready-wait-wait").exists()
    code, out, err, fake = ready(answers=ci, ledger=TICKED)

    assert (first, code) == (3, 0)
    assert [(c[0], c[1]) for c in fake.calls] == [("git", ("rev-parse", "HEAD")),
                                                  ("wait-ci.sh", (URL, "540", "", HEAD))]


def test_4032_the_wait_record_names_the_conductor_by_the_pid_and_start_time_its_pid_file_held(ready):
    import json
    _pid(ready, "111\nTue Nov 17 07:00:00 2026\n")
    ready(answers={("wait-ci.sh", None): (3, "")})

    record = json.loads((ready.wt / ".tdd" / "issue-12-pr-ready-wait-wait").read_text())
    assert (record["conductor"], record["values"]) == ({"pid": "111", "started": "Tue Nov 17 07:00:00 2026"},
                                                       {"pr_url": URL, "pr_number": "42", "metrics": 0})


@pytest.mark.parametrize("second", ["222\nTue Nov 17 07:00:00 2026\n", "111\nTue Nov 17 08:00:00 2026\n", None],
                         ids=["another pid", "another start time", "no pid file"])
def test_4032_called_under_another_conductor_it_discards_the_record_and_starts_from_its_first_call(ready, second):
    _pid(ready, "111\nTue Nov 17 07:00:00 2026\n")
    ready(answers={("wait-ci.sh", None): (3, "")})
    if second is None:
        (ready.wt / ".tdd" / "conductor.pid").unlink()
    else:
        _pid(ready, second)
    code, out, err, fake = ready()

    assert (code, fake.names()[:2], fake.names().count("pr-ready.sh")) == (0, ["git", "gh"], 1)


def test_4032_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_its_stderr(ready):
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) in ("gh", "git"):
                return code, out, err
            return code, "OUT<%d>\n" % len(self.calls) + out, "ERR<%d>\n" % len(self.calls)

    code, out, err, fake = ready(fake=Marked())

    lines = out.splitlines()
    assert code == 0
    for i, c in enumerate(fake.calls, 1):
        if c[0] in ("gh", "git"):
            continue
        named = lines[lines.index("OUT<%d>" % i) - 1]
        assert named.startswith(c[0]) and named.endswith(" exit 0") and "ERR<%d>" % i in err
