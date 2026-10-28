"""Case for the pointers skills/tdd/SKILL.md carries to RESUME.md, read as text."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
TDD = SKILL.parent
CORE = [TDD / name for name in ("SKILL.md", "SCRIPTS.md", "BAIL.md", "RECONCILE.md")]
NAMING_FILES = CORE + [TDD / "scripts" / "solvable-issues.sh"]

NAMES_RESUME = re.compile(r"\bResume\b(?!\.\*\*| check)")


def _lines(path):
    return path.read_text().split("\n")


def test_resume_pointers_name_resume_md_in_the_base_directory():
    for path in CORE:
        for n, line in enumerate(_lines(path), 1):
            if "RESUME.md" in line:
                assert "VERI_SKILL_CLONE" not in line and "~/.claude/skills" not in line, \
                    f"{path.name}:{n} points RESUME.md outside the base directory"

    for path in NAMING_FILES:
        for n, line in enumerate(_lines(path), 1):
            if NAMES_RESUME.search(line):
                assert "RESUME.md" in line, f"{path.name}:{n} names Resume without naming RESUME.md"


def test_resume_section_lives_in_resume_md_and_skill_md_carries_none_of_its_lines():
    moved = [r"\$S/event\.sh resume`", r"left=\$\(\( \$\{VERI_REFACTOR_BUDGET:-5\} - count \)\)",
             r"add-ledger-step\.sh --planned --criterion"]
    skill = _lines(SKILL)
    assert "## Resume" not in skill, "SKILL.md still carries the ## Resume heading"
    left = [p for p in moved if any(re.search(p, line) for line in skill)]
    assert not left, f"SKILL.md still carries the moved lines {left}"


def test_1967_preflight_step_3_resumed_run_block_is_one_resume_clean_sh_call_and_its_exit_2_bails_as_a_system_failure():
    text = SKILL.with_name("PREFLIGHT.md").read_text()
    start = text.index("A run that `issue-worktree.sh` handed back an existing worktree")
    end = text.index("Then the handed-back run, its uncommitted", start)
    prose = text[start:end]
    fences = re.findall(r"```\n(.*?)```", prose, re.S)
    assert len(fences) == 1, f"the resumed-run block holds {len(fences)} code fences, want 1"
    code = [line.strip() for line in fences[0].splitlines() if line.strip()]
    assert len(code) == 1 and "$S/resume-clean.sh" in code[0], f"the block is not one $S/resume-clean.sh call: {code}"
    for syntax in ("[[", "<<<", "<("):
        assert syntax not in prose, f"the resumed-run block still holds bash-only {syntax!r}"
    assert re.search(r"exit 2.*?bails as a \*\*system\*\* failure", " ".join(prose.split())), \
        "the resumed-run block does not bail its exit 2 as a system failure"
