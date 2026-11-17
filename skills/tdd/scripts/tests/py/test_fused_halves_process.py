"""Cases for red-half.sh, green-half.sh and refactor-half.sh (PRD 027.4-027.6) that start a real process: each shim's
usage, and green-half's tick-and-commit made by a real git."""
import importlib
import os
import subprocess

import pytest

from conftest import SCRIPTS

STEP = "one thing works ⟦criterion 1⟧"
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@example.com"}


@pytest.mark.process("each fused half's /bin/sh shim exec'd on the interpreter with no argument")
@pytest.mark.parametrize("shim", ["red-half.sh", "green-half.sh", "refactor-half.sh"])
def test_4026_4027_4028_each_shim_with_no_argument_prints_its_usage_and_exits_2(tmp_path, shim):
    ran = subprocess.run([str(SCRIPTS / shim)], cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True,
                         text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: %s <n>\n" % shim)


@pytest.mark.process("green-half's git status, add, commit and rev-parse run by a real git in a real repository")
def test_4027_the_tick_and_commit_lands_the_code_and_the_ticked_ledger_in_one_commit_with_the_step_subject(
        tmp_path, monkeypatch, run_cli):
    fused = importlib.import_module("veri.fused")
    green_half = importlib.import_module("veri.green_half")
    real = fused.run_script
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    rule = importlib.import_module("veri.ensure_run_state_ignored").RULE
    (wt / ".gitignore").write_text("".join(line + "\n" for line in rule))
    (wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [ ] %s\n" % STEP)
    env = {**os.environ, **IDENTITY}
    for args in (["init", "-q"], ["add", "-A"], ["add", "-f", ".tdd/issue-12.md"], ["commit", "-q", "-m", "plan"]):
        subprocess.run(["git", *args], cwd=wt, env=env, capture_output=True, check=True, timeout=60)
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("# spec\n\n## Bug\n\nit breaks\n")
    (wt / ".tdd" / "issue-12-red-half").write_text("step=%s\ntest_path=t.py\ntarget_test=t.py::test_a\n" % STEP)
    (wt / ".tdd" / "develop-green.out").write_text("{}\n")
    (wt / "a.py").write_text("x = 1\n")

    def answer(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        if base == "git":
            return real(name, *args, cwd=cwd, env=env, **kw)
        if base == "tick-ledger.sh":
            path = os.path.join(cwd, args[1])
            with open(path) as f:
                text = f.read()
            with open(path, "w") as f:
                f.write(text.replace("- [ ] " + STEP, "- [x] " + STEP + " ⟂ refactor pending"))
            return 0, "", ""
        return {"extract-result.sh": (0, "SUITE: GREEN\n"), "stop-requested.sh": (3, ""), "step-cost.sh": (3, ""),
                "gh": (0, "https://github.com/o/r/pull/7\n")}.get(base, (0, ""))[0:2] + ("",)

    monkeypatch.setattr(fused, "run_script", answer)
    code, out, err = run_cli(green_half, ["12"], cwd=str(tmp_path), env=IDENTITY)

    def git(*args):
        return subprocess.run(["git", *args], cwd=wt, capture_output=True, text=True, check=True, timeout=60).stdout

    assert code == 0, out + err
    assert git("log", "-1", "--format=%s") == "fix: one thing works (#12)\n"
    assert sorted(git("show", "--name-only", "--format=", "HEAD").split()) == [".tdd/issue-12.md", "a.py"]
    assert "- [x] %s ⟂ refactor pending" % STEP in git("show", "HEAD:.tdd/issue-12.md")
    assert "green_sha=" + git("rev-parse", "HEAD").strip() in out.splitlines()
    assert git("status", "--porcelain") == ""
