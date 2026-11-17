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


def gh_answers(head, conclusion):
    """A stub gh's body: the PR url for the branch, the PR at <head>, `gh pr ready`, and one completed check run of
    <conclusion> on the first page of check runs, the next page empty; every call appended to $CALLS."""
    runs = '{"total_count":1,"check_runs":[{"name":"ci","status":"completed","conclusion":"%s"}]}' % conclusion
    pull = '{"number":42,"state":"open","draft":false,"mergeable":true,"head":{"sha":"%s","ref":"tdd/12-thing"}}' % head
    return ('echo "$*" >> "$CALLS"\ncase "$*" in\n'
            '  *"pulls?head="*) echo %s ;;\n'
            '  *"pulls/42 --jq .head.sha"*) echo %s ;;\n'
            '  "pr ready 42") ;;\n'
            "  *check-runs?page=1) echo '%s' ;;\n"
            "  *check-runs*) echo '{\"total_count\":1,\"check_runs\":[]}' ;;\n"
            "  */status) echo '{\"state\":\"success\",\"statuses\":[]}' ;;\n"
            "  *pulls/42) echo '%s' ;;\n"
            '  *) exit 1 ;;\nesac\n' % (URL, head, runs, pull))


@pytest.mark.process("git, pr-ready.sh and wait-ci.sh, all real, against a stub gh")
@pytest.mark.parametrize("conclusion, code", [("success", 0), ("failure", 1)])
def test_4032_the_pr_is_readied_once_and_its_ci_waited_on_for_real(tmp_path, run_cli, conclusion, code):
    pr_ready_wait = importlib.import_module("veri.pr_ready_wait")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    git_env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t", "PATH": os.environ["PATH"]}
    for args in (["init", "-q", "-b", "tdd/12-thing"], ["commit", "-q", "--allow-empty", "-m", "one"]):
        subprocess.run(["git", *args], cwd=wt, capture_output=True, check=True, timeout=60, env=git_env)
    (wt / ".git" / "info" / "exclude").write_text(".tdd/\n")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt, capture_output=True, text=True, check=True,
                          timeout=60).stdout.strip()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(bin_dir / "gh", gh_answers(head, conclusion))
    calls = tmp_path / "calls"
    calls.write_text("")

    out_code, out, err = run_cli(pr_ready_wait, ["12"], cwd=str(tmp_path),
                                 env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"], "CALLS": str(calls),
                                      "VERI_GH_DRIVER": "auto", "VERI_POLL": "0", "VERI_CI_ON_PR": "1"})

    made = calls.read_text().splitlines()
    assert out_code == code, out + err
    assert made.count("pr ready 42") == 1
    if code == 0:
        assert out.splitlines()[-3:] == ["pr_url=" + URL, "pr_number=42", "ci=green"]
    else:
        assert out.splitlines()[-1].startswith("stopped at 2 wait-ci.sh %s 540  %s" % (URL, head))
        assert "ci" in (wt / ".tdd" / "wait-ci.out").read_text()
