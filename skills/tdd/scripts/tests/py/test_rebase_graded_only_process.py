"""Cases for rebase-onto-default.sh --graded-only on a real git repository."""
import subprocess
from pathlib import Path

import pytest

from conftest import INTERPRETER_VENV

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("a real two-branch git repository with a bare origin and rebase-onto-default.sh --graded-only")
def test_2706_graded_only_with_a_conflict_in_a_graded_file_and_another_path_aborts_exits_1_and_names_both(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def commit(graded, other, message):
        (work / "guide" / "GRADED").write_text(graded)
        (work / "guide" / "other.txt").write_text(other)
        git("add", ".")
        git("commit", "-q", "-m", message)

    git("init", "-q", "-b", "main")
    commit("guide/a.md " + "0" * 64 + " 2026-01-01 base\n", "base\n", "base")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env, check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("fetch", "-q", "origin")
    git("remote", "set-head", "origin", "main")
    commit("guide/a.md " + "1" * 64 + " 2026-01-01 upstream\n", "upstream\n", "upstream")
    git("push", "-q", "origin", "main")
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit("guide/a.md " + "2" * 64 + " 2026-01-01 branch\n", "branch\n", "branch")
    before = git("rev-parse", "HEAD")

    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh"), "--graded-only"], cwd=work, env=env,
                         capture_output=True, text=True)

    assert (ran.returncode, sorted(ran.stdout.split()), git("rev-parse", "HEAD"),
            (work / ".git" / "rebase-merge").exists()) == (1, ["guide/GRADED", "guide/other.txt"], before, False), ran.stderr


@pytest.mark.process("a real two-branch git repository with a bare origin and rebase-onto-default.sh without the flag")
def test_2706_without_the_flag_a_conflict_only_in_a_graded_file_aborts_exits_1_and_names_it(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def commit(graded, message):
        (work / "guide" / "GRADED").write_text(graded)
        git("add", ".")
        git("commit", "-q", "-m", message)

    git("init", "-q", "-b", "main")
    commit("guide/a.md " + "0" * 64 + " 2026-01-01 base\n", "base")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env, check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("fetch", "-q", "origin")
    git("remote", "set-head", "origin", "main")
    commit("guide/a.md " + "1" * 64 + " 2026-01-01 upstream\n", "upstream")
    git("push", "-q", "origin", "main")
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit("guide/a.md " + "2" * 64 + " 2026-01-01 branch\n", "branch")
    before = git("rev-parse", "HEAD")

    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh")], cwd=work, env=env, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout.split(), git("rev-parse", "HEAD"),
            (work / ".git" / "rebase-merge").exists()) == (1, ["guide/GRADED"], before, False), ran.stderr


@pytest.mark.process("a real two-branch git repository with a bare origin and rebase-onto-default.sh --graded-only")
def test_2706_graded_only_with_a_graded_conflict_of_adjacent_units_rebases_exits_0_and_keeps_both_units_once(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def line(unit, digit):
        return f"guide/{unit}.md {digit * 64} 2026-01-01 {unit}\n"

    def commit(graded, message, changed=()):
        (work / "guide" / "GRADED").write_text(graded)
        for unit in changed:
            (work / "guide" / f"{unit}.md").write_text(message)
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
    commit(line("a", "0") + line("c", "2") + line("z", "0"), "branch", ("c",))
    before = git("rev-parse", "HEAD")

    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh"), "--graded-only"], cwd=work, env=env,
                         capture_output=True, text=True)

    merged = (work / "guide" / "GRADED").read_text()
    assert (ran.returncode, ran.stdout.split(), sorted(merged.splitlines()), "<<<<<<<" in merged) == (
        0, [before, onto], sorted((line("a", "0") + line("b", "1") + line("c", "2") + line("z", "0")).splitlines()), False), ran.stderr


@pytest.mark.process("a real two-branch git repository with a bare origin and rebase-onto-default.sh --graded-only")
def test_2706_graded_only_with_one_hunk_changed_on_both_sides_keeps_the_branch_line_for_signed_units_and_the_base_line_for_the_rest(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def line(unit, digit):
        return f"guide/{unit}.md {digit * 64} 2026-01-01 {unit}\n"

    def commit(graded, message, changed=()):
        (work / "guide" / "GRADED").write_text(graded)
        for unit in changed:
            (work / "guide" / f"{unit}.md").write_text(message)
        git("add", ".")
        git("commit", "-q", "-m", message)

    git("init", "-q", "-b", "main")
    commit(line("a", "0") + line("x", "0") + line("z", "0"), "base")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env, check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("fetch", "-q", "origin")
    git("remote", "set-head", "origin", "main")
    commit(line("a", "0") + line("x", "1") + line("z", "0"), "upstream")
    git("push", "-q", "origin", "main")
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit(line("a", "3") + line("x", "0") + line("c", "2") + line("z", "0"), "branch", ("a", "c"))

    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh"), "--graded-only"], cwd=work, env=env,
                         capture_output=True, text=True)

    merged = (work / "guide" / "GRADED").read_text()
    assert (ran.returncode, sorted(merged.splitlines())) == (
        0, sorted((line("a", "3") + line("x", "1") + line("c", "2") + line("z", "0")).splitlines())), ran.stderr


@pytest.mark.process("a real two-branch git repository with a bare origin and rebase-onto-default.sh --graded-only")
def test_2706_graded_only_with_two_commits_that_each_conflict_only_in_a_graded_file_resolves_both_replays_and_exits_0(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def line(unit, digit):
        return f"guide/{unit}.md {digit * 64} 2026-01-01 {unit}\n"

    def commit(graded, message, changed=()):
        (work / "guide" / "GRADED").write_text(graded)
        for unit in changed:
            (work / "guide" / f"{unit}.md").write_text(message)
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
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit(line("a", "0") + line("c", "2") + line("z", "0"), "branch one", ("c",))
    commit(line("a", "0") + line("c", "3") + line("z", "0"), "branch two", ("c",))

    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh"), "--graded-only"], cwd=work, env=env,
                         capture_output=True, text=True)

    merged = (work / "guide" / "GRADED").read_text()
    assert (ran.returncode, (work / ".git" / "rebase-merge").exists(), sorted(merged.splitlines())) == (
        0, False, sorted((line("a", "0") + line("b", "1") + line("c", "3") + line("z", "0")).splitlines())), ran.stderr


@pytest.mark.process("a real two-branch git repository with a bare origin and rebase-onto-default.sh --graded-only")
def test_2706_graded_only_with_a_rebase_that_stops_without_a_conflicted_path_aborts_exits_1_and_leaves_no_rebase(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
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
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit(line("a", "0") + line("c", "2") + line("z", "0"), "graded")
    (work / "u.txt").write_text("tracked\n")
    git("add", ".")
    git("commit", "-q", "-m", "adds u")
    git("rm", "-q", "u.txt")
    git("commit", "-q", "-m", "removes u")
    before = git("rev-parse", "HEAD")
    (work / "u.txt").write_text("untracked\n")

    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh"), "--graded-only"], cwd=work, env=env,
                         capture_output=True, text=True, timeout=15)

    assert (ran.returncode, (work / ".git" / "rebase-merge").exists(), git("rev-parse", "HEAD")) == (1, False, before), ran.stderr


@pytest.mark.process("a real two-branch git repository with a bare origin and rebase-onto-default.sh --graded-only")
def test_3025_graded_only_keeps_the_branch_row_of_a_unit_whose_file_the_branch_changed_over_a_different_row_on_main(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def line(unit, digit):
        return f"guide/{unit}.md {digit * 64} 2026-01-01 {unit}\n"

    def commit(graded, message, changed=()):
        (work / "guide" / "GRADED").write_text(graded)
        for unit in changed:
            (work / "guide" / f"{unit}.md").write_text(message)
        git("add", ".")
        git("commit", "-q", "-m", message)

    git("init", "-q", "-b", "main")
    commit(line("a", "0") + line("u", "0") + line("z", "0"), "base", ("u",))
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env, check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("fetch", "-q", "origin")
    git("remote", "set-head", "origin", "main")
    commit(line("a", "0") + line("u", "1") + line("z", "0"), "upstream")
    git("push", "-q", "origin", "main")
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit(line("a", "0") + line("u", "3") + line("z", "0"), "branch", ("u",))

    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh"), "--graded-only"], cwd=work, env=env,
                         capture_output=True, text=True)

    merged = (work / "guide" / "GRADED").read_text()
    assert (ran.returncode, sorted(merged.splitlines())) == (
        0, sorted((line("a", "0") + line("u", "3") + line("z", "0")).splitlines())), ran.stderr


@pytest.mark.process("a real two-branch git repository with a bare origin and rebase-onto-default.sh --graded-only")
def test_3025_graded_only_takes_the_main_row_of_a_unit_whose_file_the_branch_never_changed_over_a_stale_branch_row(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def line(unit, digit):
        return f"guide/{unit}.md {digit * 64} 2026-01-01 {unit}\n"

    def commit(graded, message, changed=()):
        (work / "guide" / "GRADED").write_text(graded)
        for unit in changed:
            (work / "guide" / f"{unit}.md").write_text(message)
        git("add", ".")
        git("commit", "-q", "-m", message)

    git("init", "-q", "-b", "main")
    commit(line("a", "0") + line("u", "0") + line("z", "0"), "base", ("u",))
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env, check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("fetch", "-q", "origin")
    git("remote", "set-head", "origin", "main")
    commit(line("a", "0") + line("u", "1") + line("z", "0"), "upstream")
    git("push", "-q", "origin", "main")
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit(line("a", "0") + line("u", "3") + line("z", "0"), "branch")

    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh"), "--graded-only"], cwd=work, env=env,
                         capture_output=True, text=True)

    merged = (work / "guide" / "GRADED").read_text()
    assert (ran.returncode, sorted(merged.splitlines())) == (
        0, sorted((line("a", "0") + line("u", "1") + line("z", "0")).splitlines())), ran.stderr


@pytest.mark.process("a real two-branch git repository with a bare origin, rebase-onto-default.sh --graded-only and prose-owed.sh")
def test_3571_graded_only_with_each_side_re_signing_a_different_unit_rebases_exits_0_keeps_both_rows_once_and_owes_no_unit(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)
    requirements = ("## guide/a.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | It is blue. | because |\n\n"
                    "## guide/b.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| B1 | It is red. | because |\n")
    (work / "guide" / "REQUIREMENTS.md").write_text(requirements)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def sign(unit):
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import grade_prose; "
                "print(grade_prose.signature('guide/REQUIREMENTS.md', sys.argv[2]))")
        return subprocess.run([f"{INTERPRETER_VENV}/bin/python3", "-B", "-c", code, str(SCRIPTS / "veri"), unit], cwd=work, env=env,
                              check=True, capture_output=True, text=True).stdout.strip()

    def row(unit):
        return f"{unit} {sign(unit)} 2026-01-01 id template\n"

    def commit(texts, order, message):
        for name, text in texts.items():
            (work / "guide" / f"{name}.md").write_text(text)
        (work / "guide" / "GRADED").write_text("".join(row(f"guide/{name}.md") for name in order))
        git("add", ".")
        git("commit", "-q", "-m", message)

    git("init", "-q", "-b", "main")
    commit({"a": "A base.\n", "b": "B base.\n"}, "ab", "base")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env, check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("fetch", "-q", "origin")
    git("remote", "set-head", "origin", "main")
    commit({"a": "A upstream.\n"}, "ba", "upstream re-signs a")
    git("push", "-q", "origin", "main")
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit({"b": "B branch.\n"}, "ab", "branch re-signs b")

    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh"), "--graded-only"], cwd=work, env=env,
                         capture_output=True, text=True)
    owed = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(work)], env=env, capture_output=True, text=True)

    rows = sorted((work / "guide" / "GRADED").read_text().splitlines())
    assert (ran.returncode, (work / ".git" / "rebase-merge").exists(), rows, owed.returncode, owed.stdout) == (
        0, False, sorted([row("guide/a.md").strip(), row("guide/b.md").strip()]), 0, ""), ran.stderr + owed.stderr
