"""Cases for add-ledger-step.sh that start the real entry point."""
import importlib

import pytest

from conftest import SCRIPTS

import subprocess

SEED = (
    "# Plan for #42\n\n"
    "- [x] lowercase the slug ⟦criterion 1⟧\n"
    "- [ ] collapse to single hyphen ⟦criterion 2⟧\n"
    "- [ ] strip edge hyphens ⟦criterion 3⟧\n"
)


@pytest.mark.process("add-ledger-step.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_rewrites_the_relative_ledger_as_it_does_in_place(
        tmp_path, run_cli):
    add_ledger_step = importlib.import_module("veri.add_ledger_step")
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    linked = str(tmp_path / "linked-skill" / "scripts" / "add-ledger-step.sh")
    for name in ("in-place", "elsewhere"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "l.md").write_text(SEED)

    answers = {}
    for anchor in ("collapse to single hyphen", "no such step"):
        argv = ["l.md", "after", anchor, "t"]
        ran = subprocess.run([linked, *argv], cwd=tmp_path / "elsewhere", stdin=subprocess.DEVNULL,
                             capture_output=True, text=True)
        answers[anchor] = (run_cli(add_ledger_step, argv, cwd=tmp_path / "in-place"),
                           (ran.returncode, ran.stdout, ran.stderr))

    after, none = answers["collapse to single hyphen"], answers["no such step"]
    for code, out, err in after:
        assert (code, out) == (0, "")
        assert err.count("\n") == 1 and "not durable" in err.lower(), err
    assert none[0] == none[1] == (2, "", "add-ledger-step.sh: anchor matches no single step: no such step\n")
    assert (tmp_path / "elsewhere" / "l.md").read_bytes() == (tmp_path / "in-place" / "l.md").read_bytes()
    assert "- [ ] t ⟦added⟧ ⟦criterion 2⟧\n" in (tmp_path / "elsewhere" / "l.md").read_text()


@pytest.mark.process("add-ledger-step.sh run against a real git worktree whose conductor.pid names a real live process")
def test_cli_3618_step_added_while_the_conductor_is_live_is_committed_and_survives_a_reset_hard(tmp_path):
    import os
    from veri import pid_file

    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}

    def git(*args):
        return subprocess.run(["git", *args], cwd=wt, env=env, capture_output=True, text=True, check=True).stdout

    ledger = wt / ".tdd" / "issue-42.md"
    ledger.write_text(SEED)
    (wt / "other.txt").write_text("one\n")
    git("init", "-q")
    git("add", "-A", "-f")
    git("commit", "-q", "-m", "seed")

    conductor = subprocess.Popen(["sleep", "30"])
    try:
        pid_file.record(str(wt / ".tdd" / "conductor.pid"), conductor.pid)
        (wt / "other.txt").write_text("two\n")
        ran = subprocess.run([str(SCRIPTS / "add-ledger-step.sh"), str(ledger), "after", "collapse to single hyphen", "t"],
                             cwd=wt, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
        assert ran.returncode == 0, ran.stderr
        committed = sorted(git("show", "--name-only", "--format=", "HEAD").split())
        assert committed == [".tdd/issue-42-added.md", ".tdd/issue-42.md"]
        assert (wt / "other.txt").read_text() == "two\n"
        git("reset", "--hard", "HEAD")
    finally:
        conductor.kill()
        conductor.wait()

    assert "- [ ] t ⟦added⟧ ⟦criterion 2⟧\n" in ledger.read_text()
    assert (wt / ".tdd" / "issue-42-added.md").is_file()


@pytest.mark.process("add-ledger-step.sh run against a real git worktree whose conductor.pid names a real live process")
def test_cli_3618_stdout_states_the_committed_step_is_durable_naming_the_commit(tmp_path):
    import os
    from veri import pid_file

    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}

    def git(*args):
        return subprocess.run(["git", *args], cwd=wt, env=env, capture_output=True, text=True, check=True).stdout

    ledger = wt / ".tdd" / "issue-42.md"
    ledger.write_text(SEED)
    git("init", "-q")
    git("add", "-A", "-f")
    git("commit", "-q", "-m", "seed")

    conductor = subprocess.Popen(["sleep", "30"])
    try:
        pid_file.record(str(wt / ".tdd" / "conductor.pid"), conductor.pid)
        ran = subprocess.run([str(SCRIPTS / "add-ledger-step.sh"), str(ledger), "after", "collapse to single hyphen", "t"],
                             cwd=wt, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
        head = git("rev-parse", "HEAD").strip()
    finally:
        conductor.kill()
        conductor.wait()

    assert ran.returncode == 0, ran.stderr
    assert ran.stdout == ""
    assert "committed" in ran.stderr.lower()
    assert head[:7] in ran.stderr


@pytest.mark.process("add-ledger-step.sh run against a real git worktree whose commit hook refuses and conductor.pid names a real live process")
def test_cli_3618_stderr_says_not_durable_and_makes_no_durable_claim_when_the_commit_fails(tmp_path):
    import os
    from veri import pid_file

    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}

    def git(*args):
        return subprocess.run(["git", *args], cwd=wt, env=env, capture_output=True, text=True, check=True).stdout

    ledger = wt / ".tdd" / "issue-42.md"
    ledger.write_text(SEED)
    git("init", "-q")
    git("add", "-A", "-f")
    git("commit", "-q", "-m", "seed")
    hook = wt / ".git" / "hooks" / "pre-commit"
    hook.parent.mkdir(exist_ok=True)
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    seeded = git("rev-parse", "HEAD").strip()

    conductor = subprocess.Popen(["sleep", "30"])
    try:
        pid_file.record(str(wt / ".tdd" / "conductor.pid"), conductor.pid)
        ran = subprocess.run([str(SCRIPTS / "add-ledger-step.sh"), str(ledger), "after", "collapse to single hyphen", "t"],
                             cwd=wt, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
        head = git("rev-parse", "HEAD").strip()
    finally:
        conductor.kill()
        conductor.wait()

    assert head == seeded
    assert "collapse to single hyphen" in ledger.read_text()
    assert ran.returncode == 0, ran.stderr
    assert ran.stdout == ""
    assert "not durable" in ran.stderr.lower(), ran.stderr
    assert "step is durable" not in ran.stderr.lower()
    assert "committed in" not in ran.stderr.lower()


@pytest.mark.process("add-ledger-step.sh run as a child of the real live process conductor.pid names, in a real git worktree")
def test_cli_3618_step_added_by_the_live_conductor_itself_is_left_uncommitted(tmp_path):
    import os
    from veri import pid_file

    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}

    def git(*args):
        return subprocess.run(["git", *args], cwd=wt, env=env, capture_output=True, text=True, check=True).stdout

    ledger = wt / ".tdd" / "issue-42.md"
    ledger.write_text(SEED)
    git("init", "-q")
    git("add", "-A", "-f")
    git("commit", "-q", "-m", "seed")
    head = git("rev-parse", "HEAD")

    script = f'read go; "$0" "$@"; echo $? > "{tmp_path}/rc"'
    conductor = subprocess.Popen(
        ["sh", "-c", script, str(SCRIPTS / "add-ledger-step.sh"), str(ledger), "after", "collapse to single hyphen", "t"],
        cwd=wt, env=env, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        pid_file.record(str(wt / ".tdd" / "conductor.pid"), conductor.pid)
        conductor.stdin.write(b"\n")
        conductor.stdin.close()
        conductor.wait(timeout=20)
    finally:
        if conductor.poll() is None:
            conductor.kill()
            conductor.wait()

    assert (tmp_path / "rc").read_text().strip() == "0"
    assert git("rev-parse", "HEAD") == head
    assert "- [ ] t ⟦added⟧ ⟦criterion 2⟧\n" in ledger.read_text()
    assert ".tdd/issue-42.md" in git("status", "--porcelain")
