"""Cases for where the skill ships, what it calls itself, and that nothing still names the old homes."""
import pathlib
import subprocess

import pytest

from conftest import ROOT
from repo_builder import new_repo

OLD_SKILL_DIR = "skills/solve-issue"
OLD_SCRIPTS_DIR = f"{OLD_SKILL_DIR}/scripts"
STUBS = [f"{OLD_SKILL_DIR}/SKILL.md", "skills/solve-issues/SKILL.md"]
OLD_DIRS = [str(pathlib.PurePosixPath(stub).parent) for stub in STUBS]
OLD_CMDS = ["/" + pathlib.PurePosixPath(old_dir).name for old_dir in OLD_DIRS]
CMD_RE = "(^|[^[:alnum:]_/.-])" + f"({OLD_CMDS[0]}|{OLD_CMDS[1]})"


def exempt(path):
    return path.startswith(".tdd/")


def sweep(repo, mode, pattern):
    done = subprocess.run(
        ["git", "grep", "--files-with-matches", mode, "-e", pattern, "--", ":!docs", ":!projects/docs"],
        cwd=repo, capture_output=True, text=True)
    if done.returncode > 1:
        return [], [f"git grep failed with exit {done.returncode}"]
    return [line for line in done.stdout.splitlines() if line], []


def offenders(swept):
    return [path for path in swept if not exempt(path)]


def plant(path, files):
    for name, text in files.items():
        (path / name).parent.mkdir(parents=True, exist_ok=True)
        (path / name).write_text(text)
    new_repo(path)
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True)


@pytest.mark.process("git grep over the repository's tracked files for the old scripts directory")
def test_no_tracked_file_outside_the_two_stubs_still_names_the_old_scripts_dir():
    swept, problems = sweep(ROOT, "--fixed-strings", OLD_SCRIPTS_DIR)
    problems += [f"{path} still names {OLD_SCRIPTS_DIR}" for path in offenders(swept)]
    assert not problems, problems


@pytest.mark.process("git grep over the repository's tracked files for the old commands")
def test_no_tracked_file_outside_the_two_stubs_names_either_old_command():
    swept, problems = sweep(ROOT, "-E", CMD_RE)
    problems += [f"{path} still names an old command" for path in offenders(swept)]
    assert not problems, problems


@pytest.mark.process("git add and git grep over a planted repository holding files at the former stub paths")
def test_a_tracked_file_at_a_former_stub_path_fails_both_sweeps_exempt_no_longer_covers_the_stub_paths(tmp_path):
    plant(tmp_path, {
        STUBS[0]: f"scripts live at {OLD_SCRIPTS_DIR}/run.sh\n",
        STUBS[1]: f"Invoke {OLD_CMDS[0]} 12 and follow it.\n",
    })
    problems = []
    swept, failed = sweep(tmp_path, "--fixed-strings", OLD_SCRIPTS_DIR)
    problems += failed
    if STUBS[0] not in offenders(swept):
        problems.append(f"old-home sweep: {STUBS[0]} names {OLD_SCRIPTS_DIR} but was not reported — exempt still covers it")
    swept, failed = sweep(tmp_path, "-E", CMD_RE)
    problems += failed
    if STUBS[1] not in offenders(swept):
        problems.append(f"old-command sweep: {STUBS[1]} invokes {OLD_CMDS[0]} but was not reported — exempt still covers it")
    assert not problems, problems


@pytest.mark.process("git add and git grep over a planted repository holding files under .tdd/")
def test_a_tracked_file_under_tdd_naming_the_old_home_or_an_old_command_passes_both_sweeps(tmp_path):
    plant(tmp_path, {
        ".tdd/issue-1-plan.md": f"scripts live at {OLD_SCRIPTS_DIR}/run.sh\n",
        ".tdd/issue-2-plan.md": f"Invoke {OLD_CMDS[0]} 12 and follow it.\n",
    })
    problems = []
    swept, failed = sweep(tmp_path, "--fixed-strings", OLD_SCRIPTS_DIR)
    problems += failed
    if ".tdd/issue-1-plan.md" not in swept:
        problems.append("old-home sweep: .tdd/issue-1-plan.md was not matched at all, so its exemption was not tested")
    if offenders(swept):
        problems.append(f"old-home sweep: want no offenders under .tdd/, got: {offenders(swept)}")
    swept, failed = sweep(tmp_path, "-E", CMD_RE)
    problems += failed
    if ".tdd/issue-2-plan.md" not in swept:
        problems.append("old-command sweep: .tdd/issue-2-plan.md was not matched at all, so its exemption was not tested")
    if offenders(swept):
        problems.append(f"old-command sweep: want no offenders under .tdd/, got: {offenders(swept)}")
    assert not problems, problems


@pytest.mark.process("git add and git grep over a planted repository holding ADR 0013's line 18")
def test_adr_0013s_line_18_naming_the_old_home_as_a_path_passes_both_sweeps(tmp_path):
    adr_line = f"the user-level `~/.claude/{OLD_SKILL_DIR}` symlink into the primary clone silently\n"
    plant(tmp_path, {"docs/adr/0013-issue-branch-in-its-own-worktree.md": adr_line})
    problems = []
    for label, mode, pattern in (("old-home", "--fixed-strings", OLD_SCRIPTS_DIR), ("old-command", "-E", CMD_RE)):
        swept, failed = sweep(tmp_path, mode, pattern)
        problems += failed
        if offenders(swept):
            problems.append(f"{label} sweep: want no offenders for ADR 0013's line 18, got: {offenders(swept)}")
    assert not problems, problems
