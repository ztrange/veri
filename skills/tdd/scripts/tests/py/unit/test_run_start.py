"""In-process cases for veri/run_start.py, the module run-start.sh is a shim over (PRD 027.13, #4024)."""
import importlib
import os

import pytest


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, porcelain=" M .gitignore\n"):
        self.answers, self.calls, self.porcelain = dict(answers or {}), [], porcelain

    def __call__(self, name, *args, cwd=None, env=None, out=None, **_):
        code, text, err = self.answer(name, *args, cwd=cwd, env=env)
        if out is not None:
            with open(os.path.join(cwd, out), "w") as f:
                f.write(text)
            text = ""
        return code, text, err

    def answer(self, name, *args, cwd=None, env=None):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "leaf-timeout.sh":
            return 0, "1800\n", ""
        if base == "capture-spec.sh":
            return 0, "# spec of 12\n", ""
        if base == "ensure-run-state-ignored.sh":
            return 0, "added\n", ""
        if base == "git" and args == ("status", "--porcelain"):
            return 0, self.porcelain, ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]


@pytest.fixture
def start(monkeypatch, run_cli, tmp_path):
    """start(ledger=False, answers=None, fake=None, preflight=True) runs run-start for issue 12 from the main tree,
    the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    run_start = importlib.import_module("veri.run_start")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(ledger=False, answers=None, fake=None, preflight=True, argv=("12",)):
        if preflight:
            (wt / ".tdd" / "issue-12-preflight").write_text(
                "worktree=%s\nfast_cmd=make unit\nbaseline=8\nfull=95\ntimeout=1800\nrun=fresh\n" % wt)
        if ledger:
            (wt / ".tdd" / "issue-12.md").write_text("- [ ] a step\n")
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(run_start, list(argv), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4024_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(start):
    code, out, err, fake = start(argv=())

    assert (code, "run-start.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.run_start").__file__)
    assert os.path.exists(os.path.join(here, "..", "run-start.sh"))


COMMIT = ("commit", "-m", "chore: ignore veri run state (#12)")


def test_4024_it_records_the_timeout_captures_the_spec_ignores_run_state_and_commits_gitignore_in_order_in_the_worktree(
        start):
    code, out, err, fake = start()

    assert code == 0
    assert [(c[0], c[1]) for c in fake.calls] == [
        ("leaf-timeout.sh", ("8", "--full", "95")), ("capture-spec.sh", ("12",)), ("ensure-run-state-ignored.sh", ()),
        ("git", ("status", "--porcelain")), ("git", ("add", ".gitignore")), ("git", COMMIT)]
    assert {c[2] for c in fake.calls} == {str(start.wt)}
    assert fake.calls[0][3]["VERI_ISSUE"] == "12"
    assert (start.wt / ".tdd" / "issue-12-spec.md").read_text() == "# spec of 12\n"


def test_4024_already_present_commits_nothing(start):
    code, out, err, fake = start(answers={("ensure-run-state-ignored.sh", None): (0, "already present\n")})

    assert (code, fake.names()) == (0, ["leaf-timeout.sh", "capture-spec.sh", "ensure-run-state-ignored.sh"])


def test_4338_a_worktree_whose_gitignore_holds_veris_own_4048_rule_commits_nothing_at_1_4(start, fake_processes):
    import contextlib
    import io

    from conftest import SCRIPTS
    ensure_run_state_ignored = importlib.import_module("veri.ensure_run_state_ignored")
    main_gitignore = (SCRIPTS.parents[2] / ".gitignore").read_bytes()
    (start.wt / ".gitignore").write_bytes(main_gitignore)
    fake_processes.answers({"git": lambda line, **kwargs: (0, ".git\n", None)})

    class RealEnsure(Fake):
        def answer(self, name, *args, cwd=None, env=None):
            if os.path.basename(name) != "ensure-run-state-ignored.sh":
                return super().answer(name, *args, cwd=cwd, env=env)
            self.calls.append((os.path.basename(name), args, cwd, env))
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = ensure_run_state_ignored.main([cwd])
            return code, out.getvalue(), err.getvalue()

    code, out, err, fake = start(fake=RealEnsure())

    assert (code, [c[1][0] for c in fake.calls if c[0] == "git"]) == (0, [])
    assert "gitignore=already present" in out.splitlines()
    assert (start.wt / ".gitignore").read_bytes() == main_gitignore


def test_4024_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_stderr_and_the_spec_goes_to_its_file(
        start):
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            return code, out, "ERR<%s>\n" % os.path.basename(name)

    code, out, err, fake = start(fake=Marked())

    lines = out.splitlines()
    assert lines[:6] == ["leaf-timeout.sh 8 --full 95 exit 0", "1800",
                         "capture-spec.sh 12 > .tdd/issue-12-spec.md exit 0",
                         "ensure-run-state-ignored.sh exit 0", "added", "git status --porcelain exit 0"]
    assert "# spec of 12" not in lines
    assert all("ERR<%s>" % name in err for name in ("leaf-timeout.sh", "capture-spec.sh", "git"))


@pytest.mark.parametrize("failing, where", [("leaf-timeout.sh", "1.2"), ("capture-spec.sh", "1.3"),
                                            ("ensure-run-state-ignored.sh", "1.4")])
@pytest.mark.parametrize("inner, exits", [(2, 2), (1, 1), (3, 1)])
def test_4024_the_first_failing_call_stops_it_with_no_later_call_and_a_stopped_at_line(start, failing, where, inner,
                                                                                         exits):
    code, out, err, fake = start(answers={(failing, None): (inner, "")})

    assert (code, fake.names()[-1]) == (exits, failing)
    assert out.splitlines()[-1].startswith("stopped at %s %s" % (where, failing))
    assert out.splitlines()[-1].endswith("exit %d" % inner)
    assert not (start.wt / ".tdd" / "issue-12-run-start").exists()


def test_4024_a_failed_gitignore_commit_stops_it_at_1_4(start):
    code, out, err, fake = start(answers={("git", "commit"): (1, "")})

    assert (code, out.splitlines()[-1]) == (1, "stopped at 1.4 git " + " ".join(COMMIT[:2]) + " "
                                            + COMMIT[2] + " exit 1")


@pytest.mark.parametrize("porcelain", [" M .gitignore\n?? stray.py\n", " M src/a.py\n", " M .gitignore\n M .gitignore2\n"])
def test_4024_a_tree_listing_anything_but_gitignore_before_the_commit_stops_at_1_4_tree_check_committing_nothing(
        start, porcelain):
    code, out, err, fake = start(fake=Fake(porcelain=porcelain))

    assert (code, out.splitlines()[-1]) == (1, "stopped at 1.4 tree-check")
    assert fake.calls[-1][:2] == ("git", ("status", "--porcelain"))


@pytest.mark.parametrize("reverify, line", [(0, "verify_plan=owed"), (3, "verify_plan=skip")])
def test_4024_on_a_resume_it_asks_plan_reverify_and_prints_whether_verify_plan_is_owed(start, reverify, line):
    code, out, err, fake = start(ledger=True, answers={("plan-reverify.sh", None): (reverify, "")})

    assert (code, fake.calls[-1][:2]) == (0, ("plan-reverify.sh", (".tdd/issue-12.md",)))
    assert line in out.splitlines()


@pytest.mark.parametrize("reverify", [1, 2])
def test_4024_plan_reverify_failing_stops_it_at_1_5(start, reverify):
    code, out, err, fake = start(ledger=True, answers={("plan-reverify.sh", None): (reverify, "")})

    assert (code, out.splitlines()[-1]) == (reverify, "stopped at 1.5 plan-reverify.sh .tdd/issue-12.md exit %d"
                                            % reverify)


def test_4024_a_fresh_run_asks_no_plan_reverify(start):
    code, out, err, fake = start()

    assert "plan-reverify.sh" not in fake.names()
    assert not [line for line in out.splitlines() if line.startswith("verify_plan=")]


@pytest.mark.parametrize("ledger, ignored, expected", [
    (False, "added", ["run=fresh", "spec=.tdd/issue-12-spec.md", "timeout_recorded=.tdd/issue-12-timeout",
                      "gitignore=added"]),
    (True, "already present", ["run=resume", "spec=.tdd/issue-12-spec.md", "timeout_recorded=.tdd/issue-12-timeout",
                               "gitignore=already present", "verify_plan=owed"])], ids=["fresh", "resume"])
def test_4024_exit_0_writes_the_run_start_file_and_prints_the_same_lines_last(start, ledger, ignored, expected):
    code, out, err, fake = start(ledger=ledger, answers={("ensure-run-state-ignored.sh", None): (0, ignored + "\n")})

    assert code == 0
    assert (start.wt / ".tdd" / "issue-12-run-start").read_text().splitlines() == expected
    assert out.splitlines()[-len(expected):] == expected


def test_4024_the_run_start_file_is_run_state_the_ignore_rule_keeps_out_of_every_commit(start):
    import fnmatch
    rule = importlib.import_module("veri.ensure_run_state_ignored").RULE
    start()

    name = ".tdd/" + (start.wt / ".tdd" / "issue-12-run-start").name
    assert fnmatch.fnmatch(name, rule[0]) and not fnmatch.fnmatch(name, rule[1].lstrip("!"))


@pytest.mark.parametrize("ledger", [True, False], ids=["resume", "fresh"])
def test_4024_it_posts_no_comment_on_either_path(start, ledger):
    code, out, err, fake = start(ledger=ledger)

    assert code == 0
    assert "comment.sh" not in fake.names()
    assert not [c for c in fake.calls if c[0] == "gh"]


def _section(text, heading, following):
    return text[text.index(heading):text.index(following)]


def test_4024_every_inner_call_in_the_ordered_list_is_a_script_skill_md_step_1_names():
    from pathlib import Path
    run_start = importlib.import_module("veri.run_start")
    skill = (Path(run_start.__file__).resolve().parents[2] / "SKILL.md").read_text()
    step_1 = _section(skill, "### 1. Read the issue", "### 2. Scope & plan")

    assert [name for name in run_start.CALLS if "$S/" + name not in step_1] == []


def test_4024_a_resume_makes_the_calls_of_the_ordered_list_in_its_order(start):
    run_start = importlib.import_module("veri.run_start")
    code, out, err, fake = start(ledger=True)

    assert [name for name in fake.names() if name != "git"] == list(run_start.CALLS)


def test_4024_a_stop_handles_no_refusal_resets_nothing_and_writes_no_bail(start):
    code, out, err, fake = start(answers={("capture-spec.sh", None): (2, "")})

    assert not {"classify-bail.sh", "preflight-refused.sh", "comment.sh", "event.sh", "gh"} & set(fake.names())
    assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] in (("reset",), ("checkout",))]


def test_4024_a_missing_preflight_file_is_exit_2_before_any_inner_call_named_on_stderr(start):
    code, out, err, fake = start(preflight=False)

    assert (code, fake.calls) == (2, [])
    assert ".tdd/issue-12-preflight" in err


@pytest.mark.parametrize("mode, tail", [("reuse", ("--reused",)), ("run", ()), (None, ())])
def test_4835_a_reused_full_tier_time_is_handed_to_leaf_timeout_as_reused_and_a_run_one_is_not(start, mode, tail):
    line = "" if mode is None else "full_tier_mode=%s\n" % mode
    (start.wt / ".tdd" / "issue-12-preflight").write_text(
        "worktree=%s\nfast_cmd=make unit\nbaseline=0\nfull=95\n%stimeout=1800\nrun=fresh\n" % (start.wt, line))
    code, out, err, fake = start(preflight=False)

    assert (code, fake.calls[0][:2]) == (0, ("leaf-timeout.sh", ("0", "--full", "95", *tail)))
