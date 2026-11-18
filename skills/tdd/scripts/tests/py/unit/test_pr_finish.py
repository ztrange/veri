"""In-process cases for veri/pr_finish.py, the module pr-finish.sh is a shim over (PRD 027.11, #4033), and for the
run's record pr-ready-wait.sh closes through it before readying (#4332)."""
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
    """finish(answers=None, fake=None, missing=(), argv=None, ledger=LEDGER, module="pr_finish") runs pr-finish (or
    the veri <module> named) for issue 12 from the main tree, the run's worktree at .tdd/wt/12; returns (code, stdout,
    stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), argv=None, ledger=LEDGER, module="pr_finish"):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", ledger)}
        for key, (path, text) in files.items():
            if key not in missing:
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(importlib.import_module("veri." + module), list(argv if argv is not None else ("12",)),
                                 cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4033_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(finish):
    code, out, err, fake = finish(argv=())

    assert (code, "pr-finish.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.pr_finish").__file__)
    assert os.path.exists(os.path.join(here, "..", "pr-finish.sh"))


@pytest.mark.parametrize("missing, named, module", [("preflight", ".tdd/issue-12-preflight", "pr_finish"),
                                                     ("ledger", ".tdd/issue-12.md", "pr_ready_wait")])
def test_4033_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(finish, missing, named, module):
    code, out, err, fake = finish(missing=(missing,), module=module)

    assert (code, fake.calls) == (2, [])
    assert named in err


def test_4033_a_stacked_run_is_refused_with_exit_2_before_any_inner_call(finish):
    (finish.wt / ".tdd" / "issue-12-base").write_text("tdd/11-below\n")
    code, out, err, fake = finish()

    assert (code, fake.calls) == (2, [])
    assert "stacked" in err and ".tdd/issue-12-base" in err


class Failing(Fake):
    """Fake, but the first call <hit> takes (base, args) to exits <code>."""

    def __init__(self, hit, code, **kw):
        super().__init__(**kw)
        self.hit, self.code = hit, code

    def __call__(self, name, *args, **kw):
        if self.hit(os.path.basename(name), args):
            self.hit = lambda *_: False
            self.calls.append((os.path.basename(name), args, kw.get("cwd"), kw.get("env"), kw))
            return self.code, "", "boom\n"
        return super().__call__(name, *args, **kw)


def _git_hit(verb, *more):
    return lambda b, a: b == "git" and a[:1] == (verb,) and all(m in a[-1] for m in more)


@pytest.mark.parametrize("hit, code, mode, module", [
    (_git_hit("branch"), 128, "ci", "pr_finish"), (lambda b, a: b == "gh" and "pulls" in a[1], 1, "ci", "pr_finish"),
    (_git_hit("branch"), 128, "ci", "pr_ready_wait"),
    (lambda b, a: b == "gh" and "pulls" in a[1], 1, "ci", "pr_ready_wait"),
    (lambda b, a: b == "gh" and "pulls" in a[1], 4, "ci", "pr_ready_wait"),
    (lambda b, a: b == "gh" and "issues/12" in a[1], 1, "ci", "pr_ready_wait"),
    (_git_hit("add", "issue-12.md"), 128, "ci", "pr_ready_wait"),
    (_git_hit("commit", "plan:"), 1, "ci", "pr_ready_wait"),
    (_git_hit("add", "metrics"), 128, "local", "pr_ready_wait"),
    (_git_hit("commit", "metrics:"), 1, "local", "pr_ready_wait"),
    (_git_hit("status"), 128, "local", "pr_ready_wait"), (_git_hit("rev-parse"), 128, "local", "pr_ready_wait")],
    ids=["pr-finish git branch", "pr-finish gh url read", "git branch", "gh url read exit 1", "gh url read exit 4",
         "gh issue body read", "git add ledger", "git commit plan", "git add metrics", "git commit metrics",
         "git status", "git rev-parse"])
def test_4033_a_git_or_gh_call_that_fails_is_no_answer_exit_2(finish, hit, code, mode, module):
    out_code, out, err, fake = finish(fake=Failing(hit, code, mode=mode), module=module)

    assert (out_code, out.splitlines()[-1].startswith("stopped at 2 ")) == (2, True)
    assert "wait-ci.sh" not in fake.names()


def _commits(fake):
    return [c[1][2] for c in fake.made("git", "commit")]


def test_4033_under_ci_it_ticks_each_full_suite_line_and_its_criterion_and_commits_the_plan(finish):
    code, out, err, fake = finish(module="pr_ready_wait")

    assert [c[1] for c in fake.made("tick-ledger.sh")] == [(".tdd/issue-12.md", "⟦full-suite⟧")] * 3
    assert [c[1] for c in fake.made("ledger-steps.sh", "criterion")] == [("criterion", "2"), ("criterion", "3")]
    assert all(c[4]["stdin"] == BODY for c in fake.made("ledger-steps.sh", "criterion"))
    assert [c[1] for c in fake.made("tick-issue-criterion.sh")] == [("12", "two"), ("12", "three")]
    assert [c[1] for c in fake.made("git", "add")][0] == ("add", ".tdd/issue-12.md")
    assert _commits(fake)[0] == "plan: the full suite is owed to CI (#12)"


@pytest.mark.parametrize("mode, ledger", [
    ("local", LEDGER), ("ci", "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n"), ("ci", LEDGER.replace("- [ ]", "- [x]"))],
    ids=["local", "no full-suite line", "every full-suite line ticked"])
def test_4033_otherwise_it_ticks_and_commits_nothing_of_the_kind(finish, mode, ledger):
    code, out, err, fake = finish(fake=Fake(mode=mode), ledger=ledger, module="pr_ready_wait")

    assert not {"tick-ledger.sh", "tick-issue-criterion.sh"} & set(fake.names())
    assert "plan: the full suite is owed to CI (#12)" not in _commits(fake)


@pytest.mark.parametrize("stale", [None, "PR 42 has no checks\n"], ids=["no wait-ci.err", "a stale has-no-checks one"])
def test_4332_under_ci_with_no_wait_ci_err_pr_ready_wait_ticks_the_line_and_commits_it_as_owed_before_readying(finish,
                                                                                                             stale):
    if stale is not None:
        (finish.wt / ".tdd" / "wait-ci.err").write_text(stale)  # an earlier wait's, before a ⟦ci-repair⟧ loop
    code, out, err, fake = finish(module="pr_ready_wait")

    made = [c[1][2] if c[0] == "git" else c[0] for c in fake.calls
            if c[0] in ("tick-ledger.sh", "pr-ready.sh") or (c[0], c[1][:1]) == ("git", ("commit",))]
    assert (code, made) == (0, ["tick-ledger.sh"] * 3 + ["plan: the full suite is owed to CI (#12)",
                                                         "metrics: what solving #12 cost (#12)", "pr-ready.sh"])


def test_4332_with_every_full_suite_line_ticked_a_red_first_wait_stops_pr_ready_wait_with_exit_1_after_the_push(finish):
    code, out, err, fake = finish(answers={("wait-ci.sh", None): (1, "")}, ledger=LEDGER.replace("- [ ]", "- [x]"),
                                  module="pr_ready_wait")

    assert (code, out.splitlines()[-1]) == (1, "stopped at 2 wait-ci.sh %s 540  %s > .tdd/wait-ci.out 2> "
                                            ".tdd/wait-ci.err exit 1" % (URL, HEAD))
    assert [n for n in fake.names() if n in ("tick-ledger.sh", "push-branch.sh", "pr-ready.sh", "wait-ci.sh")] == [
        "push-branch.sh", "pr-ready.sh", "wait-ci.sh"]


RENDER = ".tdd/issue-12-refactor-owed-render"


def test_4332_pr_ready_wait_commits_the_metrics_then_pushes_them_then_readies_the_pr(finish):
    code, out, err, fake = finish(fake=Fake(mode="local"), module="pr_ready_wait")

    made = [c[1][2] if c[0] == "git" else c[0] for c in fake.calls
            if c[0] in ("push-branch.sh", "pr-ready.sh") or (c[0], c[1][:1]) == ("git", ("commit",))]
    assert (code, made) == (0, ["metrics: what solving #12 cost (#12)", "push-branch.sh", "pr-ready.sh"])


def test_4332_pr_finish_reads_the_pr_url_writes_the_done_mark_renders_and_settles_with_no_commit_push_or_wait(finish):
    code, out, err, fake = finish(fake=Fake(mode="local"))

    assert (code, out.splitlines()[-2:]) == (0, ["pr_url=" + URL, "refactor_owed_render=" + RENDER])
    assert (finish.wt / ".tdd" / "issue-12-pr-finish").read_text() == "pr_url=%s\nrefactor_owed_render=%s\n" % (URL,
                                                                                                              RENDER)
    assert [(c[0], c[1]) for c in fake.calls if c[0] != "gh"] == [
        ("git", ("branch", "--show-current")), ("event.sh", ("done", "pr=" + URL)),
        ("refactor-owed.sh", ("render", ".tdd/issue-12-refactor-owed.md"))]
    done = fake.made("event.sh")[0][3]
    assert (done["VERI_ISSUE"], done["VERI_ACTOR"]) == ("12", "conductor")
    assert (finish.wt / RENDER).read_text() == "## Refactor owed\n\n- extract it\n"
    assert all(c[2] == str(finish.wt) for c in fake.calls)


def test_4033_a_failed_metrics_render_commits_nothing_goes_on_and_carries_its_code(finish):
    code, out, err, fake = finish(fake=Fake(mode="local", answers={("metrics.sh", None): (2, "")}),
                                  module="pr_ready_wait")

    assert (code, "metrics=2" in out.splitlines()[-3:]) == (0, True)
    assert "metrics=2" in (finish.wt / ".tdd" / "issue-12-pr-ready-wait").read_text()
    assert _commits(fake) == [] and "push-branch.sh" in fake.names()


@pytest.mark.parametrize("listed", ["?? .tdd/issue-12-metrics.md\n", " M .tdd/issue-12-metrics.md\n"],
                         ids=["left untracked", "committed by an earlier call"])
def test_4033_a_failed_metrics_render_that_left_its_file_is_no_dirty_tree(finish, listed):
    code, out, err, fake = finish(fake=Fake(mode="local", answers={("metrics.sh", None): (1, ""),
                                                                   ("git", "status"): (0, listed)}),
                                  module="pr_ready_wait")

    assert (code, "metrics=1" in out.splitlines()[-3:], "push-branch.sh" in fake.names()) == (0, True, True)


def test_4033_a_failed_metrics_render_still_stops_at_any_other_dirty_path(finish):
    code, out, err, fake = finish(fake=Fake(mode="local", answers={
        ("metrics.sh", None): (1, ""), ("git", "status"): (0, "?? .tdd/issue-12-metrics.md\n?? stray.py\n")}),
        module="pr_ready_wait")

    assert (code, out.splitlines()[-1]) == (1, "stopped at 2 tree-check")


def test_4033_no_refactor_owed_render_writes_an_empty_file(finish):
    code, out, err, fake = finish(fake=Fake(mode="local", answers={("refactor-owed.sh", None): (3, "")}))

    assert (code, (finish.wt / RENDER).read_text()) == (0, "")


def test_4033_no_pr_for_the_branch_exits_2_before_any_tick_or_mark(finish):
    code, out, err, fake = finish(answers={("gh", None): (0, "\n")})

    assert (code, out.splitlines()[-1]) == (2, "stopped at 2 no PR for tdd/12-thing")
    assert fake.names() == ["git", "gh"]


def test_4033_a_dirty_tree_just_before_the_push_stops_it_with_exit_1(finish):
    code, out, err, fake = finish(answers={("git", "status"): (0, " M x.py\n")}, module="pr_ready_wait")

    assert (code, out.splitlines()[-1]) == (1, "stopped at 2 tree-check")
    assert "push-branch.sh" not in fake.names()


@pytest.mark.parametrize("script, inner, last, module", [
    ("push-branch.sh", 1, "push-branch.sh exit 1", "pr_ready_wait"),
    ("event.sh", 2, "event.sh metrics-cut pr=%s exit 2" % URL, "pr_ready_wait"),
    ("event.sh", 2, "event.sh done pr=%s exit 2" % URL, "pr_finish"),
    ("refactor-owed.sh", 2, "refactor-owed.sh render .tdd/issue-12-refactor-owed.md exit 2", "pr_finish"),
    ("tick-issue-criterion.sh", 2, "tick-issue-criterion.sh 12 two exit 2", "pr_ready_wait")])
def test_4033_an_inner_call_that_fails_stops_it_with_its_code_and_runs_nothing_later(finish, script, inner, last,
                                                                                     module):
    code, out, err, fake = finish(answers={(script, None): (inner, "")}, module=module)

    assert (code, out.splitlines()[-1], fake.calls[-1][0]) == (inner, "stopped at 2 " + last, script)
    assert not (finish.wt / ".tdd" / ("issue-12-" + module.replace("_", "-"))).exists()


def test_4033_it_writes_no_bail_and_handles_no_refusal_and_leaves_the_title_and_body_alone(finish):
    finish(answers={("refactor-owed.sh", None): (2, "")})
    code, out, err, fake = finish()

    assert code == 0
    assert not {"classify-bail.sh", "preflight-refused.sh", "adjudicate.sh", "comment.sh", "detach-leaf.sh",
                "add-ledger-step.sh", "rebase-onto-default.sh", "pr-body.sh", "ledger-growth.sh", "ci-flake.sh",
                "metrics.sh", "push-branch.sh", "wait-ci.sh"} & set(fake.names())
    assert [c[1] for c in fake.made("event.sh")] == [("done", "pr=" + URL)]
    assert not [c for c in fake.made("gh") if "PATCH" in c[1]]
    assert [c[1][0] for c in fake.made("git")] == ["branch"]


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


@pytest.mark.parametrize("module", ["pr_finish", "pr_ready_wait"])
def test_4033_a_clean_run_makes_the_calls_of_the_ordered_list_in_its_order(finish, module):
    calls = importlib.import_module("veri." + module).CALLS
    code, out, err, fake = finish(module=module)

    made = [name for name in fake.names() if name not in ("git", "gh")]
    assert code == 0 and set(made) == set(calls)
    firsts = [made.index(name) for name in calls]
    assert firsts == sorted(firsts)


def _pid(finish, text):
    (finish.wt / ".tdd" / "conductor.pid").write_text(text)


def test_4033_called_again_after_an_exit_3_it_only_waits_again_with_no_second_mark_commit_tick_or_push(finish):
    _pid(finish, "111\nTue Nov 17 07:00:00 2026\n")
    first = finish(fake=Fake(answers={("wait-ci.sh", None): (3, ""), ("metrics.sh", None): (2, "")}),
                   module="pr_ready_wait")[0]
    code, out, err, fake = finish(module="pr_ready_wait")

    assert (first, code) == (3, 0)
    assert [(c[0], c[1]) for c in fake.calls] == [("git", ("rev-parse", "HEAD")),
                                                  ("wait-ci.sh", (URL, "540", "", HEAD))]
    assert out.splitlines()[-4:] == ["pr_url=" + URL, "pr_number=42", "ci=green", "metrics=2"]
    assert not (finish.wt / ".tdd" / "issue-12-pr-ready-wait-wait").exists()


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
