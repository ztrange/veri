"""In-process cases for veri/run_start.py, the module run-start.sh is a shim over (PRD 027.13, #4024)."""
import importlib
import os

import pytest


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, porcelain=" M .gitignore\n"):
        self.answers, self.calls, self.porcelain = dict(answers or {}), [], porcelain

    def __call__(self, name, *args, cwd=None, env=None):
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


def test_4024_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_stderr_and_the_spec_goes_to_its_file(
        start):
    class Marked(Fake):
        def __call__(self, name, *args, cwd=None, env=None):
            code, out, err = super().__call__(name, *args, cwd=cwd, env=env)
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


def test_4024_a_stop_handles_no_refusal_resets_nothing_and_writes_no_bail(start):
    code, out, err, fake = start(answers={("capture-spec.sh", None): (2, "")})

    assert not {"classify-bail.sh", "preflight-refused.sh", "comment.sh", "event.sh", "gh"} & set(fake.names())
    assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] in (("reset",), ("checkout",))]


def test_4024_a_missing_preflight_file_is_exit_2_before_any_inner_call_named_on_stderr(start):
    code, out, err, fake = start(preflight=False)

    assert (code, fake.calls) == (2, [])
    assert ".tdd/issue-12-preflight" in err
