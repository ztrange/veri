"""Cases for step-close.sh (PRD 027.8, #4029) that start a real process: the shim's usage, and the clear, the
`chore: refactor verified` commit and its push made by the real clear-refactor-pending.sh, git and push-branch.sh."""
import importlib
import os
import subprocess

import pytest

from conftest import SCRIPTS

STEP = "one thing works ⟦criterion 1⟧"
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@example.com"}
REAL = ("git", "clear-refactor-pending.sh", "push-branch.sh", "next-unchecked.sh", "ledger-steps.sh")


@pytest.mark.process("step-close.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_4029_the_shim_with_no_argument_prints_its_usage_and_exits_2(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "step-close.sh")], cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True,
                         text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: step-close.sh <n>\n")


@pytest.mark.process("step-close's clear, git add and commit, and push-branch.sh to a bare origin, all real")
def test_4029_the_clear_commit_and_push_land_the_cleared_ledger_and_the_owed_file_on_origin(
        tmp_path, monkeypatch, run_cli):
    fused = importlib.import_module("veri.fused")
    step_close = importlib.import_module("veri.step_close")
    real = fused.run_script
    env = {**os.environ, **IDENTITY}

    def git(*args, cwd):
        return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True,
                              timeout=60).stdout

    origin = tmp_path / "origin.git"
    git("init", "-q", "--bare", str(origin), cwd=tmp_path)
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    rule = importlib.import_module("veri.ensure_run_state_ignored").RULE
    (wt / ".gitignore").write_text("".join(line + "\n" for line in rule))
    for args in (["init", "-q", "-b", "work"], ["add", "-A"], ["commit", "-q", "-m", "plan"]):
        git(*args, cwd=wt)
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] %s ⟂ refactor pending\n- [ ] two\n" % STEP)
    for args in (["add", "-f", ".tdd/issue-12.md"], ["commit", "-q", "-m", "green"],
                 ["remote", "add", "origin", str(origin)], ["push", "-q", "-u", "origin", "work"]):
        git(*args, cwd=wt)
    green = git("rev-parse", "HEAD", cwd=wt).strip()
    (wt / ".tdd" / "issue-12-refactor-owed.md").write_text("## one thing works\n\n- structural | split g\n")
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-refactor-half").write_text("step=%s\ngreen_sha=%s\nverdict_log=none\n" % (STEP, green))
    (wt / ".tdd" / "stage-rl.t").write_text("100\n")

    def answer(name, *args, **kw):
        base = os.path.basename(name)
        if base in REAL:
            return real(name, *args, **kw)
        return {"stop-requested.sh": (3, "", ""), "criterion-finished.sh": (3, "", ""),
                "run-affordable.sh": (0, "", "")}.get(base, (0, "", ""))

    monkeypatch.setattr(fused, "run_script", answer)
    code, out, err = run_cli(step_close, ["12"], cwd=str(tmp_path), env={**IDENTITY, "VERI_ISSUE": "12"})

    assert code == 0, out + err
    assert git("log", "-1", "--format=%s", cwd=wt) == "chore: refactor verified for one thing works (#12)\n"
    assert sorted(git("show", "--name-only", "--format=", "HEAD", cwd=wt).split()) == [
        ".tdd/issue-12-refactor-owed.md", ".tdd/issue-12.md"]
    assert "- [x] %s\n" % STEP in git("show", "HEAD:.tdd/issue-12.md", cwd=wt)
    assert git("rev-parse", "work", cwd=origin) == git("rev-parse", "HEAD", cwd=wt)
    assert out.splitlines()[-1] == "next=cycle"
    assert git("status", "--porcelain", cwd=wt) == ""
