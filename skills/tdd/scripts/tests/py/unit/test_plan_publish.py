"""In-process cases for veri/plan_publish.py, the module plan-publish.sh is a shim over (PRD 027.3, #4025)."""
import importlib
import json
import os

import pytest

PLAN_SHA = "c" * 40
PR_URL = "https://github.com/o/r/pull/77"
TITLE = "WIP: feat: a thing (#12)"
LEDGER = "# Plan for #12\n\n- [ ] one ⟦criterion 1⟧\n- [ ] two ⟦criterion 2⟧\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, porcelain=" M .tdd/issue-12.md\n", pr=""):
        self.answers, self.calls, self.porcelain, self.pr = dict(answers or {}), [], porcelain, pr

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "ledger-steps.sh":
            return 0, "1\topen\tstep\t0\t0\t1\tone\n2\topen\tstep\t0\t0\t2\ttwo\n", ""
        if base == "git" and args == ("status", "--porcelain"):
            return 0, self.porcelain, ""
        if base == "git" and args == ("rev-parse", "HEAD"):
            return 0, PLAN_SHA + "\n", ""
        if base == "git" and args == ("branch", "--show-current"):
            return 0, "tdd/12-a-thing\n", ""
        if base == "stack-branch.sh":
            return 3, "", ""
        if base == "gh" and args[1].startswith("repos/{owner}/{repo}/pulls?head="):
            return 0, self.pr, ""
        if base == "gh" and args[1] == "repos/{owner}/{repo}/pulls":
            return 0, PR_URL + "\n", ""
        if base == "stop-requested.sh":
            return 3, "", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def publish(monkeypatch, run_cli, tmp_path):
    """publish(answers=None, fake=None, missing=()) runs plan-publish for issue 12 from the main tree, the run's
    worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    plan_publish = importlib.import_module("veri.plan_publish")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    title = tmp_path / "title.txt"

    def go(answers=None, fake=None, missing=(), argv=None):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight",
                               "worktree=%s\nfast_cmd=make unit\ndefault_branch=main\nrun=fresh\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", LEDGER), "title": (title, TITLE + "\n")}
        for key, (path, text) in files.items():
            if key not in missing and not path.exists():
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(plan_publish, list(argv if argv is not None else ("12", str(title))),
                                 cwd=str(tmp_path))
        return code, out, err, fake

    go.wt, go.title = wt, title
    return go


def test_4025_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(publish):
    code, out, err, fake = publish(argv=())

    assert (code, "plan-publish.sh <n> <title-file>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.plan_publish").__file__)
    assert os.path.exists(os.path.join(here, "..", "plan-publish.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md"),
                                            ("title", "title.txt")])
def test_4025_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(publish, missing, named):
    code, out, err, fake = publish(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


def _seq(fake):
    return [(c[0], c[1][:2]) for c in fake.calls]


def _pr_call(fake):
    return next(c[1] for c in fake.calls if c[0] == "gh" and c[1][1] == "repos/{owner}/{repo}/pulls")


WAITING = {("wait-leaf.sh", None): (3, "")}


def test_4025_it_checks_scope_commits_the_ledger_alone_pushes_opens_the_draft_pr_and_posts_both_comments_in_order(
        publish):
    code, out, err, fake = publish(answers=WAITING)

    front = _seq(fake)[:15]
    assert front == [
        ("scope-check.sh", (".tdd/issue-12.md", ".")), ("ledger-steps.sh", ()), ("git", ("status", "--porcelain")),
        ("git", ("add", ".tdd/issue-12.md")), ("git", ("commit", "-m")), ("git", ("rev-parse", "HEAD")),
        ("push-branch.sh", ()), ("git", ("branch", "--show-current")),
        ("gh", ("api", "repos/{owner}/{repo}/pulls?head={owner}:tdd/12-a-thing")), ("stack-branch.sh", ()),
        ("event.sh", ("stage-start", "stage=draft-pr")), ("gh", ("api", "repos/{owner}/{repo}/pulls")),
        ("event.sh", ("stage-end", "stage=draft-pr")), ("comment.sh", ("12", "plan")),
        ("gh", ("api", "repos/{owner}/{repo}/issues/12/comments"))]
    assert fake.call("git", "commit")[1] == ("commit", "-m", "plan: scope #12 into 2 steps (#12)")
    assert fake.call("ledger-steps.sh")[4]["stdin"] == LEDGER
    assert {c[2] for c in fake.calls} == {str(publish.wt)}


def test_4025_the_draft_pr_call_is_step_2_3s_with_the_title_files_text_and_the_marked_closes_body(publish):
    code, out, err, fake = publish(answers=WAITING)

    assert _pr_call(fake) == (
        "api", "repos/{owner}/{repo}/pulls", "-F", "draft=true", "-f", "base=main", "-f", "head=tdd/12-a-thing",
        "-f", "title=" + TITLE, "-f", "body=<!-- veri:run-body -->\nCloses #12 — work in progress: 2 steps planned. "
        "The ledger .tdd/issue-12.md is the source of truth.\n<!-- /veri:run-body -->", "-q", ".html_url")


def test_4025_a_stack_branch_is_the_draft_prs_base(publish):
    code, out, err, fake = publish(answers={**WAITING, ("stack-branch.sh", None): (0, "stack\n")})

    assert _pr_call(fake)[5] == "base=stack"


def test_4025_an_existing_pr_for_the_branch_opens_no_second_one(publish):
    code, out, err, fake = publish(fake=Fake(WAITING, pr=PR_URL + "\n"))

    assert not [c for c in fake.calls if c[0] == "gh" and c[1][1] == "repos/{owner}/{repo}/pulls"]
    assert "stack-branch.sh" not in fake.names()


def test_4025_the_start_comment_names_the_branch_the_worktree_the_step_count_and_blind_verification(publish):
    code, out, err, fake = publish(answers=WAITING)

    body = next(c[1] for c in fake.calls if c[0] == "gh" and c[1][1].endswith("/comments"))[-1]
    assert body.startswith("body=")
    assert all(part in body for part in ("tdd/12-a-thing", ".tdd/wt/12", "2 steps", "blind-verified"))
    assert str(publish.wt) not in body


@pytest.mark.parametrize("failing, where", [("scope-check.sh", "2.2"), ("push-branch.sh", "2.3"),
                                            ("stack-branch.sh", "2.3"), ("comment.sh", "2.4")])
@pytest.mark.parametrize("inner", [1, 2])
def test_4025_the_first_failing_call_stops_it_with_no_later_call(publish, failing, where, inner):
    code, out, err, fake = publish(answers={(failing, None): (inner, "")})

    assert (code, fake.names()[-1]) == (inner, failing)
    assert out.splitlines()[-1].startswith("stopped at %s %s" % (where, failing))
    if failing == "scope-check.sh":
        assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]


class _Failing(Fake):
    """Fake whose gh call to <suffix> fails with exit 1."""
    suffix = None

    def __call__(self, name, *args, **kw):
        if os.path.basename(name) == "gh" and args[1].endswith(self.suffix):
            self.calls.append(("gh", args, kw.get("cwd"), kw.get("env"), kw))
            return 1, "", "HTTP 422\n"
        return super().__call__(name, *args, **kw)


def test_4025_a_failed_draft_pr_call_ends_its_stage_then_stops_at_2_3(publish):
    fake = _Failing()
    fake.suffix = "/pulls"
    code, out, err, fake = publish(fake=fake)

    assert fake.calls[-1][1][:3] == ("stage-end", "stage=draft-pr", "status=1")
    assert (code, out.splitlines()[-1].startswith("stopped at 2.3 gh api repos/{owner}/{repo}/pulls")) == (1, True)


def test_4025_a_failed_start_comment_stops_it_at_2b(publish):
    fake = _Failing()
    fake.suffix = "/comments"
    code, out, err, fake = publish(fake=fake)

    assert (code, out.splitlines()[-1].startswith("stopped at 2b gh api")) == (1, True)


@pytest.mark.parametrize("porcelain", [" M .tdd/issue-12.md\n?? stray.py\n", " M src/a.py\n"])
def test_4025_a_tree_listing_anything_but_the_ledger_before_the_plan_commit_stops_it_with_exit_1(publish, porcelain):
    code, out, err, fake = publish(fake=Fake(porcelain=porcelain))

    assert (code, out.splitlines()[-1]) == (1, "stopped at 2.2 tree-check")
    assert fake.calls[-1][:2] == ("git", ("status", "--porcelain"))


LAUNCH_TAIL = ("supervise.sh", "verdict-plan", "run-verdict.sh", "plan", ".tdd/issue-12-spec.md", ".tdd/issue-12.md")


def _after_comments(fake):
    names = fake.names()
    return fake.calls[names.index("comment.sh") + 2:]


def test_4025_it_refreshes_the_spec_checks_for_a_stop_launches_verdict_plan_waits_and_comments_on_a_pass(publish):
    (publish.wt / ".tdd" / "verdict-plan.exit").write_text("1\n")
    (publish.wt / ".tdd" / "verdict-plan.pid").write_text("99\n")
    code, out, err, fake = publish()

    tail = _after_comments(fake)
    assert code == 0
    assert [(c[0], c[1]) for c in tail[:2]] == [("refresh-spec.sh", ("12", ".tdd/issue-12-spec.md")),
                                                ("stop-requested.sh", ())]
    launch = tail[2]
    assert launch[0] == "detach-leaf.sh"
    assert tuple(os.path.basename(a) if a.endswith(".sh") else a for a in launch[1]) == LAUNCH_TAIL
    assert all(os.path.isabs(a) for a in launch[1] if a.endswith(".sh"))
    assert (launch[3]["VERI_TEST_CMD"], launch[3]["VERI_ISSUE"]) == ("make unit", "12")
    assert "VERI_STEP" not in launch[3]
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/verify-plan.reason", ".tdd/verify-plan.err")
    assert [(c[0], c[1]) for c in tail[3:]] == [("wait-leaf.sh", ("verdict-plan",)), ("comment.sh", ("12", "verify-plan"))]
    assert not (publish.wt / ".tdd" / "verdict-plan.exit").exists()
    assert not (publish.wt / ".tdd" / "verdict-plan.pid").exists()


@pytest.mark.parametrize("refresh", [2, 3])
def test_4025_refresh_spec_exits_2_and_3_go_on(publish, refresh):
    code, out, err, fake = publish(answers={("refresh-spec.sh", None): (refresh, "")})

    assert (code, "detach-leaf.sh" in fake.names()) == (0, True)


def test_4025_refresh_spec_exit_1_stops_it_before_any_launch(publish):
    code, out, err, fake = publish(answers={("refresh-spec.sh", None): (1, "")})

    assert (code, fake.names()[-1], out.splitlines()[-1]) == (
        1, "refresh-spec.sh", "stopped at 2c refresh-spec.sh 12 .tdd/issue-12-spec.md exit 1")


@pytest.mark.parametrize("code, mode, launches", [(3, "", True), (0, "at-ledger\n", True), (0, "at-leaf\n", False),
                                                  (0, "now\n", False), (2, "", False)])
def test_4025_the_stop_check_before_the_launch(publish, code, mode, launches):
    got, out, err, fake = publish(answers={("stop-requested.sh", None): (code, mode)})

    assert ("detach-leaf.sh" in fake.names()) == launches
    if not launches:
        assert (got, fake.names()[-1]) == (2 if code == 2 else 1, "stop-requested.sh")
        assert out.splitlines()[-1].startswith("stopped at 2c stop-requested.sh")


@pytest.mark.parametrize("verdict", [1, 2])
def test_4025_a_reject_or_no_verdict_stops_it_before_the_verify_plan_comment(publish, verdict):
    code, out, err, fake = publish(answers={("wait-leaf.sh", None): (verdict, "")})

    assert (code, fake.names()[-1]) == (verdict, "wait-leaf.sh")
    assert out.splitlines()[-1] == "stopped at 2c wait-leaf.sh verdict-plan exit %d" % verdict
    assert not (publish.wt / ".tdd" / "issue-12-plan-publish").exists()


def test_4025_a_failed_launch_stops_it_with_its_code(publish):
    code, out, err, fake = publish(answers={("detach-leaf.sh", None): (2, "")})

    assert (code, fake.names()[-1]) == (2, "detach-leaf.sh")


def test_4025_exit_0_settles_the_plan_sha_steps_pr_and_verdict_and_prints_them_last(publish):
    code, out, err, fake = publish()

    expected = ["plan_sha=" + PLAN_SHA, "steps=2", "pr_url=" + PR_URL, "pr_number=77", "verify_plan=PASS"]
    assert code == 0
    assert (publish.wt / ".tdd" / "issue-12-plan-publish").read_text().splitlines() == expected
    assert out.splitlines()[-len(expected):] == expected


def test_4025_the_settled_file_is_run_state_the_ignore_rule_keeps_out_of_every_commit():
    import fnmatch
    rule = importlib.import_module("veri.ensure_run_state_ignored").RULE

    for name in (".tdd/issue-12-plan-publish", ".tdd/issue-12-plan-publish-wait"):
        assert fnmatch.fnmatch(name, rule[0]) and not fnmatch.fnmatch(name, rule[1].lstrip("!"))


def test_4025_it_launches_no_leaf_but_through_supervise(publish):
    code, out, err, fake = publish()

    assert not {"run-leaf.sh", "run-verdict.sh", "claude", "supervise.sh"} & set(fake.names())


def test_4025_the_plan_commit_ends_stage_plan_when_the_conductor_started_it(publish):
    (publish.wt / ".tdd" / "stage-plan.t").write_text("1\n")
    code, out, err, fake = publish(answers=WAITING)

    end = fake.call("event.sh", "stage-end")
    assert end[1][:3] == ("stage-end", "stage=plan", "status=0")
    assert fake.calls.index(end) == fake.names().index("push-branch.sh") - 1
    assert end[3]["VERI_ISSUE"] == "12"
