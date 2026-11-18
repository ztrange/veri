"""Cases for pr-finish.sh (PRD 027.11, #4033) that start a real process: the shim's usage, and the ⟦full-suite⟧ tick,
the done mark, the metrics commit and the push to a real remote that pr-ready-wait.sh makes before readying (#4332),
made by the real scripts, against a stub gh."""
import importlib
import json
import os
import subprocess

import pytest

from conftest import SCRIPTS
from stub_script import write_stub

URL = "https://github.com/o/r/pull/42"
LEDGER = "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n- [ ] the full suite is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
BODY = "## Acceptance criteria\n\n- [x] one\n- [ ] the full suite is green\n"
IGNORE = ".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-*.md\n!.tdd/issue-*-metrics.md\n"


@pytest.mark.process("pr-finish.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_4033_the_shim_with_no_argument_prints_its_usage_and_exits_2(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "pr-finish.sh")], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: pr-finish.sh <n>\n")


def gh_answers(body_file):
    """A stub gh's body: the PR url for the branch, the issue body held in <body_file> (an edit rewrites it), the PR at
    the remote branch's head, `gh pr ready` (appending `ready at: <the remote branch head's subject>`), and one green
    check run on the first page of check runs; every call appended to $CALLS."""
    pull = '{"number":42,"state":"open","draft":false,"mergeable":true,"head":{"sha":"%s","ref":"work"}}'
    return ('echo "$*" >> "$CALLS"\nhead=$(git --git-dir="$REMOTE" rev-parse work 2>/dev/null)\ncase "$*" in\n'
            '  *"pulls?head="*) echo %s ;;\n'
            '  *"-X PATCH"*issues/12*body=@*) for a; do case $a in body=@*) cp "${a#body=@}" %s ;; esac; done ;;\n'
            '  *issues/12/comments*) echo https://github.com/o/r/issues/12#issuecomment-1 ;;\n'
            '  *issues/12*|"issue view 12"*) cat %s ;;\n'
            '  "pr ready 42") git --git-dir="$REMOTE" log -1 --format="ready at: %%s" work >> "$CALLS" ;;\n'
            '  *"pulls/42 --jq .head.sha"*) echo "$head" ;;\n'
            "  *check-runs?page=1) echo '{\"total_count\":1,\"check_runs\":[{\"name\":\"ci\",\"status\":\"completed\","
            "\"conclusion\":\"success\"}]}' ;;\n"
            "  *check-runs*) echo '{\"total_count\":1,\"check_runs\":[]}' ;;\n"
            "  */status) echo '{\"state\":\"success\",\"statuses\":[]}' ;;\n"
            "  *pulls/42) printf '%s\\n' \"$head\" ;;\n"
            '  *) exit 1 ;;\nesac\n' % (URL, body_file, body_file, pull))


class Run:
    """A run's worktree at .tdd/wt/12 on branch `work`, its ledger committed and pushed to a bare remote, no
    .tdd/wait-ci.err, and a stub gh; run(answer=None, module="pr_finish") runs pr-finish (or the veri
    <module> named) for issue 12, <answer> standing in for fused.run_script, and returns (code, stdout, stderr)."""

    def __init__(self, tmp_path, run_cli):
        self.tmp, self.run_cli = tmp_path, run_cli
        self.wt, self.remote = tmp_path / ".tdd" / "wt" / "12", tmp_path / "remote.git"
        (self.wt / ".tdd").mkdir(parents=True)
        self.env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                        GIT_COMMITTER_EMAIL="t@t")
        self.git("init", "-q", "--bare", str(self.remote), cwd=tmp_path)
        self.git("init", "-q", "-b", "work")
        (self.wt / ".gitignore").write_text(IGNORE)
        (self.wt / ".tdd" / "issue-12.md").write_text(LEDGER)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "plan")
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "-q", "origin", "work")
        (self.wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % self.wt)
        self.body = tmp_path / "body"
        self.body.write_text(BODY)
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        write_stub(bin_dir / "gh", gh_answers(self.body))
        self.calls = tmp_path / "calls"
        self.calls.write_text("")
        self.path = str(bin_dir) + os.pathsep + os.environ["PATH"]

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.wt, capture_output=True, text=True, check=True,
                              timeout=60, env=self.env).stdout.strip()

    def environ(self):
        return {"PATH": self.path, "CALLS": str(self.calls), "REMOTE": str(self.remote), "VERI_GH_DRIVER": "auto",
                "VERI_POLL": "0", "VERI_BRANCH_SUITE": "ci", "VERI_CI_HEAD_WAIT": "0", "GIT_AUTHOR_NAME": "t",
                "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    def run(self, monkeypatch, answer=None, module="pr_finish"):
        if answer is not None:
            monkeypatch.setattr(importlib.import_module("veri.fused"), "run_script", answer)
        return self.run_cli(importlib.import_module("veri." + module), ["12"], cwd=str(self.tmp), env=self.environ())


@pytest.mark.process("pr-ready-wait.sh's /bin/sh shim, with git, a bare remote and every inner script real, against a "
                     "stub gh")
def test_4332_the_shim_pushes_the_metrics_commit_before_it_readies_the_pr(tmp_path, run_cli):
    run = Run(tmp_path, run_cli)

    ran = subprocess.run([str(SCRIPTS / "pr-ready-wait.sh"), "12"], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=60, env=dict(os.environ, **run.environ()))

    readied = [line for line in run.calls.read_text().splitlines() if line.startswith("ready at: ")]
    assert (ran.returncode, readied) == (0, ["ready at: metrics: what solving #12 cost (#12)"]), ran.stdout + ran.stderr


@pytest.mark.process("git with a bare remote, branch-suite.sh, tick-ledger.sh, tick-issue-criterion.sh, event.sh, "
                     "metrics.sh, push-branch.sh, pr-ready.sh, wait-ci.sh and refactor-owed.sh, all real, against a "
                     "stub gh")
def test_4033_the_tick_mark_metrics_commit_push_and_wait_are_made_for_real(tmp_path, run_cli, monkeypatch):
    run = Run(tmp_path, run_cli)
    wt, git = run.wt, run.git

    code, out, err = run.run(monkeypatch, module="pr_ready_wait")

    assert code == 0, out + err + run.calls.read_text()
    assert git("log", "--format=%s").splitlines()[:2] == ["metrics: what solving #12 cost (#12)",
                                                          "plan: the full suite is owed to CI (#12)"]
    assert git("rev-parse", "work", cwd=run.remote) == git("rev-parse", "HEAD")
    assert "- [x] the full suite is green ⟦full-suite⟧" in (wt / ".tdd" / "issue-12.md").read_text()
    assert "- [x] the full suite is green" in run.body.read_text()
    marks = [json.loads(line) for line in (wt / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(m["event"], m.get("pr")) for m in marks if m["event"] == "done"] == [("done", URL)]
    head = git("rev-parse", "HEAD")
    code, out, err = run.run(monkeypatch)
    assert (code, out.splitlines()[-1]) == (0, "refactor_owed_render=.tdd/issue-12-refactor-owed-render"), out + err
    assert (git("rev-parse", "HEAD"), git("rev-parse", "work", cwd=run.remote)) == (head, head)


@pytest.mark.process("git with a bare remote and every inner script real but metrics.sh, a stub that writes its file "
                     "and exits 1, against a stub gh")
def test_4033_a_failed_metrics_render_that_left_its_file_commits_nothing_and_goes_on_for_real(tmp_path, run_cli,
                                                                                               monkeypatch):
    fused = importlib.import_module("veri.fused")
    run = Run(tmp_path, run_cli)
    stub = write_stub(tmp_path / "metrics.sh", 'echo "half a report"\nexit 1\n')
    real = fused.run_script

    def answer(name, *args, **kw):
        return real(str(stub) if os.path.basename(name) == "metrics.sh" else name, *args, **kw)

    code, out, err = run.run(monkeypatch, answer, module="pr_ready_wait")

    assert code == 0, out + err
    assert "metrics=1" in out.splitlines()[-3:]
    assert "metrics:" not in run.git("log", "--format=%s")
    assert run.git("rev-parse", "work", cwd=run.remote) == run.git("rev-parse", "HEAD")


@pytest.mark.process("pr-ready-wait.sh with metrics.sh a stub that writes its file and exits 1, then pr-finish.sh, "
                     "then run-done.sh with the real stop-requested.sh and comment.sh, against a stub gh")
def test_4033_4034_the_file_a_failed_metrics_render_left_does_not_stop_run_done_for_real(tmp_path, run_cli,
                                                                                       monkeypatch):
    fused = importlib.import_module("veri.fused")
    run_done = importlib.import_module("veri.run_done")
    run = Run(tmp_path, run_cli)
    stub = write_stub(tmp_path / "metrics.sh", 'echo "half a report"\nexit 1\n')
    real = fused.run_script

    def answer(name, *args, **kw):
        return real(str(stub) if os.path.basename(name) == "metrics.sh" else name, *args, **kw)

    assert run.run(monkeypatch, answer, module="pr_ready_wait")[0] == 0
    assert run.run(monkeypatch)[0] == 0
    code, out, err = run_cli(run_done, ["12"], cwd=str(tmp_path), env={
        "PATH": run.path, "CALLS": str(run.calls), "REMOTE": str(run.remote), "VERI_GH_DRIVER": "auto"})

    assert code == 0, out + err
    assert out.splitlines()[-2:] == ["stop_requested=3", "cleared=0"]
    assert "issues/12/comments" in run.calls.read_text()
