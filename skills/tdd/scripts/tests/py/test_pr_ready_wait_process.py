"""Cases for pr-ready-wait.sh (PRD 027.10, #4032) that start a real process: the shim's usage, and the PR readied and
its CI waited on by the real pr-ready.sh and wait-ci.sh, against a stub gh."""
import importlib
import os
import subprocess

import pytest

from conftest import SCRIPTS
from stub_script import write_stub

URL = "https://github.com/o/r/pull/42"


@pytest.mark.process("pr-ready-wait.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_4032_the_shim_with_no_argument_prints_its_usage_and_exits_2(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "pr-ready-wait.sh")], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: pr-ready-wait.sh <n>\n")


def gh_answers(conclusion):
    """A stub gh's body: the PR url for the branch, the PR at the remote branch's head ($REMOTE), `gh pr ready`, and one
    completed check run of <conclusion> on the first page of check runs, the next page empty; every call appended to
    $CALLS."""
    runs = '{"total_count":1,"check_runs":[{"name":"ci","status":"completed","conclusion":"%s"}]}' % conclusion
    pull = '{"number":42,"state":"open","draft":false,"mergeable":true,"head":{"sha":"%s","ref":"tdd/12-thing"}}'
    return ('echo "$*" >> "$CALLS"\nhead=$(git --git-dir="$REMOTE" rev-parse tdd/12-thing)\ncase "$*" in\n'
            '  *"pulls?head="*) echo %s ;;\n'
            '  *"pulls/42 --jq .head.sha"*) echo "$head" ;;\n'
            '  "pr ready 42") ;;\n'
            "  *check-runs?page=1) echo '%s' ;;\n"
            "  *check-runs*) echo '{\"total_count\":1,\"check_runs\":[]}' ;;\n"
            "  */status) echo '{\"state\":\"success\",\"statuses\":[]}' ;;\n"
            "  *pulls/42) printf '%s\\n' \"$head\" ;;\n"
            '  *) exit 1 ;;\nesac\n' % (URL, runs, pull))


@pytest.mark.process("git with a bare remote, event.sh, metrics.sh, push-branch.sh, pr-ready.sh and wait-ci.sh, all "
                     "real, against a stub gh")
@pytest.mark.parametrize("conclusion, code", [("success", 0), ("failure", 1)])
def test_4032_the_pr_is_readied_once_and_its_ci_waited_on_for_real(tmp_path, run_cli, conclusion, code):
    pr_ready_wait = importlib.import_module("veri.pr_ready_wait")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    git_env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t", "PATH": os.environ["PATH"]}
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], cwd=tmp_path, capture_output=True, check=True,
                   timeout=60)
    subprocess.run(["git", "init", "-q", "-b", "tdd/12-thing"], cwd=wt, capture_output=True, check=True, timeout=60)
    (wt / ".git" / "info" / "exclude").write_text(".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-*.md\n"
                                                  "!.tdd/issue-*-metrics.md\n")
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n")
    for args in (["add", "-A"], ["commit", "-q", "-m", "one"], ["remote", "add", "origin", str(remote)],
                 ["push", "-q", "origin", "tdd/12-thing"]):
        subprocess.run(["git", *args], cwd=wt, capture_output=True, check=True, timeout=60, env=git_env)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(bin_dir / "gh", gh_answers(conclusion))
    calls = tmp_path / "calls"
    calls.write_text("")

    out_code, out, err = run_cli(pr_ready_wait, ["12"], cwd=str(tmp_path),
                                 env=dict(git_env, PATH=str(bin_dir) + os.pathsep + os.environ["PATH"],
                                          CALLS=str(calls), REMOTE=str(remote), VERI_GH_DRIVER="auto", VERI_POLL="0",
                                          VERI_CI_ON_PR="1"))

    made = calls.read_text().splitlines()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt, capture_output=True, text=True, check=True,
                          timeout=60).stdout.strip()
    assert out_code == code, out + err
    assert made.count("pr ready 42") == 1
    if code == 0:
        assert out.splitlines()[-3:] == ["pr_url=" + URL, "pr_number=42", "ci=green"]
    else:
        assert out.splitlines()[-1].startswith("stopped at 2 wait-ci.sh %s 540  %s" % (URL, head))
        assert "ci" in (wt / ".tdd" / "wait-ci.out").read_text()
