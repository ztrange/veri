"""In-process cases for veri/pr_finish.py, the module pr-finish.sh is a shim over (PRD 027.11, #4033)."""
import importlib
import os

import pytest

URL = "https://github.com/o/r/pull/42"
HEAD = "b" * 40
LEDGER = ("# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n- [ ] the full suite is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
          "- [ ] the full suite is green on the rebased tip ⟦full-suite⟧ ⟦criterion 3⟧\n")
BODY = "## Acceptance criteria\n\n- [x] one\n- [ ] two\n- [ ] three\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout) or (code, stdout, {redirected path: its text}). tick-ledger.sh
    exits 0 <ticks> times, then 3."""

    def __init__(self, answers=None, mode="ci", ticks=2):
        self.answers, self.calls, self.mode, self.ticks = dict(answers or {}), [], mode, ticks

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
            return 0, (BODY if "issues/12" in args[1] else URL + "\n"), ""
        if base == "git" and args[:1] == ("branch",):
            return 0, "tdd/12-thing\n", ""
        if base == "git" and args[:1] == ("rev-parse",):
            return 0, HEAD + "\n", ""
        if base == "branch-suite.sh":
            return 0, self.mode + "\n", ""
        if base == "tick-ledger.sh":
            self.ticks -= 1
            return (0 if self.ticks >= 0 else 3), "", ""
        if base == "ledger-steps.sh" and args[:1] == ("criterion",):
            return 0, {"2": "two", "3": "three"}[args[1]] + "\n", ""
        if base == "metrics.sh":
            with open(os.path.join(cwd, kw["out"]), "w") as f:
                f.write("## Metrics\n")
            return 0, "", ""
        if base == "refactor-owed.sh":
            return 0, "## Refactor owed\n\n- extract it\n", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def made(self, base, first=None):
        return [c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,))]


@pytest.fixture
def finish(monkeypatch, run_cli, tmp_path):
    """finish(answers=None, fake=None, missing=(), argv=None, ledger=LEDGER) runs pr-finish for issue 12 from the main
    tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    pr_finish = importlib.import_module("veri.pr_finish")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), argv=None, ledger=LEDGER):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", ledger)}
        for key, (path, text) in files.items():
            if key not in missing:
                path.write_text(text)
        if "wait-ci.err" not in missing and not (wt / ".tdd" / "wait-ci.err").exists():
            (wt / ".tdd" / "wait-ci.err").write_text("")  # the first wait's, which pr-ready-wait.sh leaves
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(pr_finish, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4033_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(finish):
    code, out, err, fake = finish(argv=())

    assert (code, "pr-finish.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.pr_finish").__file__)
    assert os.path.exists(os.path.join(here, "..", "pr-finish.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md")])
def test_4033_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(finish, missing, named):
    code, out, err, fake = finish(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


def _commits(fake):
    return [c[1][2] for c in fake.made("git", "commit")]


def test_4033_under_ci_it_ticks_each_full_suite_line_and_its_criterion_and_commits_the_plan(finish):
    code, out, err, fake = finish()

    assert [c[1] for c in fake.made("tick-ledger.sh")] == [(".tdd/issue-12.md", "⟦full-suite⟧")] * 3
    assert [c[1] for c in fake.made("ledger-steps.sh", "criterion")] == [("criterion", "2"), ("criterion", "3")]
    assert all(c[4]["stdin"] == BODY for c in fake.made("ledger-steps.sh", "criterion"))
    assert [c[1] for c in fake.made("tick-issue-criterion.sh")] == [("12", "two"), ("12", "three")]
    assert [c[1] for c in fake.made("git", "add")][0] == ("add", ".tdd/issue-12.md")
    assert _commits(fake)[0] == "plan: the full suite is green on CI (#12)"


@pytest.mark.parametrize("mode, ledger, err_text", [
    ("local", LEDGER, ""), ("ci", "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n", ""),
    ("ci", LEDGER.replace("- [ ]", "- [x]"), ""), ("ci", LEDGER, "PR 42 has no checks\n")],
    ids=["local", "no full-suite line", "every full-suite line ticked", "has no checks"])
def test_4033_otherwise_it_ticks_and_commits_nothing_of_the_kind(finish, mode, ledger, err_text):
    (finish.wt / ".tdd" / "wait-ci.err").write_text(err_text)
    code, out, err, fake = finish(fake=Fake(mode=mode), ledger=ledger)

    assert not {"tick-ledger.sh", "tick-issue-criterion.sh"} & set(fake.names())
    assert "plan: the full suite is green on CI (#12)" not in _commits(fake)


def test_4033_no_wait_ci_err_under_ci_with_a_line_to_tick_stops_it_with_exit_2_before_any_tick(finish):
    code, out, err, fake = finish(missing=("wait-ci.err",))

    assert (code, out.splitlines()[-1]) == (2, "stopped at 2 no .tdd/wait-ci.err")
    assert not {"tick-ledger.sh", "event.sh"} & set(fake.names())


RENDER = ".tdd/issue-12-refactor-owed-render"


def test_4033_it_marks_done_commits_the_metrics_pushes_waits_renders_and_settles(finish):
    code, out, err, fake = finish(fake=Fake(mode="local"))

    assert (code, out.splitlines()[-2:]) == (0, ["pr_url=" + URL, "refactor_owed_render=" + RENDER])
    assert (finish.wt / ".tdd" / "issue-12-pr-finish").read_text() == "pr_url=%s\nrefactor_owed_render=%s\n" % (URL,
                                                                                                              RENDER)
    assert [(c[0], c[1]) for c in fake.calls if c[0] != "gh"] == [
        ("git", ("branch", "--show-current")), ("branch-suite.sh", ()), ("event.sh", ("done", "pr=" + URL)),
        ("metrics.sh", ("12",)), ("git", ("add", ".tdd/issue-12-metrics.md")),
        ("git", ("commit", "-m", "metrics: what solving #12 cost (#12)")),
        ("git", ("status", "--porcelain", "--untracked-files=all")), ("push-branch.sh", ()),
        ("git", ("rev-parse", "HEAD")), ("wait-ci.sh", (URL, "540", "", HEAD)),
        ("refactor-owed.sh", ("render", ".tdd/issue-12-refactor-owed.md"))]
    done = fake.made("event.sh")[0][3]
    assert (done["VERI_ISSUE"], done["VERI_ACTOR"]) == ("12", "conductor")
    assert fake.made("metrics.sh")[0][4]["out"] == ".tdd/issue-12-metrics.md"
    waited = fake.made("wait-ci.sh")[0][4]
    assert (waited["out"], waited["err"]) == (".tdd/wait-ci.out", ".tdd/wait-ci.err")
    assert (finish.wt / RENDER).read_text() == "## Refactor owed\n\n- extract it\n"
    assert all(c[2] == str(finish.wt) for c in fake.calls)


def test_4033_a_failed_metrics_render_commits_nothing_goes_on_and_carries_its_code(finish):
    code, out, err, fake = finish(fake=Fake(mode="local", answers={("metrics.sh", None): (2, "")}))

    assert (code, "metrics=2" in out.splitlines()[-3:]) == (0, True)
    assert "metrics=2" in (finish.wt / ".tdd" / "issue-12-pr-finish").read_text()
    assert _commits(fake) == [] and "push-branch.sh" in fake.names()


@pytest.mark.parametrize("listed", ["?? .tdd/issue-12-metrics.md\n", " M .tdd/issue-12-metrics.md\n"],
                         ids=["left untracked", "committed by an earlier call"])
def test_4033_a_failed_metrics_render_that_left_its_file_is_no_dirty_tree(finish, listed):
    code, out, err, fake = finish(fake=Fake(mode="local", answers={("metrics.sh", None): (1, ""),
                                                                   ("git", "status"): (0, listed)}))

    assert (code, "metrics=1" in out.splitlines()[-3:], "push-branch.sh" in fake.names()) == (0, True, True)


def test_4033_a_failed_metrics_render_still_stops_at_any_other_dirty_path(finish):
    code, out, err, fake = finish(fake=Fake(mode="local", answers={
        ("metrics.sh", None): (1, ""), ("git", "status"): (0, "?? .tdd/issue-12-metrics.md\n?? stray.py\n")}))

    assert (code, out.splitlines()[-1]) == (1, "stopped at 2 tree-check")


def test_4033_no_refactor_owed_render_writes_an_empty_file(finish):
    code, out, err, fake = finish(fake=Fake(mode="local", answers={("refactor-owed.sh", None): (3, "")}))

    assert (code, (finish.wt / RENDER).read_text()) == (0, "")


def test_4033_no_pr_for_the_branch_exits_2_before_any_tick_or_mark(finish):
    code, out, err, fake = finish(answers={("gh", None): (0, "\n")})

    assert (code, out.splitlines()[-1]) == (2, "stopped at 2 no PR for tdd/12-thing")
    assert fake.names() == ["git", "gh"]


def test_4033_a_dirty_tree_just_before_the_push_stops_it_with_exit_1(finish):
    code, out, err, fake = finish(answers={("git", "status"): (0, " M x.py\n")})

    assert (code, out.splitlines()[-1]) == (1, "stopped at 2 tree-check")
    assert "push-branch.sh" not in fake.names()


@pytest.mark.parametrize("script, inner, last", [
    ("push-branch.sh", 1, "push-branch.sh exit 1"), ("event.sh", 2, "event.sh done pr=%s exit 2" % URL),
    ("wait-ci.sh", 1, "wait-ci.sh %s 540  %s > .tdd/wait-ci.out 2> .tdd/wait-ci.err exit 1" % (URL, HEAD)),
    ("wait-ci.sh", 2, "wait-ci.sh %s 540  %s > .tdd/wait-ci.out 2> .tdd/wait-ci.err exit 2" % (URL, HEAD)),
    ("refactor-owed.sh", 2, "refactor-owed.sh render .tdd/issue-12-refactor-owed.md exit 2"),
    ("tick-issue-criterion.sh", 2, "tick-issue-criterion.sh 12 two exit 2")])
def test_4033_an_inner_call_that_fails_stops_it_with_its_code_and_runs_nothing_later(finish, script, inner, last):
    code, out, err, fake = finish(answers={(script, None): (inner, "")})

    assert (code, out.splitlines()[-1], fake.calls[-1][0]) == (inner, "stopped at 2 " + last, script)
    assert not (finish.wt / ".tdd" / "issue-12-pr-finish").exists()


def test_4033_it_writes_no_bail_and_handles_no_refusal_and_leaves_the_title_and_body_alone(finish):
    finish(answers={("wait-ci.sh", None): (1, "")})
    code, out, err, fake = finish()

    assert code == 0
    assert not {"classify-bail.sh", "preflight-refused.sh", "adjudicate.sh", "comment.sh", "detach-leaf.sh",
                "add-ledger-step.sh", "rebase-onto-default.sh", "pr-body.sh", "ledger-growth.sh",
                "ci-flake.sh"} & set(fake.names())
    assert [c[1][0] for c in fake.made("event.sh")] == ["done"]
    assert not [c for c in fake.made("gh") if "PATCH" in c[1]]
    assert not [c for c in fake.made("git") if c[1][:1] in (("reset",), ("push",))]


def second_block():
    """DRAFT-PR.md sub-step 2's second block, from the `Otherwise:` that opens it to its closing fence."""
    from pathlib import Path
    module = importlib.import_module("veri.pr_finish")
    draft = (Path(module.__file__).resolve().parents[2] / "DRAFT-PR.md").read_text()
    start = draft.index("\n2. **Mark the PR ready for review")
    opened = draft.index("Otherwise:\n   ```\n", start)
    return draft[opened:draft.index("   ```\n", opened + len("Otherwise:\n   ```\n"))]


def test_4033_every_inner_call_in_the_ordered_list_is_a_script_sub_step_2s_second_block_names():
    pr_finish = importlib.import_module("veri.pr_finish")

    assert [name for name in pr_finish.CALLS if "$S/" + name not in second_block()] == []


def test_4033_a_clean_run_makes_the_calls_of_the_ordered_list_in_its_order(finish):
    pr_finish = importlib.import_module("veri.pr_finish")
    code, out, err, fake = finish()

    made = [name for name in fake.names() if name not in ("git", "gh")]
    assert code == 0 and set(made) == set(pr_finish.CALLS)
    firsts = [made.index(name) for name in pr_finish.CALLS]
    assert firsts == sorted(firsts)


def _pid(finish, text):
    (finish.wt / ".tdd" / "conductor.pid").write_text(text)


def test_4033_a_wait_whose_slice_ran_out_exits_3_on_a_waiting_on_line_before_the_render(finish):
    code, out, err, fake = finish(answers={("wait-ci.sh", None): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on wait-ci.sh")
    assert "refactor-owed.sh" not in fake.names()


def test_4033_called_again_after_an_exit_3_it_only_waits_again_with_no_second_mark_commit_tick_or_push(finish):
    _pid(finish, "111\nTue Nov 17 07:00:00 2026\n")
    first = finish(fake=Fake(answers={("wait-ci.sh", None): (3, ""), ("metrics.sh", None): (2, "")}))[0]
    code, out, err, fake = finish()

    assert (first, code) == (3, 0)
    assert [(c[0], c[1]) for c in fake.calls] == [("git", ("rev-parse", "HEAD")), ("wait-ci.sh", (URL, "540", "", HEAD)),
                                                  ("refactor-owed.sh", ("render", ".tdd/issue-12-refactor-owed.md"))]
    assert out.splitlines()[-3:] == ["pr_url=" + URL, "metrics=2", "refactor_owed_render=" + RENDER]
    assert not (finish.wt / ".tdd" / "issue-12-pr-finish-wait").exists()


def test_4033_the_wait_record_names_the_conductor_by_the_pid_and_start_time_its_pid_file_held(finish):
    import json
    _pid(finish, "111\nTue Nov 17 07:00:00 2026\n")
    finish(answers={("wait-ci.sh", None): (3, "")})

    record = json.loads((finish.wt / ".tdd" / "issue-12-pr-finish-wait").read_text())
    assert record["conductor"] == {"pid": "111", "started": "Tue Nov 17 07:00:00 2026"}


@pytest.mark.parametrize("second", ["222\nTue Nov 17 07:00:00 2026\n", "111\nTue Nov 17 08:00:00 2026\n", None],
                         ids=["another pid", "another start time", "no pid file"])
def test_4033_called_under_another_conductor_it_discards_the_record_and_starts_from_its_first_call(finish, second):
    _pid(finish, "111\nTue Nov 17 07:00:00 2026\n")
    finish(answers={("wait-ci.sh", None): (3, "")})
    if second is None:
        (finish.wt / ".tdd" / "conductor.pid").unlink()
    else:
        _pid(finish, second)
    code, out, err, fake = finish()

    assert (code, fake.names()[:2], [c[1][0] for c in fake.made("event.sh")]) == (0, ["git", "gh"], ["done"])


def test_4033_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_its_stderr(finish):
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) in ("gh", "git", "branch-suite.sh", "ledger-steps.sh"):
                return code, out, err
            return code, "OUT<%d>\n" % len(self.calls) + out, "ERR<%d>\n" % len(self.calls)

    code, out, err, fake = finish(fake=Marked())

    lines = out.splitlines()
    assert code == 0
    for i, c in enumerate(fake.calls, 1):
        if c[0] in ("gh", "git", "branch-suite.sh", "ledger-steps.sh") or c[4].get("out"):
            continue
        named = lines[lines.index("OUT<%d>" % i) - 1]
        assert named.startswith(c[0]) and named.endswith((" exit 0", " exit 3")) and "ERR<%d>" % i in err
