"""Cases for where the skill ships, what it calls itself, and that nothing still names the old homes."""
import importlib
import pathlib
import re
import subprocess

import pytest

from conftest import ROOT

SKILL_DIR = "skills/tdd"
WANT_NAME = "tdd"
SKILL_MD = f"{SKILL_DIR}/SKILL.md"

OLD_SKILL_DIR = "skills/solve-issue"
OLD_SCRIPTS_DIR = f"{OLD_SKILL_DIR}/scripts"
STUBS = [f"{OLD_SKILL_DIR}/SKILL.md", "skills/solve-issues/SKILL.md"]
OLD_DIRS = [str(pathlib.PurePosixPath(stub).parent) for stub in STUBS]
OLD_CMDS = ["/" + pathlib.PurePosixPath(old_dir).name for old_dir in OLD_DIRS]
CMD_RE = "(^|[^[:alnum:]_/.-])" + f"({OLD_CMDS[0]}|{OLD_CMDS[1]})"


def frontmatter_name(path):
    lines = pathlib.Path(path).read_text().splitlines()
    if not lines or lines[0] != "---":
        return ""
    for line in lines[1:]:
        if line == "---":
            return ""
        if line.startswith("name:"):
            return line[len("name:"):].lstrip()
    return ""


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


def new_repo(path):
    for args in (["init", "-q"], ["config", "user.name", "Test"], ["config", "user.email", "test@example.com"]):
        subprocess.run(["git", "-C", str(path), *args], check=True)


def plant(path, files):
    for name, text in files.items():
        (path / name).parent.mkdir(parents=True, exist_ok=True)
        (path / name).write_text(text)
    new_repo(path)
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True)


def inputs_section():
    return importlib.import_module("skill_sections").section(ROOT / SKILL_MD, "## Inputs")


def inputs_text():
    return "".join(inputs_section().splitlines(keepends=True)[1:])


def loop_md_path():
    for line in inputs_text().splitlines():
        for found in re.findall(r"[A-Za-z0-9_./-]+\.md", line):
            if not re.search(r"(^|/)SKILL\.md$", found):
                return found if "/" in found else f"{SKILL_DIR}/{found}"
    return ""


def has_line(text, pattern):
    return any(re.search(pattern, line) for line in text.splitlines())


def test_the_skill_ships_at_skills_tdd_and_its_frontmatter_reads_name_tdd():
    problems = []
    if not (ROOT / SKILL_DIR).is_dir():
        problems.append(f"want a directory at {SKILL_DIR}, found none")
    if (ROOT / SKILL_MD).is_file():
        got = frontmatter_name(ROOT / SKILL_MD)
        if got != WANT_NAME:
            problems.append(f"{SKILL_MD} frontmatter: want name '{WANT_NAME}', got {got!r}")
    else:
        problems.append(f"want a SKILL.md at {SKILL_MD}, found none")
    assert not problems, problems


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


def test_skill_md_resolves_its_argument_an_integer_is_one_issue_any_other_word_a_scope_bare_is_plain():
    problems = []
    skill = (ROOT / SKILL_MD).read_text()
    if has_line(skill, r"^#+ .*[Dd]raining a scope"):
        problems.append(f"{SKILL_MD} still holds the scope loop's own section, billed on every conductor request")
    loop_subs = sum(1 for line in skill.splitlines() if re.search(r"^#+ Loop ", line))
    if loop_subs != 0:
        problems.append(f"{SKILL_MD} still holds {loop_subs} 'Loop *' sub-sections")
    loop_md = loop_md_path()
    if not loop_md:
        problems.append(f"{SKILL_MD} '## Inputs' names no sibling .md file, so a scope argument resolves to nothing")
    elif not (ROOT / loop_md).is_file():
        problems.append(f"{SKILL_MD} Inputs points at {loop_md}, which is not a file")
    else:
        loop = (ROOT / loop_md).read_text()
        if not has_line(loop, r"^#+ .*[Dd]raining a scope"):
            problems.append(f"{loop_md} has no 'Draining a scope' section, so the pointer leads nowhere")
        if not has_line(loop, r"^#+ Loop "):
            problems.append(f"{loop_md} has no 'Loop *' sub-sections, so the loop's steps did not move with it")
    sibling_scripts = f"../{pathlib.PurePosixPath(OLD_SKILL_DIR).name}/scripts"
    if sibling_scripts in skill:
        problems.append(f"{SKILL_MD} still locates its scripts at {sibling_scripts}, a sibling that is no longer there")
    assert not problems, problems


def test_only_the_scope_branch_is_sent_to_the_loop_file_skill_md_keeps_procedure_and_the_loop_delegates_back_to_it():
    problems = []
    skill_lines = (ROOT / SKILL_MD).read_text().splitlines()
    loop_md = loop_md_path()
    if not has_line("\n".join(skill_lines), r"^#+ Procedure$"):
        problems.append(f"{SKILL_MD} no longer holds a 'Procedure' section, so the single-issue path did not stay put")
    if not loop_md or not (ROOT / loop_md).is_file():
        problems.append(f"{SKILL_MD} '## Inputs' points at no readable loop file — who is sent to read it could not be tested")
    else:
        loop_base = pathlib.PurePosixPath(loop_md).name
        start = skill_lines.index("## Inputs")
        inside = start + len(inputs_section().splitlines())
        for number, line in enumerate(skill_lines, 1):
            if not start <= number - 1 < inside and loop_base in line:
                problems.append(f"{SKILL_MD} names {loop_base} outside '## Inputs' — {number}: {line[:90]}")
    assert not problems, problems


def test_neither_old_skill_directory_is_left_in_the_tree():
    problems = [f"want no {old_dir}/, found one" for old_dir in OLD_DIRS if (ROOT / old_dir).exists()]
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


def test_readmes_install_step_symlinks_skills_tdd_alone_and_no_old_skill_directory():
    problems = []
    inside, links = False, []
    for line in (ROOT / "README.md").read_text().splitlines():
        if line == "## Install":
            inside = True
        elif inside and line.startswith("## "):
            break
        elif inside and line.startswith("ln -s "):
            links.append(line)
    joined = "\n".join(links)
    if '/skills/vinstall" ~/.claude/skills/vinstall' not in joined:
        problems.append(f"README.md ## Install: want an ln -s of skills/vinstall to ~/.claude/skills/vinstall, got: {joined or 'no ln -s line'}")
    for old_dir in OLD_DIRS:
        if f'/{old_dir}"' in joined:
            problems.append(f"README.md ## Install still links {old_dir}/: {joined}")
    assert not problems, problems
