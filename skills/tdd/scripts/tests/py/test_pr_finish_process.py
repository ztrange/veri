"""Cases for pr-finish.sh (PRD 027.11, #4033) that start a real process: the shim's usage, and the ⟦full-suite⟧ tick,
the done mark, the metrics commit, the push to a real remote and the second CI wait made by the real scripts, against a
stub gh."""
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
    the remote branch's head, and one green check run on the first page of check runs; every call appended to
    $CALLS."""
    pull = '{"number":42,"state":"open","draft":false,"mergeable":true,"head":{"sha":"%s","ref":"work"}}'
    return ('echo "$*" >> "$CALLS"\nhead=$(git --git-dir="$REMOTE" rev-parse work 2>/dev/null)\ncase "$*" in\n'
            '  *"pulls?head="*) echo %s ;;\n'
            '  *"-X PATCH"*issues/12*body=@*) for a; do case $a in body=@*) cp "${a#body=@}" %s ;; esac; done ;;\n'
            '  *issues/12*|"issue view 12"*) cat %s ;;\n'
            "  *check-runs?page=1) echo '{\"total_count\":1,\"check_runs\":[{\"name\":\"ci\",\"status\":\"completed\","
            "\"conclusion\":\"success\"}]}' ;;\n"
            "  *check-runs*) echo '{\"total_count\":1,\"check_runs\":[]}' ;;\n"
            "  */status) echo '{\"state\":\"success\",\"statuses\":[]}' ;;\n"
            "  *pulls/42) printf '%s\\n' \"$head\" ;;\n"
            '  *) exit 1 ;;\nesac\n' % (URL, body_file, body_file, pull))


@pytest.mark.process("git with a bare remote, branch-suite.sh, tick-ledger.sh, tick-issue-criterion.sh, event.sh, "
                     "metrics.sh, push-branch.sh, wait-ci.sh and refactor-owed.sh, all real, against a stub gh")
def test_4033_the_tick_mark_metrics_commit_push_and_wait_are_made_for_real(tmp_path, run_cli):
    pr_finish = importlib.import_module("veri.pr_finish")
    wt, remote = tmp_path / ".tdd" / "wt" / "12", tmp_path / "remote.git"
    (wt / ".tdd").mkdir(parents=True)
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")

    def git(*args, cwd=wt):
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True, timeout=60,
                              env=env).stdout.strip()

    git("init", "-q", "--bare", str(remote), cwd=tmp_path)
    git("init", "-q", "-b", "work")
    (wt / ".gitignore").write_text(IGNORE)
    (wt / ".tdd" / "issue-12.md").write_text(LEDGER)
    git("add", "-A")
    git("commit", "-q", "-m", "plan")
    git("remote", "add", "origin", str(remote))
    git("push", "-q", "origin", "work")
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    body = tmp_path / "body"
    body.write_text(BODY)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(bin_dir / "gh", gh_answers(body))
    calls = tmp_path / "calls"
    calls.write_text("")

    code, out, err = run_cli(pr_finish, ["12"], cwd=str(tmp_path), env={
        "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"], "CALLS": str(calls), "REMOTE": str(remote),
        "VERI_GH_DRIVER": "auto", "VERI_POLL": "0", "VERI_BRANCH_SUITE": "ci", "VERI_CI_HEAD_WAIT": "0", "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})

    assert code == 0, out + err + calls.read_text()
    assert git("log", "--format=%s").splitlines()[:2] == ["metrics: what solving #12 cost (#12)",
                                                          "plan: the full suite is green on CI (#12)"]
    assert git("rev-parse", "work", cwd=remote) == git("rev-parse", "HEAD")
    assert "- [x] the full suite is green ⟦full-suite⟧" in (wt / ".tdd" / "issue-12.md").read_text()
    assert "- [x] the full suite is green" in body.read_text()
    marks = [json.loads(line) for line in (wt / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(m["event"], m.get("pr")) for m in marks if m["event"] == "done"] == [("done", URL)]
    assert out.splitlines()[-1] == "refactor_owed_render=.tdd/issue-12-refactor-owed-render"
