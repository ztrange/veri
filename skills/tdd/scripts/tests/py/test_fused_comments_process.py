"""run-start.sh then plan-publish.sh through their shims, on a real git repository with a stub gh: what reaches GitHub
from the plan comment and step 2b's start comment carries no local absolute path, account name or host name."""
import getpass
import os
import pathlib
import socket
import subprocess

import pytest

from stub_script import write_stub

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]

ISSUE_BODY = """## What

A widget.

## Acceptance criteria

- [ ] the widget answers
"""

LEDGER = """# Issue 12: a widget

- [ ] the widget answers ⟦criterion 1⟧
"""

# Every call is logged as its arguments, then a line `--stdin--`, then what it read on stdin, in its own file.
GH = """n=$(ls "$GH_LOG" | wc -l | tr -d ' ')
f="$GH_LOG/call-$n"
printf '%s\\n' "$@" > "$f"
echo --stdin-- >> "$f"
[ -t 0 ] || cat >> "$f"
case "$*" in
  *pulls\\?head=*) ;;
  *draft=true*) echo https://github.com/o/r/pull/34 ;;
  *comments*) echo https://github.com/o/r/issues/12#issuecomment-1 ;;
  *labels*) echo feature ;;
  *body*) cat "$GH_ISSUE_BODY" ;;
esac
exit 0
"""


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, stdin=subprocess.DEVNULL)


@pytest.mark.process("run-start.sh and plan-publish.sh through their shims on a real git repository, gh a stub")
def test_4025_the_plan_and_start_comments_that_reach_gh_carry_no_local_path_account_or_host_name(tmp_path):
    bin_dir, log = tmp_path / "bin", tmp_path / "gh-log"
    bin_dir.mkdir()
    log.mkdir()
    write_stub(bin_dir / "gh", GH)
    (tmp_path / "issue.md").write_text(ISSUE_BODY)
    git(tmp_path, "init", "-q", "--bare", "-b", "main", "remote.git")
    wt = tmp_path / "wt"
    git(tmp_path, "init", "-q", "-b", "main", "wt")
    (wt / "CLAUDE.md").write_text("veri: fast tests: true\n")
    env = dict(os.environ, PATH="%s:%s" % (bin_dir, os.environ["PATH"]), GH_LOG=str(log),
               GH_ISSUE_BODY=str(tmp_path / "issue.md"), VERI_GH_DRIVER="auto",
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@example.invalid")
    for args in (("add", "CLAUDE.md"), ("commit", "-qm", "init"), ("remote", "add", "origin", str(tmp_path / "remote.git")),
                 ("push", "-q", "origin", "main"), ("checkout", "-qb", "feature-12")):
        subprocess.run(["git", *args], cwd=wt, env=env, check=True, capture_output=True, stdin=subprocess.DEVNULL)
    (wt / ".tdd").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text(
        "worktree=%s\nbaseline=5\nfull=10\nfast_cmd=true\ndefault_branch=main\n" % wt)

    def run(*argv):
        ran = subprocess.run([str(SCRIPTS / argv[0]), *argv[1:]], cwd=wt, env=env, capture_output=True, text=True,
                             stdin=subprocess.DEVNULL)
        return ran.returncode, ran.stdout, ran.stderr

    started = run("run-start.sh", "12")
    (wt / ".tdd" / "issue-12.md").write_text(LEDGER)
    (tmp_path / "title").write_text("WIP: feat: the widget answers (#12)\n")
    (wt / ".tdd" / "stop").write_text("now\n")
    published = run("plan-publish.sh", "12", str(tmp_path / "title"))

    calls = [p.read_text() for p in sorted(log.iterdir())]
    comments = [c for c in calls if "/comments" in c]
    assert started[0] == 0, started
    assert published[1].splitlines()[-1].startswith("stopped at 2c "), published
    assert [any("veri started" in c for c in comments), any("comment.sh" in c or "Plan" in c for c in comments)] \
        == [True, True], comments
    private = {str(tmp_path), os.path.realpath(tmp_path), os.path.expanduser("~"), getpass.getuser(),
               socket.gethostname().split(".")[0]}
    assert [(word, c) for c in comments for word in private if word and word in c] == []
