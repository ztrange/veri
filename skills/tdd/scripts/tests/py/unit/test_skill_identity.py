"""Cases for where the skill ships, what it calls itself, and that nothing still names the old homes."""
import importlib
import pathlib
import re

from conftest import ROOT

SKILL_DIR = "skills/tdd"
WANT_NAME = "tdd"
SKILL_MD = f"{SKILL_DIR}/SKILL.md"

OLD_SKILL_DIR = "skills/solve-issue"
STUBS = [f"{OLD_SKILL_DIR}/SKILL.md", "skills/solve-issues/SKILL.md"]
OLD_DIRS = [str(pathlib.PurePosixPath(stub).parent) for stub in STUBS]


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
