"""Cases for SKILL.md's first CI-wait block against a real rebase-onto-default.sh and a real git repository."""
import os
import subprocess
from pathlib import Path

import pytest

from conftest import INTERPRETER_VENV
from test_skill_ci_conflict import NO_STEP, _ci_step, _first_block

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("SKILL.md's first CI-wait block runs under bash -c in a git repo with a bare origin, the real rebase-onto-default.sh and stub scripts")
def test_issue_2706_a_graded_only_conflict_with_the_marker_already_present_rebases_and_records_no_bail(tmp_path):
    step = _ci_step()
    assert step.strip(), NO_STEP
    block = _first_block(step)
    assert block.strip(), "no first CI-wait block in the CI step — nothing could be run"
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stubs = {"wait-ci.sh": '#!/bin/sh\necho "PR conflicts with its base branch" >&2\nexit 2\n',
             "event.sh": '#!/bin/sh\necho "$*" >> events.log\n',
             "classify-bail.sh": '#!/bin/sh\necho "$1"\n',
             "ledger-steps.sh": "#!/bin/sh\nexit 0\n",
             "pr-ready.sh": "#!/bin/sh\nexit 0\n",
             "gh": "#!/bin/sh\nexit 0\n",
             "rebase-onto-default.sh": f'#!/bin/sh\nexec "{SCRIPTS / "rebase-onto-default.sh"}" "$@"\n'}
    for name, body in stubs.items():
        (bin_dir / name).write_text(body)
        (bin_dir / name).chmod(0o755)
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def line(unit, digit):
        return f"guide/{unit}.md {digit * 64} 2026-01-01 {unit}\n"

    def commit(graded, message):
        (work / "guide" / "GRADED").write_text(graded)
        git("add", ".")
        git("commit", "-q", "-m", message)

    git("init", "-q", "-b", "main")
    commit(line("a", "0") + line("z", "0"), "base")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env, check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("fetch", "-q", "origin")
    git("remote", "set-head", "origin", "main")
    commit(line("a", "0") + line("b", "1") + line("z", "0"), "upstream")
    git("push", "-q", "origin", "main")
    onto = git("rev-parse", "HEAD")
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit(line("a", "0") + line("c", "2") + line("z", "0"), "branch")
    (work / ".tdd").mkdir()
    (work / ".tdd" / "ci-conflict-rebased").write_text("")

    run_env = dict(env, S=str(bin_dir), PATH=f"{bin_dir}:{env['PATH']}")
    subprocess.run(["bash", "-c", block.encode("latin-1").decode("utf-8", "surrogateescape")], cwd=work, env=run_env,
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    log = work / "events.log"
    got = log.read_text().rstrip("\n") if log.exists() else ""
    assert (got, git("rev-parse", "HEAD~1"), (work / ".tdd" / "ci-conflict-rebased").exists()) == ("", onto, True), (
        f"a GRADED-only conflict after the run's rebase recorded [{got}] instead of rebasing onto {onto}")


@pytest.mark.process("SKILL.md's first CI-wait block runs under bash -c in a git repo with a bare origin, the real rebase-onto-default.sh and stub scripts")
def test_issue_2706_a_conflict_beyond_graded_with_the_marker_already_present_records_the_ci_conflict_bail_and_leaves_head(tmp_path):
    step = _ci_step()
    assert step.strip(), NO_STEP
    block = _first_block(step)
    assert block.strip(), "no first CI-wait block in the CI step — nothing could be run"
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stubs = {"wait-ci.sh": '#!/bin/sh\necho "PR conflicts with its base branch" >&2\nexit 2\n',
             "event.sh": '#!/bin/sh\necho "$*" >> events.log\n',
             "classify-bail.sh": '#!/bin/sh\necho "$1"\n',
             "ledger-steps.sh": "#!/bin/sh\nexit 0\n",
             "pr-ready.sh": "#!/bin/sh\nexit 0\n",
             "gh": "#!/bin/sh\nexit 0\n",
             "rebase-onto-default.sh": f'#!/bin/sh\nexec "{SCRIPTS / "rebase-onto-default.sh"}" "$@"\n'}
    for name, body in stubs.items():
        (bin_dir / name).write_text(body)
        (bin_dir / name).chmod(0o755)
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def line(unit, digit):
        return f"guide/{unit}.md {digit * 64} 2026-01-01 {unit}\n"

    def commit(graded, message, other):
        (work / "guide" / "GRADED").write_text(graded)
        (work / "other.txt").write_text(other)
        git("add", ".")
        git("commit", "-q", "-m", message)

    git("init", "-q", "-b", "main")
    commit(line("a", "0") + line("z", "0"), "base", "0\n")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env, check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("fetch", "-q", "origin")
    git("remote", "set-head", "origin", "main")
    commit(line("a", "0") + line("b", "1") + line("z", "0"), "upstream", "1\n")
    git("push", "-q", "origin", "main")
    onto = git("rev-parse", "HEAD")
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit(line("a", "0") + line("c", "2") + line("z", "0"), "branch", "2\n")
    tip = git("rev-parse", "HEAD")
    (work / ".tdd").mkdir()
    (work / ".tdd" / "ci-conflict-rebased").write_text("")

    run_env = dict(env, S=str(bin_dir), PATH=f"{bin_dir}:{env['PATH']}")
    subprocess.run(["bash", "-c", block.encode("latin-1").decode("utf-8", "surrogateescape")], cwd=work, env=run_env,
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    log = work / "events.log"
    got = log.read_text().rstrip("\n") if log.exists() else ""
    assert (got, git("rev-parse", "HEAD"), (work / ".tdd" / "ci-conflict-rebased").exists()) == (
        "bail cause=ci-conflict classification=ci-conflict", tip, True), (
        f"a conflict beyond GRADED after the run's rebase recorded [{got}] instead of the ci-conflict bail with HEAD at {tip}")
