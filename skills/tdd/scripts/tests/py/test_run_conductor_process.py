"""Cases for run-conductor.sh that start a real process."""
import os
import shutil
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.mark.process("run-conductor.sh run as a real shim over veri/run_conductor.py, refusing an empty issue before any fetch")
def test_run_conductor_sh_with_an_empty_issue_forwards_it_to_the_module_and_returns_2_with_the_usage_line_alone(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "run-conductor.sh"), ""], cwd=tmp_path, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_BASH_MAJOR": "5",
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: run-conductor.sh <issue>\n")


@pytest.mark.process("a real stub process standing in for claude -p, started by run_conductor.conduct")
def test_conduct_records_the_pid_of_the_claude_process_it_starts_in_the_worktree_conductor_pid_before_that_process_runs_issue_2249(
        tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    stub = tmp_path / "stub-claude"
    stub.write_text('#!/bin/sh\ncat "%s/.tdd/wt/2249/.tdd/conductor.pid" > "%s/seen" 2>/dev/null\necho $$ > "%s/mine"\n'
                    % (tmp_path, tmp_path, tmp_path))
    stub.chmod(0o755)
    (tmp_path / ".tdd" / "wt" / "2249").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_BIN", str(stub))
    monkeypatch.setenv("PATH", os.path.dirname(sys.executable) + ":/usr/bin:/bin")
    sys.path[:0] = [str(SCRIPTS)]
    from veri import run_conductor

    run_conductor.conduct("", "2249", dict(os.environ))

    assert (tmp_path / "seen").read_text().splitlines()[0] == (tmp_path / "mine").read_text().strip() != ""


@pytest.mark.tree_audit("copies the veri and lib directories into a scratch clone")
@pytest.mark.process("a real run_conductor.main in its own process whose stub claude SIGKILLs it, over a real skill clone and a real caller repository with the run's worktree registered")
def test_main_leaves_the_pinned_scripts_under_the_existing_run_worktrees_tdd_when_the_conductor_is_killed_by_sigkill_issue_2627(
        tmp_path):
    clone = tmp_path / "clone"
    for part in ("veri", "lib"):
        shutil.copytree(SCRIPTS / part, clone / "skills" / "tdd" / "scripts" / part,
                        ignore=shutil.ignore_patterns("__pycache__"))
    (clone / "skills" / "tdd" / "SKILL.md").write_text("procedure\n")
    git_env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")

    def commit_all(directory):
        for argv in (["init", "-q"], ["add", "-A"], ["commit", "-q", "--allow-empty", "-m", "seed"]):
            subprocess.run(["git", "-C", str(directory)] + argv, check=True, env=git_env)

    commit_all(clone)
    pin = subprocess.run(["git", "-C", str(clone), "rev-parse", "HEAD"], check=True, capture_output=True,
                         text=True).stdout.strip()
    repo = tmp_path / "repo"
    repo.mkdir()
    commit_all(repo)
    worktree = repo / ".tdd" / "wt" / "2627"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "-b", "tdd/2627-pin", str(worktree)], check=True,
                   env=git_env)
    (repo / ".tdd" / "issue-2627-skill-commit").write_text(pin + "\n")
    stub = tmp_path / "stub-claude"
    stub.write_text("#!/bin/sh\nkill -9 $PPID\n")
    stub.chmod(0o755)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    veri = clone / "skills" / "tdd" / "scripts" / "veri"

    with open(tmp_path / "out", "w") as out:
        ran = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, %r); import run_conductor; sys.exit(run_conductor.main(['2627']))" % str(veri)],
            cwd=repo, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=20,
            env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_BASH_MAJOR": "5",
                 "VERI_MIN_FREE_GB": "0", "VERI_TOOL_WAIT": "0", "PYTHONDONTWRITEBYTECODE": "1",
                 "CLAUDE_BIN": str(stub), "TMPDIR": str(scratch)})

    copies = [path.read_bytes() for path in (worktree / ".tdd").rglob("run_conductor.py")]
    assert (ran.returncode, copies) == (-9, [(veri / "run_conductor.py").read_bytes()]), (tmp_path / "out").read_text()


@pytest.mark.tree_audit("copies the veri and lib directories into a scratch clone")
@pytest.mark.process("a real run_conductor.main SIGKILLed by its stub claude, then a real issue_worktree.py --remove over the same caller repository and temp directory")
def test_remove_leaves_no_copy_of_the_pinned_scripts_anywhere_after_a_sigkilled_conductor_issue_2627(tmp_path):
    clone = tmp_path / "clone"
    for part in ("veri", "lib"):
        shutil.copytree(SCRIPTS / part, clone / "skills" / "tdd" / "scripts" / part,
                        ignore=shutil.ignore_patterns("__pycache__"))
    (clone / "skills" / "tdd" / "SKILL.md").write_text("procedure\n")
    git_env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")

    def commit_all(directory):
        for argv in (["init", "-q"], ["add", "-A"], ["commit", "-q", "--allow-empty", "-m", "seed"]):
            subprocess.run(["git", "-C", str(directory)] + argv, check=True, env=git_env)

    commit_all(clone)
    pin = subprocess.run(["git", "-C", str(clone), "rev-parse", "HEAD"], check=True, capture_output=True,
                         text=True).stdout.strip()
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text(".tdd/\n")
    commit_all(repo)
    worktree = repo / ".tdd" / "wt" / "2627"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "-b", "tdd/2627-pin", str(worktree)], check=True,
                   env=git_env)
    (repo / ".tdd" / "issue-2627-skill-commit").write_text(pin + "\n")
    stub = tmp_path / "stub-claude"
    stub.write_text("#!/bin/sh\nkill -9 $PPID\n")
    stub.chmod(0o755)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    veri = clone / "skills" / "tdd" / "scripts" / "veri"
    env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_BASH_MAJOR": "5",
           "VERI_MIN_FREE_GB": "0", "VERI_TOOL_WAIT": "0", "PYTHONDONTWRITEBYTECODE": "1",
           "CLAUDE_BIN": str(stub), "TMPDIR": str(scratch)}

    with open(tmp_path / "out", "w") as out:
        killed = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, %r); import run_conductor; sys.exit(run_conductor.main(['2627']))" % str(veri)],
            cwd=repo, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=20, env=env)
    left_by_the_kill = list(scratch.rglob("run_conductor.py"))
    assert (killed.returncode, len(left_by_the_kill)) == (-9, 1), (tmp_path / "out").read_text()

    removed = subprocess.run([sys.executable, str(SCRIPTS / "veri" / "issue_worktree.py"), "--remove", "2627"],
                             cwd=repo, capture_output=True, text=True, timeout=20, env=env)

    copies = [str(path) for root in (scratch, repo) for path in root.rglob("run_conductor.py")]
    assert (removed.returncode, worktree.exists(), copies) == (0, False, []), removed.stderr


@pytest.mark.tree_audit("copies the veri and lib directories into a scratch clone")
@pytest.mark.process("a real run_conductor.main in its own process whose stub claude cuts the run's worktree and exits 3, over a real skill clone and a real caller repository")
def test_main_leaves_a_runnable_pinned_script_under_a_worktree_cut_during_the_run_when_the_conductor_bails_issue_2627(
        tmp_path):
    clone = tmp_path / "clone"
    for part in ("veri", "lib"):
        shutil.copytree(SCRIPTS / part, clone / "skills" / "tdd" / "scripts" / part,
                        ignore=shutil.ignore_patterns("__pycache__"))
    (clone / "skills" / "tdd" / "SKILL.md").write_text("procedure\n")
    (clone / "skills" / "tdd" / "scripts" / "pinned-probe.sh").write_text("#!/bin/sh\necho pinned-ok\n")
    git_env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")

    def commit_all(directory):
        for argv in (["init", "-q"], ["add", "-A"], ["commit", "-q", "--allow-empty", "-m", "seed"]):
            subprocess.run(["git", "-C", str(directory)] + argv, check=True, env=git_env)

    commit_all(clone)
    pin = subprocess.run(["git", "-C", str(clone), "rev-parse", "HEAD"], check=True, capture_output=True,
                         text=True).stdout.strip()
    repo = tmp_path / "repo"
    repo.mkdir()
    commit_all(repo)
    (repo / ".tdd").mkdir()
    (repo / ".tdd" / "issue-2627-skill-commit").write_text(pin + "\n")
    stub = tmp_path / "stub-claude"
    stub.write_text("#!/bin/sh\ncat > /dev/null\nrm -f .tdd/wt/2627/.tdd/conductor.pid\n"
                    "rmdir .tdd/wt/2627/.tdd .tdd/wt/2627\n"
                    "git worktree add -q -b tdd/2627-pin .tdd/wt/2627 || exit 9\nexit 3\n")
    stub.chmod(0o755)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    veri = clone / "skills" / "tdd" / "scripts" / "veri"

    with open(tmp_path / "out", "w") as out:
        ran = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, %r); import run_conductor; sys.exit(run_conductor.main(['2627']))" % str(veri)],
            cwd=repo, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=20,
            env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_BASH_MAJOR": "5",
                 "VERI_MIN_FREE_GB": "0", "VERI_TOOL_WAIT": "0", "PYTHONDONTWRITEBYTECODE": "1",
                 "CLAUDE_BIN": str(stub), "TMPDIR": str(scratch)})

    probes = list((repo / ".tdd" / "wt" / "2627" / ".tdd").rglob("pinned-probe.sh"))
    printed = [subprocess.run(["sh", str(path)], capture_output=True, text=True).stdout.strip() for path in probes]
    assert (ran.returncode, printed) == (3, ["pinned-ok"]), (tmp_path / "out").read_text()


@pytest.mark.tree_audit("copies the veri and lib directories into a scratch clone")
@pytest.mark.process("two real run_conductor.main processes with a stub claude that exits 0, the second re-pinning with VERI_NEW_SKILL=1 over a real skill clone and a real caller repository with the run's worktree registered")
def test_main_replaces_the_pinned_scripts_with_the_newly_pinned_commits_when_re_pinning_with_veri_new_skill_issue_2627(
        tmp_path):
    clone = tmp_path / "clone"
    for part in ("veri", "lib"):
        shutil.copytree(SCRIPTS / part, clone / "skills" / "tdd" / "scripts" / part,
                        ignore=shutil.ignore_patterns("__pycache__"))
    (clone / "skills" / "tdd" / "SKILL.md").write_text("procedure\n")
    (clone / "skills" / "tdd" / "scripts" / "pinned-old.sh").write_text("#!/bin/sh\necho old\n")
    git_env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")

    def git(directory, *argv):
        return subprocess.run(["git", "-C", str(directory)] + list(argv), check=True, env=git_env,
                              capture_output=True, text=True).stdout.strip()

    git(clone, "init", "-q")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "first pin")
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "commit", "-q", "--allow-empty", "-m", "seed")
    worktree = repo / ".tdd" / "wt" / "2627"
    git(repo, "worktree", "add", "-q", "-b", "tdd/2627-pin", str(worktree))
    stub = tmp_path / "stub-claude"
    stub.write_text("#!/bin/sh\ncat > /dev/null\nexit 0\n")
    stub.chmod(0o755)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    veri = clone / "skills" / "tdd" / "scripts" / "veri"

    def conduct(new_skill):
        env = {"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_BASH_MAJOR": "5",
               "VERI_MIN_FREE_GB": "0", "VERI_TOOL_WAIT": "0", "PYTHONDONTWRITEBYTECODE": "1",
               "CLAUDE_BIN": str(stub), "TMPDIR": str(scratch)}
        if new_skill:
            env["VERI_NEW_SKILL"] = "1"
        with open(tmp_path / "out", "a") as out:
            return subprocess.run(
                [sys.executable, "-c",
                 "import sys; sys.path.insert(0, %r); import run_conductor; sys.exit(run_conductor.main(['2627']))" % str(veri)],
                cwd=repo, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=20, env=env).returncode

    first = conduct(False)
    (clone / "skills" / "tdd" / "scripts" / "pinned-old.sh").unlink()
    (clone / "skills" / "tdd" / "scripts" / "pinned-new.sh").write_text("#!/bin/sh\necho new\n")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "second pin")
    second = conduct(True)

    kept = sorted(path.name for path in (worktree / ".tdd").rglob("pinned-*.sh"))
    recorded = (repo / ".tdd" / "issue-2627-skill-commit").read_text().strip()
    assert (first, second, kept, recorded) == (0, 0, ["pinned-new.sh"], git(clone, "rev-parse", "HEAD")), \
        (tmp_path / "out").read_text()


@pytest.mark.tree_audit("copies the veri and lib directories into a scratch clone")
@pytest.mark.process("a real run_conductor.main process with a stub claude that exits 0, then git add -A in the run's worktree, over a real skill clone and a real caller repository with the run's worktree registered")
def test_git_add_all_in_the_run_worktree_stages_nothing_from_the_pinned_scripts_copy_issue_2627(tmp_path):
    clone = tmp_path / "clone"
    for part in ("veri", "lib"):
        shutil.copytree(SCRIPTS / part, clone / "skills" / "tdd" / "scripts" / part,
                        ignore=shutil.ignore_patterns("__pycache__"))
    (clone / "skills" / "tdd" / "SKILL.md").write_text("procedure\n")
    (clone / "skills" / "tdd" / "scripts" / "pinned-probe.sh").write_text("#!/bin/sh\necho pinned-ok\n")
    git_env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")

    def git(directory, *argv):
        return subprocess.run(["git", "-C", str(directory)] + list(argv), check=True, env=git_env,
                              capture_output=True, text=True).stdout.strip()

    git(clone, "init", "-q")
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "seed")
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "commit", "-q", "--allow-empty", "-m", "seed")
    worktree = repo / ".tdd" / "wt" / "2627"
    git(repo, "worktree", "add", "-q", "-b", "tdd/2627-pin", str(worktree))
    stub = tmp_path / "stub-claude"
    stub.write_text("#!/bin/sh\ncat > /dev/null\nexit 0\n")
    stub.chmod(0o755)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    veri = clone / "skills" / "tdd" / "scripts" / "veri"

    with open(tmp_path / "out", "w") as out:
        ran = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, %r); import run_conductor; sys.exit(run_conductor.main(['2627']))" % str(veri)],
            cwd=repo, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=20,
            env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_BASH_MAJOR": "5",
                 "VERI_MIN_FREE_GB": "0", "VERI_TOOL_WAIT": "0", "PYTHONDONTWRITEBYTECODE": "1",
                 "CLAUDE_BIN": str(stub), "TMPDIR": str(scratch)})
    git(worktree, "add", "-A")
    staged = [name for name in git(worktree, "diff", "--cached", "--name-only").splitlines() if "pinned-probe.sh" in name]

    assert (ran.returncode, staged) == (0, []), (tmp_path / "out").read_text()
