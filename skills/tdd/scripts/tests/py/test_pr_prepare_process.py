"""Cases for pr-prepare.sh (PRD 027.9, #4031) that start a real process: the shim's usage, and the rebase onto a moved
default branch, the rebased tip's local run and the push under the lease pinned to the pre-rebase sha, made by the
real rebase-onto-default.sh, detach-command.sh start and wait, push-branch.sh and git."""
import importlib
import os
import subprocess

import pytest

from conftest import SCRIPTS
from stub_script import write_stub

IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@example.com"}
LEDGER = "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n"
REAL = ("git", "next-pending-refactor.sh", "rebase-onto-default.sh", "push-branch.sh", "detach-command.sh")


@pytest.mark.process("pr-prepare.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_4031_the_shim_with_no_argument_prints_its_usage_and_exits_2(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "pr-prepare.sh")], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: pr-prepare.sh <n>\n")


@pytest.mark.process("rebase-onto-default.sh, push-branch.sh --force-with-lease, detach-command.sh start and wait "
                      "and git against a bare origin, all real")
@pytest.mark.parametrize("mode, status", [("ci", 0), ("local", 0), ("local", 1)],
                         ids=["ci", "a local green run", "a local red run"])
def test_4031_a_branch_behind_main_is_rebased_and_pushed_under_the_lease_pinned_to_its_pre_rebase_sha(
        tmp_path, monkeypatch, run_cli, mode, status):
    fused = importlib.import_module("veri.fused")
    pr_prepare = importlib.import_module("veri.pr_prepare")
    real = fused.run_script
    env = {**os.environ, **IDENTITY}

    def git(*args, cwd):
        return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True,
                              timeout=60).stdout

    origin, other = tmp_path / "origin.git", tmp_path / "other"
    git("init", "-q", "--bare", "-b", "main", str(origin), cwd=tmp_path)
    git("clone", "-q", str(origin), str(other), cwd=tmp_path)
    (other / "base.txt").write_text("base\n")
    for args in (["add", "-A"], ["commit", "-q", "-m", "base"], ["push", "-q", "origin", "HEAD:main"]):
        git(*args, cwd=other)
    wt = tmp_path / ".tdd" / "wt" / "12"
    git("clone", "-q", str(origin), str(wt), cwd=tmp_path)
    rule = importlib.import_module("veri.ensure_run_state_ignored").RULE
    (wt / ".gitignore").write_text("".join(line + "\n" for line in rule))
    (wt / ".tdd").mkdir()
    (wt / ".tdd" / "issue-12.md").write_text(LEDGER)
    (wt / "work.txt").write_text("work\n")
    for args in (["checkout", "-q", "-b", "tdd/12-x"], ["add", "-A"], ["add", "-f", ".tdd/issue-12.md"],
                 ["commit", "-q", "-m", "work"], ["push", "-q", "-u", "origin", "tdd/12-x"]):
        git(*args, cwd=wt)
    pre = git("rev-parse", "HEAD", cwd=wt).strip()
    (other / "moved.txt").write_text("moved\n")
    for args in (["add", "-A"], ["commit", "-q", "-m", "main moved"], ["push", "-q", "origin", "HEAD:main"]):
        git(*args, cwd=other)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)

    def answer(name, *args, **kw):
        base = os.path.basename(name)
        if base in REAL:
            return real(name, *args, **kw)
        return {"rebased-tip-suite.sh": (0, mode + "\n", ""), "refactor-owed.sh": (3, "", ""),
                "detect-test-command.sh": (0, "sh -c 'echo suite-said-%d; exit %d'\n" % (status, status), "")}.get(
                    base, (0, "", ""))

    monkeypatch.setattr(fused, "run_script", answer)
    code, out, err = run_cli(pr_prepare, ["12"], cwd=str(tmp_path),
                             env={**IDENTITY, "VERI_ISSUE": "12", "VERI_POLL": "0.05"})

    assert code == status, out + err
    if status:
        assert out.splitlines()[-1] == "stopped at 1 detach-command.sh wait rebased-full-12 exit %d" % status
        assert "suite-said-%d" % status in (wt / ".tdd" / "rebased-full-12.out").read_text()
        assert git("rev-parse", "tdd/12-x", cwd=origin).strip() == pre
        return
    assert out.endswith("rebased=1\nrebased_from=%s\nrebased_tip_suite=%s\n" % (pre, mode))
    assert ("detach-command.sh wait rebased-full-12 exit 0" in out) == (mode == "local")
    assert "push-branch.sh --force-with-lease=tdd/12-x:%s exit 0" % pre in out
    tip = git("rev-parse", "HEAD", cwd=wt).strip()
    assert tip != pre and git("rev-parse", "tdd/12-x", cwd=origin).strip() == tip
    assert git("merge-base", "--is-ancestor", git("rev-parse", "main", cwd=origin).strip(), tip, cwd=wt) == ""
    assert git("status", "--porcelain", cwd=wt) == ""


@pytest.mark.process("pr_prepare.BLOCK run by a real sh over a stub grade-prose.sh")
@pytest.mark.parametrize("codes, highest", [({}, 0), ({"a/U.md": 1}, 1), ({"b/V.md": 2, "a/U.md": 1}, 2),
                                            ({"a/U.md": 2, "b/V.md": 1}, 2),
                                            ({"--convert": 2, "a/U.md": 1}, 2), ({"a/U.md": 2, "--convert": 1}, 2)],
                         ids=["all pass", "one reject", "the highest of two", "the highest first", "convert highest", "convert lower"])
def test_4390_the_detached_regrade_block_grades_each_unit_then_converts_and_exits_its_highest_code(
        tmp_path, codes, highest):
    pr_prepare = importlib.import_module("veri.pr_prepare")
    write_stub(tmp_path / "grade-prose.sh", 'echo "$*" >> "%s"\ncase "$*" in\n%s\nesac\nexit 0\n' % (
        tmp_path / "graded", "\n".join('  *"%s") exit %d ;;' % (k, v) for k, v in codes.items())))
    ran = subprocess.run(["sh", "-c", pr_prepare.BLOCK, "sh", str(tmp_path), "a/REQUIREMENTS.md", "a/U.md",
                          "b/REQUIREMENTS.md", "b/V.md"], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=60)

    assert ran.returncode == highest, ran.stderr
    assert (tmp_path / "graded").read_text() == "a/REQUIREMENTS.md a/U.md\nb/REQUIREMENTS.md b/V.md\n--convert\n"
